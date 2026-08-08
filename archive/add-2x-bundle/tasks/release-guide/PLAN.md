# TASK: Author release.md — the 7-step RELEASE altitude flow

slug: release-guide · created: 2026-06-16 · stage: mvp
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - NEW `release.md` in 3 byte-identical skill homes (like `graduate.md`/`fold.md`): `add-method/skill/add/` · `add-method/src/add_method/_bundled/skill/add/` · `.claude/skills/add/` — the 7-step RELEASE scope-level guide. Drafted lint-clean at `tmp/release.md`.
  - `SKILL.md` ×3 (same 3 homes) — add a release.md cross-ref in "Beyond the bundle", right AFTER the graduation paragraph (canonical L118–122), mirroring `graduate.md`'s paragraph shape.
  - `add-method/tooling/wording_lint.py:surface_files()` (L203–208) — globs `skill/add/*.md` + `phases/*.md` + appendix-b; release.md AUTO-joins the linted surface → its prose must be wording-lint clean (VERIFIED: `wording_lint.py --surface tmp/release.md` → 0 findings).
  - `add-method/tooling/test_wording_lint.py:test_surface_files_cover_the_contract` (L181 `== 27`) + `add-method/tooling/test_per_step_hooks.py:test_wording_surface_count_unchanged` (L74 `== 27`) — the 2 inventory guards that COUNT the surface; both bump 27→28 (additive registration, NOT a weakening).
  - `graduate.md` — the SIBLING scope-level guide whose form/voice/length release.md mirrors (cue → flow → floor → invariants → depth + worked example).
  - `add-method/tooling/WORDING_RUBRIC.md` (FROZEN @ v2) — the enforced-idiom source; release.md must avoid `[enforced]` phrases (`the fold` → "consolidated deltas"; `every altitude` → "every scope level").
