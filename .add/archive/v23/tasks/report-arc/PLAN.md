# TASK: Enrich report-template.md with the goal→achievement→plan decision arc

slug: report-arc · created: 2026-06-09 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a new **ARC block** atop `report-template.md`'s 5-block decision report — three labelled lines (goal · achievement · plan) every human gate carries, so the human sees the work's arc before confirming, not a local snapshot.
Framings weighed: new-ARC-block-on-top (chosen, user-confirmed) · enrich-existing-blocks (goal→SUMMARY, achievement→EVIDENCE, plan→NEXT) · one-line-arc-banner
Must:
<must>
  - `report-template.md` gains an ARC block rendered ABOVE SUMMARY, with three labelled lines: goal (the milestone/project goal this decision serves) · achievement (proven progress — tasks done, exit-criteria met, what THIS gate proves) · plan (this gate → next → goal).
  - The ARC block is required at EVERY human gate: baseline-lock · contract-freeze · verify · intake · scope · milestone-close · graduation.
  - One shared arc spec + per-gate examples: the arc ADAPTS its content per gate (verify achievement = tests + evidence; close = exit-criteria met; intake = the request sized) but keeps the three-line goal·achievement·plan shape constant.
  - Arc facts are engine-sourced (goal = m-goal · achievement = exit-criteria met/total + tasks done · plan = DECIDE NEXT), never re-typed from memory — the EVIDENCE "engine wins" rule extends to the ARC.
  - The arc is PRESENTATION only: it adds no gate and changes no PASS / RISK-ACCEPTED / HARD-STOP / freeze semantic.
  - SKILL.md's `report-template.md` pointer names the ARC block so agents render it at every decision point.
</must>
Reject:
<reject>
  - the ARC block omits any of the three parts (goal / achievement / plan) -> "arc_incomplete"   (human read at gate; the three-line shape is the contract)
  - an arc fact is re-typed from memory or disagrees with `add.py` output -> "arc_unsourced"   (human read; engine-wins rule)
  - the arc introduces a new gate or changes an outcome semantic -> "arc_changes_gate"   (human read; scope Out)
  - banned slang or an emphasis token enters the new prose -> "wording_regression"   (test_wording_lint / test_ubiquitous_language go red — report-template.md is on the 21-file lint surface)
</reject>
After:
<after>
  - `report-template.md` defines the ARC block + the per-gate adaptation; every human gate can carry goal·achievement·plan, engine-sourced; the wording-lint + ubiquitous-language surface stays green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  - resolved-by-design at §3 + confirmed at this verify gate: the arc composes from EXISTING `add.py` output (sourcing frozen TEMPLATE-COMPOSED — no engine change; `arc-evidence` did not materialise; m-goal · exit-criteria/tasks · DECIDE NEXT all present). Forward watch (not closeable by task 1 alone, milestone-spanning): the same composability across the OTHER gate types (intake · scope · milestone-close · graduation · baseline-lock) is tasks 2-3's to prove — monitored in §7.
  - [x] one shared arc spec + per-gate examples is enough (vs distinct per-gate variants) — confirmed at §3 freeze: one shape, four worked per-gate examples; the human read at this gate is the quality check the §4 test plan reserved.
  - [x] `report-template.md` is on the wording-lint + ubiquitous-language surface (21 files) — new prose must avoid banned terms / emphasis tokens — verified via wording_lint.surface_files().
  - [x] the arc facts exist in `add.py` output today (m-goal in status · exit-criteria met/total + tasks done in the rollup · DECIDE NEXT) — verified this session.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: report-template defines the ARC block above SUMMARY
  Given report-template.md before this task has only the 5 blocks
  When the template is edited
  Then it defines an ARC block, rendered above SUMMARY, with three labelled lines: goal, achievement, plan
  And the original five blocks (SUMMARY · DECISION · ⚠ FLAGS · EVIDENCE · NEXT) remain present and in order

Scenario: the ARC applies at every human gate
  Given ADD has seven human gates (lock · contract-freeze · verify · intake · scope · milestone-close · graduation)
  When the template describes when to render the ARC
  Then it states the ARC is required at every one of those gates

Scenario: one shared shape, per-gate content
  Given the arc content differs by gate (verify=tests+evidence, close=criteria met, intake=request sized)
  When the template specifies the arc
  Then the three-line goal·achievement·plan SHAPE is constant across gates
  And the template shows at least one per-gate example of the adapted content

Scenario: arc facts are engine-sourced
  Given the EVIDENCE rule says engine facts are never re-typed from memory
  When the template specifies where each arc line's facts come from
  Then goal maps to m-goal, achievement to exit-criteria met/total + tasks done, and plan to DECIDE NEXT — all from add.py output

Scenario: the SKILL pointer names the ARC block
  Given SKILL.md points agents at report-template.md for decision points
  When SKILL.md is edited
  Then that pointer names the ARC block so an agent renders it at every gate

