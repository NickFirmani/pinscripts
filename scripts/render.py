#!/usr/bin/env python3

from pathlib import Path

import yaml

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent


PAGE_W, PAGE_H = letter

MARGIN = 0.35 * inch
GUTTER = 0.18 * inch

USABLE_W = PAGE_W - (2 * MARGIN)
COL_W = (USABLE_W - GUTTER) / 2


styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=21,
    leading=22,
    spaceAfter=2,
)

SUBTITLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=10,
    textColor=colors.HexColor("#444444"),
)

SECTION = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=11,
    spaceBefore=5,
    spaceAfter=3,
    textColor=colors.HexColor("#111111"),
)

BODY = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=7.7,
    leading=9.3,
    spaceAfter=2,
)

SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
    fontSize=6.8,
    leading=8,
)

HOOK = ParagraphStyle(
    "Hook",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=10,
    borderWidth=0.5,
    borderColor=colors.HexColor("#AAAAAA"),
    borderPadding=5,
    backColor=colors.HexColor("#F5F5F5"),
    spaceAfter=5,
)

SUMMARY = ParagraphStyle(
    "Summary",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=11,
    alignment=TA_CENTER,
    borderWidth=1,
    borderColor=colors.black,
    borderPadding=5,
    spaceBefore=4,
)


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def section(title):
    return Paragraph(title.upper(), SECTION)


def bullet(text, style=BODY):
    return Paragraph(f"&bull;&nbsp; {text}", style)


def safe(text):
    if text is None:
        return ""
    return str(text)


def resolve_image_path(image_path, black_and_white=False):
    path = Path(image_path)

    if black_and_white and not path.stem.endswith("-bw"):
        path = path.with_name(f"{path.stem}-bw{path.suffix}")

    return ROOT / path


