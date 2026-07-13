# MILESTONE: Ceremony-to-effort: convert evaporating ceremony into artifact turns

goal: Convert measured evaporating ceremony into artifact effort — raise the artifact-turn ratio from ~37% toward spec-kit's ~95% band without lowering any trust floor. Target on the pinned-meter re-measure: mean add.py calls <= 12 (from 21), zero --help/duplicate-retry calls, per-task read burden <= ~30KB (from 56KB).
rationale: sub-milestone (engine+skill+template message/render layer, no lifecycle change). Origin: senior ceremony review 2026-07-13 grounded in two evidence audits — transcript anatomy of the LOOP-2 benchmark runs (best run 37% artifact / 63% ceremony vs spec-kit 95%; skip-bait + duplicate retries + --help residue quantified per call) and a guide/template weight audit (56KB read burden/task, 56% carried by 3 task-agnostic files; TASK.md.tmpl ~30% boilerplate + ~25% derivable). Human confirmed the 7-task breadth 2026-07-13. Continues risk-proportional-ceremony's held-open ≤12-call criterion with the follow-on levers its close verdict named.
stage: mvp · status: active · created: 2026-07-13T08:45:14+00:00
release: pending
relations: extends: risk-proportional-ceremony · relates-to: quality-floors, expectations-first

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  Message/render/template-layer ceremony cuts, each traced to a measured evidence line:
     (1) engine stdout truthfulness — lane-aware kickoff, full call recipe at new-task,
         precondition-honest `--to` hand-off, duplicate-identical-failure short-circuit;
     (2) engine-stamped derivable fields (Ground SHA · Status · Reported: · gate dates);
     (3) template + guide dedup (EXIT comments → pointers; single-source the 3-5×-repeated rules);
     (4) read-once gate guides (slim per-phase cards; report-template.md/run.md as reference);
     (5) resolved-scope echo at freeze + Scope auto-draft from §3 Grounding (propose-not-impose);
     (6) sensitivity-proportional gate report render;
     (7) fold auto-draft at milestone-done (human still confirms).
