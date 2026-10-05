# SWE-bench Lite pilot — ADD at low effort against raw Claude Code at medium (2026-10-03)

**Slice:** 30 instances drawn from the 300 Lite instances (`--sample 30 --seed 0`), across 10 repos:
django 9 · sympy 8 · pytest 3 · sphinx 3 · matplotlib 2 · seaborn, requests, xarray, pylint and
scikit-learn 1 each. **Model:** `claude-sonnet-5-5`, operator settings isolated
(`--setting-sources project,local`). **Runner:** `benchmark/swe/runner.py` at `501c8d01`, 4 workers.
**Scoring:** the official harness, `swebench==5.0.2`, run in local Docker with the x86 images
under Rosetta. The gold patch for `psf__requests-2317` resolved first as a sanity check.
**n = 30: directional, not a leaderboard number.**

| arm | resolved | errors · empty | cost (30) | $ per resolved | mean wall / instance |
|---|---|---|---|---|---|
| vanilla · medium | **21/30 (70.0%)** | 0 · 0 | $2.81 | $0.13 | 24 s |
| ADD 4.0 · low | **23/30 (76.7%)** | 0 · 0 | $7.56 (2.7×) | $0.33 | 86 s |

- **ADD resolved a strict superset of vanilla's instances:** all 21 of vanilla's, plus
  `scikit-learn__scikit-learn-14087` and `sympy__sympy-14817`. Vanilla resolved none that ADD missed.
- **Significance:** 2 discordant pairs, both in ADD's favour. McNemar exact p = 0.5, so this is not
  significant at n = 30. The full 300 would need roughly a 4–5 point gap that holds up to separate them.
- **Projected full-Lite cost** from this slice: ADD about $76, vanilla about $28. Local scoring of
  30 predictions took about 20 minutes per arm at 3 workers.

## Why scoring is local, not on Modal

- **`swebench` 5.0.0–5.0.2:** the Modal path still builds images from `setup_env_script`, which the
  5.x `TestSpec` no longer has. The code itself carries a TODO for this. The Modal side installs
  swebench from PyPI, so it cannot be patched locally.
- **`swebench` 4.1.0:** it calls `Sandbox.open`, which modal ≥ 1.0 removed, and Modal's servers
  refuse clients below 1.0.
- **Local fix:** on Apple Silicon, Docker asks for an arm64 manifest, which these images do not
  have. Pre-pulling each image with `--platform linux/amd64` (`pilot30-s0/eval.sh`) solves it.

## For a leaderboard submission

A submission needs all 300 instances, pass@1, and per-instance trajectories (`transcript.jsonl`
is kept per instance). Predictions, logs and transcripts are under `benchmark/runs-swe/pilot30-s0/`,
which is gitignored. Nothing has been submitted.

## Rerun with the lean skill (2026-10-04, task `lean-bounded-fixes`)

The same 30 instances, ADD arm only. The skill's floor is now a change of shape, not a touch, and the
runner's prompt no longer forces a Task.

| arm | resolved | cost (30) | $ per resolved | mean wall |
|---|---|---|---|---|
| vanilla · medium | 21/30 | $2.81 | $0.13 | 24 s |
| ADD · low, 4.0.0 skill (forced Task) | 23/30 | $7.56 | $0.33 | 86 s |
| ADD · low, lean skill (Quick lane) | 21/30 | **$4.94** | **$0.24** | **49 s** |

- All 30 runs took the Quick lane: 0 task files, down from 14. Every patch still carries tests.
- Resolved changed by −3 / +1 against the earlier ADD run (lost `scikit-learn-14087`, `sphinx-8801`,
  `sympy-19007`; gained `sympy-13915`). That is one sample at n = 30, so it does not separate from
  noise. The full 300 is the test.

## The 2×2 effort sweep (2026-10-05, final `value-final` skill)

The same 30 instances, both tools at both effort levels, scored locally by the official harness
(swebench 5.0.2, run ids `sweep-*` and `value-add-low`).

| cell | resolved | cost (30) | $ per resolved | mean wall | ran repo tests | patch ships a test |
|---|---|---|---|---|---|---|
| vanilla · low | 21/30 | $2.60 | $0.12 | 20 s | 5/30 | 1/30 |
| vanilla · medium | 20/30 | $2.83 | $0.14 | 27 s | 11/30 | 1/30 |
| ADD · low | **24/30** | $5.46 | $0.23 | 59 s | 30/30 | 30/30 |
| ADD · medium | 22/30 | $7.10 | $0.32 | 80 s | 30/30 | 30/30 |

- ADD · low resolves a superset of vanilla · medium: the same 20 issues plus django-11630,
  django-13158, sympy-14817 and sympy-19007.
- Medium effort bought neither tool anything here: vanilla went 21 → 20 and ADD 24 → 22, while
  each cost more.
- The pilot's vanilla · medium resolved 21 against this sweep's 20, which puts n = 30 noise at about
  ±1. Still directional. The full 300 is the test.

## Round 11: the official eval environment (2026-10-05, `blind-spots` skill)

`--testenv docker`: the agent edits a copy of the eval image's `/testbed`, and its python and pytest
run in the image's env (run ids `r11-add-low`, `r11-vanilla-medium`).

| cell | resolved | cost (30) | $ per resolved | mean wall | saw a green test run |
|---|---|---|---|---|---|
| vanilla · medium | 21/30 | $2.50 | $0.12 | 25 s | 7/30 |
| ADD · low | **23/30** | $3.59 | $0.16 | 49 s | 27/30 |

ADD only: scikit-learn-14087, sympy-13915, sympy-14817. Vanilla only: sympy-19007. Against round 10's
ADD-low: gained scikit-learn-14087 and sympy-13915; lost django-11630, django-13158 and sympy-19007, each
an F2P failure with 0 P2P broken. `sites:` showed up in 2 of 30 runs and did not flip django-13265.
