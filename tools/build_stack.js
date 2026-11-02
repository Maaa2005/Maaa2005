// 使っている技術の画像 assets/stack-dark.png・assets/stack-light.png を作る。
// ロゴは npm の simple-icons（13.21.0）から取る。無い物は汎用の記号にする。
// 使い方: node tools/build_stack.js <書体フォルダ> assets <simple-icons を入れた node_modules の親>
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const FONT_DIR = path.resolve(process.argv[2] || 'fonts');
const OUT = path.resolve(process.argv[3] || path.join(__dirname, '..', 'assets'));
const si = require(require.resolve('simple-icons', { paths: [path.resolve(process.argv[4] || '.')] }));

const ROWS = [
  ['Languages', [['Swift', 'siSwift'], ['Python', 'siPython'], ['TypeScript', 'siTypescript'], ['JavaScript', 'siJavascript'], ['C', 'siC']]],
  ['iOS', [['SwiftUI', 'siSwift'], ['App Intents', 'siApple'], ['WidgetKit', 'siApple'], ['StoreKit 2', 'siApple'], ['Core Motion', 'siApple'], ['EventKit', 'siApple'], ['Xcode', 'siXcode']]],
  ['AI & agents', [['MCP', null], ['Claude API', 'siAnthropic'], ['Claude Code', 'siClaude'], ['Gemini API', 'siGooglegemini'], ['Qdrant', null], ['vLLM', null], ['Local LLMs', null], ['RAG', null], ['TensorFlow Lite', 'siTensorflow'], ['NumPy', 'siNumpy'], ['pandas', 'siPandas']]],
  ['Web & backend', [['FastAPI', 'siFastapi'], ['Flask', 'siFlask'], ['Pydantic', 'siPydantic'], ['SQLAlchemy', 'siSqlalchemy'], ['React', 'siReact'], ['Next.js', 'siNextdotjs'], ['Node.js', 'siNodedotjs'], ['Vite', 'siVite'], ['Playwright', null], ['Vitest', 'siVitest'], ['Firebase', 'siFirebase'], ['Google Cloud', 'siGooglecloud']]],
  ['Desktop & tools', [['Tauri', 'siTauri'], ['Docker', 'siDocker'], ['GitHub Actions', 'siGithubactions'], ['Git', 'siGit'], ['Figma', 'siFigma']]],
];

const THEMES = {
  dark: { bg: '#161B22', border: '#30363D', fg: '#E6EDF3', label: '#8B949E', chip: '#21262D', chipBorder: '#30363D', divider: '#21262D', ground: [22, 27, 34] },
  light: { bg: '#FFFFFF', border: '#E4E1F0', fg: '#1C1A2B', label: '#6E6A86', chip: '#F7F6FC', chipBorder: '#E7E4F3', divider: '#EFEDF7', ground: [255, 255, 255] },
};

function lum(hex) {
  const c = hex.match(/../g).map((h) => parseInt(h, 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function contrast(a, rgb) {
  const l1 = lum(a);
  const l2 = lum(rgb.map((v) => v.toString(16).padStart(2, '0')).join(''));
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

// 無いロゴの代わり（小さな基板の記号）
const GENERIC = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/></svg>';

function chip(name, key, t) {
  let svg = GENERIC;
  let color = t.label;
  if (key && si[key]) {
    const ic = si[key];
    color = contrast(ic.hex, t.ground) < 2.2 ? t.fg : `#${ic.hex}`;
    svg = `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="${ic.path}"/></svg>`;
  }
  return `<span class="chip"><span class="ic" style="color:${color}">${svg}</span>${name}</span>`;
}

function html(t) {
  const css = fs.readdirSync(FONT_DIR).filter((f) => f.endsWith('.css') && !f.startsWith('noto')).map((f) => fs.readFileSync(path.join(FONT_DIR, f), 'utf8')).join('\n');
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css}
  * { box-sizing: border-box; margin: 0; padding: 0; } html, body { background: transparent; }
  body { font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }
  .box { width: 880px; background: ${t.bg}; border: 1px solid ${t.border}; border-radius: 16px; padding: 6px 22px; }
  .row { display: grid; grid-template-columns: 150px 1fr; gap: 12px; padding: 14px 0; align-items: start; }
  .row + .row { border-top: 1px solid ${t.divider}; }
  .lab { font: 500 12px/30px 'JetBrains Mono', monospace; color: ${t.label}; letter-spacing: .5px; }
  .chips { display: flex; flex-wrap: wrap; gap: 7px; }
  .chip { display: inline-flex; align-items: center; gap: 7px; height: 30px; padding: 0 11px; border-radius: 9px;
          background: ${t.chip}; border: 1px solid ${t.chipBorder}; font: 500 13px 'Inter'; color: ${t.fg}; }
  .ic { display: inline-flex; }
  </style></head><body><div class="box" id="c">
  ${ROWS.map(([lab, items]) => `<div class="row"><div class="lab">${lab}</div><div class="chips">${items.map(([n, k]) => chip(n, k, t)).join('')}</div></div>`).join('')}
  </div></body></html>`;
}

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 940, height: 600 }, deviceScaleFactor: 2 });
  for (const [name, t] of Object.entries(THEMES)) {
    await p.setContent(html(t), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const out = path.join(OUT, `stack-${name}.png`);
    await (await p.$('#c')).screenshot({ path: out, omitBackground: true });
    console.log('wrote', out);
  }
  await b.close();
})();
