# TASK: Re-freeze append-only with the recorded compaction door + reject codes

slug: invariant-amend · created: 2026-06-15 · stage: mvp · risk: high
autonomy: conservative   <!-- amends a FROZEN method invariant (append-only) AND mutates live method files (fold.md ×3 mirror homes) + the dogfood foundation; high-risk must not auto-complete (unguarded_high_risk_auto). Human at the gate. -->
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
  - `fold.md` ×3 CANONICAL mirror homes (must stay byte-identical — CONVENTIONS "mirror-clause-all-copies / dogfood md5 parity"): `add-method/skill/add/fold.md` · `add-method/src/add_method/_bundled/skill/add/fold.md` · `.claude/skills/add/fold.md`. Edit §"The ritual" + §"Status transitions & version" (the "append-only: adds bullets/rows" line) → newest-first PREPEND + the recorded compaction door. (tmp/smoke + venv copies are install/test artifacts — NOT canonical, excluded.)
  - `.add/PROJECT.md` §Key Decisions (append-only, L339 header) + §Spec — the dogfood foundation where the append-only invariant is stated; reword "append-only" → "append-only (newest-first) EXCEPT via the recorded compaction door".
  - `.add/CONVENTIONS.md` header (L1 "survivor layer — set once") — where a survivor-doc convention names append-only ordering.
  - the frozen contract: `./.add/tasks/compact-contract/compaction-contract.md` (FROZEN @ v1) — the source of truth this task realizes (eligibility · ordering · 3 reject codes · seam).
Context (working folder): the compact-contract bundle (done, gate PASS) defines the shape; book ch. `09-the-loop.md` (loop / file-hygiene) is compact-book-align's, not this task's.
Honors (patterns / conventions): mirror-clause-all-copies (every fold.md home edited together, md5-parity) · "AI proposes, human confirms" · append-only never silently rewrites · monotonic foundation-version · the frozen compaction contract is the source of truth (never edit it to fit) — task-delta only, defers to PROJECT.md/CONVENTIONS.md.
Anchors the contract cites: the 3 fold.md homes · PROJECT.md §Key-Decisions header · CONVENTIONS.md header · the 3 reject codes (open-residue-version · trail-loss · wrong-order) + a new `wrong-order` ordering guard.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Re-freeze the append-only invariant as newest-first prepend + the recorded compaction door (with the 3 contract reject codes), across all 3 fold.md mirror homes and the dogfood foundation — realizing the FROZEN compaction-contract @ v1.
Framings weighed: amend the existing append-only clause IN PLACE (chosen — one minimal coherent edit per home; no contradiction surface) · add a SEPARATE compaction section leaving the old clause untouched (more surface, risks two rules disagreeing) · engine-enforce the invariant (rejected — convention-guided per the frozen seam)
Must:
<must>
  - RE-FREEZE THE CLAUSE: fold.md's "a consolidation is append-only: it adds bullets/rows; it never silently rewrites existing foundation text" becomes "append-only (NEWEST-FIRST — prepend new records at the top) and never silently rewrites — EXCEPT via the recorded compaction door" — in ALL 3 canonical fold.md homes, BYTE-IDENTICAL.
  - NEWEST-FIRST: the amended ritual directs new records to PREPEND at the top (not append at the end); the monotonic foundation-version bump is unchanged.
  - THE DOOR: name the recorded compaction door as the ONLY sanctioned exception to append-only, pointing to compact-foundation.md, and carrying the eligibility precondition (shipped + zero open residues).
  - REJECT CODES: name the 3 contract reject codes — open-residue-version · trail-loss · wrong-order — at the invariant as JUDGMENT checks (no engine enforcement — the frozen seam).
  - FOUNDATION ECHO: PROJECT.md §Key-Decisions header + CONVENTIONS.md header read "append-only (newest-first) EXCEPT via the recorded compaction door"; no existing decision row or learning is deleted.
</must>
Reject:
<reject>
  - the 3 fold.md homes are not byte-identical after the edit (md5 drift) -> "mirror-drift"
  - the amendment drops or contradicts the existing "never silently rewrites" preservation guarantee -> "trail-loss"
  - the compaction door is stated WITHOUT its eligibility precondition (shipped + zero open residues) -> "ungated-door"
