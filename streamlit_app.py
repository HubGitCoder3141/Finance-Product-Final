"""Run with: python -m streamlit run streamlit_app.py"""

import os
from pathlib import Path
from uuid import uuid4
import streamlit as st

from coach_app.components import navigate
from coach_app.curriculum import load
from coach_app.pages import home, lesson, measurements
from coach_app.storage import Repository


def main() -> None:
    st.set_page_config(page_title="Probability · AI Learning Coach", page_icon="◒", layout="centered", initial_sidebar_state="expanded")
    modules = load()["modules"]
    root = Path(__file__).resolve().parent
    repo = Repository(os.environ.get("COACH_DB_PATH", str(root / "runtime" / "coach.sqlite3")))
    session = st.session_state.setdefault("session_id", str(uuid4()))
    repo.create_session(session)
    st.session_state.setdefault("page", "expected_value")
    st.session_state.setdefault("section", "Definition")
    with st.sidebar:
        st.markdown("### ◒ Probability lab")
        st.caption("Small steps toward clearer thinking.")
        st.button("Home · learning path", on_click=navigate, args=("Home",), key="nav_home", width="stretch")
        st.divider()
        for i, module in enumerate(modules):
            st.button(f"{i+1:02d}  {module['title']}", key=f"nav_{module['id']}",
                      type="primary" if st.session_state.page == module["id"] else "secondary",
                      on_click=navigate, args=(module["id"],), width="stretch")
        st.divider()
        st.button("Progress & measurements", on_click=navigate, args=("Measurements",), key="nav_measurements", width="stretch")
        st.caption("Demo only · no live AI calls")
        with st.expander("Reset my progress"):
            st.write("Deletes this session's stored activity, quiz attempts, selections, and conversations. Other learners are unaffected. Export first if you want to keep your results.")
            confirm = st.checkbox("I want to clear my session", key="confirm_reset")
            if st.button("Clear my progress", disabled=not confirm, key="reset_progress"):
                repo.reset(session)
                st.session_state.clear()
                st.rerun()
    if st.session_state.page == "Home":
        home(modules, repo, session)
    elif st.session_state.page == "Measurements":
        measurements(repo, session)
    else:
        module = next(m for m in modules if m["id"] == st.session_state.page)
        lesson(module, modules, repo, session)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never show SQL, paths, raw exception messages, or configuration values.
        # Streamlit's rerun/stop signals inherit BaseException and pass through.
        try:
            if "session_id" in st.session_state:
                error_repo = Repository(os.environ.get("COACH_DB_PATH", str(Path(__file__).resolve().parent / "runtime" / "coach.sqlite3")))
                error_repo.event(st.session_state.session_id, "application_error", detail={"code": "render_failed"})
        except Exception:
            pass  # An unavailable database must not mask the safe learner error.
        st.error("The learning content or local storage is unavailable. Please retry. If this continues, check the setup guide or contact the app maintainer.")
