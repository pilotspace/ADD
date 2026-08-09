# TASK: Wire every human-gate path to render the decision arc

slug: arc-gate-wiring · created: 2026-06-09 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a one-line cue at the human-approval moment of each of the SEVEN gate-path guides, pointing at `report-template.md`'s ARC block, so the goal·done·plan arc is traceable in every gate path — not only via the single `SKILL.md` pointer. The seven gate→file pairs: baseline-lock=`phases/0-setup.md` · contract-freeze=`phases/3-contract.md` · verify=`phases/6-verify.md` · intake=`intake.md` · scope=`scope.md` · milestone-close=`loop.md` · graduation=`graduate.md`.
Framings weighed: per-guide-cue-pointing-central (chosen — definition stays single-source, each path becomes traceable) · per-guide-full-arc-detail (re-spells report-template's per-gate examples into each guide — violates the repo's progressive-disclosure rule "do not duplicate the book") · central-only-no-guide-edits (relies on SKILL.md alone — fails exit-criterion-2's "traceable in each gate path": a reviewer opening `6-verify.md` finds no cue there)
Must:
<must>
  - each of the seven gate-path guides gains a one-line cue at its human-approval moment naming `report-template.md`'s ARC and the goal·done·plan shape — all seven files edited (the gate→file map above; verified present, none silently dropped).
  - the cue POINTS at the central definition; it does not re-spell the per-gate content — `report-template.md` keeps sole ownership of the seven-gate rule + the four worked per-gate examples (progressive disclosure; one definition, no per-guide divergence).
  - [SEPARABLE — this is task-1's observe delta, NOT an exit criterion; the human folds-here-or-defers-to-a-task-4 at the freeze] `report-template.md`'s Hard rules gain the digest-reconciliation rule: a gate report's ⚠ FLAGS must reconcile with `report --decide`'s open-item COUNT before the ask (the central "engine wins" rule sharpened; one place, not per-guide).
  - the three skill trees stay byte-identical (edit canonical `add-method/skill/add/` → sync dogfood `.claude/skills/add/` + bundle).
  - presentation only: no gate LOGIC change, no `add.py` change, no frozen-contract edit; `test_report_arc` (task 1's marker) stays green.
</must>
Reject:
<reject>
  - any of the seven gate-path guides is left without an arc cue -> "gate_unwired"   (test asserts the cue in all 7 files — the guard against wiring six and missing one)
  - a guide re-spells the per-gate arc content instead of pointing at `report-template.md` -> "arc_duplicated"   (human read; progressive-disclosure violation, central stays single-source)
  - a cue or the reconcile-rule edit changes gate LOGIC or an outcome semantic -> "arc_changes_gate"   (human read; scope Out, presentation only)
  - banned slang or an emphasis token enters the new prose -> "wording_regression"   (test_wording_lint / test_ubiquitous_language — all 7 guides + report-template.md are on the 21-file lint surface)
</reject>
After:
<after>
  - all seven gate-path guides name the arc at their approval moment, traceable per path; the definition stays central in `report-template.md`; the wording-lint + ubiquitous-language + parity surfaces stay green; `test_report_arc` still green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  - [x] resolved at freeze: Fork A chosen (a one-line cue per guide POINTING central) over Fork B (inline the goal·done·plan triple per guide) — the human froze the contract on Fork A; the "is a cue enough for traceable" reading is confirmed by the human read at the verify gate.
  - [x] FOLD HERE (resolved at freeze): the digest-reconciliation rule lands in report-template.md's Hard rules as part of THIS task; tested as a SEPARATE case so the wiring's green bar (exit-criterion 2) never depends on it.
  - [x] the milestone-close report moment lives in `loop.md` (the goal-gate / `milestone-done` refuse-to-close), not `fold.md` — verified via grep (loop.md:13 holds the close-refusal; fold.md is the consolidation, a different moment).
  - [x] re-editing `report-template.md` does not break `test_report_arc.py` — it asserts the ARC block shape (labels, gates, sourcing, pointer), not the Hard-rules list — verified by reading the test this session.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: every gate-path guide names the arc at its approval moment
  Given the seven gate-path guides (0-setup · 3-contract · 6-verify · intake · scope · loop · graduate)
  When each guide is edited
  Then all seven name report-template.md's ARC and the goal·done·plan shape at the human-approval moment
  And the SKILL.md central pointer (task 1) stays present and unchanged in meaning

Scenario: the cue points central, it does not re-spell the per-gate content
  Given report-template.md owns the seven-gate rule and the four worked per-gate examples
  When a gate guide adds its cue
  Then the cue references report-template.md rather than re-listing the per-gate arc content
  And report-template.md remains the single definition of the arc shape

Scenario: the reconcile rule is folded into report-template (if the human folds it here)
  Given task 1's observe surfaced the digest-reconciliation rule (FLAGS count must match report --decide)
  When the human chooses at the freeze to fold it into this task
  Then report-template.md's Hard rules gain the reconcile rule, in one central place
  And the verify-gate guide cue may note it; no per-guide duplication of the rule

Scenario: the three skill trees stay byte-identical
  Given the edited guides + report-template.md exist in canonical, dogfood, and bundle trees
  When the canonical edit is synced
  Then md5 of each edited file is equal across all three skill trees

Scenario: task 1's marker stays green
  Given test_report_arc asserts report-template.md's ARC block shape
  When report-template.md gains the reconcile rule and the guides gain cues
  Then test_report_arc stays green (the arc block shape is unchanged)

Scenario: reject — a gate-path guide is left unwired
  Given the arc must be traceable in every gate path
  When one of the seven guides has no arc cue
  Then test_arc_gate_wiring goes red -> "gate_unwired"
  And the missing guide is named so it can be wired

Scenario: reject — a guide re-spells the per-gate arc content
  Given progressive disclosure keeps the definition central
  When a guide inlines the goal·done·plan per-gate examples instead of pointing at report-template.md
  Then the human read refuses it -> "arc_duplicated"
  And report-template.md stays the single source of the per-gate examples

Scenario: reject — a cue changes a gate
  Given the wiring is presentation only (scope Out)
  When a cue or the reconcile edit adds an approval step or alters a PASS/HARD-STOP/freeze/lock semantic
  Then the human read refuses it -> "arc_changes_gate"
  And every gate's logic + outcomes stay exactly as before

Scenario: reject — banned wording enters the new prose
  Given all seven guides + report-template.md are on the 21-file lint surface
  When a new cue uses a banned idiom or an emphasis token
  Then test_wording_lint / test_ubiquitous_language go red -> "wording_regression"
  And the cue is reworded without weakening either lint
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

A skill-doc task: the "contract" is the frozen CUE format, the seven gate→file map, the
separable reconcile decision, the marker test, the three-tree sync, and the guard mapping. No API.

```
FROZEN CUE  (one line per guide, at its human-approval moment; points central, no re-spell)
  → e.g. "Present this via report-template.md — open with the ARC (goal · done · plan)."
  - placed at each guide's approval moment; the wording adapts, but the POINTER to
    report-template.md + the goal·done·plan naming are constant. It REFERENCES the central
    definition; it never re-lists the per-gate examples (those stay in report-template.md).

FROZEN GATE→FILE MAP  (all seven — the guard against wiring six and missing one)
  baseline-lock   = phases/0-setup.md    (the `add.py lock` baseline approval)
  contract-freeze = phases/3-contract.md (the one approval / the freeze)
  verify          = phases/6-verify.md   (the gate record: PASS / RISK-ACCEPTED / HARD-STOP)
  intake          = intake.md            (propose {bucket, rationale, command})
  scope           = scope.md             (propose the MILESTONE draft)
  milestone-close = loop.md              (the goal-gate / `milestone-done` close)
  graduation      = graduate.md          (propose the production roadmap)

RECONCILE RULE — SEPARABLE  (the freeze decision; recommended default = FOLD HERE)
  report-template.md's Hard rules gain: "a gate report's ⚠ FLAGS must reconcile with
  `report --decide`'s open-item COUNT before the ask — if prose and digest disagree the engine
  wins; fix the data, not the sentence." Central, one place; the verify cue may note it.
  => the human chooses FOLD-HERE or DEFER-to-a-task-4 at the freeze. The wiring's green bar
     (exit-criterion 2) does NOT depend on this — it is task-1 observe residue, tested separately.

SCOPE
  presentation only — no add.py change, no gate LOGIC, no frozen-contract edit; task 1's
  ARC block shape + the four per-gate examples stay exactly as frozen; test_report_arc stays green.

THREE-TREE SYNC TARGET  (edit canonical, then sync; all byte-identical)
  canonical (edit here):  add-method/skill/add/{0-setup,3-contract,6-verify}.md (phases/) +
                          {intake,scope,loop,graduate}.md  (+ report-template.md IF folded)
  dogfood (sync):         .claude/skills/add/{…}                           [test_tree_parity]
  bundle  (sync):         add-method/src/add_method/_bundled/skill/add/{…} [test_bundle_parity]

TEST  (skill guides agents LOAD get a marker test)
  NEW test_arc_gate_wiring.py asserts each of the seven gate-path FILES names the arc
  (report-template + the goal·done·plan / ARC naming) in its approval region. IF reconcile is
  folded: a SEPARATE case asserts report-template.md's Hard rules gained the reconcile rule —
  kept separate so the wiring can pass even if the rule is deferred. Red before edits, green after.

DO NOT TOUCH
  add.py / any gate LOGIC · the four per-gate examples' ownership (stays in report-template.md) ·
  the wording-lint rubric · task 1's frozen §3 + the ARC block shape · any skill file beyond the
  seven guides (+ report-template.md only for the reconcile rule, if folded).

GUARD MAPPING  (response per §1 Reject code)
  gate_unwired       -> test_arc_gate_wiring (asserts the cue in all 7 files)
  arc_duplicated     -> human read (progressive disclosure; central single-source)
  arc_changes_gate   -> human read (scope Out; gate logic untouched)
  wording_regression -> test_wording_lint / test_ubiquitous_language
```

Reconcile rule: FOLD HERE (human, 2026-06-09) — report-template.md's Hard rules gain it this task, separate test case.
Status: FROZEN @ v1 — approved by Tin Dang · date: 2026-06-09 (Fork A; reconcile folded here)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: a NEW marker test (`test_arc_gate_wiring`) red→green asserting the cue in all 7
gate-path FILES + tree/bundle parity + wording & ubiquitous lint green + `test_report_arc` still
green + the human read of the wired cues. (Skill guides agents LOAD get a marker test.)

Plan (each §2 scenario → its guard):
<test_plan>
  - every guide names the arc       -> test_arc_gate_wiring: each of the 7 files (0-setup · 3-contract · 6-verify · intake · scope · loop · graduate) names `report-template` AND the arc (ARC / goal·done·plan) — the all-7 guard against wiring six and missing one
  - cue points central, no re-spell  -> test_arc_gate_wiring: no guide contains the four per-gate example labels verbatim [+ human read for "points, not re-spells"]
  - reconcile rule folded (if FOLD)  -> test_arc_gate_wiring (SEPARATE case): report-template.md's Hard rules name the reconcile rule (`report --decide` count) — skipped/xfail if the human DEFERS at the freeze; the wiring bar never depends on it
  - three trees byte-identical       -> test_tree_parity (canon↔dogfood) + test_bundle_parity (canon↔bundle)
  - task 1 marker stays green        -> test_report_arc (the ARC block shape is untouched)
  - reject: gate_unwired             -> test_arc_gate_wiring (a missing file's cue fails, names the file)
  - reject: arc_duplicated           -> human read (progressive disclosure; central single-source)
  - reject: arc_changes_gate         -> human read (scope Out; add.py gate logic untouched)
  - reject: wording_regression       -> test_wording_lint / test_ubiquitous_language
</test_plan>

Red→green: `test_arc_gate_wiring` is RED now (no guide names the arc) for the right reason
(missing cues), GREEN after the 7 cue edits + the three-tree sync.

Tests live in: `add-method/tooling/test_arc_gate_wiring.py` `test_report_arc.py` `test_tree_parity.py` `test_bundle_parity.py` `test_wording_lint.py` `test_ubiquitous_language.py` · new marker test + existing guards.
MUST run red (missing implementation) before Build.
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

- [x] all tests pass — full suite 686 OK; `test_arc_gate_wiring` 4/4 (RED 2→GREEN 4, right reason: 7 guides unwired + reconcile rule absent)
- [x] coverage did not decrease — a NEW marker test ADDED (`test_arc_gate_wiring.py`, +4 cases, suite 682→686); no test removed or weakened; task 1's `test_report_arc` still green (ARC block shape untouched)
- [x] no test or contract was altered during build — only the 8 skill files edited (7 guides + report-template.md, the §3 sync target); §3 stays FROZEN @ v1; task 1's frozen §3 untouched
- [x] concurrency / timing — n/a: presentation-only skill docs, no runtime path, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose-only edits; zero new deps; lint surface green
- [x] layering & dependencies follow CONVENTIONS.md — canonical edited, then synced to dogfood + bundle byte-identical (md5 + test_tree_parity + test_bundle_parity, all 8 files)
- [ ] a person reviewed and approved the change — at this gate

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read all 8 edited files in full. Confirmed per gate: (1) **0-setup** §4 baseline-approval — cue opens the SETUP-REVIEW present with the ARC; (2) **3-contract** the-freeze — cue added to the "present the bundle lowest-confidence first" line; (3) **6-verify** gate-record — cue + a POINTER to the reconcile rule (tightened from a verbatim restatement to a pointer at report-template's rule, after an advisor-caught single-source duplication — the rule body lives only in report-template.md); (4) **intake** the-proposal — cue before "emit ONE of"; (5) **scope** confirm — cue at the rank-assumptions line; (6) **loop** Close step 6 — cue at the milestone-done close; (7) **graduate** step 4 human-confirm — cue at the roadmap present. Each cue POINTS at `report-template.md` and names goal·done·plan; NONE re-spells the four per-gate examples (arc_duplicated guard: no guide contains "report-arc tests"). The reconcile rule lives ONLY in report-template.md's Hard rules (central, not per-guide). No gate LOGIC / outcome semantic changed (arc_changes_gate: presentation only). SKILL.md's central pointer (task 1) unchanged. No banned idiom or emphasis token entered (test_wording_lint + test_ubiquitous_language green across the 21-file surface).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-09

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-guide cue drift — when report-template.md's ARC definition next changes, do the 7 guide cues stay pointers (not stale re-spells)? The marker test asserts presence, not freshness; a future edit could let a cue drift. Re-run test_arc_gate_wiring after any report-template.md ARC change.
Spec delta for the next loop: a SEPARABLE deliverable folded into a task needs its own test case isolated from the task's exit-criterion bar (done here: the reconcile-rule case is separate from the 7-gate wiring case, so a reconcile regression can't sink the wiring's green). arc-book-align (task 3) carries the same shape: the GLOSSARY term test must not gate on the book-prose read.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] when a rule is declared single-source (lives in one central file), pointing guides must POINT, not restate — a verbatim restatement is a silent single-source violation no presence-test catches, and it is exactly the failure a "traceable everywhere, defined once" design exists to prevent; a parity check or a "no-restate" lint would catch it mechanically (evidence: arc-gate-wiring verify — the reconcile rule was restated verbatim in both report-template.md AND 6-verify.md; advisor-caught, tightened to a pointer, but no test would have flagged the drift)
- [SDD · folded] the seven human gates this milestone enumerated may be incomplete: the retrospective consolidation (`fold.md` — the human consolidates open deltas into PROJECT.md, the "never self-approve a consolidation" boundary) is also a human-confirm moment not in the seven; it was out of v23's frozen scope but is a real gate the arc could serve (evidence: arc-gate-wiring froze {lock·freeze·verify·intake·scope·close·graduation}; fold.md's consolidation-confirm is an 8th human decision point the wiring did not touch)
- [ADD · folded] dogfooding the reconcile rule at the very gate that ships it caught the duplication — practicing "FLAGS must match the digest count" while presenting arc-gate-wiring's own verify gate is what made the single-source slip visible to review (evidence: arc-gate-wiring — reconciling my own gate report to digest=1 ran the new rule against itself the same session it was written)
