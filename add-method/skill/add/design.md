# Design — the design-definition loop (UDD)

When a **UI feature** reaches specify, design it before you build it. This loop takes the
feature from the **domain** to a screen the human has **seen and confirmed** — a real captured
image — *before* any implementation. Loaded on demand; the engine never runs it for you.

Design before code is the UDD half of the method. It fills the existing token + component
foundation — `tokens.json` (`udd-tokens.md`), `catalog.json` + `prototypes/<name>.json`
(`udd-catalog.md`) — for a feature and earns the human's sign-off before build.

## The loop — five beats

```
design-intake  →  review-domain  →  research-components  →  wireframe  →  render-capture-confirm
```

Run the beats in order; the last ends at a human design-confirm.

### 0 · design-intake
Before reading the domain, interview the human on **four design axes** so the look is *directed*,
not guessed — ask each, show options, record the pick:

- **FIDELITY** — how far this goes: *lo-fi wireframe* · *hi-fi mockup* · *production*. Recorded
  **intent** informing the later beats, not an engine gate.
- **CONCEPT** — the design *idea / mood / direction* in a line.
- **LAYOUT** — the *structure / grid / hierarchy* the screens lean on.
- **VISUAL DESIGN** — *color · type · spacing · imagery*. **Surface** identity values for the human
  to choose — never auto-pick a brand value (identity stays **human-owned**, `udd-tokens.md`).

Record the answers **before** review-domain: project **defaults** in DESIGN.md's `## Design intake`;
per-screen **overrides** (deltas only) in the per-feature design note (`prototypes/<name>.json`
companion). Show-before-ask — confirm the picks.

### 1 · review-domain
Start from the **domain**, not a blank canvas. Read the domain model — entities, flows, the
ubiquitous language in `PROJECT.md` / `GLOSSARY.md` — and derive **which screens** the feature
needs + the **regions** each holds. Map each entity to a *presentational* component (shows state;
owns no domain decision). The screen list + regions are this beat's output.

### 2 · research-components (reuse before you invent)
Check `catalog.json` **first** and **reuse** what's there — it keeps screens consistent. Research
a reference UI only to fill a **genuine gap**; propose a **new** catalog component for it with a
**cited** reference. Reuse before invention — a new component is the exception.

### 3 · wireframe
Draw a **low-fi**, **structural** layout per screen — regions and component slots, no styling, no
color. The cheapest artifact that shows the *expected layout*, so the human corrects structure
before a pixel is styled. Confirm, then move on.

### 4 · render-capture-confirm
Render the screen as a **self-contained HTML mock** — the component library via CDN, bound to
`tokens.json` (CSS variables), composed from the **reusable per-component kit** (one token-bound
partial per catalog component), with realistic **mock** data.
**Capture** a real image (a headless screenshot) and present it to the human for **design-confirm**
— show-before-ask, **before build**. On confirm, record the layout to `prototypes/<name>.json` +
`catalog.json`, save the image to `.add/design/captures/<name>.<ext>`, and **mention it in the
feature's `TASK.md`** — so the approved screen is traceable from the task. The HTML mock is the
*visible evidence*; the json-render tree is the *machine-checkable* record.

**Persona evidence checklist.** Before design-confirm, load the `flow: design` personas
(`.add/personas/*` frontmatter, else description-match) and render their `## Success Metrics`
as a confirmable **checklist** beside the captured image — **both dimensions**: **UI-Designer**
(visual + WCAG-AA **accessibility**) and **UX-Researcher** (methodology-first,
**validated by user evidence, not assumed**). Each item traces to a success-metric
the human confirms; it is **evidence, never an auto-pass** — a persona **never lowers a gate**
(ADD principle 2). **No UI personas**? A **generic design-confirm**, never blocked; UI-less skips it.

## Tool-agnostic capture

How you render and capture is **your** choice (headless browser, `html2image`, a design tool, a
screenshot service). The default is the self-contained HTML mock above, captured headless — no app
build, yet wearing the project's real tokens and components. For a json-render project, the default
is **`@json-render/image`** (Satori → PNG/SVG, no browser). The captured image is **design-confirm
evidence** the human approves; the engine never renders — the loop stays tool-agnostic, the method
renderer-free.

Captures live at **`.add/design/captures/<name>.<ext>`**, mentioned in the feature's `TASK.md`.
`add.py check` raises a never-red `missing_capture` WARN for any prototype lacking one — a nudge
to render + confirm.

The loop **binds** the UDD contracts **read-only** — `tokens.json` / `catalog.json` /
`prototypes/<name>.json` are read, never reshaped (a reshape is a change request). **Identity**
values stay **human-owned** (`udd-tokens.md`).

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
- **Confirm against the personas.** With UI personas seeded, the checklist carries the UI-Designer
  (visual/accessibility) + UX-Researcher (evidence-not-assumption) success-metrics — evidence,
  never an auto-pass.
</constraints>

> Used at specify for a UI feature: `phases/0-setup.md` scaffolds `DESIGN.md`, and
> `phases/1-specify.md` points here when the feature has a screen — run the four beats, then
> carry the confirmed layout into the contract.
