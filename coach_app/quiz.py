"""Scoring is independent of the interface and shared with reporting."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Attempt:
    question_id: str
    selected: str
    correct: bool
    assisted: bool

    def to_dict(self) -> dict:
        return asdict(self)


def score(question: dict, selected: str, assisted: bool) -> Attempt:
    if selected not in question["options"]:
        raise ValueError("Choose one of the available answers before submitting.")
    return Attempt(question["id"], selected, selected == question["answer"], bool(assisted))


def summarize(attempts: list[dict]) -> dict:
    return {"unassisted_correct": sum(bool(a["correct"]) and not a["assisted"] for a in attempts),
            "assisted_correct": sum(bool(a["correct"]) and bool(a["assisted"]) for a in attempts),
            "incorrect": sum(not a["correct"] for a in attempts), "answered": len(attempts)}


def completed(question_ids: list[str], attempts: list[dict]) -> bool:
    return bool(question_ids) and set(question_ids) <= {a["question_id"] for a in attempts}
