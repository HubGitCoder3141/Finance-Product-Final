"""Load and validate locally authored JSON before displaying any lessons."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODULE_IDS = ("expected_value", "independence", "conditional_probability", "base_rates")


def validate(data: dict) -> dict:
    """Raise a content error early rather than render a partly valid lesson."""
    try:
        modules = data["modules"]
        if not isinstance(modules, list) or [m["id"] for m in modules] != list(MODULE_IDS):
            raise ValueError("The curriculum must contain the four ordered concepts.")
        ids: set[str] = set()
        for module in modules:
            for field in ("title", "summary", "prerequisites", "plain", "technical", "formula", "worked", "narration"):
                if not isinstance(module[field], str) or not module[field].strip():
                    raise ValueError(f"Missing lesson text: {field}")
            if (not isinstance(module["outcomes"], list) or not module["outcomes"]
                    or not all(isinstance(o, str) and o.strip() for o in module["outcomes"])
                    or not isinstance(module["symbols"], dict) or not module["symbols"]
                    or not all(isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip()
                               for k, v in module["symbols"].items())
                    or not isinstance(module["table"], list) or not module["table"]
                    or not isinstance(module["guided"], list) or len(module["guided"]) < 2):
                raise ValueError("Missing instructional structure.")
            for step in module["guided"]:
                if not step["prompt"] or not step["explanation"] or step["answer"] not in step["options"]:
                    raise ValueError("Invalid guided example.")
            if len(module["quiz"]) != 5 or len(module["practice"]) < 2:
                raise ValueError("Each module needs five core and at least two practice questions.")
            if [q["difficulty"] for q in module["quiz"]] != [1, 1, 2, 2, 3]:
                raise ValueError("Core difficulty must progress from introductory to interpretation.")
            for q in module["quiz"] + module["practice"]:
                if q["id"] in ids or q["concept"] != module["id"]:
                    raise ValueError("Duplicate question id or wrong concept.")
                ids.add(q["id"])
                opts = q["options"]
                if not isinstance(opts, list) or len(opts) < 3 or len(set(opts)) != len(opts):
                    raise ValueError("Questions need distinct answer options.")
                if q["answer"] not in opts or set(q["feedback"]) != set(opts):
                    raise ValueError("Answer and misconception feedback must map to every option.")
                if not all(isinstance(o, str) and o.strip() for o in opts) or not all(
                        isinstance(v, str) and v.strip() for v in q["feedback"].values()):
                    raise ValueError("Options and feedback must contain readable text.")
                if q["difficulty"] not in (1, 2, 3) or q["assisted"] is not False:
                    raise ValueError("Invalid default question state.")
                for field in ("text", "hint", "explanation"):
                    if not isinstance(q[field], str) or not q[field].strip():
                        raise ValueError(f"Missing question field: {field}")
        return data
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("Malformed curriculum structure.") from exc


def load(path: Path | None = None) -> dict:
    try:
        return validate(json.loads((path or DATA_DIR / "curriculum.json").read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("The local curriculum file could not be read.") from exc
