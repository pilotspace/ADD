# MILESTONE: UDD design-definition loop

goal: A UI project's design step starts from the domain, researches and proposes components, and the human confirms the screen as a real captured image before build — so implementation matches the expected layout
rationale: new-major — extends the UDD theme (udd-design-foundation is shipped+archived, not a live milestone to slice) with a coherent ~4-beat design-definition loop too big for one task. Closes the gap the human named: today's design artifacts are abstract token/catalog/prototype JSON with no VISIBLE wireframe/layout, so neither human nor AI can confirm the expected layout before build.
stage: mvp · status: active · created: 2026-06-15

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
- `design.md` on-demand guide: the 4-beat design-definition loop — (1) review DDD (domain → screens/regions, map entities to presentational components) → (2) research + suggest components (reuse-before-invent; websearch reference UIs for gaps) → (3) wireframe the layout (low-fi, structural) → (4) render a real captured image (hi-fi mock) and confirm with the human. Referenced from `phases/0-setup.md` + `phases/1-specify.md`.
- Wireframe artifact format (Stage A, low-fi) + the self-contained HTML-mock recipe (Stage B, hi-fi): one HTML file per screen, the project's component lib via CDN, bound to the existing `tokens.json` (→ CSS variables), composed from a reusable per-component kit, populated with mock data, rendered headless → a real pixel image. + a worked sample that renders.
- Reusable per-component kit: one token-bound HTML/CSS partial per `catalog.json` component, so screens compose from reusable parts and a token change re-renders all consistently.
- Captured-image evidence convention: where captures live, a tool-agnostic capture recipe + named default (headless screenshot via Playwright/`html2image`/agent-browser/SaaS), engine-never-renders; + an `add.py check` never-red WARN when a prototype has no confirmed capture (measure, never block).
- Book (`docs/*`) + GLOSSARY + ×3-tree (canonical/bundled/dogfood) parity.

Out:
- No bundled or REQUIRED renderer / screenshot tool — the method stays tool-agnostic (recommendation + named default only; the engine never renders).
- No change to the frozen `prototypes/<name>.json` *data* contract (the json-render shape) — the loop binds/extends it; any change to it is a separate change-request.
- No new gated `design` phase — the loop ships as an on-demand guide, not a phase (the frozen 9-phase ladder is untouched).
- No live renderer or CI screenshot pipeline inside `add.py`.
- Identity values stay human-owned (unchanged); interactive-prototype linting (`state`/`on`/`visible` passthrough) stays deferred.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Tool-agnostic capture** — the guide RECOMMENDS the HTML-mock + headless-capture recipe and a named default; the engine never renders. The captured image is a **design-confirm evidence artifact**, not an engine output (consistent with the `capability-as-prose-recommendation-engine-tool-agnostic` convention).
- **Two render tiers (floor + fast-path)** — the universal FLOOR is a zero-dependency self-contained HTML+CSS mock (any stack, no toolchain, any headless screenshotter). The FAST PATH (added in `wireframe-mock-recipe`, human-decided 2026-06-16 after a deep review of vercel-labs/json-render) is to render `prototype.json` through the project's real json-render catalog (`defineCatalog` / `@json-render/shadcn`) — the mock IS the product. **`@json-render/image` (Satori → PNG/SVG, no browser) is the earmarked named-default capture engine for `capture-evidence` (task 3)** — deterministic spec→image, stronger than a headless screenshot. json-render is JS-ecosystem-only + has no wireframe mode, so it never becomes the floor and Stage A stays renderer-agnostic.
- **Reuse-before-invent + consistency-by-construction** — `catalog.json` is the single reusable-component source. The loop reuses existing catalog components first and proposes NEW ones only for genuine domain gaps. The HTML mock composes from a **per-component kit** (one token-bound partial each), so screens are consistent by construction and a semantic-token change propagates to every screen.
- **Two views of one screen** — the HTML mock is the human-facing *visible evidence*; the frozen `prototypes/<name>.json` json-render tree is the *machine-checkable* record. The confirmed layout records back to the prototype JSON + `catalog.json`.
- **Captures live in the task record** — the design-confirm captured image is **attached or mentioned in the feature's `TASK.md`** (alongside the §6 evidence), not only recorded to `prototypes/`/`catalog.json` — so the screen the human approved is traceable from the task that builds it, keeping design consistent (human steering, 2026-06-16). Owned by `capture-evidence`; design.md's beat 4 gains the same line via a coordinated reopen.
- **Glossary deltas** — `wireframe` (Stage A low-fi structural layout) · `design mock` (Stage B hi-fi self-contained HTML render) · `capture` (the real screenshot = design-confirm evidence) · `design-confirm` (the human touchpoint approving the captured image before build).

