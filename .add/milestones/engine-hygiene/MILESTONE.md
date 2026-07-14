# MILESTONE: Engine hygiene: perf/dedup cleanup + wire milestone-relations

goal: Land the value-dense engine cleanup a read-only sweep found — behavior-preserving perf hoists + duplication removal (cmd_check TOML re-reads/dead recompute, 5x snapshot-hash helper with unified exceptions, static-regex hoist, milestone-resolve DRY) and finish-wiring the never-surfaced _milestone_relations feature — with the existing ~3600-test fence as the safety net
rationale: sub-milestone — a read-only engine sweep (Explore agent, scratchpad/sweep_report.md) surfaced 8 findings; the user picked scope #1+#2+#3+#5 (behavior-preserving cleanup) + #4 (finish-wire the half-built feature) via AskUserQuestion. Value-dense, low-risk, one existing fence protects it.
stage: mvp · status: active · created: 2026-07-14T16:16:45+00:00
release: pending
relations: <cross-MILESTONE edges — add header lines `depends-on:` / `extends:` / `relates-to:` with milestone slugs (comma-sep); omit if none. Non-blocking except depends-on; validated by `add.py check`>

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  behavior-preserving perf/dedup cleanup of the ADD engine (cmd_check TOML re-reads + dead recompute → O(1) hoist; 5× snapshot-hash try/except → `_snapshot_hash` with a unified except tuple; static `_HEADING_RE` regex → module-const hoist in taskdoc.py; 4× `unknown_milestone` boilerplate → `_resolve_milestone`) · finish-wiring the parsed-but-unused `_milestone_relations` feature into cmd_check (per-finding advisory warnings) + cmd_status (a one-line count).
Out: findings #6 (no_project boilerplate — too small standalone), #7 (long fns cmd_check/cmd_status/build_parser — verbose not broken, order-sensitive stdout tests), #8 (13 broad `except` — all intentional documented fail-open). No new CLI surface, no behavior change to any existing gate.

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): <the code every task in this milestone lands in — gathered once, task-delta>
Anchors: <the shared symbols tasks may cite — the floor each task's contract builds on>
Honors (conventions): <PROJECT.md · CONVENTIONS.md · SEAMS.md rules every task honors>
Issues/Risks (shared): <traps in the shared code that feed each task's §1 expectations>

> Gather this ONCE per milestone (the drafting step in `scope.md`). Each task's `specify`
> PROJECTS its §1 expectations from here + the specific request — light, not re-grounded per task.

## Shared decisions & glossary deltas   (living — every task must honor these)
- <cross-cutting rule, named from GLOSSARY.md>

## Shared / risky contracts (freeze these first)
- <contract name> -> owning task <slug>

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] hygiene-bundle         depends-on: none            — perf hoists + dedup helpers (#1+#2+#3+#5), behavior-preserving, ~3600-test fence as net
- [x] wire-milestone-relations depends-on: hygiene-bundle — finish-wire `_milestone_relations` into cmd_check + cmd_status (advisory)

## Exit criteria (observable; map each to the task that delivers it)
- [x] cmd_check reads components.toml + contracts O(1) per invocation (not per-task), with no observable output change   (← hygiene-bundle)
- [x] every snapshot-hash read and every `unknown_milestone` resolve routes through one shared helper                    (← hygiene-bundle)
- [x] a MILESTONE.md relation edge to an unknown / self milestone surfaces as an advisory warning in `add.py check` and a one-line count in `add.py status` — never turning either red   (← wire-milestone-relations)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py — `_snapshot_hash` + `_resolve_milestone` helpers (5 + 4 call-sites deduped), cmd_check O(1) hoist (`_components`/`_contracts` lifted out of the per-task loop, dead `_arch` removed, `_task_component(comps=)` + `_component_findings(_reg)` threaded), new `_milestone_relations_health` wired into cmd_check warns + cmd_status one-liner. add_engine/taskdoc.py — static `_HEADING_RE` hoisted to module const. engine_pin.py — ENGINE_MD5 ×2 re-pins (→c3d61a86→d7079f8d), ENGINE_PKG_MD5 →265dd143. All synced ×4 engine twins byte-identically.
- skill   : untouched.
- book    : untouched. (`.add/SEAMS.md` line-pins migrated: `_declared_scope` 5723→5734→5778; `phase-body-extraction` taskdoc 159/185→164/190 — anchor bookkeeping, not a book edit.)

### Cross-task evidence   (one row per task)
- hygiene-bundle          : gate=PASS · tests=8 green (incl. O(1) call-count spy N=2 vs N=4) · full fence 3619 pass then 1 SEAMS-anchor re-pin → green · residue=none
- wire-milestone-relations : gate=PASS · tests=6 green · full fence 3626 passed, 0 failed · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
  - EC1 (cmd_check O(1)) ← hygiene-bundle row + the cmd_check hoist under Ship-by-domain/tooling; proven by the N=2-vs-N=4 call-count spy test.
  - EC2 (shared snapshot-hash / milestone-resolve helpers) ← hygiene-bundle row + the `_snapshot_hash`/`_resolve_milestone` line.
  - EC3 (advisory milestone-relation surface) ← wire-milestone-relations row; `test_check_warns_but_does_not_fail` + `test_status_prints_advisory_oneliner` prove warn-not-red.
- goal: land the value-dense engine cleanup + finish the half-built feature under the existing fence — MET: both tasks gate PASS, the whole ~3600-test suite green (last: 3626 passed / 0 failed), zero behavior change to any existing gate.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [x] both tasks committed on `feat/engine-hygiene` (cfb8fe0 + 0dddefd)
- [ ] push `feat/engine-hygiene`, open a PR (2 commits), watch CI, human reviews + merges on green
- [ ] AFTER merge: run the human-authorized paid WM1 re-measure ("wait for engine-hygiene") — engine internals only, no user-facing feature, so likely folds into the next release cut rather than its own tag
