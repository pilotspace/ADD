# TASK: The question is a summary, never the artifact

slug: question-summary-layer · created: 2026-06-07 · stage: mvp · risk: low · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- conservative: the edit is tiny but the surface is the method's own seam discipline
     (report-template.md) — human-led gate, consistent with the v17 prompt-surface tasks.
     Intake (confirmed 2026-06-07): bucket=task — frozen-scope test ran first and came back
     clean (report-template.md's constraints list is pinned by no frozen contract; created in
     standalone docs commit 103a43b). Rule shape ruled BOTH: positional + compositional. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: question-summary-layer — extend the summary-first discipline from the chat
message to the approval-question component itself: **the question is a summary, never
the artifact**. (Origin: the clarity-greenstate freeze ask crammed the whole bundle
into one dense question paragraph; the chat report obeyed the template, the question
text did not.)

Framings weighed: one-constraint-in-the-template (chosen) · sprinkle-at-seams
(rejected — duplicates the template's purpose; the seam guides already point at it;
lean-foundation drift) · engine-rendered question digest (rejected — over-engineering;
this is chat-layer discipline, no add.py change).

Must:
  - report-template.md gains ONE new constraint mandating BOTH layers at every
    human-approval question (human ruling 2026-06-07):
      · positional — a compact summary block (SUMMARY · DECISION · ⚠ FLAGS, the first
        three blocks) sits in chat immediately before the ask, adjacent to it, so the
        decision context survives a long scroll;
      · compositional — the question text itself is a short summary, two lines at
        most: intent + what "yes" means (+ the flag count), pointing at the report
        above; the full bundle/diff/artifact lives only in the chat report.
  - the five-blocks section gets a short "the ask itself" tie-in (≤3 lines) linking
    the new constraint to block 2 (DECISION) — the ask comes AFTER show-before-ask.
  - SKILL.md's existing template-anchor line carries the rule's name (≤1 line growth).
  - wording obeys the frozen v17 rubric (wording-lint green); the rule's own negative
    ("never the artifact") stays — the negative IS the obligation (positivization
    boundary, foundation-version 16).
  - additive only: no existing constraint bullet's text changes; semantic inventory green.
  - 3-mirror parity: canonical → bundled → .claude synced byte-identical.
Reject:
  - the rule restated in any phase guide / seam file beyond report-template.md +
    the one SKILL.md anchor -> "rule_sprinkled"
  - any existing constraint weakened, reworded, or removed while adding -> "guard_weakened"
  - an edit that trips wording-lint or the semantic inventory -> "semantics_changed"
  - canonical and mirror copies diverging -> "mirror_drift"
After:
  - every future seam ask inherits the two-layer rule from the one home; the skill
    surface carries it; suite + wording-lint + semantic-inventory + parity all green.
Assumptions — least-sure first:
  ⚠ the two-line bound on question text fits multi-question asks (a close seam can
    carry gate+fold+push in one call) — least sure because compression there is
    real; if wrong: askers squeeze to the point of ambiguity. Mitigated: the bound
    is per-question, and detail is one glance up by construction.
  ⚠ "compact block" = the first three template blocks (SUMMARY/DECISION/⚠ FLAGS),
    not all five — least sure because the "Both" ruling named no block depth; if
    wrong: the layer is either a duplicated full report (too heavy) or a bare
    headline (too thin).
  - [x] the rule belongs in the existing `<constraints>` list, not a new section —
    matches the file's structure.
  - [x] no engine (add.py) change — chat-layer discipline only.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the rule names both layers (the dense-question fix)
  Given report-template.md after the edit
  When you read its <constraints> list
  Then one new bullet mandates the positional layer (compact SUMMARY · DECISION ·
       ⚠ FLAGS block in chat immediately before the ask) AND the compositional
       layer (question text = a summary of two lines at most: intent + what "yes"
       means + flag count, pointing at the report above)
  And the five-blocks section carries the ≤3-line "the ask itself" tie-in at
       block 2, and SKILL.md's anchor line names the rule

Scenario: one home only (rejection: rule_sprinkled)
  Given the skill surface after the edit
  When you search every file under skill/add/ for the rule's needle phrase
  Then it matches in report-template.md and SKILL.md only
  And every phase guide / seam file (3-contract, 6-verify, fold, intake,
       setup-review, run, scope, streams, deltas) is byte-unchanged

Scenario: additive only (rejections: guard_weakened · semantics_changed)
  Given the pre-edit file with its 5 existing constraint bullets
  When the new bullet lands
  Then all 5 existing bullets are present verbatim (none reworded, none removed)
  And wording-lint and the semantic-inventory gate both stay green

Scenario: three mirrors agree (rejection: mirror_drift)
  Given the canonical edit is complete
  When prepare_bundle.py syncs the bundle and .claude/skills/add is copied
  Then the two touched files are byte-identical across all three trees
  And the whole suite stays green
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
EDIT add-method/skill/add/report-template.md       (canonical · 2 hunks · additive)
  hunk A -> <constraints> list: APPEND the frozen bullet below; the 5 existing
            bullets stay verbatim
  hunk B -> after the five numbered blocks: "The ask itself" tie-in, 3 lines max
EDIT add-method/skill/add/SKILL.md                  (1 hunk · additive)
  the existing template-anchor line gains the clause
  "the question is a summary, never the artifact" · 1 line growth max
SYNC  src/add_method/_bundled/skill/add/ + .claude/skills/add/   (mirrors, byte-equal)
  reject -> { error: "rule_sprinkled" | "guard_weakened" | "semantics_changed"
              | "mirror_drift" }
