"""Game-sheet rendering and binder PDF assembly."""

from io import BytesIO
from pathlib import Path
import tempfile
from xml.sax.saxutils import escape

import yaml
from PIL import Image, ImageOps

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
WEBP_SUFFIX = ".webp"


class PdfAssetError(ValueError):
    """Raised when configured artwork cannot be used for PDF generation."""


PAGE_W, PAGE_H = letter
SPREAD_SIZE = (PAGE_W * 2, PAGE_H)

OUTER_MARGIN = 0.38 * inch
INNER_MARGIN = 0.75 * inch
TOP_MARGIN = 0.42 * inch
BOTTOM_MARGIN = 0.52 * inch
GUTTER = 0.16 * inch

USABLE_W = PAGE_W - OUTER_MARGIN - INNER_MARGIN
COL_W = (USABLE_W - GUTTER) / 2
COL_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN
BODY_FONT_SIZE = 8.5
BODY_LEADING = 9.7
SHOTS_GAP = 0.16 * inch

INK = colors.HexColor("#142735")
ACCENT = colors.HexColor("#176B75")
MUTED = colors.HexColor("#53636C")
PALE = colors.HexColor("#EAF2F3")
RULE = colors.HexColor("#AAB8BD")
PAPER_TINT = colors.HexColor("#F7F9F8")


styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=20.5,
    spaceAfter=3,
    alignment=TA_LEFT,
    textColor=INK,
)

SUBTITLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=BODY_FONT_SIZE,
    leading=BODY_LEADING,
    textColor=MUTED,
)

SECTION = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=9.4,
    leading=10.2,
    spaceBefore=5.5,
    spaceAfter=2.5,
    keepWithNext=True,
    textColor=ACCENT,
)

BODY = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=BODY_FONT_SIZE,
    leading=BODY_LEADING,
    spaceAfter=2,
    textColor=INK,
)

SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
)

FACT_LABEL = ParagraphStyle(
    "FactLabel",
    parent=SMALL,
    fontName="Helvetica-Bold",
    spaceAfter=0,
    textColor=ACCENT,
)

FACT_VALUE = ParagraphStyle(
    "FactValue",
    parent=SMALL,
    spaceAfter=0,
)

TABLE_HEADER = ParagraphStyle(
    "TableHeader",
    parent=SMALL,
    fontName="Helvetica-Bold",
    fontSize=7.6,
    leading=8.2,
    spaceAfter=0,
    textColor=colors.white,
)

TABLE_BODY = ParagraphStyle(
    "TableBody",
    parent=SMALL,
    fontSize=7.5,
    leading=8.3,
    spaceAfter=0,
)

HOOK = ParagraphStyle(
    "Hook",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=BODY_FONT_SIZE,
    leading=BODY_LEADING,
    borderWidth=0.75,
    borderColor=RULE,
    borderPadding=5.5,
    backColor=PALE,
    textColor=INK,
    spaceAfter=4,
)

SUMMARY = ParagraphStyle(
    "Summary",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=11.5,
    alignment=TA_CENTER,
    borderWidth=0.8,
    borderColor=ACCENT,
    borderPadding=5.5,
    backColor=PALE,
    textColor=INK,
    spaceBefore=4,
)


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def safe(text):
    if text is None:
        return ""

    return (
        str(text)
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .replace("\u2192", "->")
    )


def markup(text):
    return escape(safe(text))


def section(title):
    return Paragraph(markup(title).upper(), SECTION)


def bullet(text, style=BODY):
    return Paragraph(f"&bull;&nbsp; {markup(text)}", style)


def resolve_image_path(image_path, black_and_white=False, root=ROOT):
    path = Path(image_path)

    if path.suffix.lower() != WEBP_SUFFIX:
        raise PdfAssetError(f"PDF image assets must be WebP: {image_path}")

    if black_and_white and not path.stem.endswith("-bw"):
        path = path.with_name(f"{path.stem}-bw{path.suffix}")

    resolved = root / path
    if not resolved.is_file():
        mode = "black-and-white" if black_and_white else "color"
        raise PdfAssetError(f"missing {mode} WebP image asset: {resolved}")
    return resolved


