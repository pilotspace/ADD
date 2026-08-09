# MILESTONE: flow-honesty — make ADD's stated guarantees engine-true or honestly labeled

goal: close the gap between ADD's stated guarantees and what the engine mechanically enforces, making each gate either engine-true or honestly disclosed
rationale: sub-milestone — harvested from the 2026-06-27 whole-flow audit (4 parallel reviewers, findings verified against engine source). Relationship: *extends* flow-enforcement + audit-hardening (which engine-enforced individual seams); this sweeps the WHOLE flow for guarantee-vs-reality gaps. *Overlaps* the 61 open SPEC deltas — the delta-drain task addresses them head-on. Root cause: the docs name mechanical guarantees the engine delivers only by convention; a reader cannot tell a steel gate from a painted one.
stage: mvp · status: active · created: 2026-06-27T07:52:15+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) a UNIVERSAL freeze gate — `contract_not_frozen` fires for every task at tests→build, not just `--fast`/`--await-confirm`, with an explicit `--skip-freeze` escape + grandfathering; (2) DELTA-DRAIN backpressure — a loud, forceable open-SPEC-delta floor so deltas resolve (drain the 61); (3) shape-level audit/check LINTS for an unfilled §6 Deep-checks block and an unset `risk:` at verify (presence, never judgment); (4) HONEST naming — rename the `release_tests_red` proxy + relabel scope.md's "the invariant" + reframe `goal_not_auto_ready`'s "earns trust"; (5) SECURITY-escalation disclosure — say plainly a *missed* finding is invisible to the engine; (6) make the earned-green refute-read a MANDATORY recorded verdict before an auto-PASS is valid; (7) STALE-guide sync (5-build deferral note, auto-PASS precondition list, book→TASK.md artifact cross-ref).
Out: the lower-priority sweep (parallel-stream scope false-positive on serial merge-back, soul.md reject-code formatting, zero-exit-criteria milestone close, graduation queued-guard) — recorded as forward deltas, deferred to a follow-up. Any change that makes the engine CLASSIFY scope/security/wiring (would break judgment-free) is OUT. Changing the v7 `auto`-default itself is OUT (the reversal stands).

## Shared decisions & glossary deltas   (living — every task must honor these)
- judgment-free engine stays invariant: every new lint checks SHAPE / PRESENCE only (does the block exist? is the field filled?), never meaning — `(verify: it works)` must still pass a presence lint.
- honest labeling over new gates: default to disclosure + a measure-not-block lint; reserve a real (forceable) gate for the two STRUCTURAL holes only — universal freeze and delta-drain.
- backward-compatible: grandfather every pre-existing task/milestone; nothing retro-reds a done record. New gates apply going forward, with a named escape.
- security HARD-STOP semantics are UNCHANGED — this milestone only improves the *disclosure* of its honor-system edge, never weakens the stop.

## Shared / risky contracts (freeze these first)
- the universal freeze-gate trigger + `--skip-freeze` escape semantics (changes the tests→build crossing for EVERY task) -> owning task `freeze-gate-universal`
- the delta-drain floor shape — where it fires (release floor), its reject code, and that it is `--force`-able but loud -> owning task `delta-drain`
- the recorded earned-green refute-read verdict field in §6 that the audit MEASURES (`refute_unrecorded`, never a gate-block) -> owning task `self-grading-refute-record`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] freeze-gate-universal        depends-on: none                                                   — fire `contract_not_frozen` for every task at tests→build (drop the `_optin or fast` condition); add `--skip-freeze` escape + grandfather pre-existing tasks [H1]
- [ ] delta-drain                  depends-on: none                                                   — add a loud, forceable open-SPEC-delta floor in the release gate (+ a `status` staleness line); drain or explicitly carry the 61 open deltas [H2]
- [ ] guarantee-audit-lints        depends-on: none                                                   — add shape-level lints: `shallow_deep_check` (§6 Deep-checks block unfilled at gate/audit) + `risk_unset` (`risk:` absent when a task reaches verify); presence-only [M3-lints]
- [ ] honest-reject-naming         depends-on: none                                                   — rename `release_tests_red`→`release_build_in_flight` (code + release.md); relabel scope.md "the invariant"→opt-in gate; reframe `goal_not_auto_ready` "earns trust"→"measures citation presence" [M3-naming]
- [ ] security-escalation-disclosure depends-on: none                                                 — document in 6-verify.md + run.md that `unescalated_security_note` catches MIS-escalation but cannot detect a MISSED finding; name the human spot-audit as the only backstop under `auto` [M1]
- [ ] self-grading-refute-record   depends-on: none                                                   — make the earned-green refute-read a recorded §6 verdict that `add.py audit` MEASURES (`refute_unrecorded`, never a gate-block) + disclose the auto mandate in run.md/6-verify.md/book; engine still never spawns it (the AI records the verdict) [M4]
- [ ] stale-guide-sync             depends-on: freeze-gate-universal, guarantee-audit-lints, honest-reject-naming — remove 5-build's stale "scope gate deferred" note; make the auto-PASS precondition list identical across run.md / 6-verify.md / book ch.08; add a book ch.03/04 → TASK.md §1/§2 artifact cross-ref [M5]

