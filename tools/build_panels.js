// 段の見出し（assets/sections/*-<明暗>.png）と、「大事にしていること」「歩み」の板
// （assets/panels/*-<明暗>.png）を作る。雑誌のように、番号・欧文・細い罫線で全体をそろえる。
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
  { id: 'apps', no: '01', en: 'Apps', ja: 'App Storeで公開中', meta: 'iOS · 2' },
  { id: 'oss', no: '02', en: 'On GitHub', ja: 'GitHubで公開中', meta: 'Repos · 4' },
  { id: 'principles', no: '03', en: 'Principles', ja: '大事にしていること', meta: '' },
  { id: 'stack', no: '04', en: 'Stack', ja: '使っている技術', meta: '' },
];

// 文言は README と同じ。提出済みESの範囲から出さない。
const PRINCIPLES = [
  { en: 'Doubt the default', ja: '固定概念を疑う。', body: '子どもの頃からゲームで多様な世界観に触れてきました。当たり前を疑い、広く見てから決めます。' },
  { en: 'Enjoy the change', ja: '変化を楽しむ。', body: '毎日新しい技術が出る環境にワクワクします。変化に合わせて、作り方も自分も更新し続けます。' },
  { en: 'Ship it', ja: '作って、届ける。', body: '技術がプロダクトとして人に届く瞬間が一番おもしろい。Stellise は2名のチームで約4か月かけて App Store に出しました。' },
];


const fontCss = () => readFontCss(FONT_DIR);

const page = (t, body, css) => `<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>${fontCss()}
  * { box-sizing: border-box; margin: 0; padding: 0; } html, body { background: transparent; }
  body { font-family: 'Inter', 'Noto Sans JP', sans-serif; color: ${t.fg}; -webkit-font-smoothing: antialiased; }
  .serif { font-family: 'Inter', 'Noto Sans JP', sans-serif; font-weight: 600; font-feature-settings: 'tnum' 1, 'cv11' 1; }
  .wrap { ${PHRASE_CSS} }
  ${css}</style></head><body>${body}</body></html>`;

function sectionHtml(s, t) {
  return page(t, `<div id="c" class="sec">
    <span class="no serif">(${s.no})</span><span class="en serif">${s.en}</span><span class="ja">${s.ja}</span>
    <span class="meta">${s.meta}</span>
  </div>`, `
  .sec { width: 880px; height: 62px; display: flex; align-items: baseline; gap: 12px; padding: 18px 4px 0; border-bottom: 1px solid ${t.rule}; position: relative; }
  .sec::after { content: ''; position: absolute; left: 0; bottom: -1px; width: 120px; height: 1px; background: ${t.accent}; }
  .no { font-size: 13px; letter-spacing: .4px; color: ${t.accent}; }
  .en { font-size: 26px; line-height: 1; color: ${t.fg}; letter-spacing: -.7px; }
  .ja { font: 500 13px 'Inter', 'Noto Sans JP'; color: ${t.sub}; margin-left: 2px; }
  .meta { margin-left: auto; font: 500 12px 'Inter', sans-serif; font-feature-settings: 'tnum' 1; color: ${t.sub}; letter-spacing: .2px; }
  `);
}

function principlesHtml(t) {
  return page(t, `<div id="c" class="box">${PRINCIPLES.map((p, i) => `
    <div class="col"><div class="num serif">${['01', '02', '03'][i]}</div><div class="en serif">${p.en}</div>
    <h3>${p.ja}</h3><p class="wrap">${phrase(p.body)}</p></div>`).join('')}</div>`, `
  .box { width: 880px; display: grid; grid-template-columns: repeat(3, 1fr); background: ${t.bg}; border: 1px solid ${t.border}; border-radius: 18px; overflow: hidden; }
  .col { padding: 24px 24px 26px; position: relative; }
  .col + .col { border-left: 1px solid ${t.rule}; }
  .num { font-size: 12px; letter-spacing: .4px; color: ${t.accent}; }
  .en { font-size: 21px; line-height: 1.2; margin-top: 6px; letter-spacing: -.5px; color: ${t.fg}; }
  h3 { margin-top: 14px; font: 700 15px/1.5 'Inter', 'Noto Sans JP'; color: ${t.fg}; }
  p { margin-top: 8px; font: 400 12.5px/1.75 'Inter', 'Noto Sans JP'; color: ${t.body}; }
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
  }
  await b.close();
})();