def build_blocks(data, black_and_white=False):
    """Build semantic blocks so they can be balanced across three columns."""
    del black_and_white  # Image placement is handled by the spread page callback.

    metadata = data.get("metadata", {})
    header_parts = [
        safe(data.get("manufacturer")),
        safe(data.get("year")),
        safe(metadata.get("designer")),
        safe(metadata.get("era")),
    ]

    blocks = [
        [
            Paragraph(markup(data["name"]).upper(), TITLE),
            Paragraph(
                " &nbsp;&bull;&nbsp; ".join(
                    markup(part) for part in header_parts if part
                ),
                SUBTITLE,
            ),
            Spacer(1, 4),
            Paragraph(markup(data.get("hook")), HOOK),
        ]
    ]

    facts = [
        [
            Paragraph(markup(label), FACT_LABEL),
            Paragraph(markup(value), FACT_VALUE),
        ]
        for label, value in (
            ("Designer", metadata.get("designer", "")),
            ("Artist", metadata.get("artist", "")),
            ("Production", metadata.get("production", "")),
            ("Multiball", metadata.get("multiball", "")),
        )
    ]

    fact_table = Table(
        facts,
        colWidths=[0.72 * inch, COL_W - 0.72 * inch],
        hAlign="LEFT",
    )
    fact_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    blocks.append([fact_table])

    rules = data.get("rules", {})
    rules_block = [
        section("15-second rules"),
        Paragraph(f"<b>Primary:</b> {markup(rules.get('primary'))}", BODY),
    ]
    rules_block.extend(bullet(item) for item in rules.get("bullets", []))
    blocks.append(rules_block)

    watch_block = [section("What matters")]
    watch_block.extend(
        Paragraph(
            f"<b>{markup(item.get('title'))}:</b> {markup(item.get('text'))}",
            BODY,
        )
        for item in data.get("watch", [])
    )
    blocks.append(watch_block)

    skill_shots = data.get("skill_shots", [])
    if skill_shots:
        skill_block = [section("Skill shots")]
        skill_block.extend(
            Paragraph(
                f"<b>{markup(item.get('name'))}:</b> "
                f"{markup(item.get('how'))} "
                f"<i>{markup(item.get('value'))}</i>",
                BODY,
            )
            for item in skill_shots
        )
        blocks.append(skill_block)

    features = data.get("features", [])
    if features:
        feature_block = [section("Special features")]
        feature_block.extend(
            Paragraph(
                f"<b>{markup(item.get('name'))}:</b> "
                f"{markup(item.get('text'))}",
                BODY,
            )
            for item in features
        )
        blocks.append(feature_block)

    shot_rows = [
        [
            Paragraph("#", TABLE_HEADER),
            Paragraph("Shot", TABLE_HEADER),
            Paragraph("Why", TABLE_HEADER),
            Paragraph("Risk", TABLE_HEADER),
        ]
    ]
    for shot in data.get("shots", []):
        shot_rows.append(
            [
                Paragraph(markup(shot.get("diagram")), TABLE_BODY),
                Paragraph(markup(shot.get("name")), TABLE_BODY),
                Paragraph(markup(shot.get("value")), TABLE_BODY),
                Paragraph(markup(shot.get("risk")), TABLE_BODY),
            ]
        )

    shots = Table(
        shot_rows,
        colWidths=[0.18 * inch, 0.72 * inch, COL_W - 1.58 * inch, 0.68 * inch],
        repeatRows=1,
        hAlign="LEFT",
    )
    shots.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, RULE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER_TINT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    blocks.append([section("Important shots"), shots])

    strategy = data.get("strategy", {})
    blocks.append(
        [
            section("Match strategy"),
            Paragraph(f"<b>Ahead:</b> {markup(strategy.get('ahead'))}", BODY),
            Paragraph(f"<b>Behind:</b> {markup(strategy.get('behind'))}", BODY),
            Paragraph(
                f"<b>Key decision:</b> {markup(strategy.get('key_decision'))}",
                BODY,
            ),
        ]
    )

    danger_block = [section("Danger zones")]
    danger_block.extend(bullet(item) for item in data.get("danger", []))
    blocks.append(danger_block)

    commentary_block = [section("Commentary cues")]
    commentary_block.extend(
        Paragraph(f'&ldquo;{markup(item)}&rdquo;', SMALL)
        for item in data.get("commentary", [])
    )
    blocks.append(commentary_block)

    trivia_block = [section("Trivia / filler")]
    trivia_block.extend(bullet(item, SMALL) for item in data.get("trivia", []))
    blocks.append(trivia_block)

    notes = [item for item in data.get("venue_notes", []) if item]
    notes_block = [section("Venue notes")]
    if notes:
        notes_block.extend(bullet(item, SMALL) for item in notes)
    else:
        notes_block.extend(
            [
                Paragraph("________________________________________", SMALL),
                Paragraph("________________________________________", SMALL),
            ]
        )
    blocks.append(notes_block)

    blocks.append(
        [
            KeepTogether(
                [
                    Spacer(1, 4),
                    Paragraph(markup(data.get("summary")), SUMMARY),
                ]
            )
        ]
    )

    return blocks


