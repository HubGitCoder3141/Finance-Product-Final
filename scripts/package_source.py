"""Create a source-only ZIP with an explicit allowlist; never include runtime data."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent
FILES = ["streamlit_app.py", "README.md", "requirements.txt", "requirements-dev.txt",
         "requirements-verified.txt", "pyproject.toml", ".python-version", ".gitignore", ".env.example",
         ".streamlit/config.toml", ".streamlit/secrets.example.toml", ".github/workflows/tests.yml"]
DIRECTORIES = ["coach_app", "data", "tests", "docs", "scripts"]


def package() -> Path:
    paths = [ROOT / name for name in FILES]
    for directory in DIRECTORIES:
        paths.extend(p for p in (ROOT / directory).rglob("*") if p.is_file()
                     and "__pycache__" not in p.parts and p.suffix in {".py", ".json", ".md"})
    output = ROOT / "deliverables" / "ai-learning-coach-probability.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(path, path.relative_to(ROOT).as_posix())
    return output


if __name__ == "__main__":
    print(package())
