# TASK: SETUP-REVIEW.md template + least-sure-first rules

slug: setup-review-artifact · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- high-risk: method/trust-layer scope; `auto` refused (unguarded_high_risk_auto). Front seam released by the human for the v12 tail — I self-freeze §3 and STOP at verify. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a new skill guide `skill/add/setup-review.md` that defines (a) the SETUP-REVIEW.md
template — the artifact the AI writes at `.add/SETUP-REVIEW.md` listing every decision it drafted
during autonomous setup — and (b) the least-sure-first presentation rules. SETUP-REVIEW.md is the
human's read-surface for the single lock-down (`add.py lock`, task 1): it puts the riskiest drafts
(the `guessed` ones) at the top so the one signature is informed, not a rubber stamp.

Framings weighed: skill-guide-prose (chosen) · engine-scaffolded-survivor · engine-generates-review
  - chosen: a PROSE guide defines the template + ordering rule; the AI writes `.add/SETUP-REVIEW.md`
    per project during the setup flow (task 4 wires entry). The engine is untouched — `add.py lock`
    stays judgment-free (it never parses the review; the human READING it is the gate, per task 1).
  - engine-scaffolded-survivor (rejected): have `cmd_init` scaffold an empty SETUP-REVIEW.md like the
    other survivors. Rejected: it is a per-onboarding GENERATED artifact (not a static foundation file);
    an empty skeleton the AI immediately overwrites is redundant, and it couples init to a review concept
    that belongs to the setup FLOW (task 4), not init mechanics.
  - engine-generates-review (rejected): `add.py` reads the drafts and emits SETUP-REVIEW.md — injects
    judgment into the engine; ADD keeps `add.py` judgment-free, the human signature is the gate.