## Shared / risky contracts (freeze these first)
- **the design-definition loop contract** (the 4 beats + their order + the DDD→UDD mapping + the tool-agnostic stance) -> owning task `design-loop-guide`
- **the capture evidence contract** (artifact location + naming + "evidence not engine output" + the `check` WARN surface) -> owning task `capture-evidence`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] design-loop-guide   depends-on: none              — author `design.md`: the 4-beat loop (DDD review → reuse-first component research → wireframe → render+capture+confirm), the DDD→UDD bridge, two-stage fidelity, tool-agnostic stance; wire references from setup + specify   ✓ PASS 2026-06-16 (suite 1119 green)
- [x] wireframe-mock-recipe   depends-on: design-loop-guide   — wireframe format (Stage A) + self-contained HTML-mock recipe (Stage B) composing screens from a reusable per-component kit bound to `tokens.json` + a worked sample that renders   ✓ PASS 2026-06-16 (suite 1131 green; render + token-flip captures confirmed; +json-render fast-path)
- [x] capture-evidence   depends-on: wireframe-mock-recipe   — captured image as the design-confirm evidence artifact: location + naming + tool-agnostic recipe/default (**evaluate `@json-render/image` Satori→PNG/SVG as the earmarked named default — confirm against the tool-agnostic floor**); the image is **attached/mentioned in the feature's TASK.md**; `add.py check` never-red WARN for a prototype lacking a confirmed capture; reopen design.md beat 4 to reference the TASK.md capture   ✓ PASS 2026-06-16 (suite 1145 green; live missing_capture WARN demo; captures committed to .add/design/captures/)
- [x] book-glossary-align   depends-on: capture-evidence   — propagate to book (`docs/*`) + GLOSSARY + ×3 trees byte-identical + parity tests; glossary entries for wireframe · mock · capture · design-confirm   ✓ PASS 2026-06-16 (suite 1152 green; the loop ¶ in ch.14 + 4 glossary entries propagated byte-identical to all 4 book trees — canonical · bundled · dogfood · repo-root; new test_docs_accord cross-checks accord with design.md)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `design.md` walks the 4-beat loop and is referenced from `phases/0-setup.md` + `phases/1-specify.md`   (← design-loop-guide)  (verify: test_design_loop_guide asserts design.md names the 4 ordered beats AND grep finds a design.md reference in both phase guides across the 3 trees)  ✓ met — 12/12 green
- [x] A worked wireframe + self-contained HTML mock renders to a real image binding `tokens.json`   (← wireframe-mock-recipe)  (verify: test_wireframe_mock_recipe validates the sample HTML composes catalog components and cites tokens.json semantic aliases; manual open of the sample renders)  ✓ met — 12/12 green + headless-Chrome PNG of welcome/settings confirmed
- [x] A second screen reuses ≥1 component from the first without redefining it, and a semantic-token change re-renders both consistently   (← wireframe-mock-recipe)  (verify: test_component_reuse asserts two sample screens share ≥1 catalog component id and both resolve the same flipped semantic token)  ✓ met — token flip (#3B82F6→#16A34A) re-rendered BOTH screens in pixels
- [x] The captured image is the recorded design-confirm evidence, attached/mentioned in the feature's TASK.md; `add.py check` WARNs (never red) when a prototype has no confirmed capture   (← capture-evidence)  (verify: test_capture_evidence asserts add.py check emits a never-red missing_capture WARN for a prototype without a recorded capture AND that a captured image is referenced from TASK.md)  ✓ met — 14/14 green; live WARN fires+clears (exit 0); welcome/settings captures committed + cited in §6
- [x] Book + GLOSSARY describe the loop; the ×3 trees are byte-identical, parity tests pass, and wireframe · mock · capture · design-confirm have glossary entries   (← book-glossary-align)  (verify: test_bundle_parity and test_docs_accord green AND grep finds all 4 glossary terms in GLOSSARY.md)  ✓ met — test_docs_accord 7/7 + test_book_parity + test_bundle_parity green; ch.14 names the loop + the 4 entries (`Wireframe` · `Design mock` · `Capture` · `Design-confirm`) ship byte-identical across all 4 book trees
