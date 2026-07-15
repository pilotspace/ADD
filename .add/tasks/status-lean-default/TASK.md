# TASK: lean bare status default: gate goal/m-goal prose + personas roster + milestone/task/stream lists behind --all, add count lines

slug: status-lean-default · created: 2026-07-15 · stage: mvp
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
Feature: bare `add.py status` gets a LEAN default — the 5 big multi-line blocks (project `goal` + `m-goal` prose, the personas roster, the milestones list, the tasks list, the streams per-line detail) move behind `--all`, each replaced by a one-line count/pointer — so an agent that calls bare `status` (not `--brief`) still gets a small, orienting output. GUARANTEED at the engine (not skill-dependent). The resume line, every health one-liner, and all pointers stay.
Must:
  - M1: with `not --all` (and not --brief/--json/--section), bare `status` gates the 5 blocks: `goal`/`m-goal` full prose, the `personas:` roster body, the `milestones:` list rows, the `tasks:` list rows, and the `streams:` per-stream rows — each replaced by a single count/pointer line ending `(status --all)` (or the m-goal `(← slug, status --all)`); the resume `now:`/`next:` lines, `stage`/`autonomy`/`run mode`/`goal-ready`/`context`/`voice` one-liners, and all additive cues (releasable/carried/compaction/deltas/queued/dag-plan/wave/archived + the active-task autonomy/sensitivity/bundle/grounded lines) STAY.
  - M2: `status --all` prints the FULL output byte-identical to today's bare `status` (the reference behavior is preserved, just relocated behind the flag) — nothing is lost, only paginated by default.
  - M3: `--brief`, `--json`, `--section` branches are UNCHANGED; the lean default measurably shrinks bare `status` (fewer lines + chars) on a multi-milestone/persona project.
Reject:
  - R1: passing `--all` -> the trim MUST NOT apply (`no_lean_under_all`) — full roster + full goal/m-goal prose print (regression guard; the gate is `not show_all`).
Accept: on this repo, bare `status` no longer prints the 6-line personas roster, the milestones list rows, the tasks list rows, or the full `goal:`/`m-goal:` prose — instead a `personas: N (status --all)` / `milestones: N active … (status --all)` / `tasks: N (status --all)` count line each; `status --all` still prints all of them; `--brief` is unchanged.
Boundary: bare `status` (lean) vs `status --all` (full) vs `status --brief` (2-line resume) — three distinct verbosity levels dispatched by flags; the lean default sits between brief and all.
Assumptions: ⚠ gating `m-goal` behind `--all` ripples into `report-template.md` (which tells the agent to read `m-goal` from `add.py status`) — the doc line must point at `status --all`; if missed, the report flow reads a now-absent line; cost: a stale doc instruction (fixed here, in scope), not a runtime break.

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols):
  - `add-method/tooling/add.py` — `cmd_status` human-readable branch (the `not show_all` gates): `goal` line (~2929), `m-goal` line (~2932), `personas:` roster loop (~2981-2983), `milestones:` list loop (~3000-3007), `tasks:` list loop (~3144-3158), `streams:` per-stream loop (~3064-3077). Add a count/pointer line for each when `not show_all`. `show_all = getattr(args, "all", False)` already exists.
  - `add-method/skill/add/report-template.md` (×3 skill trees) — the "read m-goal from `add.py status`" line → `add.py status --all` (m-goal now gates).
  - the 4 `add.py` twins (source · _bundled · repo `.add/` · add-method `.add/`) re-pin ENGINE_MD5; the 3 SKILL trees for report-template parity.
Context (working folder): `cmd_status` already paginates milestones/tasks lists to `_STATUS_PAGE_SIZE=10` behind `--all`; this extends the SAME `show_all` gate to full suppression (count line) + adds goal/m-goal/personas/streams. `--all` restores byte-identical full output.
Honors (patterns / conventions): additive-cue convention (present-only one-liners stay) · the existing `show_all`/`_STATUS_PAGE_SIZE` pagination seam · ENGINE_MD5 repin across 4 twins + PYTHONDONTWRITEBYTECODE=1 for the suite (help-diet lesson) · report-template parity across 3 skill trees.
Anchors the contract cites: `cmd_status`, `show_all`, `_STATUS_PAGE_SIZE`, `_persona_roster`, report-template.md m-goal line.
Ground SHA: a45878a — stamped by freeze

### Contract

```
cmd_status, human-readable branch, when `not show_all` (bare `status`):
  goal      -> suppress full prose; the `context: .add/PROJECT.md` pointer already stands (goal lives there)
  m-goal    -> `m-goal  : (← <slug>, full text: status --all)`   (keep goal-ready health line)
  personas  -> `personas: <N> (status --all)`                    (roster body only with --all)
  milestones-> `milestones: <N active> · <A> archived (status --all)`  (rows only with --all)
  tasks     -> `tasks   : <N> (status --all)`                    (rows only with --all)
  streams   -> keep `streams : <N> active`; per-stream rows only with --all

  invariants:
    - `status --all`  == today's bare `status` output, byte-identical (M2, R1 no_lean_under_all)
    - `--brief` / `--json` / `--section` byte-unchanged
    - every health one-liner + additive cue stays in the lean default (only the 5 BLOCKS gate)
    - report-template.md (×3 trees) reads m-goal from `status --all`
```

