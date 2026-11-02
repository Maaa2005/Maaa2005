# 画像の作り直し方

プロフィールの画像（`assets/`）はここのスクリプトで作っています。どの画像も明るい画面用（`-light`）と暗い画面用（`-dark`）の2種類があり、README の `<picture>` が見る人の設定に合わせて出し分けます。文言を直したら作り直してください。

| 画像 | スクリプト | 中身 |
|---|---|---|
| `assets/hero-*.svg` | `build_hero.py` | 名前と一言、浮かぶ画面3枚。真ん中の Stellise は夜の画面から朝の画面へ切り替わる |
| `assets/showcase/*-*.svg` | `build_showcase.js` → `build_strips.py` | アプリの紹介帯。下地を描いてから、画面を重ねて動きを付ける |
| `assets/cards/*-*.png`・`assets/stats-*.png` | `build_cards.js` | OSSのカードと数字の帯。文言はファイル先頭の `CARDS`・`STATS` |
| `assets/stack-*.png` | `build_stack.js` | 使っている技術。ロゴは simple-icons |
| README の「最近の更新」 | `update_recent.py` | `.github/workflows/recent.yml` が毎朝動かす |

- 画面写真は `tools/shots/`（Stellise と Voice Context の公開リポジトリにある画面写真を縮めた物）。
- 文字は図形にして埋め込んでいるので、見る人のパソコンに書体が無くても同じ見た目になる。
- 動きは「動きを減らす」設定の人には止まって見える。GIF も試したが、色が粗くなり重さが約24倍になったので使っていない。

## 用意する物

書体と simple-icons を npm から取ります。

```sh
mkdir -p /tmp/f && cd /tmp/f
npm pack @fontsource/noto-sans-jp @fontsource/inter @fontsource/jetbrains-mono
for t in *.tgz; do mkdir -p "${t%.tgz}" && tar -xzf "$t" -C "${t%.tgz}"; done
mkdir -p fonts && cp */package/files/*.woff2 fonts/
for d in fontsource-noto-sans-jp-*:noto-jp fontsource-inter-*:inter fontsource-jetbrains-mono-*:mono; do
  src=${d%%:*}; name=${d##*:}
  for c in $src/package/[0-9]*.css; do sed 's#url(./files/#url(./#g' "$c" > "fonts/$name-$(basename "$c")"; done
done
mkdir -p /tmp/icons && cd /tmp/icons && npm init -y >/dev/null && npm install simple-icons@13.21.0
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install fonttools brotli pillow
```

playwright（Chromium 付き）も要ります。

## 作る

```sh
sh tools/build_all.sh /tmp/f/fonts /tmp/icons /tmp/venv/bin/python
```

途中でできる部品は `tools/.build/` に置かれます（リポジトリには入れない）。

文言（Stellise の担当範囲・受賞名の表記など）は、提出済みの応募書類と同じ表記にそろえています。事実より大きく書かないこと。