Schema: none — prose-only; no add.py, no state.json, no engine behavior change
```

Frozen rule text (hunk A, verbatim):

> - **The question is a summary, never the artifact.** Every approval ask carries
>   two layers: a compact SUMMARY · DECISION · ⚠ FLAGS block sits in chat
>   immediately before the ask (positional), and the question text itself is a
>   summary of two lines at most — intent + what "yes" means + the flag count —
>   pointing at the report above (compositional). The full bundle, diff, or
>   artifact lives only in the chat report; a question that re-carries it buries
>   the decision.

Frozen tie-in text (hunk B, verbatim):

> **The ask itself** — when block 2's decision becomes a literal question
> component (option picker, numbered menu), compose it as a summary: the detail
> stays in the report above, the question carries intent + what "yes" means +
> the flag count.

Status: FROZEN @ v1 — approved by Tin Dang · date: 2026-06-07   <!-- the one approval over §1–§4; both ⚠ flags surfaced at the seam (two-line bound · 3-block depth) and accepted as frozen. Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every frozen hunk pinned by ≥1 needle (guard-dense, foundation-v16);
4 RED tests + 1 disclosed GREEN guard.
Plan (one test per scenario, asserting behavior not internals):
  - test_rule_bullet_present      (scenario 1, RED): report-template.md carries the frozen
    bullet's needles — rule name · "immediately before the ask" · "two lines at most" ·
    "the flag count"
  - test_ask_itself_tie_in        (scenario 1, RED): the "**The ask itself**" tie-in exists
  - test_skill_anchor_names_rule  (scenario 1, RED): SKILL.md anchor line names the rule
  - test_one_home_only            (scenario 2, RED): "question is a summary" appears in
    EXACTLY {report-template.md, SKILL.md} across skill/add/**/*.md — red now (0 homes),
    green only at exactly 2; guards rule_sprinkled permanently
  - test_existing_constraints_verbatim (scenario 3, GREEN guard — disclosed): the 5
    existing constraint bullets stay byte-present (guards guard_weakened; green at birth
    by design, like the v17 pinned-safety guards)
  - scenario 3 lint/inventory + scenario 4 parity: owned by the STANDING fences
    (`wording_lint` · semantic-inventory · the skill/add tree-parity guard) — declared
    here, never duplicated (clarity-greenstate convention, foundation-v16).

Tests live in: `add-method/tooling/` test_question_summary_layer.py · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): additive-only — the frozen hunks land character-exact
  from §3; the 5 existing constraint bullets stay verbatim (the green guard pins them).
Code lives in: add-method/skill/add/report-template.md + SKILL.md (canonical) ·
  mirrors via scripts/prepare_bundle.py + cp to .claude/skills/add/
Constraints: do NOT change any test or the contract; only the 3 contracted hunks +
  mirror sync move; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — whole suite **522 OK** (517 + the 5 new); new suite went
      4 RED → 5 green at the build, red was for the right reason (needles absent)
- [x] coverage did not decrease — suite grew by 5; standing fences untouched
- [x] no test or contract was altered during build — test_question_summary_layer.py
      byte-unchanged since the front commit; §3 hunks landed character-exact
- [x] concurrency / timing of the risky operation is safe — N/A: prose-only edit,
      no runtime path; legitimate no-op recorded (foundation-v16 convention)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose
      only; wording-lint 0 · audit clean (43) · zero new imports/packages
- [x] layering & dependencies follow CONVENTIONS.md — one-home rule (the template
      owns seam discipline; SKILL.md anchors it); 3-way mirror parity byte-identical
- [x] a person reviewed and approved the change — this gate, ruled by Tin Dang
      2026-06-07: "PASS, but rewrap hunk B"

⚠ ONE DEVIATION ruled at the gate: hunk B's frozen VERBATIM text wrapped to
4 physical lines; the contract's shape line estimated "tie-in, 3 lines max".
RESOLVED at the gate (2026-06-07): the human ratified an isolated pre-gate
rewrap to 3 lines — character stream identical modulo newlines, zero word
changes; gates re-run green after it (suite 522 OK · wording-lint 0 · mirrors
re-synced). The §3 frozen quote stays the at-freeze record; this ratification
is the governing note.

### GATE RECORD
Outcome: PASS — contingent on the gate-ratified rewrap (landed as its own
isolated commit before this stamp). Push HELD per the same ruling ("Hold — no
push"); the human says when.
Reviewed by: Tin Dang · date: 2026-06-07

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the one-home fence (test_one_home_only) is the
standing monitor for rule_sprinkled; the green guard watches guard_weakened; future
seam asks in live sessions are the behavioral signal (does the two-layer shape hold
at multi-question seams? — §1's top ⚠ assumption stays the thing to watch).
Spec delta for the next loop: none structural — the rule is one bullet in one home;
if the two-line bound chafes at multi-question seams, that returns as a change-request
against this contract, never an in-place rewording.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [SDD · folded] a numeric figure on a contract SHAPE line ("3 lines max") reads as a
  bound even when verbatim-quoted text is the authority — mark shape-line figures ≈
  or omit them where the verbatim quote governs (evidence: hunk B's 4-vs-3 wrap was
  the gate's only deviation, ruled via a ratified rewrap)
- [ADD · folded] dogfooding a seam-discipline rule at its own approval seams is cheap
  live validation — the rule's freeze and gate asks already ran in the two-layer
  shape before the rule landed (evidence: this task's freeze + gate AskUserQuestion
  seams, 2026-06-07)
