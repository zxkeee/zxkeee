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
    "dark": {"icons": "dark", "label": "#8b949e", "name": "#6e7681", "rule": "#30363d", "glint": "#58a6ff"},
    "light": {"icons": "light", "label": "#57606a", "name": "#6e7781", "rule": "#d8dee4", "glint": "#0969da"},
}

# Drawn at 840 wide and scaled by the README to fill its column.
WIDTH, LABEL_W, ICON, NAME_GAP, ROW_GAP, PAD_Y = 840, 170, 40, 18, 30, 8
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
STYLE = """
  .r { stroke-dasharray: 840; animation: draw 1.1s cubic-bezier(.4,0,.2,1) backwards; }
  @keyframes draw { from { stroke-dashoffset: 840; } }
  .l { animation: fade .6s ease-out backwards; }
  .i { animation: rise .6s cubic-bezier(.2,.8,.2,1) backwards; }
  @keyframes fade { from { opacity: 0; } }
  @keyframes rise { from { opacity: 0; transform: translateY(6px); } }
  .g { stroke-dasharray: 140 2000; stroke-dashoffset: 140; stroke-linecap: round;
       animation: glint 7s cubic-bezier(.45,0,.55,1) infinite; }
  @keyframes glint { 0% { stroke-dashoffset: 140; opacity: 0; } 8% { opacity: .9; }
                     55% { stroke-dashoffset: -840; opacity: .9; } 60%, 100% { stroke-dashoffset: -840; opacity: 0; } }
  @media (prefers-reduced-motion: reduce) { .r, .l, .i, .g { animation: none; } .g { display: none; } }
"""


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
    slot = (WIDTH - LABEL_W) / widest
    row_h = ICON + NAME_GAP
    height = PAD_Y * 2 + 6 + len(GROUPS) * row_h + (len(GROUPS) - 1) * ROW_GAP

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" fill="none" role="img" aria-label="Tech stack">',
        f"<style>{STYLE}</style>",
    ]
    for row, (label, icons) in enumerate(GROUPS):
        y = PAD_Y + row * (row_h + ROW_GAP)
        delay = row * 0.15
        if row:
            rule_y = y - ROW_GAP / 2
            parts.append(f'<line class="r" style="animation-delay:{delay:.2f}s" x1="0" y1="{rule_y}" '
                         f'x2="{WIDTH}" y2="{rule_y}" stroke="{t["rule"]}"/>')
            parts.append(f'<line class="g" style="animation-delay:{1.4 + row * 0.9:.2f}s" x1="0" y1="{rule_y}" '
                         f'x2="{WIDTH}" y2="{rule_y}" stroke="{t["glint"]}"/>')
        parts.append(f'<text class="l" style="animation-delay:{delay:.2f}s" x="0" y="{y + ICON / 2 + 4}" '
                     f'fill="{t["label"]}" font-family="{FONT}" font-size="11.5" font-weight="600" '
                     f'letter-spacing="1.8">{label}</text>')
        for col, name in enumerate(icons):
            cx = LABEL_W + slot * col + slot / 2
            icon = fetch_icon(name, t["icons"])
            icon = icon.replace('width="256" height="256"', f'width="{ICON}" height="{ICON}"', 1)
            parts.append(
                f'<g class="i" style="animation-delay:{delay + 0.2 + col * 0.06:.2f}s">'
                f'<title>{NAMES[name]}</title>'
                f'<g transform="translate({cx - ICON / 2:.1f} {y})">{icon}</g>'
                f'<text x="{cx:.1f}" y="{y + row_h + 2}" text-anchor="middle" fill="{t["name"]}" '
                f'font-family="{FONT}" font-size="11">{NAMES[name]}</text></g>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for theme in THEMES:
        (out / f"stack-{theme}.svg").write_text(build(theme))


if __name__ == "__main__":
    main()
