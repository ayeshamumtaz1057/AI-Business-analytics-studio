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
        self.cell(0, 10, 'AI CSV Analytics Pro - Summary Report', border=False, ln=True, align='C')
        self.set_draw_color(56, 189, 248)
        self.set_line_width(0.8)
        self.line(10, 22, 200, 22)
        self.ln(8)

    def footer(self):
        self.bottom_margin = 15
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')


def generate_pdf_report(metadata: Dict[str, Any], insights: Dict[str, Any]) -> bytes:
    """
    Generates a structured PDF document containing KPIs and business narratives.
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Overview Section
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, '1. Executive Dataset Summary', ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    
    summary_text = (
        f"Total Records: {metadata['rows']:,}  |  Total Columns: {metadata['columns']}  |  "
        f"Memory Usage: {metadata['memory_mb']} MB\n"
        f"Missing Cells: {metadata['total_nulls']} ({metadata['null_pct']}%)  |  "
        f"Duplicate Rows: {metadata['duplicate_rows']} ({metadata['duplicate_pct']}%)\n"
        f"Data Health Score: {insights['quality_score']} / 100"
    )
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(5)

    # Narrative Section
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, '2. Automated Business Insights', ln=True)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    for insight in insights['insights']:
        # Replace markdown bold markers for PDF compatibility
        clean_insight = insight.replace("**", "")
        pdf.multi_cell(0, 6, f"- {clean_insight}")

    pdf.ln(5)

    # Recommendations
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, '3. Strategic Recommendations', ln=True)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    for rec in insights['recommendations']:
        clean_rec = rec.replace("**", "")
        pdf.multi_cell(0, 6, f"- {clean_rec}")

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
