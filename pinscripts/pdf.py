"""Game-sheet rendering and binder PDF assembly."""

from io import BytesIO
from pathlib import Path
import tempfile
from xml.sax.saxutils import escape

import yaml
from PIL import Image, ImageOps

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    FrameBreak,
    Image as PdfImage,
    NextFrameFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .shot_labels import ShotLabelError, draw_shot_labels, load_shot_labels


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
BODY_LEADING = 10
SMALL_FONT_SIZE = BODY_FONT_SIZE
SMALL_LEADING = BODY_LEADING
SECTION_FONT_SIZE = 10
SECTION_LEADING = 12
TITLE_FONT_SIZE = 20
TITLE_LEADING = 22
SUMMARY_FONT_SIZE = BODY_FONT_SIZE
SUMMARY_LEADING = BODY_LEADING

SPACE_XS = 2
SPACE_SM = 4
SPACE_MD = 6
SPACE_LG = 8
TABLE_CELL_PADDING = SPACE_XS
SHOTS_GAP = SPACE_LG + SPACE_SM
HANDWRITING_LINE_SPACING = 0.3 * inch

INK = colors.HexColor("#142735")
ACCENT = colors.HexColor("#176B75")
MUTED = colors.HexColor("#53636C")
PALE = colors.HexColor("#EAF2F3")
RULE = colors.HexColor("#AAB8BD")
PAPER_TINT = colors.HexColor("#F7F9F8")
SECTION_STRIPE = colors.HexColor("#E3E6E7")


styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=TITLE_FONT_SIZE,
    leading=TITLE_LEADING,
    spaceAfter=SPACE_LG,
    alignment=TA_RIGHT,
    textColor=INK,
)

SECTION = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=SECTION_FONT_SIZE,
    leading=SECTION_LEADING,
    spaceAfter=0,
    textColor=INK,
)

SECTION_TABLE_STYLE = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, -1), SECTION_STRIPE),
        ("LEFTPADDING", (0, 0), (-1, -1), SPACE_XS),
        ("RIGHTPADDING", (0, 0), (-1, -1), SPACE_XS),
        ("TOPPADDING", (0, 0), (-1, -1), SPACE_XS),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]
)

BODY = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=BODY_FONT_SIZE,
    leading=BODY_LEADING,
    spaceAfter=SPACE_XS,
    textColor=INK,
)

SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
    fontSize=SMALL_FONT_SIZE,
    leading=SMALL_LEADING,
)

BULLET = ParagraphStyle(
    "Bullet",
    parent=BODY,
    spaceAfter=0,
)

TABLE_HEADER = ParagraphStyle(
    "TableHeader",
    parent=SMALL,
    fontName="Helvetica-Bold",
    spaceAfter=0,
    textColor=colors.white,
)

TABLE_BODY = ParagraphStyle(
    "TableBody",
    parent=SMALL,
    spaceAfter=0,
)

METADATA_LABEL = ParagraphStyle(
    "MetadataLabel",
    parent=TABLE_BODY,
    fontName="Helvetica-Bold",
    textColor=ACCENT,
)

HOOK = ParagraphStyle(
    "Hook",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=BODY_FONT_SIZE,
    leading=BODY_LEADING,
    textColor=INK,
    spaceAfter=0,
)

HOOK_TABLE_STYLE = TableStyle(
    [
        ("BOX", (0, 0), (-1, -1), 0.75, RULE),
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("RIGHTPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("TOPPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("BOTTOMPADDING", (0, 0), (-1, -1), SPACE_MD),
    ]
)

SUMMARY = ParagraphStyle(
    "Summary",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=SUMMARY_FONT_SIZE,
    leading=SUMMARY_LEADING,
    alignment=TA_CENTER,
    textColor=INK,
    spaceAfter=0,
)

SUMMARY_TABLE_STYLE = TableStyle(
    [
        ("BOX", (0, 0), (-1, -1), 0.8, ACCENT),
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("RIGHTPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("TOPPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("BOTTOMPADDING", (0, 0), (-1, -1), SPACE_MD),
    ]
)

DATA_TABLE_STYLE = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER_TINT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), SPACE_SM),
        ("RIGHTPADDING", (0, 0), (-1, -1), SPACE_SM),
        ("TOPPADDING", (0, 0), (-1, -1), SPACE_SM),
        ("BOTTOMPADDING", (0, 0), (-1, -1), SPACE_SM),
    ]
)


