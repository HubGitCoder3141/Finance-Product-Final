# Streamlit Community Cloud deployment

This repository is prepared for deployment; no GitHub publication or cloud deployment was performed. You control the repository and hosting account. Instructions were checked against current official documentation on 2026-09-11.

## Prepare the repository

Run the tests locally first. The repository root must contain `streamlit_app.py`, `requirements.txt`, `coach_app/`, `data/`, and `.streamlit/config.toml`. Include the tests and documentation for maintainability. No system packages, model SDKs, or external database are required. Source PDFs/DOCX files are not runtime dependencies.

Use your own GitHub repository. From this folder, review `.gitignore`, then initialize and commit the source if it is not already a repository:

```bash
git init
git add streamlit_app.py coach_app data tests docs scripts README.md requirements.txt requirements-dev.txt requirements-verified.txt pyproject.toml .python-version .gitignore .env.example .streamlit/config.toml .streamlit/secrets.example.toml .github/workflows/tests.yml
git diff --cached --stat
git diff --cached
git commit -m "Build probability learning coach prototype"
```

Create an empty GitHub repository in your own account, then follow GitHub's displayed instructions for adding its real remote and pushing your branch. This guide intentionally does not invent a repository URL. Never add `.env`, `.streamlit/secrets.toml`, runtime databases, private exports, or `.venv`.

## Deploy

1. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) with access to your GitHub repository.
2. Choose **Create app**, then **Yup, I have an app** if prompted.
3. Select your actual repository, pushed branch, and **`streamlit_app.py`** as the entrypoint path.
4. In **Advanced settings**, explicitly select **Python 3.12**. Leave secrets empty and save the settings.
5. Complete the deployment action on the form and watch the build logs. Community Cloud installs dependencies from the repository configuration.

These repository/entrypoint and runtime controls are described in the official [deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy). Confirm the runtime even if the host's default changes. `.python-version` is useful locally; do not rely on it to select the Cloud runtime.

The only direct runtime package in `requirements.txt` is the pinned Streamlit version. Read the official [dependency guide](https://docs.streamlit.io/deploy/concepts/dependencies) and [file organization guidance](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization) if dependency discovery fails. Do not deploy the local Windows virtual environment. `requirements-verified.txt` is a full tested version snapshot, including development packages; the standard deployment uses `requirements.txt` and the host resolves platform-appropriate dependencies.

## Verify the deployed app

Start from a fresh browser session with no API secrets. Confirm Expected Value opens, Home reaches every module, definitions/formulas render, an invalid expected-value total shows feedback, and each interactive example works. Complete a quiz with help on one question; confirm separate assisted credit, retry, and practice exhaustion. Send a scripted clarification and unsupported message. Check a measured local response with zero API usage. Download an export before resetting that test session.

A passing local test suite is not evidence of an actual Cloud deployment. Repeat the full checklist in `docs/verification.md` on the real deployed URL and record its date, commit, environment, and outcome.

## Storage and updates

SQLite is local host storage for this demonstration, **not durable production persistence**. Treat files as disposable across restarts, rebuilds, and redeployments. Session-state UUIDs and chat histories may also disappear when a connection ends. Export records during the demo; no authenticated recovery or progress import is implemented.

Push changes to the deployed branch to update the app. Recheck dependencies and rerun the smoke journey after changes. If a rebuild is required, the official [reboot guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/reboot-your-app) describes the workspace overflow menu's **Reboot** action and warns that it interrupts active users. Export first. This application does not claim that a reboot preserves its local database.

If package installation fails, inspect Cloud logs, confirm Python 3.12 and the entrypoint, then check the committed requirements file. Do not add secrets to resolve a placeholder-coach issue: this build does not use any key.
