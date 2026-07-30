"""
make_info_card.py — hand-authored neofetch-style SVG panel. Each row fades
and slides in on a short stagger so it looks like it's printing next to the
portrait. Set STATIC=1 to emit a frozen (already-visible) frame, useful for
local Quick Look previews.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py
"""

import os
from config import CARD_FIELDS, PATHS

STATIC = os.environ.get("STATIC") == "1"

WIDTH = 490
ROW_H = 34
TOP_PAD = 56
BOTTOM_PAD = 20
FONT = "'SFMono-Regular','Consolas','Menlo',monospace"

# key label -> accent color (like neofetch's colored fields)
ROWS = [
    ("user", "user", "#e6edf3", True),      # title-style, no label
    ("now", "now", "#39d353", False),
    ("prev", "prev", "#58a6ff", False),
    ("stack", "stack", "#f0883e", False),
    ("highlights", "highlights", "#d29922", False),
]

if CARD_FIELDS.get("now_playing"):
    ROWS.append(("now_playing", "playing", "#db61a2", False))


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    height = TOP_PAD + ROW_H * (len(ROWS) - 1) + BOTTOM_PAD + 10

    rows_svg = []
    for i, (field_key, label, color, is_title) in enumerate(ROWS):
        value = esc(CARD_FIELDS.get(field_key, ""))
        y = TOP_PAD + (i - 1) * ROW_H if not is_title else 40
        begin = round(i * 0.18, 2)

        if is_title:
            content = f'<text x="24" y="{y}" font-family="{FONT}" font-size="16" font-weight="bold" fill="{color}">{value}</text>' \
                       f'<line x1="24" y1="{y+10}" x2="{WIDTH-24}" y2="{y+10}" stroke="#30363d" stroke-width="1"/>'
        else:
            content = (
                f'<text x="24" y="{y}" font-family="{FONT}" font-size="13.5" font-weight="bold" fill="{color}">{label}</text>'
                f'<text x="130" y="{y}" font-family="{FONT}" font-size="13.5" fill="#c9d1d9">{value}</text>'
            )

        if STATIC:
            rows_svg.append(f'<g opacity="1">{content}</g>')
        else:
            rows_svg.append(f'''
    <g opacity="0" transform="translate(-8,0)">
      <animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="0.4s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate"
                         from="-8,0" to="0,0" begin="{begin}s" dur="0.4s"
                         fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1" />
      {content}
    </g>''')

    svg = f"""<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" rx="8" fill="#0d1117" stroke="#30363d" />
  {"".join(rows_svg)}
</svg>"""
    return svg


if __name__ == "__main__":
    svg = build_svg()
    with open(PATHS["info_card_svg"], "w") as f:
        f.write(svg)
    print(f"Wrote {PATHS['info_card_svg']}" + (" (static frame)" if STATIC else ""))
