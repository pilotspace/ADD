# TASK: Surface coverage_detail + code_quality_annotation in report.py's per-WM view (read-only, non-gating)

slug: report-diagnostics · created: 2026-07-15 · stage: mvp
milestone: honest-fidelity-meter
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: A per-WM DIAGNOSTICS section in `render_report` surfacing the two advisory artifacts — `coverage_detail` (which requirements the app missed) and `code_quality_annotation` — beside the metric tables, so a sub-1.0 coverage score is readable at a glance. Display-only, never a metric, never a gate.
Must:
  - M1: `render_report` renders a per-WM diagnostics table listing, per arm: coverage `#covered/#total`, the UNCOVERED requirement ids (from `coverage_detail`), and the `code_quality_annotation` text.
  - M2: read-only + fault-tolerant — a missing record, an absent `coverage_detail`/`code_quality_annotation`, or a MALFORMED `coverage_detail` JSON renders `"—"` (never raises; mirrors `_render_cell`'s "not run" tolerance). `render_report` stays a pure function over records.
  - M3: DISPLAY-ONLY — the diagnostics read `artifacts` only; no metric is added, no gate consulted; the existing metric tables + trust report are unchanged.
Reject:
  - R1: a malformed `coverage_detail` (not JSON / not a list of `{id,covered}`) -> that cell renders `"—"` (fault-tolerant degradation, NOT an exception) — no error code, preserves M2's never-raises contract.
Accept: a report over a fixture where gsd/wm2 `coverage_detail` flags `R-cancellation-window-422` uncovered shows `R-cancellation-window-422` (and its `code_quality_annotation` text) in the WM2 diagnostics row for gsd, while an arm whose record has no `coverage_detail` renders `"—"` there — and `render_report` never raises.
Boundary: artifact-present (`coverage_detail` = valid JSON list) vs artifact-absent/malformed (missing key OR unparseable string) — the diagnostics row must render in BOTH, degrading to `"—"` on the latter.
Assumptions: ⚠ every persisted record now carries `coverage_detail` (true post coverage-detail task) — but OLD/foreign records may not; the fault-tolerant `"—"` path covers that, so the biggest risk is purely cosmetic (a blank cell), never a crash.

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols):
  - `benchmark/report.py` — NEW `_render_diagnostics(runs_root, wm, arms) -> str`: a `### WM{wm} diagnostics` markdown table `| arm | coverage | uncovered | code quality |`; reads each arm's record `artifacts["coverage_detail"]` (JSON list) + `artifacts["code_quality_annotation"]`; fault-tolerant `"—"` on missing record/artifact/malformed JSON. Reuses `_load_record`@30 (already returns None on missing/invalid).
  - `benchmark/report.py:render_report`@89 — append `_render_diagnostics(root, wm, arms)` after each `_render_wm_table`@103 in the `for wm in wms` loop.
Context (working folder): `benchmark/` harness; the persisted `runs/<arm>/wm<n>/record.json` artifacts (`coverage_detail`, `code_quality_annotation`) are the read source; `benchmark/tests/test_report.py` pins the render (loose `count>=N` asserts + an `extra_artifacts` fixture hook — additive-friendly).
Honors (patterns / conventions): `_render_cell`/`render_report`'s "never raises for a missing record → NOT_RUN" tolerance (extended to missing/malformed artifacts) · the non-gating law (diagnostics read `artifacts`, add no metric) · pure-function-over-records (no live boot/judge).
Anchors the contract cites: `_render_diagnostics`, `render_report`, `_load_record`, `coverage_detail`, `code_quality_annotation`.
Ground SHA: 936706f — stamped by freeze

### Contract

