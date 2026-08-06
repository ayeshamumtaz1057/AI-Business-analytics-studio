import streamlit as st

from core import ai, auth, db, insights, state
from core.theme import page_header, insight_card

page_header("AI Business Insights", "Executive-ready analysis generated from your data.", "✨")
if not state.require_data():
    st.stop()

df, mapping = state.active_df(), state.mapping()
name = state.active_name()

c1, c2, c3 = st.columns([1, 1, 2])
if c1.button("🚀 Generate insights", type="primary", use_container_width=True):
    with st.spinner("Analysing your data…"):
        text, engine = insights.generate_report(df, mapping)
    st.session_state["ai_cache"][name] = {"text": text, "engine": engine}
    db.log(auth.current_user(), "ai_insights", f"{name} via {engine}")

if c2.button("🔄 Clear", use_container_width=True):
    st.session_state["ai_cache"].pop(name, None)
    st.rerun()

with c3:
    if ai.available():
        st.success("Gemini connected — insights are model-generated.", icon="🟢")
    else:
        st.info("Running the built-in offline analyst. Add a Gemini API key in Settings "
                "for narrative AI commentary.", icon="⚪")

st.write("")
for title, body, kind in insights.quick_cards(df, mapping):
    insight_card(title, body, kind)

cached = st.session_state["ai_cache"].get(name)
if cached:
    st.divider()
    st.caption(f"Engine: {cached['engine']}")
    st.markdown(cached["text"])
    st.download_button("⬇ Download as Markdown", cached["text"],
                       f"insights_{name}.md", "text/markdown")
    if st.button("📄 Send to Report Generator"):
        st.session_state["_report_insights"] = cached["text"]
        st.switch_page("views/reports.py")
else:
    st.info("Click **Generate insights** for a full report: executive summary, trends, "
            "best and worst products, opportunities, risks, customer insights and "
            "prioritised recommendations.")

with st.expander("What the AI sees (data brief)"):
    st.json(insights.build_brief(df, mapping), expanded=False)
