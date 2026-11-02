"""見出し画像 assets/hero-dark.svg・assets/hero-light.svg を作る。

実際の画面（Voice Context と Stellise）が浮かび、真ん中の Stellise は夜の画面から朝の画面へ
ゆっくり切り替わる。先に build_showcase.js で tools/.build/phones/*.png を作っておくこと。
文字は build_header.py と同じく図形にして埋め込む。動きを減らす設定の人には止まって見える。
使い方: python tools/build_hero.py <書体フォルダ> assets tools/.build
"""
import base64
import io
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from build_header import text_path  # noqa: E402

ASSETS = sys.argv[2] if len(sys.argv) > 2 else "assets"
BUILD = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), ".build")
W, H = 900, 440

THEMES = {
    "dark": dict(
        bg=("#1B1B3A", "#0E0E1E", "#0A0A14"), lav=".55", pink=".28", star="#E6E1FF", starmax=.8,
        label="#B4A7FF", name=("#FFFFFF", "#D9D2FF"), tag="#E6E1FF", sub="#A8A3C7", chips="#8C87AD",
        frame="#ffffff1f", edge=".7",
    ),
    "light": dict(
        bg=("#F4F1FF", "#FAF9FF", "#FFFFFF"), lav=".42", pink=".16", star="#7B6CE0", starmax=.45,
        label="#6D5BD0", name=("#1C1A2B", "#4B3FA0"), tag="#2A2547", sub="#5B5873", chips="#7A7694",
        frame="#00000014", edge=".55",
    ),
}


def phone_uri(name, width=360):
    im = Image.open(os.path.join(BUILD, "phones", f"{name}.png")).convert("RGBA")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=88, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode(), im.size


def build(theme, t, texts, phones_svg):
    label, name, tag1, tag2, sub, chips = texts
    rnd = random.Random(1206)
    stars = []
    for _ in range(46):
        sx, sy = rnd.uniform(10, W - 10), rnd.uniform(10, H - 10)
        stars.append(
            f'<circle class="tw" cx="{sx:.0f}" cy="{sy:.0f}" r="{rnd.uniform(0.5, 1.4):.2f}" '
            f'style="animation-delay:-{rnd.uniform(0, 6):.1f}s;opacity:{rnd.uniform(.2, t["starmax"]):.2f}"/>'
        )
    b0, b1, b2 = t["bg"]
    n0, n1 = t["name"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="中村 奨志 — AIを、日常に自然に溶け込ませる。iOSアプリと、AIエージェントの道具を作っています。画面は Voice Context と Stellise。">
  <style>
    .float {{ animation: float 7s ease-in-out infinite; }}
    .tw {{ fill: {t["star"]}; animation: tw 5.5s ease-in-out infinite; }}
    .morning {{ animation: morning 9s ease-in-out infinite; }}
    @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
    @keyframes tw {{ 0%,100% {{ opacity: .9; }} 50% {{ opacity: .15; }} }}
    @keyframes morning {{ 0%,35% {{ opacity: 0; }} 50%,85% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .float, .tw, .morning {{ animation: none; }} }}
  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{b0}"/><stop offset=".6" stop-color="{b1}"/><stop offset="1" stop-color="{b2}"/>
    </linearGradient>
    <radialGradient id="lav" cx="690" cy="210" r="330" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#8B7CF6" stop-opacity="{t["lav"]}"/>
      <stop offset=".55" stop-color="#6D5BD0" stop-opacity=".14"/>
      <stop offset="1" stop-color="#6D5BD0" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="pink" cx="860" cy="430" r="260" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#DB61A2" stop-opacity="{t["pink"]}"/><stop offset="1" stop-color="#DB61A2" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="name" x1="48" y1="0" x2="360" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{n0}"/><stop offset="1" stop-color="{n1}"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#8B7CF6" stop-opacity="0"/><stop offset=".5" stop-color="#8B7CF6" stop-opacity="{t["edge"]}"/><stop offset="1" stop-color="#8B7CF6" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="panel"><rect width="{W}" height="{H}" rx="20"/></clipPath>
  </defs>
  <g clip-path="url(#panel)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#lav)"/>
    <rect width="{W}" height="{H}" fill="url(#pink)"/>
    <g>{''.join(stars)}</g>
    {phones_svg}
    <rect width="{W}" height="1.5" fill="url(#edge)"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{t["frame"]}"/>
  <path fill="{t["label"]}" d="{label}"/>
  <path fill="url(#name)" d="{name}"/>
  <path fill="{t["tag"]}" d="{tag1}"/>
  <path fill="{t["tag"]}" d="{tag2}"/>
  <path fill="{t["sub"]}" d="{sub}"/>
  <path fill="{t["chips"]}" d="{chips}"/>
</svg>
'''


def main():
    jp700 = "noto-sans-jp-*-700-normal.woff2"
    jp500 = "noto-sans-jp-*-500-normal.woff2"
    jp400 = "noto-sans-jp-*-400-normal.woff2"
    mono = "jetbrains-mono-latin-500-normal.woff2"
    texts = (
        text_path("MASASHI NAKAMURA  /  CLASS OF 2028", mono, 12.5, 52, 118, tracking=1.6)[0],
        text_path("中村 奨志", jp700, 64, 48, 196, tracking=2)[0],
        text_path("AIを、日常に", jp500, 25, 52, 252, tracking=0.6)[0],
        text_path("自然に溶け込ませる。", jp500, 25, 52, 290, tracking=0.6)[0],
        text_path("iOSアプリと、AIエージェントの道具を作っています。", jp400, 13.5, 52, 332, tracking=0.4)[0],
        text_path("iOS  ·  AI agents  ·  MCP  ·  local LLMs", mono, 12.5, 52, 372, tracking=0.6)[0],
    )

    def place(names, x, y, rot, scale, delay):
        """names の1枚目を常に表示し、2枚目があれば重ねてゆっくり切り替える。"""
        layers = []
        for i, n in enumerate(names):
            uri, (pw, ph) = phone_uri(n)
            w = 194 * scale
            h = w * ph / pw
            cls = ' class="morning"' if i else ""
            layers.append(f'<image{cls} href="{uri}" x="{x}" y="{y}" width="{w:.1f}" height="{h:.1f}"/>')
        cx, cy = x + w / 2, y + h / 2
        return (f'<g class="float" style="animation-delay:-{delay}s"><g transform="rotate({rot} {cx:.0f} {cy:.0f})">'
                + "".join(layers) + "</g></g>")

    phones_svg = "".join([
        place(["vc-timeline"], 482, 96, -9, 0.9, 1.2),
        place(["stellise-tasks"], 716, 96, 9, 0.9, 2.4),
        place(["stellise-night", "stellise-clear"], 592, 46, 0, 1.06, 0.0),
    ])
    for theme, t in THEMES.items():
        out = os.path.join(ASSETS, f"hero-{theme}.svg")
        svg = build(theme, t, texts, phones_svg)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"wrote {out} ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