</reject>
After:
<after>
  - All 3 fold.md homes carry the byte-identical amended clause (newest-first + the door + 3 reject codes); PROJECT.md + CONVENTIONS.md echo it; the frozen compaction-contract is honored verbatim and the engine is untouched (still judgment-free).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ amend-in-place (not a new section) keeps fold.md coherent — lowest confidence because rewording a frozen invariant's exact sentence risks subtle contradiction with the surrounding ritual text (e.g. step 5 "append the accepted edits"); if wrong: the clause reads ambiguously and a future fold mis-orders or rewrites. Mitigation: quote the exact old sentence, replace minimally, re-read the whole § + step 5.
  - [ ] 3 fold.md homes is the COMPLETE canonical set (not 4+) — confirmed via os.walk excluding tmp/smoke + venv install artifacts; treated settled.
  - [ ] the foundation echo (PROJECT/CONVENTIONS) belongs here (the invariant STATEMENT), not in apply-compaction (the invariant APPLICATION) — treated settled.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the amended invariant directs newest-first
  Given fold.md's amended append-only clause
  When a maintainer reads how a new record is recorded
  Then the clause directs PREPEND at the top (newest-first)
  And the "never silently rewrites existing foundation text" guarantee remains

Scenario: the compaction door is the only exception, and it is gated
  Given the amended append-only clause
  When read in full
  Then it names the recorded compaction door as the ONLY sanctioned exception, citing compact-foundation.md
  And the door carries the eligibility precondition (shipped + zero open residues)

Scenario: the three reject codes are stated at the invariant
  Given the amended clause
  When read
  Then open-residue-version, trail-loss, and wrong-order are named as judgment checks
  And no add.py / engine enforcement is added (the convention-guided seam holds)

Scenario: all three fold.md homes stay byte-identical
  Given the 3 canonical fold.md homes
  When the amendment is applied
  Then all 3 are md5-identical
  And a home left out of sync is rejected with "mirror-drift"

Scenario: an ungated door is rejected
  Given a draft of the door clause missing the shipped+zero-residue precondition
  When it is reviewed
  Then it is rejected with "ungated-door"
  And the clause is fixed to carry the precondition before it lands

Scenario: the dogfood foundation echoes the invariant without loss
  Given PROJECT.md §Key-Decisions header and CONVENTIONS.md header
  When the amendment lands
  Then both read "append-only (newest-first) EXCEPT via the recorded compaction door"
  And no existing decision row or learning is deleted
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
INVARIANT AMENDMENT  — realizes compaction-contract.md @ v1 (convention-guided; engine UNCHANGED)

append-only clause  (ALL 3 fold.md homes, written from ONE source → byte-identical):
  BEFORE: "a consolidation is **append-only**: it adds bullets/rows; it never silently
           rewrites existing foundation text."
  AFTER:  "a consolidation is **append-only (newest-first)**: it PREPENDS new bullets/rows at
           the top and never silently rewrites existing foundation text — EXCEPT via the
           recorded **compaction door** (`compact-foundation.md`): eligible (shipped + zero
           open residues) stable entries collapse upward into a rolled-up settled line at the
           tail. Reject: `open-residue-version` · `trail-loss` · `wrong-order`."

mirror parity:  the 3 canonical homes — add-method/skill/add · add-method/src/.../_bundled/skill/add ·
                .claude/skills/add — are md5-identical after the edit.   drift -> "mirror-drift"

foundation echo  (dogfood .add/, no existing entry deleted):
  PROJECT.md  §Key Decisions header -> "(append-only — newest-first; compaction door per compact-foundation.md)"
  CONVENTIONS.md header             -> one line: survivor docs are append-only (newest-first), compaction door excepted

