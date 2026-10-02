"""Builds assets/hero-dark.svg and assets/hero-light.svg.

An animated banner: requests flow into a gateway, clean ones pass, hostile ones
are stopped at the shield. Pure CSS animation, honoured by GitHub's image proxy;
prefers-reduced-motion freezes it.
Run: python3 scripts/build_hero.py
"""

from pathlib import Path

W, H = 840, 260
GATE_X = 640
LANES = [96, 130, 164, 198]
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

THEMES = {
    "dark": {"bg1": "#0d1117", "bg2": "#131a2a", "border": "#30363d", "dots": "#30363d",
             "text": "#e6edf3", "muted": "#8b949e", "lane": "#3d444d",
             "g1": "#58a6ff", "g2": "#a371f7", "g3": "#3fb950",
             "ok": "#3fb950", "bad": "#f85149", "glow": "#1f6feb"},
    "light": {"bg1": "#ffffff", "bg2": "#f3f6fb", "border": "#d0d7de", "dots": "#d8dee4",
              "text": "#1f2328", "muted": "#59636e", "lane": "#c9d1d9",
              "g1": "#0969da", "g2": "#8250df", "g3": "#1a7f37",
              "ok": "#1a7f37", "bad": "#cf222e", "glow": "#54aeff"},
}

# (lane, delay seconds, hostile?)
PACKETS = [
    (0, 0.0, False), (1, 0.7, True), (2, 1.3, False), (3, 2.1, False),
    (0, 2.6, True), (2, 3.4, False), (1, 4.0, False), (3, 4.7, True),
    (0, 5.3, False), (3, 6.0, True), (1, 6.6, False), (3, 7.2, False),
]
CYCLE = 8


def css(t: dict) -> str:
    start, stop, end = 470, GATE_X - 18, W - 24
    return f"""
  .name {{ font: 700 44px {SANS}; letter-spacing: -1px; }}
  .sub  {{ font: 500 15px {SANS}; fill: {t['muted']}; }}
  .mono {{ font: 500 13px {MONO}; fill: {t['muted']}; }}
  .tag  {{ font: 600 10px {MONO}; letter-spacing: 1.4px; fill: {t['muted']}; }}
  .shine {{ animation: shine 6s ease-in-out infinite alternate; }}
  @keyframes shine {{ from {{ transform: translateX(-160px); }} to {{ transform: translateX(160px); }} }}
  .glow {{ animation: drift 9s ease-in-out infinite alternate; transform-origin: center; }}
  @keyframes drift {{ from {{ transform: translate(-60px, -10px) scale(1); }}
                      to   {{ transform: translate(80px, 20px) scale(1.25); }} }}
  .typed {{ animation: type 2.6s steps(18, end) 0.4s both; }}
  @keyframes type {{ from {{ width: 0; }} to {{ width: 146px; }} }}
  .caret {{ animation: blink 1s step-end infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .gate {{ animation: pulse 2.4s ease-in-out infinite; transform-origin: {GATE_X}px 147px; }}
  @keyframes pulse {{ 0%,100% {{ opacity: .75; transform: scale(1); }} 50% {{ opacity: 1; transform: scale(1.06); }} }}
  .ok, .bad {{ animation-duration: {CYCLE}s; animation-iteration-count: infinite;
              animation-timing-function: linear; animation-fill-mode: backwards; }}
  .ok  {{ animation-name: pass; }}
  .bad {{ animation-name: block; }}
  @keyframes pass  {{ 0% {{ transform: translateX({start}px); opacity: 0; }}
                      6% {{ opacity: 1; }}
                      40% {{ transform: translateX({end}px); opacity: 0; }}
                      100% {{ transform: translateX({end}px); opacity: 0; }} }}
  @keyframes block {{ 0% {{ transform: translateX({start}px); opacity: 0; }}
                      6% {{ opacity: 1; }}
                      22% {{ transform: translateX({stop}px); opacity: 1; r: 4px; }}
                      30% {{ transform: translateX({stop}px); opacity: 0; r: 11px; }}
                      100% {{ transform: translateX({stop}px); opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; }}
  }}"""


