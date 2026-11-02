// 段の見出し（assets/sections/*-<明暗>.png）と、「大事にしていること」「歩み」の板
// （assets/panels/*-<明暗>.png）を作る。雑誌のように、番号・欧文の斜体・細い罫線で全体をそろえる。
// 使い方: node tools/build_panels.js <書体フォルダ> assets
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { fontCss: readFontCss, serveFonts, fontsReady, phrase, PHRASE_CSS } = require('./render');

const FONT_DIR = path.resolve(process.argv[2] || 'fonts');
const OUT = path.resolve(process.argv[3] || path.join(__dirname, '..', 'assets'));

const THEMES = {
  dark: { bg: '#161B22', border: '#30363D', fg: '#E6EDF3', body: '#C9D1D9', sub: '#8B949E', rule: '#30363D', accent: '#B4A7FF', dot: '#8B7CF6', soft: '#8B7CF61f' },
  light: { bg: '#FFFFFF', border: '#E4E1F0', fg: '#1C1A2B', body: '#3B3852', sub: '#6E6A86', rule: '#E4E1F0', accent: '#6D5BD0', dot: '#6D5BD0', soft: '#6D5BD014' },
};

// 段の見出し。番号は読む順番。
const SECTIONS = [
  { id: 'numbers', no: '01', en: 'Numbers', ja: '数字で見る', meta: '2026.11' },
  { id: 'apps', no: '02', en: 'Apps', ja: 'App Storeで公開中', meta: 'iOS · 2' },
  { id: 'oss', no: '03', en: 'On GitHub', ja: 'GitHubで公開中', meta: 'repos · 4' },
  { id: 'principles', no: '04', en: 'Principles', ja: '大事にしていること', meta: '' },
  { id: 'timeline', no: '05', en: 'Timeline', ja: '歩み', meta: '2025 — 2026' },
  { id: 'activity', no: '06', en: 'Activity', ja: '毎日の積み重ね', meta: 'daily' },
  { id: 'stack', no: '07', en: 'Stack', ja: '使っている技術', meta: '' },
];

// 文言は README と同じ。提出済みESの範囲から出さない。
const PRINCIPLES = [
  { en: 'Ship it', ja: '作って、届ける。', body: '企画から公開まで運びきる。Stellise は2名のチームで約4か月かけて App Store に出しました。' },
  { en: 'Measure the goal', ja: '動いたあとに、目的を測る。', body: 'テストが通っても終わりにしない。WCC では553件のテストが通ったあとに、AIへ渡す情報量が膨らんでいるのを見つけ、約87%減らしました。' },
  { en: 'Guard by design', ja: 'AIに任せる範囲は、仕組みで守る。', body: '購入や送信は実行前に止める（WCC）。交渉の最後は人が承認する（AUN Protocol）。' },
];

const TIMELINE = [
  { date: '2025.10', text: 'Tongali アイデアピッチコンテスト 準優秀賞' },
  { date: '2026.05', text: 'G検定・Google AI Professional Certificate' },
  { date: '2026.07', text: 'KASANE を npm で公開' },
  { date: '2026.09', text: '技育博2026 に Stellise を出展・Voice Context が App Store で公開' },
  { date: '2026.10', text: 'AUN Protocol の仕様を公開・WCC の比較計測（27回）を公開' },
];

const fontCss = () => readFontCss(FONT_DIR);

const page = (t, body, css) => `<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>${fontCss()}
  * { box-sizing: border-box; margin: 0; padding: 0; } html, body { background: transparent; }
  body { font-family: 'Inter', 'Noto Sans JP', sans-serif; color: ${t.fg}; -webkit-font-smoothing: antialiased; }
  .serif { font-family: 'Instrument Serif', 'Noto Serif JP', serif; font-style: italic; font-weight: 400; }
  .wrap { ${PHRASE_CSS} }
  ${css}</style></head><body>${body}</body></html>`;

