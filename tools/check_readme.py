"""README.md と画像を点検する。CI（.github/workflows/check.yml）と手元で使う。

見る物:
- 画像がすべてあり、どの <picture> も暗い画面用と明るい画面用の2枚がそろっている
- 画像に代わりの文（alt）がある
- 「最近の更新」の目印が1組ある
- 学校名が入っていない（7月に本人の判断で外した）
- 1回の表示で読む画像の重さが上限以下（明暗それぞれ）
- 動く SVG が「動きを減らす」設定で止まる
- 活動の表が --sample の作り物のままになっていない
使い方: python3 tools/check_readme.py [README.md]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_activity import sample_weeks  # noqa: E402

MAX_MB = 3.0
NG_WORDS = ["国際工科", "専門職大学", "NIT Nagoya", "International Institute of Technology"]
PICTURE = re.compile(r"<picture>(.*?)</picture>", re.S)
SOURCE = re.compile(r'<source media="\(prefers-color-scheme: dark\)" srcset="([^"]+)"\s*/?>')
IMG = re.compile(r"<img\b([^>]*)>")
ATTR = re.compile(r'(\w+)="([^"]*)"')


def local(src):
    return not re.match(r"^(https?:)?//", src)


def main():
    readme = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    root = os.path.dirname(os.path.abspath(readme))
    text = open(readme, encoding="utf-8").read()
    errors = []
    used = {"light": set(), "dark": set()}

    for m in IMG.finditer(text):
        attrs = dict(ATTR.findall(m.group(1)))
        if not attrs.get("alt", "").strip():
            errors.append(f"alt が無い: {attrs.get('src')}")
        src = attrs.get("src", "")
        if src and local(src) and not os.path.exists(os.path.join(root, src)):
            errors.append(f"画像が無い: {src}")

    pictures = PICTURE.findall(text)
    for body in pictures:
        dark = SOURCE.search(body)
        img = IMG.search(body)
        light = dict(ATTR.findall(img.group(1))).get("src", "") if img else ""
        if not dark or not light:
            errors.append(f"明暗の片方が無い: {body[:80]}")
            continue
        dark = dark.group(1)
        if not os.path.exists(os.path.join(root, dark)):
            errors.append(f"画像が無い: {dark}")
        if dark.replace("-dark.", "-light.") != light:
            errors.append(f"明暗の組が合わない: {dark} / {light}")
        used["dark"].add(dark)
        used["light"].add(light)

    if text.count("<!-- recent:start -->") != 1 or text.count("<!-- recent:end -->") != 1 \
            or text.index("<!-- recent:start -->") > text.index("<!-- recent:end -->"):
        errors.append("「最近の更新」の目印が1組になっていない")

    svgs = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(root, "assets")) for f in fs if f.endswith(".svg")]
    for path in [readme, *svgs]:
        body = open(path, encoding="utf-8").read()
        for word in NG_WORDS:
            if word in body:
                errors.append(f"学校名が入っている: {os.path.relpath(path, root)}（{word}）")
        if path.endswith(".svg") and "@keyframes" in body and "prefers-reduced-motion" not in body:
            errors.append(f"動きを減らす設定で止まらない: {os.path.relpath(path, root)}")

    _, sample_total = sample_weeks()
    for theme in ("light", "dark"):
        path = os.path.join(root, "assets", f"activity-{theme}.svg")
        if os.path.exists(path) and f">{sample_total:,}<" in open(path, encoding="utf-8").read():
            errors.append(f"活動の表が作り物（--sample）のまま: assets/activity-{theme}.svg")

    for theme, files in used.items():
        size = sum(os.path.getsize(os.path.join(root, f)) for f in files if os.path.exists(os.path.join(root, f)))
        print(f"{theme}: {len(files)} images, {size / 1048576:.2f} MB")
        if size > MAX_MB * 1048576:
            errors.append(f"{theme} の画像が重い: {size / 1048576:.2f} MB（上限 {MAX_MB} MB）")

    print(f"pictures: {len(pictures)}")
    for e in errors:
        print("NG:", e)
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
