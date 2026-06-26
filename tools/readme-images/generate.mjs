// Generate the README section graphics with Satori (HTML/CSS -> SVG) + resvg (SVG -> PNG).
//
//   cd tools/readme-images && npm install && npm run build
//
// Emoji render as real color icons by fetching Twemoji SVGs at build time.
// Outputs PNGs to the repo root, next to the existing hand-drawn diagrams.

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, '..', '..');
const font = (f) => readFileSync(join(here, 'fonts', f));

// ---- design tokens -------------------------------------------------------
const ink = '#1f2430';
const muted = '#5b6472';
const faint = '#8a93a3';
const pageBg = '#ffffff';

// pastel themes that echo the existing add-flow.png / add-foundation.png palette
const T = {
  peach:  { bg: '#fdece2', border: '#f1cdb6', accent: '#bd6a34' },
  green:  { bg: '#e3f0e8', border: '#bcdcc8', accent: '#3f8a5d' },
  blue:   { bg: '#e2ebf7', border: '#bcd2ec', accent: '#3d6fb0' },
  beige:  { bg: '#f2ead9', border: '#ddcba9', accent: '#937234' },
  purple: { bg: '#ece1ef', border: '#d4bfdb', accent: '#84569f' },
  slate:  { bg: '#eaedf3', border: '#cfd6e2', accent: '#51607a' },
};

// ---- hyperscript helper (Satori takes React-element-like vnodes) ---------
const h = (type, props = {}, ...children) => {
  const kids = children.flat().filter((c) => c !== null && c !== undefined && c !== false);
  return { type, props: { ...props, children: kids.length <= 1 ? kids[0] : kids } };
};
const box = (style, ...children) => h('div', { style: { display: 'flex', ...style } }, ...children);
const txt = (style, value) => h('div', { style: { display: 'flex', ...style } }, String(value));

// ---- emoji -> Twemoji SVG data URI (real color icons in Satori) ----------
const EMOJI_BASES = [
  'https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/svg/',
  'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/',
];
const emojiCache = new Map();
const codepoints = (s) =>
  [...s].map((c) => c.codePointAt(0)).filter((c) => c !== 0xfe0f).map((c) => c.toString(16)).join('-');

async function emojiSvg(emoji) {
  const code = codepoints(emoji);
  if (emojiCache.has(code)) return emojiCache.get(code);
  for (const base of EMOJI_BASES) {
    try {
      const res = await fetch(base + code + '.svg');
      if (res.ok) {
        const svg = await res.text();
        const uri = 'data:image/svg+xml;base64,' + Buffer.from(svg).toString('base64');
        emojiCache.set(code, uri);
        return uri;
      }
    } catch { /* try next base */ }
  }
  throw new Error(`could not load emoji ${emoji} (${code})`);
}

const fonts = [
  { name: 'Inter', data: font('inter-400.woff'), weight: 400, style: 'normal' },
  { name: 'Inter', data: font('inter-500.woff'), weight: 500, style: 'normal' },
  { name: 'Inter', data: font('inter-600.woff'), weight: 600, style: 'normal' },
  { name: 'Inter', data: font('inter-700.woff'), weight: 700, style: 'normal' },
  { name: 'Inter', data: font('inter-800.woff'), weight: 800, style: 'normal' },
  { name: 'JetBrains Mono', data: font('mono-400.woff'), weight: 400, style: 'normal' },
  { name: 'JetBrains Mono', data: font('mono-600.woff'), weight: 500, style: 'normal' },
];

async function loadAdditionalAsset(code, text) {
  if (code === 'emoji') return emojiSvg(text);
  return code;
}

// ---- shared pieces -------------------------------------------------------
const page = (...children) =>
  box(
    {
      width: '100%', flexDirection: 'column', backgroundColor: pageBg,
      padding: '56px 60px', fontFamily: 'Inter', color: ink,
    },
    ...children,
  );

const header = (title, subtitle) =>
  box({ flexDirection: 'column', marginBottom: 34 },
    txt({ fontSize: 52, fontWeight: 800, letterSpacing: -1 }, title),
    txt({ fontSize: 24, fontWeight: 500, color: muted, marginTop: 10 }, subtitle),
  );

const emojiIcon = (uri, size = 34) =>
  h('img', { src: uri, width: size, height: size, style: { display: 'flex' } });

