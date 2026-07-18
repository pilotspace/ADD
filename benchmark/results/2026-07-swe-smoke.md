# SWE-bench Lite smoke — does ADD change what a coding agent ships?

**2026-07-19 · smoke-scale (n=3 instances × 2 arms × 2 models) · officially evaluated**

The wm bench measures ADD on a longitudinal project it designed. This campaign
asks the outside question: on **leaderboard-class tasks nobody designed for ADD**
(real GitHub issues from SWE-bench Lite), does installing ADD change what the
same agent ships? Smoke-scale by design — it proves the pipeline and gives
directional evidence, not a leaderboard submission.

## Method

- Instances: `psf__requests-2317`, `psf__requests-1963`, `psf__requests-863`
  (SWE-bench Lite, small repo → fast clones; rows via HF datasets-server,
  cached in `runs-swe/instances.json`).
- Arms, same pinned meter (`claude -p … --output-format stream-json`):
  - **vanilla** — bare agent + issue text in the checkout.
  - **add** — ADD 2.0 (this checkout) installed into the repo
    (`uv venv` + editable install + `pilotspace-add init`), prompt drives the
    oneshot ADD loop (status → new-task → freeze --cross → build → gate).
- Prediction = `git diff <base_commit>` of tracked files, filtered of method
  artifacts (`.add/`, `.claude/`, `CLAUDE.md`, venvs) — the fix only.
- Evaluation: official `swebench` 4.1.0 Docker harness
  (`run_evaluation`, `--namespace ''` local builds), never self-scored.
- Harness: `benchmark/swe/runner.py` (guards in
  `benchmark/tests/test_swe_smoke.py`).

## Results — claude-sonnet-5 (frontier model)

| arm | resolved | cost | wall | patch character |
|---|---|---|---|---|
| vanilla | **3/3** | $0.95 | 6.4 min | fix only |
| add | **3/3** | $5.28 | 50.9 min | fix **+ a regression test per issue** |

Per instance:

| instance | vanilla | add |
|---|---|---|
| psf__requests-2317 | ✓ 536B · $0.39 · 123s | ✓ 1,583B · $1.77 · 1,098s |
| psf__requests-1963 | ✓ 365B · $0.24 · 103s | ✓ 3,185B · $1.93 · 1,108s |
| psf__requests-863 | ✓ 553B · $0.32 · 157s | ✓ 1,565B · $1.58 · 847s |

**Honest read.** On a frontier model and friendly instances, resolve rate ties —
exactly what the wm bench predicted (friendly ground cannot differentiate
methods; see `2026-07-add-2.0-remeasure.md`, Finding 3). ADD costs ~5.5× and
~8× wall for the same official verdict. What ADD changes is **what ships**:
every ADD patch carried a regression test capturing the issue (the loop's red
test), applied cleanly alongside the official test patch, and the fix went
through a frozen contract + gate. Vanilla shipped bare fixes. On tasks this
easy, that guarantee is pure overhead; the method's bet is that it stops being
overhead when the model is weaker or the task is hostile.

## Results — claude-haiku-4-5 ("mini agent", the differentiation probe)

_Testable prediction from appendix-h: enforced discipline should help weaker
models more than frontier models._

| arm | resolved | cost | wall |
|---|---|---|---|
| vanilla | **3/3** | $0.90 | 27.9 min |
| add | **2/3** | $2.52 | 65.2 min |

Per instance:

| instance | vanilla | add |
|---|---|---|
| psf__requests-2317 | ✓ 398B · $0.25 · 448s | ✓ 1,645B · $0.84 · 1,478s |
| psf__requests-1963 | ✓ 666B · $0.30 · 550s | ✓ 13,356B · $0.76 · 1,179s |
| psf__requests-863 | ✓ 544B · $0.35 · 677s | **✗** 4,175B · $0.92 · 1,256s |

**The prediction was NOT supported at this n — published anyway.** Bare haiku
also cleared all three (these instances are too friendly to differentiate at
any tier). Worse, haiku+ADD *lost* one: on `psf__requests-863` the target fix
was correct (all FAIL_TO_PASS tests pass) but the model over-built and broke
two pre-existing tests (`test_GET_no_redirect`,
`test_prefetch_return_response_interaction` — PASS_TO_PASS regressions caught
by the official harness).

**Diagnosis — a real method-integration gap, found exactly the way a smoke
should find it.** ADD's gate never saw the breakage because the loop bound only
its OWN task tests as the floor; in a foreign repo, the host suite is the
regression floor and the loop must declare it (run the existing tests before
the gate). This mirrors the wm bench's structure — where ADD's `regression_run`
DOES bind prior milestones' suites — and is a one-line prompt/lane fix
(`§5 Scope` + existing-suite floor) to test in the next iteration.

## Verdict

- **Pipeline proven end-to-end**: 12 agent runs, 4 official Docker
  evaluations, zero harness errors, resumable predictions.
- **Friendly instances cannot differentiate** — same lesson as the wm
  campaign, now confirmed on foreign ground at two model tiers.
- **What ADD changes on SWE tasks today**: every patch ships with a regression
  test for the issue; cost ~3-8× wall/​dollars.
- **What the smoke caught**: the host-repo test suite must be declared as a
  floor in foreign repos — without it, a weak model's over-build can pass ADD's
  gate and fail the world's. Fix identified; next iteration tests it.

## Reproduce

```bash
python3 -m benchmark.swe.runner --arms vanilla add            # sonnet-5
python3 -m benchmark.swe.runner --arms vanilla add \
    --model claude-haiku-4-5-20251001 --runs-root benchmark/runs-swe/mini
cd benchmark/runs-swe && uv run --no-project --with swebench \
    python3 -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path predictions_<arm>.jsonl \
    --max_workers 2 --run_id add-smoke-<arm> --namespace ''
```
