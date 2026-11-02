#!/bin/sh
# プロフィールの画像をすべて作り直す。
# 使い方: sh tools/build_all.sh <書体フォルダ> <simple-icons を入れたフォルダ> [python]
set -eu
FONT_DIR=$1
ICON_PKG=$2
PY=${3:-python3}
cd "$(dirname "$0")/.."
node tools/build_showcase.js "$FONT_DIR" tools/.build
node tools/build_cards.js "$FONT_DIR" assets
node tools/build_panels.js "$FONT_DIR" assets
NODE_PATH=$(npm root -g) node tools/build_stack.js "$FONT_DIR" assets "$ICON_PKG"
"$PY" tools/build_hero.py "$FONT_DIR" assets tools/.build
"$PY" tools/build_strips.py assets tools/.build
