// HTML を Chromium で描く画像（cards・panels・showcase・stack）で共通に使う部品。
// - 書体: fontsource の CSS は url(./…) で書体のファイルを指す。そのまま setContent すると
//   読めず、パソコンにある別の書体で黙って描かれる。決まった住所に書き換え、その住所への
//   問い合わせを書体フォルダのファイルで返す。読めなかった書体があれば止める。
// - 改行: 日本語は BudouX で文節に区切り、文節の途中では折り返さない。
const fs = require('fs');
const path = require('path');

const HOST = 'https://fonts.profile.invalid/';

function fontCss(dir, keep = () => true) {
  return fs.readdirSync(dir).filter((f) => f.endsWith('.css') && keep(f))
    .map((f) => fs.readFileSync(path.join(dir, f), 'utf8').replace(/url\(\.\//g, `url(${HOST}`))
    .join('\n');
}

async function serveFonts(page, dir) {
  await page.route(`${HOST}**`, (route) => {
    const file = path.join(dir, path.basename(new URL(route.request().url()).pathname));
    if (!fs.existsSync(file)) return route.fulfill({ status: 404 });
    const type = file.endsWith('.woff2') ? 'font/woff2' : 'font/woff';
    return route.fulfill({ path: file, headers: { 'Content-Type': type, 'Access-Control-Allow-Origin': '*' } });
  });
}

async function fontsReady(page) {
  const failed = await page.evaluate(async () => {
    await document.fonts.ready;
    return [...document.fonts].filter((f) => f.status === 'error').map((f) => `${f.family} ${f.weight} ${f.style}`);
  });
  if (failed.length) throw new Error(`書体を読めなかった: ${[...new Set(failed)].join(', ')}`);
}

let parser;
function phrase(text) {
  if (!parser) parser = require('budoux').loadDefaultJapaneseParser();
  return parser.parse(text).join('<wbr>');
}

// 文節の区切り（<wbr>）と空白でだけ折り返す。
const PHRASE_CSS = 'word-break: keep-all; overflow-wrap: anywhere; text-wrap: pretty;';

module.exports = { fontCss, serveFonts, fontsReady, phrase, PHRASE_CSS };
