# TASK: Fidelity trajectory + dip artifacts at WM3 — make mid-run collapses visible

slug: bench-fidelity-dip · created: 2026-07-08 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): benchmark/score.py:score_record — the wm==3 branch already holds prior_fidelities; benchmark/tests/ (new module)
Context (working folder): OLS slope at n=3 reduces to (f3−f1)/2 — the middle WM has ZERO weight, so gsd's wm2=0.50 crash is invisible to context_rot_slope; artifacts precedent: judge_scores · engine_calls
Honors (patterns / conventions): frozen 5-metric set NEVER grows — new signals ship as artifacts
Anchors the contract cites: score_record · artifacts["fidelity_trajectory"] · artifacts["fidelity_min"]
Ground SHA: ec71858

---

## 1 · SPECIFY — the rules

Feature: fidelity trajectory + dip artifacts at WM3
Must:
  - at wm==3, score_record writes artifacts["fidelity_trajectory"] = "f1;f2;f3" (the per-WM spec_fidelity values in order, str-joined like judge_scores)
  - at wm==3, artifacts["fidelity_min"] = str(min(f1, f2, f3)) — the mid-run collapse detector the slope cannot see
  - wm 1/2 records unchanged (priors are only loaded at wm3 — no new reads); frozen 5-metric set untouched
Reject:
  - (none new — wm3 without prior records already raises missing_prior_wm_record upstream)
Accept: Given wm3 scoring with priors 0.97/0.50 and a judged 0.95, When score_record runs, Then artifacts carry fidelity_trajectory "0.97;0.5;0.95" and fidelity_min "0.5" while metrics keys are unchanged.
Assumptions: ⚠ none material — biggest risk: a report reader treats fidelity_min as a 6th metric; the artifact naming + report prose must keep it advisory

---

## 3 · CONTRACT — freeze the shape

```
score_record(arm, 3, ...) -> RunRecord with
  artifacts["fidelity_trajectory"] = "<f1>;<f2>;<f3>"
  artifacts["fidelity_min"]        = "<min>"
frozen: metrics dict keys (5) unchanged; wm1/wm2 artifacts unchanged
```

`Least-sure flag surfaced at freeze:` [spec] float formatting — str(0.5) vs "0.50"; frozen as plain str(value) to match judge_scores precedent; if wrong: cosmetic only
Status: FROZEN @ v1 — approved by Tin Dang (guided confirm 2026-07-08: "yes" to variance-alongside-slope artifact, option 2)

---

## 4 · TESTS — failing-first (red)

Suite: benchmark/tests/test_fidelity_dip.py — 3 tests (dip trajectory+min · flat trajectory ·
wired into the wm==3 branch only). RED confirmed: collection ImportError on
`_fidelity_artifacts` — red for the right reason.

---

## 5 · BUILD — AI writes code

Scope (may touch): `./src/`   <every file the build may write — declared before the §3 freeze>
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass — benchmark suite 105 green (3 new); no test or contract altered during build
- [x] green was EARNED — dip case asserts the exact gsd-shaped trajectory; branch-placement test pins wm3-only wiring
- [x] no security surface — pure artifact computation, no new deps

Build expectations (from §1 Accept + §3 CONTRACT): wm3 records carry fidelity_trajectory + fidelity_min — confirmed by benchmark/tests/test_fidelity_dip.py; visible in the enforced rerun's wm3 record.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08

