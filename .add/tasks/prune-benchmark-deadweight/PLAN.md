# TASK: Prune benchmark dead weight: hv track + v1 regression fn (pre-merge)

slug: prune-benchmark-deadweight · created: 2026-07-10 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
fast: true
oneshot: true
gate_mode: ai-plan-verify

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `benchmark/workload/hv1|hv2|hv3/` (whole dirs — the WV2 hostile track; hypothesis failed at n=1, human-decided prune 2026-07-10) · `benchmark/score.py:compute_regression_rate` (:190, v1 — zero production callers, §7-delta prune candidate since v2-meter-fixes) · `benchmark/tests/test_wv2_family.py` (6 hv-DATA pins die with the track: hv_base_pair_matches_wm_bytes · hv3_prompt_contradicts_and_pins · hv3_prompt_is_silent_about_tests · hv3_oracle_probes_exist · hv3_oracle_speaks_the_track_shape · hv3_probe_windows_are_disjoint; the 5 family-SEAM pins STAY — fixture-based) · `benchmark/tests/test_pilot_cwd_hardening.py:73` (calls v1 directly — that case dies with the fn) · `benchmark/tests/test_score.py:374-376` (monkeypatches the v1 name with a raising setattr — pin dies with the fn)
Context (working folder): benchmark/results/*.md ledgers + v2/DESIGN.md STAY (the honest record); the WV2 archive lives on the runner machine and its trust report reads records+snapshots only — pruning hv dirs does NOT break `report --trust --family hv` on the archive
Honors (patterns / conventions): the generic `family` seam in score/tamper/pilot/report STAYS (fixture-tested); only the hv workload DATA + its byte-guard go; dead tests are removed WITH their feature per the frozen contract, never to make a build pass
Anchors the contract cites: `benchmark/score.py:compute_regression_rate` · `benchmark/workload/hv{1,2,3}/` · `benchmark/tests/test_wv2_family.py` · `benchmark/tests/test_pilot_cwd_hardening.py` · `benchmark/tests/test_score.py`
Ground SHA: `e0ea737`
Skip rationale: scenarios — mechanical deletion, the one §1 Accept line covers it; observe — one optional delta line at the gate suffices

---

## 1 · SPECIFY — the rules

Feature: prune benchmark dead weight before the main merge — remove the hv hostile track (one-shot workload, hypothesis failed at n=1) and the v1 `compute_regression_rate` (superseded by v2, zero production callers), each with exactly its own dead pins
Must:
  - `benchmark/workload/hv1/`, `hv2/`, `hv3/` deleted entirely (prompts, oracles, survivors, byte-guard target)
  - `benchmark/score.py:compute_regression_rate` (v1) deleted; `compute_regression_rate_v2` untouched
  - the 6 hv-DATA pins in test_wv2_family.py removed WITH the track; the 5 family-SEAM pins (prompt_path default · unknown_family fail-loud · family-local oracle resolution · family-keyed snapshots · execute_wm model stamp · pilot CLI --family) kept green — the `family` parameter seam survives the data prune
  - test_pilot_cwd_hardening.py's v1-calling case and test_score.py's v1 monkeypatch pin removed with the fn; every other pin in those files stays byte-identical
  - benchmark/results/ ledgers, v2/DESIGN.md, and all wm workloads untouched (the honest record + the live meter stay)
Reject:
  - any edit to compute_regression_rate_v2, tamper.py, trust.py, report.py, or the family seam -> "seam_overreach"
  - a surviving reference to hv workload paths or the v1 fn anywhere in benchmark/*.py -> "dangling_reference"
Accept: Given the prune is applied, When `python3 -m pytest benchmark/tests/ -q` runs, Then the suite is fully green with zero hv-workload or v1-regression references left in benchmark (guard test asserts: hv dirs absent · `compute_regression_rate` absent from score.py's namespace while `_v2` resolves · no `workload/hv` string in any benchmark/*.py)
Assumptions: ⚠ nothing else imports the v1 fn or reads workload/hv paths at import time — grepped clean at ground (only the 3 named test files); if wrong: an ImportError surfaces loudly in the same suite run, cost = one repair loop

---

## 3 · CONTRACT — freeze the shape

```
DELETE  benchmark/workload/hv1/  hv2/  hv3/          (whole dirs, nothing retained)
DELETE  benchmark/score.py::compute_regression_rate  (v1 only; _v2 byte-identical)
DELETE  test_wv2_family.py::{test_hv_base_pair_matches_wm_bytes, test_hv3_prompt_contradicts_and_pins,
        test_hv3_prompt_is_silent_about_tests, test_hv3_oracle_probes_exist_and_separate_respec_from_gaming,
        test_hv3_oracle_speaks_the_track_shape, test_hv3_probe_windows_are_disjoint}
DELETE  test_pilot_cwd_hardening.py::<the case invoking score.compute_regression_rate at :73>
DELETE  test_score.py::<the v1 monkeypatch pin at :374-376>
ADD     benchmark/tests/test_prune_deadweight.py — the §1 Accept guard (red until the prune lands):
        hv dirs absent · v1 fn absent AND _v2 present · no "workload/hv" reference in benchmark/**/*.py