// ===========================================================================
// THE METHOD — four artifacts, then build, then verify
// ===========================================================================
async function methodArtifacts() {
  const arts = [
    ['1', 'Specify', 'the rules it must obey', 'peach'],
    ['2', 'Scenarios', 'those rules as pass / fail', 'peach'],
    ['3', 'Contract', 'data & interface — frozen', 'green'],
    ['4', 'Tests', 'failing first — the safety net', 'green'],
  ];
  const artCard = ([n, name, sub, theme]) => {
    const t = T[theme];
    return box(
      {
        flexBasis: 0, flexGrow: 1, height: 156, flexDirection: 'column', justifyContent: 'center',
        backgroundColor: t.bg, border: `1px solid ${t.border}`, borderRadius: 20, padding: '20px 22px',
      },
      txt({ fontSize: 17, fontWeight: 700, color: t.accent }, `Step ${n}`),
      txt({ fontSize: 30, fontWeight: 800, color: ink, marginTop: 4 }, name),
      txt({ fontSize: 16.5, fontWeight: 500, color: muted, marginTop: 6 }, sub),
    );
  };

  const outcome = (uri, lead, body, theme) => {
    const t = T[theme];
    return box(
      {
        flexBasis: 0, flexGrow: 1, alignItems: 'center', gap: 18,
        backgroundColor: t.bg, border: `1px solid ${t.border}`, borderRadius: 20, padding: '22px 26px',
      },
      emojiIcon(uri, 40),
      box({ flexDirection: 'column' },
        txt({ fontSize: 22, fontWeight: 700, color: ink }, lead),
        txt({ fontSize: 16.5, fontWeight: 500, color: muted, marginTop: 4 }, body),
      ),
    );
  };
  const [buildUri, verifyUri] = await Promise.all([emojiSvg('⚙️'), emojiSvg('🔎')]);

  return page(
    header('The method, in one move', 'Before AI writes any code, you write four artifacts — in order. Then it builds; you verify.'),
    box({ gap: 18, marginBottom: 22 }, ...arts.map(artCard)),
    box({ gap: 18, marginBottom: 26 },
      outcome(buildUri, 'AI makes the tests pass', 'Without changing them — red to green.', 'blue'),
      outcome(verifyUri, 'You verify by evidence', 'Observed behavior, not by reading code.', 'beige'),
    ),
    box({ alignItems: 'center', justifyContent: 'center', backgroundColor: '#f6f7f9', border: `1px solid #e6e9ef`, borderRadius: 16, padding: '16px 24px' },
      txt({ fontSize: 21, fontWeight: 600, color: ink }, 'The code is disposable. The artifacts are the durable asset.'),
    ),
  );
}

// ===========================================================================
// INSTALL — three steps from nothing to your first feature
// ===========================================================================
async function install() {
  const codeChip = (text) =>
    box(
      { backgroundColor: '#1f2430', borderRadius: 10, padding: '12px 16px', marginTop: 16, alignSelf: 'flex-start' },
      txt({ fontSize: 19, fontWeight: 500, fontFamily: 'JetBrains Mono', color: '#e7ebf2' }, text),
    );

  const step = (n, title, code, body, theme) => {
    const t = T[theme];
    return box(
      {
        flexBasis: 0, flexGrow: 1, flexDirection: 'column',
        backgroundColor: t.bg, border: `1px solid ${t.border}`, borderRadius: 22, padding: 28,
      },
      box({ alignItems: 'center', gap: 14 },
        box({ width: 46, height: 46, borderRadius: 23, backgroundColor: t.accent, alignItems: 'center', justifyContent: 'center' },
          txt({ fontSize: 24, fontWeight: 800, color: '#ffffff' }, n)),
        txt({ fontSize: 25, fontWeight: 700, color: ink }, title),
      ),
      codeChip(code),
      txt({ fontSize: 16.5, fontWeight: 500, color: muted, marginTop: 16, lineHeight: 1.36 }, body),
    );
  };

  return page(
    header('From nothing to your first feature', 'Install once — then talk to the agent and it drives the method.'),
    box({ gap: 20 },
      step('1', 'Install', 'npx @pilotspace/add init', 'One command. Also on pip, or as a Claude Code plugin — zero config.', 'peach'),
      step('2', 'Spawn a feature', "/add 'your goal'", 'Confirm the milestone shape, give one approval at the frozen contract.', 'green'),
      step('3', 'Resume anytime', '/add', 'State lives in .add/state.json — close your laptop, come back, no context rot.', 'blue'),
    ),
  );
}

// ---- render --------------------------------------------------------------
async function render(name, vnode, width) {
  const svg = await satori(vnode, { width, fonts, loadAdditionalAsset });
  const png = new Resvg(svg, { fitTo: { mode: 'width', value: width * 2 } }).render().asPng();
  const out = join(repoRoot, name);
  writeFileSync(out, png);
  console.log(`  ✓ ${name}  (${(png.length / 1024).toFixed(0)} KB)`);
}

console.log('Generating README graphics with Satori…');
await render('add-method.png', await methodArtifacts(), 1280);
await render('add-install.png', await install(), 1280);
console.log('Done.');
