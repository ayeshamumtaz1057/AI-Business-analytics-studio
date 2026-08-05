"""
app.py
Streamlit front-end for the CSV/Excel Data Cleaner & Report Automator.
Upload a messy CSV or Excel file, see it cleaned, and download the result.
"""

import io
import pandas as pd
import streamlit as st

from data_cleaner import (
    clean_column_names,
    clean_text_columns,
    handle_missing_values,
    remove_duplicates,
    generate_report,
)

st.set_page_config(page_title="Data Cleaner & Report Automator", page_icon="🧹", layout="wide")

st.title("🧹 Excel/CSV Data Cleaner & Report Automator")
st.write(
    "Upload a messy CSV or Excel file and this tool will strip whitespace, "
    "fix capitalization, fill missing values, drop duplicates, and give you "
    "a summary report — plus a cleaned file to download."
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

    # --- Cleaned data preview ---
    st.subheader("Cleaned data")
    st.dataframe(df)

    # --- Download button ---
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download cleaned CSV",
        data=csv_buffer.getvalue(),
        file_name="cleaned_data.csv",
        mime="text/csv",
    )
else:
    st.info("👆 Upload a .csv, .xlsx, or .xls file to get started.")
