import streamlit as st

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
"""
app.py
Streamlit front-end for the CSV/Excel Data Cleaner & Report Automator.
Upload a messy CSV or Excel file, see it cleaned, and download the result.
"""

import io
import pandas as pd
import streamlit as st
import plotly.express as pxnumeric = df.select_dtypes(include="number").columns

x = st.selectbox("X Axis", df.columns)

y = st.selectbox("Y Axis", numeric)

fig = px.bar(

    df,

    x=x,

    y=y

)

st.plotly_chart(

    fig,

    use_container_width=True

)




from data_cleaner import (
    clean_column_names,
    clean_text_columns,
    handle_missing_values,
    remove_duplicates,
    generate_report,
)

st.set_page_config(page_title="AI CSV Analytics", page_icon="🧹", layout="wide")

st.title("AI CSV Analytics")
st.write(
    "st.markdown("""
# 📊 AI CSV Analytics Pro

### Upload • Clean • Analyze • Visualize • Export
""")."
)

uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # Load directly from the uploaded file object (no need to save to disk first)
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Couldn't read that file: {e}")
        st.stop()

    with st.expander("Preview of the raw data", expanded=False):
        st.dataframe(df.head(20))

    with st.spinner("Cleaning your data..."):
        df = clean_column_names(df)
        df = clean_text_columns(df)
        df = handle_missing_values(df)
        df, duplicates_removed = remove_duplicates(df)
        df, report = generate_report(df, duplicates_removed)

    st.success("Done! Here's what changed.")

    # --- Summary metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total rows", report["total_rows"])
    col2.metric("Duplicates removed", report["duplicates_removed"])
    if report["total_revenue"] is not None:
        col3.metric("Total revenue", f"{report['total_revenue']:,.0f}")

    # --- Quantity per product ---
    if report["quantity_per_product"] is not None:
        st.subheader("Total quantity sold per product")
        st.bar_chart(report["quantity_per_product"])

   # st.subheader("Dataset Preview")

st.dataframe(

    df,

    use_container_width=True,

    height=400

)

    # --- Download button ---
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download cleaned CSV",
        data=csv_buffer.getvalue(),
        file_name="cleaned_data.csv",
        mime="text/csv",
    )
    
   # st.subheader("Summary Statistics")

st.write(df.describe())
else:
    st.info("👆 Upload a .csv, .xlsx, or .xls file to get started.")
