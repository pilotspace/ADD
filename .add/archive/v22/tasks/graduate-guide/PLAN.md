# TASK: graduate.md orchestration: cue → analytics → interview → production roadmap → confirmed flip

slug: graduate-guide · created: 2026-06-09 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: graduate-guide — make stage-graduation a real orchestration, not a bare label flip. TWO layers: (1) ENGINE GUARD — `add.py stage production` refuses without a roadmap; (2) a new `graduate.md` skill guide + SKILL routing that drives cue → analytics → interview → N production MILESTONE drafts → human confirm → the (now-guarded) flip. The 4th scope altitude after setup · intake · the milestone-loop.
Framings weighed: B = engine-guard + guide (chosen — "NEVER" enforced + red/green testable, mirrors the milestone goal-gate; human-chosen 2026-06-09) · A = guide-only prose (rejected — softens "NEVER", exit-criterion-4 untestable) · C = generalize the guard to every stage flip (rejected — the milestone scopes the floor to →production; prototype/poc/mvp flips stay byte-unchanged)
Must:
<must>
  - GUARD (engine, testable seam): `add.py stage production` REFUSES with a non-zero exit when 0 milestones in `state["milestones"]` have `stage == "production"`, printing the remediation ("draft ≥1 production milestone via graduate.md, or --force to override"). The refusal is a real gate (non-zero exit) — UNLIKE `graduation-report` (always 0) — because it stops an unsafe transition, like the milestone goal-gate's `milestone_goal_unmet`.
  - GUARD is GATHER-not-JUDGE: it counts a TALLY (≥1 production-stage milestone exists), never assessing whether those milestones are done/good/sufficient. The human + interview own readiness; the engine owns only the floor.
  - GUARD scope is `→production` ONLY: a flip to `prototype`/`poc`/`mvp` is the existing bare flip, byte-unchanged (output + exit code identical to today). No other `cmd_stage` behavior changes.
  - GUARD escape: a `--force` flag on `stage` overrides the refusal (precedent: `lock --force`) — preserving human authority for grandfathered/edge cases; `--force` prints that it bypassed the roadmap check.
  - GUIDE (`graduate.md`, prose — no new subcommand): drives the orchestration end-to-end — (1) recognize the `MVP covered → propose graduation` cue from `status`; (2) gather via `graduation-report` (analytics, read-only); (3) co-specify INTERVIEW — synthesize "what production means here" WITH the human (the judgment the engine refuses); (4) draft N≥1 production MILESTONEs via the EXISTING `new-milestone <slug> --stage production --goal …` + goal-gate criteria; (5) human CONFIRMS the roadmap; (6) ONLY THEN `add.py stage production` (the guard now passes). Reuses existing commands; adds no orchestration engine.
  - GUIDE invariant: `add.py stage production` is NEVER proposed outside the confirmed-roadmap path; the flip is the orchestration's FINAL recorded step; the engine never auto-flips (every step is human-confirmed).
  - SKILL routing (additive): `SKILL.md` routes to `graduate.md` on the cue (a "Beyond the bundle"-style pointer) AND the "Depth by stage" production line points at the orchestration (graduate.md), not just a depth hint. Existing routing text otherwise unchanged.
  - The guide is stage-agnostic in principle (prototype→poc, poc→mvp reuse it) but mvp→production is the documented v22 proof case.
</must>
Reject:
<reject>
  - `add.py stage production` with 0 production-stage milestones and no `--force` -> refuse, non-zero exit, state UNCHANGED :: "stage_no_roadmap"
  - no `.add/` project root -> existing `_require_root` die (unchanged) :: "no_project"
  - an unknown stage name -> existing `stage must be one of …` die (unchanged) :: "bad_stage"
  - a flip to prototype/poc/mvp -> NOT guarded; the bare flip succeeds exactly as today (a non-event, named so the contract pins "guard is →production only") :: "unguarded_by_design"
  - `add.py init --stage production` (a project DECLARED at production at creation) -> NOT guarded; this is an explicit at-creation human declaration (same authority as `--force`), not a transition, so the transition guard does not apply (named so the contract pins the boundary — the guard scopes to the `stage` flip, not init) :: "declared_at_init"
  - the engine deciding/judging production-readiness, or auto-flipping without human confirm -> refused by design; readiness is the interview's judgment, the flip is human-driven :: "would_be_judging" (design invariant)
