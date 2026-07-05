#!/usr/bin/env python3
"""Build a clean PDF slide deck for the World Cup 2022 network project."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
OUTPUT = ROOT / "presentation" / "world_cup_2022_network_presentation.pdf"

SLIDE_SIZE = (13.333, 7.5)
SLIDE_W_IN, SLIDE_H_IN = SLIDE_SIZE

BG = "#f5f7fb"
INK = "#172033"
MUTED = "#5b6577"
BLUE = "#245c8c"
RED = "#8f3f2f"
ORANGE = "#b45f06"
GREEN = "#2f6f73"
PURPLE = "#6f4aa8"
LINE = "#cfd7e4"
WHITE = "#ffffff"

CONTENT_LEFT = 0.06
CONTENT_RIGHT = 0.94
HEADER_RULE_Y = 0.805
FOOTER_Y = 0.055


# --------------------------------------------------------------------------
# Low-level text layout helpers
#
# All text on a slide is placed using axis-fraction coordinates (0-1), but
# font sizes are in points. These helpers convert between the two so that
# text can be wrapped to a target width *in inches* and stacked vertically
# *in inches* without guessing magic-number gaps that later overlap.
# --------------------------------------------------------------------------

def line_height_frac(fontsize: float, linespacing: float = 1.3) -> float:
    """Height of one text line, as a fraction of the slide height."""
    return (fontsize * linespacing) / 72.0 / SLIDE_H_IN


def chars_per_line(max_width: float, fontsize: float, factor: float = 0.52) -> int:
    """Rough max character count that fits in `max_width` (axis fraction)."""
    width_in = max_width * SLIDE_W_IN
    char_width_in = fontsize * factor / 72.0
    return max(8, int(width_in / char_width_in))


def draw_wrapped(
    ax: plt.Axes,
    text: str,
    x: float,
    y: float,
    *,
    max_width: float,
    fontsize: float,
    color: str = INK,
    fontweight: str | None = None,
    ha: str = "left",
    linespacing: float = 1.28,
) -> int:
    """Draw top-anchored, word-wrapped text. Returns the number of lines used."""
    width = chars_per_line(max_width, fontsize)
    lines: list[str] = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=width) or [""])
    ax.text(
        x,
        y,
        "\n".join(lines),
        fontsize=fontsize,
        color=color,
        fontweight=fontweight,
        ha=ha,
        va="top",
        linespacing=linespacing,
    )
    return len(lines)


def add_bullets(
    ax: plt.Axes,
    items: list[str],
    x: float,
    y: float,
    *,
    color: str = BLUE,
    size: float = 15.0,
    max_width: float = 0.30,
    row_gap: float = 0.028,
    linespacing: float = 1.25,
) -> float:
    """Draw a bulleted list, wrapping each item and stacking rows without
    overlap regardless of how many lines an item wraps to. Returns the
    y-coordinate just below the last line drawn."""
    lh = line_height_frac(size, linespacing)
    marker_dy = lh * 0.38
    cur_y = y
    for item in items:
        n_lines = draw_wrapped(
            ax,
            item,
            x + 0.026,
            cur_y,
            max_width=max_width,
            fontsize=size,
            color=INK,
            linespacing=linespacing,
        )
        ax.scatter([x], [cur_y - marker_dy], s=34, color=color, zorder=3)
        cur_y -= n_lines * lh + row_gap
    return cur_y


# --------------------------------------------------------------------------
# Slide scaffolding
# --------------------------------------------------------------------------

def new_slide() -> tuple[plt.Figure, plt.Axes]:
    fig = plt.figure(figsize=SLIDE_SIZE, facecolor=BG)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def add_header(ax: plt.Axes, heading: str, subtitle: str | None = None) -> None:
    draw_wrapped(
        ax, heading, CONTENT_LEFT, 0.93,
        max_width=CONTENT_RIGHT - CONTENT_LEFT, fontsize=25, color=INK,
        fontweight="bold", linespacing=1.15,
    )
    if subtitle:
        draw_wrapped(
            ax, subtitle, CONTENT_LEFT, 0.855,
            max_width=CONTENT_RIGHT - CONTENT_LEFT, fontsize=12.5, color=MUTED,
            linespacing=1.2,
        )
    ax.plot([CONTENT_LEFT, CONTENT_RIGHT], [HEADER_RULE_Y, HEADER_RULE_Y], color=LINE, linewidth=1.1)


def add_footer(ax: plt.Axes, slide_no: int) -> None:
    ax.text(CONTENT_LEFT, FOOTER_Y, "Network Science Project | FIFA World Cup 2022", fontsize=8.5, color=MUTED)
    ax.text(CONTENT_RIGHT, FOOTER_Y, str(slide_no), fontsize=8.5, color=MUTED, ha="right")


def add_image(fig: plt.Figure, path: Path, box: tuple[float, float, float, float]) -> None:
    image = mpimg.imread(path)
    ax_img = fig.add_axes(box, facecolor=WHITE)
    ax_img.imshow(image)
    ax_img.set_xticks([])
    ax_img.set_yticks([])
    for spine in ax_img.spines.values():
        spine.set_visible(False)


def tournament_context(pdf: PdfPages, slide_no: int) -> None:
    fig, ax = new_slide()
    add_header(ax, "Tournament Context", "Knockout bracket and final path")
    add_image(fig, FIGURES / "context.png", (0.20, 0.10, 0.60, 0.68))
    add_footer(ax, slide_no)
    save(fig, pdf)


def outcome_pagerank(pdf: PdfPages, slide_no: int) -> None:
    fig, ax = new_slide()
    add_header(ax, "Outcome PageRank", "Ranking success through opponent importance")
    add_image(fig, FIGURES / "top_outcome_pagerank.png", (0.07, 0.15, 0.60, 0.58))

    side_x = 0.72
    ax.text(side_x, 0.72, "Key points", fontsize=13.5, color=MUTED, fontweight="bold")
    add_bullets(
        ax,
        [
            "Argentina #1",
            "France #2",
            "Upsets gain structural value",
        ],
        side_x,
        0.64,
        color=BLUE,
        size=13.8,
        max_width=CONTENT_RIGHT - side_x,
        row_gap=0.035,
    )
    add_footer(ax, slide_no)
    save(fig, pdf)


def pagerank_upset_context(pdf: PdfPages, slide_no: int) -> None:
    fig, ax = new_slide()
    add_header(ax, "PageRank Upset Context", "Why Tunisia and Saudi Arabia appear unusually high")
    add_image(fig, FIGURES / "arg_arab.png", (0.10, 0.53, 0.80, 0.145))
    add_image(fig, FIGURES / "tun_fra.png", (0.10, 0.34, 0.80, 0.145))
    add_bullets(
        ax,
        [
            "Saudi Arabia receives result support from Argentina.",
            "Tunisia receives result support from France.",
            "Because Argentina and France are important nodes, these upset links carry extra PageRank value.",
        ],
        0.12,
        0.235,
        color=BLUE,
        size=12.6,
        max_width=0.76,
        row_gap=0.018,
    )
    add_footer(ax, slide_no)
    save(fig, pdf)


def add_figure_slide(
    pdf: PdfPages,
    slide_no: int,
    heading: str,
    subtitle: str,
    figure: str,
    bullets: list[str],
    color: str,
    image_box: tuple[float, float, float, float] = (0.07, 0.15, 0.60, 0.58),
) -> None:
    fig, ax = new_slide()
    add_header(ax, heading, subtitle)
    add_image(fig, FIGURES / figure, image_box)

    bullets_x = 0.72
    bullets_max_width = CONTENT_RIGHT - bullets_x
    ax.text(bullets_x, 0.72, "Key points", fontsize=13.5, color=MUTED, fontweight="bold")
    add_bullets(
        ax, bullets, bullets_x, 0.64,
        color=color, size=13.8, max_width=bullets_max_width, row_gap=0.035,
    )
    add_footer(ax, slide_no)
    save(fig, pdf)


def save(fig: plt.Figure, pdf: PdfPages) -> None:
    pdf.savefig(fig, facecolor=fig.get_facecolor())
    plt.close(fig)


# --------------------------------------------------------------------------
# Individual slides
# --------------------------------------------------------------------------

def cover(pdf: PdfPages) -> None:
    fig, ax = new_slide()
    ax.set_facecolor("#10263d")
    fig.set_facecolor("#10263d")
    ax.text(0.07, 0.72, "Network-Based Analysis", fontsize=35, color=WHITE, fontweight="bold")
    ax.text(0.07, 0.62, "FIFA World Cup 2022", fontsize=34, color="#d7edf9", fontweight="bold")
    ax.text(
        0.07,
        0.48,
        "Teams as nodes. Results, performance and style as edges.",
        fontsize=17,
        color="#dfeaf3",
    )
    ax.text(0.07, 0.30, "Rui Coelho | Tiago Figueiredo", fontsize=15, color="#c4d0dc")
    ax.text(0.07, 0.245, "Network Science Project", fontsize=12.5, color="#c4d0dc")
    ax.plot([0.07, 0.58], [0.18, 0.18], color="#4d7190", linewidth=2)
    add_footer(ax, 1)
    save(fig, pdf)


def research_focus(pdf: PdfPages) -> None:
    fig, ax = new_slide()
    add_header(ax, "Research Focus", "One tournament, multiple network interpretations")

    divider_x = 0.63
    bullets_max_width = divider_x - 0.08 - 0.05  # keep clear of the divider line
    add_bullets(
        ax,
        [
            "Can network rankings reproduce competitive hierarchy?",
            "Which teams dominated statistically?",
            "Which teams were efficient, disruptive, or stylistically similar?",
        ],
        0.08,
        0.66,
        size=16.5,
        max_width=bullets_max_width,
        row_gap=0.045,
    )

    stat_x = (divider_x + CONTENT_RIGHT) / 2
    ax.text(stat_x, 0.62, "64", fontsize=55, color=BLUE, fontweight="bold", ha="center")
    ax.text(stat_x, 0.545, "matches", fontsize=14, color=MUTED, ha="center")
    ax.text(stat_x, 0.42, "32", fontsize=55, color=BLUE, fontweight="bold", ha="center")
    ax.text(stat_x, 0.345, "teams", fontsize=14, color=MUTED, ha="center")
    ax.plot([divider_x, divider_x], [0.27, 0.70], color=LINE, linewidth=1.3)
    add_footer(ax, 2)
    save(fig, pdf)


def pipeline(pdf: PdfPages) -> None:
    fig, ax = new_slide()
    add_header(ax, "Analysis Pipeline", "From match table to generated network outputs")
    steps = [
        ("Raw CSV", "match results\nand statistics"),
        ("Clean data", "numeric fields\nteam-match table"),
        ("Build networks", "six edge\nsemantics"),
        ("Compute metrics", "PageRank\nstrength\ncommunities"),
        ("Generate figures", "rankings\nnetwork views"),
    ]
    xs = [0.11, 0.30, 0.49, 0.68, 0.87]
    y = 0.52
    ax.plot([xs[0], xs[-1]], [y, y], color=LINE, linewidth=2)
    for i, ((label, desc), x) in enumerate(zip(steps, xs), start=1):
        ax.scatter([x], [y], s=1450, color=BLUE, zorder=3)
        ax.text(x, y, str(i), fontsize=12, color=WHITE, fontweight="bold", ha="center", va="center", zorder=4)
        ax.text(x, y - 0.10, label, fontsize=13.5, color=INK, fontweight="bold", ha="center", va="top")
        ax.text(x, y - 0.155, desc, fontsize=10.6, color=MUTED, ha="center", va="top", linespacing=1.4)
    add_footer(ax, 3)
    save(fig, pdf)


def network_construction(pdf: PdfPages) -> None:
    fig, ax = new_slide()
    add_header(ax, "Network Construction", "Same teams, different edge meanings")
    rows = [
        ("Signed match", "team1 -> team2, weight = goal difference", BLUE),
        ("Outcome", "loser -> winner; draws are reciprocal", BLUE),
        ("Statistical dominance", "stronger standardized match profile -> opponent", RED),
        ("Offensive efficiency", "better conversion ratios -> opponent", ORANGE),
        ("Pressure / recovery", "more defensive pressure and forced turnovers -> opponent", GREEN),
        ("Style similarity", "teams linked by similar average profiles", PURPLE),
    ]

    name_x, desc_x = 0.12, 0.37
    name_w = desc_x - name_x - 0.02
    desc_w = CONTENT_RIGHT - desc_x
    fs_name, fs_desc = 14.0, 12.6
    linespacing = 1.25
    lh_name = line_height_frac(fs_name, linespacing)
    lh_desc = line_height_frac(fs_desc, linespacing)

    y = 0.735
    row_gap = 0.022
    for name, desc, color in rows:
        n_name = draw_wrapped(
            ax, name, name_x, y, max_width=name_w, fontsize=fs_name,
            color=INK, fontweight="bold", linespacing=linespacing,
        )
        n_desc = draw_wrapped(
            ax, desc, desc_x, y, max_width=desc_w, fontsize=fs_desc,
            color=MUTED, linespacing=linespacing,
        )
        marker_y = y - lh_name * 0.35
        ax.scatter([0.085], [marker_y], s=54, color=color, zorder=3)

        lines_used = max(n_name, n_desc, 1)
        y -= lines_used * max(lh_name, lh_desc) + row_gap

    add_footer(ax, 4)
    save(fig, pdf)


def conclusion(pdf: PdfPages, slide_no: int) -> None:
    fig, ax = new_slide()
    add_header(ax, "Main Takeaway", "Changing the edge definition changes the football story")
    draw_wrapped(
        ax, "Results, dominance, efficiency, pressure and style",
        0.09, 0.64, max_width=0.82, fontsize=26, color=INK, fontweight="bold", linespacing=1.2,
    )
    draw_wrapped(
        ax, "are related, but not equivalent.",
        0.09, 0.535, max_width=0.82, fontsize=25, color=BLUE, fontweight="bold", linespacing=1.2,
    )
    add_bullets(
        ax,
        [
            "Outcome PageRank captures opponent-sensitive success.",
            "Performance networks separate control, conversion and disruption.",
            "Style similarity groups teams by how they played.",
        ],
        0.10,
        0.36,
        size=16.5,
        max_width=0.82,
        row_gap=0.04,
    )
    add_footer(ax, slide_no)
    save(fig, pdf)


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUTPUT) as pdf:
        cover(pdf)
        research_focus(pdf)
        pipeline(pdf)
        network_construction(pdf)
        tournament_context(pdf, 5)
        outcome_pagerank(pdf, 6)
        pagerank_upset_context(pdf, 7)
        add_figure_slide(
            pdf,
            8,
            "Statistical Dominance",
            "Match control is not the same as the points table",
            "points_vs_statistical_dominance.png",
            ["Argentina leads", "Brazil, Spain, England high", "Dominance tracks control"],
            RED,
        )
        add_figure_slide(
            pdf,
            9,
            "Offensive Efficiency",
            "Conversion over volume",
            "top_offensive_efficiency.png",
            ["Netherlands #1", "England and France high", "Rewards finishing efficiency"],
            ORANGE,
        )
        add_figure_slide(
            pdf,
            10,
            "Pressure / Recovery",
            "Defensive disruption and regain actions",
            "top_pressure_recovery.png",
            ["Morocco #1", "Japan #2", "Different from possession dominance"],
            GREEN,
        )
        add_figure_slide(
            pdf,
            11,
            "Efficiency vs Pressure",
            "Two distinct performance profiles",
            "efficiency_vs_pressure_recovery.png",
            ["Efficiency aligns with goals", "Pressure identifies disruption", "Morocco/Japan stand out"],
            GREEN,
            image_box=(0.07, 0.15, 0.56, 0.58),
        )
        add_figure_slide(
            pdf,
            12,
            "Style Similarity Network",
            "Teams linked by similar average match profiles",
            "style_similarity_network.png",
            ["Cosine similarity", "4 nearest neighbours", "Label propagation communities"],
            PURPLE,
            image_box=(0.08, 0.13, 0.58, 0.62),
        )
        add_figure_slide(
            pdf,
            13,
            "Performance Heatmap",
            "Standardized team profiles",
            "team_performance_heatmap.png",
            ["Spain: possession/passes", "Brazil/Germany: shot volume", "Morocco/Japan: pressure"],
            RED,
            image_box=(0.10, 0.13, 0.54, 0.62),
        )
        conclusion(pdf, 14)

    print(OUTPUT)


if __name__ == "__main__":
    build()