def build_story(data, black_and_white=False):
    """Return an unpartitioned story for compatibility and text-level tests."""
    return [
        flowable
        for block in build_blocks(data, black_and_white)
        for flowable in block
    ]


def _flowable_height(flowable, canvas):
    if isinstance(flowable, KeepTogether):
        return sum(
            _flowable_height(item, canvas)
            for item in flowable._content
        )

    _, height = flowable.wrapOn(canvas, COL_W, COL_H)
    return flowable.getSpaceBefore() + height + flowable.getSpaceAfter()


def _is_shots_block(block):
    first = block[0] if block else None
    return (
        isinstance(first, Paragraph)
        and first.getPlainText() == "IMPORTANT SHOTS"
    )


def _prepare_print_image(source, directory, dpi=220):
    """Create a bounded JPEG derivative without changing the canonical WebP."""
    target = directory / f"{source.stem}-print.jpg"
    max_size = (
        round((COL_W / inch) * dpi),
        round((COL_H / inch) * dpi),
    )
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        if image.mode in {"RGBA", "LA"}:
            background = Image.new("RGB", image.size, "white")
            background.paste(image, mask=image.getchannel("A"))
            image = background
        elif image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        image.save(target, "JPEG", quality=90, optimize=True, progressive=True)
    return target


def _draw_spread_chrome(canvas, image_path, title):
    image_x = PAGE_W + INNER_MARGIN + COL_W + GUTTER

    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.45)
    footer_y = BOTTOM_MARGIN - 0.16 * inch
    canvas.line(OUTER_MARGIN, footer_y, PAGE_W - INNER_MARGIN, footer_y)
    canvas.line(
        PAGE_W + INNER_MARGIN,
        footer_y,
        (2 * PAGE_W) - OUTER_MARGIN,
        footer_y,
    )
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(OUTER_MARGIN, footer_y - 9, "PINBALL COMMENTARY BINDER")
    canvas.drawRightString(
        (2 * PAGE_W) - OUTER_MARGIN,
        footer_y - 9,
        safe(title).upper(),
    )

    if image_path:
        with Image.open(image_path) as image:
            image_width, image_height = image.size
        scale = min(COL_W / image_width, COL_H / image_height)
        draw_width = image_width * scale
        draw_height = image_height * scale
        draw_x = image_x + ((COL_W - draw_width) / 2)
        draw_y = BOTTOM_MARGIN + COL_H - draw_height
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.rect(draw_x, draw_y, draw_width, draw_height, stroke=1, fill=0)
        canvas.drawImage(
            str(image_path),
            draw_x,
            draw_y,
            width=draw_width,
            height=draw_height,
            mask="auto",
        )
    canvas.restoreState()


