# Requirements traceability

## Source review

All four supplied documents were read before implementation. The PRD's six PDF pages (including its blank final page) and the one-page technology PDF were extracted and visually inspected. The PRD page 1 diagram was inspected as an image, including its home tiles, collapsible module navigation, lesson progression, progress indicator, question access, and visual/reading/audio presentation matrix. Both Word documents were read in full, including their tables and checklist; their packages contain no embedded images or attached files. The Word text extraction included all document paragraphs and relevant XML parts, rather than relying on a table of contents. No narration recordings were supplied.

| Short name | Exact supplied file | Source scope used |
|---|---|---|
| PRD | `Product Requirement Document (PRD)_HAI_AI_Learning_Coach_Aug2026.pdf` | v1.0, 25 Aug 2026; pp. 1–5 interface and lessons, p. 6 blank |
| Brief | `Week-1-Brief-Design.docx` | v1.0; learner assumptions, concept map, golden-set fields, refusal cases, completed design context |
| Proposal | `AI-Learning-Coach-Probability-ProjectDocument.docx` | v3.0, 5 Aug 2026; §4 fixed curriculum, §4.2 refusals, §§3/6/7 measures/deliverables, §§9/12 stack/budget |
| Stack | `Module1_ExpectedValue_ProjectDocument - TechStack.pdf` | p. 1 technology/deployment table |

The original files are preserved unchanged in the workspace. They are not required at runtime or silently replaced by this document. Repository consumers can identify the design sources without redistributing the supplied originals.

## Precedence and resolved inconsistencies

The master prompt overrides proposal programme constraints, then PRD detail, then Stack, then Brief process. This is the build week; the Brief's “no code” instruction did not restart planning. No further planning approval was requested.

- **Four versus six:** Proposal §4 names and limits the curriculum to four concepts. Six-concept references in the proposal and golden-set wording are treated as inconsistent editing remnants. Only the four named concepts are implemented.
- **Marble arithmetic:** PRD p. 4 incorrectly uses seven as the count of blue marbles. Lessons use three blue among ten, P(blue)=3/10; subsequent dependent draw is 2/9.
- **Prepared examples versus submitted problems:** Worked examples and guided explanations are authored instructional material. Coach responses scaffold the method without solving submitted homework or assessment problems.
- **Live model references:** PRD chat connection, Stack question models, model-as-judge, and proposal SDK choices are future integration context. The master prompt explicitly requires a placeholder, which cannot call any provider.
- **Model identifiers:** Names in the documents are not assumed valid API identifiers and do not appear as live configuration defaults.
- **Evidence and history:** No student transcripts, interviews, Week 3 baseline, or improvement measurements were invented. Evaluation fixtures identify authored text and limited research provenance. Blank recording templates support future real work.
- **Base-rate interpretation:** The Brief's simplified “beats a clue” phrasing is taught as combining prevalence with evidence strength, not claiming prevalence always dominates.

## Implementation and verification matrix

Paths below are repository-relative. Test names refer to concrete executable tests, not proposed checks.

