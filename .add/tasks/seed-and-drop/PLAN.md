# TASK: Seed/drop verbs — resolve an open SPEC delta into a task or dismiss it

slug: seed-and-drop · created: 2026-06-16 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
  - `add-method/tooling/add.py:cmd_new_task` (460-515) — scaffolds a task: validates slug/milestone, renders TASK.md via `_render_template`, writes the `state["tasks"][slug]` entry (title·phase·gate·milestone·depends_on·created·updated). SEED extends it: a `--from-delta <prior>` flag reads the prior's open SPEC delta, pre-fills the new §1 `Feature:` line, and records `from_delta: <prior>` lineage.
  - `add-method/tooling/add.py` new-task subparser (4668-4675) — `pn.add_argument(...)`; add `--from-delta <prior-slug>`.
  - `add-method/tooling/add.py:_collect_open_spec_deltas` (3925) + `_spec_delta_entries` (3922) + `_SPEC_DELTA_RE` (3765) — task-1 READERS of the `### Spec delta` block; reused to find the prior's first OPEN SPEC delta (text + line). NO existing writer flips a delta status — that is NEW here.
  - NEW `_resolve_spec_delta(text, new_status, pointer=None)` — PURE transformer: rewrite the FIRST `[SPEC · open]` line → `[SPEC · seeded] … [→ <pointer>]` or `[SPEC · dropped]`; returns None when there is no open SPEC delta (caller refuses, no write — validate-all-then-write).
  - NEW `cmd_drop_delta` + `drop-delta` subparser — the DROP verb: flips a task's open SPEC delta → `dropped` (dismiss without a task). Drop cannot live on `new-task` (it creates nothing).
  - `add-method/tooling/add.py:_atomic_write` (159) — temp-file-then-os.replace; the durable per-file write for both the new TASK.md and the prior-task flip.
  - `add-method/tooling/add.py:_resolve_task` (549) — slug→validated-task guard, reused by `drop-delta` and to validate `--from-delta <prior>`.