class HandwrittenNotes(Flowable):
    """Fill the available frame height with evenly spaced writing lines."""

    def __init__(self, line_spacing=HANDWRITING_LINE_SPACING):
        super().__init__()
        self.line_spacing = line_spacing

    def wrap(self, available_width, available_height):
        self.width = available_width
        self.available_height = max(0, available_height)
        return self.width, 0

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(RULE)
        self.canv.setLineWidth(0.35)
        line_y = -self.line_spacing
        while line_y >= -self.available_height:
            self.canv.line(0, line_y, self.width, line_y)
            line_y -= self.line_spacing
        self.canv.restoreState()

METADATA_TABLE_STYLE = TableStyle(
    [
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, RULE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, PAPER_TINT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), TABLE_CELL_PADDING),
        ("RIGHTPADDING", (0, 0), (-1, -1), TABLE_CELL_PADDING),
        ("RIGHTPADDING", (0, 0), (0, -1), SPACE_SM),
        ("LEFTPADDING", (1, 0), (1, -1), SPACE_SM),
        ("TOPPADDING", (0, 0), (-1, -1), SPACE_SM),
        ("BOTTOMPADDING", (0, 0), (-1, -1), SPACE_SM),
    ]
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
        .replace("->", "\u2192")
    )


def markup(text):
    return escape(safe(text))


def display_risk(text):
    value = safe(text)
    return "Med/High" if value == "Medium-High" else value


def section(title):
    heading = Table(
        [[Paragraph(markup(title).upper(), SECTION)]],
        colWidths=[COL_W],
        hAlign="LEFT",
        spaceBefore=SPACE_LG,
        spaceAfter=1,
    )
    heading.setStyle(SECTION_TABLE_STYLE)
    heading.keepWithNext = True
    heading.is_section_heading = True
    heading.section_title = safe(title).upper()
    return heading


def bullet(text):
    return Paragraph(f"&bull;&nbsp; {markup(text)}", BULLET)


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
    blocks = [[Paragraph(markup(data["name"]).upper(), TITLE)]]

    fact_rows = [
        [
            Paragraph(markup(label), METADATA_LABEL),
            Paragraph(markup(value), TABLE_BODY),
        ]
        for label, value in (
            ("Manufacturer", metadata.get("manufacturer", "")),
            ("Year", metadata.get("year", "")),
            ("Designer", metadata.get("designer", "")),
            ("Artist", metadata.get("artist", "")),
            ("Production", metadata.get("production", "")),
            ("Era", metadata.get("era", "")),
            ("Multiball", metadata.get("multiball", "")),
        )
    ]
    fact_table = Table(
        fact_rows,
        colWidths=[0.94 * inch, COL_W - 0.94 * inch],
        hAlign="LEFT",
    )
    fact_table.setStyle(METADATA_TABLE_STYLE)
    blocks.append([fact_table])
    hook_box = Table(
        [[Paragraph(markup(data.get("hook")), HOOK)]],
        colWidths=[COL_W],
        hAlign="LEFT",
        spaceAfter=SPACE_SM,
    )
    hook_box.setStyle(HOOK_TABLE_STYLE)
    blocks.append([section("Rules Summary (15-30 seconds)"), hook_box])

    rules = data.get("rules", {})
    rules_block = [
        Paragraph(markup(rules.get("primary")), BODY),
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
                Paragraph(markup(display_risk(shot.get("risk"))), TABLE_BODY),
            ]
        )

    shots = Table(
        shot_rows,
        colWidths=[0.24 * inch, 0.86 * inch, COL_W - 1.78 * inch, 0.68 * inch],
        repeatRows=1,
        hAlign="LEFT",
    )
    shots.setStyle(DATA_TABLE_STYLE)
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
    trivia_block.extend(bullet(item) for item in data.get("trivia", []))
    blocks.append(trivia_block)

    summary_box = Table(
        [[Paragraph(markup(data.get("summary")), SUMMARY)]],
        colWidths=[COL_W],
        hAlign="LEFT",
        spaceBefore=SPACE_LG,
        spaceAfter=SPACE_LG,
    )
    summary_box.setStyle(SUMMARY_TABLE_STYLE)
    summary_box.is_summary_box = True
    blocks.append([summary_box])

    notes = [item for item in data.get("venue_notes", []) if item]
    notes_block = [section("Venue notes")]
    notes_block.extend(bullet(item) for item in notes)
    blocks.append(notes_block)

    return blocks


