"""
prep_photo.py — turn a normal photo into a high-contrast, background-free
grayscale image that converts cleanly to ASCII.

Usage:
    python scripts/prep_photo.py source-photo.jpg
"""

import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove

from config import PATHS


def prep(src_path: str, out_path: str = PATHS["source_prepped"]):
    # 1. Remove background -> RGBA with transparent bg
    with open(src_path, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)

    with open("_tmp_nobg.png", "wb") as f:
        f.write(output_bytes)

    rgba = Image.open("_tmp_nobg.png").convert("RGBA")

    # 2. Composite onto pure white so background maps to blank end of ramp
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("L")

    # 3. Boost local contrast with CLAHE so a flat face gets real
    #    highlights/shadows instead of converting to a dark blob.
    gray_np = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray_np)

    Image.fromarray(contrasted).save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <photo.jpg>")
        sys.exit(1)
    prep(sys.argv[1])
