# TASK: freeze scope echo emits a paste-ready §5 Scope line when declared tokens miss §3 Touches

slug: scope-first-draft · created: 2026-07-14 · stage: mvp
milestone: call-residuals
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: paste-ready scope line at freeze — when the declared §5 Scope resolves [ok] but MISSES a §3 Touches path, the freeze scope-echo prints ONE ready-to-paste corrected "Scope (may touch): …" line (declared tokens + the uncovered Touches paths), so the agent fixes scope AT freeze instead of hitting a post-freeze re-cross repair (the measured lever).
Must:
  - when `_scope_echo` finds ≥1 §3 Touches path NOT covered by a resolved, non-empty declared scope, it prints a single paste-ready line: `scope (paste-ready — declared misses §3 Touches): Scope (may touch): <declared tokens + the uncovered Touches paths, space-joined, deduped>`
  - the paste-ready line is propose-not-impose: printed to stdout, never written into TASK.md
  - unchanged: the per-token "note: §3 Touches cites <tok> outside the declared scope" lines, and the UNDECLARED / garbage / all-missing "scope (proposed …)" path
Reject:
  - none — pure additive echo; no gate / scope ENFORCEMENT change (milestone OUT-of-scope)
Accept: Given a frozen task whose §5 Scope resolves [ok] but omits a §3 Touches path, When the scope echo runs at freeze, Then stdout contains a paste-ready "Scope (may touch): …" line that merges the declared tokens with the uncovered Touches path
Boundary: none — reads TASK.md §3 Touches + the §5 declaration only; no external input shape
Assumptions: ⚠ the too-narrow §5 is the dominant post-freeze re-cross cause (task 1 init-idempotent-nudge just hit it) — a paste-ready line turns a re-derive into a copy-paste; if wrong (agent ignores the line): no harm, still propose-only

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): `add-method/tooling/add.py:_scope_echo` — the ONLY symbol edited (add the paste-ready branch after the per-token "note:" loop, ~L1073-1077); it READS `_touches_paths` · `_in_scope` · `_declared_scope` unchanged
Context (working folder): `add-method/tooling/` (canonical engine). The full file write-set — canonical add.py, its 3 engine twins, engine_pin.py, the new test — is the §5 Scope below (not re-listed here); ENGINE_MD5 + SEAMS `_declared_scope` pin re-aimed as part of any engine edit
Honors (patterns / conventions): propose-not-impose (PRINT, never write TASK.md); `_scope_echo` is already fail-open-wrapped at its freeze call site; reuses `_in_scope`/`_touches_paths` — no parallel predicate
Anchors the contract cites: `_scope_echo` (edited) · `_touches_paths`, `_in_scope`, `_declared_scope` (read)
Ground SHA: 9c4eeeb — stamped by freeze

### Contract

```
_scope_echo, resolved declared scope is non-empty AND ≥1 §3 Touches path is not _in_scope(tok, resolved):
  → (unchanged) per uncovered tok: "note: §3 Touches cites <tok> outside the declared scope"
  → (NEW) exactly one line: "scope (paste-ready — declared misses §3 Touches): Scope (may touch): <T>"
          where <T> = the resolved declared tokens followed by each uncovered §3 Touches path,
          space-joined, order-preserving, de-duplicated
  → printed to stdout only; TASK.md is NOT written
_scope_echo, all other cases (UNDECLARED · every-token-dropped · all-[MISSING] · fully-covered):
  → unchanged (existing "scope (proposed from §3 Touches): …" behaviour intact)
```

`Least-sure flag surfaced at freeze:` [contract] the exact prefix wording of the paste-ready line ("scope (paste-ready — declared misses §3 Touches):") — if wrong, cosmetic one-string change, no behaviour shift.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/.add/tooling/engine_pin.py` `add-method/tooling/test_scope_first_draft.py`
Strategy & known-problem fixes: (1) in `_scope_echo`, in the `else` (non-empty resolved) branch, after the per-token note loop, collect `uncovered = [tok for tok in _touches_paths() if not _in_scope(tok, resolved)]`; if `uncovered`, print the paste-ready line merging `resolved + [u for u in uncovered if u not in resolved]` (trap: dedupe + preserve order; do NOT touch the UNDECLARED/garbage/all-missing block below it). (2) red test first: a task whose §5 resolves [ok] but whose §3 Touches names a wider real path → echo stdout contains "Scope (may touch):" + the missing path (declare the full §5 scope UP FRONT — the task-1 lesson). (3) sync ×4 twins, re-pin ENGINE_MD5 + SEAMS.
Approach (domain strategy): message-layer only — one additive echo branch reusing existing predicates; propose-not-impose, correctness-first, zero enforcement change.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — in `_scope_echo`'s non-empty-resolved branch, collected `uncovered = [tok for tok in _touches_paths() if not _in_scope(tok, resolved)]` (one list, reused by the existing per-token note loop), and when non-empty printed ONE `scope (paste-ready — declared misses §3 Touches): Scope (may touch): <declared + uncovered, order-preserving, deduped>` line. Zero enforcement change; the UNDECLARED/garbage/all-missing "proposed" block below is untouched. Synced ×4 twins, ENGINE_MD5→3b438d30, SEAMS _declared_scope pin 5670→5677.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (full fence exit 0)
- [x] green was EARNED — RED confirmed first (uncovered case failed for want of the line; the two guards passed), then GREEN after the additive branch
- [x] input dialect held — test fixtures speak the real §3 Touches / §5 backticked-token dialect
- [x] no exposed secrets, injection openings, or unexpected dependencies (pure read/print, security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): a frozen task whose §5 Scope resolves [ok] but omits a §3 Touches path makes the freeze scope-echo emit ONE paste-ready "scope (paste-ready — declared misses §3 Touches): Scope (may touch): <declared + uncovered>" line to stdout, merging declared tokens with the uncovered Touches path, deduped/order-preserving, writing nothing to TASK.md; fully-covered and UNDECLARED/garbage/all-missing cases unchanged — confirmed by test_scope_first_draft (3 asserts: emits-when-uncovered · silent-when-covered · never-writes) + green parity/seams/engine guards.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

