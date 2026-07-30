"""
fetch_contributions.py — pull the public contribution calendar HTML fragment
GitHub itself uses (no GraphQL API, no personal access token needed) and
turn it into data/contributions.json with raw days + derived stats
(current streak, longest streak, best day, monthly totals).

Usage:
    python scripts/fetch_contributions.py

Note: this depends on GitHub's public HTML markup for the calendar fragment.
If GitHub changes that markup, the attribute names below (`data-date`,
`data-level`, tooltip text) may need small tweaks — the parsing is written
defensively with a couple of fallbacks for that reason.
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import GITHUB_USERNAME, PATHS

URL = f"https://github.com/users/{GITHUB_USERNAME}/contributions"
HEADERS = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}


def fetch_html(username: str) -> str:
    resp = requests.get(f"https://github.com/users/{username}/contributions", headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("td[data-date], [data-date]")

    days = []
    for cell in cells:
        date_str = cell.get("data-date")
        if not date_str:
            continue

        level = cell.get("data-level")
        count = None

        # Prefer an explicit contribution count if GitHub embeds one
        # (older markup used a tool-tip element with text like
        # "5 contributions on Jan 3rd").
        tooltip_text = cell.get("aria-label") or cell.get("title") or ""
        m = re.search(r"([\d,]+)\s+contribution", tooltip_text)
        if m:
            count = int(m.group(1).replace(",", ""))

        if level is None:
            # crude fallback: bucket by count if we have one, else 0
            if count is None:
                level = 0
            elif count == 0:
                level = 0
            elif count <= 2:
                level = 1
            elif count <= 5:
                level = 2
            elif count <= 9:
                level = 3
            else:
                level = 4
        else:
            level = int(level)

        days.append({"date": date_str, "level": level, "count": count if count is not None else level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    # streaks (consecutive days with count > 0), based on calendar order
    longest = current = 0
    running = 0
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak = trailing run ending today (or most recent day present)
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = defaultdict(int)
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] += d["count"]

    return {
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main():
    try:
        html = fetch_html(GITHUB_USERNAME)
    except requests.RequestException as e:
        print(f"Failed to fetch contributions for {GITHUB_USERNAME}: {e}", file=sys.stderr)
        sys.exit(1)

    days = parse_days(html)
    if not days:
        print("Warning: no day cells parsed — GitHub's markup may have changed.", file=sys.stderr)

    stats = compute_stats(days)
    out = {"username": GITHUB_USERNAME, "days": days, "stats": stats}

    with open(PATHS["contributions_json"], "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {PATHS['contributions_json']} ({len(days)} days, {stats['total_last_year']} contributions)")


if __name__ == "__main__":
    main()
