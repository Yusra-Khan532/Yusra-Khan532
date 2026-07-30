"""
render_heatmap_svg.py — draw the classic 53-week x 7-day contribution grid
as rounded, colored boxes. Reveals once with a diagonal line-after-line
slide-down (CSS keyframes that play on load, then freeze - no looping
"glow"). Adds a Less->More legend and a stats footer.

Usage:
    python scripts/render_heatmap_svg.py
"""

import json
from config import PATHS, HEATMAP_PALETTE

BOX = 11
GAP = 3
CELL = BOX + GAP
COLS = 53
ROWS = 7
MARGIN_L = 20
MARGIN_T = 20
LEGEND_H = 26
FOOTER_H = 26
STAGGER = 0.012   # seconds per diagonal step (col + row)


def load_days():
    with open(PATHS["contributions_json"]) as f:
        data = json.load(f)
    return data


def to_grid(days, cols=COLS, rows=ROWS):
    """Map a flat, date-sorted day list onto a cols x rows grid,
    right-aligned so the most recent day lands in the last column."""
    grid = [[None] * rows for _ in range(cols)]
    total_cells = cols * rows
    padded = ([None] * (total_cells - len(days))) + days if len(days) < total_cells else days[-total_cells:]
    for i, day in enumerate(padded):
        col = i // rows
        row = i % rows
        if col < cols:
            grid[col][row] = day
    return grid


def build_svg(data) -> str:
    days = data["days"]
    stats = data["stats"]
    grid = to_grid(days)

    width = MARGIN_L * 2 + COLS * CELL
    height = MARGIN_T + ROWS * CELL + LEGEND_H + FOOTER_H

    boxes = []
    for col in range(COLS):
        for row in range(ROWS):
            day = grid[col][row]
            level = day["level"] if day else 0
            level = max(0, min(level, len(HEATMAP_PALETTE) - 1))
            color = HEATMAP_PALETTE[level]
            x = MARGIN_L + col * CELL
            y = MARGIN_T + row * CELL
            delay = round((col + row) * STAGGER, 3)
            title = f"{day['count']} contributions on {day['date']}" if day else ""
            boxes.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2" fill="{color}" style="animation-delay:{delay}s">'
                f'<title>{title}</title></rect>'
            )

    legend_y = MARGIN_T + ROWS * CELL + 16
    legend_x = width - MARGIN_L - (len(HEATMAP_PALETTE) * (BOX + 3)) - 40
    legend_boxes = []
    for i, color in enumerate(HEATMAP_PALETTE):
        lx = legend_x + 30 + i * (BOX + 3)
        legend_boxes.append(f'<rect x="{lx}" y="{legend_y-9}" width="{BOX}" height="{BOX}" rx="2" fill="{color}" />')

    total = stats.get("total_last_year", 0)
    footer_y = height - 8
    footer_text = f"{total:,} contributions in the last year  ·  current streak {stats.get('current_streak',0)}  ·  longest streak {stats.get('longest_streak',0)}"

    svg = f"""<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .box {{
      opacity: 0;
      transform: translateY(-6px);
      animation: reveal 0.35s ease-out forwards;
    }}
    @keyframes reveal {{
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .lbl {{ font-family: 'SFMono-Regular','Consolas','Menlo',monospace; font-size: 11px; fill: #8b949e; }}
  </style>
  <rect width="100%" height="100%" fill="#0d1117" />
  {"".join(boxes)}
  <text x="{legend_x}" y="{legend_y+4}" class="lbl">Less</text>
  {"".join(legend_boxes)}
  <text x="{legend_x + 30 + len(HEATMAP_PALETTE)*(BOX+3) + 6}" y="{legend_y+4}" class="lbl">More</text>
  <text x="{MARGIN_L}" y="{footer_y}" class="lbl">{footer_text}</text>
</svg>"""
    return svg


if __name__ == "__main__":
    data = load_days()
    svg = build_svg(data)
    with open(PATHS["heatmap_svg"], "w") as f:
        f.write(svg)
    print(f"Wrote {PATHS['heatmap_svg']}")
