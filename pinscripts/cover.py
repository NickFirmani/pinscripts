"""Printable front-cover and spine inserts for physical binders."""

from fractions import Fraction
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas


PAGE_W, PAGE_H = letter
MIN_SPINE_WIDTH = 0.5
MAX_SPINE_WIDTH = 5.0

INK = colors.HexColor("#142735")
ACCENT = colors.HexColor("#176B75")
MUTED = colors.HexColor("#53636C")
RULE = colors.HexColor("#AAB8BD")
PAPER_TINT = colors.HexColor("#F7F9F8")


class BinderCoverError(ValueError):
    """Raised when a binder insert cannot be generated."""


def parse_spine_width(value):
    """Return a validated spine width in inches.

    Decimal values and common mixed fractions such as ``1 1/2`` are accepted.
    The width is the physical spine pocket width, not the ring diameter.
    """
    if isinstance(value, bool):
        raise BinderCoverError("binder size must be a number of inches or common mixed fractions such as ``1 1/2``")

    if isinstance(value, (int, float)):
        width = float(value)
    else:
        text = str(value).strip().lower()
        text = re.sub(r"\s*(?:inches|inch|in\.?|\")\s*$", "", text)
        if not text:
            raise BinderCoverError("binder size is required")
        try:
            if " " in text and "/" in text:
                whole, fraction = text.split(None, 1)
                width = float(int(whole) + Fraction(fraction))
            elif "/" in text:
                width = float(Fraction(text))
            else:
                width = float(text)
        except (ValueError, ZeroDivisionError) as error:
            raise BinderCoverError(
                "binder size must be an inch measurement such as 1, 1.5, or 2"
            ) from error

    if not MIN_SPINE_WIDTH <= width <= MAX_SPINE_WIDTH:
        raise BinderCoverError(
            f"binder size must be between {MIN_SPINE_WIDTH:g} and "
            f"{MAX_SPINE_WIDTH:g} inches"
        )
    return width


def ask_spine_width(input_fn=input, output_fn=print):
    """Ask for a binder spine width until a valid measurement is entered."""
    while True:
        try:
            value = input_fn(
                "Binder spine width in inches (for example 1, 1.5, 2, or 3): "
            )
        except EOFError as error:
            raise BinderCoverError("binder size is required") from error
        try:
            return parse_spine_width(value)
        except BinderCoverError as error:
            output_fn(f"Please enter a valid size: {error}")


def _fit_font(text, font_name, maximum, minimum, available_width):
    size = float(maximum)
    while size > minimum and pdfmetrics.stringWidth(text, font_name, size) > available_width:
        size -= 0.5
    return max(size, float(minimum))


def _wrap_title(text, font_name, font_size, available_width, max_lines=3):
    words = text.split()
    lines = []
    current = []
    for word in words:
        candidate = " ".join((*current, word))
        if current and pdfmetrics.stringWidth(candidate, font_name, font_size) > available_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines if len(lines) <= max_lines else None


def _front_title_layout(title, available_width, maximum=38, minimum=21):
    for size in range(maximum, minimum - 1, -1):
        lines = _wrap_title(title, "Helvetica-Bold", size, available_width)
        if lines is not None:
            return float(size), lines
    return float(minimum), [title]


def _draw_front(canvas, location):
    margin = 0.58 * inch
    content_left = margin + 0.16 * inch
    title_left = content_left + 0.27 * inch
    title_width = PAGE_W - title_left - margin

    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(margin, margin, 0.13 * inch, PAGE_H - (2 * margin), fill=1, stroke=0)

    canvas.setFillColor(ACCENT)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(title_left, PAGE_H - margin - 0.05 * inch, location.upper())

    title_y = PAGE_H * 0.69
    title_size, title_lines = _front_title_layout(
        "PINBALL COMMENTARY GUIDES",
        title_width,
        maximum=44,
        minimum=28,
    )
    leading = title_size * 1.08
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", title_size)
    for line in title_lines:
        canvas.drawString(title_left, title_y, line)
        title_y -= leading

    rule_y = max(title_y - 0.18 * inch, PAGE_H * 0.43)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.8)
    canvas.line(title_left, rule_y, PAGE_W - margin, rule_y)

    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 13)
    canvas.drawString(title_left, rule_y - 0.34 * inch, "GUIDES TO THE RULES, STRATEGY, AND TRIVIA FOR THE GAMES")

    canvas.setFillColor(PAPER_TINT)
    canvas.roundRect(
        title_left,
        margin,
        PAGE_W - title_left - margin,
        0.48 * inch,
        0.08 * inch,
        fill=1,
        stroke=0,
    )
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(
        title_left + 0.16 * inch,
        margin + 0.18 * inch,
        "KNOW THE GAME • FIND THE STORY • CALL THE ACTION",
    )


def _draw_cut_mark(canvas, x, y, horizontal_direction, vertical_direction):
    mark = 0.18 * inch
    gap = 0.04 * inch
    canvas.line(x + (horizontal_direction * gap), y, x + (horizontal_direction * mark), y)
    canvas.line(x, y + (vertical_direction * gap), x, y + (vertical_direction * mark))


def _draw_spine(canvas, location, spine_width):
    width = spine_width * inch
    left = (PAGE_W - width) / 2
    right = left + width

    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(PAPER_TINT)
    canvas.rect(left, 0, width, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(left, 0, min(0.12 * inch, width * 0.12), PAGE_H, fill=1, stroke=0)

    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.55)
    canvas.line(left, 0, left, PAGE_H)
    canvas.line(right, 0, right, PAGE_H)
    for y, vertical_direction in ((0.25 * inch, 1), (PAGE_H - 0.25 * inch, -1)):
        _draw_cut_mark(canvas, left, y, -1, vertical_direction)
        _draw_cut_mark(canvas, right, y, 1, vertical_direction)

    available_length = PAGE_H - (1.75 * inch)
    title = "PINBALL COMMENTARY GUIDES"
    title_size = _fit_font(title, "Helvetica-Bold", 22, 10, available_length)
    canvas.saveState()
    canvas.translate((left + right) / 2, 0)
    canvas.rotate(90)
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", title_size)
    canvas.drawCentredString(PAGE_H / 2, -(title_size * 0.34), title)
    canvas.restoreState()

    canvas.saveState()
    canvas.translate(right - max(0.13 * inch, width * 0.12), 0)
    canvas.rotate(90)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica-Bold", 6.5)
    location_size = _fit_font(
        location.upper(),
        "Helvetica-Bold",
        6.5,
        5,
        PAGE_H - (0.76 * inch),
    )
    canvas.setFont("Helvetica-Bold", location_size)
    canvas.drawString(0.38 * inch, 0, location.upper())
    canvas.restoreState()


def render_binder_inserts(location, spine_width, output_path: Path):
    """Create a two-page letter PDF containing a front and spine insert."""
    if not isinstance(location, str) or not location.strip():
        raise BinderCoverError("binder title is required")
    width = parse_spine_width(spine_width)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    canvas = Canvas(str(destination), pagesize=letter)
    canvas.setTitle(f"{location.strip()} Pinball Commentary Binder Inserts")
    canvas.setAuthor("Pinball Commentary Binder")
    _draw_front(canvas, location.strip())
    canvas.showPage()
    _draw_spine(canvas, location.strip(), width)
    canvas.showPage()
    canvas.save()
    return destination


def spine_width_label(width):
    """Return a compact, filename-safe width label."""
    return f"{parse_spine_width(width):g}in"
