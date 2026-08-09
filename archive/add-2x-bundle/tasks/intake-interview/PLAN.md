# TASK: Interview before you size — proactive intent clarification at intake

slug: intake-interview · created: 2026-06-07 · stage: mvp · risk: low · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- conservative: the edit is tiny but the surface is the method's own intake discipline
     (intake.md) — human-led gate, consistent with question-summary-layer.
     Intake (confirmed 2026-06-07 via AskUserQuestion): bucket=task, standalone — frozen-scope
     test ran first and came back clean (versioning-policy §3 pins intake.md's required units,
     "MUST contain", not "ONLY contain" — an additive section changes no frozen unit's meaning;
     ask_human stays the floor). Surface ruled intake-only · depth ruled lean rule. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: intake-interview — extend the intake altitude with a proactive clarify step:
**interview before you size**. When the user brings a question or a request whose
intent is not yet sharp enough to place in one bucket, the AI explores it WITH the
user — reflect the intent heard, name what seems in and out of scope, offer 2–3
sized options with a recommendation — and only then emits the intake proposal.
(Origin: the human's ask 2026-06-07 — "when user makes a question, help them explore;
proactively interview their scope and milestone with your suggestion." This task's own
intake ran in exactly this shape: surface/depth/sizing interviewed before classification.)

Framings weighed: one-rule-in-intake.md (chosen) · intake + every seam via
report-template.md (rejected by the human — bigger surface, touches v17's
just-rewritten files) · session-behavior-only, no method change (rejected by the
human — the method should carry it for every agent).

Must:
  - intake.md gains ONE new section `## Interview before you size`, placed between the
    intro paragraph and `## The four buckets` (chronological: interview, then classify),
    carrying: the trigger (a question, or intent not sharp enough to size into one
    bucket) · the three moves (reflect the intent heard · name in/out of scope · offer
    2–3 sized options with your own recommendation) · the closing duty (only then emit
    `{ bucket, rationale, command }`) · the floor (`ask_human` stays the reject when the
    interview cannot converge — quoting the existing "never guess a bucket" verbatim).
  - SKILL.md's intake paragraph names the rule (≤1 line growth) so the behavior is
    discoverable from the always-loaded surface; intake.md stays the one home.
  - wording obeys the frozen v17 rubric (wording-lint green); the floor's negative
    quotes the existing ask_human line — the negative IS the obligation
    (positivization boundary, foundation-version 16).
  - additive only: the 4 bucket rows · the tie-break line · the 3 reject codes · the
    worked-examples table stay verbatim (versioning-policy structural test + semantic
    inventory stay green).
  - 3-mirror parity: canonical → `_bundled/` → `.claude/skills/add` byte-identical.
Reject:
  - the rule restated in any file beyond intake.md + the one SKILL.md anchor
    -> "rule_sprinkled"
  - any frozen intake unit (bucket row, tie-break, reject code, example row)
    reworded, weakened, or removed while adding -> "guard_weakened"
  - an edit that trips wording-lint or the semantic inventory -> "semantics_changed"
  - canonical and mirror copies diverging -> "mirror_drift"
After:
  - every future raw request inherits interview-first from the one home: a question
    is explored and suggested into shape BEFORE it is sized; the proposal
    `{ bucket, rationale, command }` (or a reject code) remains the only exit;
    suite + wording-lint + semantic-inventory + parity all green.