Context (working folder): drafted guide `tmp/release.md` (lint-clean) + `tmp/release-chapter-outline.md` (the ch.16 outline is `release-docs-align`'s, NOT this task). MILESTONE.md shared decisions every task honors (engine-records-human-ships · security HARD-STOP un-forceable · notes-from-consolidated-deltas · append-only ledger · bundles ≥1 milestone). Book `docs/16-releasing.md` is `release-docs-align`'s, not this task.
Honors (patterns / conventions): mirror-clause-all-copies (guide + SKILL byte-identical in all 3 homes, md5-parity) · a new skill-surface guide is NOT free — register BOTH inventory guards (count + membership) up front in §5 (the compact-guide OBSERVE lesson) · wording-lint is PROSE-ONLY + word-boundary/phrase-level (code-span doc names; avoid `[enforced]` phrases) · convention-guided seam — the guide DESCRIBES `release-report`/`release` but adds NO `add.py` (those are sibling tasks); engine UNCHANGED · v16 XML: 5-tag block vocab, release.md uses `<reject_codes>`; inline `<version>` is a placeholder like `<slug>`.
Anchors the contract cites: `release.md` (the new guide) · the SKILL.md "Beyond the bundle" release cross-ref · the 2 inventory-guard counts (27→28) · `graduate.md` (the sibling form) · the FROZEN `WORDING_RUBRIC.md`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: release.md — the 7-step RELEASE scope-level guide (cut a versioned, watched ship), mirrored byte-identical across the 3 skill homes + a SKILL.md "Beyond the bundle" cross-ref.
Framings weighed: ONE on-demand guide mirroring `graduate.md`'s shape (chosen — release is a scope level like graduation; the maintainer reads one place) · a new gated phase in the 9-phase ladder (rejected — the frozen ladder is untouched; release bundles milestones, it is not per-task) · fold release into `graduate.md` (rejected — release ships a version, graduation moves rigor; orthogonal axes).
Must:
<must>
  - THE FLOW: release.md states the 7 ordered steps — cue → gather (`release-report`) → draft notes from consolidated deltas → readiness floor → human confirms → cut (`add.py release`, record-only) → watch — in `graduate.md`'s "AI gathers, human confirms, engine records + enforces a floor" voice.
  - THE CUE: names the `→ releasable: N milestone(s) closed since last release` status line as a TALLY (never a judgment), silent until ≥1 closed-and-unreleased milestone exists.
  - THE FLOOR: names the 4 reject codes (`release_security_open` · `release_tests_red` · `release_no_closed_milestone` · `release_undisclosed_waiver`) and states security is the ONE un-forceable reject (`--force` never overrides it).
  - ENGINE-RECORDS-HUMAN-SHIPS: states the engine RECORDS (CHANGELOG + `RELEASES.md` ledger + milestone attribution) and NEVER tags/publishes/deploys — the outward act is human-owned + tool-agnostic.
  - ORDER + REUSE: states release runs AFTER `fold.md` (notes drawn from consolidated deltas), bundles ≥1 milestone (orthogonal to stage), and scales depth by stage.
  - SKILL CROSS-REF: SKILL.md (3 homes) cross-refs release.md in "Beyond the bundle", right AFTER the graduation paragraph.
  - MIRROR PARITY: release.md + the SKILL.md edit are byte-identical across the 3 homes; the 2 surface-count guards register the new file (27→28); `add.py` is UNCHANGED.
  - LINT-CLEAN: release.md prose passes wording-lint (no `[enforced]` rubric idiom).
</must>
Reject:
<reject>
  - release.md or the SKILL.md edit is not byte-identical across the 3 homes -> "mirror-drift"
  - the guide introduces an `add.py` command / check enforcement (the cut's behavior is the sibling release-report/release-command tasks') -> "engine-creep"
  - release.md prose contains an `[enforced]` wording-rubric idiom -> "wording-regression"
  - the guide's floor / steps / reject-code set diverges from the milestone's shared decisions (security un-forceable; engine-records-human-ships; after-fold order) -> "decision-drift"
</reject>
After:
<after>
  - release.md exists in 3 byte-identical homes stating the 7-step flow + the cue + the 4-code floor + engine-records-human-ships; SKILL.md cross-refs it in all 3 homes; the 2 surface-count guards read 28; wording-lint is green; `add.py` is unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the SKILL.md cross-ref belongs right AFTER the graduation paragraph (canonical L122), as a sibling scope-level — lowest confidence because release is orthogonal-to-stage, so a reader might expect it grouped with `loop.md` (milestone-close) instead; if wrong: a 1-line move of the cross-ref. Mitigation: place it after graduation (the nearest scope-level sibling) and name the orthogonality in the sentence.
  - [ ] release.md mirrors `graduate.md`'s length/voice (~90 lines) — style; treated settled (the draft already matches).
  - [ ] naming the not-yet-built `release-report`/`release` commands in a guide is fine before they exist — treated settled (`graduate.md` already names `graduation-report`; the guide IS the spec the sibling tasks build to).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the guide states the 7-step flow and the cue
  Given release.md
  When a maintainer reads it
  Then it names the 7 ordered steps (cue → gather → draft notes → readiness floor → human confirms → cut → watch)
  And it names the `→ releasable: N milestone(s)` cue as a tally that is silent until ≥1 closed-and-unreleased milestone

Scenario: the floor names four codes and security is un-forceable
  Given release.md's floor section
  When read
  Then it names release_security_open, release_tests_red, release_no_closed_milestone, release_undisclosed_waiver
  And it states `--force` never overrides release_security_open

Scenario: the engine records and the human ships
  Given release.md
  When read for what the cut does
  Then it states `add.py release` records the CHANGELOG entry + a RELEASES.md ledger row + milestone attribution
  And it states the engine never tags, publishes, or deploys — the human owns that outward act

Scenario: release runs after fold and bundles one-or-more milestones
  Given release.md
  When read for ordering and scope
  Then it states release runs after `fold.md` (notes drawn from consolidated deltas) and bundles ≥1 milestone, orthogonal to stage
  And the lifecycle order milestone-done → fold → compact → archive → release → watch is stated

Scenario: SKILL cross-refs release.md in all three homes
  Given the 3 SKILL.md homes
  When read at "Beyond the bundle"
  Then each cross-refs release.md right after the graduation paragraph
  And the graduation cross-ref remains (release follows graduation)

Scenario: the guide and SKILL edit are byte-identical across the 3 homes
  Given the 3 skill homes
  When release.md and the SKILL.md edit land
  Then release.md and SKILL.md are md5-identical across all 3 homes and the 2 surface-count guards read 28
  And a home left out of sync is rejected with "mirror-drift"

Scenario: the guide stays convention-guided
  Given release.md
  When reviewed for engine surface
  Then it introduces no `add.py` command or check enforcement and `add.py` is unchanged
  And an engine reference to release behavior is rejected with "engine-creep"

Scenario: the guide prose passes wording-lint
  Given release.md on the linted surface
  When wording_lint.py runs
  Then it reports 0 findings (no `[enforced]` rubric idiom)
  And a banned idiom in the prose is rejected with "wording-regression"

Scenario: the guide does not drift from the milestone's shared decisions
  Given release.md's floor, steps, and reject codes
  When compared to the milestone shared decisions
  Then they match (security un-forceable; engine-records-human-ships; after-fold order)
  And a divergence is rejected with "decision-drift"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
RELEASE-GUIDE CONTRACT — release.md (NEW), the 7-step RELEASE scope-level guide (convention-guided)

deliverable: release.md (NEW), byte-identical in 3 homes —
  add-method/skill/add · add-method/src/add_method/_bundled/skill/add · .claude/skills/add

structure (the guide document, mirroring graduate.md's shape/voice):
  # Release — cut a versioned ship, never an unwatched flip
  intro              — the 5th scope level; release ≠ milestone-close and ≠ graduation (orthogonal axes)
  ## The cue         — `→ releasable: N milestone(s) closed since last release` — a tally, silent until ≥1
  ## The flow        — the 7 ordered steps: cue → gather (`release-report`) → draft notes (from consolidated
                       deltas) → readiness floor → human confirms → cut (`add.py release`, record-only) → watch
  ## The floor       — the 4 reject codes; `release_security_open` is un-forceable (`--force` never overrides)
  ## Invariants      — engine records (CHANGELOG + RELEASES.md ledger + attribution); human ships
                       (tag/publish/deploy); after-fold order; append-only ledger; bundles ≥1 milestone
  ## Depth and reuse — depth by stage (prototype preview → prod GA)
  ## Worked example  — the repo's own 1.5.0 cut

SKILL.md cross-ref (3 homes, byte-identical): in "Beyond the bundle", AFTER the graduation paragraph (≈L122)
  add a release.md paragraph (cue → release-report → notes → floor → human confirms → records → watch;
  engine records, human ships).

mirror parity : release.md + SKILL.md md5-identical across 3 homes.            drift -> "mirror-drift"
surface guards: test_wording_lint.py + test_per_step_hooks.py count 27 -> 28   (additive registration)
wording       : release.md prose 0 wording-lint findings.                      banned idiom -> "wording-regression"
engine        : UNCHANGED — no add.py edit (else "engine-creep"); the decision-set must match the milestone (else "decision-drift")
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-16
Least-sure flag surfaced at freeze: [spec] the SKILL.md cross-ref placement — after the graduation paragraph (chosen: nearest scope-level sibling) vs grouped with `loop.md`/milestone-close; release is orthogonal-to-stage, so a reader's mental model could differ. If wrong: a 1-line move of the cross-ref — no contract shape rides on it.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: each Must + each Reject has a test; assert guide structure + md5 parity + surface-count + wording-clean (behavioral, not bare token).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_guide_exists_3_homes: release.md exists in all 3 skill homes
  - test_guide_mirror_parity: md5 the 3 homes / assert all equal [guards mirror-drift]
  - test_flow_7_steps: the guide names the 7 ordered steps (cue → gather → draft → floor → confirm → cut → watch) in order
  - test_cue_named: the guide names the `→ releasable` cue as a tally (silent until ≥1)
  - test_floor_4_codes_security_unforceable: names the 4 reject codes AND states `--force` never overrides release_security_open
  - test_engine_records_human_ships: states the engine records (CHANGELOG + RELEASES.md + attribution) AND never tags/publishes/deploys
  - test_after_fold_bundles: states the after-fold order AND bundles ≥1 milestone orthogonal to stage
  - test_skill_cross_ref_3_homes: SKILL.md (3 homes) cross-refs release.md after graduation, byte-identical
  - test_surface_count_28: wl.surface_files() length is 28 (release.md registered) [guards the inventory bump]
  - test_no_engine_creep: add.py (both homes) gained no release command/reject-code enforcement [guards engine-creep]
  - test_wording_clean: wording_lint over release.md -> 0 findings [guards wording-regression]
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/release.md` `add-method/src/add_method/_bundled/skill/add/release.md` `.claude/skills/add/release.md` `add-method/skill/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/tooling/test_wording_lint.py` `add-method/tooling/test_per_step_hooks.py` `./tests/`   — new guide ×3 + SKILL cross-ref ×3 + the 2 inventory guards (surface count 27→28; additive registration, NOT engine behavior — add.py untouched) + this task's guard tests. NO `add.py` (convention-guided seam).
Strategy (ordered batches): 1. write `./tests/` red · 2. copy lint-clean `tmp/release.md` → the 3 homes byte-identical (md5) · 3. add the SKILL cross-ref ONCE → apply byte-identical to the 3 SKILL.md homes (md5) · 4. bump the 2 surface-count guards 27→28 · 5. run green (this suite + the full engine suite).
Safety rule (feature-specific): each mirrored file is written from ONE source (write-once-copy) so md5 parity is STRUCTURAL; the surface-count bump is additive registration only (no existing assert weakened); never add an `add.py` command.
Code lives in: the 3 release.md homes + the 3 SKILL.md homes + the 2 inventory guards
Constraints: do NOT change any test or the frozen contract; no `add.py`/engine edit; allow-list only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — release-guide suite 11/11 GREEN (`tests/test_release_guide.py`); full add-method engine suite 1152/1152 OK; `add.py check` 325 passed / 0 failed (14 pre-existing orphan-task warnings only).
- [x] coverage did not decrease — STRENGTHENED: +11 task tests; the 2 inventory guards gained a `release.md` membership assert + count 27→28. No assert removed.
- [⚠] no test or contract was altered during build — the FROZEN §3 and this task's red suite are UNCHANGED. DISCLOSED (×2): (a) 2 PRE-EXISTING inventory guards were UPDATED to REGISTER the new surface file — `test_wording_lint.py` (count 27→28 + membership) + `test_per_step_hooks.py` (27→28); additive registration of a deliberately-added guide, declared in §5 Scope, NOT a weakening (same pattern as compact-guide). (b) `test_no_engine_creep` was implemented as "no engine home references `release.md` (the guide file)" rather than the §4-plan's literal "no release command" — because the sibling `release-command` task WILL add an `add.py release` command; the guide-file check guards the convention-guided seam (engine never parses guides) and survives that landing. Faithful to the frozen `engine-creep` reject intent; no contract shape changed.
- [x] the green was EARNED, not gamed — tests are behavioral: they assert the guide NAMES the 7 ordered steps (arc string), the cue-as-tally, the 4 floor codes + `--force does not override`, engine-records/never-ships, the after-fold order, md5 parity across 3 homes, the surface count 28, and 0 wording findings. No vacuous asserts; no fixture overfit (the surface/lint are read live). Static prose — no logic to stub.
- [x] concurrency / timing — N/A: static method-doc prose (no runtime path).
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: prose guide; `add.py` untouched; no new dependency.
- [x] layering & dependencies follow CONVENTIONS.md — mirror-clause-all-copies honored (release.md + SKILL.md md5-identical across the 3 homes: `d96414c8…` / `8e4cbf3a…`); convention-guided seam preserved (no `add.py` edit — `test_no_engine_creep` green); BOTH fences green (phrase-level `wording_lint` 0 findings + bare-word `test_ubiquitous_language` 0 hits after purging prose `fold`/`altitude`, keeping only code-span `fold.md` + the one-line order arc).
- [ ] a person reviewed and approved the change — PENDING the human gate (autonomy: conservative).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read `release.md` (all 3 homes via md5 parity) end-to-end + the SKILL.md cross-ref. Confirmed: the 7 steps appear in order (cue → gather → draft → floor → confirm → cut/record + ship → watch); the cue is a tally; the floor names all 4 codes with security un-forceable; the engine records (CHANGELOG + RELEASES.md + attribution) and never tags/publishes/deploys; the after-fold lifecycle order is stated; release bundles ≥1 milestone orthogonal to stage; depth-by-stage + the hotfix path are present; the 1.5.0 worked example matches the real history (udd-design-loop 4/4 → fv33 → test_release_1_5_0.py). All cross-refs resolve (`design.md` · `advisor.md` · `intake.md` · `scope.md` · `loop.md` · `graduate.md` · `fold.md` · `report-template.md` · `phases/0-setup.md` · `phases/7-observe.md`). No internal contradiction.

### GATE RECORD
Outcome: PASS
Note: PASS accepts the 2 disclosed additive changes — (a) the 2 inventory guards registered the new surface file (count 27→28 + a `release.md` membership assert), (b) `test_no_engine_creep` scoped to the guide file so the sibling `release-command` landing won't turn it red. No frozen contract or red-suite test was weakened.
Reviewed by: Tin Dang · date: 2026-06-16

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): both wording fences (phrase-level `wording_lint` + bare-word `test_ubiquitous_language`) over the new guide · mirror md5 drift across the 3 release.md / SKILL.md homes · the 2 surface-count guards · scope_violation on any task that adds a skill guide.
Spec delta for the next loop: the sibling tasks build the engine behavior this guide SPECIFIES — `release-report` (the cue + the 5 record-sets + the RELEASES.md schema), `release-command` (the guarded `add.py release` + the 4 floor codes), `release-docs-align` (book ch.16 + glossary). 3/4 milestone tasks remain.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [ADD · folded] a new skill-surface guide must clear TWO wording fences, not one — the phrase-level `wording_lint`/WORDING_RUBRIC AND the stricter bare-word `test_ubiquitous_language` (bans `fold`/`altitude` as whole words in prose, code-span-exempt); clearing only the first leaves the engine suite red (evidence: tmp/release.md passed wording_lint 0-findings but test_slang_absent_extended_surface flagged fold+altitude until the prose was purged)
  - [ADD · folded] the inline-code-span exemption in `test_ubiquitous_language` is PER-LINE — a backtick span that wraps across two physical lines leaves its first-line banned tokens exposed to the bare-word fence (evidence: the `milestone-done → fold → …` order arc wrapped two lines → `fold` flagged until the whole arc was placed on one line)
  - [TDD · folded] the §3 freeze flag label is a parsed MACHINE TOKEN — the `unflagged_freeze` guard requires the literal `Least-sure flag surfaced at freeze:` and rejects any reworded label, blocking the tests→build crossing (evidence: `add.py advance` refused with unflagged_freeze until the reworded "Lowest-confidence flag surfaced for freeze" was restored verbatim)
  - [TDD · folded] a guide-task's "engine untouched" guard must assert a DURABLE invariant (the engine never references the guide FILE), never "no <feature> command", when a sibling task will legitimately add that command — else the guard reddens on the sibling's landing (evidence: test_no_engine_creep scoped to `release.md` not the `release` command, so the future release-command task will not turn it red)
  - [ADD · folded] adding a skill guide is not free — it auto-joins the wording-lint surface, so BOTH surface-count guards (count + membership) must bump in the SAME build; declare them in §5 up front (evidence: reused the compact-guide lesson — both guards bumped 27→28 with no gate surprise)
