# README section graphics (Satori)

These scripts generate the three section graphics used by the repo-root [`README.md`](../../README.md):

| Output (written to repo root) | Replaces |
| --- | --- |
| `add-method.png` | the "method in one move" paragraph |
| `add-install.png` | the install / first-feature steps |

They are rendered from plain HTML/CSS with [Satori](https://github.com/vercel/satori)
(HTML/CSS → SVG) and [`@resvg/resvg-js`](https://github.com/yisibl/resvg-js) (SVG → PNG).
Emoji render as real color icons by fetching [Twemoji](https://github.com/jdecked/twemoji)
SVGs at build time (network required only when re-generating).

## Re-generate

```bash
cd tools/readme-images
npm install
npm run build      # writes the three PNGs to the repo root
```

Edit the copy, colors, or layout in [`generate.mjs`](./generate.mjs) and re-run.

## Fonts

Bundled under `fonts/` so the build is portable (no system fonts required):

- **Inter** (`inter-*.woff`) — [SIL Open Font License](https://github.com/rsms/inter/blob/master/LICENSE.txt)
- **JetBrains Mono** (`mono-*.woff`) — [SIL Open Font License](https://github.com/JetBrains/JetBrainsMono/blob/master/OFL.txt)

Satori supports `ttf` / `otf` / `woff` (not `woff2`).
