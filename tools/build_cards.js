// OSSのカード（assets/cards/*-<明暗>.png）と数字の帯（assets/stats-<明暗>.png）を作る。
// HTML を Chromium で描いて 2 倍の解像度で保存する。使い方は tools/README.md。
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const FONT_DIR = path.resolve(process.argv[2] || process.env.FONT_DIR || 'fonts');
const ROOT = path.resolve(__dirname, '..');
const ICONS = path.join(__dirname, 'icons');

const STATUS = {
  store: { color: '#3FB950', text: 'App Storeで公開中' },
  oss: { color: '#7C8CFF', text: '公開中のOSS' },
  spec: { color: '#7C8CFF', text: '公開中の仕様' },
  npm: { color: '#F0883E', text: 'npmで公開中' },
  proto: { color: '#8B949E', text: '公開中の試作' },
};

// 文言は life/job-hunt の整合性ノートと提出済みES（ARISE Q1/Q2）に合わせる。
const CARDS = [
  {
    id: 'wcc', title: 'Web Capability Compiler', status: 'oss', icon: { text: 'W', from: '#7C8CFF', to: '#A371F7' }, accent: '#7C8CFF',
    desc: '既存のWebサイトを、AIエージェントが安全に呼べる道具に変える。購入や送信は実行前に止める。',
    meta: '個人開発 · テスト553件 · AIへ渡す情報量を約87%削減',
    tags: ['Python', 'MCP', 'Playwright'],
  },
  {
    id: 'aun', title: 'AUN Protocol', status: 'spec', icon: { text: '阿吽', from: '#2EA6A6', to: '#3B82F6', small: true }, accent: '#2EA6A6',
    desc: '持ち主の代わりにAIエージェント同士が交渉するための約束事。開示は最小、最後は人が承認。',
    meta: 'Apache-2.0 · 仕様・スキーマ・検証用データ',
    tags: ['Protocol', 'JSON Schema'],
  },
  {
    id: 'kasane', title: 'KASANE', status: 'npm', icon: { text: '重', from: '#F0883E', to: '#DB61A2' }, accent: '#F0883E',
    desc: 'コーディングAIが実際に読んでいる文脈を、点検・説明・比較するコマンドラインの道具。',
    meta: 'npm: kasane-cli',
    tags: ['TypeScript', 'CLI'],
  },
  {
    id: 'local-rag-agent', title: 'local-rag-agent', status: 'proto', icon: { text: 'R', from: '#6E7681', to: '#7C8CFF' }, accent: '#58A6FF',
    desc: '機密文書をネットに出さずに検索するRAGの試作。閲覧権限に合わせて答えを絞る。',
    meta: 'チーム開発 · RAGの設計と構築を担当',
    tags: ['Python', 'Qdrant', 'vLLM'],
  },
];

const STATS = [
  { num: '2', unit: '本', label: 'App Storeで公開中のアプリ' },
  { num: '4', unit: '本', label: '公開しているOSS' },
  { num: '553', unit: '件', label: 'WCCのテスト' },
  { num: '87', unit: '%減', pre: '約', label: 'WCCでAIへ渡す情報量' },
];

function fontCss() {
  return fs.readdirSync(FONT_DIR)
    .filter((f) => f.endsWith('.css'))
    .map((f) => fs.readFileSync(path.join(FONT_DIR, f), 'utf8'))
    .join('\n');
}

// 明るい画面用と暗い画面用の色。README では <picture> で出し分ける。
const THEMES = {
  dark: {
    bg: '#161B22', border: '#30363D', fg: '#E6EDF3', body: '#C9D1D9', sub: '#8B949E',
    tagBg: '#21262D', tagBorder: '#30363D', divider: '#21262D', glow: '40', glow2: '14', iconBorder: '#ffffff1a', line: 'cc',
  },
  light: {
    bg: '#FFFFFF', border: '#E4E1F0', fg: '#1C1A2B', body: '#3B3852', sub: '#6E6A86',
    tagBg: '#F4F2FB', tagBorder: '#E4E0F2', divider: '#EDEAF6', glow: '22', glow2: '0c', iconBorder: '#00000014', line: '99',
  },
};

const BASE = (t) => `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { background: transparent; }
  body { font-family: 'Inter', 'Noto Sans JP', sans-serif; color: ${t.fg}; -webkit-font-smoothing: antialiased; }
  .desc, .meta, .label { word-break: auto-phrase; text-wrap: pretty; }
`;

function iconHtml(icon) {
  if (icon.img) {
    const data = fs.readFileSync(path.join(ICONS, icon.img)).toString('base64');
    return `<img class="icon" src="data:image/png;base64,${data}">`;
  }
  return `<div class="icon tile${icon.small ? ' small' : ''}" style="background:linear-gradient(135deg, ${icon.from}, ${icon.to})">${icon.text}</div>`;
}

