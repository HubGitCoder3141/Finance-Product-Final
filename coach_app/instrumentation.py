"""Measure actual local service time, without inventing model usage."""

from time import perf_counter
from coach_app.coach import CoachService, Reply
from coach_app.storage import Repository


def measured_reply(service: CoachService, repository: Repository, session: str,
                   module: str, message: str, question_id: str | None = None) -> Reply:
    start = perf_counter()
    try:
        reply = service.respond(message, module, quiz_context=question_id is not None)
    except Exception:
        repository.event(session, "application_error", module, {"code": "coach_response_failed"})
        raise
    elapsed_ms = (perf_counter() - start) * 1000
    repository.record_coach(session, module, question_id, reply.route, elapsed_ms)
    return reply


def measurement_summary(export: dict) -> dict:
    records = export["coach_metrics"]
    return {"responses": len(records),
            "mean_local_ms": sum(r["elapsed_ms"] for r in records) / len(records) if records else None,
            "api_requests": sum(r["api_requests"] for r in records),
            "api_cost_usd": sum(r["api_cost_usd"] for r in records),
            "model_tokens": None, "provider_mode": "placeholder"}
