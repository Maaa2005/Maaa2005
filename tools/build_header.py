"""見出し画像 assets/header.svg を作る。

文字はすべて図形（パス）に変換して埋め込むので、見る人の環境に書体が無くても同じ見た目になる。
使い方: tools/README.md を参照。
"""
import glob
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FONT_DIR", "fonts")
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/header.svg"

_cache = {}


def fonts(pattern):
    if pattern not in _cache:
        files = sorted(glob.glob(os.path.join(FONT_DIR, pattern)))
        if not files:
            raise SystemExit(f"font not found: {pattern} in {FONT_DIR}")
        _cache[pattern] = [TTFont(f) for f in files]
    return _cache[pattern]


def text_path(text, pattern, size, x, y, tracking=0.0):
    """text を (x, y) を基準線にしたパス文字列にして、右端の x を返す。"""
    out = []
    cur = x
    for ch in text:
        for f in fonts(pattern):
            cmap = f.getBestCmap()
            if ord(ch) in cmap:
                break
        else:
            raise SystemExit(f"glyph missing: {ch!r} ({pattern})")
        upem = f["head"].unitsPerEm
        scale = size / upem
        gname = cmap[ord(ch)]
        gs = f.getGlyphSet()
        pen = SVGPathPen(gs)
        gs[gname].draw(TransformPen(pen, (scale, 0, 0, -scale, cur, y)))
        d = pen.getCommands()
        if d:
            out.append(d)
        cur += f["hmtx"][gname][0] * scale + tracking
    return " ".join(out), cur - tracking


def main():
    jp700 = "noto-sans-jp-*-700-normal.woff2"
    jp500 = "noto-sans-jp-*-500-normal.woff2"
    mono = "jetbrains-mono-latin-500-normal.woff2"

    label, _ = text_path("MASASHI NAKAMURA  /  CLASS OF 2028", mono, 13, 56, 64, tracking=1.6)
    name, name_end = text_path("中村 奨志", jp700, 62, 52, 138, tracking=2)
    tagline, _ = text_path("AIを、日常に自然に溶け込ませる。", jp500, 22, 56, 184, tracking=0.6)
    chips, _ = text_path("iOS  ·  AI agents  ·  MCP  ·  local LLMs", mono, 13, 56, 222, tracking=0.6)

    # 星座（Stellise の星にちなむ）。座標は右側に置く。
    stars = [(616, 92, 2.4), (684, 58, 2.0), (744, 104, 3.6), (814, 72, 2.2),
             (858, 128, 2.0), (790, 166, 2.6), (700, 186, 2.0)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (2, 5), (5, 6)]
    lines = []
    for i, (a, b) in enumerate(edges):
        x1, y1, _ = stars[a]
        x2, y2, _ = stars[b]
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        lines.append(
            f'<line class="ln" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'style="stroke-dasharray:{length:.1f};stroke-dashoffset:{length:.1f};animation-delay:{0.25 + i * 0.22:.2f}s"/>'
        )
    # 背景の小さな星（毎回同じ配置になるよう乱数の種を固定）
    import random
    rnd = random.Random(2028)
    field = []
    while len(field) < 34:
        fx, fy = rnd.uniform(430, 890), rnd.uniform(14, 246)
        if any(abs(fx - sx) < 14 and abs(fy - sy) < 14 for sx, sy, _ in stars):
            continue
        field.append(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="{rnd.uniform(.5, 1.1):.2f}" fill="#8B949E" opacity="{rnd.uniform(.18, .5):.2f}"/>')
    dots = []
    for i, (cx, cy, r) in enumerate(stars):
        cls = "st big" if r > 3 else "st"
        dots.append(f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}" style="animation-delay:{i * 0.7:.1f}s"/>')
    # 一番大きい星には十字の光
    bx, by, _ = stars[2]
    sparkle = (f'<path class="spark" d="M{bx} {by-13} L{bx+2.2} {by-2.2} L{bx+13} {by} L{bx+2.2} {by+2.2} '
               f'L{bx} {by+13} L{bx-2.2} {by+2.2} L{bx-13} {by} L{bx-2.2} {by-2.2} Z"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 260" width="900" height="260" role="img" aria-label="中村 奨志 — AIを、日常に自然に溶け込ませる。 iOS, AI agents, MCP, local LLMs">
  <style>
    .label {{ fill: #7C8CFF; }}
    .name {{ fill: #E6EDF3; }}
    .tag {{ fill: #C9D1D9; }}
    .chips {{ fill: #8B949E; }}
    .ln {{ stroke: #5A6380; stroke-width: 1; fill: none; animation: draw 1.1s ease-out forwards; }}
    .st {{ fill: #C9D1D9; animation: tw 5.2s ease-in-out infinite; }}
    .big {{ fill: #E6EDF3; }}
    .spark {{ fill: #E6EDF3; opacity: .9; transform-origin: {bx}px {by}px; animation: pulse 5.2s ease-in-out infinite; }}
    .shoot {{ stroke: url(#tail); stroke-width: 1.4; stroke-linecap: round; opacity: 0; animation: shoot 9s ease-in 2.5s infinite; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    @keyframes tw {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
    @keyframes pulse {{ 0%,100% {{ transform: scale(1); opacity: .9; }} 50% {{ transform: scale(.72); opacity: .55; }} }}
    @keyframes shoot {{ 0% {{ opacity: 0; transform: translate(0,0); }} 3% {{ opacity: .9; }} 9% {{ opacity: 0; transform: translate(-150px,60px); }} 100% {{ opacity: 0; transform: translate(-150px,60px); }} }}
    @media (prefers-reduced-motion: reduce) {{
      .ln {{ animation: none; stroke-dashoffset: 0 !important; }}
      .st, .spark, .shoot {{ animation: none; }}
    }}
  </style>
  <defs>
    <radialGradient id="glow" cx="760" cy="110" r="300" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#7C8CFF" stop-opacity=".20"/>
      <stop offset="1" stop-color="#7C8CFF" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="900" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#7C8CFF" stop-opacity="0"/>
      <stop offset=".5" stop-color="#7C8CFF" stop-opacity=".55"/>
      <stop offset="1" stop-color="#7C8CFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="tail" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#E6EDF3" stop-opacity="1"/>
      <stop offset="1" stop-color="#E6EDF3" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="panel"><rect x="0" y="0" width="900" height="260" rx="18"/></clipPath>
  </defs>
  <rect x="0.5" y="0.5" width="899" height="259" rx="18" fill="#161B22" stroke="#30363D"/>
  <g clip-path="url(#panel)">
    <rect x="0" y="0" width="900" height="260" fill="url(#glow)"/>
    <rect x="0" y="0" width="900" height="1.5" fill="url(#edge)"/>
    <line class="shoot" x1="880" y1="30" x2="940" y2="6"/>
  </g>
  <path class="label" d="{label}"/>
  <path class="name" d="{name}"/>
  <path class="tag" d="{tagline}"/>
  <path class="chips" d="{chips}"/>
  <g>{''.join(field)}</g>
  <g>{''.join(lines)}</g>
  <g>{''.join(dots)}{sparkle}</g>
</svg>
'''
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {OUT} ({len(svg)//1024} KB), name ends at x={name_end:.0f}")


if __name__ == "__main__":
    main()