Must:
  - A new canonical guide `skill/add/setup-review.md` defines the SETUP-REVIEW.md TEMPLATE: a header
    (project · stage · brownfield|greenfield · drafted-by model + date) + a decision table with columns
    {Decision · Lands in (PROJECT.md|scope|first-contract) · Tag (`guessed`|`evidence-grounded`) · Why/Evidence}.
  - The guide states the ORDERING RULE: rows least-sure-first — `guessed` decisions float to the top
    (lowest confidence first); `evidence-grounded` rows (cite the source file) sink below. The riskiest
    drafts meet the human's eye first.
  - The guide ties the artifact to the gate: SETUP-REVIEW.md is read-only context for the human's
    `add.py lock` sign; the engine never parses it (judgment-free, task 1) — reading it IS the review.
  - The guide states the write rule: the AI writes ONE artifact at `.add/SETUP-REVIEW.md`; never clobber
    a human-edited one (mirrors init's non-clobber survivor rule).
  - `setup-review.md` is byte-identical across the canonical + dogfood skill trees (+ the bundle).

Reject:
  - none material — this is PROSE (a guide + a template shape); it cannot fail at runtime. The single
    biggest risk is the guide drifting from the engine it references (e.g. naming a `lock` behavior task 1
    does not have). Mitigated by grounding every engine reference in task 1's frozen `lock` contract
    (signature-is-the-gate, no content checks) — checked at verify. Flagged ⚠ below.

After:
  - `skill/add/setup-review.md` ships in all three skill trees (byte-identical); the autonomous-setup flow
    (task 4) can route to it; the template + least-sure-first rule are defined for the AI to follow.

Assumptions — least-sure first:
  ⚠ [contract] SETUP-REVIEW.md is a PROSE artifact defined by a skill guide, NOT a scaffolded survivor or
    an engine-generated file. Least sure because the milestone calls it a "template shape" risky-contract
    (could read as an engine artifact). Chose prose to keep `add.py` judgment-free (task 1's invariant).
    If wrong (you want init to scaffold it / lock to require it), that re-opens the judgment-free boundary —
    cost: a code re-cut + couples init/lock to the review. Surfaced at the verify gate.
  - [ ] the artifact lives at `.add/SETUP-REVIEW.md` (alongside PROJECT.md) — confirm vs a tasks/ or
    milestones/ location. Chose `.add/` root: it is a setup-altitude, per-onboarding artifact.
  - [ ] ordering key is confidence-ascending with `guessed` above `evidence-grounded` on ties — confirm
    vs a flat guessed-section-then-evidence-section. Chose a single ranked table (one scan, no section hop).

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: setup-review.md ships byte-identical in every skill tree
  Given the repo
  Then skill/add/setup-review.md == .claude/skills/add/setup-review.md == _bundled/skill/add/setup-review.md
  (asserted by the existing tree-parity + bundle-parity guards — adding the guide to canonical alone
   turns them RED with an orphan; syncing turns them GREEN. This is the red→green for a prose guide.)

Scenario: the guide defines the template (human-read, prose)
  Given skill/add/setup-review.md
  Then it specifies the header + the decision table columns {Decision, Lands in, Tag, Why/Evidence}
  And it names the `guessed` | `evidence-grounded` tag vocabulary (matching adopt.md + the milestone)

Scenario: the guide states the least-sure-first ordering (human-read, prose)
  Given skill/add/setup-review.md
  Then it states rows are ordered least-sure-first, `guessed` above `evidence-grounded`
  And it ties SETUP-REVIEW.md to `add.py lock` as read-only context (engine never parses it)

Scenario: the guide does NOT contradict task 1's lock contract (cross-task consistency, human-read)
  Given the frozen `lock` contract (signature is the gate; no content checks)
  Then setup-review.md describes lock as the human sign, NOT as a step that reads/validates the review
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable (the parity one by test, the prose ones by human read). -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# skill guide (PROSE — gated by parity + human read, NO new unit test; TDD binds only where there is code.
#   Red→green IS the parity guard: orphan in canonical -> test_tree_parity/_bundle_parity RED -> sync -> GREEN.)
skill/add/setup-review.md  — the SETUP-REVIEW.md template + least-sure-first rules:

  TEMPLATE (the artifact the AI writes at .add/SETUP-REVIEW.md):
    # SETUP REVIEW — <project>
    <stage> · <brownfield|greenfield> · drafted by <model> @ <date>
    | # | Decision | Lands in | Tag | Why / Evidence |
    |---|----------|----------|-----|----------------|
    (rows ordered least-sure-first: `guessed` at top, `evidence-grounded` below)
    Sign: reviewed the above -> `add.py lock --by "<name>"`

  RULES (prose the AI follows):
    - order rows by confidence ASCENDING; `guessed` floats above `evidence-grounded` on ties
    - every row tagged `guessed` (state the inference + why) | `evidence-grounded` (cite the source file)
    - brownfield -> most rows evidence-grounded (read from code); thin-greenfield -> rows flagged guessed
    - SETUP-REVIEW.md is READ-ONLY context for the human's `add.py lock`; the engine never parses it
      (judgment-free, task 1) — the human reading it IS the review
    - write ONE artifact at .add/SETUP-REVIEW.md; NEVER clobber a human-edited one

  Synced: .claude/skills/add/setup-review.md + src/add_method/_bundled/skill/add/setup-review.md (byte-identical)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- self-frozen 2026-06-04: the human released the front seam for the v12 tail; the least-sure flag is carried to the verify gate instead. -->
<!-- Least-sure flag for the gate: SETUP-REVIEW.md is PROSE (a skill-guide template), not a scaffolded
     survivor or an engine-generated file — chosen to keep `add.py` judgment-free per task 1. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY (guessed|evidence-grounded) + least-sure flag surfaced. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: prose guide — NO new unit test (TDD binds where there is code). The red→green safety net
is the EXISTING parity pair: `test_tree_parity` (canonical ↔ dogfood file-set + md5) and `test_bundle_parity`
(canonical ↔ bundle). Adding `setup-review.md` to canonical ALONE turns both RED (orphan file in canonical);
syncing to the dogfood + bundle trees turns them GREEN. That orphan→sync is the documented red→green cycle.
No new test file is created (asserting prose content would be the over-testing the method warns against).

Tests live in: (existing) `add-method/tooling/test_tree_parity.py` + `test_bundle_parity.py` · MUST be RED
(orphan in canonical) before the sync, GREEN after.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason (orphan); target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): this is PROSE; no code, no new imports, no engine change. The guide must not
describe any `add.py lock` behavior beyond task 1's frozen contract (signature-is-the-gate, no content checks).
Code lives in: `add-method/skill/add/setup-review.md` (canonical) → synced to `.claude/skills/add/setup-review.md`
+ `src/add_method/_bundled/skill/add/setup-review.md`.
Constraints: stdlib n/a (no code); do NOT touch the engine or any test; keep all three trees byte-identical.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `Ran 318 tests … OK`; `test_tree_parity` + `test_bundle_parity` confirm
      setup-review.md ships byte-identical in all three trees (the orphan→sync red→green completed: both were
      RED with `only in canonical: ['setup-review.md']` before the sync, GREEN after).
- [x] coverage did not decrease — prose guide; the parity pair gained a new guarded file (file-set widened by one).
- [x] no test or contract was altered during build — §3 frozen; NO existing test modified; NO engine change
      (zero edits to add.py — confirmed by add.py 3-tree md5 unchanged at `7174a4cf…` from task 2).
- [x] concurrency / timing safe — n/a (no code; a static markdown guide; no state writes).
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no imports, no eval, no secrets.
- [x] layering & dependencies follow CONVENTIONS.md — setup-review.md 3-tree md5 parity `bb847472…`; cross-task
      consistency verified: the guide describes `lock` only as the human sign (matches task 1's signature-is-the-gate,
      no content checks) and reuses the `guessed`/`evidence-grounded` tag vocab from adopt.md + the v12 milestone.
- [x] a person reviewed and approved the change   <!-- autonomy: conservative — Tin reviewed at the verify gate;
      the prose-not-engine flag (+ `.add/SETUP-REVIEW.md` location, single-ranked-table) accepted, PASS approved. -->

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-04
Note: prose skill guide `setup-review.md`; red→green via the parity pair (orphan→sync); 318 tests green;
      3-tree md5 `bb847472…`; zero engine change. No security finding. Least-sure flag (SETUP-REVIEW.md is
      prose, not engine-scaffolded — keeps `add.py` judgment-free) accepted by design.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): on real onboardings, does the human's lock land AFTER reading
SETUP-REVIEW.md? are `guessed` rows the ones edited/corrected most (the ranking earning its place)?
Spec delta for the next loop: <what dogfooding the review artifact taught>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [ADD · open] the least-sure-first ranking changed which drafts the human checked (evidence: …) -->
