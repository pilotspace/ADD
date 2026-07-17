# TASK: Compaction contract — shared eligibility + 4 per-spec rolled-line shapes + convention-vs-engine seam

slug: compact-contract · created: 2026-06-15 · stage: mvp · risk: high
autonomy: conservative   <!-- method-defining: this contract redefines how the append-only invariant is amended downstream; high-risk scope must not auto-complete (unguarded_high_risk_auto). Human stays at the gate. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `.add/PROJECT.md` §Key Decisions (append-only, L339) — dated `| date | decision | why | outcome |` table, CURRENTLY oldest-first (2026-06-01 top → 2026-06-14/fv30 bottom); §Spec/SDD (L37–261) version bullets tagged `[folded foundation-version N]`, also oldest-first; `foundation-version: 30` marker (L8).
  - `.add/CONVENTIONS.md` §Method learnings (L28) — flat `- (TAG) **Title.** …` list, oldest-first append (689 lines — the bloat source).
  - `.add/GLOSSARY.md` (25L `Term: def`, some verbose) · `.add/MODEL_REGISTRY.md` (6L, current model only) — the two tiny specs (minimal/forward-looking shapes).
  - `.add/tooling/add.py` `cmd_compact` (L2031) — the EXISTING *archive* compaction (recovery-bundle move) → the naming seam to disambiguate; `cmd_reopen` (L768) appends an append-only `reopens` entry (sibling append-only surface).
Context (working folder): `.claude/skills/add/fold.md` (the fold ritual — §Status transitions L37–43: "append-only: adds bullets/rows" · monotonic `foundation-version` bump) + its dogfood mirror under `.add/`; book ch. `09-the-loop.md` (loop / file-hygiene) — the chapter compact-book-align extends.
Honors (patterns / conventions): fold.md "AI proposes, human confirms" · v18 archive lifecycle (light-archive → compact) · monotonic foundation-version bump · the §Key-Decisions row shape · GLOSSARY one-name-per-concept — task-delta only, defers to PROJECT.md/CONVENTIONS.md.
Anchors the contract cites: the 4 spec section headers · `cmd_compact` (the disambiguation seam) · fold.md's append→prepend rule · the `foundation-version` marker.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: The foundation-compaction contract — the frozen rule-set every consumer task (invariant-amend · compact-guide · apply-compaction) builds against: one eligibility test, four per-spec rolled-line shapes, the newest-first ordering rule, the preservation guarantees, and the convention-vs-engine seam.
Framings weighed: convention-guided ritual (chosen — a `compact-foundation.md` guide + judgment reject codes; engine stays judgment-free, mirroring fold) · engine-checked op (reject codes enforced in `add.py check` / a new command) · hybrid (guide-driven + a lightweight `check` WARN on un-compacted bloat — deferred OUT)
Must:
<must>
  - ELIGIBILITY: define ONE test — an entry is compaction-eligible IFF its milestone is SHIPPED (done/archived) AND it carries ZERO open residues/deltas.
  - PER-SPEC SHAPES: define a distinct rolled-line shape for each spec — PROJECT §Spec bullets → "settled fvN–fvM" line · PROJECT §Key-Decisions rows → "settled <dateA–dateB>" row · CONVENTIONS §Method-learnings run → "settled-conventions <range>" pointer · GLOSSARY verbose definition → terse canonical + git pointer · MODEL_REGISTRY superseded rows → "prior models (see git)" line.
  - NEWEST-FIRST ORDERING: every append-only sequence prepends the newest record at the TOP; the rolled-up settled line anchors at the BOTTOM (oldest) — compaction collapses upward from the tail.
  - PRESERVATION: never delete — summarize + a surviving git/archive pointer; OPEN residues stay live; the audit trail is summarized-not-deleted.
  - SEAM: name foundation compaction as a convention-guided ritual (human-confirmed, AI-proposes) DISTINCT from the existing engine `add.py compact <slug>` (archive recovery-bundle move) — no new engine command, no `add.py check` enforcement.
</must>
Reject:
<reject>
  - an entry that is unshipped OR carries ≥1 open delta/residue is offered for collapse -> "open-residue-version"
  - a collapse that would drop the git/archive pointer or the summarized audit trail -> "trail-loss"
  - a record placed out of newest-first order, or a settled line not anchored at the tail -> "wrong-order"
