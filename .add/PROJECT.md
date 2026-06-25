# PROJECT — survivor layer (cross-milestone context)

> The durable foundation that outlives every milestone and feeds context into each
> TDD⇄ADD loop. Read this FIRST in any session. Keep it lean — one screen, not a
> manual. Map to the AIDD diagram: Domain = DDD · Spec = SDD (living document) ·
> UI/UX = UDD. When a loop reveals a gap here, come back and update this file.

slug: AIDD-Book · stage: mvp · updated: 2026-06-16 · foundation-version: 50
autonomy: auto   <!-- project default — new tasks inherit this rung (manual < conservative < auto); lower a single task in its TASK.md header when it needs a human gate. -->
goal: ship ADD as a lean, trustworthy AI-driven method — any agent drives spec-and-tests-first development through the CLI alone while the human owns direction and verification — installable as @pilotspace/add / pilotspace-add, with less doc-time than GSD and no lost context across sessions

---

## Domain (DDD) — the language and the boundaries
- (DDD) "owner/assignee" (mutable, directive) is a genuinely distinct concept from the "actor stamp" (immutable, historical) even though they share the `{name,email,source}` shape — a new `source:"assigned"` value marks human-typed provenance vs git/os/override resolution (evidence: ownership-model reused the shape but needed the 4th source value to stay honest).  [folded foundation-version 43 · from ownership-model]
- (DDD) the managed↔user-data boundary is now a REUSED domain concept: heal-reconcile/global-install copy the MANAGED layer, global-data copies its COMPLEMENT (user-data) — naming the boundary once (an explicit include/exclude rule) let both sides share it (evidence: `_is_user_data` is the inverse of MANAGED).  [folded foundation-version 38 · from global-data]
- Core concepts: **task** (one feature), **milestone** (depth-bounded group of
  tasks), **phase** (specify→…→observe→done), **gate** (PASS·RISK-ACCEPTED·HARD-STOP),
  **contract** (frozen shape), **survivor layer** (durable artifacts), **stage**
  (prototype·poc·mvp·production).
- Bounded contexts / modules: **tooling** (`add.py` + `state.json` — the state
  engine), **skill** (router `SKILL.md` + on-demand `phases/*` — what Claude loads),
  **book** (`docs/*` — the trust layer users read).
- Invariants that must always hold: the `phase:` marker in TASK.md == `state.json`;
  a FROZEN contract never changes silently (change request → back to SPECIFY) — the freeze
  binds the **data/interface seam** (fields · reject codes · behavior); a **presentation/layout**
  layer iterates freely WITHOUT a re-freeze (v9: the report render re-skinned v2→v3→v4 with zero
  data-seam change); survivor files are never clobbered; writes are atomic; the skill stays lean
  (progressive disclosure) and all state lives on disk (anti-context-rot).
- **Verify re-checks the milestone's frozen exit criteria** after a task changes shape — a
  shared-contract drift turns a gate red, not slips silently to milestone close (v9 · SDD).
- **Residue** (what an evidence auto-gate must escalate to a human) is not limited to
  security·concurrency·architecture — **method/trust-layer edits are a residue category** (v6).