</reject>
After:
<after>
  - `add.py stage production` refuses (`stage_no_roadmap`, non-zero, state byte-unchanged) until ≥1 production-stage milestone exists, then succeeds; `--force` overrides; every non-production flip is byte-identical to today.
  - `graduate.md` exists and drives cue → analytics → interview → roadmap(≥1) → confirm → flip; SKILL routes to it on the cue and the Depth-by-stage production line points at it.
  - The project stage cannot TRANSITION to `production` (via `add.py stage`) without a human-confirmed roadmap of ≥1 production milestone — the guard is the floor, the guide is the path, the human is the judgment. (`add.py init --stage production` stays an explicit at-creation declaration, out of scope of the transition guard — the boundary is named in Reject.) Exit criteria 4 + 5 are met.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The guard's roadmap PROXY = "≥1 milestone in `state["milestones"]` with `stage == "production"`, status-agnostic" — lowest confidence because it equates "a confirmed roadmap exists" with "a production-stage milestone record exists": it fires green on a freshly-drafted-but-unconfirmed production milestone, and (if all production milestones were later archived out of state) could refuse a legitimate re-flip. If wrong: the floor is slightly too low (a draft counts) or too high (archived roadmap missed) — bounded, since `--force` is the escape and the guide is the real confirmation path. The contract MUST pin exactly what counts (any state milestone with stage==production, regardless of status — chosen; archived-only edge deferred to --force).
  ⚠ The existing `test_stage_change` (test_add.py:104 — `init → stage production → assert production`, no roadmap) MUST be adapted under B (its premise — an unguarded production flip — no longer holds). Lowest-confidence #2 because it is a touch on an existing test and could read as weakening. If wrong: misread as gaming green. Mitigation the contract/tests must honor: split it — keep an unguarded-flip test on a non-production stage (mechanic preserved) AND add NEW guard tests (refuse@0 / succeed@≥1 / --force-override); disclose the adaptation at verify as a precondition-change, never a weakening.
  - [ ] `graduate.md` adds NO new subcommand — it documents the existing-command sequence + the one guard (matches loop.md/intake.md being prose-only) — confirm at contract (low stakes).
  - [ ] the `--force` flag name + the refusal exit code being non-zero (a real gate, unlike graduation-report's always-0) — confirm at contract (low stakes).
  - [ ] roadmap floor = N≥1 (exit criterion 4 says "≥1"), not a fixed N — confirm (low stakes).
  - [ ] SKILL routing is additive (a pointer + the Depth-by-stage production line), not a restructure — confirm (low stakes).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
# --- GUARD: Must rules (engine, red/green) ---
Scenario: Flip to production refuses without a roadmap            # Must-1 / Reject stage_no_roadmap
  Given an initialised project at stage mvp with 0 milestones whose stage is "production"
  When I run `add.py stage production`
  Then the command exits non-zero and prints "stage_no_roadmap" with the remediation hint
  And the project stage is still "mvp" (state byte-unchanged — no partial flip)

Scenario: Flip to production succeeds once a roadmap exists       # Must / After
  Given a project at stage mvp with ≥1 milestone whose stage is "production"
  When I run `add.py stage production`
  Then the command exits 0 and the project stage is "production"

Scenario: The guard counts a tally, not readiness               # Must-2 (gather-not-judge) / Reject would_be_judging
  Given a single production-stage milestone that is NOT done (status active, no exit criteria met)
  When I run `add.py stage production`
  Then the command exits 0 and the stage is "production"
  # proves the proxy is status-agnostic: it counts existence, it never judges whether the milestone is "ready"

Scenario: --force overrides the roadmap floor                    # Must-4 (escape)
  Given a project at stage mvp with 0 production-stage milestones
  When I run `add.py stage production --force`
  Then the command exits 0, the stage is "production", and it prints that the roadmap check was bypassed

Scenario: Non-production flips are unguarded and byte-unchanged   # Must-3 (scope) / Reject unguarded_by_design
  Given a project at stage mvp with 0 production-stage milestones
  When I run `add.py stage poc`
  Then the command exits 0 and the stage is "poc" (identical to today — no roadmap check applied)
  And no production-roadmap error is ever emitted for a non-production target

# --- GUARD: existing rejections preserved ---
Scenario: An unknown stage still dies                            # Reject bad_stage
  Given an initialised project
  When I run `add.py stage bogus`
  Then the command dies with "stage must be one of …"
  And the project stage is unchanged

Scenario: No project still dies                                  # Reject no_project
  Given a directory with no .add/ project
  When I run `add.py stage production`
  Then the command dies with the no-project message
  And nothing is created or changed

# --- GUIDE + SKILL: Must rules (prose, observable by reading the files) ---
Scenario: graduate.md drives the full orchestration              # Must (guide) + GUIDE invariant
  Given the repo after this task
  When I read .claude/skills/add/graduate.md
  Then it documents the ordered steps cue → analytics (graduation-report) → co-specify interview →
    N≥1 production MILESTONE drafts (new-milestone --stage production) → human confirm → stage production
  And it states the invariant that `stage production` is the FINAL step, never called outside the confirmed-roadmap path, and the engine never auto-flips

Scenario: SKILL routes to graduate.md on the cue                 # Must (SKILL routing)
  Given the repo after this task
  When I read .claude/skills/add/SKILL.md
  Then it routes to graduate.md on the graduation cue (a pointer in the body)
  And the "Depth by stage" production line points at the orchestration (graduate.md), not just a depth hint
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI  add.py stage <name> [--force]          # <name> ∈ STAGES = {prototype, poc, mvp, production}  (unchanged)

  name != "production"   ->  existing bare flip: state["stage"]=name; save; print "project stage -> <name>"; exit 0
                            (--force is a no-op here; output + exit code BYTE-IDENTICAL to today)

  name == "production"   ->  roadmap = _has_production_roadmap(state)
        roadmap OR --force ->  state["stage"]="production"; save; print "project stage -> production"; exit 0
                              (if --force AND not roadmap: also print "(--force: bypassed roadmap check — no production milestone drafted)")
        else               ->  _die("stage_no_roadmap: …draft ≥1 production milestone via graduate.md "
                                     "(new-milestone --stage production), or use --force.")  # non-zero exit, NO state write

  name not in STAGES     ->  _die("stage must be one of: …")        # bad_stage (existing, unchanged)
  no .add/ project       ->  _require_root() die                    # no_project (existing, unchanged)

Helper (pure, no writes — single source of the proxy):
  _has_production_roadmap(state: dict) -> bool
     := any(m.get("stage") == "production" for m in state.get("milestones", {}).values())
     # STATUS-AGNOSTIC (active|done|any) — resolves §1 ⚠#1: the floor is "a production milestone RECORD exists",
     # not "is done". Archived-out-of-state roadmaps fall to --force (deferred edge).

Reject responses (one per §1 code):
  stage_no_roadmap     -> _die, non-zero, state byte-unchanged (die precedes save)
  no_project           -> _require_root die (existing)
  bad_stage            -> _die "stage must be one of …" (existing)
  unguarded_by_design  -> N/A non-event: a non-production target never enters the guard branch
  declared_at_init     -> N/A out of scope: `cmd_init` writes state["stage"] directly (an at-creation declaration, not a transition); the guard lives ONLY in `cmd_stage`. Boundary named, not extended — `init --stage production` keeps the same human authority as `--force`. cmd_init is NOT modified by this task.
  would_be_judging     -> structurally impossible: the guard reads only the tally; there is no readiness field to compute

Prose deliverables (observable surface — asserted by content tests, the SEMANTIC verify path):
  graduate.md  NEW, documenting the ordered orchestration:
     cue (`MVP covered → propose graduation`) → `graduation-report` (analytics) → co-specify interview →
     `new-milestone --stage production` ×N≥1 + goal-gate → human confirm → `stage production`
     AND the invariant: `stage production` is the FINAL step, never outside the confirmed-roadmap path, engine never auto-flips.
     The flow is CONTINUOUS, not cue-reentrant: drafting the first production milestone makes `_graduation_ready` false (the "all milestones done" tally breaks), so the guide must NOT tell the user to re-await the cue after drafting.
  SKILL.md:
     (i) a routing pointer to graduate.md on the graduation cue;
     (ii) the "Depth by stage" production line references graduate.md (the orchestration), not only a depth hint.
  THREE-TREE PARITY (mirrors the add.py triple-tree): graduate.md is added AND SKILL.md edited IDENTICALLY across all three skill trees —
     `.claude/skills/add/` (dogfood) · `add-method/skill/add/` (canonical) · `add-method/src/add_method/_bundled/skill/add/` (bundle) —
     or `test_bundle_parity` goes red. Content tests assert the canonical + dogfood copies (the existing test_competency_deltas / test_dynamic_task_loop pattern).

Schema: READS state["milestones"][*]["stage"] (existing field — NO new field, NO migration); WRITES state["stage"] (unchanged).
        New arg `--force` on the `stage` subparser (additive; mirrors `lock --force`). New error token `stage_no_roadmap`.
        `cmd_init` is NOT touched (the guard scopes to transitions; init-at-production is the `declared_at_init` boundary).
Names (GLOSSARY): stage-graduation · graduation analytics · stage-goal-criteria · production · stage_no_roadmap (new code).
Contract tests: the §4 guard tests ARE the pinning (a CLI/engine change has no separate mock — the command behavior is the contract, as in graduation-analytics).
```

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-09. Bundle lowest-confidence surfaced at freeze: (1) status-agnostic roadmap proxy [contract]; (2) test_stage_change adaptation = precondition-change, not weakening [spec/test]. Resolved pre-freeze: second-door (declared_at_init boundary, cmd_init untouched) · three-tree skill parity · dogfood-safety. Changing this contract = change request back to SPECIFY.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every guard branch + one test per scenario; full engine suite stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  GUARD (new file `add-method/tooling/test_graduate_guard.py`):
  - test_production_refuses_without_roadmap: init mvp, 0 production milestones / run `stage production` / assert non-zero exit + "stage_no_roadmap" in stderr + state["stage"] still "mvp" (unchanged)
  - test_production_succeeds_with_roadmap: new-milestone --stage production / run `stage production` / assert exit 0 + state["stage"]=="production"
  - test_guard_is_status_agnostic_tally: a production milestone that is NOT done (active) / run `stage production` / assert exit 0 (proves the proxy counts existence, judges no readiness)
  - test_force_overrides_floor: 0 production milestones / run `stage production --force` / assert exit 0 + stage=="production" + bypass note printed
  - test_nonproduction_flip_unguarded: 0 production milestones / run `stage poc` / assert exit 0 + stage=="poc" + NO roadmap error emitted (byte-unchanged path)
  - test_bad_stage_still_dies: run `stage bogus` / assert die "stage must be one of" + stage unchanged
  - test_no_project_dies: no .add/ / run `stage production` / assert die no_project + nothing created
  GUIDE + SKILL (content tests, same file or `add-method/tooling/test_graduate_guide_docs.py`):
  - test_graduate_md_documents_orchestration: read `.claude/skills/add/graduate.md` / assert it names the ordered steps (cue · graduation-report · interview · new-milestone --stage production · confirm · stage production) AND the "final step / never outside confirmed path / no auto-flip" invariant
  - test_skill_routes_to_graduate: read `.claude/skills/add/SKILL.md` / assert it references graduate.md on the cue AND the Depth-by-stage production line references graduate.md
  EXISTING test adaptation (precondition-change, NOT a weakening — disclosed at verify):
  - `test_add.py::test_stage_change` flips straight to production with no roadmap (premise broken by the guard). Split: keep it as an unguarded NON-production flip (e.g. `stage poc`) to preserve the bare-flip mechanic; the production path is now covered by the new guard tests above.
  Triple-tree byte-identity + ENGINE_MD5 re-pin after the engine edit (canonical → .add → bundled); test_min_pillar LIFECYCLE already covers `stage` (no new subcommand) so no coverage-list change.
  SKILL THREE-TREE PARITY: add graduate.md + edit SKILL.md identically in all three skill trees (.claude/skills/add · add-method/skill/add · _bundled/skill/add) so test_bundle_parity stays green.
  DOGFOOD SAFETY: the guard SUCCESS path mutates state["stage"] — exercise it ONLY in a temp project; never run `stage production` on the real `.add/` (it would graduate the book's own project + leave a junk milestone). The REFUSAL path (0 production milestones → dies before save) is safe to dogfood live.
</test_plan>

Tests live in: `add-method/tooling/test_graduate_guard.py` · MUST run red (missing implementation) before Build.
RED CONFIRMED (2026-06-09): 4 fail for the right reason — refuse-without-roadmap (today succeeds, code 0) · --force (argparse: unrecognized arg) · graduate.md missing · SKILL routing missing. The 5 invariant-preservation tests are green now (success path · status-agnostic · non-production flip · bad_stage=argparse "invalid choice" · no_project) — they pin scope+existing-rejections that must STAY true.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **676 OK** (8.8s); `test_graduate_guard` = 9/9.
- [x] coverage did not decrease — **net +9** (new `test_graduate_guard.py`: 5 guard-behavior + 2 existing-rejection + 2 content). The production-flip mechanic is still proven (moved to `test_production_succeeds_with_roadmap`).
- [⚠] no test or contract was altered during build — **CONTRACT untouched** (§3 FROZEN @ v1). **TWO tests touched, neither a weakening** (disclosed for the gate): (1) `test_add.py::test_stage_change` production→poc = **precondition-change** — the guard broke the old premise (an unguarded production flip); the production path is now covered by the new guard tests. (2) `test_wording_lint` surface count 20→21 + `assertIn("graduate.md")` = **sanctioned self-maintenance** — a new guide legitimately grows the linted surface (same class as the LIFECYCLE-list extension in task 2). No assertion was loosened; no green was bought.
- [x] concurrency / timing of the risky operation is safe — **N/A**: single-process CLI, one synchronous read-then-write of `state.json`; the guard `_die`s BEFORE any save (refusal leaves state byte-unchanged — proven by `test_production_refuses_without_roadmap` asserting `stage` stays `mvp`).
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`argparse`/`json`/`pathlib`); no new import; the guard reads an existing in-state field, no shell/eval/network.
- [x] layering & dependencies follow CONVENTIONS.md — engine-only change in `cmd_stage` + a pure helper `_has_production_roadmap`; triple-tree byte-identity held (`add.py` md5 `eab62794` ×3) and **ENGINE_MD5 re-aimed** to match; three-tree skill parity held (graduate.md `6fcbd9c9` ×3, SKILL.md `182931f5` ×3).
- [x] a person reviewed and approved the change — Tin Dang · 2026-06-09 (human-led gate; two test touches disclosed + accepted)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_has_production_roadmap` is called in `cmd_stage` (add.py:~683); `--force` is read via `getattr(args, "force", False)` and wired on the `stage` subparser (add.py:2772); the `stage_no_roadmap` die is reachable (proven red→green by `test_production_refuses_without_roadmap`). Every new symbol is referenced.
- [x] DEAD-CODE (code) — no NEW dead symbol. **Pre-existing note (candidate observe):** `if args.stage not in STAGES: _die("stage must be one of …")` in `cmd_stage` is unreachable from the CLI (argparse `choices=STAGES` rejects an unknown stage first with "invalid choice") — this predates the task; `test_bad_stage_still_dies` asserts the real observable ("invalid choice"). Not introduced here, surfaced honestly, not papered over.
- [x] SEMANTIC (prose / non-code) — read graduate.md + the SKILL.md routing/Depth edits **in full**. Confirmed: ordered orchestration (cue → graduation-report → co-specify interview → `new-milestone --stage production` ×N≥1 → human confirm → guarded flip), the three invariants (final step · never auto-flips · continuous-not-cue-reentrant), slang-clean ("scope level"/"consolidate"). **Honesty bound:** the two content tests are **lexical marker checks**, NOT proof the orchestration *works* — the real proof of the guide is the human read + the guard's runtime behavior + the live refusal-path dogfood.

**Guard-surface-complete (the task's central claim, VERIFIED not believed):** project `state["stage"]` has exactly **two** writers — `cmd_init` (add.py:377, dict-literal = the `declared_at_init` boundary, out-of-scope by design) and `cmd_stage` (add.py:697, the GUARDED transition). No third writer; `load_state` does not normalize/migrate stage; `cmd_check` (add.py:930) only reads (`key in state`); `new-milestone` (add.py:1028) writes the *milestone* stage (the roadmap record the guard *counts*), not the project stage. → exit-criterion-4 ("cannot TRANSITION to production without a roadmap") holds.

**Live dogfood (refusal path — the safe one):** `add.py stage production` on a 0-production-milestone temp project → `stage_no_roadmap`, exit 1, stage byte-unchanged. The success path was exercised in temp projects only (never on the real `.add/`, per §4 DOGFOOD SAFETY).

### GATE RECORD
Outcome: PASS   <!-- human-led: TWO test files touched (precondition-change + sanctioned maintenance), contract FROZEN untouched, central claim verified, suite 676 OK, no security surface -->
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-09

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the roadmap PROXY's two known soft edges (named in §1 ⚠#1) — (a) it fires green on a freshly-DRAFTED-but-unconfirmed production milestone (a draft counts as a roadmap), and (b) it would refuse a legitimate re-flip if every production milestone were archived out of `state["milestones"]`. The live signal for (b) is a `--force` used to clear `stage_no_roadmap` when a roadmap genuinely exists but was archived — that is the trigger to extend the proxy to an archived-aware source (today deferred to `--force`). Separately, watch the `--force` rate itself: every `--force` on `→production` is a human stepping over the floor; a rising rate means the floor sits wrong.
Spec delta for the next loop: the proxy is status-AGNOSTIC by contract (any production-stage milestone counts, done or active). If a future interview needs a *confirmed* roadmap (not merely a drafted one) to satisfy the floor, that is a CONTRACT change-request back to this task — the floor would need a confirmation field that does not exist today; never scrape milestone text for it. Cross-artifact vocabulary debt surfaced for task 4 (book-align): this frozen §1 + MILESTONE.md + GLOSSARY say "altitude"/"scope altitude" while the approved guide term (graduate.md) is "scope level" — reconcile to one term and document the `stage_no_roadmap` error code.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->

- [ADD · folded] **To verify a "X can NEVER reach state S" guarantee, enumerate every WRITER of S — not the string-callers of the command.** The first pass grepped `stage production` (string callers); the load-bearing proof was grepping every assignment to `state["stage"]` (the guarded field). Lesson: a transition guard's completeness is the full set of mutators of the target state — enumerate it, never infer it from the obvious entry point. (evidence: advisor's pre-gate check turned the central claim believed→verified — exactly two writers, cmd_init=declared_at_init boundary + cmd_stage=guard, no third, load_state does not normalize)
- [SDD · folded] **A guarded transition must explicitly NAME its at-creation door, or the "NEVER" silently leaks.** `init --stage production` writes the guarded state directly, bypassing the transition guard — a "second door." Resolved by scoping the guard to transitions and naming `init` the `declared_at_init` boundary (same human authority as `--force`), not by silently leaving it nor over-extending the guard into init. Lesson: floor = `cmd_stage` guard · path = `graduate.md` · judgment = the human interview — and every door into the floored state is either guarded or named-as-boundary, never unlisted. (evidence: advisor caught the second door at the freeze; the §3 After-claim was tightened from "cannot reach" to "cannot TRANSITION to" production)
- [TDD · folded] **A prose deliverable's content tests are lexical MARKER checks, not proof the behavior works — keep §6 honest about what they verify.** `test_graduate_md_documents_orchestration` / `test_skill_routes_to_graduate` assert the guide NAMES the right steps; they cannot prove the orchestration actually drives a human through cue→roadmap→flip. Lesson: prose tests pin vocabulary (a regression fence); the behavior is verified by the human and by whatever ENGINE seam the prose points at, never by the marker test alone — sibling of graduation-analytics' structural-vs-lexical delta. (evidence: advisor flagged the SEMANTIC over-claim risk; §6 records the guide's real proof as the human read + the guard's runtime behavior + the live refusal dogfood)
- [TDD · folded] **A new guard that invalidates an existing test's PREMISE is adapted by SPLITTING, not loosening — and disclosed at the gate as a precondition-change.** `test_stage_change` flipped straight to production with no roadmap; the guard broke that premise. Fix: keep the bare-flip mechanic on a non-guarded stage (`stage poc`) AND add the guard tests (refuse@0 / succeed@≥1 / --force) → net coverage +9. Lesson: never weaken an assertion to buy green — when a precondition genuinely changes, move the old guarantee to where it still holds, add the new guarantee, and surface the touch at verify so it is judged, not hidden. (evidence: §6 ⚠ discloses both touched test files — this + test_wording_lint's sanctioned surface-count bump — as non-weakenings; the human-led gate accepted them)