function cardHtml(c, t) {
  const st = STATUS[c.status];
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>${fontCss()}${BASE(t)}
  .card { width: 420px; height: 200px; border: 1px solid ${t.border}; border-radius: 16px;
          background: radial-gradient(circle at 100% 0%, ${c.accent}${t.glow}, transparent 55%), radial-gradient(circle at 0% 100%, ${c.accent}${t.glow2}, transparent 50%), ${t.bg};
          padding: 20px 22px; display: flex; flex-direction: column; position: relative; overflow: hidden; }
  .card::after { content: ''; position: absolute; inset: 0 0 auto 0; height: 1.5px;
          background: linear-gradient(90deg, transparent, ${c.accent}${t.line}, transparent); }
  .top { display: flex; align-items: center; gap: 14px; }
  .icon { width: 48px; height: 48px; border-radius: 12px; flex: none; border: 1px solid ${t.iconBorder}; }
  .tile { display: flex; align-items: center; justify-content: center; color: #fff; font: 700 22px 'Inter', 'Noto Sans JP'; }
  .tile.small { font-size: 15px; letter-spacing: 1px; }
  h1 { font: 700 20px/1.2 'Inter', 'Noto Sans JP'; letter-spacing: -.2px; }
  .status { margin-top: 5px; font: 500 11.5px 'Inter', 'Noto Sans JP'; color: ${t.sub}; display: flex; align-items: center; gap: 6px; }
  .dot { width: 7px; height: 7px; border-radius: 50%; background: ${st.color}; box-shadow: 0 0 8px ${st.color}88; }
  .desc { margin-top: 14px; font: 500 13.5px/1.65 'Inter', 'Noto Sans JP'; color: ${t.body}; letter-spacing: .1px; }
  .meta { margin-top: 6px; font: 400 11.5px/1.5 'Inter', 'Noto Sans JP'; color: ${t.sub}; }
  .tags { margin-top: auto; display: flex; gap: 6px; }
  .tag { font: 400 11px 'JetBrains Mono'; color: ${t.body}; background: ${t.tagBg}; border: 1px solid ${t.tagBorder}; border-radius: 999px; padding: 3px 10px; }
  </style></head><body><div class="card" id="c">
    <div class="top">${iconHtml(c.icon)}<div><h1>${c.title}</h1><div class="status"><span class="dot"></span>${st.text}</div></div></div>
    <div class="desc">${c.desc}</div>
    <div class="meta">${c.meta}</div>
    <div class="tags">${c.tags.map((x) => `<span class="tag">${x}</span>`).join('')}</div>
  </div></body></html>`;
}

function statsHtml(t) {
  const grad = t === THEMES.dark ? 'linear-gradient(180deg, #FFFFFF, #C9C1FF)' : 'linear-gradient(180deg, #2A2547, #6D5BD0)';
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>${fontCss()}${BASE(t)}
  .strip { width: 880px; height: 112px; background: radial-gradient(circle at 50% -40%, #8B7CF6${t.glow}, transparent 60%), ${t.bg}; border: 1px solid ${t.border}; border-radius: 16px;
           display: grid; grid-template-columns: repeat(${STATS.length}, 1fr); position: relative; overflow: hidden; }
  .strip::after { content: ''; position: absolute; inset: 0 0 auto 0; height: 1.5px; background: linear-gradient(90deg, transparent, #8B7CF6${t.line}, transparent); }
  .cell { display: flex; flex-direction: column; justify-content: center; padding: 0 26px; }
  .cell + .cell { border-left: 1px solid ${t.divider}; }
  .num { font: 700 34px/1 'Inter'; letter-spacing: -1px; background: ${grad}; -webkit-background-clip: text; color: transparent; }
  .num small, .num .pre { font: 500 14px 'Inter', 'Noto Sans JP'; letter-spacing: 0; color: ${t.body}; -webkit-text-fill-color: ${t.body}; }
  .num small { margin-left: 3px; } .num .pre { margin-right: 3px; }
  .label { margin-top: 10px; font: 400 12px 'Inter', 'Noto Sans JP'; color: ${t.sub}; }
  </style></head><body><div class="strip" id="c">
  ${STATS.map((x) => `<div class="cell"><div class="num">${x.pre ? `<span class="pre">${x.pre}</span>` : ''}${x.num}<small>${x.unit}</small></div><div class="label">${x.label}</div></div>`).join('')}
  </div></body></html>`;
}

async function render(page, html, out) {
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const el = await page.$('#c');
  await el.screenshot({ path: out, omitBackground: true });
  console.log('wrote', path.relative(ROOT, out));
}

(async () => {
  const outDir = path.resolve(process.argv[3] || path.join(ROOT, 'assets'));
  fs.mkdirSync(path.join(outDir, 'cards'), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 960, height: 400 }, deviceScaleFactor: 2 });
  for (const [name, t] of Object.entries(THEMES)) {
    for (const c of CARDS) await render(page, cardHtml(c, t), path.join(outDir, 'cards', `${c.id}-${name}.png`));
    await render(page, statsHtml(t), path.join(outDir, `stats-${name}.png`));
  }
  await browser.close();
})();
