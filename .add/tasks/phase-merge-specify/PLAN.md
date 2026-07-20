# TASK: Merge scenarios into specify: 8->7 phase list

slug: phase-merge-specify · created: 2026-07-14 · stage: mvp
milestone: six-phase-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: phase-merge-specify — the scenarios PHASE folds into specify (six-phase-loop 1/6, human-decided TRUE merge): one drafting phase produces §1 rules AND §2 Given/When/Then; the §-section shape of TASK.md is UNTOUCHED (sections are the stable API; only the lifecycle list shrinks)
Must:
  - PHASES drops "scenarios" (7 tokens incl done); a bare `advance` from specify lands at plan; every phase map follows (PHASE_GUIDE action for specify gains the Given/When/Then clause · PHASE_OWNER · PHASE_GROUPS DIRECTION=(specify,plan,tests) · PHASE_AGENT · _FRONT_PHASES · the status blurb map · the phases/*.md guide-file map)
  - legacy state migrates on read: phase token "scenarios" -> "specify" via _normalize_phase_tokens's _legacy map (ground/contract precedent — silent, TOTAL, idempotent, normalize-on-read only)
  - _SKIPPABLE_PHASES shrinks to ("observe",); a pre-merge task HEADER still declaring `skip: scenarios` is tolerated loud (an advisory note, never a die) — the declaration is simply ignored
  - freeze's early-phase check (add.py ~6516 `phase in ("specify","scenarios")`) reads specify only; the skip-rationale regex drops the scenarios alternative
Reject:
  - `advance --to scenarios` / `phase scenarios <slug>` -> the existing unknown/invalid-phase refusal (scenarios is no longer a phase token)
  - a NEW skip declaration naming scenarios -> the advisory note (not the old bad-token die, not a silent accept)
Accept: Given a fresh task at specify with §1+§2 drafted, When `advance` runs bare, Then the task is at plan (one hop, no scenarios stop); and Given a pre-merge state.json with a task at phase "scenarios", When any command loads state, Then the task reads as phase "specify" byte-safe elsewhere.
Boundary: two legacy dialects — the state token ("scenarios" in state.json) and the header skip declaration (`skip: scenarios — reason`); both must land tolerated, differently (silent normalize vs loud ignore)
Assumptions: ⚠ ~19 fixture files step through the scenarios phase and shift by one advance — why: measured by grep, but sequence-shift breakage is only visible at the fence; if wrong (more suites pin the 8-list): each is a declared doc-truth ripple, fixed within scope (cost: fence reruns)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/tooling/add_engine/constants.py:PHASES/_SKIPPABLE_PHASES/PHASE_GUIDE/PHASE_OWNER/PHASE_GROUPS/PHASE_AGENT · add-method/tooling/add.py:_normalize_phase_tokens/_FRONT_PHASES/_SKIP_RATIONALE_CLAUSE_RE/freeze-check-6516/status-blurb-2025/guide-file-map-3059/skip-reader-1805 · fixture files stepping the scenarios phase (fence-named, declared ripples)
Context (working folder): ENGINE_MD5 + ENGINE_PKG_MD5 both re-aim (constants.py is add_engine/); SEAMS pin drifts on add.py shifts; sync x3
Honors (patterns / conventions): expectations-first migration precedent (_legacy map, normalize-on-read) · sections never renumber (§3 stays §3 everywhere) · defaults loud, never silent-skip · guides/SKILL.md prose re-cut deferred to guide-recut (doc-truth transitional state accepted within the milestone)
Anchors the contract cites: PHASES · _normalize_phase_tokens · _SKIPPABLE_PHASES · PHASE_GROUPS
Ground SHA: 37d5a80 — stamped by freeze

### Contract

```
constants.py:
  PHASES = ("specify", "plan", "tests", "build", "verify", "observe", "done")
  _SKIPPABLE_PHASES = ("observe",)
  PHASE_GUIDE["specify"] action += "; write one Given/When/Then per Must AND per Reject (§2)"
  PHASE_GROUPS["DIRECTION"] = ("specify", "plan", "tests")
  PHASE_OWNER/PHASE_AGENT/PHASE_GUIDE: scenarios keys removed
add.py:
  _normalize_phase_tokens: _legacy = {"ground": "specify", "contract": "plan",
                                      "scenarios": "specify"}
  _FRONT_PHASES = ("specify", "plan", "tests")
  freeze check: phase in ("specify",)  [or == "specify"]
  _SKIP_RATIONALE_CLAUSE_RE: (observe) only
  skip reader: token "scenarios" -> print note "scenarios merged into specify — skip
    declaration ignored", never die; other bad tokens keep the existing die
guide-file map: scenarios entry removed (2-scenarios.md file untouched until guide-recut)
```

`Least-sure flag surfaced at freeze:` [test] the tolerated-skip note path — why: the skip reader dies on bad tokens today and its callers may assume a validated set; threading a tolerated-but-ignored token through _task_skip_set's return shape risks a downstream KeyError; if wrong: filter the token OUT of the returned set and note at the READ site only (cost: one refactor round)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `add-method/.add/` `add-method/bin/` `add-method/src/add_method/_installer.py`
Strategy & known-problem fixes: red tests -> constants maps -> add.py sites -> skip tolerance -> migration token -> fence -> fixture ripple repair rounds. Traps: phase-index-vs-§-section off-by-one (sections DO NOT move) · test_phase_bundles hardcoded expected_bundle dict · fast-lane-skips suite pins scenarios as a skippable example (rewrite to observe) · sync engine x3 never tests · ENGINE_PKG_MD5 re-aims too (constants.py).
Approach (domain strategy): lifecycle shrinks, section API frozen; migrate-on-read; loud tolerance for retired declarations

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (constants.py:59/347/72-124, add.py:125-141/1603/1805/2025/3059/6181/6516 all read this session)
- [x] §1 every Must + every Reject present, each paired with its outcome
- [x] §3 Contract shape is concrete
- [x] Lowest-confidence flag surfaced and substantive (the tolerated-skip return-shape risk)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-14T01:20:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_phases_has_no_scenarios · test_advance_specify_lands_plan · test_legacy_state_token_normalizes · test_old_skip_declaration_tolerated_loud · test_new_phase_cmd_scenarios_refused · test_maps_carry_no_scenarios_key · test_specify_guide_action_names_gwt.
Tests live in: `add-method/tooling/test_phase_merge_specify.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned, with two corrections the code taught: (1) skip validation + the retired-`scenarios` note stay INSIDE the observe-crossing branch — the frozen M13 pin (non-skippable crossings run ZERO skip logic) refuted an always-validate restructure; the tolerated token is filtered OUT of _task_skip_set's return exactly as the freeze flag's fallback predicted. (2) task_phases' index-derived n→§(n+1) mapping broke when PHASES shrank — replaced with the explicit _PHASE_SECTIONS table (the milestone's named off-by-one trap, hit live). Fixture ripple was ~30 suites (vs the §1 ~19 estimate), repaired in fence rounds.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): PHASES carries no `scenarios`; a bare advance from specify lands at plan; a legacy `scenarios` state token normalizes on read; a pre-merge `skips: scenarios` header is tolerated loud (note at the observe crossing) while a non-skippable token still dies — confirmed by test_phase_merge_specify 8/8 (red first, then green) + the FULL fence 3517 tests OK / REAL_EXIT=0 (fence-pms-final2.log; ~30 legacy-sequence fixture suites repaired as the §1-declared ripple, zero tests weakened); engine twins ×3 byte-identical; ENGINE_MD5 b27ce845 + ENGINE_PKG_MD5 870a4ce0 re-pinned; SEAMS `_declared_scope` anchor verified at add.py:5631.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

