import io
import zipfile

import streamlit as st

from core import reports, state
from core.theme import page_header

page_header("Export Data", "Download any loaded dataset in the format you need.", "⬇️")
if not state.require_data():
    st.stop()

names = state.names()
chosen = st.multiselect("Datasets to export", names, default=[state.active_name()])
fmt = st.radio("Format", ["CSV", "Excel (one workbook)", "JSON", "ZIP (all as CSV)"],
               horizontal=True)

if chosen:
    frames = {n: st.session_state["datasets"][n] for n in chosen}
    total = sum(len(d) for d in frames.values())
    st.caption(f"{len(frames)} dataset(s) · {total:,} rows total")

    if fmt == "CSV":
        for n, d in frames.items():
            st.download_button(f"⬇ {n}.csv", d.to_csv(index=False),
                               f"{n}.csv", "text/csv", key=f"csv_{n}")
    elif fmt.startswith("Excel"):
        st.download_button("⬇ datasets.xlsx", reports.build_excel(frames), "datasets.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif fmt == "JSON":
        for n, d in frames.items():
            st.download_button(f"⬇ {n}.json", d.to_json(orient="records", date_format="iso"),
                               f"{n}.json", "application/json", key=f"js_{n}")
    else:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for n, d in frames.items():
                z.writestr(f"{n}.csv", d.to_csv(index=False))
        st.download_button("⬇ datasets.zip", buf.getvalue(), "datasets.zip", "application/zip")

st.divider()
st.subheader("Preview")
prev = st.selectbox("Dataset", names, index=names.index(state.active_name()))
st.dataframe(st.session_state["datasets"][prev].head(50), use_container_width=True)
