# TASK: Engine next-hints teach advance --fill at the moment of use

slug: engine-hint-batch-ops · created: 2026-07-08 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): add-method/tooling/add.py:~5741-5750 (the `next:` footer composer — `command = "add.py advance"` branch) + 2 engine twins; engine_pin.py (ENGINE_MD5 re-pin); new guard test
Context (working folder): enforced wm1 census — 208 engine calls, ZERO uses of advance --fill/status --brief/status --section; the lean ops exist but are undiscoverable: the workspace agent only sees the engine's own output. The footer is the one line every turn reads.
Honors (patterns / conventions): 3-tree engine byte parity + ENGINE_MD5 pin; SEAMS.md pins _declared_scope at add.py:4892 (edit is BELOW it — verify unshifted); hint text feeds slang-guard spans
Anchors the contract cites: the footer composer's `command` expression · PHASE-conditional fill hint
Ground SHA: d16cb53

---

## 1 · SPECIFY — the rules

Feature: next-hint teaches the batch form at the moment of use
Must:
  - for section-drafting phases (ground · specify · scenarios · contract · tests) the `next:` footer prints `add.py advance --fill <draft>` as the command instead of bare `add.py advance`
  - build/observe hints unchanged (`advance` — those phases produce code/notes, not a fillable §body first); verify's gate hint unchanged
  - pure hint-text change: no verb semantics, no new flags, no state writes
Reject:
  - (none — render-only)
Accept: Given a task at specify, When any engine verb prints its footer, Then it reads `next: add.py advance --fill <draft> — state every rule [human gate]`; Given build, Then the bare `advance` hint is unchanged.
Assumptions: ⚠ prose-pin guards may pin the exact old footer string in some test — why: hints are pinned often; if wrong: migrate the pin forward (doc-truth ripple, never weaken)

---

## 3 · CONTRACT — freeze the shape

```
footer command = "add.py advance --fill <draft>"  when phase in {ground, specify, scenarios, contract, tests}
               | "add.py gate ..."                when verify   (unchanged)
               | "add.py advance"                 otherwise    (unchanged)
frozen: no engine semantics change; 3-tree parity; ENGINE_MD5 re-pinned once
```

`Least-sure flag surfaced at freeze:` [test] how many existing suites pin the bare footer string — why: footer text appears in many transcripts-of-record tests; if wrong: each pin migrates forward mechanically
Status: FROZEN @ v1 — approved by Tin Dang (guided confirm 2026-07-08: "yes" to engine-hint-batch-ops proposal)

---

## 4 · TESTS — failing-first (red)

Suite: add-method/tooling/test_hint_batch_ops.py — 1 ordered-walk test (drafting phases
ground→tests print `advance --fill <draft>`; build reverts to bare `advance`; single test so
no cross-test ordering dependency). RED confirmed: current footer prints bare `advance` at
every phase — red for the right reason.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_hint_batch_ops.py` · `add-method/tooling/` (pin-migrating guard tests only) · `.add/SEAMS.md` · `benchmark/runs/` · `tmp/` · `.add/`
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass — full tooling suite 3203 green in one clean run (no footer-pin ripple); test probe corrected to `status --brief` + bare-branch source pin via re-cross (guarded tests→build refusal made the cheap walk stop at tests — floor working as designed)
- [x] green was EARNED — live-engine walk over all five drafting phases; ENGINE_MD5 re-pinned 3745c847; SEAMS `_declared_scope` pin verified unshifted at 4892
- [x] no security surface — render-only hint text

Build expectations (from §1 Accept + §3 CONTRACT): every drafting-phase footer teaches `advance --fill <draft>` — confirmed by test_hint_batch_ops + the next add-arm run's census (adoption > 0).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08

