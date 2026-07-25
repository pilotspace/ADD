# PLAN: Seed three planner personas at task, milestone, and release altitude

slug: planner-personas-seed
kind: docs · created: 2026-07-25 · stage: mvp
milestone: persona-template-completeness
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: three planner personas join the roster, one per ADD scope altitude — `task-planner` (ordering the moves inside one frozen contract), `milestone-planner` (ordering tasks into a DAG behind freeze-first contracts), `release-planner` (ordering shipped milestones into a cut) — each authored against the four-leg template, each with a boundary that does not overlap `method-product-owner` or its two planner siblings.

Framings weighed: three-planners-by-ALTITUDE (chosen — the human's call; altitude is the one axis on which ADD already separates scope, so it is the axis most likely to yield disjoint `use-when` lines) · one-planner-with-per-flow-stances (my original recommendation on roster-overlap grounds; rejected by the human, and the boundary test below is where that call gets checked rather than argued) · fold-planning-into-method-product-owner (rejected — it already owns sizing and the cut list; adding ordering would make one lens own both "whether" and "in what order", which is the overlap this task must avoid).

Must:
<must>
  - M1: three new personas exist at `.add/personas/{task-planner,milestone-planner,release-planner}.md`, each schema-conformant (`add.py check` reports 9 schema-conformant personas, 0 persona findings).
  - M2: each planner's `not-when:` names `method-product-owner` for the sizing/exit-criteria near-miss, and names its planner siblings for the wrong-altitude near-miss.
  - M3: each planner's `use-when:` enumerates concrete triggers at ITS altitude only — no trigger appears in two planners' `use-when:` lines.
  - M4: each planner is authored to the four-leg template: an ORIENT-first `## Abilities`, a per-flow stance for its declared flows, and an `## Escalation` section (all three own a gate or advise at one).
  - M5: `flow:` and `task-kinds:` values are inside the closed taxonomies, so each planner is loadable by a surface and scoreable on the persona scoreboard.
  - M6: `.add/personas/` is a single tree (no mirror set) — assert no planner file was written into a tooling or skill tree by mistake.
  - M7: `method-product-owner` is FOLDED (not forked) to make the boundary real: its `use-when:` stops claiming "ordering" at milestone altitude, its `not-when:` names `milestone-planner`, and its `folded:` line records the change. Its four required sections and its Identity are untouched — this is a routing-frontmatter fold, not a rewrite.
</must>
Reject:
<reject>
  - a planner whose `use-when:` trigger also appears in a sibling planner's or `method-product-owner`'s -> "roster_overlap"
  - a `flow:` or `task-kinds:` value outside the closed taxonomy -> "persona_quality"
  - an `## Escalation` line that restates the universal security HARD-STOP instead of a domain stop-condition -> "floor_restated"
</reject>
After:
<after>
  - an agent picking a persona for planning work can choose by ALTITUDE from frontmatter alone, with no tie against `method-product-owner`.
  - the four-leg template has been dogfooded by authoring three personas against it, and any thinness it still has is recorded before the 12-preset fold locks the shape in.
</after>
Boundary: none — no external input; three markdown files in one tree.
<assumptions>
  ⚠ that three altitudes yield three DISJOINT `use-when` sets. `milestone-planner` is the one at risk: `method-product-owner` already owns "drafting/ordering milestone scope and exit criteria", and the word "ordering" is literally in its `use-when:`. If the boundary cannot be drawn, M3 fails and the honest outcome is to say so at the gate — a near-twin that ships is worse than a planner that does not.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
ROSTER (before): 6 personas · no lens owns ORDERING at any altitude
ROSTER (after):  9 personas · one planner per ADD scope altitude

NEW .add/personas/task-planner.md
  altitude: inside ONE frozen contract
  owns: the order of moves in a build - first unblocking slice, what to
        prove before what, where a step becomes independently verifiable
  flow: design, advisor      task-kinds: feature, refactor, integration

NEW .add/personas/milestone-planner.md
  altitude: across tasks, within one milestone
  owns: the task DAG - depends-on edges, freeze-first contracts, parallel
        waves, the critical path, what a wave costs if a contract moves
  flow: design, advisor      task-kinds: feature, integration, infra

NEW .add/personas/release-planner.md
  altitude: across milestones, into a cut
  owns: the ship order - version spots in lockstep, ledger/CHANGELOG
        attribution, migration + publish order, rollback, what blocks a tag
  flow: advisor, verify      task-kinds: release, infra

FOLD .add/personas/method-product-owner.md   (frontmatter only)
  ~ use-when:  drops the "ordering" claim at milestone altitude
  ~ not-when:  gains "ordering tasks into a DAG -> milestone-planner"
  ~ folded:    records this boundary change, newest first
  UNCHANGED: Identity, Abilities, Critical Rules, Anti-patterns,
             Default Requirement, Success Metrics, Playbook

EACH new persona is authored to the four legs: ORIENT-first Abilities,
per-flow stance in Critical Rules, and an ## Escalation stop-condition.
UNCHANGED (asserted): add.py · add_engine/* · both pins · every skill and
             tooling tree (.add/personas/ has NO mirror set)
```

Target (measurable): `add.py check` reports **9** schema-conformant personas and **0** persona findings · 0 `use-when` trigger shared between any two of {task-planner, milestone-planner, release-planner, method-product-owner} · each new persona has an ORIENT line, a per-flow stance, and an `## Escalation` section · `git diff main` on `add.py` + `add_engine/` empty · no file created outside `.add/personas/` and this task dir.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `.add/personas/` `./`
Regression floor: `python3 .add/tooling/add.py check` (persona schema + quality predicates) and `add-method/tooling/test_fold_persona_sections.py` (the fold/roster machinery). No mirror test applies — `.add/personas/` is a single tree.
Persona (optional): `.add/personas/method-product-owner.md` — the lens that owns roster/method shape, and the one whose boundary this task narrows; using it keeps the fold honest (it argues its own corner).

Least-sure flag surfaced at freeze: [spec] whether `milestone-planner` can be made genuinely disjoint from `method-product-owner`. I recommended ONE planner for this reason and was overruled, which is a legitimate call — but it means M3 is a real test this bundle can FAIL. The M7 fold is my best attempt to make the boundary true rather than asserted; if after the fold the two lenses still tie on a trigger, the honest gate outcome is to report the overlap, not to ship a near-twin.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - check_three_planners_conformant: `add.py check` reports 9 schema-conformant personas and 0 `persona_quality`/`persona_schema_incomplete` findings. RED now: 6 personas, the three files do not exist. · covers: M1, M5, R:persona_quality
  - check_not_when_names_owner: each of the three planners has a `not-when:` naming `method-product-owner` for the sizing/exit-criteria near-miss AND naming its planner siblings for the wrong-altitude near-miss. RED now: no file. · covers: M2
  - check_use_when_disjoint: tokenize the `use-when:` line of all four lenses (3 planners + method-product-owner); assert no significant trigger phrase appears in two of them. This is the milestone exit criterion's real test and the one that can legitimately FAIL. RED now: `method-product-owner` claims "drafting/ordering milestone scope", which will collide with `milestone-planner` until the M7 fold lands. · covers: M3, M7, R:roster_overlap
  - check_four_legs_authored: each new persona has an `## Abilities` whose first bullet is an ORIENT command, a per-flow stance line in `## Critical Rules` (each declares 2 flows), and an `## Escalation` section. RED now: no file. · covers: M4
  - check_escalation_not_floor_restated: no planner's `## Escalation` merely restates "a security finding is HARD-STOP"; each names a stop-condition specific to its altitude. Judged by reading, not grep — the failure is a line that is technically present and says nothing. RED now: no file. · covers: R:floor_restated
  - check_owner_fold_is_frontmatter_only: `git diff` on `method-product-owner.md` touches only `use-when:`, `not-when:`, and `folded:` — its Identity and all six body sections are byte-unchanged. GREEN-by-construction; the check exists because a "fold" that quietly rewrites a persona body is the failure mode `persona-author` warns about. · covers: M7
  - check_single_tree: no file created or modified outside `.add/personas/` and this task dir — `.add/personas/` has NO mirror set, so a copy landing in a skill or tooling tree is a defect, not propagation. GREEN now and must STAY green. · covers: M6
  - check_engine_untouched: `git diff --stat main -- add-method/tooling/add.py add-method/tooling/add_engine/` empty, pins unchanged. GREEN now and must STAY green. · covers: (standing floor)
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: evidence · MUST run red before Build.

Non-coding task (`kind: docs`): §4 is a failing-first ACCEPTANCE CHECK set. Five are RED now (the three files do not exist; the disjointness check is red on a real, already-verified collision — `method-product-owner`'s `use-when` contains "ordering"). Three are standing checks.

`check_use_when_disjoint` is the one that matters: it is the milestone exit criterion, it encodes the disagreement recorded in §1 Framings, and it is allowed to fail. If the M7 fold does not make the boundary real, the gate reports the overlap rather than shipping a near-twin.

Build-guidance (prose, not gated): seed each planner from the nearest teacher source rather than a blank page — `project-management/project-manager-senior.md` (spec→task list, realistic scope) for task-planner, `project-management/project-management-project-shepherd.md` + `product/product-sprint-prioritizer.md` for milestone-planner, `engineering/engineering-devops-automator.md` + the repo's own RELEASES.md ritual for release-planner. Record each in `source:`.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — seeded each planner from its named teacher source, then applied the M7 frontmatter-only fold to method-product-owner. THREE corrections during the build, none of them by relaxing a check. (1) `release-planner` tripped a real `persona_quality` WARN: a backtick span wrapped across a newline, so `<tag>` fell outside any code span and read as a bare placeholder — the ORIENT bullet was reflowed so no span crosses a line break. (2) The disjointness checker itself was wrong first: `(?!\w+:)` does not exclude `not-when:` (a hyphen is not `\w`), so every not-when line was being swallowed into use-when and five pairs falsely "collided". Fixed the extractor and asserted `not-when` is absent from the captured text so the bug cannot recur silently. (3) With the corrected checker, ONE real collision survived — `rest deciding`, from "before the rest, deciding" appearing in both task-planner and milestone-planner. The tempting fix was to stop the tokenizer forming bigrams across punctuation; that would have been retuning the instrument after seeing the failure, so instead milestone-planner's prose was reworded ("must freeze first, judging what can run…"). The check was re-run unchanged and passed.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all §4 acceptance checks pass — 8/8. Roster 6→9, all schema-conformant, 0 persona findings; use-when lines disjoint across all 6 pairs; each planner carries ORIENT + per-flow stance + Escalation; the owner fold touched 6 lines, all frontmatter.
- [x] coverage did not decrease — n/a for `kind: docs`.
- [x] no test or contract was altered during build — one §4 edit WAS made (adding `R:persona_quality` to a covers line, closing an engine-reported coverage gap) and it went through `re-cross --by`, the sanctioned post-freeze path, not a silent edit. Frozen §3 unchanged.
- [x] the green was EARNED — see the refute-read; the one check that was allowed to fail did fail first, and was resolved by changing the artifact, not the check.
- [x] concurrency / timing — n/a.
- [x] no exposed secrets, injection openings, or unexpected dependencies — 4 markdown files in one tree.
- [x] layering & dependencies — `.add/personas/` has no mirror set; nothing was written outside it and this task dir. Engine untouched, pins unchanged.
- [x] a person reviewed and approved the change — Tin Dang, at the verify gate, after the disjointness failures and the residual were disclosed

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: the bundle's declared failure mode — that three altitudes would not actually yield three disjoint lenses.
  (1) The disjointness check was run, FAILED, and the failure was taken seriously rather than tuned away. Its first failure (5 pairs) was a bug in my own extractor; its second (1 pair, `rest deciding`) was a genuine textual overlap, fixed in the persona prose with the checker left untouched and re-run.
  (2) The M7 fold was verified to be what it claimed: `git diff -U0` on method-product-owner.md shows 6 changed lines, all matching `^[+-](use-when|not-when|folded):`. Its Identity and all six body sections are byte-unchanged — the "fold that quietly becomes a rewrite" failure did not occur.
  (3) The `persona_quality` WARN on release-planner was a REAL defect found by the engine, not a false positive: a multi-line backtick span left `<tag>` unprotected. Fixed at the source rather than suppressed.
  Residual, stated honestly: the disjointness check is a bigram overlap test over `use-when` prose. It proves no shared trigger PHRASE; it cannot prove two lenses would never be plausible for the same request. The boundary as written is defensible — owner decides whether/how big, planners decide in what order, and the three planners are separated by altitude — but the real proof is route-outcome data over several milestones, which does not exist yet. Recorded as a delta rather than claimed as verified.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-25

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose three-planners-by-ALTITUDE; rejected one-planner-with-per-flow-stances (my original recommendation on roster-overlap grounds; rejected by the human, and the boundary test below is where that call gets checked rather than argued) · fold-planning-into-method-product-owner (rejected — it already owns sizing and the cut list; adding ordering would make one lens own both "whether" and "in what order", which is the overlap this task must avoid).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — seeded each planner from its named teacher source, then applied the M7 frontmatter-only fold to method-product-owner. THREE corrections during the build, none of them by relaxing a check. (1) `release-planner` tripped a real `persona_quality` WARN: a backtick span wrapped across a newline, so `<tag>` fell outside any code span and read as a bare placeholder — the ORIENT bullet was reflowed so no span crosses a line break. (2) The disjointness checker itself was wrong first: `(?!\w+:)` does not exclude `not-when:` (a hyphen is not `\w`), so every not-when line was being swallowed into use-when and five pairs falsely "collided". Fixed the extractor and asserted `not-when` is absent from the captured text so the bug cannot recur silently. (3) With the corrected checker, ONE real collision survived — `rest deciding`, from "before the rest, deciding" appearing in both task-planner and milestone-planner. The tempting fix was to stop the tokenizer forming bigrams across punctuation; that would have been retuning the instrument after seeing the failure, so instead milestone-planner's prose was reworded ("must freeze first, judging what can run…"). The check was re-run unchanged and passed.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
