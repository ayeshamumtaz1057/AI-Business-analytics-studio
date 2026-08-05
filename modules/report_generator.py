"""
Automated PDF and Excel report generation module.
"""
import io
import pandas as pd
from fpdf import FPDF
from typing import Dict, Any


class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(30, 41, 59)
        
        # Calculate explicit printable width
        eff_w = self.w - self.l_margin - self.r_margin
        self.set_x(self.l_margin)
        self.cell(eff_w, 10, 'AI CSV Analytics Pro - Summary Report', border=False, new_x="LMARGIN", new_y="NEXT", align='C')
        
        self.set_draw_color(56, 189, 248)
        self.set_line_width(0.8)
        self.line(10, 22, 200, 22)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(148, 163, 184)
        
        eff_w = self.w - self.l_margin - self.r_margin
        self.set_x(self.l_margin)
        self.cell(eff_w, 10, f'Page {self.page_no()}', align='C')


def generate_pdf_report(metadata: Dict[str, Any], insights: Dict[str, Any]) -> bytes:
    """
    Generates a structured PDF document containing KPIs and business narratives safely.
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Sanitize text to remove Markdown & handle non-Latin-1 chars/emojis safely
    def sanitize_text(text: str) -> str:
        clean = text.replace("**", "")
        return clean.encode("latin-1", "replace").decode("latin-1")

    # Explicit available width (Page width minus both margins)
    eff_width = pdf.w - pdf.l_margin - pdf.r_margin

    # 1. Overview Section
    pdf.set_x(pdf.l_margin)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(eff_width, 8, '1. Executive Dataset Summary', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    
    summary_text = (
        f"Total Records: {metadata['rows']:,}  |  Total Columns: {metadata['columns']}  |  "
        f"Memory Usage: {metadata['memory_mb']} MB\n"
        f"Missing Cells: {metadata['total_nulls']} ({metadata['null_pct']}%)  |  "
        f"Duplicate Rows: {metadata['duplicate_rows']} ({metadata['duplicate_pct']}%)\n"
        f"Data Health Score: {insights['quality_score']} / 100"
    )
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(eff_width, 6, sanitize_text(summary_text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # 2. Narrative Section
    pdf.set_x(pdf.l_margin)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(eff_width, 8, '2. Automated Business Insights', new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    for insight in insights.get('insights', []):
        clean_insight = sanitize_text(insight)
        # Reset cursor to left margin before each item
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(eff_width, 6, f"- {clean_insight}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # 3. Recommendations Section
    pdf.set_x(pdf.l_margin)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(eff_width, 8, '3. Strategic Recommendations', new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    for rec in insights.get('recommendations', []):
        clean_rec = sanitize_text(rec)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(eff_width, 6, f"- {clean_rec}", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def generate_excel_report(df: pd.DataFrame, summary_stats: pd.DataFrame) -> bytes:
    """
    Generates a multi-tab Excel workbook containing clean data and summary statistics.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Cleaned Data', index=False)
        if not summary_stats.empty:
            summary_stats.to_excel(writer, sheet_name='Summary Statistics')
            
    return output.getvalue()