</reject>
After:
<after>
  - A frozen contract names all five Musts (eligibility · 4 shapes · ordering · preservation · seam) and the three reject codes — a stable shape the other four tasks build against without re-litigation.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ convention-guided (NOT engine-checked) is the right seam — lowest confidence because the three reject codes READ like an engine lint and a future maintainer may want `add.py check` to WARN on un-compacted bloat; if wrong: invariant-amend builds judgment-only reject codes that later need engine enforcement (guard + test rework). Recommendation: convention-guided, mirroring fold's judgment-free-engine precedent; a `check` WARN stays a deferred, OUT-of-scope follow-up.
  - [ ] four per-spec shapes (not one generalized shape) is the right granularity — human-chosen at intake; treated settled.
  - [ ] newest-first applies uniformly to all three PROJECT/CONVENTIONS sequences — human-chosen "all append-only sequences"; treated settled.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: eligible entry collapses with a surviving pointer
  Given a shipped milestone's §Spec bullets with zero open residues
  When the maintainer applies the foundation-compaction ritual
  Then the stable bullets roll into one "settled fvN–fvM" line carrying a git/archive pointer
  And every OPEN residue elsewhere stays live and untouched

Scenario: each spec collapses by its own tailored shape
  Given stable shipped entries in PROJECT §Key-Decisions, CONVENTIONS §Method-learnings, GLOSSARY, and MODEL_REGISTRY
  When each is compacted
  Then each uses its named shape (settled-row · settled-conventions pointer · terse+git · prior-models line)
  And no source text is deleted — every collapse leaves a git pointer

Scenario: append-only records read newest-first
  Given a new §Key-Decisions row recorded via fold
  When it is added
  Then it appears at the TOP of the table (newest-first)
  And the rolled-up settled line stays at the BOTTOM (oldest)

Scenario: an open residue blocks collapse
  Given a version bullet carrying an OPEN delta/residue
  When the maintainer offers it for collapse
  Then the ritual rejects with "open-residue-version"
  And the bullet stays live and unchanged

Scenario: a collapse that loses the trail is rejected
  Given a proposed collapse that would drop the git/archive pointer or the audit summary
  When it is validated
  Then it rejects with "trail-loss"
  And the original entry stays unchanged

Scenario: an out-of-order record is rejected
  Given a record placed out of newest-first order, or a settled line not at the tail
  When it is validated
  Then it rejects with "wrong-order"
  And the sequence stays unchanged

Scenario: the ritual is distinct from the engine compact command
  Given the existing `add.py compact <slug>` (archive recovery-bundle move)
  When a maintainer reads the foundation-compaction contract
  Then it names foundation compaction as a DISTINCT convention-guided ritual on living specs
  And it adds no new engine command and no add.py check enforcement
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FOUNDATION-COMPACTION CONTRACT  — convention-guided ritual (engine stays judgment-free)

eligibility(entry)   -> eligible IFF  shipped(entry.milestone) AND open_residues(entry) == 0
ordering(sequence)   -> newest-first: prepend newest at TOP; settled line anchored at the BOTTOM (oldest)

rolled_line_shape  (per spec — tailored):
  PROJECT.md §Spec          stable [folded fv N..M] bullets  -> "settled fvN–fvM — <1-line theme> (see git)"
  PROJECT.md §Key-Decisions  matching shipped rows           -> "| settled <dateA>–<dateB> | <N> decisions rolled | … | see git |"
  CONVENTIONS.md §learnings  run of stable (TAG) bullets      -> "- settled conventions <range> — <N> rules (see git)"
  GLOSSARY.md                verbose stable definition        -> terse canonical line + "(rationale: see git)"
  MODEL_REGISTRY.md          superseded model rows            -> "Prior models: <list> (see git)"

preservation (every collapse):  NEVER delete · summarize + a surviving git/archive pointer ·
                                OPEN residues stay live · audit trail summarized-not-deleted

reject:
  open-residue-version  -> entry is unshipped OR has ≥1 open delta/residue   (leave it live)
  trail-loss            -> collapse would drop the git/archive pointer or the audit summary
  wrong-order           -> record not newest-first, or settled line not at the tail