def _split_spread(spread_path, output_path, title, prepend_blank_page=False):
    reader = PdfReader(str(spread_path))
    if len(reader.pages) != 1:
        raise ValueError(
            f"expected one rendered spread for {title!r}, got {len(reader.pages)}"
        )

    source = reader.pages[0]
    writer = PdfWriter()
    if prepend_blank_page:
        writer.add_blank_page(width=PAGE_W, height=PAGE_H)
    for page_number in range(2):
        page = writer.add_blank_page(width=PAGE_W, height=PAGE_H)
        page.merge_transformed_page(
            source,
            Transformation().translate(tx=-(PAGE_W * page_number), ty=0),
        )

    writer.add_metadata(
        {
            "/Title": safe(title),
            "/Author": "Pinball Commentary Binder",
        }
    )
    with output_path.open("wb") as stream:
        writer.write(stream)


def render_game(
    content_path: Path,
    output_path: Path,
    black_and_white=False,
    asset_root=ROOT,
    prepend_blank_page=False,
):
    data = load_yaml(content_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    blocks = build_blocks(data, black_and_white)
    shots_block = next(block for block in blocks if _is_shots_block(block))
    text_blocks = [block for block in blocks if block is not shots_block]

    measuring_canvas = Canvas(BytesIO(), pagesize=SPREAD_SIZE)
    shots_height = sum(
        _flowable_height(flowable, measuring_canvas)
        for flowable in shots_block
    ) + 2
    third_column_height = COL_H - shots_height - SHOTS_GAP
    if third_column_height <= 0:
        raise ValueError("Important Shots is too tall for column three")

    text_columns = [
        Frame(
            OUTER_MARGIN,
            BOTTOM_MARGIN,
            COL_W,
            COL_H,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="text-1",
        ),
        Frame(
            OUTER_MARGIN + COL_W + GUTTER,
            BOTTOM_MARGIN,
            COL_W,
            COL_H,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="text-2",
        ),
        Frame(
            PAGE_W + INNER_MARGIN,
            BOTTOM_MARGIN,
            COL_W,
            third_column_height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="text-3",
        ),
        Frame(
            PAGE_W + INNER_MARGIN,
            BOTTOM_MARGIN + third_column_height + SHOTS_GAP,
            COL_W,
            shots_height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="important-shots",
        ),
    ]

    configured_image = data.get("image")
    image_path = (
        resolve_image_path(configured_image, black_and_white, asset_root)
        if configured_image
        else None
    )

    with tempfile.TemporaryDirectory(dir=output_path.parent) as directory:
        temporary_directory = Path(directory)
        spread_path = temporary_directory / f"{output_path.stem}-spread.pdf"
        print_image = (
            _prepare_print_image(image_path, temporary_directory)
            if image_path
            else None
        )
        doc = BaseDocTemplate(
            str(spread_path),
            pagesize=SPREAD_SIZE,
            leftMargin=OUTER_MARGIN,
            rightMargin=OUTER_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
            title=data.get("name", ""),
            author="Pinball Commentary Binder",
        )
        doc.addPageTemplates(
            [
                PageTemplate(
                    id="two-page-spread",
                    frames=text_columns,
                    onPage=lambda canvas, _doc: _draw_spread_chrome(
                        canvas,
                        print_image,
                        data.get("name", ""),
                    ),
                )
            ]
        )
        story = [
            flowable
            for block in text_blocks
            for flowable in block
        ]
        story.append(FrameBreak)
        story.extend(shots_block)
        doc.build(story)
        _split_spread(
            spread_path,
            output_path,
            data.get("name", ""),
            prepend_blank_page,
        )

    print(f"Wrote {output_path}")


def merge_pdfs(paths, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()

    for path in paths:
        writer.append(str(path))

    with output_path.open("wb") as stream:
        writer.write(stream)

    print(f"Wrote {output_path} ({len(paths)} games)")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m pinscripts.pdf <input.yaml> <output.pdf>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    render_game(
        input_path,
        output_path,
        asset_root=Path("tests/fixtures"),
        prepend_blank_page=True,
    )
