# Design — the design-definition loop (UDD)

When a **UI feature** reaches specify, design it before you build it. This loop takes the
feature from the **domain** to a screen the human has **seen and confirmed** — a real captured
image — *before* any implementation. It is loaded on demand (like `advisor.md` / `confidence.md`);
the engine never runs it for you.

Design before code is the UDD half of the method. The token + component foundation a UI project
draws from already exists — `tokens.json` (the compact-DTCG dialect, `udd-tokens.md`),
`catalog.json` + `prototypes/<name>.json` (`udd-catalog.md`). This loop fills that foundation
for a feature and earns the human's sign-off on the look before build.

## The loop — five beats

```
design-intake  →  review-domain  →  research-components  →  wireframe  →  render-capture-confirm
```

Run the beats in order. Each feeds the next; the last ends at a human design-confirm.

### 0 · design-intake
Before you read the domain, interview the human on **four design axes** — so the look is
*directed*, not guessed. Ask each, show the options, record the pick:

- **FIDELITY** — how far this design goes: *lo-fi wireframe* · *hi-fi mockup* · *production*.
  Recorded **intent** that **informs** how far the later beats render (it is not an engine gate).
- **CONCEPT** — the design *idea / mood / direction* in a line.
- **LAYOUT** — the *structure / grid / hierarchy* the screens lean on.
- **VISUAL DESIGN** — *color · type · spacing · imagery*. **Surface** identity values for the
  human to choose — never auto-pick a brand value (identity stays **human-owned**, `udd-tokens.md`).

Record the answers **before** review-domain, at both levels: project **defaults** in DESIGN.md's
`## Design intake` section; per-screen **overrides** (only the deltas) in the per-feature design
note (the `prototypes/<name>.json` companion). Show-before-ask — confirm the picks, never assume.

### 1 · review-domain
Start from the **domain**, not a blank canvas. Read the domain model — entities, flows, the
ubiquitous language in `PROJECT.md` / `GLOSSARY.md` — and derive **which screens** the feature
needs and the **regions** each screen holds. Map each domain entity to a *presentational*
component (it shows state; it does not own a domain decision). The screen list + per-screen
regions are this beat's output, grounded in the domain you just read.

### 2 · research-components (reuse before you invent)
Check `catalog.json` **first** and **reuse** the components already there — that keeps screens
consistent. Research a reference UI only to fill a **genuine gap**, and propose a **new** catalog
component for that gap with a **cited** reference. Reuse before invention; a new component is the
exception, not the default.

### 3 · wireframe
Draw a **low-fi**, **structural** layout for each screen — regions and component slots, no
styling, no color. This is the cheapest artifact that shows the *expected layout*, so the human
can correct structure before a pixel is styled. Confirm the wireframe, then move on.

### 4 · render-capture-confirm
Render the screen as a **self-contained HTML mock** — the project's component library via CDN,
bound to `tokens.json` (resolved to CSS variables), composed from the **reusable per-component
kit** (one token-bound partial per catalog component), populated with realistic **mock** data.
**Capture** a real image (a headless screenshot) and present that image to the human for
**design-confirm** — show-before-ask, **before build**. On confirm, record the layout back to
`prototypes/<name>.json` + `catalog.json`, save the captured image to
`.add/design/captures/<name>.<ext>`, and **attach or mention it in the feature's `TASK.md`** —
so the screen the human approved is traceable from the task that builds it. The HTML mock is the
*visible evidence*; the json-render tree is the *machine-checkable* record.

## Tool-agnostic capture

How you render and capture is **your** choice: a headless browser (Playwright / Puppeteer), an
`html2image`-style renderer, a browser-automation skill, a design tool, or a hosted screenshot
service. The recommended default is the self-contained HTML mock above, captured headless,
because it needs no app build yet still wears the project's real tokens and component vocabulary.
For a project that renders json-render, the recommended default is **`@json-render/image`**
(Satori → PNG/SVG, no browser). The captured image is **design-confirm evidence** the human
approves; the engine never renders. This keeps the loop tool-agnostic and the method renderer-free.

Captures live at **`.add/design/captures/<name>.<ext>`** and are attached/mentioned in the
feature's `TASK.md`. `add.py check` raises a never-red `missing_capture` WARN for any prototype
under `.add/design/prototypes/` that still lacks a capture — a nudge to render + confirm it.

The loop **binds** the existing UDD contracts **read-only**: `tokens.json`, `catalog.json`, and
`prototypes/<name>.json` are read and composed, never reshaped — the `prototypes/<name>.json`
data contract stays **unchanged** (a change to it is a change request, not a design step). And
**identity** values — brand color, palette, typeface — stay **human-owned**: surface them for the
human to decide, never auto-pick a brand value (`udd-tokens.md`).

## The hard rules

<constraints>
- **Intake before domain.** The four axes (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) are
  interviewed and recorded — DESIGN.md defaults + per-screen overrides — before beat 1.
- **Domain first.** A screen is derived from the domain (beat 1), never sketched blind.
- **Reuse before invent.** Beat 2 checks the catalog first; a new component is a justified,
  cited exception — never the reflex.
- **Confirm before build.** The captured image is approved by the human *before* implementation;
  a design-confirm placed at or after build defeats the loop.
- **The engine never renders.** Capture is a recommended, tool-agnostic recipe run by the
  agent's own tools; the image is evidence, not an engine artifact.
- **Bind, don't break.** The loop reads `tokens.json` / `catalog.json` / `prototypes/<name>.json`
  read-only; the data contract is unchanged, and identity values stay human-owned.
</constraints>

> Used at specify for a UI feature: `phases/0-setup.md` scaffolds `DESIGN.md`, and
> `phases/1-specify.md` points here when the feature has a screen — run the four beats, then
> carry the confirmed layout into the contract.
