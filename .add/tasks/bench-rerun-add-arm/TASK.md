# TASK: Re-run add arm on the lean loop vs round-3 baseline

slug: bench-rerun-add-arm · created: 2026-07-07 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — measurement task; the trust floor still holds.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): benchmark/pilot.py run-all --arms add (harness unchanged — same fairness triple, same Sonnet wrappers, same oracles/scoring incl. median-of-3 + regression split) · benchmark/runs/baseline-round3/add/ (round-3 records preserved as the comparison baseline)
Context (working folder): lean loop shipped in tasks 1–4 (advance --fill · status --brief/--section · seed-and-defer setup · fast-fit intake); the add arm installs pilotspace-add from THIS repo, so the rerun exercises the lean engine + guides
Honors (patterns / conventions): records-as-ledger resume; baseline never overwritten; comparison uses the SAME judge/scoring pins as the baseline rescore
Anchors the contract cites: run_pilot(arms=["add"]) · baseline-round3 records
Ground SHA: e4ab7f7

---

## 1 · SPECIFY — the rules

Feature: lean-loop add-arm measurement
Must:
  - Run the add arm WM1→WM3 on the lean engine (Sonnet agent + judge wrappers, defaults 1800s/1 retry) with round-3 add records moved to benchmark/runs/baseline-round3/.
  - Score with the shipped pipeline (median-of-3 judge, split regression) and compare per-WM tokens_total, spec_fidelity, context_rot_slope against the baseline in a written comparison appended to PILOT-REPORT.md.
Reject:
  - any WM ends non-done -> report honestly as "lean-loop rerun failed at WMn", never retro-tuned
Accept: Given the lean engine, When the 3 WMs complete and score, Then the comparison table exists with the milestone's 4 measurable exit criteria each marked met/not-met from the numbers.
Assumptions: ⚠ the headless agent actually ADOPTS the batched commands (it learns them from the workspace CLAUDE.md/skill seeds) — if it ignores them, tokens won't drop and the result honestly shows the adoption gap; cost: the milestone loop iterates on adoption, not a wasted run.

---

## 3 · CONTRACT — freeze the shape

```
benchmark/runs/add/wm{1,2,3}/record.json           (lean-loop rerun, status done, scored)
benchmark/runs/baseline-round3/add/wm*/record.json  (untouched baseline)
PILOT-REPORT.md += "## Appendix C — lean-loop add-arm rerun vs round-3 baseline"
  per-WM: tokens (rerun vs baseline vs ≤50% target) · fidelity (±0.05 band) · slope (≥ −0.01)
  + met/not-met verdict per milestone exit criterion
```

`Least-sure flag surfaced at freeze:` [test] adoption — the ≤50% token criterion measures agent BEHAVIOR, not just engine capability; a miss is signal, not harness failure.
Status: FROZEN @ v1 — approved by Tin Dang (milestone task 5, plan confirmed)

---

## 4 · TESTS — failing-first (red)

Plan: the oracle suites ARE the red tests (wm1–wm3, unchanged, red against an empty workspace by construction); the comparison table's existence + baseline immutability asserted at verify by inspection.
Tests live in: `benchmark/workload/*/oracle/` · red pre-run (empty workspace).

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/runs/` (run artifacts only — no source file)
Strategy & known-problem fixes: run backgrounded with the round-3 monitor pattern · resume on transient failures (records-as-ledger) · never touch baseline-round3.
Approach (domain strategy): measurement, correctness-first.
Strategy actually used: as planned; run completed without resume; failure reported honestly per the Reject rule
Code lives in: n/a · Constraints: no harness/source changes during the run (frozen-tree discipline).

---

## 6 · VERIFY — evidence + gate

- [x] 3 rerun records done + scored (median-of-3); baseline-round3 byte-untouched
- [x] Appendix C written — tokens 2/3 MET (−73% aggregate), fidelity NOT MET (uvicorn entry-contract trap on wm1/wm3), honest not-retro-tuned verdicts
- [x] no harness change mid-run

Build expectations (from §1 Accept + §3 CONTRACT): comparison table with 4 exit-criteria verdicts — confirmed by the appended report + record.json values.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07
