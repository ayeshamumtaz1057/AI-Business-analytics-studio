import streamlit as st
import pandas as pd
import plotly.express as px
import io

uploaded_file = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.dataframe(df, use_container_width=True)

    st.subheader("Summary Statistics")
    st.write(df.describe())

    corr = df.corr(numeric_only=True)

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="Viridis"
    )

    st.plotly_chart(fig)

    csv_buffer = io.StringIO()

    df.to_csv(csv_buffer, index=False)

    st.download_button(
        "⬇️ Download Clean CSV",
        csv_buffer.getvalue(),
        "cleaned_data.csv",
        "text/csv"
    )

    st.subheader("AI Insights")

    st.success(f"""
    ✅ Total Records : {len(df)}

    ✅ Columns : {len(df.columns)}

    ✅ Missing Values : {df.isnull().sum().sum()}

    ✅ Duplicate Rows : {df.duplicated().sum()}
    """)

else:
    st.info("👆 Upload a .csv, .xlsx, or .xls file to get started.")
