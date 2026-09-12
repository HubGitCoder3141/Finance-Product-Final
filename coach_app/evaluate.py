"""Offline fixture harness. Routing correctness is not teaching effectiveness."""

import json
from coach_app.coach import PlaceholderCoach
from coach_app.curriculum import DATA_DIR


def evaluate() -> dict:
    cases = json.loads((DATA_DIR / "evaluation_cases.json").read_text(encoding="utf-8"))["cases"]
    service = PlaceholderCoach()
    results = []
    for case in cases:
        reply = service.respond(case["learner_says"], case["concept"])
        results.append({"id": case["id"], "expected": case["expected_route"], "actual": reply.route,
                        "passed": reply.route == case["expected_route"]})
    return {"scope": "Authored placeholder routing checks only; not model quality or refusal robustness.",
            "api_requests": 0, "api_cost_usd": 0, "model_tokens": None, "results": results}


if __name__ == "__main__":
    report = evaluate()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if all(r["passed"] for r in report["results"]) else 1)