KEEP    (byte-identical): family seam in score/tamper/pilot/report · the 5 family-seam pins ·
        results/ ledgers · v2/DESIGN.md · every wm workload
```

`Least-sure flag surfaced at freeze:` [test] the no-dangling-reference guard greps "workload/hv" across benchmark/**/*.py — if some file references hv via a computed path (f-string family template) the grep can't see, a dangling runtime path survives the guard; cost = one loud unknown_workload_family error at next use, not silent corruption
Status: FROZEN @ v1 — approved by claude-fable-5
Freeze mode: ai-plan-verify — verified by claude-fable-5 at 2026-07-10T17:01:46+00:00

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §0 GROUND anchors resolve in the current tree — score.py:190 `compute_regression_rate`, the 3 hv dirs, and all 3 test-file line anchors grepped live at ground SHA e0ea737
- [x] §1 every Must + every Reject present, each Reject paired with an error code (`seam_overreach` · `dangling_reference`)
- [x] §3 CONTRACT shape is concrete (no template placeholder text remains) — every deletion named symbol-by-symbol, the KEEP set explicit
- [x] Lowest-confidence flag surfaced and substantive — the computed-path blind spot of the grep guard, with its failure cost
Verified by: claude-fable-5 (session ee9aef91, orchestrator inline) · at: 2026-07-10T18:55:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_prune_deadweight.py — three guards from the §1 Accept: test_hv_track_absent (the 3 dirs gone) · test_v1_regression_fn_absent_v2_present (getattr on score module) · test_no_dangling_hv_references (grep benchmark/**/*.py, excluding the guard file itself). Red now (the track exists); green only when the prune lands. Dead-pin removals happen HERE (tests phase), recorded before the tests→build snapshot — never during build.
Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/` `tmp/`
Strategy & known-problem fixes: 1. tests phase: add the guard file red + remove the 6+2 dead pins 2. build: `git rm -r` the 3 hv dirs 3. delete the v1 fn body 4. full benchmark suite green. Traps: test_score.py's monkeypatch uses raising setattr — remove the WHOLE pin, don't leave a dangling patch; the guard's grep must exclude itself and the results/*.md prose (py files only).
Approach (domain strategy): mechanical deletion, correctness-first — every removal named in the frozen contract, nothing inferred at build time
Strategy actually used: as planned, plus two discoveries — (1) §0's "5 seam pins are fixture-based" was WRONG for test_oracle_resolution_is_family_local (it leaned on the real hv dirs); re-crossed to TESTS and rebuilt it on a SYNTHETIC zz family under a monkeypatched REPO_ROOT — strictly stronger, zero data coupling; (2) `git rm -r` left the dirs alive via untracked __pycache__ plus two junk `hv1 wm1`/`hv2 wm2` dirs from an old zsh word-splitting session bug — rm -rf'd all five
Code lives in: `benchmark/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — benchmark suite 186 passed (190 − 6 hv pins − 1 v1 case + 3 guards = 186, the arithmetic closes); the one mid-build test amendment went through an explicit TESTS re-cross, never in-build
- [x] green was EARNED — the 3 guards assert absence against the real tree (dir existence, module namespace, source grep), not mocks; the amended seam pin now proves family-locality with a synthetic family (stronger than the pre-prune version); reject-codes honored: v2/tamper/trust/report untouched (git status shows only the 4 contracted files + deletions)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — deletion-only build; no new imports, no subprocess changes

Build expectations (from §1 Accept + §3 CONTRACT): full benchmark suite green post-prune with hv dirs gone and v1 fn gone — confirmed: `python3 -m pytest benchmark/tests/ -q` → 186 passed; `ls benchmark/workload/` shows wm1-6 only; ledgers/DESIGN.md/wm workloads byte-untouched (git status clean outside the contracted set)

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (autonomy: auto — complete evidence, deletion-only, no security surface) · date: 2026-07-10
OBSERVE: [SPEC · seeded] the v1 compute_regression_rate prune-candidate delta (open since v2-meter-fixes §7) is CONSUMED by this task — resolve it at the source task (evidence: this §3 DELETE + 186-green suite)

