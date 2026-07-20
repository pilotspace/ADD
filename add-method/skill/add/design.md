# Design — the design-definition loop (UDD)

When a **UI feature** — or any human-facing **experience surface** (screen · interactive flow ·
**human gate**) — reaches specify, design it first. UDD is experience-driven, not UI-only: it takes
the surface from the **domain** to a real captured image the human has **seen and confirmed** —
*before* build. Loaded on demand; the engine never runs it. It fills the existing token + component
foundation — `tokens.json` (schema: `templates/udd-tokens.md`), `catalog.json` +
`prototypes/<name>.json` (schema: `templates/udd-catalog.md`).

## The loop — five beats

```
design-intake  →  review-domain  →  research-components  →  wireframe  →  render-capture-confirm
```

Run the beats in order; the last ends at a human design-confirm.

## Personas carry the design — the loop carries the discipline

Load the design-fit persona FIRST: it brings the **frontend-designer** performance, the loop keeps
the rigor (personas carry the expertise, the loop the discipline). Two `flow: design` dimensions
(`.add/personas/*` frontmatter, else description-match) — **UI-Designer** (visual systems · component
libraries · pixel-craft · WCAG-AA **accessibility**) and **UX-Researcher** (evidence-validated,
never assumed). None fits? Seed from `.add/personas-teacher/design/` (ui-designer · ux-researcher ·
ux-architect) + `engineering-frontend-developer` via the add agent in persona mode, then load — seed
per DOMAIN, reuse across screens. The persona's **Critical Rules** shape every beat; its **Success
Metrics** become the beat-4 confirm checklist. Advisory: it sharpens the design, never lowers a gate.

### 0 · design-intake
Before reading the domain, interview the human on **five design axes** — ask each, show options,
record the pick:

- **FIDELITY** — *lo-fi wireframe* · *hi-fi mockup* · *production*. Recorded intent, not a gate.
- **CONCEPT** — the *idea / mood / direction* in a line.
- **LAYOUT** — the *structure / grid / hierarchy*.
- **VISUAL DESIGN** — *color · type · spacing · imagery*. **Surface** identity values for the human
  to choose — never auto-pick (identity stays **human-owned**, `templates/udd-tokens.md`).
- **INTERACTION** — *cadence · when/how to seek the human · turn-rhythm*; static screen → *none*.

Record **before** review-domain: project **defaults** in DESIGN.md's `## Design intake`; per-screen
**overrides** in the per-feature note (`prototypes/<name>.json` companion). Show-before-ask.

### 1 · review-domain
Start from the **domain**, not a blank canvas. Read the domain model — entities, flows, the
ubiquitous language in `PROJECT.md` / `GLOSSARY.md` — and derive **which screens** the feature needs
+ each screen's **regions**. Map each entity to a *presentational* component (owns no domain
decision). Output: the screen list + regions.

### 2 · research-components (reuse before you invent)
Check `catalog.json` **first** and **reuse** it. Research a reference UI only for a **genuine gap**;
propose a **new** catalog component with a **cited** reference — the exception, not the reflex.

### 3 · wireframe
Draw a **low-fi**, **structural** layout per screen — regions and component slots, no styling, no
color. Confirm structure before a pixel is styled, then move on.

### 4 · render-capture-confirm
Render the screen as a **self-contained HTML mock** (component library via CDN, bound to
`tokens.json`, composed from the per-component kit, realistic **mock** data). **Capture** a real
image (headless screenshot), present it for **design-confirm** — show-before-ask, **before build**.
On confirm: record layout to `prototypes/<name>.json` + `catalog.json`, save image to
`.add/design/captures/<name>.<ext>`, mention it in the feature's `PLAN.md`.

**Persona evidence checklist.** Render the loaded personas' `## Success Metrics` as a confirmable
**checklist** beside the image — both dimensions: **UI-Designer** (visual/**accessibility**) and
**UX-Researcher** (evidence, not assumed). Each item traces to a metric the human confirms —
**evidence, never an auto-pass**; a persona **never lowers a gate**. **No UI personas** → a
generic design-confirm; UI-less skips it.

### Text-mode gate variant
A **human gate** runs the loop in **text mode** — intake the **INTERACTION** axis → design the
report per `gate-udd.md` → **confirm**; no capture beat.

## Tool-agnostic capture

Render/capture however you like (headless browser, `html2image`, a screenshot service); the default
is the self-contained HTML mock above, captured headless. For a json-render project, the default is
**`@json-render/image`** (Satori → PNG/SVG, no browser). The engine never renders — the loop stays
tool-agnostic. Captures live at **`.add/design/captures/<name>.<ext>`**, mentioned in `PLAN.md`;
`add.py check` raises a never-red `missing_capture` WARN for any prototype lacking one.

The loop **binds** the UDD contracts **read-only** — `tokens.json` / `catalog.json` /
`prototypes/<name>.json` are read, never reshaped (a reshape is a change request). **Identity**
values stay **human-owned** (`templates/udd-tokens.md`).

> Used at specify for a UI feature: `phases/direction.md`'s setup span scaffolds `DESIGN.md`, and
> its Rules span points here when the feature has a screen — run the four beats, then
> carry the confirmed layout into the contract.