function sectionHtml(s, t) {
  return page(t, `<div id="c" class="sec">
    <span class="no serif">(${s.no})</span><span class="en serif">${s.en}</span><span class="ja">${s.ja}</span>
    <span class="meta">${s.meta}</span>
  </div>`, `
  .sec { width: 880px; height: 62px; display: flex; align-items: baseline; gap: 12px; padding: 18px 4px 0; border-bottom: 1px solid ${t.rule}; position: relative; }
  .sec::after { content: ''; position: absolute; left: 0; bottom: -1px; width: 120px; height: 1px; background: ${t.accent}; }
  .no { font-size: 17px; color: ${t.accent}; }
  .en { font-size: 32px; line-height: 1; color: ${t.fg}; letter-spacing: -.3px; }
  .ja { font: 500 13px 'Inter', 'Noto Sans JP'; color: ${t.sub}; margin-left: 2px; }
  .meta { margin-left: auto; font: 400 11px 'JetBrains Mono', monospace; color: ${t.sub}; letter-spacing: .6px; }
  `);
}

function principlesHtml(t) {
  return page(t, `<div id="c" class="box">${PRINCIPLES.map((p, i) => `
    <div class="col"><div class="num serif">${['i.', 'ii.', 'iii.'][i]}</div><div class="en serif">${p.en}</div>
    <h3>${p.ja}</h3><p class="wrap">${phrase(p.body)}</p></div>`).join('')}</div>`, `
  .box { width: 880px; display: grid; grid-template-columns: repeat(3, 1fr); background: ${t.bg}; border: 1px solid ${t.border}; border-radius: 18px; overflow: hidden; }
  .col { padding: 24px 24px 26px; position: relative; }
  .col + .col { border-left: 1px solid ${t.rule}; }
  .num { font-size: 15px; color: ${t.accent}; }
  .en { font-size: 26px; line-height: 1.1; margin-top: 2px; color: ${t.fg}; }
  h3 { margin-top: 14px; font: 700 15px/1.5 'Inter', 'Noto Sans JP'; color: ${t.fg}; }
  p { margin-top: 8px; font: 400 12.5px/1.75 'Inter', 'Noto Sans JP'; color: ${t.body}; }
  `);
}

function timelineHtml(t) {
  return page(t, `<div id="c" class="box"><div class="line"></div>${TIMELINE.map((e, i) => `
    <div class="ev${i === TIMELINE.length - 1 ? ' now' : ''}"><div class="date">${e.date}</div><div class="dot"></div><p class="wrap">${phrase(e.text)}</p></div>`).join('')}</div>`, `
  .box { width: 880px; display: grid; grid-template-columns: repeat(${TIMELINE.length}, 1fr); background: ${t.bg}; border: 1px solid ${t.border}; border-radius: 18px; padding: 26px 18px 26px; position: relative; overflow: hidden; }
  .line { position: absolute; left: 40px; right: 40px; top: 63px; height: 1px; background: linear-gradient(90deg, ${t.rule}, ${t.accent}, ${t.rule}); }
  .ev { padding: 0 8px; position: relative; }
  .date { font: 500 12px 'JetBrains Mono', monospace; color: ${t.sub}; letter-spacing: .5px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; background: ${t.bg}; border: 2px solid ${t.dot}; margin: 12px 0 14px; position: relative; z-index: 1; }
  .now .dot { background: ${t.dot}; box-shadow: 0 0 0 5px ${t.soft}; }
  .now .date { color: ${t.accent}; }
  p { font: 500 12px/1.7 'Inter', 'Noto Sans JP'; color: ${t.body}; }
  `);
}

async function shot(p, html, out) {
  await p.setContent(html, { waitUntil: 'load' });
  await fontsReady(p);
  await (await p.$('#c')).screenshot({ path: out, omitBackground: true });
  console.log('wrote', out);
}

(async () => {
  fs.mkdirSync(path.join(OUT, 'sections'), { recursive: true });
  fs.mkdirSync(path.join(OUT, 'panels'), { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 940, height: 600 }, deviceScaleFactor: 2 });
  await serveFonts(p, FONT_DIR);
  for (const [name, t] of Object.entries(THEMES)) {
    for (const s of SECTIONS) await shot(p, sectionHtml(s, t), path.join(OUT, 'sections', `${s.id}-${name}.png`));
    await shot(p, principlesHtml(t), path.join(OUT, 'panels', `principles-${name}.png`));
    await shot(p, timelineHtml(t), path.join(OUT, 'panels', `timeline-${name}.png`));
  }
  await b.close();
})();