Out: NO lifecycle/phase change (expectations-first just landed, unmeasured). NO gate/freeze/
     floor semantics change — every recorded outcome, tamper tripwire, and HARD-STOP stays
     byte-equivalent in behavior. NO scope-grammar redraw (the scope-decl grammar is frozen;
     echo/auto-draft COMPOSE with it). NO stdout terseness work (grounded at ~$0.02, dropped
     in risk-proportional-ceremony). Author-toil items (SEAMS symbol pins · sync-twins) ride
     as separate fast tasks, not here. Benchmark re-measure EXECUTION is a release step, not a task.

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): `add-method/tooling/add.py` (`_next_command`/`_next_footer` ~6372-6425 · `cmd_init` kickoff ~668-677 · `_declared_scope` ~5490 · freeze/gate/report stamp paths · `cmd_milestone_done`) ×4 engine twins; `add-method/tooling/templates/TASK.md.tmpl` + `TASK.fast.md.tmpl` ×5 template twins; `add-method/skill/add/` (SKILL.md · phases/*.md · run.md · report-template.md) ×3 skill trees.
Anchors: `_next_command` (the single-source composer — status/guide/footer can never drift; EXTEND it, never fork a 4th surface) · `_declared_scope` (frozen token grammar) · `_raw_phase_bodies` (phase-span parser; §-heading sensitive) · lean ceilings TASK.md.tmpl 12400B/2850B · skill byte pools (phases + reference + whole-tree).
Honors (conventions): lean budget = COMPRESS to absorb, never bump · slang guard (no prose fold/altitude/blast-radius/bare-seam on template+skill surfaces) · twin byte-parity tests bind every edit ×3-5 trees · ENGINE_MD5/PKG re-pin on any engine byte change · SEAMS.md pins drift on add.py line shifts.
Issues/Risks (shared): TASK.md.tmpl edits trip the frozen tag census + BOTH ceiling pins (migrate in lockstep, test_taskmd_lean + test_facet_adr_harvest) · report-template.md prose is pin-hardened from the report-gate imperative — dedup must keep the pinned imperatives · `_next_command` stdout is test-pinned (first-call-ergonomics suite) · engine stamps must never write inside a FROZEN §3 body (tamper tripwire) · rep0 hit its scope repair ON the engine that already names the recipe — kickoff-truth's grounding must find why the message didn't land before changing it.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Floors untouched**: freeze · red-first tests · recorded gate · security HARD-STOP. Every task is message/render/template layer or an engine stamp of mechanically-derivable data. A task that finds itself editing gate SEMANTICS has left this milestone's scope — stop and re-intake.
- **Evidence-traced tasks**: each task's §1 cites the audit finding (transcript call#/file or weight-audit line) it kills; "feels lighter" is not a criterion.
- **Propose-not-impose**: every auto-draft (scope, fold) renders as a DRAFT the agent/human confirms; the engine never self-approves.
- **Measured exit**: the goal number (calls ≤ 12, read ≤ ~30KB) binds at the pinned-meter re-measure (release step), not at per-task gates.
- Persona: methodology-engine-dev (confirmed fit — engine/message-layer domain).

## Shared / risky contracts (freeze these first)
- `_next_command` composer output shape (kickoff + recipe lines) -> owning task **kickoff-truth**; derived-stamps + scope-echo-draft consume its footer conventions.
- TASK.md.tmpl field/placeholder layout -> owning task **derived-stamps**; template-dedup edits the SAME file — serialize (template-dedup depends-on derived-stamps).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] kickoff-truth       depends-on: none            — engine message layer: lane-aware kickoff (oneshot-first for single-task work) · new-task emits the FULL remaining call recipe for its lane · `--to` hand-off names its fill-first precondition · 2nd byte-identical failing call short-circuits with a change-something-first hint. GROUND FIRST: re-verify which transcript baits survive the current engine.
- [ ] derived-stamps      depends-on: none            — engine auto-stamps Ground SHA · Status DRAFT→FROZEN · Reported: · GATE dates; template fields become engine-filled placeholders (fast twin parity incl. the Ground-SHA inconsistency).
- [ ] template-dedup      depends-on: derived-stamps  — TASK.md.tmpl: 11 EXIT comments (~2.9KB, 23%) → one-line pointers to the phase guides' own exit_gate blocks; single-source the 5 rules currently stated 3-5× across SKILL.md/guides/template.
- [ ] gate-read-diet      depends-on: none            — report-template.md + run.md become read-once-per-session references; each gate's ~20 essential lines fold into its phase guide as a slim card; SKILL.md orient + flow-table trim (drop the Produces column).
- [ ] scope-echo-draft    depends-on: none            — freeze report renders the RESOLVED scope token list (mis-resolution becomes a zero-call read at the approval already happening); Scope line auto-drafted from §3 Grounding Touches, propose-not-impose, grammar untouched.
- [ ] risk-report-render  depends-on: gate-read-diet  — compact gate render for sensitivity:mechanical/fast lane; the full 8-section render reserved for security/data/architecture + the freeze.
- [ ] fold-draft-at-close depends-on: none            — milestone-done auto-DRAFTS the fold (deltas grouped, seed/drop pre-classified with one-line rationale); human still confirms the fold — no gate change.

## Exit criteria (observable; map each to the task that delivers it)
- [x] a fresh task's stdout hands the full lane recipe; a repeated byte-identical failing call gets the short-circuit hint — test-pinned   (← kickoff-truth; verified by test_kickoff_truth 7/7 `260cdef`)
- [x] a fresh task shows Ground SHA / Reported: / gate dates engine-written, agent never authors them — test-pinned   (← derived-stamps; verified by test_derived_stamps 4/4 `789e0cc` — and the stamp fired LIVE on tasks 4-7's own freezes)
- [x] TASK.md.tmpl carries zero EXIT restatements and stays under BOTH existing ceilings; tag census green   (← template-dedup; verified by test_template_dedup 6/6 `2fe9cb3` — v2 note: 4 pre-existing suites pin the scope-grammar restatement as load-bearing, kept verbatim; EXIT pointers ≤120B, comments 2568/2650)
- [ ] canonical happy-path read burden ≤ ~30KB (weight-audit method re-run, from 56KB)   (← gate-read-diet + template-dedup; PARTIAL 2026-07-13 — fast lane 37.0KB, full lane 49.1KB, big refs 0x on standard gates (were up to 64.4KB of re-reads); ≤30KB unmet — dominant residual is SKILL.md 12.8K, the flow-table trim did not ship; the binding number lands at the WM1 re-measure)
- [x] the freeze report renders the resolved scope list; a garbage declaration is visible AT the freeze   (← scope-echo-draft; verified by test_scope_echo_draft 6/6 `dbb3a97` — echoed LIVE on tasks 6-7's freezes incl. the add-method/../.add/ climb form)
- [x] a sensitivity:mechanical gate renders the compact report; security/data/architecture render the full one — test-pinned   (← risk-report-render; verified by test_risk_report_render 7/7 `60e8b64`)
- [x] milestone-done renders a fold DRAFT (grouped, pre-classified); fold stays human-confirmed — test-pinned   (← fold-draft-at-close; verified by test_fold_draft_at_close 5/5 `6abd287`)
- [x] floors byte-equivalent in behavior: freeze · red-first · gate record · HARD-STOP; full suite green; ENGINE_MD5/PKG re-pinned; twin parity holds   (← all; fence 3488/3488 OK at 7/7 — grew 3446→3488 = +42 new tests, zero weakened; ENGINE_MD5→8aef02ae, PKG→d83fc67f; parity suites green in every fence)
- [ ] pinned-meter WM1 re-measure (n=3): mean add.py calls ≤ 12 · zero --help turns · zero duplicate-identical failing calls · turns/cost ≤ 77.7t/$2.97 · oracle fidelity held · scope_violation count 0   (← all; release step, paid run ~$10-15 — HUMAN-GATED, not yet run)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py — lane-aware kickoff + full call recipe at new-task (kickoff-truth) · dup-failure short-circuit via OS-tmp sidecar (io_state.py, kickoff-truth v2) · Ground SHA stamped by freeze (derived-stamps) · _scope_echo at freeze (scope-echo-draft) · fold draft at milestone-done (fold-draft-at-close); templates — TASK.md.tmpl EXIT pointers + engine-stamp placeholders, 12055B/2568B under both ceilings (derived-stamps + template-dedup); ENGINE_MD5 e2ed6599→8aef02ae across 4 re-aims, PKG→d83fc67f @ kickoff-truth v2
- skill   : 3-plan.md + 6-verify.md gate render cards + read-once big refs (gate-read-diet) · right-size dispatch mechanical/fast→compact, security/data/architecture+freeze→full (risk-report-render) · SKILL.md read-once rule + same-pool compression, core landed exactly 18186/18186 · fast-lane.md render sentence (reference pool, same-guide absorbed); x3 trees synced every task
- book    : untouched (method semantics unchanged; guides carry the procedure)

### Cross-task evidence   (one row per task)
- kickoff-truth       : gate=PASS `260cdef` · tests=7 green (test_kickoff_truth) · residue=none (v2 change request: sidecar → OS tmp, byte fence clean)
- derived-stamps      : gate=PASS `789e0cc` · tests=4 green (test_derived_stamps) · residue=none (stamp inside the tamper fingerprint, proven by M2)
- template-dedup      : gate=PASS `2fe9cb3` · tests=6 green (test_template_dedup) · residue=none (v2: grammar restatements kept — 4 suites pin them)
- gate-read-diet      : gate=PASS `7728f2b` · tests=7 green (test_gate_read_diet) · residue=note: SKILL.md flow-table trim did not ship (pool landed at exactly 18186/18186 — no headroom left)
- scope-echo-draft    : gate=PASS `dbb3a97` · tests=6 green (test_scope_echo_draft) · residue=none (drop? is a question by design — exists() is rename-blind, flagged at freeze)
- risk-report-render  : gate=PASS `60e8b64` · tests=7 green (test_risk_report_render) · residue=none
- fold-draft-at-close : gate=PASS `6abd287` · tests=5 green (test_fold_draft_at_close) · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — 7/9 satisfied and cited inline above; OPEN: read-burden ≤30KB (partial, 56→37-49KB) + the pinned-meter re-measure (human-gated paid run)
- goal: convert measured evaporating ceremony into artifact effort without lowering any trust floor — the deliverable-side evidence is complete (7 gates PASS, fence 3488/3488, every floor exercised and held: byte fence, tamper tripwire, lean pools, slang/anchor guards each refuted a draft this milestone and were healed by sanctioned paths, zero tests weakened); the GOAL NUMBER (calls ≤12, ≤30KB, ≤77.7t/$2.97) binds only at the WM1 re-measure, which has not run

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] rebase feat/ceremony-to-effort onto main once PR #145 (flow-reorder, 3 milestones) merges — this branch stacks on it
- [ ] run the pinned-meter WM1 re-measure (n=3, ~$10-15, strategy-A harness) — the goal-number criterion binds here
- [ ] open a PR from the Close ship-review; human reviews + merges
- [ ] bundle into the next release cut per release.md (human tags/publishes)
