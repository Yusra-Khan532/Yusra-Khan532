#!/usr/bin/env python3
"""Generate light and dark SVG contribution heatmaps from GitHub GraphQL data."""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets"
USERNAME = os.environ.get("GITHUB_USERNAME", "Yusra-Khan532")
TOKEN = os.environ.get("GITHUB_TOKEN")
TODAY = dt.date.today()
TO_DATE = TODAY
FROM_DATE = TODAY - dt.timedelta(days=364)


def fetch_contributions() -> tuple[dict[dt.date, int], int]:
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN is required; refusing to generate without authenticated data")

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }
    """
    payload = json.dumps({
        "query": query,
        "variables": {
            "login": USERNAME,
            "from": f"{FROM_DATE.isoformat()}T00:00:00Z",
            "to": f"{TO_DATE.isoformat()}T23:59:59Z",
        },
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "Yusra-Khan532-profile-heatmap",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get("errors"):
        raise SystemExit(f"GitHub GraphQL error: {result['errors']}")
    calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    counts = {
        dt.date.fromisoformat(day["date"]): int(day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    }
    return counts, int(calendar["totalContributions"])


def fetch_public_levels() -> tuple[dict[dt.date, int], None]:
    """Fetch GitHub's public calendar levels for the initial checked-in image."""
    levels: dict[dt.date, int] = {}
    for year in range(FROM_DATE.year, TO_DATE.year + 1):
        url = f"https://github.com/users/{USERNAME}/contributions?from={year}-01-01&to={year}-12-31"
        request = urllib.request.Request(url, headers={"User-Agent": "Yusra-Khan532-profile-heatmap"})
        with urllib.request.urlopen(request, timeout=30) as response:
            markup = response.read().decode("utf-8")
        for date_text, level_text in re.findall(
            r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d+)"', markup
        ):
            day = dt.date.fromisoformat(date_text)
            if FROM_DATE <= day <= TO_DATE:
                # Preserve GitHub's real visual level without inventing a total.
                levels[day] = (0, 1, 2, 4, 8)[min(int(level_text), 4)]
    if not levels:
        raise SystemExit("GitHub public contribution calendar returned no cells")
    return levels, None


def level(count: int) -> int:
    if count <= 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    if count <= 7:
        return 3
    return 4


def svg_for(counts: dict[dt.date, int], total: int | None, dark: bool) -> str:
    colors = ["#17233b", "#164e63", "#0e7490", "#14b8a6", "#5eead4"] if dark else [
        "#e8eef7", "#b9e8e2", "#5ccfc1", "#0d9488", "#075e63"
    ]
    background = "#0b1426" if dark else "#f8fbff"
    text = "#e6edf7" if dark else "#0b1426"
    muted = "#8ea3c4" if dark else "#52637d"
    start = FROM_DATE - dt.timedelta(days=(FROM_DATE.weekday() + 1) % 7)
    end = TO_DATE + dt.timedelta(days=(6 - ((TO_DATE.weekday() + 1) % 7)))
    weeks = ((end - start).days + 1) // 7
    cell = 12
    gap = 4
    left = 64
    top = 78
    step = cell + gap
    width = 1000
    height = 300
    total_label = f"{total} contributions" if total is not None else "contribution levels from GitHub"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="GitHub Activity heatmap for {html.escape(USERNAME)}">',
        f'<rect width="100%" height="100%" rx="18" fill="{background}"/>',
        f'<text x="48" y="42" fill="{text}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="24" font-weight="700">GitHub Activity</text>',
        f'<text x="48" y="63" fill="{muted}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13">{html.escape(USERNAME)} · last 12 months · {total_label}</text>',
    ]
    month_seen: set[tuple[int, int]] = set()
    for column in range(weeks):
        week_start = start + dt.timedelta(days=column * 7)
        for offset in range(7):
            day = week_start + dt.timedelta(days=offset)
            if day < FROM_DATE or day > TO_DATE:
                continue
            if day.day <= 7 and (day.year, day.month) not in month_seen:
                month_seen.add((day.year, day.month))
                parts.append(
                    f'<text x="{left + column * step}" y="94" fill="{muted}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">{day.strftime("%b")}</text>'
                )
            count = counts.get(day, 0)
            x = left + column * step
            y = top + offset * step
            title = html.escape(f"{count} contribution{'s' if count != 1 else ''} on {day.isoformat()}")
            delay = min((column * 7 + offset) * 0.006, 1.5)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{colors[level(count)]}" opacity="0">'
                f'<title>{title}</title><animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.28s" fill="freeze"/></rect>'
            )
    parts.extend([
        f'<text x="{left}" y="{top + 7 * step + 22}" fill="{muted}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">Less</text>',
        *[
            f'<rect x="{left + 34 + i * 18}" y="{top + 7 * step + 12}" width="12" height="12" rx="3" fill="{color}"/>'
            for i, color in enumerate(colors)
        ],
        f'<text x="{left + 34 + len(colors) * 18 + 8}" y="{top + 7 * step + 22}" fill="{muted}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">More</text>',
        "</svg>",
    ])
    return "".join(parts)


def main() -> None:
    counts, total = fetch_public_levels() if "--public" in sys.argv else fetch_contributions()
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "activity-dark.svg").write_text(svg_for(counts, total, True), encoding="utf-8")
    (OUTPUT / "activity-light.svg").write_text(svg_for(counts, total, False), encoding="utf-8")


if __name__ == "__main__":
    main()
