"""Small SQLite repository with isolated sessions and atomic quiz submissions."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from coach_app.quiz import score


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Repository:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY, created_at TEXT NOT NULL,
                    synthetic INTEGER NOT NULL DEFAULT 0 CHECK(synthetic IN (0,1))
                );
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
                    created_at TEXT NOT NULL, kind TEXT NOT NULL, module TEXT,
                    detail TEXT NOT NULL, dedupe_key TEXT,
                    UNIQUE(session_id, dedupe_key)
                );
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
                    module TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('quiz','practice')),
                    number INTEGER NOT NULL, created_at TEXT NOT NULL,
                    UNIQUE(session_id,module,kind,number)
                );
                CREATE TABLE IF NOT EXISTS assistance (
                    run_id TEXT NOT NULL REFERENCES runs(id), question_id TEXT NOT NULL,
                    PRIMARY KEY(run_id,question_id)
                );
                CREATE TABLE IF NOT EXISTS attempts (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    question_id TEXT NOT NULL, selected TEXT NOT NULL,
                    correct INTEGER NOT NULL CHECK(correct IN (0,1)),
                    assisted INTEGER NOT NULL CHECK(assisted IN (0,1)), created_at TEXT NOT NULL,
                    UNIQUE(run_id,question_id)
                );
                CREATE TABLE IF NOT EXISTS coach_metrics (
                    id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
                    module TEXT NOT NULL, question_id TEXT, route TEXT NOT NULL,
                    created_at TEXT NOT NULL, provider_mode TEXT NOT NULL CHECK(provider_mode='placeholder'),
                    elapsed_ms REAL NOT NULL CHECK(elapsed_ms>=0),
                    api_requests INTEGER NOT NULL CHECK(api_requests=0),
                    api_cost_usd REAL NOT NULL CHECK(api_cost_usd=0),
                    input_tokens INTEGER, output_tokens INTEGER,
                    CHECK(input_tokens IS NULL AND output_tokens IS NULL)
                );
                CREATE INDEX IF NOT EXISTS events_session ON events(session_id);
                CREATE INDEX IF NOT EXISTS metrics_session ON coach_metrics(session_id);
            """)

    def create_session(self, session_id: str, synthetic: bool = False) -> None:
        with self.connection() as db:
            db.execute("INSERT OR IGNORE INTO sessions VALUES (?,?,?)", (session_id, utc_now(), int(synthetic)))

    def event(self, session: str, kind: str, module: str | None = None,
              detail: dict | None = None, dedupe: str | None = None) -> None:
        """Callers pass structural metadata only, never messages or exception strings."""
        with self.connection() as db:
            db.execute("INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?)",
                       (str(uuid4()), session, utc_now(), kind, module, json.dumps(detail or {}), dedupe))

    def current_run(self, session: str, module: str, kind: str = "quiz") -> str:
        with self.connection() as db:
            row = db.execute("SELECT id FROM runs WHERE session_id=? AND module=? AND kind=? ORDER BY number DESC LIMIT 1",
                             (session, module, kind)).fetchone()
        return row["id"] if row else self.new_run(session, module, kind)

    def new_run(self, session: str, module: str, kind: str = "quiz") -> str:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            number = db.execute("SELECT COALESCE(MAX(number),0)+1 FROM runs WHERE session_id=? AND module=? AND kind=?",
                                (session, module, kind)).fetchone()[0]
            run = str(uuid4())
            db.execute("INSERT INTO runs VALUES (?,?,?,?,?,?)", (run, session, module, kind, number, utc_now()))
        return run

    @staticmethod
    def _owned(db, session: str, run: str):
        row = db.execute("SELECT * FROM runs WHERE id=? AND session_id=?", (run, session)).fetchone()
        if row is None:
            raise ValueError("This quiz is not part of the current session.")
        return row

    def mark_assisted(self, session: str, run: str, question_id: str) -> None:
        with self.connection() as db:
            self._owned(db, session, run)
            db.execute("INSERT OR IGNORE INTO assistance VALUES (?,?)", (run, question_id))
            # Asking after submitting never rewrites a historical score.

    def is_assisted(self, session: str, run: str, question_id: str) -> bool:
        with self.connection() as db:
            self._owned(db, session, run)
            return db.execute("SELECT 1 FROM assistance WHERE run_id=? AND question_id=?", (run, question_id)).fetchone() is not None

    def submit(self, session: str, run: str, question: dict, selected: str) -> dict:
        """First submission wins. A duplicate returns the original attempt."""
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            owner = self._owned(db, session, run)
            if question["concept"] != owner["module"]:
                raise ValueError("Question does not belong to this module.")
            old = db.execute("SELECT * FROM attempts WHERE run_id=? AND question_id=?", (run, question["id"])).fetchone()
            if old:
                return dict(old)
            assisted = db.execute("SELECT 1 FROM assistance WHERE run_id=? AND question_id=?", (run, question["id"])).fetchone() is not None
            result = score(question, selected, assisted)
            db.execute("INSERT INTO attempts VALUES (?,?,?,?,?,?,?)",
                       (str(uuid4()), run, question["id"], result.selected, int(result.correct), int(result.assisted), utc_now()))
            return dict(db.execute("SELECT * FROM attempts WHERE run_id=? AND question_id=?", (run, question["id"])).fetchone())

    def attempts(self, session: str, run: str) -> list[dict]:
        with self.connection() as db:
            self._owned(db, session, run)
            return [dict(r) for r in db.execute("SELECT * FROM attempts WHERE run_id=? ORDER BY created_at,id", (run,))]

    def record_coach(self, session: str, module: str, question_id: str | None, route: str, elapsed_ms: float) -> None:
        with self.connection() as db:
            db.execute("INSERT INTO coach_metrics VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                       (str(uuid4()), session, module, question_id, route, utc_now(), "placeholder", elapsed_ms, 0, 0.0, None, None))

    def export(self, session: str) -> dict:
        """Export only this anonymous session; free-text chat is never persisted."""
        with self.connection() as db:
            row = db.execute("SELECT * FROM sessions WHERE id=?", (session,)).fetchone()
            if row is None:
                raise ValueError("Unknown session.")
            events = [dict(r) for r in db.execute("SELECT * FROM events WHERE session_id=? ORDER BY created_at,id", (session,))]
            for event in events:
                event["detail"] = json.loads(event["detail"])
            return {"schema_version": 1, "session": dict(row), "events": events,
                    "runs": [dict(r) for r in db.execute("SELECT * FROM runs WHERE session_id=? ORDER BY created_at,id", (session,))],
                    "attempts": [dict(r) for r in db.execute("SELECT a.* FROM attempts a JOIN runs r ON a.run_id=r.id WHERE r.session_id=? ORDER BY a.created_at,a.id", (session,))],
                    "assistance": [dict(r) for r in db.execute("SELECT a.* FROM assistance a JOIN runs r ON a.run_id=r.id WHERE r.session_id=?", (session,))],
                    "coach_metrics": [dict(r) for r in db.execute("SELECT * FROM coach_metrics WHERE session_id=? ORDER BY created_at,id", (session,))]}

    def reset(self, session: str) -> None:
        """Delete only this session's records; other learners are untouched."""
        with self.connection() as db:
            db.execute("DELETE FROM assistance WHERE run_id IN (SELECT id FROM runs WHERE session_id=?)", (session,))
            db.execute("DELETE FROM attempts WHERE run_id IN (SELECT id FROM runs WHERE session_id=?)", (session,))
            for table in ("runs", "events", "coach_metrics"):
                db.execute(f"DELETE FROM {table} WHERE session_id=?", (session,))
            db.execute("DELETE FROM sessions WHERE id=?", (session,))
