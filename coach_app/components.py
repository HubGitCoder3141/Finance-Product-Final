"""Reusable Streamlit components using supported APIs only."""

import json
from time import monotonic
import streamlit as st

from coach_app.coach import LABEL, PlaceholderCoach
from coach_app.instrumentation import measured_reply
from coach_app.quiz import summarize


def navigate(page: str, section: str = "Definition") -> None:
    st.session_state.page = page
    st.session_state.section = section


def score_cards(attempts: list[dict]) -> None:
    summary = summarize(attempts)
    cols = st.columns(3)
    for col, label, field in zip(cols, ("Unassisted correct", "Assisted correct", "Incorrect"),
                                 ("unassisted_correct", "assisted_correct", "incorrect")):
        col.metric(label, summary[field])


def coach_panel(repo, session: str, module: dict) -> None:
    """An active unfinished quiz question remains linked even after navigation."""
    mid = module["id"]
    with st.expander("Ask a Question · demo coach", expanded=st.session_state.get("coach_open", False)):
        st.info(LABEL)
        st.caption("Scripted local responses. Live responses require a Claude API key and a separately enabled integration. A key alone does nothing in this build.")
        st.write(f"**Module context:** {module['title']}")
        active = st.session_state.get("active_question")
        if active and active["module"] != mid:
            active = None
        if active and any(a["question_id"] == active["id"] for a in repo.attempts(session, active["run"])):
            active = None
        if active:
            st.caption("Help will mark your active question as assisted. The demo gives a method hint without revealing its final answer.")
        histories = st.session_state.setdefault("histories", {})
        history = histories.setdefault(mid, [])
        for message in history:
            with st.chat_message(message["role"]):
                st.text(message["text"])
        st.caption("Try: explain this concept · hint · why? · solve my homework · betting advice. Free-text messages stay in this browser session's server memory and are not saved to SQLite or exports.")
        with st.form(f"coach_form_{mid}", clear_on_submit=True):
            message = st.text_area("Your question", max_chars=1000, key=f"message_{mid}", height=85)
            send = st.form_submit_button("Send to demo coach", type="primary")
        if send:
            if not message.strip():
                st.warning("Write a question before sending.")
            elif st.session_state.get("coach_count", 0) >= 80:
                st.warning("This session has reached 80 demo responses. Keep learning in the lessons, or export and reset your progress for a new session.")
            elif monotonic() - st.session_state.get("last_send", -1000) < 0.8:
                st.warning("Please wait a moment before sending another message.")
            else:
                if active:
                    repo.mark_assisted(session, active["run"], active["id"])
                try:
                    with st.spinner("Preparing a scripted response…"):
                        reply = measured_reply(PlaceholderCoach(), repo, session, mid, message,
                                               active["id"] if active else None)
                    history.extend([{"role": "user", "text": message}, {"role": "assistant", "text": reply.text}])
                    histories[mid] = history[-40:]
                    st.session_state.last_send = monotonic()
                    st.session_state.coach_count = st.session_state.get("coach_count", 0) + 1
                    st.session_state.coach_open = True
                    st.rerun()
                except (ValueError, RuntimeError):
                    st.error("The demo response could not be prepared. Check your input and try again.")
        if st.button("Reset this conversation", key=f"reset_chat_{mid}"):
            histories[mid] = []
            repo.event(session, "conversation_reset", mid)
            st.rerun()
        st.caption("Up to 20 exchanges remain visible per module. Conversation reset clears text; recorded response timings and assistance remain until you reset progress.")


def export_button(repo, session: str) -> None:
    st.download_button("Export my progress and measurements", json.dumps(repo.export(session), indent=2),
                       file_name="probability-coach-session.json", mime="application/json", key="export_session")
