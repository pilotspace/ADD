# TASK: TASK.md header carries an engine-written milestone: backlink

slug: task-milestone-backlink · created: 2026-06-30 · stage: mvp
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
  - `add-method/tooling/add.py:_render_template` (l.138) — substitutes `{{key}}` tokens; `cmd_new_task` (l.451) calls it at l.512 with `title/slug/date/stage/autonomy` — ADD `milestone=`.
  - `add-method/tooling/add.py:cmd_new_task` (l.466) — `milestone = args.milestone or _active_milestone(state)`; the parent is already resolved here, just not passed to the render.
  - `add-method/tooling/add.py:cmd_set_milestone` (l.3751) — moves/detaches a task; writes state ONLY (l.3763), does NOT rewrite TASK.md → the backlink would drift on a move. Must rewrite the `milestone:` line.
  - `add-method/tooling/add.py:cmd_check` (l.2531 per-task loop, l.2538 `ms = t.get("milestone")`) — ADD a backlink-drift WARN (TASK.md `milestone:` ≠ state).
  - `add-method/tooling/templates/TASK.md.tmpl` (l.3 `slug: {{slug}} · created: {{date}} · stage: {{stage}}`) — ADD a `milestone:` header field. (×3 template trees)
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` — re-pinned (engine changes this milestone). (×3 add.py copies)
Context (working folder):
  - `.add/state.json` `tasks.<slug>.milestone` — the authoritative parent the backlink mirrors. `_active_milestone(state)` resolves the default.
  - sibling: M1 `test_ground_*` pattern for 3+3 parity; `test_skill_lean.py` phases pool (this task adds NO phase-guide prose → pool untouched).
Honors (patterns / conventions):
  - validate-then-write (cmd_new_task/set_milestone already do); `_atomic_write*`; warn-never-block for drift nudges (the existing milestone-resolve check is a hard check, but backlink drift is a soft WARN per the milestone decision).
  - design-for-failure: a milestone-free task (fast/standalone) must render a sane `milestone:` value (none), never a broken backlink.
Anchors the contract cites: cmd_new_task render call (add.py:512) · cmd_set_milestone (add.py:3763) · cmd_check per-task loop (add.py:2538) · TASK.md.tmpl `milestone:` header line · engine_pin.ENGINE_MD5
Issues/Risks (→ feed §1):
  - **milestone-free tasks** — `new-task` with no active milestone (or `set-milestone none`) leaves `milestone` = None; `_render_template` does `text.replace`, which needs a STRING → must pass `milestone or "(none)"` (or similar), else a None crashes the replace. The backlink for a milestone-free task must read cleanly (e.g. `(none)`), not empty/broken.
  - **set-milestone drift** — if only `new-task` writes the field but `set-milestone` doesn't rewrite it, the backlink silently lies after a move. The "engine-maintained, can't drift" decision REQUIRES set-milestone to rewrite the TASK.md line too.
  - **grandfathered tasks** — ~190 archived + existing in-flight tasks have no `milestone:` line; `check` must NOT retro-red them (warn-never-block, and only when the line EXISTS and disagrees).
  - **engine re-pin trap** — touching add.py drifts ENGINE_MD5; all 3 copies + engine_pin must move in lockstep or the parity/pin tests go red (a deliberate tripwire, not a bug to silence).
Related intent: PROJECT.md "no lost context across sessions" (a self-describing artifact needs no state.json to know its parent) · GLOSSARY "milestone"/"task" · originating request — Tin's "enhance metadata block of *.md for ... relationship cross artifact like task.md <-> milestone.md"; artifact-trust roadmap M2 (minimal, engine-populated backlinks).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: TASK.md header carries an engine-written `milestone:` backlink to its parent (task→milestone)
Framings weighed: engine-populated header field — add.py writes + maintains it (chosen, Tin-confirmed: drift-proof) · template-only field the AI hand-fills (rejected — can drift, doesn't meet "traversable without re-deriving") · a rich node+edge graph (rejected — Tin chose minimal)
Must:
<must>
  - M1: `add.py new-task <slug>` writes a `milestone:` line into the new TASK.md header naming the resolved parent (the `--milestone` arg or the active milestone) — via a `{{milestone}}` token in TASK.md.tmpl + the `_render_template` call (cmd_new_task, add.py:512) passing `milestone=`.
  - M2: a milestone-free task (no active milestone, `--milestone none`-equivalent, or a standalone `--fast` task) renders `milestone: (none)` — a clean, valid backlink, never blank/None/broken.
  - M3: `add.py set-milestone <task> <ms|none>` REWRITES the TASK.md `milestone:` line to match the new parent (the slug, or `(none)` on detach), so the backlink can't drift after a move — state and file stay in lockstep.
  - M4: `add.py check` emits a WARN (never red, warn-never-block) when a TASK.md `milestone:` line EXISTS and disagrees with `state.json`; a task with NO `milestone:` line (grandfathered/archived) is NOT flagged.
  - M5: invariants — every `add.py` copy is byte-identical and equals the RE-PINNED `engine_pin.ENGINE_MD5`; `TASK.md.tmpl` `milestone:` field present in ×3 template trees byte-identical; the phases lean pool is UNTOUCHED (no phase-guide prose added).
</must>
Reject:
<reject>
  - new-task renders a blank/None `milestone:` for a milestone-free task (must read `(none)`) -> "backlink_blank_or_none"
  - set-milestone moves a task but leaves the TASK.md `milestone:` line stale -> "backlink_drift_on_move"
  - check hard-fails (red) a grandfathered task that has no `milestone:` line -> "grandfather_retro_red"
  - the build edits add.py without re-pinning ENGINE_MD5 across all 3 copies -> "engine_pin_drift" (pin/parity tripwire)
</reject>
After:
<after>
  - A task created or moved by the engine carries a `milestone:` header backlink that matches state.json; a milestone-free task reads `milestone: (none)`; `add.py check` flags only a present-and-disagreeing line; add.py re-pinned + ×3 byte-identical; template ×3 byte-identical; full suite green; phases pool unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The header placement — a NEW `milestone:` line (after the `slug:` line) vs appending to the `slug: … · stage:` line. Lowest confidence: whether a separate line breaks any existing header parser (the `slug:`/`autonomy:`/`phase:` lines are read by predicates). A separate line is cleaner to read + rewrite (M3's regex), but if a parser keys on line positions it could shift. If wrong: a header-parse regression in a sibling test → mitigate by placing the line AFTER the existing keyed lines and re-running the full suite.
  - [ ] set-milestone rewrites via a line-regex on the existing TASK.md (the file may predate the field) — if the line is ABSENT (grandfathered task being moved), set-milestone INSERTS it after the slug line rather than failing.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: new-task writes the milestone backlink   # M1
  Given a confirmed milestone "demo" is active
  When I run `add.py new-task feat-x`
  Then tasks/feat-x/TASK.md header has a line `milestone: demo`
  And that matches state.json tasks.feat-x.milestone

Scenario: milestone-free task reads (none)   # M2, R:backlink_blank_or_none
  Given no milestone is active (or the task is a standalone --fast)
  When I run `add.py new-task loose-x` (milestone-free)
  Then tasks/loose-x/TASK.md header has `milestone: (none)`
  And the line is never blank, "None", or broken

Scenario: set-milestone rewrites the backlink   # M3, R:backlink_drift_on_move
  Given task feat-x has `milestone: demo` in its TASK.md
  When I run `add.py set-milestone feat-x other`
  Then tasks/feat-x/TASK.md header now reads `milestone: other`
  And on `set-milestone feat-x none` it reads `milestone: (none)`
  And state.json and the TASK.md line agree after each move

Scenario: check warns on a disagreeing backlink   # M4
  Given task feat-x TASK.md says `milestone: demo` but state says `other`
  When I run `add.py check`
  Then it emits a WARN naming feat-x's backlink drift
  And the WARN does not make check exit non-zero (warn-never-block)

Scenario: check does not retro-red a grandfathered task   # M4, R:grandfather_retro_red
  Given task old-y TASK.md has NO `milestone:` line
  When I run `add.py check`
  Then old-y is not flagged for a backlink mismatch
  And check's failed-count is unchanged by the absence of the line

Scenario: the engine stays pinned and the trees match   # M5, R:engine_pin_drift
  Given the change is applied
  When I md5 every add.py copy and the 3 TASK.md.tmpl copies
  Then each add.py equals the re-pinned engine_pin.ENGINE_MD5
  And the 3 template copies are byte-identical
  And the phases lean pool is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
TASK.md header backlink — frozen shape @ v1   (engine-maintained milestone↔task link)

TASK.md.tmpl header gains, after the `slug: … · stage: …` line:
    milestone: {{milestone}}
  rendered by add.py: {{milestone}} := the parent slug, or "(none)" when milestone-free.

add.py cmd_new_task (render call ~l.512):
    _render_template("TASK.md"|"TASK.fast.md", …, milestone=(milestone or "(none)"))
  -> new TASK.md header line `milestone: <slug|(none)>` matching state.tasks.<slug>.milestone

add.py cmd_set_milestone (after the state write ~l.3763):
    rewrite TASK.md `^milestone: .*$` -> `milestone: <new|(none)>`;
    if no such line exists (grandfathered), INSERT it after the `slug:` line.
  -> file + state stay in lockstep; no drift on move/detach.

add.py cmd_check (per-task loop ~l.2538):
    if a TASK.md `milestone:` line EXISTS and its value != state value (normalizing (none)↔None):
        warnings.append((task, "milestone backlink disagrees with state — re-run set-milestone"))
    absent line -> NO finding (grandfathered; warn-never-block; never feeds `failed`).

Invariants: add.py ×3 byte-identical == re-pinned engine_pin.ENGINE_MD5; TASK.md.tmpl ×3
byte-identical; phases lean pool unchanged (no phase-guide prose).
```

