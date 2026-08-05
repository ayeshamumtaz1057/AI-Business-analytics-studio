"""
AI CSV Analytics Pro - Streamlit Master Web Application
"""
import streamlit as st
import pandas as pd
import numpy as np
import os

# Page Configuration - MUST BE FIRST STREAMLIT CALL
st.set_page_config(
    page_title="AI CSV Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS Styling
def load_css(file_path="styles.css"):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Import Custom Core Modules
from modules.data_loader import load_file
from modules.data_cleaner import clean_dataset, get_column_types
from modules.analytics import calculate_metadata, compute_summary_stats, generate_ai_insights
from modules.visualizer import render_chart
from modules.ml_engine import run_linear_regression
from modules.report_generator import generate_pdf_report, generate_excel_report


# Initialize Session States
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'df' not in st.session_state:
    st.session_state.df = None


# --- HERO LANDING BANNER ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">📊 AI CSV Analytics Pro</div>
    <div class="hero-subtitle">
        Enterprise-grade automated data cleaning, exploratory visual analytics, 
        and predictive intelligence for any tabular dataset.
    </div>
</div>
""", unsafe_allow_html=True)


# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("⚙️ Data Control Center")
    uploaded_file = st.file_uploader(
        "Upload File (CSV, XLSX, XLS)", 
        type=["csv", "xlsx", "xls"],
        help="Automated encoding and format parser supported."
    )

    if uploaded_file is not None:
        if st.session_state.raw_df is None or st.sidebar.button("Reload Original File"):
            with st.spinner("Ingesting and parsing data structure..."):
                raw_data, error = load_file(uploaded_file)
                if error:
                    st.error(error)
                else:
                    st.session_state.raw_df = raw_data
                    st.session_state.df = raw_data.copy()
                    st.success("File uploaded successfully!")

    st.markdown("---")
    st.info("💡 **Pro Tip**: Upload any dataset. The engine will automatically detect column structures.")


# MAIN APP PIPELINE
if st.session_state.df is not None:
    df = st.session_state.df
    col_types = get_column_types(df)
    meta = calculate_metadata(df)

    # TABBED NAVIGATION DASHBOARD
    tab_overview, tab_clean, tab_visuals, tab_filter, tab_ai, tab_stats, tab_ml, tab_export = st.tabs([
        "📋 Data Info",
        "🧹 Data Cleaning",
        "📈 Visualizations",
        "🔍 Filter Engine",
        "🤖 AI Insights",
        "📐 Statistics",
        "🧠 ML Prediction",
        "📥 Export Reports"
    ])

    # =========================================================================
    # TAB 1: DATASET INFORMATION & PREVIEW
    # =========================================================================
    with tab_overview:
        st.subheader("Dataset Overview & Structure")

        # Metric KPI Display
        kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
        kpi1.metric("Total Rows", f"{meta['rows']:,}")
        kpi2.metric("Total Columns", meta['columns'])
        kpi3.metric("Missing Cells", f"{meta['total_nulls']:,}")
        kpi4.metric("Null Rate", f"{meta['null_pct']}%")
        kpi5.metric("Duplicates", f"{meta['duplicate_rows']:,}")
        kpi6.metric("Memory", f"{meta['memory_mb']} MB")

        st.markdown("---")

        # Column Schema Table
        st.write("### Feature Attribute Schema")
        schema_df = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": [str(dtype) for dtype in df.dtypes],
            "Non-Null Count": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Unique Values": [df[col].nunique() for col in df.columns]
        })
        st.dataframe(schema_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.write("### Interactive Data Explorer")
        
        # Pagination & Search Controls
        search_term = st.text_input("🔍 Search dataset records:", "")
        filtered_preview_df = df
        if search_term:
            filtered_preview_df = df[df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
        
        st.dataframe(filtered_preview_df, use_container_width=True)

    # =========================================================================
    # TAB 2: DATA CLEANING MODULE
    # =========================================================================
    with tab_clean:
        st.subheader("Automated Data Hygiene & Remediation")
        st.write("Clean missing values, drop duplicate records, and standardize field dtypes seamlessly.")

        col_c1, col_c2 = st.columns([1, 2])
        
        with col_c1:
            st.markdown("#### Operational Actions")
            if st.button("🧹 Clean Dataset Now", type="primary"):
                with st.spinner("Applying data sanitization rules..."):
                    cleaned_df, stats = clean_dataset(st.session_state.raw_df)
                    st.session_state.df = cleaned_df
                    st.success("Dataset successfully sanitized!")
                    
                    st.write("**Remediation Summary:**")
                    st.write(f"- Duplicates Removed: `{stats['duplicates_removed']}`")
                    st.write(f"- Empty Columns Dropped: `{stats['columns_removed']}`")
                    st.write(f"- Missing Values Imputed: `{stats['missing_imputed']}`")
                    st.write(f"- Date Formats Converted: `{stats['dates_converted']}`")
                    st.rerun()

            if st.button("🔄 Reset to Original Data"):
                st.session_state.df = st.session_state.raw_df.copy()
                st.info("Reset to initial raw data upload state.")
                st.rerun()

        with col_c2:
            st.markdown("#### Data Health Profile")
            st.write(f"- **Numeric Columns ({len(col_types['numeric'])}):** {', '.join(col_types['numeric']) if col_types['numeric'] else 'None'}")
            st.write(f"- **Categorical Columns ({len(col_types['categorical'])}):** {', '.join(col_types['categorical']) if col_types['categorical'] else 'None'}")
            st.write(f"- **Date Columns ({len(col_types['date'])}):** {', '.join(col_types['date']) if col_types['date'] else 'None'}")

    # =========================================================================
    # TAB 3: DATA VISUALIZATION ENGINE
    # =========================================================================
    with tab_visuals:
        st.subheader("Interactive Visual Analytics Studio")

        chart_list = [
            "Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart",
            "Histogram", "Box Plot", "Correlation Matrix",
            "Treemap", "Sunburst Chart", "Area Chart"
        ]
        
        c_type = st.selectbox("Select Visual Chart Type", chart_list)

        v_col1, v_col2, v_col3 = st.columns(3)

        all_cols = df.columns.tolist()
        num_cols = col_types["numeric"]

        with v_col1:
            x_axis = st.selectbox("X-Axis Feature", all_cols, index=0)
        
        with v_col2:
            # Default Y-axis to second column if available
            y_default_idx = 1 if len(all_cols) > 1 else 0
            y_axis = st.selectbox("Y-Axis Feature (Aggregation / Metric)", [None] + all_cols, index=y_default_idx)
            
        with v_col3:
            group_col = st.selectbox("Color / Group Category (Optional)", [None] + col_types["categorical"])

        try:
            fig = render_chart(c_type, df, x_col=x_axis, y_col=y_axis, color_col=group_col)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render {c_type} with selected columns. Detail: {str(e)}")

    # =========================================================================
    # TAB 4: ADVANCED FILTERING ENGINE
    # =========================================================================
    with tab_filter:
        st.subheader("Dynamic Slice & Dice Filter Studio")

        f_col1, f_col2 = st.columns(2)
        filtered_df = df.copy()

        with f_col1:
            if col_types["categorical"]:
                cat_filter_col = st.selectbox("Filter by Category Column", [None] + col_types["categorical"])
                if cat_filter_col:
                    selected_cats = st.multiselect(
                        f"Select Values for {cat_filter_col}",
                        options=df[cat_filter_col].unique().tolist(),
                        default=df[cat_filter_col].unique().tolist()[:5]
                    )
                    if selected_cats:
                        filtered_df = filtered_df[filtered_df[cat_filter_col].isin(selected_cats)]

        with f_col2:
            if col_types["numeric"]:
                num_filter_col = st.selectbox("Filter by Numeric Range Column", [None] + col_types["numeric"])
                if num_filter_col:
                    min_v = float(df[num_filter_col].min())
                    max_v = float(df[num_filter_col].max())
                    if min_v < max_v:
                        selected_range = st.slider(
                            f"Range for {num_filter_col}",
                            min_value=min_v, max_value=max_v, value=(min_v, max_v)
                        )
                        filtered_df = filtered_df[
                            (filtered_df[num_filter_col] >= selected_range[0]) & 
                            (filtered_df[num_filter_col] <= selected_range[1])
                        ]

        st.write(f"Showing **{len(filtered_df):,}** of **{len(df):,}** records.")
        st.dataframe(filtered_df, use_container_width=True)

    # =========================================================================
    # TAB 5: AUTOMATED AI INSIGHTS ENGINE
    # =========================================================================
    with tab_ai:
        st.subheader("AI Synthetic Business Intelligence")
        
        ai_data = generate_ai_insights(df, meta)

        ai_c1, ai_c2 = st.columns([1, 2])
        
        with ai_c1:
            st.markdown("#### Data Health Score")
            st.metric("Overall Score", f"{ai_data['quality_score']} / 100")
            st.progress(ai_data['quality_score'] / 100)
            
            st.markdown("#### Executive Summary")
            st.write(ai_data['summary'])

        with ai_c2:
            st.markdown("#### Key Automated Findings")
            for ins in ai_data['insights']:
                st.markdown(f"<div class='insight-box'><p>💡 {ins}</p></div>", unsafe_allow_html=True)

            st.markdown("#### Strategic Recommendations")
            for rec in ai_data['recommendations']:
                st.markdown(f"<div class='recommendation-box'><p>🎯 {rec}</p></div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 6: STATISTICAL ANALYSIS
    # =========================================================================
    with tab_stats:
        st.subheader("Descriptive Mathematical & Distribution Analysis")

        summary_df = compute_summary_stats(df)
        if not summary_df.empty:
            st.write("### Numerical Column Descriptive Statistics")
            st.dataframe(summary_df, use_container_width=True)

            st.markdown("---")
            st.write("### Correlation Matrix Table")
            num_only = df.select_dtypes(include=[np.number])
            if not num_only.empty:
                st.dataframe(num_only.corr().round(3), use_container_width=True)
        else:
            st.warning("No numeric columns available in dataset for statistical modeling.")

    # =========================================================================
    # TAB 7: MACHINE LEARNING ENGINE
    # =========================================================================
    with tab_ml:
        st.subheader("Automated Predictive Linear Regression")

        if len(col_types["numeric"]) < 2:
            st.warning("Predictive modeling requires at least TWO numeric features (1 Target, 1+ Predictors).")
        else:
            ml_c1, ml_c2 = st.columns([1, 2])

            with ml_c1:
                target_feature = st.selectbox("Select Target Variable (Y)", col_types["numeric"], index=len(col_types["numeric"])-1)
                available_predictors = [c for c in col_types["numeric"] if c != target_feature]
                selected_predictors = st.multiselect("Select Feature Predictors (X)", available_predictors, default=available_predictors)

                train_btn = st.button("🚀 Train Model", type="primary")

            with ml_c2:
                if train_btn and selected_predictors:
                    with st.spinner("Fitting Linear Regression model..."):
                        metrics, err = run_linear_regression(df, target_feature, selected_predictors)
                        
                        if err:
                            st.error(err)
                        else:
                            st.success("Model trained successfully!")
                            
                            # Display ML KPIs
                            m1, m2, m3 = st.columns(3)
                            m1.metric("R² Score", metrics["r2"])
                            m2.metric("RMSE", metrics["rmse"])
                            m3.metric("MAE", metrics["mae"])

                            st.markdown("---")
                            st.write("### Actual vs. Predicted Output (Test Set Sample)")
                            st.dataframe(metrics["results_df"].head(10), use_container_width=True)

                            # Plot Actual vs Predicted Scatter
                            fig_ml = render_chart("Scatter Plot", metrics["results_df"], x_col="Actual", y_col="Predicted")
                            st.plotly_chart(fig_ml, use_container_width=True)

    # =========================================================================
    # TAB 8: REPORT EXPORT ENGINE
    # =========================================================================
    with tab_export:
        st.subheader("Export Reports & Data Artifacts")
        st.write("Download sanitized data, formatted Excel workbooks, or automated PDF summaries.")

        exp_c1, exp_c2, exp_c3 = st.columns(3)

        # 1. Cleaned CSV Export
        with exp_c1:
            st.markdown("#### Cleaned Data (CSV)")
            csv_bytes = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Clean CSV",
                data=csv_bytes,
                file_name="Cleaned_Dataset.csv",
                mime="text/csv"
            )

        # 2. Excel Multi-Tab Report Export
        with exp_c2:
            st.markdown("#### Excel Workbook Report")
            summary_stats_df = compute_summary_stats(df)
            excel_data = generate_excel_report(df, summary_stats_df)
            st.download_button(
                label="📥 Download Excel Report",
                data=excel_data,
                file_name="Analytics_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # 3. PDF Summary Report Export
        with exp_c3:
            st.markdown("#### Executive PDF Summary")
            ai_data = generate_ai_insights(df, meta)
            pdf_data = generate_pdf_report(meta, ai_data)
            st.download_button(
                label="📥 Download PDF Summary",
                data=pdf_data,
                file_name="AI_Analytics_Executive_Report.pdf",
                mime="application/pdf"
            )

else:
    # LANDING STATE WHEN NO FILE IS UPLOADED
    st.info("👆 Please upload a CSV or Excel file using the sidebar to begin analysis.")
    
    st.markdown("---")
    st.markdown("### 🌟 Key App Capabilities")
    f1, f2, f3 = st.columns(3)
    f1.markdown("**🧹 Smart Cleaning**\nAutomated deduplication, median/mode missing value imputation, and date casting.")
    f2.markdown("**📈 Visual Analytics**\nDynamic Plotly charts (Scatter, Treemap, Heatmaps, Sunburst) with zero code.")
    f3.markdown("**🤖 Predictive ML**\nAutomated Linear Regression with R², RMSE, and MAE evaluation metrics.")
