"""Game-sheet rendering and binder PDF assembly."""

from datetime import date
from io import BytesIO
from pathlib import Path
import subprocess
import tempfile
from xml.sax.saxutils import escape

import qrcode
import yaml
from PIL import Image, ImageOps

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
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
BOTTOM_MARGIN = 0.44 * inch
FOOTER_Y = 0.36 * inch
GUTTER = 0.16 * inch

USABLE_W = PAGE_W - OUTER_MARGIN - INNER_MARGIN
COL_W = (USABLE_W - GUTTER) / 2
COL_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN

BODY_FONT_SIZE = 9
BODY_LEADING = 11
SMALL_FONT_SIZE = BODY_FONT_SIZE
SMALL_LEADING = BODY_LEADING
SECTION_FONT_SIZE = 10
SECTION_LEADING = 12
TITLE_FONT_SIZE = 20
TITLE_LEADING = 22

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
    spaceBefore=2,
    spaceAfter=6,
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
    spaceAfter=5,
)

TABLE_HEADER = ParagraphStyle(
    "TableHeader",
    parent=SMALL,
    fontName="Helvetica-Bold",
    spaceAfter=0,
    textColor=INK,
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

CALLOUT_TEXT = ParagraphStyle(
    "CalloutText",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=BODY_FONT_SIZE,
    leading=BODY_LEADING,
    textColor=INK,
    spaceAfter=0,
)

CALLOUT_TABLE_STYLE = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, -1), SECTION_STRIPE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("RIGHTPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("TOPPADDING", (0, 0), (-1, -1), SPACE_MD),
        ("BOTTOMPADDING", (0, 0), (-1, -1), SPACE_MD),
    ]
)

DATA_TABLE_STYLE = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, 0), SECTION_STRIPE),
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


