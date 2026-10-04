from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/technical-report-draft.md"
OUTPUT = ROOT / "outputs/report/gridpulse-technical-report-v0.1.pdf"
FONT = Path(r"C:\Windows\Fonts\simhei.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\Dengb.ttf")


def register_fonts() -> None:
    if not FONT.is_file() or not FONT_BOLD.is_file():
        raise FileNotFoundError("Noto Sans SC fonts are required for Chinese PDF export.")
    pdfmetrics.registerFont(TTFont("NotoSC", str(FONT)))
    pdfmetrics.registerFont(TTFont("NotoSC-Bold", str(FONT_BOLD)))


def inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r"<font name='NotoSC-Bold'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="NotoSC-Bold", fontSize=20, leading=27, alignment=TA_CENTER, textColor=colors.HexColor("#17302A"), spaceAfter=14),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="NotoSC-Bold", fontSize=15, leading=21, textColor=colors.HexColor("#0F766E"), spaceBefore=12, spaceAfter=7),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="NotoSC-Bold", fontSize=12, leading=17, textColor=colors.HexColor("#17302A"), spaceBefore=9, spaceAfter=5),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="NotoSC", fontSize=9.2, leading=14, textColor=colors.HexColor("#24332F"), spaceAfter=5),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="NotoSC", fontSize=9.0, leading=13, leftIndent=13, firstLineIndent=-8, spaceAfter=2),
        "code": ParagraphStyle("code", parent=base["Code"], fontName="NotoSC", fontSize=8.5, leading=12, backColor=colors.HexColor("#F0F5F2"), borderPadding=6, spaceBefore=4, spaceAfter=7),
        "caption": ParagraphStyle("caption", parent=base["BodyText"], fontName="NotoSC", fontSize=8, leading=11, textColor=colors.HexColor("#50625E"), spaceAfter=6),
    }


def parse_table(lines: list[str], styles):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        rows.append([Paragraph(inline(cell), styles["body"]) for cell in cells])
    if not rows:
        return Spacer(1, 1)
    widths = [((A4[0] - 35 * mm) / len(rows[0]))] * len(rows[0])
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "NotoSC-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D6D0")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FAFAF7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return KeepTogether([Spacer(1, 4), table, Spacer(1, 7)])


def build_story(styles):
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story = []
    i = 0
    in_code = False
    code_lines: list[str] = []
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if in_code:
                story.append(Paragraph(inline("\n".join(code_lines)).replace("\n", "<br/>"), styles["code"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            story.append(parse_table(table_lines, styles))
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["title"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["h1"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), styles["h2"]))
        elif line.startswith("- "):
            story.append(Paragraph("- " + inline(line[2:]), styles["bullet"]))
        elif re.match(r"^\d+\. ", line):
            story.append(Paragraph(inline(line), styles["bullet"]))
        else:
            story.append(Paragraph(inline(line), styles["body"]))
        i += 1
    return story


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("NotoSC", 8)
    canvas.setFillColor(colors.HexColor("#50625E"))
    canvas.drawString(18 * mm, 12 * mm, "GridPulse | 技术报告初稿 | 公开数据回测原型")
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, f"第 {doc.page} 页")
    canvas.restoreState()


def main() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=19 * mm, title="GridPulse 技术报告初稿",
        author="GridPulse",
    )
    doc.build(build_story(make_styles()), onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