Least-sure flag surfaced at freeze: [contract/test] the `milestone:` header LINE PLACEMENT (a new line after `slug:`) — verified low-risk (header parsers key on line prefixes via regex, not positions; full suite re-run guards it), but it is the one point a sibling header test could trip. Cost if wrong: a localized header-parse fix + re-cross, no contract change. The `(none)` sentinel spelling is a deliberate frozen choice (clean, greppable, never blank).

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete (one test per Must + per Reject)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_new_task_writes_milestone_backlink: init+new-milestone v1 / new-task / assert header `milestone: v1`
  - test_milestone_free_reads_none: deactivate v1 / new-task / assert `milestone: (none)`
  - test_set_milestone_rewrites_on_move_and_detach: new-task / set-milestone v2 then none / assert line tracks each
  - test_check_warns_on_disagreeing_backlink: corrupt the line / check / assert WARN + exit 0
  - test_check_ignores_grandfathered_task_without_line: strip the line / check / assert no finding + exit 0
  - test_template_has_milestone_field_and_is_parity / test_engine_byte_identical_to_pin / test_phases_pool_untouched
</test_plan>

Tests live in: `add-method/tooling/test_milestone_backlink.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/templates/TASK.md.tmpl` `.add/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/tooling/templates/TASK.fast.md.tmpl` `.add/tooling/templates/TASK.fast.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl` `add-method/tooling/test_milestone_backlink.py` `add-method/tooling/test_fast_lane_template.py`
Strategy (ordered batches): 1. TASK.md.tmpl: add `milestone: {{milestone}}` after the `slug:` line. 2. add.py: a `_set_milestone_line(text, value)` helper (rewrite `^milestone:` or insert after `slug:`); cmd_new_task render passes `milestone=(milestone or "(none)")`; cmd_set_milestone rewrites the file after save_state; cmd_check per-task loop WARNs on a present-and-disagreeing line. 3. propagate add.py + template to the 2 twins; re-pin engine_pin (×3) to the new md5; prepare_bundle. 4. full suite green.

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2527/0 (2519 + 8 new)
- [x] coverage did not decrease — new behavior fully guarded; no code path left untested
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the only test edit was the NEW test_milestone_backlink.py (in §5 scope)
- [x] the green was EARNED, not gamed — refute-read below (caught + fixed a real if/elif/else hijack regression mid-build)
- [x] concurrency / timing — n/a (synchronous CLI; `_atomic_write` for the file rewrite)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib re; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — helpers sit beside _render_template; validate-then-write + degrade-safe honored
- [ ] a person reviewed and approved the change — ENGINE/method-trust change → ESCALATED to Tin (this gate is human-approved, not auto-resolved)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] A freshly created task's TASK.md header shows `milestone: <parent>` (or `(none)`) — confirmed: repro showed `milestone: v1`; tests green
- [x] After `set-milestone`, the header line tracks the new parent / detach — confirmed: rewrite test (v2 then none) green
- [x] `add.py check` stays exit-0 and WARNs only on a present-and-disagreeing line; a missing line is silent — confirmed: drift + grandfathered tests green; repro exit-0
- [x] every add.py copy == the re-pinned engine_pin.ENGINE_MD5; TASK.md.tmpl ×3 byte-identical; phases pool ≤ target — confirmed: parity/pin tests green
- [x] full suite green (no sibling header-parser regression) — confirmed: 2527/0 (orphan-guard regression found + fixed)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_milestone_backlink_value`/`_set_milestone_line`/`_read_milestone_line` are referenced by cmd_new_task (render), cmd_set_milestone (rewrite), and cmd_check (drift); each path is test-exercised.
- [x] DEAD-CODE — no orphaned symbol; every helper has a live caller + a test.
- [x] SEMANTIC — read the diffed regions in full: the if/elif/else milestone-resolve chain is intact (the backlink block now sits AFTER it); the template line carries no trailing comment (so new-task and set-milestone render identically).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (a) Is the green gamed? NO — the first full-suite run was RED (test_v8_1_orphan_guard) because my backlink block hijacked the milestone if/elif/else chain; I did NOT weaken that sibling test — I fixed the real defect (moved the block after the chain) and re-ran. (b) Do the tests assert behavior, not internals? Yes — they drive new-task/set-milestone/check via the real CLI and read the rendered file. (c) Is the (none) sentinel real? Yes — milestone-free repro renders `milestone: (none)`. (d) Engine/parity? add.py ×3 == re-pinned pin; template ×3 identical. No overfit, no contract edit.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — no new I/O surface beyond a confined TASK.md read/write under the project root; no secrets, no injection (pure stdlib re on a known header).
2. Concurrency: CLEAR — synchronous CLI; the file rewrite uses `_atomic_write`; degrade-safe on OSError.
3. Architecture: CLEAR — the fast-lane residue was CLOSED by change-request (Tin's call): TASK.fast.md.tmpl ×3 now carry `milestone: {{milestone}}`, a `--fast` task renders the backlink (test_fast_task_carries_backlink + fast-template parity green); the sibling test_fast_lane_template render was updated to pass milestone= (added to §5 scope). add.py + pin UNCHANGED (template-only change).
Verdict: PASS
Residue: none (the fast-template residue was closed this task, not deferred).
Binding: advisory — method/trust (engine change → human-gated; NOT mechanical)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (human-gated; engine/method-trust change; residue closed by his change-request) · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose engine-populated header field — add.py writes + maintains it; rejected template-only field the AI hand-fills (rejected — can drift, doesn't meet "traversable without re-deriving") · a rich node+edge graph (rejected — Tin chose minimal)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang (human-gated; engine/method-trust change; residue closed by his change-request))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
