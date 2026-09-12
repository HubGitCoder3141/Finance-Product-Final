"""Small manipulatives with textual equivalents and explicit validation."""

import streamlit as st
from coach_app.math_logic import expected_value, frequencies, from_counts, second_blue


def render_interactive(module: str, repo, session: str) -> None:
    st.subheader("Explore the idea")
    try:
        if module == "expected_value":
            st.write("Change the two probability weights. The shuttle outcomes remain 0 and 10 minutes.")
            p0 = st.number_input("Probability of 0 minutes", min_value=0.0, max_value=1.0, value=0.5, step=0.05, key="ev_p0")
            p10 = st.number_input("Probability of 10 minutes", min_value=0.0, max_value=1.0, value=0.5, step=0.05, key="ev_p10")
            if st.button("Calculate weighted average", key="calculate_ev"):
                st.session_state["ev_result"] = (p0, p10)
                repo.event(session, "interactive_calculation", module)
            if st.session_state.get("ev_result") == (p0, p10):
                value = expected_value([0, 10], [p0, p10])
                st.metric("Theoretical expected wait", f"{value:.2f} minutes")
                st.bar_chart({"Weighted minutes": [0 * p0, 10 * p10]}, x_label="Outcome index: 0 = immediate, 1 = later", y_label="Weighted minutes", color="#17685C")
                st.write(f"0 × {p0:.2f} = 0.00; 10 × {p10:.2f} = {10*p10:.2f}. Total = {value:.2f} minutes.")
                st.caption("This is a theoretical calculation, not a simulation or a promised wait.")
            else:
                st.caption("Calculate to see the weighted contributions. Invalid totals are explained, never silently changed.")
        elif module == "independence":
            blue = st.slider("Blue marbles in a bag of 10", 1, 9, 3, key="ind_blue")
            replacement = st.toggle("Replace and remix after the first draw", value=True, key="ind_replace")
            result = second_blue(blue, 10, replacement)
            st.write(f"**Before:** {blue}/10 = {blue/10:.3f}. **After learning the first draw was blue:** {result:.3f}.")
            st.bar_chart({"Before information": [blue/10], "Given first blue": [result]}, y_label="Probability of second blue")
            st.info("Independent: replacing and remixing restores the same probabilities." if replacement else "Dependent: the first blue draw changes both the blue count and total count.")
            if st.button("Record this comparison", key="record_ind"):
                repo.event(session, "interactive_calculation", module, {"replacement": replacement, "blue": blue})
                st.success("Comparison recorded.")
        elif module == "conditional_probability":
            st.write("A fictional group has 30 students: 12 in art, 18 in music, 6 in both. Restrict the population to see which denominator matters.")
            group = st.radio("Count within", ["All students", "Music members", "Art members"], key="conditional_group")
            total = {"All students": 30, "Music members": 18, "Art members": 12}[group]
            value = from_counts(6, total, 30)
            st.metric("Both-club members within selected group", f"6/{total} = {value:.2%}")
            # A count table remains readable to screen readers and does not rely on color.
            st.table([{"Within selected group": "Both clubs", "Count": 6},
                      {"Within selected group": "Other selected members", "Count": total - 6},
                      {"Within selected group": "Outside selected group (excluded)", "Count": 30 - total}])
            st.caption("Music → P(art | music); Art → P(music | art); All → P(art and music). The overlap stays 6 while the denominator changes.")
            if st.button("Record this sample space", key="record_cond"):
                repo.event(session, "interactive_calculation", module, {"group": group})
                st.success("Sample space recorded.")
        else:
            prevalence = st.slider("Misprint prevalence (%)", 0, 100, 2, key="base_prevalence") / 100
            sensitivity = st.slider("Flag rate among misprints (%)", 0, 100, 90, key="base_sensitivity") / 100
            false_positive = st.slider("Flag rate among correct labels (%)", 0, 100, 10, key="base_false") / 100
            f = frequencies(1000, prevalence, sensitivity, false_positive)
            st.table([{"Group": "Misprinted", "Population": f["target"], "Expected flags": f["true_clues"]},
                      {"Group": "Correct", "Population": f["other"], "Expected flags": f["false_clues"]}])
            if f["posterior"] is None:
                st.warning("No labels are flagged under these inputs. Probability given a flag is undefined because its denominator is zero.")
            else:
                st.metric("Misprints among flags", f"{f['posterior']:.2%}")
                st.write(f"{f['true_clues']:.2f} true flags ÷ {f['total_clues']:.2f} total flags.")
            st.caption("Expected frequencies for 1,000 fictional labels; some settings produce fractional counts. These are theoretical expectations, not observed records. Display rounds to two decimals; calculations retain precision.")
            if st.button("Record this population", key="record_base"):
                repo.event(session, "interactive_calculation", module, {"prevalence": prevalence, "sensitivity": sensitivity, "false_positive": false_positive})
                st.success("Population calculation recorded.")
    except ValueError as exc:
        st.warning(str(exc))