def build_story(data, black_and_white=False):
    """Return an unpartitioned story for compatibility and text-level tests."""
    return [
        flowable
        for block in build_blocks(data, black_and_white)
        for flowable in block
    ]


def _flowable_height(flowable, canvas):
    _, height = flowable.wrapOn(canvas, COL_W, COL_H)
    return flowable.getSpaceBefore() + height + flowable.getSpaceAfter()


def _is_shots_block(block):
    first = block[0] if block else None
    return getattr(first, "section_title", None) == "IMPORTANT SHOTS"


def _is_section_block(block, title):
    first = block[0] if block else None
    return getattr(first, "section_title", None) == title.upper()


def _is_summary_block(block):
    return len(block) == 1 and getattr(block[0], "is_summary_box", False)


def _partition_leading_story(blocks, capacities, canvas):
    """Lay out ordered paragraphs before the fixed tail of column three."""
    flowables = [flowable for block in blocks for flowable in block]
    heights = [
        _flowable_height(flowable, canvas)
        for flowable in flowables
    ]
    valid_breaks = [
        index
        for index in range(1, len(flowables) + 1)
        if index == len(flowables)
        or not getattr(flowables[index - 1], "is_section_heading", False)
    ]
    best = None
    for first_break in valid_breaks:
        for second_break in (
            index for index in valid_breaks if index >= first_break
        ):
            column_heights = (
                sum(heights[:first_break]),
                sum(heights[first_break:second_break]),
                sum(heights[second_break:]),
            )
            overflow = sum(
                max(0, height - capacity) ** 2
                for height, capacity in zip(column_heights, capacities)
            )
            score = (
                overflow > 0,
                overflow,
                column_heights[2],
                abs(column_heights[0] - column_heights[1]),
            )
            if best is None or score < best[0]:
                best = (score, first_break, second_break)

    if best is None or best[0][0]:
        raise ValueError("content cannot fit before the fixed column-three notes")

    _, first_break, second_break = best
    story = list(flowables[:first_break])
    story.append(FrameBreak)
    story.extend(flowables[first_break:second_break])
    story.append(FrameBreak)
    story.extend(flowables[second_break:])
    return story


def _prepare_print_image(
    source,
    directory,
    dpi=220,
    shot_labels=None,
    black_and_white=False,
):
    """Create a bounded JPEG derivative without changing the canonical WebP."""
    target = directory / f"{source.stem}-print.jpg"
    max_size = (
        round((COL_W / inch) * dpi),
        round((COL_H / inch) * dpi),
    )
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        if shot_labels:
            expected_size = (
                shot_labels["image_width"],
                shot_labels["image_height"],
            )
            if image.size != expected_size:
                raise PdfAssetError(
                    f"labeled image is {expected_size[0]}x{expected_size[1]}, "
                    f"but print source is {image.width}x{image.height}"
                )
            image = draw_shot_labels(
                image,
                shot_labels["coordinates"],
                black_and_white,
            )
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        if image.mode in {"RGBA", "LA"}:
            background = Image.new("RGB", image.size, "white")
            background.paste(image, mask=image.getchannel("A"))
            image = background
        elif image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        image.save(target, "JPEG", quality=90, optimize=True, progressive=True)
    return target