Scenario: the three skill trees stay byte-identical
  Given report-template.md + SKILL.md exist in .claude/skills/add, add-method/skill/add, and the bundle
  When the canonical edit is synced
  Then md5 of each edited file is equal across all three skill trees

Scenario: reject — the ARC omits a part
  Given the arc's contract is the three lines goal · achievement · plan
  When an ARC block is written with only goal and plan (achievement missing)
  Then the human read at the gate refuses it -> "arc_incomplete"
  And the three-line contract in report-template.md stays the single definition of the shape

Scenario: reject — an arc fact is unsourced
  Given the engine-wins rule extends to the ARC
  When an arc line states an achievement figure re-typed from memory that disagrees with add.py output
  Then the human read refuses it -> "arc_unsourced"
  And report-template.md's "engine-sourced only" rule stays unchanged

Scenario: reject — the arc changes a gate
  Given the arc is presentation only (scope Out)
  When an edit makes the ARC add a new approval step or alter a PASS/HARD-STOP/freeze semantic
  Then the human read refuses it -> "arc_changes_gate"
  And the gate logic + outcomes stay exactly as before

Scenario: reject — banned wording enters the new prose
  Given report-template.md is on the 21-file wording-lint + ubiquitous-language surface
  When the new ARC prose uses a banned idiom or an emphasis token
  Then test_wording_lint / test_ubiquitous_language go red -> "wording_regression"
  And the new prose is reworded without weakening either lint
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

A skill-doc task: the "contract" is the frozen ARC block FORMAT, the sourcing decision, the
three-tree sync, the marker test, and the guard mapping (one response per §1 Reject). No API.

```
FROZEN ARC BLOCK  (rendered as the FIRST block, above SUMMARY; labels verbatim per the chosen preview)
  ARC  goal: <the milestone/project goal this decision serves — from m-goal>
       done: <proven progress — tasks done · exit-criteria met · what THIS gate proves>
       plan: <this gate → the next step → the goal>
  - three labelled lines, in order: `goal:` · `done:` (≡ achievement) · `plan:`
  - then a separator, then the unchanged five blocks (SUMMARY · DECISION · ⚠ FLAGS · EVIDENCE · NEXT)

FROZEN RULES
  - required at all SEVEN human gates: baseline-lock · contract-freeze · verify · intake · scope ·
    milestone-close · graduation
  - one shared shape, per-gate content: the three labels are constant; the content adapts; the
    template carries ≥1 worked per-gate example
  - SOURCING = TEMPLATE-COMPOSED (freeze-first resolved): the arc is composed by the agent from
    EXISTING add.py output — goal=m-goal (status) · done=exit-criteria met/total + tasks done
    (rollup) · plan=DECIDE NEXT. "what this gate proves" is composed from the gate's own evidence,
    NOT a new engine fact. => NO add.py change; the milestone's possible `arc-evidence` task does
    NOT materialise.
  - presentation only: adds no gate, changes no PASS / RISK-ACCEPTED / HARD-STOP / freeze semantic
  - SKILL.md's report-template pointer names the ARC block

THREE-TREE SYNC TARGET  (edit canonical, then sync; all byte-identical)
  canonical (edit here):  add-method/skill/add/{report-template.md, SKILL.md}
  dogfood (sync):         .claude/skills/add/{…}            [guarded: test_tree_parity]
  bundle  (sync):         add-method/src/add_method/_bundled/skill/add/{…}   [guarded: test_bundle_parity]

TEST (skill guides agents LOAD get a marker test — unlike book edits)
  NEW test_report_arc.py asserts report-template.md: defines the ARC block with the three labels
  goal/done/plan above SUMMARY · states the all-seven-gates rule · maps each line to its add.py
  source · and SKILL.md's pointer names ARC. Red before the edit, green after.

DO NOT TOUCH
  - add.py / any gate LOGIC (presentation-only) · the five existing blocks' meaning (only ADD the
    ARC above them) · the wording-lint rubric · any skill file other than report-template.md + SKILL.md

GUARD MAPPING  (response per §1 Reject code)
  arc_incomplete     -> test_report_arc (asserts all three labels) + human read
  arc_unsourced      -> human read (engine-wins rule; no mechanical guard)
  arc_changes_gate   -> human read (scope Out; gate logic untouched)
  wording_regression -> test_wording_lint / test_ubiquitous_language
```

Status: FROZEN @ v1 — approved by Tin Dang · date: 2026-06-09
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: a NEW marker test (`test_report_arc`) red→green + tree/bundle parity + wording &
ubiquitous-language lint green + the human read of the rendered ARC spec. (Skill guides agents LOAD
get a marker test — unlike book edits, which rest on parity + read alone.)

