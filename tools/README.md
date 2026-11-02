# 画像の作り直し方

プロフィールの画像（`assets/`）はここのスクリプトで作っています。文言を直したら作り直してください。

| 画像 | スクリプト | 中身 |
|---|---|---|
| `assets/header.svg` | `build_header.py` | 名前と一言。文字は図形にして埋め込むので、見る人の書体に左右されない |
| `assets/cards/*.png`・`assets/stats.png` | `build_cards.js` | 作品カードと数字の帯。文言はファイル先頭の `CARDS`・`STATS` |
| README の「最近の更新」 | `update_recent.py` | `.github/workflows/recent.yml` が毎朝動かす |

## 書体を用意する

npm から書体を取って、1つのフォルダ（下の `fonts/`）に `*.woff2` と `@font-face` の CSS を集めます。

```sh
mkdir -p /tmp/f && cd /tmp/f
npm pack @fontsource/noto-sans-jp @fontsource/inter @fontsource/jetbrains-mono
for t in *.tgz; do mkdir -p "${t%.tgz}" && tar -xzf "$t" -C "${t%.tgz}"; done
mkdir -p fonts && cp */package/files/*.woff2 fonts/
for d in fontsource-noto-sans-jp-*:noto-jp fontsource-inter-*:inter fontsource-jetbrains-mono-*:mono; do
  src=${d%%:*}; name=${d##*:}
  for c in $src/package/[0-9]*.css; do sed 's#url(./files/#url(./#g' "$c" > "fonts/$name-$(basename "$c")"; done
done
```

## 作る

```sh
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install fonttools brotli
/tmp/venv/bin/python tools/build_header.py /tmp/f/fonts assets/header.svg
node tools/build_cards.js /tmp/f/fonts assets   # playwright が要る
```

文言（Stellise の担当範囲・受賞名の表記など）は、提出済みの応募書類と同じ表記にそろえています。事実より大きく書かないこと。