Assumptions — least-sure first:
  ⚠ the trigger is CONDITIONAL (a question, or unsharp intent) — a crisp,
    already-sized request still classifies directly — least sure because the ask
    said "when user make a question", which could mean interview ALWAYS; if wrong:
    friction on crisp requests, or missed interviews — a one-clause change request.
  ⚠ "2–3 sized options with a recommendation" is the right suggestion shape (mirrors
    co-specify's diverge move at the intake altitude) — least sure because the ask
    named "suggestion" without a shape; if wrong: the rule under- or over-formats
    chat behavior — wording-only fix.
  - [x] placement between intro and buckets is structurally free — verified:
    test_intake_rubric.py asserts unit presence, never section order or adjacency.
  - [x] no engine (add.py) change — chat-layer discipline only (matches
    question-summary-layer).
  - [x] lint/inventory/parity are owned by the standing fences — declared, never
    duplicated (clarity-greenstate convention, foundation-v16).

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the rule teaches interview-then-propose (the clarify-first fix)
  Given intake.md after the edit
  When you read the section between the intro and "## The four buckets"
  Then "## Interview before you size" states the trigger (a question, or intent
       not sharp enough to place in one bucket), the three moves (reflect the
       intent heard · name in and out of scope · offer 2–3 sized options with a
       recommendation), and the closing duty (only then emit
       { bucket, rationale, command })
  And the floor line keeps ask_human as the reject when the interview cannot
       converge — "never guess a bucket" verbatim

Scenario: discoverable from the always-loaded surface
  Given SKILL.md after the edit
  When you read its intake paragraph
  Then it names "Interview before you size" and points at intake.md
  And the paragraph grew by at most one line

Scenario: one home only (rejection: rule_sprinkled)
  Given the skill surface after the edit
  When you search every file under skill/add/ for "Interview before you size"
  Then it matches in intake.md and SKILL.md only
  And every other engine doc and phase guide is byte-unchanged

Scenario: additive only (rejections: guard_weakened · semantics_changed)
  Given the pre-edit intake.md with its 4 bucket rows, tie-break line, 3 reject
       codes, and worked-examples table
  When the new section lands
  Then every one of those frozen units is present verbatim (none reworded,
       none removed)
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
EDIT add-method/skill/add/intake.md            (canonical · 1 hunk · additive)
  hunk A -> INSERT the frozen section below between the intro paragraph and
            "## The four buckets"; every existing unit stays verbatim
EDIT add-method/skill/add/SKILL.md             (1 hunk · additive)
  hunk B -> the intake paragraph's closing sentence gains the rule by name,
            ≤1 line growth
SYNC  src/add_method/_bundled/skill/add/ + .claude/skills/add/   (mirrors, byte-equal)
  reject -> { error: "rule_sprinkled" | "guard_weakened" | "semantics_changed"
              | "mirror_drift" }
Schema: none — prose-only; no add.py, no state.json, no engine behavior change
```

Frozen section text (hunk A, verbatim):

> ## Interview before you size
>
> When the request arrives as a question, or its intent is not yet sharp enough to
> place in one bucket: explore it WITH the user before classifying. Reflect the
> intent you heard, name what seems in and out of scope, and offer 2–3 sized
> options with your own recommendation. Only then emit `{ bucket, rationale,
> command }`. `ask_human` stays the floor: when interviewing cannot sharpen the
> request, reject — never guess a bucket.

Frozen anchor text (hunk B, verbatim — appended to the SKILL.md intake paragraph):

> A question or unsharp intent? **Interview before you size** — explore and
> suggest first (`intake.md`).

Status: FROZEN @ v1 — approved by Tin Dang · date: 2026-06-07   <!-- the one approval over §1–§4; both ⚠ flags surfaced at the seam (conditional trigger · 2–3-options shape) and accepted as frozen. Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every frozen hunk pinned by ≥1 needle (guard-dense, foundation-v16);
4 RED tests + 1 disclosed GREEN guard.
Plan (one test per scenario, asserting behavior not internals):
  - test_interview_section_present   (scenario 1, RED): intake.md carries the frozen
    section's needles — "## Interview before you size" · "explore it WITH the user" ·
    "2–3 sized options" · "Only then emit" · "never guess a bucket" in the floor line
  - test_section_before_buckets      (scenario 1, RED): the section header's index <
    "## The four buckets" index (pins the chronological placement)
  - test_skill_anchor_names_rule     (scenario 2, RED): SKILL.md carries
    "Interview before you size"
  - test_one_home_only               (scenario 3, RED): "Interview before you size"
    appears in EXACTLY {intake.md, SKILL.md} across skill/add/**/*.md — red now
    (0 homes), green only at exactly 2; guards rule_sprinkled permanently
  - test_ask_human_floor_verbatim    (scenario 4, GREEN guard — disclosed): the
    existing ask_human reject line ("Ask the human; never guess a bucket.") stays
    byte-present (guards guard_weakened; green at birth by design, like the
    question-summary-layer pinned guard)
  - scenario 4 lint/inventory + scenario 5 parity: owned by the STANDING fences
    (`wording_lint` · semantic-inventory · the skill/add tree-parity + md5 guards) —
    declared here, never duplicated (clarity-greenstate convention, foundation-v16).

Tests live in: `add-method/tooling/` test_intake_interview.py · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): additive-only — the frozen hunks land character-exact
  from §3; every existing intake.md unit stays verbatim (the green guard + standing
  fences pin them).
Code lives in: add-method/skill/add/intake.md + SKILL.md (canonical) ·
  mirrors via scripts/prepare_bundle.py + cp to .claude/skills/add/
Constraints: do NOT change any test or the contract; only the 2 contracted hunks +
  mirror sync move; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — whole suite **527 OK** (522 + the 5 new); new suite went
      4 RED → 5 green at the build, red was for the right reason (needles absent)
- [x] coverage did not decrease — suite grew by 5; standing fences untouched
      (wording-lint 0 findings · semantic-inventory green · 3-tree md5 parity verified)
- [x] no test or contract was altered during build — test_intake_interview.py and §3
      byte-unchanged since the front commit. ONE disclosed deviation: hunk A landed
      word-identical but re-wrapped vs the §3 blockquote ("2–3 sized options" made
      contiguous for the needle) — freeze-data-not-presentation; same class as the
      question-summary-layer ratified rewrap. Ruled at the gate below.
- [x] concurrency / timing — n/a: prose-only, no engine or runtime behavior
- [x] no exposed secrets, injection openings, or unexpected dependencies — doc edit
      only; `add.py audit` clean (44 tasks) · `check` 188 passed
- [x] layering & dependencies follow CONVENTIONS.md — one home + one anchor
      (rule_sprinkled guard green); additive-only (guard_weakened guard green)
- [x] a person reviewed and approved the change — gate ruled via AskUserQuestion,
      2026-06-07: PASS, the word-identical rewrap RATIFIED as a presentation
      deviation (freeze-data-not-presentation; question-summary-layer precedent)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-07

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): future intakes follow interview→propose for
questions/unsharp intent while crisp requests still classify directly (the ⚠
conditional-trigger flag); the ask_human rejection rate at intake (the interview
should lower it, never replace it). The decisive signal is the FIRST raw question
in a COLD session — this task's own intake is a non-blind sample of one (the
author-agent knew the rule); a fresh session interviewing before sizing is the
behavioral proof that counts.
Spec delta for the next loop: both frozen ⚠ flags held in the rule's first live
run — this task's own intake (surface · depth · sizing interviewed, then sized);
if crisp requests start drawing needless interviews, the trigger clause is the
one-line change request.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] a §4 needle frozen from a wrapped §3 blockquote collides with the
  landed re-flow — pin needles as single-line fragments of the frozen text (or
  whitespace-normalize the assert) at WRITE time (evidence: the build's only red
  after a word-exact landing was the "2–3 sized / options" wrap break — second
  occurrence of this class after question-summary-layer's ratified rewrap)
- [ADD · folded] fold routing carries a real-but-unwritten exception: contract-AUTHORING
  SDD lessons fold into CONVENTIONS beside their siblings, not §Spec — name the split
  in fold.md ("what we build" → §Spec · "how we author" → CONVENTIONS) or it bends
  silently (evidence: this session's fold + the v16/v17 SDD bullets living at
  CONVENTIONS:236 against fold.md's SDD→§Spec row)
- [TDD · folded] the presence-based narrative census leaves a NEW prose section
  unguarded against future stray tags — add new sections to test_xml_convention's
  per-file enumeration when they land (evidence: "## Interview before you size"
  absent from intake.md's narrative tuple; suite green only because the census
  asserts listed sections, never the full set)