def _build_reference_story(blocks, image_path, canvas):
    story = [flowable for block in blocks for flowable in block]
    if not image_path:
        return story

    image_gap = SPACE_LG
    content_height = sum(_flowable_height(item, canvas) for item in story)
    available_height = COL_H - content_height - image_gap

    with Image.open(image_path) as image:
        image_width, image_height = image.size

    scale = min(COL_W / image_width, available_height / image_height)
    draw_width = image_width * scale
    draw_height = image_height * scale
    pdf_image = PdfImage(
        str(image_path),
        width=draw_width,
        height=draw_height,
    )
    image_box = Table(
        [[pdf_image]],
        colWidths=[draw_width],
        rowHeights=[draw_height],
        hAlign="CENTER",
    )
    image_box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    bottom_space = max(0, available_height - draw_height)
    story.extend([Spacer(1, image_gap + bottom_space), image_box])
    return story


def _draw_spread_chrome(canvas, title):

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
    summary_block = next(block for block in blocks if _is_summary_block(block))
    venue_notes_block = next(
        block for block in blocks if _is_section_block(block, "Venue notes")
    )
    reference_blocks = blocks[:2]
    leading_blocks = [
        block
        for block in blocks[2:]
        if block is not shots_block
        and block is not summary_block
        and block is not venue_notes_block
    ]

    measuring_canvas = Canvas(BytesIO(), pagesize=SPREAD_SIZE)
    shots_height = sum(
        _flowable_height(flowable, measuring_canvas)
        for flowable in shots_block
    ) + 2
    third_column_height = COL_H - shots_height - SHOTS_GAP
    if third_column_height <= 0:
        raise ValueError("Important Shots is too tall for column three")

    fixed_third_column_height = sum(
        _flowable_height(flowable, measuring_canvas)
        for block in (summary_block, venue_notes_block)
        for flowable in block
    )
    leading_capacities = (
        COL_H,
        COL_H,
        third_column_height - fixed_third_column_height,
    )
    if leading_capacities[2] <= 0:
        raise ValueError("Summary and venue notes are too tall for column three")

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
            BOTTOM_MARGIN + shots_height + SHOTS_GAP,
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
            BOTTOM_MARGIN,
            COL_W,
            shots_height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="important-shots",
        ),
        Frame(
            PAGE_W + INNER_MARGIN + COL_W + GUTTER,
            BOTTOM_MARGIN,
            COL_W,
            COL_H,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="reference",
        ),
    ]

    configured_image = data.get("image")
    image_path = (
        resolve_image_path(configured_image, black_and_white, asset_root)
        if configured_image
        else None
    )
    try:
        shot_labels = load_shot_labels(data, asset_root) if image_path else None
    except ShotLabelError as error:
        game_id = data.get("id", content_path.stem)
        raise PdfAssetError(
            f"invalid shot labels for {game_id}: {error}; "
            f"run make shot-labels GAME=\"{game_id}\""
        ) from error

    with tempfile.TemporaryDirectory(dir=output_path.parent) as directory:
        temporary_directory = Path(directory)
        spread_path = temporary_directory / f"{output_path.stem}-spread.pdf"
        print_image = (
            _prepare_print_image(
                image_path,
                temporary_directory,
                shot_labels=shot_labels,
                black_and_white=black_and_white,
            )
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
                        data.get("name", ""),
                    ),
                )
            ]
        )
        story = _partition_leading_story(
            leading_blocks,
            leading_capacities,
            measuring_canvas,
        )
        story.extend(summary_block)
        story.extend(venue_notes_block)
        story.append(HandwrittenNotes())
        story.extend([NextFrameFlowable("important-shots"), FrameBreak])
        story.extend(shots_block)
        story.extend([NextFrameFlowable("reference"), FrameBreak])
        story.extend(
            _build_reference_story(
                reference_blocks,
                print_image,
                measuring_canvas,
            )
        )
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
