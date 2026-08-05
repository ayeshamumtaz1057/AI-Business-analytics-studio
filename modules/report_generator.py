from fpdf import FPDF


def generate_pdf_report(meta, ai_data):
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
