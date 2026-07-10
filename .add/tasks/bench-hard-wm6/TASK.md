# TASK: WM6 precision-semantics hard milestone — where does ADD out-earn spec-kit

slug: bench-hard-wm6 · created: 2026-07-08 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): benchmark/workload/wm6 (PROMPT.md + oracle) · VALID_WMS in run/pilot/score · benchmark/tests/test_wm4plus.py (VALID_WMS pin migrates 5→6) · new test module
Context (working folder): diagnosis — on easy CRUD the judge ceiling (~0.98) leaves ~0.03 headroom; spec-kit reaches 0.95-0.97 unaided. A discriminating milestone needs requirements where naive implementations FAIL EXACT checks: timezone-instant overlap, boundary fenceposts, idempotency, malformed-input hardening. Deterministic oracle probes, not vibes.
Honors (patterns · conventions): oracle style running_app/http_call; wm1-5 prompts/oracles byte-untouched; frozen metric semantics (regression stays wm3-only; slope generalizes already)
Anchors the contract cites: workload/wm6/oracle/test_precision.py · VALID_WMS
Ground SHA: ef25576

---

## 1 · SPECIFY — the rules

Feature: WM6 precision-semantics hard milestone
Must:
  - WM6 prompt (on the inherited wm5 app): (a) timezone-correct overlap — start/end may carry ANY UTC offset; conflicts are decided on absolute instants; (b) boundary exactness — touching intervals (end == next start) do NOT conflict; (c) idempotent create — an `Idempotency-Key` header makes repeated identical POSTs return the SAME booking, never a duplicate; (d) input hardening — malformed ISO datetimes, end<=start, and unknown status values return 400 (never 500, never a stack trace); all wm2-wm5 behavior keeps working
  - oracle: >=10 deterministic probes covering each precision rule + a same-instant-different-offset conflict + a touching-intervals pass + idempotent replay + 500-vs-400 hardening
  - harness: VALID_WMS -> (1..6) in run/pilot/score; test_wm4plus VALID_WMS pin migrates forward; wm1-5 workload files byte-unchanged
Reject:
  - (none new — existing missing_prior_wm_record covers unscored priors)
Accept: Given the wm6 oracle against a naive workspace that compares datetime STRINGS, When the same instant arrives with different offsets, Then the conflict probe fails (the oracle discriminates); Given VALID_WMS, Then wm6 runs/scoresthrough the standard pipeline.
Assumptions: ⚠ Python stdlib fromisoformat parses most offsets — the naive failure mode may be less common than assumed — why: modern agents often normalize; if wrong: wm6 discriminates less (still valid as a harder-workload data point); mitigate with the boundary + idempotency + hardening probes which fail on comparison-operator and state-management sloppiness

---

## 3 · CONTRACT — freeze the shape

```
workload/wm6/PROMPT.md + oracle/test_precision.py  (>=10 probes: tz-instant · fencepost · idempotency · 400-hardening · carry-over)
VALID_WMS = (1..6) across run.py · pilot.py · score.py; test_wm4plus pin migrates
frozen: wm1-5 workload byte-unchanged; metric names/semantics unchanged
```

`Least-sure flag surfaced at freeze:` [spec] fencepost rule direction (touching = no conflict) — frozen as the industry-standard half-open interval [start, end); if wrong: the oracle punishes a defensible alternative reading (visible as a uniform miss across arms, not a discriminator)
Status: FROZEN @ v1 — approved by Tin Dang (instruction 2026-07-08: "I need a harder benchmark to make sure ADD where most value vs speckit")

---

## 4 · TESTS — failing-first (red)

Suite: benchmark/tests/test_hard_wm6.py — 5 tests (wm6 prompt+oracle with >=10 probes ·
prompt names all four precision rules + entry contract · oracle probes non-UTC offsets +
fencepost · wm5 anchor untouched · VALID_WMS == (1..6)). RED confirmed: wm6 missing +
VALID_WMS still (1..5) — red for the right reason.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/workload/` · `benchmark/run.py` · `benchmark/pilot.py` · `benchmark/score.py` · `benchmark/tests/` · `benchmark/runs/` · `benchmark/BENCHMARK.md` · `tmp/` · `.add/`
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass — benchmark suite 122 green (5 new); VALID_WMS + resume-count + pilot-seed pins migrated forward per §3, recorded via re-cross
- [x] green was EARNED — 12 oracle probes each target a named naive failure mode (string compare · closed interval · no idempotency state · unhandled parse); tz probe distinguishes same-instant from same-wall-clock
- [x] no security surface — workload prompt/oracle + constants

Build expectations (from §1 Accept + §3 CONTRACT): wm6 runs through the standard pipeline for both arms; the oracle discriminates naive implementations — confirmed by the wm6 run's fidelity spread.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08

