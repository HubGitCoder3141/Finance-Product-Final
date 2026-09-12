"""Home, lessons, assessment, and honest local measurement views."""

import streamlit as st
from coach_app.components import coach_panel, export_button, navigate, score_cards
from coach_app.instrumentation import measurement_summary
from coach_app.interactives import render_interactive
from coach_app.quiz import completed

SECTIONS = ["Definition", "Equation", "Examples", "Quiz", "Practice"]


def completion_modules(records: dict) -> set[str]:
    return {e["module"] for e in records["events"] if e["kind"] == "quiz_completed"}


def home(modules: list[dict], repo, session: str) -> None:
    st.caption("PROBABILITY LAB / FOUR IDEAS, ONE CLEARER WAY TO THINK")
    st.title("AI Learning Coach for Probability")
    st.write("Build intuition for uncertainty. Explore an idea, work through an example, and check what you understand at your own pace.")
    st.button("Start with Expected Value", type="primary", on_click=navigate, args=("expected_value",), key="start_ev")
    st.info("Demo coach — live Claude integration is not connected. Questions receive scripted local guidance; no API key or paid service is needed.")
    records = repo.export(session)
    done = completion_modules(records)
    st.subheader("Your learning path")
    st.progress(len(done) / 4, text=f"{len(done)} of 4 quizzes completed in this session")
    st.caption("Completion means submitting every core question, regardless of score. Quiz performance is a practice signal, not evidence of lasting learning.")
    search = st.text_input("Search lessons", placeholder="Try average, sample space, or clues", key="search_lessons")
    matches = [m for m in modules if search.casefold() in (m["title"] + m["summary"] + m["plain"]).casefold()]
    if not matches:
        st.info("No matching lessons. Try a broader word or clear the search.")
    for m in matches:
        with st.container(border=True):
            st.caption(f"MODULE {modules.index(m)+1:02d}  ·  {'QUIZ COMPLETED' if m['id'] in done else 'READY TO EXPLORE'}")
            st.subheader(m["title"])
            st.write(m["summary"])
            for outcome in m["outcomes"]:
                st.write(f"• {outcome}")
            st.button(f"Open {m['title']}", key=f"open_{m['id']}", on_click=navigate, args=(m["id"],))
    with st.expander("About this learning experience"):
        st.write("Designed for learners who know basic arithmetic and fractions. This is an implementation assumption, not a researched learner profile. Start with Expected Value; conditional probability then gives the foundation for base rates. All modules remain open for review.")
        st.write("Lessons are prepared instructional material. The coach gives methods and prompts, rather than solving a submitted homework or assessment problem. No recordings were supplied; complete narration text is available within each module.")


def guided(module: dict, repo, session: str) -> None:
    st.markdown(module["guided_intro"])
    for i, step in enumerate(module["guided"]):
        key = f"guided_{module['id']}_{i}"
        saved = st.session_state.setdefault("guided_answers", {})
        previous = saved.get(key)
        choice = st.radio(step["prompt"], step["options"], index=step["options"].index(previous) if previous else None,
                          key=f"{key}_choice")
        if st.button(f"Check step {i+1}", key=f"{key}_check"):
            if choice is None:
                st.warning("Choose an answer to check this step.")
            else:
                saved[key] = choice
                repo.event(session, "guided_checked", module["id"], {"step": i+1, "correct": choice == step["answer"]})
        if key in saved:
            if saved[key] == step["answer"]:
                st.success("That's right. " + step["explanation"])
            else:
                st.info("Try this reasoning: " + step["explanation"])
    st.caption("These checks do not count toward your quiz score. You can review or continue at any time.")