- **A done-tally over `state["milestones"]` has an all-archived blind spot** — every milestone archived →
  empty map → `bool(ms)` False → a cue keyed on "every milestone done" never fires. A long-lived project that
  archives finished milestones is a real path; count archived milestones toward such tallies, or document why
  not (v22 · DDD; same archive seam as graduation-analytics' traversal-basis convention).

## Spec / Living Document (SDD) — what we are building, now
- (SDD) YAML 1.1 parses a bare `on:` key as the boolean True — a workflow-shape test must read `cfg.get("on", cfg.get(True))` or it silently asserts against a missing key (evidence: the trigger test needed the True-key fallback to see the `on:` block).  [folded foundation-version 49 · from pages-deploy]
- (SDD) a frozen DESCRIPTIVE parenthetical can mis-count while the binding SEAM holds — "6 < 9" vs the true "6 < 8" (the §3 set {0,1,3,4,5,6} is unambiguous); disclose at verify, don't retro-edit the frozen contract (evidence: tests assert 6 < 8; disclosed in §6).  [folded foundation-version 48 · from fast-lane-template]
- (SDD) the suite IS the behavior contract for a prose compaction — 2 wording slips ("Tie-break order", "never the artifact") were caught only by the FULL suite, not the 33-subset (evidence: gate-on-full-suite mitigation paid off).  [folded foundation-version 46 · from skill-core-compact]
- (SDD) a new runtime dependency falsifies any "zero-dep" prose; grep + fix the claim in the SAME change (evidence: cli.js header corrected from "Zero npm dependencies"; README/GETTING-STARTED/docs grepped clean).  [folded foundation-version 38 · from installer-prompts]
- (SDD) one glossary term touches 9 files across 3 sync regimes (book ×4 · template ×3 · dogfood ×1) and must be written in EACH type's native format (appendix `**T** — d` · template/dogfood `t: d`) — parity guards catch byte-divergence but the per-type FORMAT is a manual judgment the test must pin per type (evidence: test_B2 asserts format-by-type)  [folded foundation-version 37 · from close-book-accord]
- (SDD) the wording-lint scans skill guides for bare status/process slang AND exempts code spans — the lifecycle `milestone-done → fold → compact → archive` must be backticked (as release.md does), not bare prose; a bare "fold" turned the full suite red (evidence: test_slang_absent_extended_surface term='fold' until the code-span reword)  [folded foundation-version 37 · from close-guide]
- (SDD) the domain wording-lint rejects status-name slang in new docstrings — document the grammar abstractly, not by spelling the status words (evidence: test_sync_guidelines_domain_clean failed twice before the reword)  [folded foundation-version 36 · from spec-delta-grammar]
- **decision-suggestions (decision-point UX — the guided choice): SHIPPED 2026-06-16** — every human gate now
  presents its DECISION as a **guided choice**: one highlighted ▶ recommended pick + 1–3 real described alternatives,
  so the human decides with the recommendation and each option's consequence in view, not a bare next-step line. A
  PRESENTATION layer (NO engine change — the presentation/layout layer iterates WITHOUT a re-freeze): `report-template.md`
  SPECIFIES the convention, all 8 human-gate guides (setup·contract·verify·intake·scope·close·graduate·release) CUE it,
  and the book (02-the-flow + GLOSSARY: **Guided decision** · **Recommended pick**) DESCRIBES it — pointing at
  report-template.md, never re-specifying. Carries 2 SDD lessons: a prose-convention §3 freezes a TOKEN SET + structural
  invariants (not an HTTP shape) as its checkable seam; a docs-accord task that DESCRIBES (vs specifies) verifies by
  own-entry-regex + cross-tree md5 + a points-at-source assertion, so the book stays a pointer not a second source of
  truth. [folded foundation-version 35]
- **release-altitude (the 5th scope level — RELEASE): SHIPPED 2026-06-16** — releasing is now a first-class scope
  level, ORTHOGONAL to stage: bundle ≥1 closed milestone into a versioned, watched cut. The arc
  `cue → gather → draft notes → readiness floor → human confirms → cut → watch` ships as `release.md` (guide) +
  `add.py release-report` (read-only gather, 5 record-sets) + `add.py release <version>` (guarded record-only) +
  the append-only `RELEASES.md` ledger + book ch.16 + 5 glossary entries. Attribution is RELEASES.md MEMBERSHIP
  (not a per-milestone marker), so the `→ releasable: N` cue stays read-only over compacted milestones; the
  lifecycle order is `milestone-done → fold → compact → archive → (repeat ≥1×) → release → watch`. The engine
  RECORDS; the human SHIPS (never tags/publishes/deploys). [folded foundation-version 34]
- **Additive content folds into a frozen contract with NO re-freeze (udd-design-loop · SDD):** content that removes
  no frozen §3 section and changes no reject is INSIDE the frozen contract — the "additive ⊆ frozen" judgment (the
  json-render fast-path folded into `wireframe-mock-recipe` mid-build with no re-freeze; 12 tests + parity stayed
  green), sibling to the §Domain "presentation/layout iterates freely WITHOUT a re-freeze" invariant. And a frozen
  DESCRIPTIVE annotation can be wrong while the binding SEAM holds (§3 read a wording-lint count "25→26"; the real
  base was 26→27 — the binding rule, design.md increments the guard by one + both guards update, held): honor the
  seam, disclose the stale integer at the verify gate, never silently retrofit. [folded foundation-version 33]
- **foundation-compaction (all 4 foundation specs shrink — newest-first + per-spec settled lines): SHIPPED 2026-06-15** —
  every append-only foundation sequence now reads NEWEST-FIRST (newest record on top) and, at milestone close, collapses its
  stable shipped zero-residue tail into ONE per-spec **rolled-up settled line** at the bottom (summarize + a `see git` pointer,
  NEVER delete; every OPEN residue stays live). One shared eligibility rule (shipped + zero open residues) drives a PER-SEQUENCE
  predicate, not a single global cutoff (§Spec keys on un-fv-stamped prose · §Key-Decisions on date · learnings on max-foundation-version)
  and a PER-SPEC rolled-line dialect, not one generalized shape; newest-first ordering + compaction are ONE invariant amendment
  (newest on top, settled tail at the bottom — collapse upward), not two themes. Reject codes open-residue-version · trail-loss ·
  wrong-order. Dogfooded on the LIVE specs with ZERO data loss, refute-verified against git: PROJECT.md 399→215, CONVENTIONS.md
  689→360 (foundation 1088→575, −47%). Convention-guided — there is deliberately no `add.py` command for the ritual (read
  `compact-foundation.md`); distinct from the engine `add.py compact <slug>` (the archive recovery-bundle move). [folded foundation-version 31]
- **next-step-seams (Engine next-step footer + driver marker): SHIPPED 2026-06-12** — every COMPLETING mutating
  verb now prints one engine-sourced `next:` footer (Arm A: in-flight task → phase command; Arm B: state-arm decide)
  from a SINGLE resolver `_next_footer`; bespoke ad-hoc tails converged (no double-print). The driver marker
  `[you drive]` / `[human gate]` fills the reserved trailing slot from a single `_driver_stop` resolver (autonomy
  × phase, one refinement: verify reads the dial; every other phase reads `_phase_owner` structurally). The frozen
  machine-state-json `stop` (cmd_guide JSON) is UNTOUCHED — the marker lives on the footer + guide TEXT only
  (Option F; residue: guide-TEXT vs JSON diverge at verify-auto, deferred as a deliberate change-request for the
  machine-state-json contract). SDD learning: a verb-set contract must name the verb CLASS (workflow vs setup vs
  control) and pre-map frozen tests before broadening — "every mutating verb" over-reached init, surfacing only at
  full-suite run. [folded foundation-version 29]
- **verify-integrity (Prove the green was EARNED, not gamed): SHIPPED 2026-06-11** — the verify gate now carries a
  two-layer anti-cheat + a bounded self-heal. Layer 1: a MECHANICAL tamper-tripwire snapshots md5(red test paths + §3
  contract) at tests→build and re-checks at the verify gate — any edit since the red run blocks an auto-PASS. Layer 2:
  the earned-green rubric scores the judgment cheats (overfit · vacuous · stubbed-away) by an INDEPENDENT adversarial
  refute-read (a subagent recommended under `auto`; the engine never spawns it — tool-agnostic). A confirmed cheat
  (either layer) returns to BUILD for ≤3 honest re-builds, monotonically, then HARD-STOPs to the human; a gamed green is
  never auto-passed and never RISK-ACCEPTED-waived (HARD-STOP-class, like security). Engine pin bumped
  a6eed5e0→7b05eaf9 ×3 trees. The milestone validated BOTH gate paths in one run (task 1 human-gated · task 2
  auto-resolved · task 3 human-gated — the autonomy ladder discriminates by risk, not ceremony) and exercised the
  live-dogfood re-anchor path (a task that crossed tests→build under the OLD engine re-snapshots under the NEW via
  `phase tests`+`advance`; `reopen` works only on done tasks). [folded foundation-version 27]
- **ground-context (Ground gathers the whole working folder, efficiently): SHIPPED 2026-06-11** — the §0 GROUND
  gather now spans the working folder, not only code: docs/textbase · TODOs · config/manifests · data/fixtures
  (task-delta only). `0-ground.md` also gained a gather-METHOD hint — sweep the broad pass cheaply (a small-model
  subagent / fast index / skim) then DEEPEN task-specifically, a recommendation the engine never spawns
  (tool-agnostic; `add.py` byte-identical to `engine_pin` throughout). Closed the fv25 honest ceiling: the first
  lived ground run (a task created AT `ground`) reached `grounded ✓`. Additive prose/template only — the §0
  anchors-keyed grounding measure is unchanged. [folded foundation-version 26]
- **ground-phase (Ground phase — build against the real codebase): SHIPPED 2026-06-11** — the task ladder gained
  a **phase-0 `ground` preamble** before specify (`PHASES` now 9: ground→…→done; the seven steps specify→observe
  keep their §1–§7 brand). `ground` is **AI-owned, NO new human gate** (the one approval stays at the §3 freeze);
  `new-task` starts at `ground`, `advance` hops ground→specify. Each task carries a `## 0 · GROUND` map (real
  files/symbols/conventions + the anchors §3 cites); `add.py status`/`check` SURFACE the grounding state (a
  human-readable line + a never-red WARN — measure, never block). Additive to the frozen 7-step task flow: the
  seven steps' numbering + gate are unchanged, ground rides in front. Grounding INFORMS the contract, never
  authors it. Honest ceiling: shipped with ZERO lived runs starting at ground (all 3 tasks grandfathered at
  specify; §0 retrofitted at build) — first lived run is next-milestone. [folded foundation-version 25]
- goal-auto-ready (autonomy earned by goal-clarity): **SHIPPED 2026-06-10** — two halves of one lever.
  (1) A project-level `autonomy: auto` default written to PROJECT.md at init, inherited by `new-task`,
  fail-SAFE (`_project_autonomy`: absent→auto, garbled→conservative), surfaced in `status`. (2) The
  **auto-ready-goal** check: a milestone goal is auto-ready iff its `## Exit criteria` has ≥1 criterion
  AND every one cites a verifier `(verify: <test|command|metric>)`; `cmd_check` WARNs `goal_not_auto_ready`
  (NEVER red, the OPEN active milestone only — done/archived never retro-flagged), `cmd_status` prints a
  `goal-ready:` line, the term is named ×3 (GLOSSARY + book + skill). Surface-only by design: the freeze
  gate, the per-task autonomy contract, and `milestone_goal_unmet` are UNCHANGED. add.py ×3 byte-identical
  (re-pinned 70d779c4); 747 tests. **OPEN (SDD forward-question):** an `init --autonomy <level>` knob (a
  non-auto project default at init) was DEFERRED as YAGNI — recorded so a future "configurable default"
  need is not re-discovered from scratch. The deferred SPINE decision (can an auto-ready goal RELAX the
  freeze gate / wire not-auto-ready → lowered autonomy) is its own later milestone, not this one's deliverable.
  [folded foundation-version 24]
- flag-first-freeze (Flag-first freeze + explicit autonomy level): **SHIPPED 2026-06-10** — two fail-closed
  guards on the freeze/autonomy seam: (1) the lowest-confidence flag is MECHANICALLY required at every freeze
  (`unflagged_freeze`, fail-closed — advance refuses + audit verifies via a verified-marker on the guarded
  crossing); (2) the per-task autonomy header is an explicit ordered 3-mode LEVEL — `autonomy: manual |
  conservative | auto`, the high-risk guard widened to refuse any UN-lowered rung, `cmd_status` surfaces the
  active level, `cmd_check` reds `unknown_autonomy_level` + WARNs live-only `implicit_autonomy`, seed default
  `auto`. add.py ×3 byte-identical (re-pinned c0c9329c); prose ≡ enforcement pinned across GLOSSARY + book
  (appendix-c · 10-setup · 11-governance) + skill (run.md · streams.md · SKILL.md). 717 tests.
  [folded foundation-version 23]
- v23 (Decision-point transparency — the decision arc): **SHIPPED 2026-06-09** — every human decision gate now
  opens its synthesized report with the **decision arc**: `goal:` (the milestone goal) · `done:` (achievement —
  the proven progress) · `plan:` (what's next), rendered first above the five report blocks, engine-sourced,
  presentation-only (never a new gate / never changes a PASS·RISK-ACCEPTED·HARD-STOP). Wired into all seven gate
  guides (lock·freeze·verify·intake·scope·close·graduation) + the reconcile rule (FLAGS must match `report --decide`'s
  count); the book + GLOSSARY describe it. 691 tests; book ×4 byte-identical. **OPEN (SDD forward-question):** the
  seven gates may be incomplete — `fold.md`'s consolidation-confirm (the human approves a fold, the AI never
  self-approves) is a candidate 8th human decision point the arc could serve; weigh in a future milestone.
  [folded foundation-version 22]
- v22 (Stage graduation — the 4th scope level): **SHIPPED** — `mvp→production` becomes an analytics-driven,
  interview-led, human-confirmed roadmap, never a label flip: `graduation-report` clusters five MVP record-sets
  (gather-not-judge) · `graduate.md` orchestrates cue→interview→draft≥1 production milestone→confirm→flip ·
  `stage production` is guarded (`stage_no_roadmap`, a tally not a readiness verdict; `--force` + `init --stage`
  are the named at-creation doors) · `stage-goal-criteria` (the human's `[x]` "mvp covered" checklist). SDD
  learnings carried to CONVENTIONS (how-we-author): guarded-transition-names-its-door · data-shape-bounded-clause-
  names-its-trigger · contract-freeze-cross-checks-the-prior-frozen-seam. [folded foundation-version 22]
- v21 (Foundations & Lineage / grounding): **SHIPPED 2026-06-08** — the book gains a references appendix (27
  grouped, verified sources, a "how ADD relates" line each + a spec-kit↔ADD phase table), a "Foundations &
  Lineage" chapter, and inline citations woven into 02/03/09, all ×4 byte-identical. Three SDD learnings: a
  survey/lineage chapter's natural citation density is NEAR-COMPLETE (26/27, each load-bearing), not the sparse
  "subset" a spec instinctively pictures — spec a survey as near-full coverage; and the cross-task-finding path
  is the recorded `reopen` — a defect found while working task N in an already-done task M is fixed by `reopen M`
  (recorded, gate reset), never a silent out-of-scope edit (validated: inline-citations → reopen foundations-chapter
  to reframe the [Yuan et al. 2024] framing). OPEN: the cite-key suffix-assignment order (2025a/b/c) is
  deterministic-by-appendix-reading-order but undocumented in appendix-g "How to cite" — a one-line note hardens
  it (deferred, a doc touch for a future appendix milestone). [folded foundation-version 21]
- settled fv1–fv20 — ADD bootstrapping → production-ready: SDD foundation · self-driving run · one-approval auto · awareness surface · decision-point reports · zero-command on-ramp · prompt & file hygiene · dynamic loop (see git)

## Users (UDD) — UI/UX: design before code
- (UDD) keeping the site home OUT of the book (README→index.html via MkDocs default) is the lean choice for a book whose source is mirror-guarded — it adds zero new file, zero bundle/parity work, and the existing README already carries an intro + linked TOC that makes a good landing (evidence: human chose it over a new index.md; strict build confirmed README is the site root).  [folded foundation-version 49 · from site-scaffold]
<!-- No-UI project: ADD ships as a CLI + a Claude skill. The "interface" is the
     command surface and the text it prints — there is no screen, so this stays short. -->
- **The UDD design-definition loop SHIPPED end-to-end (udd-design-loop · UDD):** the loop
  (`review-domain → research-components → wireframe → render-capture-confirm`) now lives where a PERSON learns ADD —
  book ch.14 + GLOSSARY (`wireframe` · `design mock` · `capture` · `design-confirm`) — not only in the agent's
  `design.md` guide. **Capture is measure-never-block**: the engine raises a never-red `missing_capture` WARN and
  NEVER renders; the captured image is design-confirm evidence committed at `.add/design/captures/<name>.<ext>` AND
  cited in the feature's `TASK.md` (traceability). **Two render tiers**: a zero-dependency HTML+CSS floor (any stack,
  any screenshotter) + a json-render fast-path (`prototypes/<name>.json` IS a json-render `Spec`; `@json-render/image`
  = deterministic Satori→PNG/SVG capture, no browser). Consistency-by-construction is demonstrable (one
  semantic-token flip re-rendered both sample screens identically). Built-for-downstream ceiling reaffirmed — ADD is
  CLI/no-UI, so the loop is validated by shape-lint + the design.md content, not a live ADD screen.
  [udd-design-loop (4 tasks) — folded foundation-version 33]
- **Setup SUGGESTS, never interrogates**: after the brownfield scan / greenfield interview, setup proposes
  the first milestone (goal + flow + scenarios) for the human to react to, and surfaces the run-mode as a
  comparison table + confirm-to-keep default — show-before-ask at the foundation altitude, not a questionnaire.
  [setup-run-mode + setup-suggest-milestone — folded foundation-version 32]
- Primary users & jobs: the author (MRQ maintainer) shipping ADD as a product;
  **AI agents** that load the skill; **developers** adopting ADD who must
  read/trust/follow the method.
- The interface (no GUI): the `add.py` command surface + `npx @pilotspace/add`, and the text
  they print. Core flow: `init` → fill foundation → `new-task` → run the loop →
  `verify`/gate → resume any session with `status`.
- "UI states" for a CLI = output states: a clear success line, an empty/idle state
  (nothing to do), and actionable errors with named exit codes — never a bare trace.
- **TUI rendering house rule (no `wcwidth`/`rich`, stdlib-only)**: carry richness on
  width-neutral channels (color on a tty only, honoring `NO_COLOR`/`TERM`); put only ASCII-safe
  text in `len()`-aligned columns; confine Unicode glyphs to line-END or non-aligned row STARTs
  (bullets). Two glyph tiers (Unicode/ASCII) chosen by stdout encoding/`--plain`. The persisted
  render is PLAIN + fixed-width (canonical); color/adaptive-width are a tty-only skin (v9 · UDD).
- **Two render idioms, chosen by PURPOSE (v9-1 · UDD)**: a ROLLUP (`report <m>`) is a scannable
  digest — collapse prose, fit `len()`-aligned columns. A DRILL (`report <task>`) is a READ surface
  where line-structure (scenarios, contract code) carries meaning — preserve physical lines + each
  line's indent, soft-wrap only over-long lines, never clip. Don't force one renderer's rules on
  the other; the shared frozen thing is the DATA seam, not the layout.
- Design source of truth: the skill prose (`SKILL.md` + `phases/*`) and the book.
- What "good" feels like: never lose context across sessions; less doc time than GSD;
  one command to know "where am I and what's next".
- Empty-project `status` now prints a **first-run panel** (`/add` + `new-task` escape hatch) —
  the worst-lost moment (a brand-new project) is actionable, not a bare line (v7/onboarding-align).
- ADDRESSED (UDD, 2026-06-02): the one-approval rubber-stamp risk is met by **co-specification's
  least-sure flag** — the AI ranks the 1–2 most-likely-wrong points bundle-wide and leads the
  single approval with them, instead of a flat all-`[x]` assumptions wall. Deliberately NOT a
  front-checklist (that would re-add the ceremony ADD avoids). Honest residual: the flag aims the
  review but cannot *force* engagement; true enforcement waits on a CI checker (prose ≠ enforcement).
  The reform reaches the **operational artifact**, not only the book: `new-task` now scaffolds the
  ranked least-sure §1 (`templates/TASK.md.tmpl` + the `_FALLBACK_TASK` circuit breaker), pinned by
  `test_cospecify_scaffold.py` so it cannot regress to the flat confirm-list that originally exposed it.
- **One next step at the most-lost moment (v12-1 · UDD):** when the user is most lost (unlocked setup,
  empty project), status must show exactly ONE next move — competing hints dilute the only correct
  action. The unlocked window now replaces the generic resume//add hint with the single review→lock step.
- **A review prompt lives AT the seam (v14 · UDD):** put the checklist where the decision already
  happens, sized to the reviewer's real attention (one minute · six lines · ⚠-first) — a separate
  review artifact is ceremony that competes with the decision instead of aiming it.
- **Precise promises beat catchy absolutes (v15 · UDD):** "zero-command" survived contact with the
  rewrite only as "one **shell** command" — `/add` is still typed. A headline that the product can't
  literally keep erodes trust; name the exact, honest boundary (the install is the one command; the
  loop after it is conversational) rather than the slogan.
- **Leanness is a UX constraint on a dual-audience prose file (v16 · UDD):** a prompt file is read by BOTH
  the agent and a human, so over-tagging hurts the human reader — a markup convention's vocabulary is sized
  for readability, not only correctness. v16 drove the scheme from a field-level tagging down to 5 BLOCK-level
  tags (tags mark block boundaries only; skeleton labels like `Role:`/`Never:` stay plain text) precisely to
  keep the prose scannable; and on a RENDERED page (appendix-b) the tag wraps an intact code fence so the page
  still renders verbatim — the reader's experience, not just the agent's parse, set the layout.
- **The goal-gate prevents theater only if the human writes REAL, checkable exit-criteria lines (v20 · UDD):**
  a box checked without a real goal behind it is goal-met theater — the same failure mode the method warns about
  for an unearned `gate=PASS`. The engine reads the [x]/[ ] tally; it cannot judge whether the box was earned, so
  the trust model is human discipline (surfaced in `loop.md`). v20's own close dogfooded it: each of the 4 exit
  criteria mapped to a done+PASS task with observable proof BEFORE the boxes were checked.
- **The dogfood book copy `.add/docs/` can drift silently — it is gitignored and outside `test_bundle_parity`
  (v21 · UDD):** parity guards canonical↔`_bundled` only, so the dogfood install tree is unprotected; its README
  carried pre-existing drift (a missing ch.14 line) found only while wiring ch.15. Accept it as a known-throwaway
  install artifact (regenerated on install) OR extend a parity check to the dogfood README — for now named as a
  known gap, not silently trusted. [folded foundation-version 21]
- **Identity values are human-owned — SETTLED (udd-design-foundation · UDD):** design tokens (brand color,
  palette, type) are surfaced AT specify for the human to fill; the AI never auto-picks from a menu. DESIGN.md is
  the prose FRONT-DOOR that binds the named-set JSON (tokens · catalog · prototypes) the AI drafts UI from; its
  identity section ships as HTML-comment PROMPTS, never pre-filled values (`identity_prefilled` guard enforces
  both halves). The human adding a SCREENS section at the freeze confirmed DESIGN.md also doubles as the
  per-screen `prototypes/<name>.json` index — a shape worth defaulting into the template. [folded foundation-version 29]
- **UDD forward gaps (udd-design-foundation · UDD):** (a) DTCG `$type`-inheritance: a cross-file resolver
  must treat "resolved `$type` ∉ valid set" as the upstream token-schema validator's concern, never re-flag it —
  the `got ∉ _TOKEN_TYPES` skip-guard is the settled boundary. (b) Compact-dialect value-form STRICTNESS has
  three under-pinned spots (`fontWeight` any string · weight floats like `700.0` rejected · negative dimensions
  like `"-16px"` pass) — defensible for MVP but a real renderer would reject some; tighten in a follow-up task
  when real token files hit them. (c) The `GOAL_UNSET` sentinel text is slightly stale: an empty `goal:` line
  now EXISTS post-init, so the text should say "fill in the goal: value" not "add a goal: line" — a deferred
  wording-only fix. (d) `_section0_anchors` registers grounding only from INLINE content on the Anchors line,
  not a bulleted list below it — either teach the parser the list form or make the inline-only shape explicit in
  the guide; this is a RECORDED KNOWN GAP, deferred to a future engine task. [folded foundation-version 29]
- **The ubiquitous-language ban is PROSE-ONLY (foundation-compaction · UDD):** a banned term survives inside a `code span`
  or a fenced block — so a user-facing guide references doc/machine names as code-spans (`fold.md`, `folded`) and uses the
  domain terms in prose ("retrospective consolidation", "foundation spec"), never the bare slang. The readable surface stays
  on-vocabulary without losing the precise file/machine names. [folded foundation-version 31]

## Key Decisions (append-only — newest-first; compaction door per compact-foundation.md)
| date | decision | why | outcome |
|------|----------|-----|---------|
| 2026-06-25 | fold all → foundation-version 50 (TDD 1 · ADD 3) | consolidate captured OBSERVE lessons into the versioned foundation | 4 lessons open→folded; +4 routed bullets; 49→50 |
| 2026-06-24 | fold all → foundation-version 49 (SDD 1 · UDD 1 · TDD 2 · ADD 2) | consolidate captured OBSERVE lessons into the versioned foundation | 6 lessons open→folded; +6 routed bullets; 48→49 |
| 2026-06-23 | fold all → foundation-version 48 (SDD 1 · ADD 2) | consolidate captured OBSERVE lessons into the versioned foundation | 3 lessons open→folded; +3 routed bullets; 47→48 |
| 2026-06-23 | fold all → foundation-version 47 (ADD 4) | consolidate captured OBSERVE lessons into the versioned foundation | 4 lessons open→folded; +4 routed bullets; 46→47 |
| 2026-06-23 | fold all → foundation-version 46 (SDD 1 · ADD 4) | consolidate captured OBSERVE lessons into the versioned foundation | 5 lessons open→folded; +5 routed bullets; 45→46 |
| 2026-06-22 | fold all → foundation-version 45 (TDD 3 · ADD 3) | consolidate captured OBSERVE lessons into the versioned foundation | 6 lessons open→folded; +6 routed bullets; 44→45 |
| 2026-06-22 | fold all → foundation-version 44 (TDD 2 · ADD 2) | consolidate captured OBSERVE lessons into the versioned foundation | 4 lessons open→folded; +4 routed bullets; 43→44 |
| 2026-06-22 | fold all → foundation-version 43 (DDD 1 · TDD 1 · ADD 1) | consolidate captured OBSERVE lessons into the versioned foundation | 3 lessons open→folded; +3 routed bullets; 42→43 |
| 2026-06-22 | fold all → foundation-version 42 (ADD 3) | consolidate captured OBSERVE lessons into the versioned foundation | 3 lessons open→folded; +3 routed bullets; 41→42 |
| 2026-06-22 | fold all → foundation-version 41 (TDD 3 · ADD 5) | consolidate captured OBSERVE lessons into the versioned foundation | 8 lessons open→folded; +8 routed bullets; 40→41 |
| 2026-06-18 | fold --task pty-clack-harness → foundation-version 40 (TDD 2 · ADD 3) | consolidate captured OBSERVE lessons into the versioned foundation | 5 lessons open→folded; +5 routed bullets; 39→40 |
| 2026-06-18 | fold all → foundation-version 39 (TDD 1 · ADD 1) | consolidate captured OBSERVE lessons into the versioned foundation | 2 lessons open→folded; +2 routed bullets; 38→39 |
| 2026-06-17 | fold all → foundation-version 38 (DDD 1 · SDD 1 · TDD 5 · ADD 8) | consolidate captured OBSERVE lessons into the versioned foundation | 15 lessons open→folded; +15 routed bullets; 37→38 |
| 2026-06-17 | fold all → foundation-version 37 (SDD 2 · TDD 1 · ADD 4) | consolidate captured OBSERVE lessons into the versioned foundation | 7 lessons open→folded; +7 routed bullets; 36→37 |
| 2026-06-17 | fold all → foundation-version 36 (SDD 1 · TDD 3 · ADD 6) | consolidate captured OBSERVE lessons into the versioned foundation | 10 lessons open→folded; +10 routed bullets; 35→36 |
| 2026-06-16 | ship decision-suggestions + fold → foundation-version 35 (10 open deltas from 3 tasks — SDD 3 · TDD 2 · ADD 5; consolidated into 4 new bullets — 1 §Spec decision-suggestions ship bullet carrying the 2 SDD lessons (prose-convention-§3-freezes-a-token-set · docs-accord-describes-by-own-entry-regex+md5+points-at-source) + 3 CONVENTIONS (ADD presentation-convention-ships-as-a-trail+dogfoods-its-own-gates · ADD discriminate-autonomy-by-change-type · TDD prose-red-suite-splits+closing-tag-lint+climb-token-scope); the §5 repo-root scope-token bug reaffirms the fv29 §5-scope-frozen-at-tests→build convention) — every human gate now renders its DECISION as a guided choice (▶ recommended pick + 1–3 described alternatives): report-template.md specifies · 8 guides cue · book+GLOSSARY describe; NO engine change | the human asked to highlight a suggestion + short description at every gate — the convention makes the recommendation + consequences visible instead of a bare next-step line, dogfooding ADD's own presentation layer (it even rendered its own freeze/verify/close gates as guided choices); consolidate-don't-append (10→4) keeps the foundation one-screen | decision-suggestions SHIPPED 3/3 tasks, 3/3 criteria, 3 PASS (suggestion-block risk:high conservative · gate-wiring + suggest-book-align auto); +1 §Spec +3 CONVENTIONS; 34→35; all 10 deltas open→folded; report-template.md + engine add.py byte-unchanged; full suite 1158 green; verify caught a real §5 scope-token bug (bare filename vs `add-method/..` climb), fixed by re-crossing tests→build; commits a378d2e (report-template) · 450483e (8 guides) · <task-3 book> on feat/decision-suggestions |
| 2026-06-16 | ship release-altitude + fold → foundation-version 34 (17 open deltas from 4 tasks — SDD 2 · TDD 5 · ADD 10; consolidated into 5 new bullets — 4 CONVENTIONS (release-engine-records-only-security-un-forceable · two-wording-fences+per-line-code-span · subcommand-census-self-maintains · appended-chapter-chains-forward-only) + 1 TDD CONVENTIONS (release/docs-guard-patterns) — + 1 §Spec release-altitude ship bullet carrying the 2 SDD lessons (RELEASES.md-membership attribution + the wrapped-backtick-arc hazard); the §5-scope-anchor-at-tests→build delta reaffirms the fv29 convention) — RELEASE is now a first-class 5th scope level: `release.md` + `add.py release-report` + `add.py release` (guarded record-only, security un-forceable) + `RELEASES.md` ledger + book ch.16 + 5 glossary entries | the milestone closed the gap the human named (ADD formalized building/looping/graduating but never the act of SHIPPING a version — which the repo proved real by doing it by hand every release); engine records / human ships keeps the tag/publish/deploy human-owned + tool-agnostic; consolidate-don't-append (17→5) keeps the foundation one-screen | release-altitude SHIPPED 4/4 tasks, 4/4 criteria, 4 PASS (release-command risk:high · all conservative · human-gated); +5 CONVENTIONS +1 §Spec ship bullet; 33→34; all 17 deltas open→folded; NO engine change in task 4 (engine md5 unchanged since 9c479010); full suite 1158 green; commits b098b66 (guide) · 6fe347c (report) · a3beccd (command) · <task-4 docs> on feat/release-altitude |
| 2026-06-16 | ship udd-design-loop + fold → foundation-version 33 (19 open deltas from 4 tasks — SDD 2 · UDD 7 · TDD 4 · ADD 6; consolidated into 5 new bullets — §Users UDD design-loop-shipped · §Spec additive-⊆-frozen · 3 CONVENTIONS (docs-guard-cross-checks-source · tool-cache-outside-scope-exclude · release-pin-migration-same-commit) — + 6 flip-cite reaffirmations: §5-scope-before-crossing ×2 · dogfood-at-own-gate · engine-pin-3-parts · vacuous-substring-matcher · built-for-downstream) — the UDD design-definition loop (review-domain → research-components → wireframe → render-capture-confirm) now ships end-to-end: design.md guide + udd-wireframe.md recipe + capture-evidence `missing_capture` WARN + the loop described in the book ch.14 + GLOSSARY | the milestone closed the gap the human named (abstract token/catalog/prototype JSON had no VISIBLE layout to confirm before build) — a UI project's design now starts from the domain, researches+reuses components, and the human confirms a REAL captured image before build; consolidate-don't-append (19→5) keeps the foundation one-screen | udd-design-loop SHIPPED 4/4 tasks, 5/5 criteria, 4 PASS (all risk:high · conservative · human-gated); +1 §Users +1 §Spec +3 CONVENTIONS; 32→33; all 19 deltas open→folded; new test_docs_accord (7) + the release-gate migration to test_release_1_5_0; full suite 1152 green; commits bc5ac7f (task 4) · d8bc376 (release-gate) on release/v1.5.0 |
| 2026-06-15 | ship v13-onboarding-polish + fold → foundation-version 32 (16 open deltas from 7 tasks — SDD 1 · UDD 1 · TDD 4 · ADD 10; merged into 7 new CONVENTIONS bullets + 1 §Users line) — setup now proposes run-mode + first milestone + per-drive domain deep-dive; `add.py waves` schedules the dependency DAG; and SOUL.md ("Trusting") + soul.md give the AI a human-owned, self-improving voice | the milestone made onboarding guided/self-tuning and gave the method its first VOICE loop; consolidate-don't-append (16→8) keeps the foundation lean; the SOUL.md voice ships as a human-owned PROPOSED starter (gate attests mechanism, human keeps voice) | v13 SHIPPED 6/6 tasks, 7/7 criteria, 6 PASS; +7 CONVENTIONS bullets; §Users suggest-not-interrogate line; 31→32; all 16 deltas open→folded; engine eebbb443→6c5ba081 (SOUL.md scaffold); full suite 1095 green; commits 372c74c · 44e401c · 3fe97af |
| 2026-06-15 | ship foundation-compaction + fold → foundation-version 31 (19 open deltas from 6 tasks — SDD 4 · UDD 1 · TDD 6 · ADD 8, incl. 2 carried from gitignore-scaffold; aggressively merged into 1 §Spec ship bullet + 1 §Users prose-only-ban line + 6 new CONVENTIONS bullets + 3 flip-cites) — all four foundation specs now read NEWEST-FIRST and collapse their stable shipped zero-residue tail into a per-spec rolled-up settled line (summarize + `see git`, never delete; OPEN residue stays live); convention-guided (no `add.py` command) | the foundation grows past v30 and must stay relevant-first + one-screen — this milestone re-ordered every append-only sequence newest-first, added the compaction door, and dogfooded it on the LIVE specs with zero loss | foundation-compaction SHIPPED 5/5 tasks, 6/6 exit criteria; +6 CONVENTIONS +3 flip-cites; §Spec ship bullet; §Users prose-only-ban line; 30→31; all 19 deltas open→folded; build committed c93e41e |
| 2026-06-14 | ship advisor-context + fold → foundation-version 30 (4 open deltas from 2 tasks: SDD 1 · TDD 1 · ADD 2; merged into 3 CONVENTIONS bullets) — every ADD step now carries a THIN Advisor·Confidence hook pointing to two new shared engine docs: `advisor.md` (when/how to spawn one plan-following subagent, vendor-neutral) + `confidence.md` (advisory 0–1 six-dimension self-score, refine-if-<0.9, never a gate) | the subagent-spawn pattern was scattered (ground sweep · verify refuter · streams adapter) and the self-score lived only in the streams worker prompt; promote both into first-class per-step guidance so any agent driving the loop knows when to delegate and how to self-assess — engine still never spawns, score never gates | advisor-context SHIPPED 3/3 tasks, 5/5 criteria; 3 new guards (test_confidence_rubric · test_advisor_strategy · test_per_step_hooks) + xml_convention ENGINE_FILES & wording_lint COUNT 22→24; +3 CONVENTIONS bullets (new-engine-doc-trips-inventory-guards · enumerate-full-set+distinctness · build-in-build+thin-pointer); 29→30; all 4 deltas open→folded |
| 2026-06-13 | fold udd-design-foundation learnings → foundation-version 29 (41 open deltas from 10 tasks: SDD 9 · UDD 6 · TDD 12 · ADD 14; merged into ~14 foundation additions — 8 new CONVENTIONS bullets · 1 §Spec next-step-seams ship bullet · 2 §Users bullets (identity-settled + UDD-forward-gaps) · 1 CARRY-FORWARD known-gap recorded in §Users) | human-confirmed fold of the udd-design-foundation milestone's full OBSERVE backlog; aggressively merged (41→14) to keep the foundation lean; one ADD carry-forward (active_milestone re-aim) recorded as a known-gap engine task, still flipped folded | 8 new CONVENTIONS bullets (contract-completeness-3-checks · verb-set-broadening-names-class · adversarial-refute-conformant-happy-path · string-presence-under-enforces · engine-pin-3-mandatory-parts · mid-build-CR-trips-tamper · §5-scope-frozen-at-tests-build · state-create-needs-remove+shared-cap); §Spec next-step-seams bullet; §Users identity-settled + UDD-forward-gaps; 28→29; all 41 deltas open→folded |
| 2026-06-12 | fold engine-hardening + wave learnings → foundation-version 28 (11 open deltas: 9 new CONVENTIONS bullets — hand-written-input-parsing-discipline (2 SDD merged: exactly-one-match + terminator-explicit) · name-enforcement-deferral-at-freeze · coverage-gaps-route-as-deltas · grammar-drift-fixtures · token-presence+mirror-parity · sandbox-only-mutating-probes · close-gap-before-gate · mirror-folded-exceptions · shifts-never-skips — · 1 flip-cite onto mechanical-HARD-STOP+monotonic-cap) | human-gated fold after the engine-hardening ground tasks (argv-portability PASS auto-resolved · merge-base-enforcement PASS human-gated after 7 refute passes, 4 human-approved contract versions, 2 heal_exhausted HARD-STOPs — the fv27 mechanical guard's first live fire, held both times); all 11 confirmed (none rejected) | +9 CONVENTIONS +1 flip-cite; 27→28; 11 deltas open→folded; engine b441421c ×3; PR #8 |
| 2026-06-11 | ship verify-integrity + fold → foundation-version 27 (16 open deltas: 5 new CONVENTIONS bullets — floor+ceiling+HARD-STOP-class · mechanical-HARD-STOP-pattern+monotonic-cap · evolution-not-weakening-discriminator · security-line-emerges-at-build · two-how-we-author — · 3 flip-cites onto dogfood-at-own-gate / presence-necessary-not-sufficient / prose-guide-red→green · 1 §Spec verify-integrity ship bullet carrying both-gate-paths + live-re-snapshot) | human-gated fold at verify-integrity close (3/3 tasks, 3/3 criteria); the method's FIRST mechanically-enforced HARD-STOP shipped and dogfooded its own earned-green rubric on its own build (independent refute-read returned EARNED, one nit fixed pre-gate); all 16 confirmed (none rejected) | +5 CONVENTIONS +3 flip-cites; §Spec verify-integrity bullet; 26→27; 16 deltas open→folded; engine 7b05eaf9 ×3 |
| 2026-06-11 | fold ground-context learnings → foundation-version 26 (9 open deltas: 4 new CONVENTIONS bullets — ground-two-axes-completeness+economics · capability-as-prose-recommendation-engine-tool-agnostic · dogfood-technique-in-flight · prose-feature-red-greenable-by-token-presence — · 2 flip-cites onto fv25 bullets — additive-byte-invisible template-twin · grandfather-ceiling CLOSED — · 1 §Spec ground-context ship bullet; δ6 self-closed within-milestone, task 2 reworded the intro it flagged) | human-gated fold at ground-context close (2/2 tasks, 2/2 criteria); the milestone dogfooded its own technique in-flight (haiku subagent broad sweep · main-context deepen) and closed the fv25 zero-lived-run ceiling in real time | +4 CONVENTIONS +2 flip-cites; §Spec ground-context bullet; 25→26; 9 deltas open→folded (incl. δ6 self-closed); engine e6b8c3da ×3 unchanged (prose/template only) |
| 2026-06-11 | fold ground-phase learnings → foundation-version 25 (12 open deltas: 5 new CONVENTIONS bullets — ground-before-§3 · ordered-constant-index-hazard · additive-surface-byte-invisible · engine-derived-prose-guard · grandfather-retrofit-ceiling — · 1 flip-cite onto four-mirror-trees · 1 §Spec ground-phase ship bullet) | human-gated fold at ground-phase close (3/3 tasks, 3/3 criteria); the milestone's own theme dogfooded — grounding §3 in the real engine pre-caught 4 defects, and the phase shipped with zero LIVED runs (all 3 tasks grandfathered at specify, §0 retrofitted at build — honest ceiling, not papered) | +5 CONVENTIONS +1 flip-cite; §Spec ground-phase ship bullet + the 7-step frozen-line parenthetical; 24→25; 12 deltas open→folded; engine e6b8c3da ×3 (unchanged this milestone — prose/template only) |
| 2026-06-10 | ship goal-auto-ready + fold → foundation-version 24 (7 deltas: 3 new CONVENTIONS bullets — anchor-declaration-token-reader · live-only-guard-keys-on-terminal-status · lint-forces-a-slot-not-honesty — · 1 frozen-guard→fix-build flip-cite · 1 §Spec ship bullet carrying 2 SDD; the OSError-guard divergence on `_exit_criteria_cited` recorded as an ACCEPTED CEILING, not hardened in isolation — it mirrors the sibling `_exit_criteria` convention) | human-gated fold at goal-auto-ready close (2/2 tasks, 3/3 criteria); the verify adversarial pass caught its own Must #4 gap (the live-only WARN fired on a done-but-not-yet-archived milestone), closed test-first before the gate (close-gap-before-gate); all 7 confirmed (none rejected) | +3 CONVENTIONS +1 flip-cite; §Spec goal-auto-ready bullet (auto default + auto-ready-goal check, --autonomy knob deferred OPEN, spine decision deferred); 23→24; 7 deltas open→folded; engine 70d779c4 ×3 |
| 2026-06-10 | ship flag-first-freeze + fold → foundation-version 23 (4 deltas: 2 new CONVENTIONS bullets — verified-marker-scopes-forward · prose-accord-pins-every-surface+word-ban-blind — · 1 cross-surface-term flip-cite · 1 §Spec ship bullet) | human-gated fold at flag-first-freeze close; the milestone's own theme (a guard with mechanical teeth) caught its own gap — DocsAccordTest pinned 1 of 4 named surfaces, surfaced by human review at the verify gate not CI; MILESTONE.md was a never-authored stub, back-filled at close | +2 CONVENTIONS +1 flip-cite; §Spec flag-first-freeze bullet; 22→23; 4 deltas open→folded; engine c0c9329c ×3 |
| 2026-06-09 | fold v22+v23 learnings → foundation-version 22 (24 open deltas: 12 new CONVENTIONS bullets covering ADD 12 + TDD 4 + SDD-how-we-author 6, several as explicit reinforcements · 1 §Spec v22 ship bullet · 1 §Spec v23 ship bullet carrying the 8th-gate SDD forward-question · 1 §Domain all-archived done-tally blind-spot) | human-gated bulk fold at v23 close clearing the unfolded v22 (stage-graduation) backlog + the v23 deltas; consolidate not append-24-bullets (lean foundation); all 24 confirmed (none rejected) | +12 CONVENTIONS bullets (four-book-trees+unguarded-appendix-root · dogfood-at-own-gate-proof · change-request-is-the-method · single-source-point-not-restate · enumerate-every-writer-of-S · one-traversal-basis-per-tier · reconcile-flags-with-digest · cross-surface-term-two-axes · sweep-loaded-prose · presence≠coverage-fence · split-don't-loosen · five-how-we-author-sharpenings); §Spec v22+v23 bullets; §Domain done-tally bullet; deltas flipped open→folded |
| 2026-06-09 | ship v23 the decision arc: every human decision gate opens its report with goal·done·plan (rendered first, engine-sourced, presentation-only) — report-arc (the block + reconcile rule) · arc-gate-wiring (all 7 gate guides cue it) · arc-book-align (book + GLOSSARY describe it) | the user asked to make the synthesized report transparent — tie each gate's ask to the goal it serves, what's achieved, and the plan ahead, so the human confirms with the whole arc in sight, not a local snapshot | v23 SHIPPED 3/3, 3/3 criteria; 691 tests; book ×4 byte-identical; arc-book-align hit a v1→v2 change-request at verify (chapter named 5 of 7 wired gates — baseline-approval+scope undocumented; reopened→contract→re-froze→widened to 7 + a gate-coverage fence), the milestone's own theme catching its own gap |
| settled 2026-05-28–2026-06-08 | 48 foundational decisions rolled (v1.0 npm scope → v20 dynamic loop) | bootstrapping through production-ready ADD | see git |
