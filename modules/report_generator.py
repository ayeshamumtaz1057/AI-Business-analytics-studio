"""
Report generation module: exports cleaned data and insights as PDF and Excel files.
"""
import io
import pandas as pd
from fpdf import FPDF


def generate_pdf_report(meta, ai_data):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Dataset Analytics Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    # Metadata
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Dataset Summary", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", "", 10)
    for key, value in meta.items():
        text = f"{key}: {value}".encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # Insights
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "AI Insights", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", "", 10)
    for ins in ai_data.get("insights", []):
        text = str(ins).encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, "- " + text, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def generate_excel_report(df, summary_stats):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Cleaned Data", index=False)
        if isinstance(summary_stats, pd.DataFrame):
            summary_stats.to_excel(writer, sheet_name="Summary Stats", index=False)

    output.seek(0)
    return output.getvalue()
