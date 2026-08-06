"""
AI CSV Analytics Pro - Streamlit Master Web Application
"""
import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. Page Configuration - MUST BE FIRST STREAMLIT CALL
st.set_page_config(
    page_title="AI CSV Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Load Custom CSS Styling
def load_css(file_path="styles.css"):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# 3. Import Custom Core Modules
from modules.data_loader import load_file
from modules.data_cleaner import clean_dataset, get_column_types
from modules.analytics import calculate_metadata, compute_summary_stats, generate_ai_insights
from modules.visualizer import render_chart
from modules.ml_engine import run_linear_regression
from modules.report_generator import generate_pdf_report, generate_excel_report

# 4. Initialize Session States
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'df' not in st.session_state:
    st.session_state.df = None

# 5. Hero Landing Banner
st.markdown("""
    <div style="background-color: #0f172a; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
        <h1 style="color: #38bdf8; margin: 0;">📊 AI CSV Analytics Pro</h1>
        <p style="color: #94a3b8; margin-top: 0.5rem; font-size: 1.1rem;">
            Enterprise-grade automated data cleaning, exploratory visual analytics, 
            and predictive intelligence for any tabular dataset.
        </p>
    </div>
""", unsafe_allow_html=True)

# 6. Sidebar Control Panel
with st.sidebar:
    st.header("⚙️ Data Control Center")
    uploaded_file = st.file_uploader(
        "Upload File (CSV, XLSX, XLS)",
        type=["csv", "xlsx", "xls"],
        help="Automated encoding and format parser supported."
    )
    
    st.markdown("---")
    st.header("🧹 Cleaning Options")
    drop_dups = st.checkbox("Remove Duplicate Rows", value=True)
    fill_method = st.selectbox(
        "Handle Missing Values", 
        ["None", "Mean/Mode", "Drop Rows"]
    )

# 7. Main Application Logic
if uploaded_file is not None:
    # Load raw file
    if st.session_state.raw_df is None or st.session_state.get('last_uploaded') != uploaded_file.name:
        loaded_df, load_error = load_file(uploaded_file)
        if load_error:
            st.error(load_error)
            st.stop()
        st.session_state.raw_df = loaded_df
        st.session_state.last_uploaded = uploaded_file.name

    # Apply data cleaning
    st.session_state.df, cleaning_stats = clean_dataset(
        st.session_state.raw_df, 
        drop_duplicates=drop_dups, 
        fill_na=fill_method
    )
    
    df = st.session_state.df
    meta = calculate_metadata(df)

    # Overview Section
    st.subheader("📋 Executive Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", f"{meta['rows']:,}")
    col2.metric("Total Columns", meta["columns"])
    col3.metric("Missing Cells", f"{meta['null_pct']}%")
    col4.metric("Duplicates Removed", meta["duplicate_rows"])

    st.markdown("---")

    # Data Explorer
    st.subheader("🔍 Smart Data Explorer")
    selected_cols = st.multiselect(
        "Select columns to display:", 
        options=df.columns.tolist(), 
        default=df.columns.tolist()[:min(6, len(df.columns))]
    )
    
    if selected_cols:
        st.dataframe(df[selected_cols].head(20), use_container_width=True)

    st.markdown("---")

    # AI Insights & Download Reports
    st.subheader("🤖 AI Insights & Download Reports")
    ai_data = generate_ai_insights(df, meta)

    col_ins, col_rec = st.columns(2)
    with col_ins:
        st.write("### 💡 Key Insights")
        for ins in ai_data.get("insights", []):
            st.write(f"- {ins}")
            
    with col_rec:
        st.write("### 🎯 Recommendations")
        for rec in ai_data.get("recommendations", []):
            st.write(f"- {rec}")

    st.markdown("---")

    btn1, btn2 = st.columns(2)
    with btn1:
        pdf_bytes = generate_pdf_report(meta, ai_data)
        st.download_button(
            "📄 Download PDF Report", 
            pdf_bytes, 
            "Analytics_Report.pdf", 
            "application/pdf", 
            use_container_width=True
        )
    with btn2:
        summary_stats = compute_summary_stats(df)
        excel_bytes = generate_excel_report(df, summary_stats)
        st.download_button(
            "📊 Download Excel Workbook", 
            excel_bytes, 
            "Cleaned_Dataset.xlsx", 
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            use_container_width=True
        )

else:
    st.info("👆 Upload a CSV or Excel file from the left sidebar to begin.")
