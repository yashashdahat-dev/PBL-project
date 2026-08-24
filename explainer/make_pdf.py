"""
Converts theory_explainer.md to a styled PDF using ReportLab.
"""
import re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Preformatted
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

MD_PATH  = r"d:\ff\explainer\theory_explainer.md"
PDF_PATH = r"d:\ff\explainer\theory_explainer.pdf"

# ── Color palette ────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#0d1b2a")
BLUE   = colors.HexColor("#0077b6")
CYAN   = colors.HexColor("#00b4d8")
LCYAN  = colors.HexColor("#bee9f5")
BGCODE = colors.HexColor("#0d1b2a")
FGCODE = colors.HexColor("#64ffda")
BGQUO  = colors.HexColor("#e8f7fc")
TH_BG  = colors.HexColor("#0077b6")
ALT_BG = colors.HexColor("#f0f8ff")
BLACK  = colors.HexColor("#1a1a2e")
GREY   = colors.HexColor("#555555")

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

S = {
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20, textColor=NAVY,
                          spaceAfter=8, spaceBefore=20, borderPadding=(0,0,4,0),
                          leading=26),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, textColor=BLUE,
                          spaceAfter=4, spaceBefore=16, leading=18,
                          borderPadding=(2,2,2,8), leftIndent=0),
    "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY,
                          spaceAfter=3, spaceBefore=10, leading=15),
    "h4": ParagraphStyle("h4", fontName="Helvetica-Bold", fontSize=11, textColor=BLUE,
                          spaceAfter=2, spaceBefore=8, leading=13),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, textColor=BLACK,
                            spaceAfter=4, leading=15),
    "li":  ParagraphStyle("li", fontName="Helvetica", fontSize=10, textColor=BLACK,
                            leftIndent=16, spaceAfter=2, leading=14, bulletIndent=8),
    "bq":  ParagraphStyle("bq", fontName="Helvetica-Oblique", fontSize=10,
                            textColor=BLUE, backColor=BGQUO, leftIndent=12,
                            rightIndent=12, spaceAfter=6, spaceBefore=6,
                            leading=14, borderPadding=8),
    "code":ParagraphStyle("code", fontName="Courier", fontSize=9, textColor=FGCODE,
                            backColor=BGCODE, leading=12, leftIndent=8, rightIndent=8,
                            spaceAfter=8, spaceBefore=4, borderPadding=8),
}

def inline_format(text):
    """Convert inline markdown (**bold**, `code`) to ReportLab XML."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`',       r'<font name="Courier" color="#023e8a">\1</font>', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)   # strip links, keep text
    return text

def parse_md(md_text):
    """Parse markdown and return a list of ReportLab Flowables."""
    story = []
    lines = md_text.split("\n")
    i = 0
    in_code = False
    code_buf = []

    while i < len(lines):
        line = lines[i]

        # ── Fenced code block ──────────────────────────────────────────
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                code_buf = []
            else:
                in_code = False
                code_text = "\n".join(code_buf)
                story.append(Preformatted(code_text, S["code"],
                                          maxLineLength=90))
                story.append(Spacer(1, 4))
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # ── Table ──────────────────────────────────────────────────────
        if line.strip().startswith("|"):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_line = lines[i].strip().strip("|")
                cells = [c.strip() for c in row_line.split("|")]
                # skip separator rows
                if not all(re.match(r"^[-:]+$", c) for c in cells if c):
                    table_rows.append(cells)
                i += 1

            if not table_rows:
                continue

            col_count = max(len(r) for r in table_rows)
            # Normalise row lengths
            table_rows = [r + [""] * (col_count - len(r)) for r in table_rows]

            # Build styled table
            col_width = (A4[0] - 4*cm) / col_count
            tbl = Table(table_rows, colWidths=[col_width]*col_count, repeatRows=1)
            ts = TableStyle([
                ("BACKGROUND",  (0,0), (-1,0), TH_BG),
                ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
                ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",    (0,0), (-1,-1), 9),
                ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
                ("TEXTCOLOR",   (0,1), (-1,-1), BLACK),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, ALT_BG]),
                ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#c0d8e8")),
                ("TOPPADDING",  (0,0), (-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
                ("LEFTPADDING", (0,0), (-1,-1), 7),
                ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ])
            tbl.setStyle(ts)
            story.append(Spacer(1, 6))
            story.append(tbl)
            story.append(Spacer(1, 8))
            continue

        # ── Horizontal rule ────────────────────────────────────────────
        if line.strip() in ("---", "***", "___"):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=1.5,
                                    color=LCYAN, spaceAfter=4))
            i += 1
            continue

        # ── Headings ───────────────────────────────────────────────────
        if line.startswith("#### "):
            story.append(Paragraph(inline_format(line[5:]), S["h4"])); i += 1; continue
        if line.startswith("### "):
            story.append(Paragraph(inline_format(line[4:]), S["h3"])); i += 1; continue
        if line.startswith("## "):
            story.append(Spacer(1, 4))
            txt = inline_format(line[3:])
            story.append(Paragraph(txt, S["h2"]))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=CYAN, spaceAfter=4))
            i += 1; continue
        if line.startswith("# "):
            story.append(Spacer(1, 6))
            story.append(Paragraph(inline_format(line[2:]), S["h1"]))
            story.append(HRFlowable(width="100%", thickness=2,
                                    color=CYAN, spaceAfter=6))
            i += 1; continue

        # ── Blockquote ─────────────────────────────────────────────────
        if line.startswith("> "):
            story.append(Paragraph(inline_format(line[2:]), S["bq"]))
            i += 1; continue

        # ── Bullet list ────────────────────────────────────────────────
        if re.match(r"^[\*\-\•] ", line):
            story.append(Paragraph("• " + inline_format(line[2:]), S["li"]))
            i += 1; continue

        # ── Empty line ─────────────────────────────────────────────────
        if line.strip() == "":
            story.append(Spacer(1, 3))
            i += 1; continue

        # ── Paragraph ─────────────────────────────────────────────────
        story.append(Paragraph(inline_format(line), S["body"]))
        i += 1

    return story

# ── Build PDF ────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    PDF_PATH,
    pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="AI-Native LEO Satellite Network — Theory Explainer",
    author="LEO Digital Twin Simulation"
)

with open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()

# Remove image embeds (can't embed in PDF this way)
md_text = re.sub(r'!\[.*?\]\(.*?\)', '', md_text)

story = parse_md(md_text)

doc.build(story)
print(f"PDF saved to: {PDF_PATH}")
