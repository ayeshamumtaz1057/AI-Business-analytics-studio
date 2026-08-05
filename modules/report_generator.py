import io
import pandas as pd
from fpdf import FPDF


def generate_pdf_report(meta, ai_data):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Dataset Analytics Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Key Insights", ln=True)

    pdf.set_font("Arial", "", 10)

    for insight in ai_data.get("insights", []):
        text = str(insight).encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, f"- {text}")

    return pdf.output(dest="S")


def generate_excel_report(meta, ai_data):
    output = io.BytesIO()

    meta_df = pd.DataFrame(
        list(meta.items()),
        columns=["Property", "Value"]
    )

    insights_df = pd.DataFrame({
        "Insights": ai_data.get("insights", [])
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        meta_df.to_excel(writer, sheet_name="Metadata", index=False)
        insights_df.to_excel(writer, sheet_name="AI Insights", index=False)

    output.seek(0)
    return output.getvalue()
