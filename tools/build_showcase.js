// 実物の画面を使う画像の部品を作る。
//   tools/.build/phones/*.png          … iPhone の枠に入れた画面（見出しと紹介帯に埋め込む）
//   tools/.build/<id>-base-<theme>.png … 紹介帯の、画面を除いた下地（build_strips.py が使う）
// 使い方は tools/README.md。
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { fontCss: readFontCss, serveFonts, fontsReady, phrase, PHRASE_CSS } = require('./render');

const FONT_DIR = path.resolve(process.argv[2] || process.env.FONT_DIR || 'fonts');
const BUILD = path.resolve(process.argv[3] || path.join(__dirname, '.build'));
const SHOTS = path.join(__dirname, 'shots');
const ICONS = path.join(__dirname, 'icons');

const b64 = (p) => fs.readFileSync(p).toString('base64');
const shot = (name) => `data:image/jpeg;base64,${b64(path.join(SHOTS, `${name}.jpg`))}`;
const icon = (name) => `data:image/png;base64,${b64(path.join(ICONS, `${name}.png`))}`;

const fontCss = () => readFontCss(FONT_DIR);

const THEMES = {
  dark: { fg: '#E6EDF3', body: '#D0D7DE', sub: '#8B949E', border: '#30363D', tagBg: '#ffffff0f', tagBorder: '#ffffff1f', iconBorder: '#ffffff1a', glow: '55' },
  light: { fg: '#1C1A2B', body: '#3B3852', sub: '#6E6A86', border: '#E4E1F0', tagBg: '#ffffffb3', tagBorder: '#E4E0F2', iconBorder: '#00000014', glow: '33' },
};

// 作品の紹介帯：左に説明、右に画面3枚（画面は build_strips.py が動きを付けて重ねる）
const SHOWCASE = [
  {
    id: 'stellise', title: 'Stellise', icon: 'stellise', accent: '#8B7CF6',
    status: 'App Storeで公開中',
    desc: '予定と天気から、AIが朝にやることを提案する目覚ましアプリ。画面は1つにまとめ、夜は就寝用、朝はAIの提案を出す。',
    meta: '2名のチームで約4か月 · 企画とSwiftUIのフロントエンドを担当',
    tags: ['iOS', 'SwiftUI'],
    bg: {
      dark: 'linear-gradient(120deg, #1B1B3A 0%, #0E0E1E 55%, #1A1530 100%)',
      light: 'linear-gradient(120deg, #EEEAFE 0%, #FFFFFF 55%, #F4EFFF 100%)',
    },
  },
  {
    id: 'voice-context', title: 'Voice Context', icon: 'voice-context', accent: '#4C7DFF',
    status: 'App Storeで公開中',
    desc: '対面の会話を、AIエージェントが後から読める記録に変えるiOSアプリ。決めたこと・やること・背景を残す。',
    meta: '開発を担当 · App Storeへの公開はチームメイト',
    tags: ['iOS', 'Swift', 'MCP'],
    bg: {
      dark: 'linear-gradient(120deg, #0E1A33 0%, #0D1117 55%, #131A2E 100%)',
      light: 'linear-gradient(120deg, #E8F0FF 0%, #FFFFFF 55%, #EEF3FF 100%)',
    },
  },
];

const BASE = (t) => `* { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { background: transparent; }
  body { font-family: 'Inter', 'Noto Sans JP', sans-serif; color: ${t.fg}; -webkit-font-smoothing: antialiased; }
  .desc, .meta { ${PHRASE_CSS} }`;

const PHONE_CSS = `.phone { width: 150px; height: 326px; border-radius: 27px; padding: 5px; flex: none;
           background: linear-gradient(160deg, #3a3a48, #101016 40%, #1c1c26);
           box-shadow: 0 0 0 1px #ffffff26 inset, 0 24px 48px -12px #000000aa, 0 8px 18px -6px #00000066; }
  .phone img { width: 140px; height: 316px; border-radius: 22px; display: block; object-fit: cover; }`;

const page = (t, body, css = '') => `<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>${fontCss()}${BASE(t)}${PHONE_CSS}${css}</style></head><body>${body}</body></html>`;

// 1台ずつの iPhone（影の分だけ余白を取る：左右22・上18・下40）
const phoneHtml = (name) => page(THEMES.dark, `<div id="c" style="padding:18px 22px 40px;display:inline-block"><div class="phone"><img src="${shot(name)}"></div></div>`);

function stripHtml(s, theme) {
  const t = THEMES[theme];
  return page(t, `<div id="c" class="strip">
    <div class="glow"></div>
    <div class="text">
      <div class="top"><img class="icon" src="${icon(s.icon)}"><div><h1>${s.title}</h1><div class="status"><span class="dot"></span>${s.status}</div></div></div>
      <p class="desc">${phrase(s.desc)}</p>
      <p class="meta">${phrase(s.meta)}</p>
      <div class="tags">${s.tags.map((x) => `<span class="tag">${x}</span>`).join('')}</div>
    </div>
  </div>`, `
  .strip { width: 880px; height: 300px; border-radius: 18px; border: 1px solid ${t.border}; background: ${s.bg[theme]};
           position: relative; overflow: hidden; display: flex; }
  .glow { position: absolute; right: -80px; top: -120px; width: 520px; height: 520px; border-radius: 50%;
          background: radial-gradient(closest-side, ${s.accent}${t.glow}, transparent); }
  .text { position: relative; width: 380px; padding: 30px 0 26px 32px; display: flex; flex-direction: column; }
  .top { display: flex; align-items: center; gap: 14px; }
  .icon { width: 52px; height: 52px; border-radius: 13px; border: 1px solid ${t.iconBorder}; }
  h1 { font: 700 24px/1.15 'Inter'; letter-spacing: -.3px; }
  .status { margin-top: 6px; font: 500 12px 'Inter', 'Noto Sans JP'; color: ${t.sub}; display: flex; align-items: center; gap: 6px; }
  .dot { width: 7px; height: 7px; border-radius: 50%; background: #3FB950; box-shadow: 0 0 8px #3FB95088; }
  .desc { margin-top: 18px; font: 500 14.5px/1.7 'Inter', 'Noto Sans JP'; color: ${t.body}; }
  .meta { margin-top: 8px; font: 400 12px/1.5 'Inter', 'Noto Sans JP'; color: ${t.sub}; }
  .tags { margin-top: auto; display: flex; gap: 6px; }
  .tag { font: 400 11px 'JetBrains Mono'; color: ${t.body}; background: ${t.tagBg}; border: 1px solid ${t.tagBorder}; border-radius: 999px; padding: 3px 10px; }
  `);
}

async function shotEl(p, html, out) {
  await p.setContent(html, { waitUntil: 'load' });
  await fontsReady(p);
  await (await p.$('#c')).screenshot({ path: out, omitBackground: true });
  console.log('wrote', out);
}

(async () => {
  fs.mkdirSync(path.join(BUILD, 'phones'), { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 600 }, deviceScaleFactor: 2 });
  await serveFonts(p, FONT_DIR);
  const names = fs.readdirSync(SHOTS).filter((f) => f.endsWith('.jpg')).map((f) => f.replace(/\.jpg$/, ''));
  for (const n of names) await shotEl(p, phoneHtml(n), path.join(BUILD, 'phones', `${n}.png`));
  for (const s of SHOWCASE) {
    for (const theme of Object.keys(THEMES)) await shotEl(p, stripHtml(s, theme), path.join(BUILD, `${s.id}-base-${theme}.png`));
  }
  await b.close();
})();