def assessment(module: dict, repo, session: str, kind: str) -> None:
    questions = module[kind]
    run = repo.current_run(session, module["id"], kind)
    attempts = repo.attempts(session, run)
    by_id = {a["question_id"]: a for a in attempts}
    st.subheader("Check your understanding" if kind == "quiz" else "A little more practice")
    st.caption("Five core questions, from foundations to interpretation." if kind == "quiz" else "Two additional authored questions. This finite bank does not generate new questions.")
    st.progress(len(attempts) / len(questions), text=f"{len(attempts)} of {len(questions)} submitted")
    if completed([q["id"] for q in questions], attempts):
        repo.event(session, f"{kind}_completed", module["id"], {"run_id": run}, dedupe=f"complete:{run}")
        st.success("Quiz complete — review your reasoning below." if kind == "quiz" else "You have used every available practice question in this module. You can revisit the explanations; no unseen questions remain.")
        score_cards(attempts)
        st.caption("Only unassisted correct responses earn unassisted credit. Assistance never blocks feedback. These are immediate practice results, not a validated mastery or retention measure.")
        wrong_or_helped = [q for q in questions if not by_id[q["id"]]["correct"] or by_id[q["id"]]["assisted"]]
        if wrong_or_helped:
            st.info("Suggested review: revisit Equation and Examples, then explain the method in your own words before retrying.")
            st.button("Review the worked example", key=f"review_{kind}", on_click=navigate, args=(module["id"], "Examples"))
        for i, q in enumerate(questions):
            a = by_id[q["id"]]
            with st.expander(f"{i+1}. {'Correct' if a['correct'] else 'Incorrect'} · {'Assisted' if a['assisted'] else 'Unassisted'} — {q['text']}"):
                st.write(f"Your answer: {a['selected']}")
                st.write(f"Correct answer: {q['answer']}")
                st.write(q["explanation"])
                if not a["correct"]:
                    st.write(q["feedback"][a["selected"]])
        if kind == "quiz":
            st.warning("Retry uses the same five questions. Prior exposure can improve a retry score without demonstrating new learning. Previous attempts remain in your export.")
            if st.button("Start a fresh quiz attempt", key="retry_quiz"):
                repo.new_run(session, module["id"], kind)
                st.session_state.pop("active_question", None)
                st.rerun()
            st.button("Continue with additional practice", key="go_practice", on_click=navigate, args=(module["id"], "Practice"))
        return
    # Exactly one question is active. A submitted answer is immutable until a new run.
    index_key = f"question_index_{run}"
    index = st.session_state.setdefault(index_key, len(attempts))
    index = min(index, len(questions)-1)
    q = questions[index]
    a = by_id.get(q["id"])
    st.caption(f"QUESTION {index+1} / {len(questions)} · DIFFICULTY {q['difficulty']} OF 3")
    st.write(f"**{q['text']}**")
    if a:
        st.write(f"Your answer: {a['selected']}")
        (st.success if a["correct"] else st.info)(q["explanation"])
        st.caption("Assisted attempt" if a["assisted"] else "Unassisted attempt")
        if not a["correct"]:
            st.write(q["feedback"][a["selected"]])
        if st.button("Next question", type="primary", key=f"next_{run}_{q['id']}"):
            st.session_state[index_key] = index+1
            st.rerun()
        return
    st.session_state.active_question = {"id": q["id"], "run": run, "module": module["id"]}
    # Domain selections survive widget cleanup on page changes.
    selections = st.session_state.setdefault("quiz_selections", {})
    selection_key = f"{run}:{q['id']}"
    prior = selections.get(selection_key)
    choice = st.radio("Choose one answer", q["options"], index=q["options"].index(prior) if prior else None,
                      key=f"answer_{run}_{q['id']}")
    if choice is not None:
        selections[selection_key] = choice
    if repo.is_assisted(session, run, q["id"]):
        st.info("Assistance used · this answer cannot earn unassisted credit.")
        st.write(q["hint"])
    cols = st.columns(2)
    if cols[0].button("Show hint", key=f"hint_{run}_{q['id']}"):
        repo.mark_assisted(session, run, q["id"])
        repo.event(session, "quiz_assistance", module["id"], {"question_id": q["id"], "run_id": run}, dedupe=f"hint:{run}:{q['id']}")
        st.rerun()
    if cols[1].button("Ask a Question about this question", key=f"ask_{run}_{q['id']}"):
        repo.mark_assisted(session, run, q["id"])
        st.session_state.coach_open = True
        st.rerun()
    if st.button("Submit answer", type="primary", key=f"submit_{run}_{q['id']}"):
        if choice is None:
            st.warning("Select an answer before submitting.")
        else:
            repo.submit(session, run, q, choice)
            st.rerun()


