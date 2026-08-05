import io
import pandas as pd
from fpdf import FPDF


def generate_pdf_report(meta, ai_data):
    """Generates a PDF report from dataset metadata and AI insights."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Dataset Analytics Report", ln=True, align="C")
    pdf.ln(5)

    # Insights Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Key Insights:", ln=True)
    pdf.set_font("Arial", "", 10)

    for ins in ai_data.get("insights", []):
        # Sanitize special characters/emojis for Latin-1 standard fonts
        clean_ins = str(ins).encode("latin-1", "replace").decode("latin-1")
        # Reset horizontal cursor to left margin
        pdf.set_x(pdf.l_margin)
        # Use effective page width explicitly
        pdf.multi_cell(w=pdf.epw, h=6, txt=f"- {clean_ins}")
        pdf.ln(1)

    return bytes(pdf.output())


def generate_excel_report(meta, ai_data):
    """Generates an in-memory Excel report with metadata and insights."""
    output = io.BytesIO()

    # Create DataFrames from the dictionary data
    insights_df = pd.DataFrame({"Insights": ai_data.get("insights", [])})
    meta_df = pd.DataFrame(list(meta.items()), columns=["Property", "Value"])

    # Write multiple sheets into an in-memory Excel workbook
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        meta_df.to_excel(writer, sheet_name="Metadata", index=False)
        insights_df.to_excel(writer, sheet_name="AI Insights", index=False)

    return output.getvalue()