Context (working folder):
  - tests (unittest): `add-method/tooling/test_*.py`; NEW `test_seed_and_drop.py`. Touches none existing (additive verbs). Baseline green: 1169 OK.
  - parity: the 3 md5-identical `add.py` copies + `prepare_bundle.py` + `engine_pin.py` — re-sync after the canonical edit (same discipline as task 1's §5 ADD lesson).
Honors (patterns / conventions):
  - design-for-failure (CLAUDE.md): validate-ALL-then-write — prove prior-exists · prior-has-open-SPEC · new-slug-free BEFORE any write; per-file `_atomic_write`; cross-file residue (new TASK.md written but prior-flip fails) named in §5 + verified.
  - the pure-transform + caller-atomic-write pattern already used by `_autonomy_decl_line` (789); SPEC statuses `seeded`/`dropped` were TOLERATED on read by task 1 — this task is their FIRST writer.
  - MILESTONE shared decision: a SPEC delta resolves into a TASK (seeded) or is dismissed (dropped) — never folded; the `[→ <new>]` stamp is the seed provenance.
Anchors the contract cites: `cmd_new_task` · `new-task --from-delta` · `_resolve_spec_delta` · `cmd_drop_delta` / `drop-delta` · `_collect_open_spec_deltas` · `_SPEC_DELTA_RE` · `_atomic_write` · `state["tasks"][slug].from_delta`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: SPEC-delta resolution verbs — `new-task --from-delta <prior>` (SEED an open SPEC delta into a new task) and `drop-delta <task>` (DISMISS one) — the first WRITERS that move a SPEC delta off `open`.
Framings weighed: seed on `new-task --from-delta` + drop as its own `drop-delta` verb (chosen — seed inherently scaffolds a task, drop creates nothing) · one unified `spec-delta <task> --seed|--drop` (rejected — seed would duplicate new-task's whole scaffold job) · a `--drop` flag on `new-task` (rejected — nonsensical, drop makes no task)
Must:
<must>
  - `new-task <new-slug> --from-delta <prior-slug>`: read the prior's FIRST open SPEC delta; pre-fill the new task's §1 `Feature:` line with that delta text + a trailing ` (from <prior-slug> spec-delta)` provenance note; flip the prior's `[SPEC · open]` → `[SPEC · seeded]` and append a ` [→ <new-slug>]` pointer stamp; record `from_delta: <prior-slug>` in `state["tasks"][<new-slug>]`. All other new-task behavior (slug/milestone validation, tests/+src/ scaffold, depends_on) unchanged.
  - `drop-delta <task-slug>`: flip that task's FIRST open SPEC delta `[SPEC · open]` → `[SPEC · dropped]`, leaving text + `(evidence: …)` intact. Writes that one file, nothing else.
  - Both verbs operate on the FIRST open SPEC delta in source order — one resolution per invocation; re-run to resolve the next.
  - The flip changes ONLY the status token (plus the `[→ <new>]` stamp for seed); the entry text and `(evidence: …)` are byte-preserved.
  - Validate-ALL-then-write: prove (prior/task exists · it has ≥1 open SPEC delta · for seed: new-slug valid & free · milestone valid) BEFORE any write; on any failure refuse with a named code and write NOTHING. The flip is computed by the pure `_resolve_spec_delta` ahead of the durable `_atomic_write`.
  - A resolved (seeded/dropped) source delta is thereafter EXCLUDED from `_collect_open_spec_deltas` — resolving consumes the open nudge (verified via `deltas`).
</must>
Reject:
<reject>
  - `--from-delta <prior>` / `drop-delta <task>` where the task has NO open SPEC delta -> "no_open_spec_delta"
  - either verb naming an unknown task -> "unknown task '<slug>'"   (existing `_resolve_task` code)
  - seed where `<new-slug>` already exists -> "task '<slug>' already exists"   (existing new-task guard, unchanged)
  - a prior with MULTIPLE open SPEC deltas is NOT rejected — the first is taken; the rest stay open and keep nudging
</reject>
After:
<after>
  - the source delta reads `[SPEC · seeded] <text> (evidence: …) [→ <new>]` (seed) or `[SPEC · dropped] <text> (evidence: …)` (drop); `add.py deltas` no longer lists it open; for seed a new task exists with the pre-filled `Feature:` + `from_delta` lineage in state; `add.py check` stays green (task-1 lint tolerates seeded/dropped); full unittest suite + 3-copy md5 parity stay green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "FIRST open SPEC delta" is the right selector when a task holds several — lowest confidence because a human may mean a specific one; if wrong: the wrong delta is seeded/dropped (recoverable by hand-editing the status back to `open`, but noisy). A `--match <substr>` selector is the considered alternative, deferred unless the freeze asks for it.
  - [ ] drop is a SEPARATE `drop-delta` verb, not a `new-task` flag — confirm the command surface at the freeze (the §3 shape decision).
  - [ ] seed writes TWO files + state (new TASK.md, prior flip, state.json); there is no cross-file transaction. Mitigation: validate-all-then-write + per-file atomic write; residue = "new task created, prior flip failed" → re-run blocked by the slug-exists guard, prior stays open & visible. Confirm this ordering is acceptable (named in §5, checked in verify).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: seed creates a task and consumes the source delta
  Given a prior task whose §7 holds "- [SPEC · open] rate-limit retries (evidence: herd)"
  When I run `new-task followup --from-delta prior`
  Then task 'followup' exists with §1 Feature "rate-limit retries (from prior spec-delta)"
  And the prior delta now reads "[SPEC · seeded] rate-limit retries (evidence: herd) [→ followup]"
  And state["tasks"]["followup"]["from_delta"] == "prior"
  And the delta's "(evidence: herd)" text is unchanged

Scenario: drop dismisses the source delta without creating a task
  Given a task whose §7 holds "- [SPEC · open] drop idea (evidence: scope)"
  When I run `drop-delta thattask`
  Then the delta now reads "[SPEC · dropped] drop idea (evidence: scope)"
  And no new task directory was created
  And the "(evidence: scope)" text is unchanged

Scenario: only the first open SPEC delta is resolved
  Given a task with TWO open SPEC deltas, "alpha" then "beta"
  When I run `drop-delta thattask`
  Then "alpha" reads "[SPEC · dropped]" and "beta" stays "[SPEC · open]"
  And "alpha"'s text and evidence are unchanged

Scenario: seed refuses when the prior has no open SPEC delta
  Given a prior task with no open SPEC delta (only seeded/dropped/none)
  When I run `new-task followup --from-delta prior`
  Then it exits non-zero with "no_open_spec_delta"
  And no task 'followup' directory was created
  And the prior TASK.md is byte-unchanged

Scenario: drop refuses when the task has no open SPEC delta
  Given a task with no open SPEC delta
  When I run `drop-delta thattask`
  Then it exits non-zero with "no_open_spec_delta"
  And the task TASK.md is byte-unchanged

Scenario: either verb refuses an unknown task
  Given no task named 'ghost'
  When I run `drop-delta ghost`
  Then it exits non-zero with "unknown task 'ghost'"
  And no file was written

Scenario: seed refuses a taken slug WITHOUT consuming the source delta (validate-all-then-write)
  Given a prior with an open SPEC delta AND an existing task 'followup'
  When I run `new-task followup --from-delta prior`
  Then it exits non-zero with "already exists"
  And the prior delta is still "[SPEC · open]" (not seeded) — nothing was written
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py new-task <new-slug> --from-delta <prior-slug> [--title T] [--milestone M] [--depends-on D]
  ok  -> scaffolds tasks/<new-slug>/ (TASK.md + tests/ + src/); §1 "Feature: <delta-text> (from <prior-slug> spec-delta)";
         flips prior's FIRST "[SPEC · open] X (evidence:e)" -> "[SPEC · seeded] X (evidence:e) [→ <new-slug>]";
         state["tasks"][<new-slug>]["from_delta"] = "<prior-slug>"; prints created + seeded lines
  err -> "no_open_spec_delta"                  prior has no open SPEC delta — NOTHING written
         "unknown task '<prior-slug>'"          prior not found (_resolve_task)
         "task '<new-slug>' already exists"     slug taken — prior NOT flipped (validate-all-then-write)

add.py drop-delta <task-slug>
  ok  -> flips task's FIRST "[SPEC · open] X (evidence:e)" -> "[SPEC · dropped] X (evidence:e)"; prints dropped line
  err -> "no_open_spec_delta"                  no open SPEC delta — NOTHING written
         "unknown task '<task-slug>'"           task not found (_resolve_task)

Internal: _resolve_spec_delta(text:str, new_status:str, pointer:str|None=None) -> str | None
  PURE — rewrites only the FIRST "[SPEC · open]" line's status token (+ " [→ <pointer>]" when seeding);
  returns None when no open SPEC delta exists (caller refuses, writes nothing).
State:  state["tasks"][<new-slug>]["from_delta"] = "<prior-slug>"   (NEW key; seed only; absent for normal new-task)
Files:  seed → _atomic_write(new TASK.md) + _atomic_write(prior TASK.md flip);  drop → _atomic_write(task TASK.md flip)
Stages: 3 byte-identical add.py copies re-synced; engine_pin ENGINE_MD5 re-aimed (no template change this task)
```

Least-sure flag surfaced at freeze: [spec] the "FIRST open SPEC delta" selector — when a task holds several open SPEC deltas both verbs take the first in source order; if a human meant a specific one the wrong delta is seeded/dropped (recoverable by editing the status back to `open`, but noisy). Pinned by test_only_first_open_resolved; a `--match <substr>` selector was weighed and deferred. (Runner-up [contract]: seed's cross-file write has no transaction — validate-all-then-write makes the worst residue "new task created, prior still open & visible", pinned by test_seed_taken_slug_no_consume.)

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-16
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject has a test (7 scenarios → ≥7 tests); full suite stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_seed_creates_task_and_seeds_source: prior open SPEC delta / new-task X --from-delta prior / assert task X exists, §1 Feature has "(from prior spec-delta)", prior line == "[SPEC · seeded] … [→ X]", state[X].from_delta == "prior", evidence text unchanged
  - test_drop_dismisses_without_task: task open SPEC delta / drop-delta t / assert line == "[SPEC · dropped] …", evidence intact, NO new task dir
  - test_only_first_open_resolved: task w/ TWO open SPEC deltas / drop-delta t / assert first == dropped, second still open
  - test_seed_no_open_refuses: prior w/o open SPEC delta / new-task X --from-delta prior / assert exit≠0 + "no_open_spec_delta", task X NOT created, prior bytes unchanged
  - test_drop_no_open_refuses: task w/o open SPEC delta / drop-delta t / assert exit≠0 + "no_open_spec_delta", bytes unchanged
  - test_unknown_task_refuses: drop-delta ghost / assert exit≠0 + "unknown task 'ghost'", nothing written
  - test_seed_taken_slug_no_consume: existing task X + prior open delta / new-task X --from-delta prior / assert exit≠0 + "already exists" AND prior delta still "[SPEC · open]" (validate-all-then-write)
  - test_resolve_spec_delta_pure_none: _resolve_spec_delta(text-with-no-open, "dropped") returns None (unit, no write)
  - (regression) existing new-task tests + add.py check + bundle/tree parity stay green
</test_plan>

Tests live in: `add-method/tooling/test_seed_and_drop.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_seed_and_drop.py` `add-method/tooling/test_min_pillar.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py`
<!-- pre-declared up front per task-1's ADD lesson (avoid a mid-build scope expansion): the 3 byte-identical add.py copies + engine_pin re-pin + the new red suite. NO template change this task (the §7 block already shipped in task 1).
     EXPANDED mid-build (disclosed, re-crossed tests→build to re-anchor the scope snapshot): the NEW `drop-delta` SUBCOMMAND tripped test_min_pillar.test_every_subcommand_is_covered — a read-spy census that derives the full command set from the parser and requires every command to appear in its LIFECYCLE. My pre-build grep (add_parser/--help/COMMANDS) MISSED it because the census reads `sub.choices` DYNAMICALLY, not a literal list. Fix: added `["drop-delta","t"]` to LIFECYCLE + `drop-delta` to _NONZERO_OK (task t holds no open SPEC delta → refuses no_open_spec_delta, the existing refusal-verb pattern). NOT a weakening — the census got STRONGER (one more command proven docs-silent). A `--from-delta` FLAG adds no subcommand, so it did not trip it. Refined lesson recorded as a §7 TDD delta. -->
Strategy (ordered batches): 1. write the red suite test_seed_and_drop.py · 2. `_resolve_spec_delta` pure transformer (first-open status flip + optional [→ ptr] stamp; None when none) · 3. `cmd_drop_delta` + `drop-delta` subparser · 4. `--from-delta` on cmd_new_task + subparser (read prior open delta → prefill Feature → flip prior → from_delta state) · 5. sync .add/tooling + prepare_bundle, re-pin engine_pin, assert 3-copy parity
Safety rule (feature-specific): validate-ALL-then-write — for SEED, compute the prior flip (pure `_resolve_spec_delta`) AND assert the new slug is free BEFORE writing anything; order writes new-TASK.md → prior-flip → state so the worst residue is "new task exists, prior still OPEN & visible" (re-run blocked by slug-exists; never a dangling [→] pointer at an absent task). Each file via `_atomic_write`.
Code lives in: `add-method/tooling/` (engine) — NOT this task's `./src/`.
Constraints: do NOT change any test's intent or the frozen contract; allow-list packages only (stdlib only); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1177 OK (0 fail); baseline 1169 → +8 new seed-and-drop
- [x] coverage did not decrease — +8 tests; census STRENGTHENED (drop-delta added to test_min_pillar LIFECYCLE — one more command proven docs-silent)
- [~] no test or contract was altered during build — CONTRACT untouched. ONE test edit DISCLOSED: test_min_pillar.py — the NEW `drop-delta` subcommand tripped the read-spy census (test_every_subcommand_is_covered, derives commands from `sub.choices`); added `["drop-delta","t"]` to LIFECYCLE + `drop-delta` to _NONZERO_OK. This is an EXTENSION (census got stronger), NOT a weakening. §5 scope expanded to include test_min_pillar.py + re-crossed tests→build to re-anchor the scope snapshot.
- [x] the green was EARNED — live adversarial proof on the dogfood engine (not fixtures): seed flips `[SPEC · open]`→`[SPEC · seeded] … [→ followup]` (evidence byte-preserved) + pre-fills Feature provenance + records from_delta; drop flips ONLY the first open (seeded sibling untouched); taken-slug refusal leaves the source delta OPEN (validate-all-then-write proven — nothing consumed). `add.py check` stays green with seeded/dropped present.
- [x] concurrency / timing — N/A: single-process CLI, no shared state. validate-ALL-then-write (resolve prior · prove open delta · compute flip BEFORE any write); per-file `_atomic_write`; ordered new-TASK.md → prior-flip → state.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; the Feature pre-fill uses a LAMBDA `re.sub` replacement so delta text can never inject a backreference; no eval/shell/network.
- [x] layering & dependencies follow CONVENTIONS.md — pure transformer + caller-atomic-write (mirrors `_autonomy_decl_line`); single-source grammar REUSED (`_SPEC_DELTA_RE`, no second SPEC regex); 3-copy md5 parity restored (5120b0c2a42e56a196ad5e30b1d8754e); engine_pin re-aimed newest-first.
- [x] a person reviewed and approved the change — Tin Dang, 2026-06-16 (gate PASS; census edit + §5 expansion disclosed)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: _resolve_spec_delta ×2 calls (cmd_new_task seed flip · cmd_drop_delta) · _first_open_spec_text ×1 (cmd_new_task) · _SPEC_OPEN_TOKEN_RE ×1 (in _resolve_spec_delta) · cmd_drop_delta wired to the `drop-delta` subparser · `--from-delta`→from_delta read in cmd_new_task
- [x] DEAD-CODE (code) — no orphaned symbol; each new function/constant has a live call site (counts above)
- [x] SEMANTIC (prose) — §5 disclosure + the §7 TDD delta (census-ripple lesson) read in full; provenance/stamp formats match the contract

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-16   (disclosed: test_min_pillar census EXTENSION + §5 scope expansion + re-cross — no contract/security)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-verb refusal rate (`no_open_spec_delta` · `already exists`) · `deltas` open-spec count drop after a seed/drop

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task.
  - [SPEC · seeded] add a `--match <substr>` selector to `new-task --from-delta` and `drop-delta` so a specific open SPEC delta can be targeted when a task holds several (evidence: the v1 freeze took "first-open" as the coarse default and deferred this — flagged the bundle's lowest-confidence point) [→ delta-match-selector]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [TDD · folded] a new SUBCOMMAND ripples into test_min_pillar's LIFECYCLE census, which derives the command set from `sub.choices` DYNAMICALLY — grep `LIFECYCLE`/`sub.choices`/`_NONZERO_OK` before adding a subcommand, not just `add_parser`/`--help` (evidence: `drop-delta` tripped test_every_subcommand_is_covered after a clean pre-build grep, forcing a §5 expansion + re-cross) [folded foundation-version 36]
  - [ADD · folded] verb-vs-flag sizes the census ripple: a new FLAG on an existing command (`--from-delta`) adds no subcommand and is census-free, but a new SUBCOMMAND (`drop-delta`) costs a LIFECYCLE entry — declare the census file in §5 up front whenever a task adds a subcommand (evidence: the flag was free, the verb was not) [folded foundation-version 36]
