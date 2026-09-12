# AI Learning Coach for Probability

A runnable, local-first Streamlit prototype that teaches **Expected Value, Independence, Conditional Probability, and Base Rates**. All four modules include definitions, notation, interactive calculations, worked and guided examples, quizzes, and additional practice.

**Demo coach — live Claude integration is not connected.** The coach uses deterministic authored responses. No model SDK, key, external database, agent framework, or content-generation network request is used. A Claude key alone cannot activate live mode.

## Run locally

Use **Python 3.12**. Open a terminal in this repository directory.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m streamlit run streamlit_app.py
```

If activation is blocked by your shell policy, avoid changing the policy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

macOS / Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`. Expected Value opens by default. The sidebar's **Home · learning path** button opens the searchable module overview. **No secrets setup is needed.** Installation downloads packages; educational content and coach generation are local thereafter.

Runtime-only installation: `python -m pip install -r requirements.txt`. The only direct runtime dependency is Streamlit 1.58.0; pytest 8.4.2 is used for development. The standard library supplies SQLite, JSON, timing, and mathematical operations. `requirements-verified.txt` records the complete Python 3.12 environment used for verification; use `python -m pip install -r requirements-verified.txt` to reproduce those exact package versions. It includes test dependencies. Streamlit's platform-specific transitive dependencies may differ on other operating systems; CI checks Python 3.12 on Linux.

## Verify

```bash
python -m pytest -q
python -m coach_app.evaluate
python -m pip check
```

Tests create isolated temporary databases and do not need an API key. See [verification](docs/verification.md) for actual execution evidence and the manual journey checklist. A passing scripted evaluation measures fixture routing, not future model teaching quality.

## What learners can do

- Explore all four complete lessons and move among Definition, Equation, Examples, Quiz, and Practice.
- Adjust probability inputs, compare replacement rules, restrict a sample space, and change prevalence and clue rates.
- Submit each of 20 core questions once per attempt, request help, review feedback, and explicitly retry.
- Use eight additional authored practice questions; the interface explains when the finite bank is exhausted.
- Ask the demo coach for a concept explanation, follow-up, or method hint. The coach redirects submitted-problem solutions and real betting advice.
- View actual session performance and local response timings, export records, and reset their own progress.

No audio files were supplied. Narration is disabled and complete matching scripts are included. Section navigation provides controlled reading without automatic scrolling.

## Data and reset

On first startup, the app creates `runtime/coach.sqlite3` and its tables automatically. `COACH_DB_PATH` may override that location via an operating-system environment variable; `.env` is an example, not automatically loaded. Do not put a production database inside the repository.

An anonymous UUID is held in Streamlit session state. Widget reruns retain quiz selections and attempts. A new browser connection can start a new session; this prototype has no cross-device identity or authenticated recovery. Old database records are not exposed to the new session. Free-text chat remains in server memory for the current connection only; it is absent from SQLite and exports.

Use **Progress & measurements → Export my progress and measurements** to download your session as JSON. Exports contain events, runs, attempts, assistance, and response metrics. There is no progress-import function.

To clear only your own records, open **Reset my progress**, check **I want to clear my session**, then select **Clear my progress**. This also resets quiz selections and conversations. Other sessions remain unchanged.

For a whole local database reset, stop Streamlit with Ctrl+C, then remove just this application database (this deletes all locally stored sessions):

```powershell
# PowerShell, from the repository root
Remove-Item -LiteralPath .\runtime\coach.sqlite3
```

```bash
# macOS/Linux, from the repository root
rm -- runtime/coach.sqlite3
```

Restart the app to recreate it. If you set `COACH_DB_PATH`, manage that explicit file instead.

Optional synthetic data:

```bash
python -m coach_app.seed_demo
```

This writes `runtime/synthetic-demo.sqlite3` and `exports/synthetic-demo.json`, both ignored by Git. The fixed synthetic session is labeled and separate from real learner data. It includes sample events, not fabricated response timings, learner research, or completed historical measurements. Rerunning the command does not duplicate the seed events.

## Repository map

```text
streamlit_app.py                 App entry, session bootstrap, navigation, reset
coach_app/
  pages.py                      Home, lessons, quiz/practice, measurements
  components.py                 Shared score, coach, export controls
  interactives.py               Supported Streamlit educational manipulatives
  math_logic.py                 Validated pure mathematical functions
  curriculum.py                 JSON loading and validation
  quiz.py                       Immutable scoring and completion rules
  coach.py                      Provider protocol and exclusive placeholder
  storage.py                    Idempotent SQLite schema and repository
  instrumentation.py            Actual local timing and measurement summaries
  evaluate.py                   Offline scripted routing harness
  seed_demo.py                  Separate optional synthetic activity export
data/
  curriculum.json               All lessons, narration, 20 core + 8 practice questions
  evaluation_cases.json         14 labeled authored evaluation cases
  synthetic_activity.json       Explicit synthetic event fixtures
tests/                          Mathematics, content, service, repository, AppTest journeys
docs/                           Architecture, traceability, deployment, verification, limitations
.streamlit/                     Theme and dummy secrets example
.github/workflows/tests.yml     Python 3.12 automated checks
requirements*.txt               Runtime, development, and verified version snapshot
.env.example                    Dummy future configuration / database override
.gitignore                      Excludes secrets, original source documents, runtime data
scripts/package_source.py       Rebuilds the source-only delivery ZIP
```

The four original specification documents remain unmodified in the working folder and are not needed to run the app. They are ignored by Git because they are user-supplied source material; the traceability document identifies them exactly. No repository URL is claimed and no external repository or deployment has been created.

The prepared `deliverables/ai-learning-coach-probability.zip` contains only the source, authored content, tests, and documentation. Rebuild it with `python scripts/package_source.py`. It excludes local environment files, original source documents, private exports, and runtime databases by an explicit allowlist.

## Documentation

- [Architecture and exact scoring rules](docs/architecture.md)
- [Source requirements and implementation traceability](docs/requirements-traceability.md)
- [Teaching design and evaluation provenance](docs/teaching-and-evaluation.md)
- [Streamlit Community Cloud deployment](docs/deployment.md)
- [Verification and test journeys](docs/verification.md)
- [Known limitations and future Claude boundary](docs/limitations.md)
- [Improvement log template](docs/improvement-log.md)

## Troubleshooting

**Python 3.12 not found:** install Python 3.12 from python.org, reopen your terminal, and confirm `python --version` inside the virtual environment. Do not try to specify Python as a pip dependency.

**Missing Streamlit or pytest:** use the same virtual environment interpreter for installation and execution. Run `python -m pip install -r requirements-dev.txt`.

**Port busy:** run `python -m streamlit run streamlit_app.py --server.port 8502` and use the new printed URL.

**Local storage unavailable:** verify the repository's `runtime/` folder is writable. If using `COACH_DB_PATH`, check its parent folder permissions. Do not place the SQLite file on a shared network filesystem. Stop concurrent app processes before whole-database maintenance.

**Content unavailable:** restore valid `data/curriculum.json`, run pytest, and restart. The app validates content and shows a generic error instead of exposing file paths or a traceback.

**Progress disappeared after refresh/redeployment:** anonymous connection state and cloud local disk are not durable identity/storage. Export during the session. This build deliberately does not promise account-based recovery.

**AppTest warns about a missing ScriptRunContext:** Streamlit can print this while its test harness executes outside a live browser context. Assess the pytest results and `app.exception`, not this warning alone.