| Requirement / source | Implementation | Verification | Limitation or decision |
|---|---|---|---|
| Complete runnable build; master §§1, 4, 16 | `streamlit_app.py`, `requirements*.txt`, `.streamlit/` | `test_app.py`; actual Streamlit launch | External Cloud publication not performed |
| Python 3.12, Streamlit, SQLite, pytest, JSON; Stack p.1 / Proposal §9 | `coach_app/`, `.python-version`, CI | Python 3.12.11 execution; dependency compatibility check | Standard library replaces extra service dependencies |
| Home, four tiles, search, outcomes; PRD pp.1–2 | `pages.home`, sidebar in entrypoint | `test_navigation_preserves_quiz_choice_and_events` | Expected Value opens first per master; Home is always reachable |
| Module and section navigation; PRD p.1 diagram | `pages.lesson`, `components.navigate` | All four parametrized module journeys | Native collapsible sidebar; no invented duration estimates |
| Real session progress, reset; master §6 | `completion_modules`, `Repository.reset` | Session reset and separation tests | Anonymous connection only, no account recovery |
| Plain + technical definitions; PRD p.2 | `data/curriculum.json`, `curriculum.validate` | `test_complete_curriculum`, content fault tests | Learner age/session length remain unspecified assumptions |
| Formula, each symbol, glossary; PRD p.3 | Equation section, symbol expanders | AppTest checks all formula pages | Expanders replace hover pop-ups; compact base-rate notation defined |
| Visuals and manipulatives; PRD pp.2–4 / master §7 | `interactives.py`, authored tables | `test_interactives_and_invalid_total`, `test_math.py` | Theoretical calculations; no simulation needed |
| Narration and matched text; PRD pp.2–4 | `narration` in JSON, disabled control | Complete-content test; browser inspection | No recordings; no paid voice generation |
| Auto-scroll and synchronized highlighting; PRD pp.3–4 | User-selected sections and glossary controls | Navigation tests, browser layout check | No automatic movement, voice tone/speed, or glow animation without audio |
| Worked and guided examples with nonblocking errors; PRD p.4 | `worked`, `guided`, `pages.guided` | All four guided journeys; math examples | Prepared examples do not represent learner submissions |
| EV weighted sum, non-outcome expectation; Proposal §4 / master §7.1 | EV JSON, `expected_value`, EV interactive | `test_verified_examples`, invalid distribution cases | Finite distributions only |
| Independence, replacement, “due” misconception; Brief §§3/5 | Independence JSON, `second_blue`, `independent` | Math tests and full module journey | Assumes uniform draws/remixing and independent fair coin as stated |
| Conditional sample restriction, reversal, nonzero denominator | Conditional JSON, `from_counts`, `conditional` | Numeric, zero-denominator, reversal fixtures | Equally likely countable populations used |
| Base rates, natural frequencies, both evidence and prior | Base-rate JSON, `frequencies` | Natural-frequency expectations and boundary tests | Fictional scanner; no medical or financial advice |
| Five increasingly difficult MCQs/module; PRD pp.2/4–5 | 20 core JSON questions | Independent answer-key review and schema tests | Difficulty is an authored ordinal, not psychometric calibration |
| Assistance invalidates unassisted credit; PRD p.5 | `assistance` table, scoring, active-question context | Scoring tests, quiz+coach AppTest | Still awards separate assisted-correct feedback |
| Duplicate prevention, retry, results | Unique run/question key; immutable first submission | `test_duplicate_retry_assistance_and_persistence` | Same-question retry disclosed as prior exposure |
| More practice; PRD p.5 | Eight authored additional questions | Full journeys exhaust practice in each module | Finite bank; no unseen items after exhaustion |
| Ask a Question during lecture; PRD pp.1/5 | Coach expander on every module section | Coach supported/unsupported journey | Always prominently disclosed as demo |
| Chat history, context, send, reset, errors; master §9 | `components.coach_panel` | Chat/limit/reset tests; sanitized service error test | 20 exchanges/module in memory, 80 replies/session |
| Clarification, follow-up, hint, refusals, fallback | `PlaceholderCoach`, 14 fixtures | `test_evaluation_cases_without_network` | Keyword routing; does not validate a future model's robustness |
| No live requests or key activation; master §9.3 | No live provider code or SDK; ignored future key config | Socket-blocked evaluation with key and live env set | Future integration requires code changes and a separate enablement gate |
| Session, interaction, attempt, completion records; master §10 | `storage.py` tables | Repository idempotency, persistence, session/export tests | Local SQLite only |
| Honest timing/cost/token metrics; Proposal §3 / master §10 | `instrumentation.py`, `coach_metrics` constraints | Controlled-clock timing and no-text tests | Local service duration, not model or browser latency |
| Teaching-quality measurement goal | Misconception fields, immediate quiz summary, rubric/template | Provenance/fixture tests | No long-term study, validated rubric scores, or model-as-judge claims |
| $20 total / $5 prototype budget; Proposal §12 | README, dashboard, architecture, future boundary | Source review and document consistency | This runtime has zero model API cost |
| Export and cloud persistence disclosure | Session JSON download, README, deployment guide | JSON roundtrip, session isolation, AppTest download control | No durable hosting guarantee or import |
| Synthetic demonstration separation | `seed_demo.py`, separate synthetic database/session | Synthetic idempotency test | No fabricated timings or quiz performance |
| Research-informed golden-set structure; Brief §6 | `evaluation_cases.json`, provenance fields | 14-case fixture harness and provenance tests | Two research-informed authored inputs, twelve software fixtures; no participant quotations |
| Credentials, SQL, HTML, connection hygiene | `.gitignore`, dummy config, parameterized SQL, safe text | Injection string and secret-absence tests | Not an authentication/anti-abuse platform |
| Tests, clean startup, GitHub readiness; master §§13–14 | `tests/`, workflow, requirements and docs | Recorded local suite and startup | CI definition provided; hosted Actions run not claimed |
| Deployment-specific verification; master §15 | `docs/deployment.md` | Official Streamlit docs checked 2026-09-11 | Actual deployment depends on user's repository/account |
| Improvement log and baseline structures; Proposal D4/D5 | `docs/improvement-log.md`, template JSON | Template fields inspected | Blank until actual measurements are collected |

## Acceptance reading

Implementation covers the locally verifiable prototype scope. Live AI and unavailable narration are explicit boundaries. Cloud deployment, real-learner effectiveness research, assistive-technology audits, and hosted CI execution must be verified in their own environments; this repository does not present them as completed work.
