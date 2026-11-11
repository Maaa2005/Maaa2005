# 画像の作り直し方

プロフィールの画像（`assets/`）はここのスクリプトで作っています。どの画像も明るい画面用（`-light`）と暗い画面用（`-dark`）の2種類があり、README の `<picture>` が見る人の設定に合わせて出し分けます。文言を直したら作り直してください。

| 画像 | スクリプト | 中身 |
|---|---|---|
| `assets/hero-*.svg` | `build_hero.py` | 名前と一言、浮かぶ画面3枚。真ん中の Stellise は夜の画面から朝の画面へ切り替わる |
| `assets/showcase/*-*.svg` | `build_showcase.js` → `build_strips.py` | アプリの紹介帯。下地を描いてから、画面を重ねて動きを付ける |
| `assets/cards/*-*.png` | `build_cards.js` | OSSのカード。文言はファイル先頭の `CARDS` |
| `assets/sections/*-*.png`・`assets/panels/*-*.png` | `build_panels.js` | 段の見出し（番号・欧文・細い罫線）と「大事にしていること」の板 |
| `assets/stack-*.png` | `build_stack.js` | 使っている技術。ロゴは simple-icons |

- 画面写真は `tools/shots/`（Stellise と Voice Context の公開リポジトリにある画面写真を縮めた物）。
- 文字は図形にして埋め込んでいるので、見る人のパソコンに書体が無くても同じ見た目になる。
- 動きは「動きを減らす」設定の人には止まって見える。GIF も試したが、色が粗くなり重さが約24倍になったので使っていない。

## 用意する物

書体（Noto Sans JP・Inter。欧文と数字は Inter にそろえる）、simple-icons、playwright（Chromium 付き）、budoux を、版を固定して1か所に入れます。Python は fonttools・brotli・pillow を使います。

```sh
sh tools/setup_build.sh /tmp/build
python3 -m pip install fonttools brotli pillow
```

## 作る

```sh
NODE_PATH=/tmp/build/node_modules sh tools/build_all.sh /tmp/build/fonts /tmp/build python3
python3 tools/check_readme.py README.md
```

- 途中でできる部品は `tools/.build/` に置かれます（リポジトリには入れない）。
- 書体は `tools/render.js` が書体フォルダから直接渡します。読めない書体があると止まります（以前は黙ってパソコンの別の書体で描かれ、見出しの斜体や数字が意図と違う書体になっていた）。
- 日本語は BudouX で文節に区切り、文節の途中では折り返しません。
- `check_readme.py` は、画像の有無・明暗の組・代わりの文・学校名が入っていないこと・画像の重さ（明暗それぞれ 3MB まで）・動きを減らす設定への対応を見ます。

## 点検（CI）

`.github/workflows/check.yml` が変更依頼のたびに動きます。

- README と画像の点検（`check_readme.py`）
- 画像の作り直し: 上の手順を最初から回し、作り直した画像を成果物として残す

文言（Stellise の担当範囲・受賞名の表記など）は、提出済みの応募書類と同じ表記にそろえています。事実より大きく書かないこと。