engine:  UNCHANGED — no add.py edit, no new reject-code enforcement (the frozen seam).
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-15
Least-sure flag surfaced at freeze: [contract] the exact AFTER wording of a frozen invariant — risk of ambiguity against the surrounding ritual (step 5 "append the accepted edits" must read consistently with "prepend"); mitigated by minimal in-place replacement + a full re-read of fold.md §ritual + §status-transitions.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: each Must + each Reject has a test; assert the amended clause SHAPE + the md5 parity (behavioral, per CONVENTIONS "mirror-clause-all-copies" + "words-exist ≠ method-works").
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_append_only_newest_first: for EACH of the 3 fold.md homes / assert the amended clause says append-only (newest-first)/prepend-at-top AND retains "never silently rewrites"
  - test_compaction_door_named_and_gated: arrange the clause / assert it names the recorded compaction door as the ONLY exception, cites compact-foundation.md, and carries the "shipped + zero open residues" precondition [guards ungated-door]
  - test_three_reject_codes_at_invariant: arrange the clause / assert open-residue-version, trail-loss, wrong-order are all named
  - test_fold_mirror_parity: md5 the 3 canonical fold.md homes / assert all equal [guards mirror-drift]
  - test_foundation_echo_no_loss: arrange PROJECT.md §Key-Decisions header + CONVENTIONS.md header / assert both echo the amended invariant AND the §Key-Decisions data-row count did not decrease [guards trail-loss]
  - test_engine_unchanged: grep add.py / assert NO compaction reject-code enforcement was added (the 3 codes are not wired into check) — the convention-guided seam holds
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/fold.md` `add-method/src/add_method/_bundled/skill/add/fold.md` `.claude/skills/add/fold.md` `.add/PROJECT.md` `.add/CONVENTIONS.md` `./tests/`   — the 3 fold.md homes (byte-identical from one source) + the dogfood foundation echo + guard tests. NO `add.py`/engine edit (the convention-guided seam).
Strategy (ordered batches): 1. write `./tests/` red · 2. amend ONE fold.md home — the clause AND reconcile step-5 "append the accepted edits" → "prepend" so the ritual reads consistently — then COPY byte-identical to the other 2 (md5 verify) · 3. echo in PROJECT.md §Key-Decisions header + CONVENTIONS.md header · 4. run green.
Safety rule (feature-specific): edit the 3 fold.md homes from a SINGLE source text (write once → copy), so md5 parity is STRUCTURAL, never hand-synced; never edit the frozen compaction-contract to fit.
Code lives in: the 3 fold.md homes + `.add/PROJECT.md` + `.add/CONVENTIONS.md`
Constraints: do NOT change any test or the frozen contract; no `add.py`/engine edit (convention-guided seam); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 8/8 green (task suite); the method's OWN engine suite 1027/1027 OK (the live-method edit broke no guard)
- [x] coverage did not decrease — +1 test file (8 tests); strengthened mid-build with the coherence guard; no existing test weakened
- [x] no test or contract was altered during build — §3 FROZEN @ v1 + the red suite unchanged; build touched only the 3 fold.md homes + PROJECT.md + CONVENTIONS.md
- [x] the green was EARNED, not gamed — the build was a fail-closed verbatim-transform script (asserts each old string appears exactly once); tests assert real file content + md5 parity across 3 homes, not fixtures; no vacuous/stubbed assert
- [x] concurrency / timing of the risky operation is safe — N/A (static doc edit)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose edits only; stdlib-only test
- [x] layering & dependencies follow CONVENTIONS.md — mirror-clause-all-copies HONORED (3 homes byte-identical, md5 5fdc1c72…); engine untouched (convention-guided seam)
- [ ] a person reviewed and approved the change — ⟵ YOUR gate (conservative + risk:high — edits the LIVE method)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read fold.md §ritual + §status-transitions in full after the edit: the clause, step 5, line-34 (§Key-Decisions row), and line-39 (routed-target) now ALL read newest-first/prepend — coherent, no self-contradiction. PROJECT/CONVENTIONS headers echo it; no decision row deleted.
- [~] DISCLOSED BOUNDARY — the routing TABLE verbs ("refine/append a model bullet" · "append a testing/build convention", fold.md L28–32) still say "append". Left intentionally: they name the TARGET SECTION (DDD→§Domain, etc.), not the within-section position — which the amended clause now governs. Closing the genuine position-contradictions (step5/L34/L39) was in scope; rewording the routing table's "add" verbs is a separate judgment for your review.

### GATE RECORD
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether future folds actually prepend (newest-first) in the live foundation; md5 parity of the 3 fold.md homes on every method change.
Spec delta for the next loop: apply-compaction must now REORDER the existing live PROJECT.md/CONVENTIONS.md to newest-first (the invariant is stated; the existing data is still oldest-first until applied).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] amending a frozen-invariant DOC means reconciling EVERY position-describing sentence, not just the named clause — coherence spans the whole ritual (evidence: the clause-only red suite missed step5/L34/L39; the added coherence guard caught them)
- [TDD · folded] a byte-identical multi-home edit is provable by an md5-parity test + a fail-closed verbatim-transform script (evidence: invariant-amend wrote 3 fold.md homes from one source, md5 5fdc1c72 across all)
- [ADD · folded] a disclosed boundary AT the verify gate lets the human rule the reach explicitly instead of the AI guessing it (evidence: PASS accepted the routing-table-verbs boundary at the gate)
