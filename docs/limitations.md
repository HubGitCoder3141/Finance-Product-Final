# Known limitations and future integration boundary

## Material prototype limits

- The coach is a keyword-routed, locally authored demonstration. It does not understand arbitrary language. Its few refusal cases demonstrate interface behavior and do not establish robust natural-language refusal performance. No Claude or other live model is connected.
- No narration assets were supplied. Audio is visibly unavailable; complete narration text is included. There is no synchronized highlighting, adjustable voice, or automatic scrolling. Native section navigation and symbol expanders provide controlled, accessible alternatives.
- SQLite is demonstration storage on the app host, not durable production storage. A browser reconnection may lose the anonymous session link; Cloud restarts and redeployments may lose files. Export during the session. There is no authentication, import, cross-device history, or old-session recovery UI.
- Core retries repeat the same questions. Additional practice has two authored questions per module. Neither retry accuracy nor the local scripted fixture score proves sustained learning or future model teaching quality.
- The dashboard measures actual local provider execution only; it excludes browser round-trip and database latency. Tokens are unavailable, API requests and cost are zero.
- Two fixtures are research-informed authored inputs; the rest are labeled software fixtures. No learner interviews, recorded role-play, empirical golden-set collection, historical baseline, or improvement results are fabricated.
- Native controls and text alternatives were used and browser layouts were checked. This does not constitute a certified accessibility audit, screen-reader study, or validation across every browser/device.
- Session-level limits bound ordinary messages/history. They are not authentication, global traffic throttling, retention scheduling, or a multi-instance abuse defense. The prototype is intentionally small and single-host.
- Cloud deployment and GitHub Actions execution require a real repository/account. Only local tests and the local server were run for delivery; no published URL is claimed.

## Future Claude boundary

The current coach is intentionally a placeholder because this build must work with no API key, no model requests, and no API charges. `CoachService` in `coach_app/coach.py` is the provider interface. A future Anthropic implementation would belong in a separate module, for example `coach_app/providers/anthropic.py`, introduced by an explicitly reviewed implementation change. That file does not exist or get imported in this build.

Secrets belong in local environment variables or ignored `.streamlit/secrets.toml`, and in Cloud's secrets settings when deployed. The examples contain dummy values only. A key alone must never turn on live mode: an explicit configuration gate, a reviewed provider factory, and operator enablement are required. This build reads neither the key nor the provider environment setting and always uses `PlaceholderCoach`.

Before enabling a future provider:

1. Verify currently available Anthropic API model identifiers and prices against official documentation. Do not assume names in the source documents are valid API identifiers.
2. Introduce an explicit opt-in mode, typed request/response boundary, timeout, retry/backoff policy, error redaction, context bounds, and per-session/global request limits. Test startup with no key and with disabled live mode.
3. Track actual provider token usage and prices with version/date provenance, total request count, latency, and cost. Include evaluator/model-as-judge traffic. Enforce budget stops against the $20 total / $5 initial allocation before calls, not just after an overrun.
4. Validate refusal behavior against varied and adversarial submitted-problem and betting-advice requests. Preserve helpful method scaffolds without leaking active quiz answers. A keyword-router fixture pass is insufficient evidence.
5. Evaluate teaching with human-reviewed misconception cases, independent transfer tasks, and delayed assessments. Validate any automated judge against human disagreement and track its cost separately.
6. Establish data consent and retention before persisting or transmitting learner text. Confirm what reaches the provider, and keep secrets and unnecessary personal information out of logs.
7. Add integration tests with a controlled mock provider, then explicitly authorized bounded live checks. Verify costs, timeouts, failure recovery, session isolation, and opt-out behavior.

No part of this list is represented as an already completed live integration.
