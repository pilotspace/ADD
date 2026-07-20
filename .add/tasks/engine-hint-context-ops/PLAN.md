# TASK: Resume line teaches status --section; footer ecosystem teaches --brief

slug: engine-hint-context-ops · created: 2026-07-08 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): add-method/tooling/add.py:2409-2410 (full-`status` resume block) + 2 engine twins; engine_pin.py; new guard test
Context (working folder): Appendix G — post-hint wm1 census: advance --fill ×12 adopted, but status --brief/--section adoption = 0; the resume line still says "read .add/tasks/<slug>/TASK.md" (the WHOLE file, every re-orient — the context-tax driver). Only pin on the wording: test_status_lock_hint asserts "read .add/tasks/" ABSENT in the unlocked-setup case (a NotIn — safe).
Honors (patterns / conventions): moment-of-use > documentation (engine-hint-batch-ops precedent, validated −29%); 3-tree parity + ENGINE_MD5 re-pin; SEAMS _declared_scope pin at add.py:4892 (edit at ~2410 is ABOVE it — the pin WILL drift; re-pin SEAMS line)
Anchors the contract cites: the `resume  :` block's read line
Ground SHA: 797c387

---

## 1 · SPECIFY — the rules

Feature: resume line teaches the cheap context ops at the moment of use
Must:
  - full `status` resume block (active task, phase != done) prints: read the live §body via `add.py status --section <phase>` (whole TASK.md only if the section is not enough) and re-orient next turn via `add.py status --brief`
  - done-task resume branch unchanged; unlocked-setup case still shows NO resume read-line (existing NotIn pin holds)
  - render-only: no verb semantics, no state writes
Reject:
  - (none — render-only)
Accept: Given an active task at build, When `add.py status` prints, Then the resume block names `status --section build` and `status --brief` and no longer instructs reading the whole TASK.md as the first action.
Assumptions: ⚠ agents may still open the whole file out of habit — why: hints steer, not force; if wrong: adoption census stays 0 and the next lever is guide-level (cost: one more rerun to learn it)

---

## 3 · CONTRACT — freeze the shape

```
resume block (phase != done):
  resume  : task '<slug>' is at phase '<ph>'.
            read its live section: add.py status --section <ph>  (whole TASK.md only if needed)
            re-orient next turn: add.py status --brief
frozen: done-branch + unlocked-setup rendering unchanged; 3-tree parity; ENGINE_MD5 re-pinned once; SEAMS line re-pinned
```

`Least-sure flag surfaced at freeze:` [test] unknown suites may pin the old "read .add/tasks/<slug>/TASK.md" line positively — why: resume wording is old; if wrong: migrate each pin forward mechanically
Status: FROZEN @ v1 — approved by Tin Dang (instruction 2026-07-08: "push the ≤50% criterion now")

---

## 4 · TESTS — failing-first (red)

Suite: add-method/tooling/test_hint_context_ops.py — 3 tests (resume names --section <phase> ·
names --brief · old whole-file line replaced · done-branch rendering pinned unchanged).
RED confirmed: 2 failures (resume still prints the whole-TASK.md instruction) —
red for the right reason.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_hint_context_ops.py` · `add-method/tooling/` (pin-migrating guard tests only) · `.add/SEAMS.md` · `benchmark/runs/` · `benchmark/BENCHMARK.md` · `tmp/` · `.add/`
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass — full tooling suite 3206 green in one clean run; no old-wording pin broke (only pin was a NotIn, verified held)
- [x] green was EARNED — live-engine probe asserts both new hints + the old whole-file line gone; done-branch rendering pinned unchanged; ENGINE_MD5 re-pinned 352d8bc2; SEAMS _declared_scope re-pinned 4892→4896 (edit above it)
- [x] no security surface — render-only

Build expectations (from §1 Accept + §3 CONTRACT): resume block teaches status --section <phase> + status --brief — confirmed by test_hint_context_ops + the wm1 rerun's adoption census.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08

