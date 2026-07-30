"""
make_ascii_svg.py — downsample the prepped photo to a character grid and
render it as an SVG that "types" itself in: each row fades in and slides
in slightly, staggered top to bottom. Plays once, then freezes (fill="freeze").
"""

from PIL import Image
from config import PATHS, ASCII_COLS, ASCII_ROWS, ASCII_RAMP

CHAR_W = 7.2
CHAR_H = 13.5
FONT_SIZE = 13
ROW_STAGGER = 0.045
ROW_DURATION = 0.35
FILL_COLOR = "#a8b4c2"

RAMP = ASCII_RAMP
RAMP_LEN = len(RAMP)


def image_to_ascii_rows(path, cols, rows):
    img = Image.open(path).convert("L").resize((cols, rows))
    pixels = list(img.getdata())
    ascii_rows = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]
            idx = int((255 - brightness) / 255 * (RAMP_LEN - 1))
            row_chars.append(RAMP[idx])
        ascii_rows.append("".join(row_chars))
    return ascii_rows


def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(ascii_rows, cols):
    width = cols * CHAR_W + 20
    height = len(ascii_rows) * CHAR_H + 20
    body = []

    for i, row in enumerate(ascii_rows):
        begin = round(i * ROW_STAGGER, 3)
        y = 10 + i * CHAR_H + FONT_SIZE
        text = escape_xml(row).replace(" ", "\u00a0")

        body.append(f"""
    <g opacity="0" transform="translate(-6,0)">
      <animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="{ROW_DURATION}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate"
                         from="-6,0" to="0,0" begin="{begin}s" dur="{ROW_DURATION}s" fill="freeze" />
      <text x="10" y="{y}" font-family="'SFMono-Regular','Consolas','Menlo',monospace"
            font-size="{FONT_SIZE}" fill="{FILL_COLOR}" xml:space="preserve">{text}</text>
    </g>""")

    svg = f"""<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#0d1117" />
  {"".join(body)}
</svg>"""
    return svg


if __name__ == "__main__":
    rows = image_to_ascii_rows(PATHS["source_prepped"], ASCII_COLS, ASCII_ROWS)
    svg = build_svg(rows, ASCII_COLS)
    with open(PATHS["ascii_svg"], "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {PATHS['ascii_svg']}")
