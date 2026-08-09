# TASK: Freeze echoes resolved scope; proposes a Scope line from §3 Touches

slug: scope-echo-draft · created: 2026-07-13 · stage: mvp
milestone: ceremony-to-effort
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: scope echo + draft at freeze — the scope-token-grammar seam's mis-resolution class (3 tasks independently rediscovered it) becomes a zero-call read at the approval already happening
Must:
  - freeze output echoes each RESOLVED scope entry as `scope: <root-relative> [ok|MISSING]` before the next-footer (footer stays the last line)
  - a declaration whose tokens resolve to nonexistent paths shows `MISSING` at the freeze (e.g. the `./src/` template default in a task with no src/)
  - when the declaration is UNDECLARED, garbage-empty, or every path MISSING: freeze also prints `scope (proposed from §3 Touches): ...` — backticked tokens composed from the Touches paths in the frozen grammar's contains-'/' form
  - propose-not-impose: the TASK.md Scope line is byte-untouched by the proposal; the resolution grammar (_declared_scope) is untouched — echo is a pure read
Reject:
  - any echo/proposal failure blocking a freeze -> fail-open (echo wrapped, freeze output still ends with the footer)
  - writing the proposed line into TASK.md -> never; the agent/human re-drafts and re-freezes deliberately
Accept: Given a plan-phase task whose Scope line still carries the template default and whose §3 Touches names real paths, When freeze runs, Then stdout shows each resolved entry marked MISSING plus a proposed Scope line drawn from Touches, and the TASK.md Scope line is byte-identical.
Boundary: three declaration states — real tokens (echo ok) · default/garbage (MISSING + proposal) · UNDECLARED grandfather (proposal only, no false MISSING)
Assumptions: ⚠ no existing suite pins freeze stdout as ENDING at 'froze §3...' or asserts an exact line count — why: grepped freeze-output asserts, all assertIn-based; if wrong: the fence names the suite and the echo moves/compresses (cost: one re-run)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/tooling/add.py:cmd_freeze (tail prints, after the Ground-SHA stamp block) · add.py:_declared_scope (read-only reuse) · add.py:_raw_phase_bodies (Touches extraction)
Context (working folder): SEAMS.md scope-token-grammar pin (add.py:5526) drifts on this insertion — re-pin; ENGINE_MD5 re-aims
Honors (patterns / conventions): fail-open derived-render (mirrors the Ground-SHA stamp) · footer-last output convention (kickoff-truth) · compose-never-redraw (component-aware-add precedent) · Seams consulted: .add/SEAMS.md#scope-token-grammar
Anchors the contract cites: cmd_freeze · _declared_scope · _raw_phase_bodies
Ground SHA: 7728f2b — stamped by freeze

### Contract

```
_scope_echo(root, slug) -> None   (new helper; prints, never writes)
  resolved = _declared_scope(root, slug)
  None      -> "scope: UNDECLARED (grandfathered)" + proposal
  []        -> "scope: every token dropped — a garbage declaration grants NO cover" + proposal
  [entries] -> per entry: "scope: <rel> [ok]" | "scope: <rel> [MISSING]"
  proposal (only when None / [] / all MISSING):
    paths = path-like heads of §3 'Touches' lines (token before ':', containing '/')
    "scope (proposed from §3 Touches): `<p1>` `<p2>` ..." (dedup, root-relative, grammar's contains-'/' form)
cmd_freeze: after the froze-print, before the footer:
    try: _scope_echo(root, slug)
    except Exception: pass          # fail-open — echo never blocks a freeze
No state.json change · no TASK.md change beyond the existing freeze writes.
```

`Least-sure flag surfaced at freeze:` [contract] the Touches path-head heuristic (token before ':' containing '/') may under-extract real paths on prose-y Touches lines — why: Touches is free prose; if wrong: the proposal is thin, never wrong-format (cost: agent falls back to hand-drafting, today's behavior)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/../.add/` `.add/tooling/` `add-method/.add/`
Strategy & known-problem fixes: 1) red tests test_scope_echo_draft.py 2) _scope_echo helper + cmd_freeze call 3) engine sync x3 + ENGINE_MD5 re-pin 4) SEAMS scope-token-grammar line re-pin 5) fence. Traps: footer must stay the LAST stdout line; echo must not fire on the reject path (freeze refusals die before it — placement after the atomic write guarantees it); never sync test files into twins.
Approach (domain strategy): pure-read derived render, fail-open, compose-never-redraw

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (cmd_freeze tail + _declared_scope read this session)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (Touches path-head heuristic)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T13:05:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_echo_ok (real dir token -> [ok]) · test_echo_missing_default (./src/ default -> MISSING) · test_proposal_from_touches (default scope + real Touches -> proposed line, Scope line byte-identical) · test_undeclared_grandfather (no Scope line -> UNDECLARED + proposal, no MISSING noise) · test_footer_stays_last (freeze stdout still ends with the next-footer) · test_reject_path_no_echo (refused freeze prints no scope: lines).
Tests live in: `add-method/tooling/test_scope_echo_draft.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned, with two ground corrections found red-side: (1) a second freeze on a FROZEN contract is a benign exit-0 no-op notice, not a die — the R2 test now pins the no-op prints no echo; (2) the `./src/` template default is REAL (new-task scaffolds a task-local src/), so the MISSING fixture uses a token no tree provides (`pkg/nope/`). Both are §4-phase test amendments via the sanctioned phase-tests step-back, before any build edit touched them.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (fence 3476/3476 OK; §4 amendments happened in the tests phase via the sanctioned step-back, before build edits)
- [x] green was EARNED — the 6 tests drive a REAL board through the CLI (init/lock/new-task/freeze) and assert stdout + file bytes; no fixture the echo could overfit
- [x] input dialect held — three declaration states (real · dead · UNDECLARED) each pinned by its own test, per the §1 Boundary
- [x] no exposed secrets, injection openings, or unexpected dependencies (stdlib-only pure read; the git-free echo path never shells out)

Build expectations (from §1 Accept + §3 CONTRACT): freeze stdout shows each resolved scope entry [ok|MISSING], proposes a Scope line from §3 Touches when the declaration is dead, and the TASK.md Scope line stays byte-identical — confirmed by test_scope_echo_draft (6/6) + this task's OWN freeze echoing its 5 tokens live.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

