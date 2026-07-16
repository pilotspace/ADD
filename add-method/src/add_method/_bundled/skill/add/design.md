# Design — the design-definition loop (UDD)

When a **UI feature** — or any human-facing **experience surface** (screen · interactive flow ·
**human gate**) — reaches specify, design it first. UDD is experience-driven, not UI-only: it takes
the surface from the **domain** to a real captured image the human has **seen and confirmed** —
*before* build. Loaded on demand; the engine never runs it. It fills the existing token + component
foundation — `tokens.json` (`udd-tokens.md`), `catalog.json` + `prototypes/<name>.json`
(`udd-catalog.md`).

## The loop — five beats

```
design-intake  →  review-domain  →  research-components  →  wireframe  →  render-capture-confirm
```

Run the beats in order; the last ends at a human design-confirm.

### 0 · design-intake
Before reading the domain, interview the human on **five design axes** — ask each, show options,
record the pick:

- **FIDELITY** — *lo-fi wireframe* · *hi-fi mockup* · *production*. Recorded intent, not a gate.
- **CONCEPT** — the *idea / mood / direction* in a line.
- **LAYOUT** — the *structure / grid / hierarchy*.
- **VISUAL DESIGN** — *color · type · spacing · imagery*. **Surface** identity values for the human
  to choose — never auto-pick (identity stays **human-owned**, `udd-tokens.md`).
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
`.add/design/captures/<name>.<ext>`, mention it in the feature's `TASK.md`.

**Persona evidence checklist.** Before design-confirm, load the `flow: design` personas
(`.add/personas/*` frontmatter, else description-match) and render their `## Success Metrics` as a
confirmable **checklist** beside the image — **both dimensions**: **UI-Designer** (visual + WCAG-AA
**accessibility**) and **UX-Researcher** (evidence-validated, not assumed). Each item traces to a
success-metric the human confirms — **evidence, never an auto-pass**; a persona
**never lowers a gate** (principle 2). **No UI personas** → a generic design-confirm; UI-less skips it.

### Text-mode gate variant
A **human gate** runs the loop in **text mode** — intake the **INTERACTION** axis → design the
report per `gate-udd.md` → **confirm**; no capture beat.

## Tool-agnostic capture

Render/capture however you like (headless browser, `html2image`, a screenshot service); the default
is the self-contained HTML mock above, captured headless. For a json-render project, the default is
**`@json-render/image`** (Satori → PNG/SVG, no browser). The engine never renders — the loop stays
tool-agnostic. Captures live at **`.add/design/captures/<name>.<ext>`**, mentioned in `TASK.md`;
`add.py check` raises a never-red `missing_capture` WARN for any prototype lacking one.

The loop **binds** the UDD contracts **read-only** — `tokens.json` / `catalog.json` /
`prototypes/<name>.json` are read, never reshaped (a reshape is a change request). **Identity**
values stay **human-owned** (`udd-tokens.md`).

## The hard rules

<constraints>
- **Intake before domain.** The five axes (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN ·
  INTERACTION) are interviewed and recorded — DESIGN.md defaults + per-screen overrides — before beat 1.
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