def lesson(module: dict, modules: list[dict], repo, session: str) -> None:
    mid = module["id"]
    st.caption(f"PROBABILITY LAB / MODULE {modules.index(module)+1:02d}")
    st.title(module["title"])
    st.write(module["summary"])
    st.info("Demo coach — live Claude integration is not connected.")
    section = st.radio("Lesson section", SECTIONS, horizontal=True, key="section")
    repo.event(session, "section_visited", mid, {"section": section}, dedupe=f"visit:{mid}:{section}")
    st.caption(f"You are in {module['title']} › {section}")
    if section == "Definition":
        st.subheader("What you will be able to do")
        for outcome in module["outcomes"]:
            st.write(f"• {outcome}")
        with st.expander("Before you start · prerequisite reminder", expanded=True):
            st.write(module["prerequisites"])
        st.subheader("The idea in everyday language")
        st.write(module["plain"])
        with st.container(border=True):
            st.markdown("**The precise definition**")
            st.write(module["technical"])
        render_interactive(mid, repo, session)
    elif section == "Equation":
        st.subheader("Read the formula, one part at a time")
        st.latex(module["formula"])
        for symbol, description in module["symbols"].items():
            with st.expander(symbol):
                st.write(description)
        st.caption("Every symbol has a text explanation. Open any glossary entry with the keyboard; color is never needed to interpret the formula.")
    elif section == "Examples":
        st.markdown(module["worked"])
        st.table(module["table"])
        guided(module, repo, session)
    else:
        assessment(module, repo, session, "quiz" if section == "Quiz" else "practice")
    if section in SECTIONS[:3]:
        st.button("Continue to " + SECTIONS[SECTIONS.index(section)+1], type="primary",
                  key="next_section", on_click=navigate, args=(mid, SECTIONS[SECTIONS.index(section)+1]))
    coach_panel(repo, session, module)
    with st.expander("Narration and reading controls"):
        st.button("Narration unavailable — no recording supplied", disabled=True, key=f"audio_{mid}")
        st.caption("Complete narration script below. Read at your own pace. Section navigation replaces automatic scrolling; the app never moves your reading position on a timer.")
        st.markdown(module["narration"])
    next_index = (modules.index(module)+1) % len(modules)
    st.divider()
    if next_index:
        st.button("Next module: " + modules[next_index]["title"], key="next_module", on_click=navigate, args=(modules[next_index]["id"],))
    else:
        st.button("Return to your learning path", key="return_home", on_click=navigate, args=("Home",))


def measurements(repo, session: str) -> None:
    st.caption("PROBABILITY LAB / YOUR RECORDED ACTIVITY")
    st.title("Progress & measurements")
    data = repo.export(session)
    summary = measurement_summary(data)
    st.write("These records belong to your current anonymous session. Free-text conversations are excluded. Local cloud storage may disappear after a restart or redeployment; export results you want to keep.")
    st.subheader("Practice performance")
    score_cards(data["attempts"])
    st.caption("Cumulative attempts, including retries and additional practice. Completed modules remain marked complete after retry. Accuracy does not establish long-term learning or validate teaching quality.")
    st.subheader("Scripted response measurements")
    cols = st.columns(3)
    cols[0].metric("Local responses", summary["responses"])
    cols[1].metric("Mean local service time", "Not yet measured" if summary["mean_local_ms"] is None else f"{summary['mean_local_ms']:.3f} ms")
    cols[2].metric("Model API cost", "$0.00")
    st.caption("Provider: placeholder · API requests: 0 · model tokens: unavailable. Timing covers local response routing, excluding database writes and browser rendering. It is not model latency.")
    if data["coach_metrics"]:
        st.dataframe([{k: r[k] for k in ("created_at", "module", "route", "elapsed_ms", "provider_mode")} for r in data["coach_metrics"]], hide_index=True, width="stretch")
    else:
        st.info("No coach responses recorded yet. Ask a Question in any module to record an actual local timing.")
    st.subheader("Activity log")
    if data["events"]:
        st.dataframe([{k: e[k] for k in ("created_at", "kind", "module")} for e in data["events"]], hide_index=True, width="stretch")
    else:
        st.info("Open a module to begin recording your learning activity.")
    export_button(repo, session)
    st.caption("Project budget context: $20 API/MCP total, $5 initial prototyping allocation. This build makes zero model calls. Future accounting must include evaluations and model-as-judge calls.")