def build_story(data, black_and_white=False):
    story = []

    # -------------------------------------------------------------
    # Header
    # -------------------------------------------------------------
    story.append(Paragraph(safe(data["name"]).upper(), TITLE))

    metadata = data.get("metadata", {})

    header_parts = [
        safe(data.get("manufacturer")),
        safe(data.get("year")),
        safe(metadata.get("designer")),
        safe(metadata.get("era")),
    ]

    story.append(
        Paragraph(
            " &nbsp;&bull;&nbsp; ".join(p for p in header_parts if p),
            SUBTITLE,
        )
    )

    story.append(Spacer(1, 4))
    story.append(Paragraph(safe(data.get("hook")), HOOK))

    # -------------------------------------------------------------
    # Quick facts
    # -------------------------------------------------------------
    facts = [
        ["Designer", metadata.get("designer", "")],
        ["Artist", metadata.get("artist", "")],
        ["Production", metadata.get("production", "")],
        ["Multiball", metadata.get("multiball", "")],
    ]

    fact_table = Table(
        facts,
        colWidths=[0.72 * inch, COL_W - 0.72 * inch],
    )

    fact_table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )

    story.append(fact_table)

    # -------------------------------------------------------------
    # Image
    # -------------------------------------------------------------
    image_path = data.get("image")

    if image_path:
        full_image_path = resolve_image_path(image_path, black_and_white)

        if full_image_path.exists():
            img = Image(str(full_image_path))

            max_w = COL_W
            max_h = 2.35 * inch

            ratio = min(max_w / img.imageWidth, max_h / img.imageHeight)

            img.drawWidth = img.imageWidth * ratio
            img.drawHeight = img.imageHeight * ratio

            story.append(Spacer(1, 4))
            story.append(img)

    # -------------------------------------------------------------
    # Rules
    # -------------------------------------------------------------
    story.append(section("15-second rules"))

    rules = data.get("rules", {})

    story.append(
        Paragraph(
            f"<b>Primary:</b> {safe(rules.get('primary'))}",
            BODY,
        )
    )

    for item in rules.get("bullets", []):
        story.append(bullet(item))

    # -------------------------------------------------------------
    # What matters
    # -------------------------------------------------------------
    story.append(section("What matters"))

    for item in data.get("watch", []):
        story.append(
            Paragraph(
                f"<b>{safe(item.get('title'))}:</b> "
                f"{safe(item.get('text'))}",
                BODY,
            )
        )

    # -------------------------------------------------------------
    # Shots table
    # -------------------------------------------------------------
    story.append(section("Important shots"))

    shot_rows = [["#", "Shot", "Why", "Risk"]]

    for shot in data.get("shots", []):
        shot_rows.append(
            [
                safe(shot.get("diagram")),
                safe(shot.get("name")),
                safe(shot.get("value")),
                safe(shot.get("risk")),
            ]
        )

    shots = Table(
        shot_rows,
        colWidths=[
            0.20 * inch,
            0.78 * inch,
            COL_W - 1.65 * inch,
            0.67 * inch,
        ],
        repeatRows=1,
    )

    shots.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Helvetica", 6.3),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#AAAAAA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    story.append(shots)

    # -------------------------------------------------------------
    # Strategy
    # -------------------------------------------------------------
    strategy = data.get("strategy", {})

    story.append(section("Match strategy"))

    story.append(
        Paragraph(
            f"<b>Ahead:</b> {safe(strategy.get('ahead'))}",
            BODY,
        )
    )

    story.append(
        Paragraph(
            f"<b>Behind:</b> {safe(strategy.get('behind'))}",
            BODY,
        )
    )

    story.append(
        Paragraph(
            f"<b>Key decision:</b> {safe(strategy.get('key_decision'))}",
            BODY,
        )
    )

    # -------------------------------------------------------------
    # Danger
    # -------------------------------------------------------------
    story.append(section("Danger zones"))

    for item in data.get("danger", []):
        story.append(bullet(item))

    # -------------------------------------------------------------
    # Commentary
    # -------------------------------------------------------------
    story.append(section("Commentary cues"))

    for item in data.get("commentary", []):
        story.append(
            Paragraph(
                f'&ldquo;{safe(item)}&rdquo;',
                SMALL,
            )
        )

    # -------------------------------------------------------------
    # Trivia
    # -------------------------------------------------------------
    story.append(section("Trivia / filler"))

    for item in data.get("trivia", []):
        story.append(bullet(item, SMALL))

    # -------------------------------------------------------------
    # Venue-specific
    # -------------------------------------------------------------
    story.append(section("Venue notes"))

    notes = [x for x in data.get("venue_notes", []) if x]

    if notes:
        for item in notes:
            story.append(bullet(item, SMALL))
    else:
        story.append(Paragraph("________________________________________", SMALL))
        story.append(Paragraph("________________________________________", SMALL))

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    story.append(
        KeepTogether(
            [
                Spacer(1, 4),
                Paragraph(safe(data.get("summary")), SUMMARY),
            ]
        )
    )

    return story


def render_game(content_path: Path, output_path: Path, black_and_white=False):
    data = load_yaml(content_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    frame_left = Frame(
        MARGIN,
        MARGIN,
        COL_W,
        PAGE_H - 2 * MARGIN,
        leftPadding=0,
        rightPadding=GUTTER / 2,
        topPadding=0,
        bottomPadding=0,
        id="left",
    )

    frame_right = Frame(
        MARGIN + COL_W + GUTTER,
        MARGIN,
        COL_W,
        PAGE_H - 2 * MARGIN,
        leftPadding=GUTTER / 2,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="right",
    )

    doc = BaseDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=data.get("name", ""),
        author="Pinball Commentary Binder",
    )

    doc.addPageTemplates(
        [
            PageTemplate(
                id="one-page",
                frames=[frame_left, frame_right],
            )
        ]
    )

    doc.build(build_story(data, black_and_white))

    print(f"Wrote {output_path}")


def merge_pdfs(paths, output_path: Path):
    from pypdf import PdfWriter

    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()

    for path in paths:
        writer.append(str(path))

    with output_path.open("wb") as f:
        writer.write(f)

    print(f"Wrote {output_path} ({len(paths)} games)")
