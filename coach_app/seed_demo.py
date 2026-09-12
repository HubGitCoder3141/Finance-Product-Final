"""Load optional synthetic records into a separate database, never the live app DB."""

import argparse
import json
from pathlib import Path
from coach_app.curriculum import DATA_DIR
from coach_app.storage import Repository


def seed(path: Path) -> dict:
    repo = Repository(path)
    session = "synthetic-demo-session"
    repo.create_session(session, synthetic=True)
    fixture = json.loads((DATA_DIR / "synthetic_activity.json").read_text(encoding="utf-8"))
    for i, e in enumerate(fixture["events"]):
        repo.event(session, e["kind"], e["module"], e["detail"], dedupe=f"synthetic:{i}")
    return repo.export(session)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("exports/synthetic-demo.json"))
    args = parser.parse_args()
    records = seed(Path("runtime/synthetic-demo.sqlite3"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Synthetic session exported to {args.output}. No timing or learning measurements were fabricated.")
