# Verification record and repeatable checks

## Local execution record

Verified on 2026-09-11 on Windows with **Python 3.12.11**, **Streamlit 1.58.0**, and **pytest 8.4.2**. See `requirements-verified.txt` for all installed package versions.

| Check actually run | Result |
|---|---|
| `python -m pytest -q` | **57 passed**; includes mathematical, schema, repository, coach, instrumentation, export/seed, and Streamlit AppTest journeys |
| `python -m coach_app.evaluate` | **14/14 expected routes passed**, zero model requests/cost, unavailable token counts |
| `uv pip check --python .venv/Scripts/python.exe` | **All 48 installed packages compatible** |
| `python -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501` | Server started and app rendered in the in-app browser |
| `python -m coach_app.seed_demo` | Separate labeled synthetic database/export produced; no fabricated timings |
| AppTest cold startup with temporary DB and no key | Passed, including idempotent table creation and default Expected Value |
| Socket-blocked coach fixture test with dummy key and requested live mode | Passed; no live provider activated or connection made |
| Source ZIP extracted into a fresh directory, then `python -m pytest -q` | **57 passed** from the extracted source; one Windows sandbox warning prevented writing pytest's optional cache |
| Clean extracted app startup with default DB location and no secrets | Passed; `runtime/coach.sqlite3` created automatically and no UI errors |
| Source-only ZIP allowlist inspection | 43 source/config/documentation files; no PDF/DOCX originals, secrets, database, export, cache, or virtual environment |

AppTest exercises every module's equation, guided steps, correct and incorrect quiz answers, assistance, completion, review, retry, and finite practice exhaustion. It also verifies interactive inputs, invalid totals, coach context, supported and unsupported messages, message limits, reset, distinct session IDs, retained quiz selections after navigation, and export-control availability. Repository tests verify export contents and isolation independently of the download control.

During verification, an AppTest case needed an explicit intermediate rerun to consume its preceding form trigger, matching normal browser behavior. The adjusted test passed. A long-running development server later showed an importlib/pandas NameError after source edits. A fresh server was used for final browser checks. Unexpected rendering errors now have a generic error message and a sanitized event code, verified by an injected-failure test. The final suite has no failing tests. No earlier incomplete run is counted as successful evidence.

## Browser and accessibility scope

The running application was inspected through the in-app browser. Desktop lesson layout and 390 × 844 phone-width equation/section navigation were visually reviewed. The phone-width page reported a 390-pixel document width in a 390-pixel viewport. Labels, expandable glossary, collapsed mobile sidebar, and formula rendering were checked. The app uses Streamlit's native keyboard-accessible controls and text equivalents for charts.

These are bounded visual and functional checks, not a certified WCAG audit or screen-reader evaluation. Native increment/decrement controls are supplied by Streamlit. Hosted browser behavior and all device combinations are not inferred from local AppTest success.

## Repeat locally

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -m pytest -q
python -m coach_app.evaluate
python -m streamlit run streamlit_app.py
```

The tests always use temporary SQLite files and do not delete real learner databases. The application test harness sets `COACH_DB_PATH` and removes the model key for startup. The explicit no-network service test patches socket connections and sets dummy configuration to verify the strict provider boundary.

## End-to-end checklist for future changes or deployment

1. Start a clean copy with Python 3.12, no secrets, and no runtime database. Confirm Expected Value and no error state.
2. Open Home, search a matching term and a nonmatching term, then open every module. Confirm title, outcome, current section, and return/next navigation.
3. On Expected Value, submit probabilities totaling 0.9 and see validation; then use 0.4/0.6 and get 6.00 minutes. Compare replacement and no replacement. Restrict the club table to music and see 6/18. Set prevalence to 10% with 90%/10% clue rates and see 50%.
4. In each module's Examples, submit one incorrect guided answer and review the explanation; submit correct steps and confirm you can continue without a lock.
5. Begin a quiz. Try an empty submission, a correct answer, and an incorrect answer. Confirm an answered question cannot be rescored accidentally.
6. Ask for a hint or open the question-specific coach on a different question. Submit correctly and confirm assisted-correct increments while unassisted-correct does not.
7. Complete all five questions, open results explanations, revisit Examples, then retry. Confirm fresh selection/assistance state and retained historical attempts in the export.
8. Finish both additional practice questions. Confirm the exhaustion message and no fabricated new questions.
9. Send “explain this concept,” “hint,” an unsupported phrase, a request to solve homework, and a real-betting request to the demo. Verify disclosure, routes, history, and useful method guidance. Check that an active quiz receives no final answer from the coach.
10. Reset conversation, confirm history clears while timing/assistance remain. Export from measurements, verify only the current session's data and no free-text messages. Explicitly reset progress, confirm a new session and empty prior scores. Use a second connection to confirm isolation.

## External checks not run

No GitHub repository was published, no hosted Actions job was triggered, and no Community Cloud app was deployed. Cloud instructions were checked against official docs, but a real deployment smoke test must still be run after publication. No paid/live model test, learner interview, delayed-learning study, or model-as-judge evaluation was performed or required for this placeholder build.
