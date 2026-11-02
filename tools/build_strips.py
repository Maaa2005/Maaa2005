"""アプリの紹介帯 assets/showcase/<id>-<theme>.svg を作る。

build_showcase.js が作った下地（説明文の入った帯）に、iPhone の画面を3枚重ねて、ゆっくり浮かせる。
2枚指定した画面は、時間をずらして切り替わる。動きを減らす設定の人には止まって見える。
使い方: python tools/build_strips.py assets tools/.build
"""
import base64
import io
import os
import sys

from PIL import Image

ASSETS = sys.argv[1] if len(sys.argv) > 1 else "assets"
BUILD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), ".build")
W, H = 880, 300

# 画面の並び（左から）。リストに2枚あれば切り替える。
STRIPS = {
    "stellise": [["stellise-rain"], ["stellise-tasks", "stellise-clear"], ["stellise-sleep"]],
    "voice-context": [["vc-timeline"], ["vc-detail", "vc-recorder"], ["vc-disclosure"]],
}
# 枠つき画面の画像（194x384 相当）を置く位置。build_showcase.js の帯の右側に合わせる。
SLOTS = [(384, 16), (552, 42), (720, 68)]


def webp_uri(path, width=None, quality=88):
    im = Image.open(path).convert("RGBA")
    if width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def build(sid, theme):
    base = webp_uri(os.path.join(BUILD, f"{sid}-base-{theme}.png"), quality=92)
    phones = []
    for i, (names, (x, y)) in enumerate(zip(STRIPS[sid], SLOTS)):
        layers = []
        for j, n in enumerate(names):
            uri = webp_uri(os.path.join(BUILD, "phones", f"{n}.png"), width=388)
            cls = ' class="swap"' if j else ""
            layers.append(f'<image{cls} href="{uri}" x="{x}" y="{y}" width="194" height="384"/>')
        phones.append(f'<g class="float" style="animation-delay:-{i * 1.6:.1f}s">{"".join(layers)}</g>')
    frame = "#30363D" if theme == "dark" else "#E4E1F0"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">
  <style>
    .float {{ animation: float 7s ease-in-out infinite; }}
    .swap {{ animation: swap 8s ease-in-out infinite; }}
    @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}
    @keyframes swap {{ 0%,40% {{ opacity: 0; }} 50%,90% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .float, .swap {{ animation: none; }} }}
  </style>
  <defs><clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
  <g clip-path="url(#c)">
    <image href="{base}" width="{W}" height="{H}"/>
    {"".join(phones)}
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{frame}"/>
</svg>
'''


def main():
    os.makedirs(os.path.join(ASSETS, "showcase"), exist_ok=True)
    for sid in STRIPS:
        for theme in ("dark", "light"):
            out = os.path.join(ASSETS, "showcase", f"{sid}-{theme}.svg")
            svg = build(sid, theme)
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(svg)
            print(f"wrote {out} ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
