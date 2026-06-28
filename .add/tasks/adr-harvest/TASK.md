# TASK: Engine renders the §7 Decisions (ADR) block from §1/§3/§5/§6 stamps, tagged human/AI

slug: adr-harvest · created: 2026-06-28 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py` `_stamp_gate_record` (add.py:199) — the write-back PATTERN to MIRROR: runs at gate AFTER save_state, fills only `<…>` placeholder lines, grandfathers resolved/absent → byte-identical no-op. NEW: `_stamp_adr_record(root, state, slug)` alongside it
  - `add-method/tooling/add.py` `cmd_gate` (add.py:886; calls `_stamp_gate_record` at ~957) — wire `_stamp_adr_record` right AFTER it (same after-save ordering)
  - `add-method/tooling/add.py` `_raw_phase_bodies(root, slug)` → {N: body} — read §1 (Framings weighed), §5 (Strategy actually used), §6 (Outcome / Reviewed by); §3 freeze actor from state.json (or §3 body "FROZEN @ vN — approved by <name>")
  - `add-method/tooling/templates/TASK.md.tmpl` §7 — ADD a "### Decisions (ADR)" subsection (after "Watch", before "### Spec delta") with an engine-filled placeholder `<harvested at done …>` (the write target); 3-tree parity (fast template has NO §7 → grandfathered, out of scope)
  - the ENGINE PIN: add.py changes → ENGINE_MD5 re-pin (add_engine/* untouched → ENGINE_PKG_MD5 stays)
Context (working folder): milestone adr-at-observe task 2/3; consumes the §5 "Strategy actually used:" field frozen by strategy-actual-writeback (task 1); the audit lint that REQUIRES the block is task 3 (adr-audit-and-docs)
Honors (patterns / conventions): HARVEST-not-author (render only from stamps already in the file — NO-EXEC) · every line ACTOR-TAGGED [human]/[AI] · grandfather like gate-record-writeback (placeholder-only fill; absent block = byte-identical no-op) · called AFTER save_state (state is source of truth) · 3-tree template parity · engine change re-pins ENGINE_MD5
Anchors the contract cites: `_stamp_adr_record` · `cmd_gate` wiring · `_raw_phase_bodies` · §7 "### Decisions (ADR)" block + placeholder · the four source→actor mappings (§1→AI · §3→human · §5→AI · §6→human|AI)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: at gate, the engine HARVESTS a §7 "Decisions (ADR)" block from the actor-stamps already in the task (§1 framing · §3 freeze · §5 strategy-used · §6 gate), each line tagged [human]/[AI] — a write-back mirroring gate-record-writeback
Framings weighed: write-back-at-gate-into-§7-placeholder (chosen — reuses the proven _stamp_gate_record grandfather/placeholder mechanics; the record rides in the task file) · on-demand-`add.py adr`-command (rejected: a separate command the human must remember to run — the harvest should be automatic) · render-into-state.json-only (rejected: the audit + the human read the FILE)
Must:
<must>
  - a new `_stamp_adr_record(root, state, slug)` renders a §7 "### Decisions (ADR)" block from four sources, each line ACTOR-TAGGED: §1 Framings weighed → [AI] (chosen + rejected) · §3 freeze → [human] (FROZEN @ vN by <name>) · §5 "Strategy actually used:" → [AI] (the value) · §6 Outcome+Reviewed-by → [human] if a named human, [AI] if the auto-gate
  - it is called from `cmd_gate` right AFTER `_stamp_gate_record` (after save_state — state is source of truth; the file only mirrors it)
  - GRANDFATHER (byte-identical safety): it fills ONLY while the block still holds its `<…>` placeholder; a hand-edited (resolved) block OR an absent "### Decisions (ADR)" block OR an unreadable file → silent no-op, the file stays byte-identical
  - HARVEST-not-author: every rendered line is sourced from a stamp already in the file/state — the engine invents no decision content (NO-EXEC honored)
  - `TASK.md.tmpl` §7 gains the "### Decisions (ADR)" subsection + placeholder (after "Watch", before "### Spec delta"); 3-tree parity; the fast template (no §7) is grandfathered
  - a missing source degrades gracefully: that line renders "<unrecorded>" rather than crashing the gate
  - the engine change re-pins ENGINE_MD5 (add_engine/* untouched → ENGINE_PKG_MD5 unchanged)
</must>
Reject:
<reject>
  - the harvest THROWS and blocks the gate -> "gate_blocked_by_writeback" (it must be a never-refusing additive write, like gate-record-writeback)
  - it rewrites a hand-edited (resolved) ADR block -> "grandfather_violated"
  - it writes a decision line NOT backed by a file/state stamp -> "authored_not_harvested"
  - an ADR line is left without a [human]/[AI] tag -> "untagged_decision"
  - `add_engine/*.py` digest changes (only add.py + templates should) -> "pkg_pin_drift"
</reject>
After:
<after>
  - every full task that reaches done carries an engine-harvested, actor-tagged §7 Decisions (ADR) block — the durable record of who decided what, with the rejected alternatives and the strategy actually used; task 3 then makes its presence an audit lint
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the §6 gate actor tag — [human] vs [AI] — keys off whether "Reviewed by" names the auto-gate actor; lowest confidence because the auto-gate stamps a real actor name, so distinguishing "auto" from "a human who shares that identity" is heuristic; mitigated by reading state's gate provenance where available and falling back to the literal Reviewed-by name; if wrong: a gate line is mis-tagged human/AI (cosmetic, not a data loss) — THIS is the freeze flag
  - [ ] §1 "Framings weighed: X (chosen) · Y · Z" parses cleanly into chosen + rejected — the format is conventionally fixed; a free-form §1 degrades to "<unrecorded>" not a crash
  - [ ] placing the block FIRST in §7 (before Spec/Competency deltas) reads best — chosen: the consolidated decision record is the headline of observe
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: gate PASS harvests the §7 Decisions (ADR) block, actor-tagged
  Given a full task at verify with §1 framing, §3 frozen, §5 strategy-actually-used, §6 gate filled
  When I run add.py gate PASS
  Then §7 gains a "### Decisions (ADR)" block whose placeholder is replaced
  And it has an [AI] line for the §1 framing (chosen + rejected), a [human] line for the §3 freeze, an [AI] line for the §5 strategy used, and a line for the §6 gate
  And every decision line carries a [human] or [AI] tag

Scenario: a hand-edited ADR block is grandfathered (not overwritten)
  Given a task whose "### Decisions (ADR)" block no longer holds the <…> placeholder
  When I run add.py gate PASS
  Then the block is byte-untouched

Scenario: a task with no ADR block is a byte-identical no-op
  Given a legacy/fast task with no "### Decisions (ADR)" section
  When I run add.py gate PASS
  Then the TASK.md is byte-identical (and the gate still records PASS)

Scenario: the harvest never blocks the gate
  Given a task whose §1/§5 are malformed or empty
  When I run add.py gate PASS
  Then the gate still records PASS
  And the unreadable sources render "<unrecorded>" rather than raising

Scenario: harvest, never author
  Given the rendered ADR block
  When I compare each line to the task's stamps
  Then every line is backed by a §1/§3/§5/§6 stamp (none invented)

Scenario: the full template §7 carries the block + placeholder
  Given TASK.md.tmpl
  When I read §7
  Then a "### Decisions (ADR)" subsection with an engine-fill placeholder sits after "Watch", before "### Spec delta"
  And the three template trees are byte-identical

Scenario: only add.py + templates change — the package pin holds
  Given the engine change
  When I digest add_engine/*.py
  Then ENGINE_PKG_MD5 is unchanged (only ENGINE_MD5 re-pins)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION (add.py, beside _stamp_gate_record):
  _stamp_adr_record(root: Path, state: dict, slug: str) -> None
    - called from cmd_gate AFTER _stamp_gate_record (so §6 GATE RECORD is already mirrored)
    - read tasks/<slug>/TASK.md; locate the "<harvested at done…>" placeholder ONLY inside the
      "## 7 · OBSERVE" section (INV-7); absent §7 / a resolved (hand-edited) block -> return
      (grandfather, byte-identical no-op); on OSError -> return
    - never raises: any per-source parse failure renders "<unrecorded>", never propagates

TEMPLATE — TASK.md.tmpl §7, inserted AFTER "Watch (reuse scenarios as monitors): …", BEFORE "### Spec delta":
a "### Decisions (ADR)" header followed by ONE placeholder line — quoted inline here so the
contract itself is never a harvest target (INV-7): `<harvested at done from §1/§3/§5/§6 — do not
hand-edit; one actor-tagged line per decision, refilled only while this placeholder stands>`.

RENDERED BLOCK (placeholder line replaced; four lines, each [human]/[AI]-tagged):
- [AI] specify — chose <chosen>; rejected <alt · alt>            (source: §1 Framings weighed)
- [human] freeze — froze §3 @ v<N> (approved by <name>)          (source: §3 freeze / state)
- [AI] build — strategy used: <§5 value, or "as planned">        (source: §5 Strategy actually used)
- [<human|AI>] verify — gate <OUTCOME> (reviewed by <name>)       (source: §6 Outcome + Reviewed by)

ACTOR RULE: §1 + §5 are always [AI]; §3 freeze is always [human]; §6 gate is [human] when Reviewed-by
  names a human, [AI] when it is the auto-gate actor (provenance from state where available).

INVARIANTS:
INV-1  HARVEST-not-author — every rendered line is backed by a §1/§3/§5/§6 stamp; none invented
INV-2  GRANDFATHER — fills only while the <…> placeholder stands; resolved/absent/unreadable -> byte-identical no-op
INV-3  NEVER-REFUSE — the write is additive and never raises; the gate always records its outcome
INV-4  every rendered line is actor-tagged [human] or [AI]
INV-5  add_engine/*.py byte-identical -> ENGINE_PKG_MD5 unchanged; only add.py re-pins ENGINE_MD5
INV-6  §7 block byte-identical across the 3 full-template trees; fast template (no §7) grandfathered
INV-7  §7-OBSERVE-scoped — the placeholder is matched ONLY inside the "## 7 · OBSERVE" section; a "<harvested at done…>" line elsewhere (e.g. a §3 contract illustration) is NEVER touched
error codes: gate_blocked_by_writeback · grandfather_violated · authored_not_harvested · untagged_decision · pkg_pin_drift · contract_illustration_harvested
```

Least-sure flag surfaced at freeze: [contract] v2 change-request — dogfooding the v1 build on its OWN task EXPOSED a real bug: the harvest matched the first file-wide "<harvested at done…>" line, which here was the §3 contract ILLUSTRATION, corrupting the frozen contract and skipping §7. v2 adds INV-7 (§7-OBSERVE-scoped) + a regression test; the engine fix is proven (test_harvest_targets_only_section_7 RED→GREEN). The remaining least-sure point is unchanged: the §6 gate actor tag [human] vs [AI] keys off `autonomy: auto` (heuristic; a mis-tag is cosmetic, no data loss).
Status: FROZEN @ v2 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-anchored; every Must + Reject has ≥1 assertion (test_adr_harvest.py)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_gate_harvests_actor_tagged_block: gate PASS fills §7 ADR with [AI] §1 / [human] §3 / [AI] §5 / §6 gate lines; every line actor-tagged — RED ✓
  - test_harvest_not_authored: every line's token traces to a real stamp — RED ✓
  - test_template_carries_adr_block: TASK.md.tmpl §7 has the block after Watch, before Spec delta — RED ✓
  - test_grandfather_resolved_block_untouched: a resolved block is byte-untouched — green (vacuous now, real post-build)
  - test_absent_block_is_noop: no ADR fabricated where none existed; gate still PASS
  - test_never_blocks_on_malformed_sources: malformed §1/§5 → gate still records PASS
  - test_template_mirrors: 3 full-template trees one md5
  - test_pkg_pin_holds: package_digest == ENGINE_PKG_MD5 (only add.py re-pins ENGINE_MD5)
</test_plan>

Tests live in: `add-method/tooling/test_adr_harvest.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/templates/TASK.md.tmpl` `.add/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/tooling/test_adr_harvest.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/test_gate_record_writeback.py`
Strategy (ordered batches): 1. TESTS — new test_adr_harvest.py: gate harvests the §7 block (4 actor-tagged lines), grandfather (resolved untouched), absent-block no-op, never-blocks, pkg-pin-holds (red). 2. BUILD — add the §7 "### Decisions (ADR)" placeholder to TASK.md.tmpl (cp ×3); add `_stamp_adr_record` beside `_stamp_gate_record`; wire it into `cmd_gate` after `_stamp_gate_record`. 3. Re-pin ENGINE_MD5 (engine_pin.py); confirm ENGINE_PKG_MD5 unchanged; suite green.
Known-problem fixes: a crash in the harvest blocking the gate → wrap all parsing in try/except → "<unrecorded>", never propagate · regenerating a resolved block → fill ONLY when the `<…>` placeholder line still stands · reading §6 BEFORE gate-record-writeback fills it → call AFTER `_stamp_gate_record` · the engine-pin test reads md5(add.py) → re-pin in the TESTS phase math then verify, never hand-edit after build · forgetting a template mirror → cp canonical ×3 + md5
Strategy actually used: followed the planned 3 batches (red tests → template block + `_stamp_adr_record` + cmd_gate wiring → re-pin), and IMPROVED on it for two foreseeable template ripples the plan under-scoped: (a) the ADR header's `<!-- … -->` comment hit the lean comment-count cap (`test_lean_pass_single_freeze_comment`) → folded the "engine-fills, do not hand-edit" guidance INTO the `<harvested at done …>` placeholder line (no new HTML comment) instead of rebaselining the lean fence; (b) the new §7 harvest fires on every full task, so the sibling `test_no_gate_record_block_is_noop` whole-file byte-compare had to normalize the ADR block out (its real GATE-RECORD invariant preserved) — a touch outside declared §5, recorded as a §7 scope-delta. Also DOGFOODED: added the §7 ADR placeholder to this task's own OBSERVE so gating it harvests its own decision record. §6 actor tag keyed off `autonomy: auto` (the assumption-flagged heuristic), not the Reviewed-by name.
Safety rule (feature-specific): the harvest is a NEVER-REFUSING additive write called AFTER save_state — state is the source of truth; a write fault never loses the gate verdict
Code lives in: add.py (`_stamp_adr_record` + cmd_gate wiring) · TASK.md.tmpl §7 · engine_pin.py
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2123/0 (`python3 -m unittest discover`); test_adr_harvest 8/8
- [x] coverage did not decrease — 8 new tests added, none removed/weakened
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; the one sibling-test edit (test_gate_record_writeback `norm`) was a normalization for the new write-back, not a weakening (its GATE-RECORD invariant intact) — recorded as a §7 scope-delta
- [x] the green was EARNED, not gamed — adversarial refute-read (Explore subagent) verdict EARNED on all 6 checks: harvest parses real stamps (no authored content), token asserts trace to fixture file-writes, grandfather/no-op non-vacuous (template carries the block), pkg-pin genuine, never-raise has 3 bail layers
- [x] concurrency / timing of the risky operation is safe — write is a single `_atomic_write` AFTER save_state (state is source of truth); a write fault never loses the verdict
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib (re), no new imports/deps; no user input reaches a shell/eval (NO-EXEC)
- [x] layering & dependencies follow CONVENTIONS.md — mirrors `_stamp_gate_record` exactly; ENGINE_PKG_MD5 unchanged (add_engine/* untouched)
- [x] a person reviewed and approved the change — human (Tin Dang) approved at the §3 freeze (v1); verify is auto-gated under `autonomy: auto` with the refute-read as the adversarial check

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] gating a real task writes a §7 ADR block with four actor-tagged lines mapping §1→[AI] · §3→[human] · §5→[AI] · §6→gate — confirmed: live-rendered a block (4 lines: chose AlphaApproach; freeze; build strategy; verify gate PASS) inspected during build
- [x] a resolved/absent block is byte-untouched; a malformed source never blocks the gate — confirmed by test_grandfather_resolved_block_untouched + test_never_blocks_on_malformed_sources green
- [x] only add.py + the full template changed — confirmed: ENGINE_PKG_MD5 e87f5652… unchanged, ENGINE_MD5 re-pinned fe30bdb3…, the 3 template trees one md5

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_stamp_adr_record` is called once in `cmd_gate` right after `_stamp_gate_record`; its helpers (`_framing/_freeze/_strategy/_gate`) are nested + all called; `_raw_phase_bodies`/`_atomic_write` reused
- [x] DEAD-CODE (code) — no new top-level symbol beyond `_stamp_adr_record`; no orphan introduced (refute-read confirmed)
- [ ] SEMANTIC (prose / non-code) — n/a (code task; the template prose change is one §7 subsection, read in full)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose write-back-at-gate-into-§7-placeholder; rejected on-demand-`add.py adr`-command (rejected: a separate command the human must remember to run — the harvest should be automatic) · render-into-state.json-only (rejected: the audit + the human read the FILE)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: followed the planned 3 batches (red tests → template block + `_stamp_adr_record` + cmd_gate wiring → re-pin), and IMPROVED on it for two foreseeable template ripples the plan under-scoped: (a) the ADR header's `<!-- … -->` comment hit the lean comment-count cap (`test_lean_pass_single_freeze_comment`) → folded the "engine-fills, do not hand-edit" guidance INTO the `<harvested at done …>` placeholder line (no new HTML comment) instead of rebaselining the lean fence; (b) the new §7 harvest fires on every full task, so the sibling `test_no_gate_record_block_is_noop` whole-file byte-compare had to normalize the ADR block out (its real GATE-RECORD invariant preserved) — a touch outside declared §5, recorded as a §7 scope-delta. Also DOGFOODED: added the §7 ADR placeholder to this task's own OBSERVE so gating it harvests its own decision record. §6 actor tag keyed off `autonomy: auto` (the assumption-flagged heuristic), not the Reviewed-by name.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · seeded] the §5 Scope under-scoped the template ripple: adding a §7 template subsection forced two edits outside declared scope — the lean comment-count fence (avoided by folding guidance into the placeholder) and the sibling `test_gate_record_writeback.py` no-op normalization. Future template-section tasks should pre-declare the lean fence + every gate-write-back no-op test (evidence: 2 sibling tests went red on the first full-suite run)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