def build(name: str) -> str:
    t = THEMES[name]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="Nikita Velbovets — backend and API security, Go">',
        "<defs>",
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg1"]}"/>'
        f'<stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>',
        f'<radialGradient id="glow"><stop offset="0" stop-color="{t["glow"]}" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></radialGradient>',
        f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="48" y1="0" x2="420" y2="0">'
        f'<stop offset="0" stop-color="{t["g1"]}"/><stop offset=".55" stop-color="{t["g2"]}"/>'
        f'<stop offset="1" stop-color="{t["g3"]}"/></linearGradient>',
        f'<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="160" y2="0">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".45"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="shield" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["g1"]}"/>'
        f'<stop offset="1" stop-color="{t["g2"]}"/></linearGradient>',
        f'<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{t["dots"]}"/></pattern>',
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
        f'<clipPath id="nameclip"><text x="48" y="118" class="name">Nikita Velbovets</text></clipPath>',
        '<clipPath id="typeclip"><rect class="typed" x="48" y="190" width="146" height="24"/></clipPath>',
        f"<style>{css(t)}</style>",
        "</defs>",
        '<g clip-path="url(#card)">',
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)" opacity=".6"/>',
        f'<circle class="glow" cx="{GATE_X}" cy="140" r="220" fill="url(#glow)"/>',
        "</g>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{t["border"]}"/>',
        # left: identity
        '<text x="48" y="64" class="tag">KYIV · KYIV-MOHYLA ACADEMY</text>',
        '<text x="48" y="118" class="name" fill="url(#ink)">Nikita Velbovets</text>',
        '<g clip-path="url(#nameclip)"><rect class="shine" x="48" y="70" width="160" height="60" fill="url(#sheen)"/></g>',
        '<text x="48" y="150" class="sub">Backend &amp; API security · mostly Go</text>',
        '<g clip-path="url(#typeclip)">'
        f'<text x="48" y="207" class="mono"><tspan fill="{t["ok"]}">$</tspan> go run ./gateway</text></g>',
        f'<rect class="caret" x="196" y="195" width="8" height="15" fill="{t["muted"]}"/>',
    ]
    # right: traffic through the gate
    for y in LANES:
        out.append(f'<line x1="470" y1="{y}" x2="{W - 24}" y2="{y}" stroke="{t["lane"]}" '
                   f'stroke-dasharray="2 6" stroke-linecap="round"/>')
    for lane, delay, hostile in PACKETS:
        cls, color = ("bad", t["bad"]) if hostile else ("ok", t["ok"])
        # where the packet rests when animation is off; the CSS transform overrides it otherwise
        rest = GATE_X - 18 if hostile else 490 + (delay * 97) % 320
        out.append(f'<circle class="{cls}" cx="0" cy="{LANES[lane]}" r="4" fill="{color}" '
                   f'transform="translate({rest:.0f} 0)" style="animation-delay:{delay}s"/>')
    shield = (f"M{GATE_X} 118 l22 8 v18 c0 16 -10 26 -22 32 c-12 -6 -22 -16 -22 -32 v-18 z")
    out += [
        f'<line x1="{GATE_X}" y1="76" x2="{GATE_X}" y2="218" stroke="{t["g1"]}" stroke-opacity=".35" stroke-width="2"/>',
        f'<g class="gate"><path d="{shield}" fill="{t["bg1"]}" stroke="url(#shield)" stroke-width="2.5" '
        f'stroke-linejoin="round"/>'
        f'<path d="M{GATE_X - 8} 146 l6 6 l11 -12" fill="none" stroke="{t["ok"]}" stroke-width="2.5" '
        f'stroke-linecap="round" stroke-linejoin="round"/></g>',
        f'<text x="{GATE_X}" y="238" class="tag" text-anchor="middle">EVERY REQUEST, INSPECTED</text>',
        "</svg>",
    ]
    return "\n".join(out)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for theme in THEMES:
        (out / f"hero-{theme}.svg").write_text(build(theme))


if __name__ == "__main__":
    main()