def git_updated_at(content_path: Path, repo_root=ROOT):
    """Return the date of the most recent commit that changed a content file."""
    try:
        relative_path = content_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return "UNKNOWN"

    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "log",
                "-1",
                "--format=%as",
                "--follow",
                "--",
                relative_path.as_posix(),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "UNKNOWN"

    return result.stdout.strip() or date.today().isoformat()


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
        spaceAfter=0,
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
        [[Paragraph(markup(data.get("hook")), CALLOUT_TEXT)]],
        colWidths=[COL_W],
        hAlign="LEFT",
        spaceBefore=0,
        spaceAfter=SPACE_SM,
    )
    hook_box.setStyle(CALLOUT_TABLE_STYLE)
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

    summary_box = Table(
        [[Paragraph(markup(data.get("summary")), CALLOUT_TEXT)]],
        colWidths=[COL_W],
        hAlign="LEFT",
        spaceBefore=0,
        spaceAfter=SPACE_SM,
    )
    summary_box.setStyle(CALLOUT_TABLE_STYLE)

    strategy = data.get("strategy", {})
    blocks.append(
        [
            section("Match strategy"),
            summary_box,
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


def _flowables_height(flowables, canvas):
    """Measure a flow sequence using ReportLab's collapsed spacing rules."""
    height = 0
    previous_space_after = 0
    for index, flowable in enumerate(flowables):
        _, wrapped_height = flowable.wrapOn(canvas, COL_W, COL_H)
        if index:
            height += max(
                flowable.getSpaceBefore() - previous_space_after,
                0,
            )
        height += wrapped_height + flowable.getSpaceAfter()
        previous_space_after = flowable.getSpaceAfter()
    return height


def _is_shots_block(block):
    first = block[0] if block else None
    return getattr(first, "section_title", None) == "IMPORTANT SHOTS"


def _is_section_block(block, title):
    first = block[0] if block else None
    return getattr(first, "section_title", None) == title.upper()


def _partition_leading_story(blocks, capacities, canvas):
    """Fill each text column in order before advancing to the next."""
    flowables = [flowable for block in blocks for flowable in block]
    chunks = []
    index = 0
    while index < len(flowables):
        chunk = [flowables[index]]
        if (
            getattr(flowables[index], "is_section_heading", False)
            and index + 1 < len(flowables)
        ):
            index += 1
            chunk.append(flowables[index])
        chunks.append(chunk)
        index += 1

    columns = [[], [], []]
    column_index = 0
    for chunk in chunks:
        candidate_height = _flowables_height(
            [*columns[column_index], *chunk],
            canvas,
        )
        if (
            columns[column_index]
            and candidate_height > capacities[column_index]
        ):
            column_index += 1
        if column_index >= len(columns):
            raise ValueError("content cannot fit before the fixed column-three notes")
        candidate_height = _flowables_height(
            [*columns[column_index], *chunk],
            canvas,
        )
        if candidate_height > capacities[column_index]:
            raise ValueError("content cannot fit before the fixed column-three notes")
        columns[column_index].extend(chunk)

    story = list(columns[0])
    story.append(FrameBreak)
    story.extend(columns[1])
    story.append(FrameBreak)
    story.extend(columns[2])
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
            expected_aspect = expected_size[0] / expected_size[1]
            print_aspect = image.width / image.height
            if abs(expected_aspect - print_aspect) > 0.002:
                raise PdfAssetError(
                    "the labeled color image and print image have different "
                    "aspect ratios; regenerate the print image or redo the labels"
                )
            scale_x = image.width / expected_size[0]
            scale_y = image.height / expected_size[1]
            coordinates = [
                {
                    **point,
                    "x": round(point["x"] * scale_x),
                    "y": round(point["y"] * scale_y),
                }
                for point in shot_labels["coordinates"]
            ]
            image = draw_shot_labels(
                image,
                coordinates,
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
    content_height = _flowables_height(story, canvas)
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


def _draw_spread_chrome(
    canvas,
    title,
    updated_at,
    page_number_start=None,
    rules_basis=None,
    page_labels=None,
):
    if page_labels is None and page_number_start is not None:
        page_labels = (str(page_number_start), str(page_number_start + 1))
    if page_labels is not None:
        if len(page_labels) != 2:
            raise ValueError("page_labels must contain exactly two labels")
        page_labels = tuple(str(label) for label in page_labels)

    canvas.saveState()
    footer_y = FOOTER_Y
    canvas.setFillColor(MUTED)
    footer_text = rules_footer_text(rules_basis, updated_at)
    title_y = footer_y - 8
    detail_y = footer_y - 17

    if footer_text:
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.45)
        canvas.line(OUTER_MARGIN, footer_y, PAGE_W - INNER_MARGIN, footer_y)
        canvas.line(
            PAGE_W + INNER_MARGIN,
            footer_y,
            (2 * PAGE_W) - OUTER_MARGIN,
            footer_y,
        )
        page_label_width = (
            pdfmetrics.stringWidth(
                f"PAGE {page_labels[1]}",
                "Helvetica",
                6.5,
            )
            if page_labels is not None
            else 0
        )
        footer_width = USABLE_W - page_label_width - SPACE_MD
        footer_line = f"{safe(title).upper()} • {footer_text}"
        footer_font_size = min(
            6.5,
            6.5 * footer_width
            / max(pdfmetrics.stringWidth(footer_line, "Helvetica", 6.5), 1),
        )
        canvas.setFont("Helvetica", max(footer_font_size, 5.0))
        canvas.drawString(OUTER_MARGIN, title_y, footer_line)
        canvas.drawString(PAGE_W + INNER_MARGIN, title_y, footer_line)

    if page_labels is not None:
        canvas.setFont("Helvetica", 6.5)
        page_y = title_y if footer_text else detail_y
        canvas.drawRightString(
            PAGE_W - INNER_MARGIN,
            page_y,
            f"PAGE {page_labels[0]}",
        )
        canvas.drawRightString(
            (2 * PAGE_W) - OUTER_MARGIN,
            page_y,
            f"PAGE {page_labels[1]}",
        )

    canvas.restoreState()


def rules_footer_text(rules_basis, updated_at):
    """Return revision text for code/ROM games and none for fixed rules."""
    if not isinstance(rules_basis, dict):
        return None

    kind = rules_basis.get("kind")
    version = safe(rules_basis.get("version"))
    if kind == "code":
        release_date = safe(rules_basis.get("release_date"))
        return (
            f"CODE {version} • RELEASED {release_date} • "
            f"UPDATED AT {safe(updated_at)}"
        )
    if kind == "rom":
        return f"ROM {version} • UPDATED AT {safe(updated_at)}"
    return None


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
    page_number_start=None,
    page_labels=None,
):
    data = load_yaml(content_path)
    rules_basis = data.get("rules_basis")
    updated_at = (
        git_updated_at(content_path)
        if isinstance(rules_basis, dict)
        and rules_basis.get("kind") in {"code", "rom"}
        else None
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    blocks = build_blocks(data, black_and_white)
    shots_block = next(block for block in blocks if _is_shots_block(block))
    venue_notes_block = next(
        block for block in blocks if _is_section_block(block, "Venue notes")
    )
    reference_blocks = blocks[:2]
    leading_blocks = [
        block
        for block in blocks[2:]
        if block is not shots_block
        and block is not venue_notes_block
    ]

    measuring_canvas = Canvas(BytesIO(), pagesize=SPREAD_SIZE)
    shots_height = _flowables_height(shots_block, measuring_canvas) + 2
    third_column_height = COL_H - shots_height - SHOTS_GAP
    if third_column_height <= 0:
        raise ValueError("Important Shots is too tall for column three")

    fixed_third_column_height = _flowables_height(
        venue_notes_block,
        measuring_canvas,
    )
    leading_capacities = (
        COL_H,
        COL_H,
        third_column_height - fixed_third_column_height,
    )
    if leading_capacities[2] <= 0:
        raise ValueError("Venue notes are too tall for column three")

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
                        updated_at,
                        page_number_start,
                        rules_basis,
                        page_labels,
                    ),
                )
            ]
        )
        story = _partition_leading_story(
            leading_blocks,
            leading_capacities,
            measuring_canvas,
        )
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