seam:  foundation compaction ≠ engine `add.py compact <slug>` (archive recovery-bundle move).
       Realized as the `compact-foundation.md` convention (AI proposes · human confirms) —
       NO new engine command, NO add.py check enforcement (a `check` WARN is a deferred, OUT follow-up).
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-15
Least-sure flag surfaced at freeze: [spec] convention-guided vs engine-checked seam — the three reject codes read like an engine lint; chosen convention-guided to keep the engine judgment-free (fold precedent). If wrong: invariant-amend's reject codes need later engine enforcement (guard + test rework).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject has one scenario-test (prose-contract tests — assert the rule's SHAPE and behavior per CONVENTIONS "prose-guide tasks are red→green-testable" + "words-exist ≠ method-works", not bare token presence).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_eligibility_rule: arrange a shipped+zero-residue entry and an open-residue entry / act parse the contract's eligibility rule / assert the first is eligible, the second yields "open-residue-version"
  - test_per_spec_shapes_named: arrange the frozen contract / assert a DISTINCT rolled-line shape is named for each of the 5 spec sections (PROJECT §Spec · §Key-Decisions · CONVENTIONS · GLOSSARY · MODEL_REGISTRY) — present and non-identical
  - test_newest_first_ordering: arrange a sequence + a new record / assert the contract mandates prepend-at-top and settled-line-at-tail, and an out-of-order record yields "wrong-order"
  - test_preservation_guarantees: arrange a collapse proposal / assert never-delete + surviving git/archive pointer + OPEN-residue-stays, and a pointer-dropping collapse yields "trail-loss"
  - test_disambiguation_seam: arrange the contract + the engine `add.py compact` help / assert the contract marks them distinct and asserts NO new engine command and NO add.py check enforcement (convention-guided)
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `./compaction-contract.md` `./tests/`   — the canonical frozen rule doc the 4 consumer tasks cite + its guard tests. Convention-guided → NO `add.py`/engine touch (the seam decision).
Strategy (ordered batches): 1. write `./tests/` red against the empty/absent doc · 2. write `compaction-contract.md` realizing the frozen §3 (eligibility · 5 shapes · ordering · preservation · seam · 3 reject codes) until green.
Safety rule (feature-specific): the doc RESTATES the frozen §3 verbatim-in-meaning; if the build reveals the contract is wrong, STOP — change-request back to SPECIFY, never edit the frozen contract to pass.
Code lives in: `./compaction-contract.md`
Constraints: do NOT change any test or the contract; no engine/add.py edits (convention-guided seam); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 6/6 green (`python3 -m unittest discover -s tests`)
- [x] coverage did not decrease — +1 new test file (6 tests); no existing test touched
- [x] no test or contract was altered during build — §3 FROZEN + the red suite unchanged; build wrote ONLY `compaction-contract.md`
- [x] the green was EARNED, not gamed — self-refute: each of the 6 asserts checks a DISTINCT semantic property (eligibility logic · 5 mutually-distinct quoted shapes · ordering + wrong-order · preservation + trail-loss · seam disclaimers · 3 reject codes) against the REAL consumed artifact, not a fixture; no vacuous/stubbed assert (conservative — human owns the gate; subagent refute optional, not run for a 6-assert prose contract)
- [x] concurrency / timing of the risky operation is safe — N/A (a static prose contract; no runtime operation)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose doc; zero deps; stdlib-only test (`re`/`os`/`unittest`)
- [x] layering & dependencies follow CONVENTIONS.md — convention-guided seam HONORED: no `add.py`/engine edit; unittest per repo convention
- [ ] a person reviewed and approved the change — ⟵ YOUR gate (conservative + risk:high)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read `compaction-contract.md` in full: it RESTATES frozen §3 (eligibility · 5 tailored shapes · newest-first ordering · preservation · 3 reject codes · the engine-`compact` seam) verbatim-in-meaning; no drift from §3.
- [~] WIRING / DEAD-CODE (code) — N/A: no code symbols; the doc is CITED by the 4 downstream tasks, not imported.

### GATE RECORD
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-reject-code rate once apply-compaction runs the ritual (open-residue-version · trail-loss · wrong-order frequency); compaction events per milestone close.
Spec delta for the next loop: the contract is convention-guided (no engine enforcement) — watch whether maintainers actually run the ritual at close, or whether the deferred `check` WARN on un-compacted bloat becomes necessary.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] foundation specs need a PER-SPEC rolled-line dialect, not one generalized shape — the four specs' append-only forms differ structurally (evidence: compact-contract froze 5 distinct shapes for 5 spec sections)
- [ADD · folded] a convention-guided method contract (engine stays judgment-free) is still TDD-able via a prose contract doc + structural asserts (evidence: compact-contract shipped 6 green prose-contract tests with zero engine edit)
- [SDD · folded] newest-first ordering and compaction compose into ONE invariant amendment (newest on top, settled tail at bottom), not two themes (evidence: the ordering enhancement folded into invariant-amend mid-intake without a new task)
