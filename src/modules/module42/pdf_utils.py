from fpdf import FPDF

def sanitize_text(text):
    """Replace unicode characters not supported by standard Helvetica font."""
    replacements = {
        '\u2014': '-', '\u2013': '-',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2026': '...',
        '\u2022': '-',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Force encode to latin-1, replacing any remaining unsupported chars with '?'
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf(patient_id, title, content):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(left=20, top=20, right=20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Header bar ──────────────────────────────────────────────────────────
    pdf.set_fill_color(26, 26, 110)   # deep navy blue
    pdf.rect(0, 0, 210, 30, 'F')

    pdf.set_font("Helvetica", style="B", size=14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(20, 8)
    safe_title = sanitize_text(f"ClinicalView System - {title}")
    # Use multi_cell so long titles wrap rather than overflow
    pdf.multi_cell(170, 7, text=safe_title, align='C')

    # ── Patient reference sub-header ────────────────────────────────────────
    pdf.set_xy(20, pdf.get_y() + 2)
    pdf.set_font("Helvetica", style="I", size=10)
    pdf.set_text_color(200, 200, 255)
    pdf.multi_cell(170, 6, text=f"Patient Reference: {patient_id}", align='C')

    pdf.ln(8)
    pdf.set_text_color(0, 0, 0)

    # ── Divider ─────────────────────────────────────────────────────────────
    pdf.set_draw_color(26, 26, 110)
    pdf.set_line_width(0.6)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(5)

    # ── Body content ────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(30, 30, 30)

    # Ensure content is a string
    if isinstance(content, list):
        content = "\n".join(str(item) for item in content)
    elif not isinstance(content, str):
        content = str(content)

    # Strip basic markdown symbols
    clean_content = (content
        .replace('**', '')
        .replace('### ', '')
        .replace('## ', '')
        .replace('# ', '')
        .replace('* ', '- '))

    safe_content = sanitize_text(clean_content)

    # multi_cell wraps lines automatically within the 170mm usable width
    pdf.multi_cell(170, 7, text=safe_content)

    # ── Footer ──────────────────────────────────────────────────────────────
    pdf.set_y(-18)
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 5, text="ClinicalView - Confidential Clinical Document", align='C')

    return bytes(pdf.output())
