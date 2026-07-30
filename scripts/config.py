"""
Central config for the profile-art pipeline.
Edit GITHUB_USERNAME (and optionally NOW_PLAYING) then run the scripts in order:

    python scripts/prep_photo.py source-photo.jpg
    python scripts/make_ascii_svg.py
    python scripts/make_info_card.py
    python scripts/fetch_contributions.py
    python scripts/render_heatmap_svg.py
"""

import os

GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "Yusra-Khan532")

CARD_FIELDS = {
    "user":       f"{GITHUB_USERNAME}@github",
    "now":        "Software Engineer, Data Analyst",
    "prev":       "Previous role / school",
    "stack":      "MERN, Python",
    "highlights":  "Shipped X, built Y, spoke at Z",
    "now_playing": "",
}

ASCII_COLS = 100
ASCII_ROWS = 53
ASCII_RAMP = " .`:-=+*cs#%@"

HEATMAP_PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

PATHS = {
    "source_prepped": "source-prepped.png",
    "ascii_svg": "avi-ascii.svg",
    "info_card_svg": "info-card.svg",
    "contributions_json": "data/contributions.json",
    "heatmap_svg": "contrib-heatmap.svg",
}
