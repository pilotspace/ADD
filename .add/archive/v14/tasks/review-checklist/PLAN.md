# TASK: one-approval checklist surfaced at the freeze seam

slug: review-checklist · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the freeze seam presents a compact review checklist — the human's one
  minute, aimed — without re-adding GSD-style ceremony (v14 exit criterion 5);
  also redeems high-risk-signal's ⚠: "is this scope high-risk?" becomes an
  explicit prompt at the freeze, shrinking the undeclared-scope honest limit
Framings weighed: a six-line checklist INSIDE 3-contract.md at the seam where
  the approval already happens (chosen: aims the existing ONE approval; zero new
  artifacts, zero new gates — the anti-GSD constraint is structural) · a
  separate REVIEW.md per task (rejected: that IS the GSD ceremony this method
  exists to avoid) · an engine-rendered checklist in `guide` output (rejected:
  judgment prompts are prose, not state; the engine stays judgment-free)
Must:
  - phases/3-contract.md gains "## The freeze review checklist" directly after
    the one-approval paragraph: SIX items, each one line, in the human's lens —
    (1) ⚠ flags FIRST (accept each knowing its cost), (2) intent (§1 says what
    you actually want), (3) cases (every Must/Reject has an observable scenario
    you care about), (4) shape (glossary names · error codes · additive vs
    breaking), (5) RISK — "is this scope high-risk/method-defining? then require
    `risk: high · autonomy: conservative` in the header; the engine refuses an
    unguarded completion", (6) tests (red for the right reason, behavior not
    internals).
  - The checklist ends with the no-ceremony clause: it AIMS the one approval —
    never a second gate, no sign-off forms, no extra documents.
  - run.md's one-approval-front section points to the checklist by name (one
    sentence; the flow rubric and the seam guide stay accorded).
  - Both files synced ×3; no engine change (add.py byte-identical).
Reject:
  - any new approval step, file, or form -> rejected by design; the prose itself
    states the never-a-second-gate rule and the test pins section size
Assumptions — least-sure first:
  ⚠ [spec] six items is the right size — least sure because too few misses the
    risk prompt's value, too many re-creates checklist fatigue (the GSD failure
    mode); if wrong: prose-only change, one-line cost to tune later; the size
    guard (≤16 lines) keeps drift honest
  - [x] no engine change needed — confirmed: judgment prompts belong to prose;
    the engine's role (refusing the unguarded completion) already shipped in
    high-risk-signal

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the seam guide presents the checklist
  Given phases/3-contract.md
  When the AI (or any agent) reaches the freeze and reads the guide
  Then "The freeze review checklist" section exists with six one-line items
  And the first item directs the reader to the ⚠ least-sure flags

Scenario: the risk prompt is explicit
  Given the checklist
  When the human walks it
  Then one item asks "is this scope high-risk/method-defining?" and names the
       exact tokens `risk: high · autonomy: conservative`

Scenario: no ceremony is re-added
  Given the checklist section
  When its size and language are checked
  Then it stays within 16 lines, adds no second gate, and says so

Scenario: the flow rubric stays accorded
  Given run.md's one-approval-front section
  When it is read
  Then it points to the freeze review checklist by name

Scenario: three trees agree
  Given the canonical, dogfood, and bundled copies of both files
  Then they are byte-identical
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
phases/3-contract.md   (canonical add-method/skill/add/phases/, synced ×3)
  + "## The freeze review checklist" after the one-approval paragraph
    six items: ⚠-first · intent · cases · shape · RISK (names the tokens
    `risk: high · autonomy: conservative`) · tests
    closing clause: aims the ONE approval — never a second gate, no sign-off
    forms, no extra documents
  size bound: the new section ≤ 16 lines (the anti-ceremony pin)
run.md   (one-approval-front section, synced ×3)
  + one sentence pointing at "the freeze review checklist" in phases/3-contract.md
ENGINE UNTOUCHED: add.py byte-identical ×3 before and after.
GUARD: add-method/tooling/test_review_checklist.py — heading + ⚠-first + risk
tokens + size bound + run.md accord + ×3 parity for both files.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front via AskUserQuestion; ⚠ six-items-size flag surfaced and accepted)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must has a test; suite stays green elsewhere (no engine
change — add.py md5 pinned unchanged across the build).
Plan (one test per scenario, asserting behavior not internals):
  - test_seam_guide_presents_checklist: heading anchor + six "- **" items +
    the ⚠ item is FIRST (RED: section absent)
  - test_risk_prompt_names_the_tokens: contiguous `risk: high · autonomy:
    conservative` inside the checklist section (RED)
  - test_no_ceremony: section ≤ 16 lines AND contains the never-a-second-gate
    clause (RED)
  - test_run_md_accord: run.md names "the freeze review checklist" (RED)
  - test_three_trees_agree: byte parity ×3 for 3-contract.md and run.md
    (green-by-design after sync; red on divergence)
  - test_engine_untouched: add.py md5 equals the recorded pre-task hash
    ccb0aa1589c09d3238d7e7fbca1e0240 (guards scope creep into the engine)

Tests live in: `add-method/tooling/test_review_checklist.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): prose only — add.py stays byte-identical (pinned
by test); the checklist aims the existing approval and may not introduce any new
gate, file, or form.
Code lives in: `add-method/skill/add/phases/3-contract.md` · `add-method/skill/add/run.md` · synced ×3
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 426/426 OK (was 420; +6 in test_review_checklist.py)
- [x] coverage did not decrease — 4 red→green + 2 green-by-design guards;
      check 205/0 (4 pre-existing warnings)
- [x] no test or contract was altered during build — prose written to the §4
      anchors as frozen; §3 untouched
- [x] concurrency / timing of the risky operation is safe — static prose; no
      runtime path touched (engine md5 ccb0aa1589c09d3238d7e7fbca1e0240 asserted
      identical ×3 by test_engine_untouched)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose
      only; no new dependency; no command examples beyond the existing CLI
- [x] layering & dependencies follow CONVENTIONS.md — both files ×3; the
      checklist adds no gate/file/form (≤16-line anti-ceremony bound pinned)
- [x] outcome recorded — auto-resolved under autonomy: auto (evidence complete ·
      loops dry · no residue: prose-only, security clean, engine byte-identical)

### GATE RECORD
Outcome: PASS (auto-resolved on complete evidence)
Reviewed by: auto-gate under autonomy: auto — run: review-checklist build→verify,
  accountable owner this session · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether the human actually walks the six at
real freezes (the next few fronts this session are the live sample); whether item
5 produces risk declarations on scopes that warrant them (the high-risk-signal
honest limit shrinking in practice); checklist fatigue signals (humans skipping
to approve) — if seen, six was too many.
Spec delta for the next loop: v14 exit criterion 5 CLOSED; the freeze seam now
carries flags + checklist + engine-refused unguarded completions — the
one-approval front is fully furnished; release-1-1-0 ships it.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [UDD · folded] a review prompt belongs AT the seam where the decision already
    happens, sized to the reviewer's real attention (one minute, six lines,
    ⚠-first) — a separate review artifact is ceremony that competes with the
    decision instead of aiming it (evidence: checklist landed inside
    3-contract.md with a ≤16-line pin; zero new gates)
