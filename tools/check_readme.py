"""README.md と画像を点検する。CI（.github/workflows/check.yml）と手元で使う。

見る物:
- 画像がすべてあり、明るい画面用と暗い画面用が組になっている
  （<picture> は使わない。見る人のブラウザの設定に従うので、GitHub だけ暗くしている人には
  暗いページに明るい画像が出る。2026-10-22 に本人の画面で起きた。GitHub のテーマに従う
  #gh-light-mode-only / #gh-dark-mode-only の付いたリンクで包む）
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


MAX_MB = 3.0
NG_WORDS = ["国際工科", "専門職大学", "NIT Nagoya", "International Institute of Technology"]
MODE = re.compile(r'<a href="(?P<href>[^"]+)#gh-(?P<mode>light|dark)-mode-only"><img\b(?P<img>[^>]*)></a>')
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

    if "<picture" in text:
        errors.append("<picture> を使っている（GitHub のテーマに従わない）。#gh-light-mode-only / #gh-dark-mode-only の組にする")
    modes = [(m["mode"], m["href"], dict(ATTR.findall(m["img"])).get("src", "")) for m in MODE.finditer(text)]
    pairs = 0
    for i in range(0, len(modes), 2):
        light, dark = modes[i], modes[i + 1] if i + 1 < len(modes) else ("", "", "")
        if light[0] != "light" or dark[0] != "dark":
            errors.append(f"明るい画面用と暗い画面用が順に並んでいない: {light[2]}")
            break
        if light[2].replace("-light.", "-dark.") != dark[2] or "-light." not in light[2]:
            errors.append(f"明暗の組が合わない: {light[2]} / {dark[2]}")
        if light[1] != dark[1] and (light[1], dark[1]) != (light[2], dark[2]):
            errors.append(f"明暗でリンク先が違う: {light[1]} / {dark[1]}")
        if not os.path.exists(os.path.join(root, dark[2])):
            errors.append(f"画像が無い: {dark[2]}")
        used["light"].add(light[2])
        used["dark"].add(dark[2])
        pairs += 1


    svgs = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(root, "assets")) for f in fs if f.endswith(".svg")]
    for path in [readme, *svgs]:
        body = open(path, encoding="utf-8").read()
        for word in NG_WORDS:
            if word in body:
                errors.append(f"学校名が入っている: {os.path.relpath(path, root)}（{word}）")
        if path.endswith(".svg") and "@keyframes" in body and "prefers-reduced-motion" not in body:
            errors.append(f"動きを減らす設定で止まらない: {os.path.relpath(path, root)}")


    for theme, files in used.items():
        size = sum(os.path.getsize(os.path.join(root, f)) for f in files if os.path.exists(os.path.join(root, f)))
        print(f"{theme}: {len(files)} images, {size / 1048576:.2f} MB")
        if size > MAX_MB * 1048576:
            errors.append(f"{theme} の画像が重い: {size / 1048576:.2f} MB（上限 {MAX_MB} MB）")

    print(f"pairs: {pairs}")
    for e in errors:
        print("NG:", e)
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