```
_render_diagnostics(runs_root: pathlib.Path, wm: int, arms: Sequence[str]) -> str:
  - header "### WM{wm} diagnostics" + table | arm | coverage | uncovered | code quality |
  - per arm (via _load_record; None -> every cell "—"):
      coverage      = "#covered/#total" from json.loads(artifacts["coverage_detail"])   (else "—")
      uncovered     = comma-joined ids where covered is false   ("none" if all covered · "—" if absent/malformed)
      code quality  = artifacts["code_quality_annotation"], collapsed to one line, truncated ~60 chars   (else "—")
  - a missing record / absent key / unparseable coverage_detail -> "—" for that cell (R1: NEVER raises)

render_report(...):
  - after each per-WM metric table, appends _render_diagnostics(root, wm, arms)
  - remains a pure read-only function; metric tables + trust report UNCHANGED; adds no metric
```

`Least-sure flag surfaced at freeze:` [contract] rendering the FULL `code_quality_annotation` could be long/multi-line — truncating to ~60 chars on one line keeps the table readable; if the full note matters, it can be linked/expanded later — cost: a cosmetic truncation only, the raw note stays in the record.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `benchmark/report.py` `benchmark/tests/`
Strategy & known-problem fixes: 1. RED tests first (benchmark/tests/test_report.py): (a) M1/Accept — a fixture with gsd/wm2 `coverage_detail` flagging `R-cancellation-window-422` → `render_report` output contains `R-cancellation-window-422` in a WM2 diagnostics row + the annotation text; (b) M2/R1 — a record with NO `coverage_detail` and a MALFORMED `coverage_detail` string both render `"—"` and `render_report` does not raise; (c) M3 — the existing metric-table asserts still hold (diagnostics are additive). 2. add `_render_diagnostics`, wire into `render_report`. Trap: fault-tolerance — wrap the `json.loads` + row parsing so a bad artifact degrades to `"—"`, never propagates (mirror `_load_record`'s except). Trap: additive only — do NOT alter the metric tables' text (test_report.py's `count>=N` + `N/A` asserts must still pass).
Approach (domain strategy): "fault-tolerant additive render"

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
Strategy actually used: as planned — NEW `_render_diagnostics` + a `_diagnostics_cells(record)` helper (coverage `#/#`, uncovered ids, one-line-truncated annotation; fault-tolerant em-dash on missing record / absent key / `json.loads` failure), wired into `render_report` after each per-WM metric table. Test-authoring lesson caught during red: pytest's `tmp_path` dir name contains the test-function name → a naive `assert "diagnostics" in text` was vacuously satisfied by the evidence-link PATHS; re-pinned both tests on the distinctive table header `| arm | coverage | uncovered | code quality |`.
Code lives in: `benchmark/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — `benchmark/tests/` 212 passed (2 new report tests + 210), 0 failed; frozen contract untouched
- [x] green was EARNED — the initial red suite had a VACUOUS assert (tmp_path dir name embeds "diagnostics" into evidence paths); caught and re-pinned on the distinctive `| arm | coverage | uncovered | code quality |` header + the real `R-cancellation-window-422` / `4/5` / annotation strings — no overfit, no stub
- [x] input dialect held — the diagnostics read `coverage_detail` (JSON list of `{id,covered}`) + `code_quality_annotation` string exactly as the scorer writes them; malformed JSON degrades to em-dash
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — stdlib `json` only; pure read over on-disk records; no live boot/judge/network; no user input

Build expectations (from §1 Accept + §3 CONTRACT): `python3 -m benchmark.report` prints a `### WM{n} diagnostics` table `| arm | coverage | uncovered | code quality |`; on the REAL persisted `vanilla/wm2` it reads `| vanilla | 5/5 | none | unavailable: no judge configured (deterministic scoring) |`, and an arm with no record degrades to `| add | — | — | — |` — confirmed live. The fixture test proves a gsd/wm2 `coverage_detail` flagging `R-cancellation-window-422` surfaces that id + its annotation in the WM2 diagnostics row.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate, autonomy: auto — evidence-complete; human spot-audit backstop) · date: 2026-07-15
OBSERVE: [SPEC · open] report.py resolves records only at the `runs/<arm>/wm<n>` layout, so archived comparison arms under alternate run-labels (add-v2meter-r0, …) render "—"; a `--label`/glob resolution (or a per-label report) would let the diagnostics show for every persisted arm, not just the arm-name-layout ones.