def _title_page():
    title_page_stream = BytesIO()
    title_page = Canvas(title_page_stream, pagesize=letter)
    title_page.setTitle("Pinball Commentary Quickstart")
    title_page.setFillColor(INK)
    # Draw the following text in a centered position on the page
    # Draw the title first
    title_page.setFont("Helvetica-Bold", 24)
    title_page.drawCentredString(
        PAGE_W / 2,
        PAGE_H / 2 + 144,
        "Pinball Commentary Quick Reference",
    )
    subtitle = """A collection of quick informational sheets for pinball commentary.
    
    Disclaimer: The content was researched by LLMs (from official sources), and may contain inaccuracies. 
    
    If you find an issue or have notes on a game, please feel free to just write on the sheets! 
    
    The content lives at the GitHub repository below, and if you want to contribute, please submit a pull request.
    """.lstrip().replace("\n", "<br/>")
    subtitle_style = ParagraphStyle(
        "subtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
    )

    subtitle_width = 440
    subtitle_paragraph = Paragraph(subtitle, subtitle_style)

    w, h = subtitle_paragraph.wrap(subtitle_width, PAGE_H)

    subtitle_paragraph.drawOn(
        title_page,
        (PAGE_W - subtitle_width) / 2,
        (PAGE_H / 2) - 25,
    )

    # Add a link and QR code to the GitHub repository
    url = "https://github.com/NickFirmani/pinscripts"
    title_page.setFont("Helvetica", 10)
    title_page.drawCentredString(
        PAGE_W / 2,
        (PAGE_H / 2) - 50,
        f"GitHub Repository: {url}"
    )
    # Generate and add a QR code to the GitHub repository
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_stream = BytesIO()
    img.save(img_stream, format="PNG")
    img_stream.seek(0)

    title_page.drawImage(
        ImageReader(img_stream),
        (PAGE_W / 2) - 50,
        (PAGE_H / 2) - 160,
        width=100,
        height=100,
    )

    title_page.save()
    title_page_stream.seek(0)
    return PdfReader(title_page_stream).pages[0]


def merge_pdfs(paths, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    writer.add_page(_title_page())

    for path in paths:
        writer.append(str(path))

    with output_path.open("wb") as stream:
        writer.write(stream)

    print(f"Wrote {output_path} ({len(paths)} games)")


def merge_print_packet(
    target_path: Path,
    output_path: Path,
    preceding_path=None,
    following_path=None,
):
    """Create four pages ordered for two-sheet, long-edge duplex printing."""
    target = PdfReader(str(target_path))
    if len(target.pages) != 2:
        raise ValueError(f"print-packet target must have two pages: {target_path}")

    writer = PdfWriter()
    if preceding_path is None:
        writer.add_page(_title_page())
    else:
        preceding = PdfReader(str(preceding_path))
        if len(preceding.pages) != 2:
            raise ValueError(
                f"preceding print-packet game must have two pages: {preceding_path}"
            )
        writer.add_page(preceding.pages[1])

    writer.add_page(target.pages[0])
    writer.add_page(target.pages[1])

    if following_path is None:
        writer.add_blank_page(width=PAGE_W, height=PAGE_H)
    else:
        following = PdfReader(str(following_path))
        if len(following.pages) != 2:
            raise ValueError(
                f"following print-packet game must have two pages: {following_path}"
            )
        writer.add_page(following.pages[0])

    writer.add_metadata(
        {
            "/Title": f"Binder print packet - {target_path.stem}",
            "/Author": "Pinball Commentary Binder",
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as stream:
        writer.write(stream)
    print(f"Wrote {output_path} (4 pages; print duplex, flip on long edge)")


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
