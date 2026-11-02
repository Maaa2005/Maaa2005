#!/bin/sh
# 画像を作り直すのに要る物を <置き場> に入れる（書体・simple-icons・playwright と Chromium・budoux）。
# 使い方: sh tools/setup_build.sh <置き場>
# 書体は <置き場>/fonts、node_modules は <置き場>/node_modules にできる。版は固定して、誰が作っても同じ見た目にする。
set -eu
DIR=$1
mkdir -p "$DIR"
cd "$DIR"
[ -f package.json ] || echo '{"name":"profile-build","private":true}' > package.json
npm install --no-audit --no-fund --silent playwright@1.49.1 budoux@0.6.4 simple-icons@13.21.0 \
  @fontsource/noto-sans-jp@5.3.1 @fontsource/inter@5.3.0 @fontsource/jetbrains-mono@5.3.0 @fontsource/instrument-serif@5.3.0
npx playwright install chromium
mkdir -p fonts
cp node_modules/@fontsource/*/files/*.woff2 fonts/
for d in noto-sans-jp:noto-jp inter:inter jetbrains-mono:mono instrument-serif:serif; do
  src=${d%%:*}
  name=${d##*:}
  for c in node_modules/@fontsource/"$src"/[0-9]*.css; do
    sed 's#url(./files/#url(./#g' "$c" > "fonts/$name-$(basename "$c")"
  done
done
echo "ready: $DIR/fonts, $DIR/node_modules"
