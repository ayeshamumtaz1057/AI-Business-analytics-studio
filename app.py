from fpdf import FPDF


def generate_pdf_report(meta, ai_data):
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 16)

  # Title
  pdf.cell(0, 10, "Dataset Analytics Report", ln=True, align="C")
  pdf.ln(5)

  # Metadata Section
  pdf.set_font("Arial", "B", 12)
  pdf.cell(0, 10, "Executive Overview:", ln=True)
  pdf.set_font("Arial", "", 10)
  pdf.cell(0, 8, f"Total Records: {meta.get('rows', 0):,}", ln=True)
  pdf.cell(0, 8, f"Total Columns: {meta.get('columns', 0)}", ln=True)
  pdf.cell(0, 8, f"Missing Cells: {meta.get('null_pct', 0)}%", ln=True)
  pdf.cell(
      0, 8, f"Duplicates Removed: {meta.get('duplicate_rows', 0)}", ln=True
  )
  pdf.ln(5)

  # Key Insights
  pdf.set_font("Arial", "B", 12)
  pdf.cell(0, 10, "Key Insights:", ln=True)
  pdf.set_font("Arial", "", 10)

  for ins in ai_data.get("insights", []):
    clean_text = str(ins).encode("latin-1", "replace").decode("latin-1")
    # Reset x cursor and force effective page width (epw)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(w=pdf.epw, h=6, txt=f"- {clean_text}")
    pdf.ln(2)

  pdf.ln(3)

  # Recommendations
  pdf.set_font("Arial", "B", 12)
  pdf.cell(0, 10, "Recommendations:", ln=True)
  pdf.set_font("Arial", "", 10)

  for rec in ai_data.get("recommendations", []):
    clean_text = str(rec).encode("latin-1", "replace").decode("latin-1")
    # Reset x cursor and force effective page width (epw)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(w=pdf.epw, h=6, txt=f"- {clean_text}")
    pdf.ln(2)

  return bytes(pdf.output())
