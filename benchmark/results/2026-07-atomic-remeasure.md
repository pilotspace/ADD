# Atomic-template remeasure — SWE smoke A/B + cross-milestone session (2026-07-19/20)

The atomic-node change (`0b0192a7` + `121c2feb`: ONE atomic PLAN.md, lanes removed,
host-suite Regression floor, Build-expectations folded into §3 Target) re-run against
the recorded old-template baselines. Same harness, same instances, official swebench
4.1.0 docker eval (`--namespace ''`), same pinned agent.

## SWE smoke — resolve / cost / wall-clock

| Arm | Old template (f08a5334) | Atomic template | Vanilla (recorded) |
|---|---|---|---|
| sonnet-5 | 3/3 · $5.28 · 50.9 min | **3/3 · $5.99 · 28.1 min** | 3/3 · $0.95 · 6.4 min |
| haiku-4.5 | 2/3 · $2.52 | **3/3 · $2.15** | 3/3 · $0.90 |

- **haiku 2/3 → 3/3, and cheaper.** The published against-us instance
  (`psf__requests-863`: fix correct, over-build broke 2 neighboring tests) now fully
  resolves — F2P 4/4, P2P 0. Its patch shrank 1,626B → **559B** (minimal-fix shape).
  The fix that did it is now method, not prompt luck: the template's §3
  `Regression floor:` line + the SWE prompt declaring the HOST repo's suite as that
  floor. Appendix-H prediction 1 flips back in ADD's favor at the tier where it failed.
- **sonnet parity at nearly half the wall-clock.** 3/3 both templates; 50.9 → 28.1 min.
  First eval scored 2317 unresolved on `test_BASICAUTH_TUPLE_HTTP_200_OK_GET` — a
  live-httpbin network test on an instance whose eval ran 14 min vs ~3 min for its
  siblings; a single-instance re-eval (`atomic-add-flakecheck`) resolves it with zero
  P2P failures. Verdict: eval flake, recorded here so the 2/3 in the first run's logs
  is not misread.
- Cost stays ~2.2–6× vanilla on friendly instances — unchanged conclusion from the
  smoke report: ADD buys regression tests + an auditable loop, not cheap patches, and
  friendly instances cannot differentiate on resolve rate at the sonnet tier.

## Cross-milestone session bench — the context-rot claim, remeasured

ADD arm, 6 WMs, `--session-mode continue`: ONE persistent workspace + ONE continuing
conversation (`runs-atomic-session`). Baseline = the conv-carry runs recorded in the
honesty wave (`runs-session`, old template).

| WM | Old fid-trajectory | Old $ | Atomic fid-trajectory | Atomic $ |
|---|---|---|---|---|
| 1 | 0.92 | 0.53 | 1.0 | 1.87 |
| 2 | 0.80 | 2.85 | 1.0 | 2.81 |
| 3 | 0.75 | 2.46 | 1.0 | 2.71 |
| 4 | **0.17** | 4.69 | 1.0 | 3.67 |
| 5 | 0.75 | 8.29 | 1.0 | 3.24 |
| 6 | 1.00 | 3.85 | 1.0 | 3.45 |
| **Σ** | decay slope −.083 | **$22.67** | **flat 1.0 × 6** | **$17.75** |

- **Conversation-carry rot: eliminated in this sample.** Old template decayed
  0.92→0.75 by WM3 and cratered to 0.17 at WM4 (one WM1 deviation never re-examined
  in-conversation). Atomic template holds oracle 1.0 · coverage 1.0 · regressions 0 ·
  fidelity 1.0 at every milestone — and is 22% cheaper with no WM5-style $8 blowup.
  n=1 per mode; directional, not a leaderboard claim.
- `tests_weakened` flags audited benign: WM2=5 is WM1's tests reshaped when auth became
  mandatory (workload-required); WM3=1 is the obsolete `test_create_bad_duration_400`
  removed when the end-time shape banned `duration`. The metric is assert-fingerprint
  departure (disclosed in `tamper.py` as "never auto-labeled cheating"); oracle/
  regression corroborate.
- WM5 first attempt died on a 5-hour API session limit (429), not the method;
  `run_pilot(resume=True)` on the same runs-root reattached the continuing
  conversation and both remaining WMs passed clean.

## Harness defect found and fixed mid-campaign

`install_add` for the SWE arm never seeded the workspace's own `.add/state.json`; an
agent that skips `init` (haiku, all 3 instances) walks ancestor root discovery UP into
**this repo's** `.add` and drives its whole loop there. Fixed in `93360765` (install
ends with the engine `init`; `WorkspaceIsolationTest` pins it). The contaminated first
haiku run is kept at `runs-swe/atomic-mini` (1/3, reference only); the canonical haiku
numbers above are the clean re-run (`runs-swe/atomic-mini2`).

## Same-mode comparison vs spec-kit (recorded arm, not re-run)

Spec-kit's continue-mode board (`runs-session/spec-kit`, wm1–3 recorded; nothing in
the atomic change touches its arm):

| | spec-kit (recorded) | old ADD (recorded) | atomic ADD (new) |
|---|---|---|---|
| Fidelity wm1→2→3 | 0.92 → 0.80 → 0.75 | 0.92 → 0.80 → 0.75 | **1.0 → 1.0 → 1.0** |
| Regression rate wm2 / wm3 | **0.33 / 0.29** | 0 / 0 | 0 / 0 |
| Oracle wm1–3 | 0.8 / 0.8 / 1.0 | 0.8 / 0.8 / 1.0 | 1.0 × 3 |
| Cost wm1–3 | $4.48 | $5.84 | $7.39 |

- The honesty wave's verdict was "the mode is the hazard, not the method" — both arms
  decayed identically in a continuing conversation. **That no longer holds**: atomic
  ADD is flat 1.0 in the exact mode where spec-kit rots to 0.75 by wm3 AND breaks a
  third of wm1's behaviors at wm2 with nothing in its flow to notice.
- What spec-kit still wins, unchanged: raw price on friendly workloads (~1.7× gap
  survives the trim), and the fresh-mode matrix (spec-kit 6/6 $10.05) stands
  un-rechallenged until both arms re-run in atomic-era conditions. The appendix-H
  bottom line does not flip on this data.

## Reproduce

```bash
# SWE arms (fresh runs-roots)
python3 -m benchmark.swe.runner --arms add --runs-root benchmark/runs-swe/atomic
python3 -m benchmark.swe.runner --arms add --model claude-haiku-4-5-20251001 \
  --runs-root benchmark/runs-swe/atomic-mini2
# official eval (cwd = the runs dir)
uv run --no-project --with swebench python3 -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Lite --predictions_path predictions_add.jsonl \
  --max_workers 2 --run_id <id> --namespace ''
# cross-milestone session bench
python3 -m benchmark.pilot run-all --arms add --wms 1 2 3 4 5 6 \
  --session-mode continue --runs-root benchmark/runs-atomic-session
```
