# UDD wireframe + HTML mock — make the layout visible before build

`udd-tokens.md` says what a UI is *made of*; `udd-catalog.md` says what it is *built
from*. Both are abstract JSON. This doc closes the last gap design.md names: turn a
prototype tree into a **real, captured screen the human confirms BEFORE build** — so
the build matches the expected layout instead of discovering it.

Two stages, low-fi → hi-fi:

- **Stage A — wireframe**: a fast, low-fi *structural* map. No styling.
- **Stage B — HTML mock**: a self-contained screen the human (or a headless tool)
  actually renders and screenshots. The image is the design-confirm evidence.

The engine never renders. This is a recommendation + a worked sample, tool-agnostic
(consistent with `udd-catalog.md`'s render recipe). A worked pair ships beside it —
`welcome.sample.html` + `settings.sample.html` — that you can open in any browser.

## Stage A — wireframe (low-fi, structural)

A **wireframe** is a low-fidelity, *structural* map of one screen — regions and the
component **slots** inside them — derived directly from the prototype tree, **before**
any color, type scale, or spacing is decided. It answers "what goes where", not "what
it looks like".

Derive it mechanically from `prototypes/<name>.json`: each container element is a
region, each leaf element is a slot, the tree's nesting is the layout nesting. Keep it
in plain text or boxes — the point is speed and a shared structural picture, not paint.

Worked example: `wireframe.sample.txt` is the Stage-A map of the welcome screen
(`Screen > Card > {Text, Text, Button}`), with each slot mapped 1:1 to its prototype
element. No colors, no pixel values — those arrive in Stage B.

## Stage B — HTML mock (hi-fi, self-contained, screenshot-able)

The mock is a real screen built from the design foundation in **four moves**:

1. **Resolve `tokens.json`'s `semantic` layer → CSS custom properties.** Each
   `{semantic.dotted.path}` alias becomes a `--semantic-dotted-path` variable in a
   `:root` block. This file is the single source of token values — see
   `tokens.sample.css`.
2. **One kit class per `catalog.json` component.** Each component (Screen, Card, Text,
   Button, …) gets exactly one CSS class whose every visual value is a `var(--…)` from
   step 1 — never a literal. This is the reusable **kit** — see `kit.sample.css`.
3. **Compose the prototype tree into HTML using the kit classes.** Walk
   `prototypes/<name>.json`: each element becomes an HTML node carrying its
   component's kit class; nesting follows `children`. Style nothing inline.
4. **Populate with mock data.** Fill the `Text`/`Button` content from the prototype's
   props (or representative stand-ins). The result is a **self-contained** screen —
   *no network*: it links only local sibling files — that opens offline and a
   **headless** tool can **screenshot** directly (Playwright, `html2image`,
   an agent browser, or a SaaS renderer — pick one; the engine never renders).

`welcome.sample.html` is the worked Stage-B mock of `prototype.sample.json`.

## Fast path — render via json-render (for JS-ecosystem projects)

Your `prototypes/<name>.json` is already a **json-render `Spec`** — the exact schema
`udd-catalog.md` pins. If your project renders json-render (React, Vue, Svelte, Solid,
React Native, …) you can skip the hand-authored kit and render the prototype through
your *real* catalog, so the mock **is** the product and cannot drift from it:

- **Render** — feed `prototype.json` into your `defineCatalog(…)` (see `udd-catalog.md`'s
  "Render recipe"), or use a pre-built catalog such as `@json-render/shadcn` (36
  shadcn/ui components) — no hand-written components for those stacks.
- **Capture** — `@json-render/image` renders a `Spec` straight to **PNG / SVG** (Satori,
  no browser), a deterministic captured image with no headless-screenshot step. That
  image is the same design-confirm evidence (see "Capture is evidence").

Trade-off — this is the *fast path*, not the floor. json-render needs the JS/npm
toolchain + a renderer package, so it does NOT cover a native (SwiftUI / Flutter / …)
project, and it has **no wireframe mode** (Stage A stays a separate, renderer-agnostic
structural artifact). When there is no toolchain, or the stack is not JS, the
self-contained HTML + CSS mock above is the universal default.

## Reuse & consistency (by construction)

Screens compose **only** from the shared kit + token vars — never hand-styled per
screen. Because every screen links the *same* `tokens.sample.css` + `kit.sample.css`,
a single **semantic-token flip** (one line in `tokens.sample.css`) re-renders **every**
screen the same way. Reuse before invent: pull an existing kit class first; add a new
one only for a genuine new `catalog.json` component.

`settings.sample.html` is a SECOND screen that **reuses** the welcome kit classes
(screen/card/text/button) without redefining them — proving the consistency: flip
`--semantic-color-surface` once and both screens change together.

## Capture is evidence

The screenshot of a Stage-B mock is **design-confirm evidence** — the human-facing
proof of beat 4 in `design.md`. Captures live at **`.add/design/captures/<name>.<ext>`**
(one per prototype) and are **attached or mentioned in the feature's `PLAN.md`**
(alongside the §6 evidence), so the screen the human approved stays traceable from the
task that builds it. The recommended default capture engine for a json-render project is
**`@json-render/image`** (Satori → PNG/SVG, no browser); otherwise capture the
self-contained HTML mock headless. The engine never produces this image — it only
MEASURES presence (`add.py check` raises a never-red `missing_capture` WARN for a
prototype with no capture); the capture recipe is a recommendation, not an engine feature.

## Binds (read-only)

This recipe **consumes** the UDD contracts and never reshapes them:

- `tokens.json` — the semantic layer is the source of the CSS variables (unchanged).
- `catalog.json` — its component set is the source of the kit classes (unchanged).
- `prototypes/<name>.json` — the json-render tree is the structure both stages walk
  (unchanged; the frozen data contract is read-only — a change there is a separate
  change-request).

The mock (`*.sample.html`) is the human-facing *visible* view; the frozen
`prototypes/<name>.json` tree is the *machine-checkable* record. They are two views of
one screen.

## Ships byte-identical

`udd-wireframe.md` and its five sample files ship **byte-identical** in both template
trees (canonical `tooling/templates/` and the `_bundled` mirror) — enforced by
`test_bundle_parity`. A file present in one tree but missing from the other is a
`parity_break`.