Plan (each §2 scenario → its guard):
<test_plan>
  - ARC defined above SUMMARY      -> test_report_arc: report-template.md has an "ARC" block with labels goal:/done:/plan: appearing before the SUMMARY block; the 5 blocks still present
  - ARC at every gate              -> test_report_arc: the template names all seven gates as requiring the ARC
  - one shape, per-gate content    -> test_report_arc: ≥1 per-gate example present [+ human read for quality]
  - arc facts engine-sourced       -> test_report_arc: the source mapping names m-goal · exit-criteria/tasks · DECIDE NEXT
  - SKILL pointer names ARC        -> test_report_arc: SKILL.md's report-template pointer mentions the ARC block
  - three trees byte-identical     -> test_tree_parity (canon↔dogfood) + test_bundle_parity (canon↔bundle)
  - reject: arc_incomplete         -> test_report_arc (all three labels required) + human read
  - reject: arc_unsourced          -> human read (engine-wins; no mechanical guard)
  - reject: arc_changes_gate       -> human read (scope Out; add.py gate logic untouched)
  - reject: wording_regression     -> test_wording_lint / test_ubiquitous_language
</test_plan>

Red→green: `test_report_arc` is RED now (no ARC block in report-template.md) for the right reason
(missing implementation), and GREEN after the build edits + the three-tree sync.

Tests live in: `add-method/tooling/test_report_arc.py` `test_tree_parity.py` `test_bundle_parity.py` `test_wording_lint.py` `test_ubiquitous_language.py` · new marker test + existing guards.
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

- [x] all tests pass — full suite 682 OK; `test_report_arc` 6/6 (RED 6→GREEN 6, the right reason: no ARC block before the edit)
- [x] coverage did not decrease — a NEW marker test was ADDED (`test_report_arc.py`, +6 cases); no test removed or weakened
- [x] no test or contract was altered during build — only `report-template.md` + `SKILL.md` edited (the §3 sync target); §3 stays FROZEN @ v1
- [x] concurrency / timing — n/a: presentation-only skill doc, no runtime path, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose-only edit; zero new deps; wording-lint surface stays green
- [x] layering & dependencies follow CONVENTIONS.md — canonical edited, then synced to dogfood + bundle byte-identical (md5 + test_tree_parity + test_bundle_parity)
- [ ] a person reviewed and approved the change — at this gate

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read `report-template.md` + `SKILL.md` in full. Confirmed: the ARC block renders FIRST above SUMMARY with the three labels in order (`goal:`·`done:`·`plan:`); the seven gates are named (baseline-lock · contract-freeze · verify · intake · scope · milestone-close · graduation); the engine-source mapping is explicit (goal=`m-goal` · done=exit-criteria met/total + tasks done · plan=`DECIDE NEXT`, engine-wins); four worked per-gate examples carry the constant shape; the "presentation only — adds no gate, changes no PASS/RISK-ACCEPTED/HARD-STOP/freeze" line holds the scope-Out boundary (arc_changes_gate); the five blocks remain unchanged below; SKILL.md's pointer now names the ARC. No banned idiom or emphasis token entered (test_wording_lint + test_ubiquitous_language green).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-09

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): cross-gate-type arc composability — does the goal·done·plan shape compose cleanly from `add.py` output at intake · scope · milestone-close · graduation · baseline-lock (not just verify)? If any gate type needs a fact the rollup does not bundle, the deferred `arc-evidence` task materialises. Proven for verify here; tasks 2-3 (`arc-gate-wiring`) exercise the rest.
Spec delta for the next loop: the arc's "engine wins" rule has a sharper edge than the contract stated — a gate report must reconcile its ⚠ FLAGS with the engine's open-item COUNT (`report --decide`), not just per-fact figures. `arc-gate-wiring` should make every wired gate path render the arc AND check the digest count agrees before the ask.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a gate report's ⚠ FLAGS must reconcile with the engine digest's open-item count before stamping — prose claiming "resolved" while `report --decide` still counts the item is the un-transparent gate the arc exists to kill; fix the data (TASK.md markers), never the sentence (evidence: report-arc verify — digest showed NEEDS YOUR JUDGMENT (3) while the report prose claimed 2 of them resolved; reconciling the §1 markers brought the digest to (1), advisor-caught)
- [SDD · folded] an assumption resolved-by-DESIGN yet milestone-spanning needs a state beyond `[x]`/`[ ]`/⚠ — a resolved-with-forward-watch bullet plus a §7 monitor — so it neither overclaims (checked-off) nor underclaims (a bare open flag) (evidence: report-arc §1 composability assumption — resolved at §3 for the verify gate, but intake/scope/close/graduation/lock remain tasks 2-3's, now tracked as a §7 watch)
- [ADD · folded] dogfooding a new presentation contract at its own gate is a fast correctness check — rendering the ARC for report-arc's own verify gate surfaced the digest-vs-prose gap because the `done:` line demands proven facts, not a hope (evidence: report-arc — the first live ARC render is what exposed the (3)-vs-2 mismatch)
