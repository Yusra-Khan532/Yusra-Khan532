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

# --- REQUIRED: change this ---
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "your-github-username")

# --- neofetch card content: edit freely ---
CARD_FIELDS = {
    "user":       f"{GITHUB_USERNAME}@github",
    "now":        "Software Engineer",
    "prev":       "Previous role / school",
    "stack":      "Python, TypeScript, Rust",
    "highlights":  "Shipped X, built Y, spoke at Z",
    # Optional: shown as its own row in the card. Not real audio -
    # GitHub strips <audio>/<video>/autoplay, this is just a text/status line.
    "now_playing": "Now Playing: (edit me, or leave blank to omit)",
}

# --- visual tuning ---
ASCII_COLS = 100
ASCII_ROWS = 53
ASCII_RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)

HEATMAP_PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

PATHS = {
    "source_prepped": "source-prepped.png",
    "ascii_svg": "avi-ascii.svg",
    "info_card_svg": "info-card.svg",
    "contributions_json": "data/contributions.json",
    "heatmap_svg": "contrib-heatmap.svg",
}