`Least-sure flag surfaced at freeze:` [test] the additive-cue tests assert cue PRESENCE in bare `status`; the 5 gated blocks' tests must forward-migrate to `--all` (sanctioned, they pin RELOCATED not removed behavior) — mis-judging which tests assert a gated block vs a kept one-liner is the main risk; the M2 "--all byte-identical" test is the backstop.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `add-method/skill/add/report-template.md` `add-method/src/add_method/_bundled/skill/add/report-template.md` `.claude/skills/add/report-template.md` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/test_status_lean_default.py` `.add/SEAMS.md` `add-method/tooling/test_report_shape_scan_audit.py` `add-method/tooling/test_machine_state.py` `add-method/tooling/test_parallel_status_view.py` `add-method/tooling/test_per_stream_owner.py` `add-method/tooling/test_project_goal.py` `add-method/tooling/test_relations.py` `add-method/tooling/test_roster_status_line.py` `add-method/tooling/test_ux_stale_followups.py`
Strategy & known-problem fixes: 1. RED: `test_status_lean_default.py` — (M1) bare `status` on a fixture project with ≥2 personas + ≥11 milestones + ≥11 tasks omits the roster body / list rows / goal-m-goal prose, printing the count lines; (M2) `status --all` still contains them (byte-superset); (R1) `--all` shows full goal prose; `--brief` unchanged. 2. gate the 5 blocks in `cmd_status` on `not show_all`. 3. update report-template.md m-goal line (×3 trees). 4. run FULL suite — forward-migrate the additive-cue tests that assert a GATED block in bare status to `--all` (sanctioned relocation, not weakening); keep those asserting kept one-liners. 5. re-pin ENGINE_MD5 across 4 twins. Trap: `--all` path must stay byte-identical (don't reformat kept lines). Trap: sync ALL 4 add.py twins + 3 report-template trees (help-diet/status-brief lessons). Trap: PYTHONDONTWRITEBYTECODE=1.
Approach (domain strategy): "flag-gated verbosity tiers"

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
Strategy actually used: as planned, with two disciplined refinements. (1) The frozen contract scoped ONLY the report-template `m-goal` line; I initially also edited its `tasks:`/`streams:` line (line 69) but the verbose wording blew the `reference` skill-pool byte budget (−134 B over) — reverted to the minimal contract-mandated `m-goal → status --all` edit offset by same-guide compression (`re-typed from memory` → `from memory`, net −3 B), keeping the pool under budget (slack +4 B). (2) The task ROWS gating subsumed the old pagination `… N more` note, so `test_machine_state`'s truncation test forward-migrated to assert the new `tasks : <N> (status --all)` count line. SEAMS.md `_declared_scope` anchor repinned 5778→5800 (my +22 cmd_status lines shifted it); §5 widened + re-crossed to cover SEAMS.md + the 8 forward-migrated relocation-pin test files.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [ ] all tests pass · coverage held · no test or contract altered during build
- [ ] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [ ] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [ ] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): on THIS repo (202 tasks · 108 milestones · 6 personas · 15 active streams) bare `python3 .add/tooling/add.py status` = **1,965 bytes** vs `status --all` = **20,444 bytes** (a −90.4% lean default). Bare output shows the count/pointer lines — `personas: 6 (status --all)` · `milestones: 38 active · 0 archived (status --all)` · `tasks   : 202 (status --all)` · `m-goal  : (← honest-fidelity-meter, full text: status --all)` · `streams : 15 active milestones (per-stream rows: status --all)` — and NO roster body / milestone rows / task rows / goal prose, while every resume line (`now:`/`next:`/`active :`), health one-liner, and additive cue (releasable/carried/compaction/deltas/spec) STAYS. `status --all` restores all of them; `--brief`/`--json`/`--section` unchanged. Confirmed by `test_status_lean_default.py` (5) + the full engine suite (3638 passed, 162 subtests) with the 8 relocation-pin tests forward-migrated to `--all`.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-15
Evidence: full engine suite 3638 passed + 162 subtests (PYTHONDONTWRITEBYTECODE=1); test_status_lean_default 5/5; the −90.4% bare-status shrink measured live above. Security: none — output-gating + doc/test edits only, no secrets/injection/new deps (mechanical/UX class). ENGINE_MD5 1dd8c1b1→a773d868 synced across all 4 add.py twins; SEAMS anchor repinned; report-template reference pool under budget.

