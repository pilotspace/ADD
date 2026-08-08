# TASK: Seed WM(k) workspace from WM(k-1) — make the benchmark truly longitudinal

slug: bench-carry-forward · created: 2026-07-08 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): benchmark/runner/core.py:execute_wm (workspace creation, line ~227) — new _seed_from_prior helper; benchmark/tests/ (new module)
Context (working folder): wm2/wm3 PROMPT.md assume the prior milestone's app exists; the harness gave every WM a fresh dir — prior runs masked it by rebuilding from scratch (A4 delta CONFIRMED by the enforced rerun: the add agent honestly refused an empty wm3). Resume path re-enters execute_wm with a populated workspace — seeding must be fresh-workspace-only.
Honors (patterns / conventions): setup_steps recreate .venv per WM (excluded from the copy); records/workspaces under benchmark/runs are runtime artifacts
Anchors the contract cites: execute_wm · _seed_from_prior
Ground SHA: 92077f2

---

## 1 · SPECIFY — the rules

Feature: WM(k) workspace seeded from WM(k-1)
Must:
  - for wm>1, when the WM's workspace is empty (fresh run) and wm(k-1)/workspace exists, execute_wm copies it in BEFORE setup steps — excluding `.venv` (recreated by setup) — so the prior milestone's app/tests/agent-state carry forward
  - wm==1 unchanged; a NON-empty workspace (resume/retry) is never overwritten
  - copy failure -> record status "failed" with the reason in attempts (never a silent fresh start)
Reject:
  - prior workspace missing for wm>1 -> proceed unseeded (wm run from scratch stays possible; the record notes "unseeded")
Accept: Given wm2 with an empty workspace and a wm1 workspace containing app/main.py, When execute_wm prepares the workspace, Then app/main.py exists in wm2's workspace, .venv was not copied, and the seeding is noted in attempts.
Assumptions: ⚠ copying .add state carries the PRIOR milestone's task history — intended (longitudinal), but the agent may resume rather than start the new milestone; if wrong: prompts still state the new WM goal (cost: none to metrics)

---

## 3 · CONTRACT — freeze the shape

```
_seed_from_prior(workspace_dir, arm_name, wm, runs_root) -> str | None
  # returns a one-line note ("seeded from wm<k-1>" | "unseeded: no prior workspace" | None for wm1/non-empty)
  # copies wm(k-1)/workspace -> workspace_dir, ignore=.venv; raises nothing — failures return via BenchError
execute_wm: calls it right after workspace mkdir, appends the note to attempts_log
frozen: record schema unchanged; wm1 byte-identical behavior
```

`Least-sure flag surfaced at freeze:` [test] "empty workspace" detection — any(iterdir()) vs allowing stray .DS_Store; frozen as any-entry = non-empty (strict); if wrong: a junk file blocks seeding (visible in attempts)
Status: FROZEN @ v1 — approved by Tin Dang (guided confirm 2026-07-08: "Seed WM(k) from WM(k-1)")

---

## 4 · TESTS — failing-first (red)

Suite: benchmark/tests/test_carry_forward.py — 5 tests (seed app + exclude .venv · wm1 never
seeds · non-empty workspace untouched (resume-safe) · missing prior notes unseeded ·
execute_wm wiring). RED confirmed: collection ImportError on `_seed_from_prior` —
red for the right reason.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/runner/core.py` · `benchmark/tests/test_carry_forward.py` · `benchmark/runs/` · `tmp/` · `.add/`
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass — benchmark suite 110 green (5 new); no test or contract altered during build
- [x] green was EARNED — resume-safety and .venv-exclusion asserted directly; wiring test pins the call site after mkdir
- [x] no security surface — local copytree within benchmark/runs; no new deps

Build expectations (from §1 Accept + §3 CONTRACT): wm2/wm3 workspaces start with the prior WM's app; the seeding note appears in attempts — confirmed by the seeded rerun's records.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08

