#!/usr/bin/env python3
"""
Simple PDF generator for Helix-Zero documentation
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import os

# Create PDF
md_file = os.path.join(
    os.path.dirname(__file__), "HELIX_ZERO_V8_TECHNICAL_DOCUMENTATION.md"
)
pdf_file = os.path.join(
    os.path.dirname(__file__), "HELIX_ZERO_V8_TECHNICAL_DOCUMENTATION.pdf"
)

with open(md_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "Title",
    fontSize=24,
    textColor=colors.HexColor("#1a5f7a"),
    alignment=1,
    spaceAfter=20,
)
h1_style = ParagraphStyle(
    "H1",
    fontSize=16,
    textColor=colors.HexColor("#1a5f7a"),
    spaceBefore=20,
    spaceAfter=10,
    fontName="Helvetica-Bold",
)
h2_style = ParagraphStyle(
    "H2",
    fontSize=13,
    textColor=colors.HexColor("#2e8b57"),
    spaceBefore=15,
    spaceAfter=8,
    fontName="Helvetica-Bold",
)
h3_style = ParagraphStyle(
    "H3",
    fontSize=11,
    textColor=colors.HexColor("#4a4a4a"),
    spaceBefore=12,
    spaceAfter=6,
    fontName="Helvetica-Bold",
)
body_style = ParagraphStyle("Body", fontSize=9, leading=12, alignment=4, spaceAfter=6)
code_style = ParagraphStyle(
    "Code",
    fontSize=7,
    leading=9,
    fontName="Courier",
    backColor=colors.HexColor("#f5f5f5"),
    borderPadding=3,
)

story = []
in_code = False
code_lines = []

for line in lines:
    if line.startswith("```"):
        if in_code:
            # End code block
            story.append(Paragraph("<br/>".join(code_lines), code_style))
            story.append(Spacer(1, 8))
            code_lines = []
        in_code = not in_code
        continue

    if in_code:
        code_lines.append(line.rstrip())
        continue

    # Skip TOC
    if "Table of Contents" in line and "#" in line[:5]:
        continue

    if line.startswith("# "):
        story.append(Paragraph(line[2:].strip(), title_style))
        story.append(Spacer(1, 15))
    elif line.startswith("## "):
        story.append(Paragraph(line[3:].strip(), h1_style))
    elif line.startswith("### "):
        story.append(Paragraph(line[4:].strip(), h2_style))
    elif line.startswith("#### "):
        story.append(Paragraph(line[5:].strip(), h3_style))
    elif line.startswith("|"):
        # Simple table handling
        continue
    elif line.startswith("- "):
        story.append(Paragraph(f"• {line[2:].strip()}", body_style))
    elif line.strip() == "":
        story.append(Spacer(1, 5))
    elif not line.startswith("---"):
        # Clean basic markdown
        text = line.strip().replace("**", "").replace("`", "")
        if text and not text.startswith("#"):
            story.append(Paragraph(text, body_style))

print("Building PDF...")
doc = SimpleDocTemplate(
    pdf_file,
    pagesize=A4,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
    topMargin=0.75 * inch,
    bottomMargin=0.75 * inch,
)
doc.build(story)
print(f"PDF created: {pdf_file}")
