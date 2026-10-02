"""Builds assets/stack-dark.svg and assets/stack-light.svg.

Icons are fetched from skillicons.dev once and inlined, because GitHub serves
README images through a proxy that does not load external resources inside SVG.
Run: python3 scripts/build_stack.py
"""

import re
import urllib.request
from pathlib import Path

GROUPS = [
    ("LANGUAGES", ["go", "python", "c", "bash"]),
    ("DATA", ["postgres", "redis"]),
    ("INFRASTRUCTURE", ["docker", "kubernetes", "nginx", "linux", "githubactions", "git"]),
    ("WEB", ["django", "electron", "html", "css", "js"]),
]

NAMES = {
    "go": "Go", "python": "Python", "c": "C", "bash": "Bash",
    "postgres": "PostgreSQL", "redis": "Redis", "docker": "Docker",
    "kubernetes": "Kubernetes", "nginx": "nginx", "linux": "Linux",
    "githubactions": "GitHub Actions", "git": "Git", "django": "Django",
    "electron": "Electron", "html": "HTML", "css": "CSS", "js": "JavaScript",
}

THEMES = {
    "dark": {"icons": "dark", "panel": "#161b22", "border": "#30363d",
             "label": "#8b949e", "rule": "#21262d"},
    "light": {"icons": "light", "panel": "#f6f8fa", "border": "#d0d7de",
              "label": "#57606a", "rule": "#eaeef2"},
}

ICON, GAP, ROW_GAP, PAD_X, PAD_Y, LABEL_W = 40, 10, 22, 28, 26, 170
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def fetch_icon(name: str, theme: str) -> str:
    url = f"https://skillicons.dev/icons?i={name}&theme={theme}"
    req = urllib.request.Request(url, headers={"User-Agent": "profile-builder"})
    with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310 - fixed https host
        body = resp.read().decode()
    inner = re.search(r"<g[^>]*>\s*(<svg.*</svg>)\s*</g>", body, re.S)
    if not inner:
        raise ValueError(f"unexpected skillicons response for {name}")
    return inner.group(1)


def build(theme_name: str) -> str:
    t = THEMES[theme_name]
    widest = max(len(icons) for _, icons in GROUPS)
    width = PAD_X * 2 + LABEL_W + widest * ICON + (widest - 1) * GAP
    height = PAD_Y * 2 + len(GROUPS) * ICON + (len(GROUPS) - 1) * ROW_GAP

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none" role="img" aria-label="Tech stack">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" '
        f'fill="{t["panel"]}" stroke="{t["border"]}"/>',
    ]
    for row, (label, icons) in enumerate(GROUPS):
        y = PAD_Y + row * (ICON + ROW_GAP)
        if row:
            rule_y = y - ROW_GAP / 2
            parts.append(f'<line x1="{PAD_X}" y1="{rule_y}" x2="{width - PAD_X}" y2="{rule_y}" '
                         f'stroke="{t["rule"]}"/>')
        parts.append(f'<text x="{PAD_X}" y="{y + ICON / 2 + 4}" fill="{t["label"]}" '
                     f'font-family="{FONT}" font-size="11.5" font-weight="600" '
                     f'letter-spacing="1.6">{label}</text>')
        for col, name in enumerate(icons):
            x = PAD_X + LABEL_W + col * (ICON + GAP)
            icon = fetch_icon(name, t["icons"])
            icon = icon.replace('width="256" height="256"', f'width="{ICON}" height="{ICON}"', 1)
            parts.append(f'<g transform="translate({x} {y})"><title>{NAMES[name]}</title>{icon}</g>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for theme in THEMES:
        (out / f"stack-{theme}.svg").write_text(build(theme))


if __name__ == "__main__":
    main()