## Exit criteria (observable; map each to the task that delivers it)
- [x] a full-lane task on a plain milestone cannot cross tests→build with a DRAFT §3 — `--skip-freeze` is the only bypass   (verify: test_freeze_gate_universal — PASS)        (← freeze-gate-universal)
- [x] `add.py release` refuses (forceable, loud) when open SPEC deltas > 0; the 61 are drained or explicitly carried   (verify: test_delta_drain — PASS + `add.py deltas` = 0 open)  (← delta-drain)
- [x] `add.py audit` flags an unfilled §6 Deep-checks block and an unset `risk:` at verify                            (verify: test_guarantee_lints — PASS)               (← guarantee-audit-lints)
- [x] `release_tests_red` is gone (renamed) everywhere; scope.md + `goal_not_auto_ready` framing read honestly         (verify: grep clean + test_reject_names — PASS)            (← honest-reject-naming)
- [x] 6-verify.md + run.md state plainly that a MISSED security finding is invisible to the engine                    (verify: doc grep — run.md:120 + 6-verify.md present)    (← security-escalation-disclosure)
- [x] under `auto` the earned-green refute-read verdict is recorded in §6; `add.py audit` surfaces an unrecorded one (`refute_unrecorded`, a measure not a gate) + run.md/6-verify.md/book disclose the mandate   (verify: test_refute_record_required — PASS)        (← self-grading-refute-record)
- [x] 5-build deferral note removed; auto-PASS precondition list identical across the three files; book→TASK.md cross-ref present   (verify: test_tree_parity + test_stale_guide_sync — PASS + doc grep clean)  (← stale-guide-sync)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : two REAL (forceable, loud) gates — universal freeze (`contract_not_frozen` for every task at tests→build + `--skip-freeze` escape) and the delta-drain release floor (`release_build_in_flight`, `--force`-able + `status` staleness line); three measure-not-block audit lints (`shallow_deep_check`, `risk_unset`, `refute_unrecorded`); honest reject-name rename (`release_tests_red`→`release_build_in_flight`); the §6 `### Refute-read verdict` template field the audit measures. Engine grew across tasks 1–6; task 7 was PROSE-ONLY (ENGINE_MD5 9d73e5ab unchanged).
- skill   : run.md owns the ONE canonical 8-item auto-PASS list; 6-verify.md records the mandatory earned-green refute verdict under `auto` + the missed-finding disclosure + points to run.md; 5-build.md says the scope gate is ENFORCED (stale `scope-gate-enforce` deferral removed); scope.md "the invariant"→opt-in gate; `goal_not_auto_ready` reframed "measures citation presence".
- book    : ch.08 names the same auto-PASS set + the never-marked-security-finding blind spot + spot-audit backstop; ch.03/04 "Produces:" cross-ref §1/§2 of TASK.md.

### Cross-task evidence   (one row per task)
- freeze-gate-universal        : gate=PASS · test_freeze_gate_universal green · residue=none (recorded `--skip-freeze` escape + grandfather)
- delta-drain                  : gate=PASS · test_delta_drain green · residue=none (open SPEC deltas drained/carried → 0)
- guarantee-audit-lints        : gate=PASS · test_guarantee_lints green · residue=none (presence-only, exit stays gated on findings)
- honest-reject-naming         : gate=PASS · test_reject_names green + grep clean · residue=none
- security-escalation-disclosure : gate=PASS · doc-grep disclosure present (run.md:120 + 6-verify.md) · residue=none
- self-grading-refute-record   : gate=PASS · test_refute_record_required green · residue=none (dogfooded its own §6 verdict)
- stale-guide-sync             : gate=PASS · test_stale_guide_sync + test_tree_parity green · residue=ONE flagged collateral test-token edit (test_scope_decl_template scope-gate-enforce→scope_violation), refute-read EARNED-flagged for spot-audit
- whole-suite                  : full suite 2167/0 · check 478/0 · audit exit 0 · 0 open SPEC deltas · ENGINE_MD5 9d73e5ab

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — EC1↔freeze-gate-universal · EC2↔delta-drain · EC3↔guarantee-audit-lints · EC4↔honest-reject-naming · EC5↔security-escalation-disclosure · EC6↔self-grading-refute-record · EC7↔stale-guide-sync
- goal: close the gap between ADD's stated guarantees and what the engine mechanically enforces — every gate now either engine-true (universal freeze, delta-drain floor, scope gate) or honestly disclosed (missed-finding blind spot, the three measure-not-block lints, the recorded earned-green refute-read). Proof: the two STRUCTURAL holes became real forceable gates; the four honor-system edges became plain disclosures + presence lints — no new claim in the guides/book contradicts the engine (verified live: scope_violation ships via cmd_gate, audit emits the 3 lints, freeze gate fires universally).

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] commit tasks 5–7 (uncommitted on the working branch) with the standard message format; review the diff first
- [ ] open a PR from this branch — the human reviews + merges (spot-audit the one flagged test-token edit in stale-guide-sync)
- [ ] fold confirmed deltas → archive the 7 done tasks (`add.py fold` → `compact-foundation` → `milestone-archive`)
- [ ] bundle into the next release cut (release.md) when ≥1 milestone is releasable — tag / publish / deploy is human-run
