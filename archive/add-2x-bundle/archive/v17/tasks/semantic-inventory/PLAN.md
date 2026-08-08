# TASK: Capture the semantic-preservation inventory + ship the deterministic diff gate

slug: semantic-inventory · created: 2026-06-06 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the SEMANTIC-PRESERVATION INVENTORY (one frozen doc) + `semantic-inventory` — a
  DETERMINISTIC preservation-diff GATE; the blocking gate rewrite-core + rewrite-guides build behind.
Framings weighed: deterministic token+anchor diff (chosen) · verbatim-text diff (rejected —
  false-positives on every legit reword, the metric trap one level up) · model-judged "same meaning?"
  diff (rejected — non-deterministic, model-in-loop; that IS the indicative eval, never the gate)

Must:
  - Freeze ONE inventory doc capturing the surface's preservation-critical SEMANTIC UNITS in two layers:
    (a) a per-file TOKEN INVENTORY — stable identifiers that must survive a rewrite UNCHANGED: gate-outcome
        tokens (PASS · RISK-ACCEPTED · HARD-STOP · ESCALATE · auto-resolved), named codes (snake_case
        reject/error codes: unguarded_high_risk_auto · metric_gate · frozen_scope · unescalated_security_note
        · already_locked · setup_unlocked · the intake/scope/fold/delta codes), and the method's defined vocabulary;
    (b) a LEAN ANCHORED-INVARIANT list — each safety proposition the token layer can't guard, as
        { id, file, anchor_tokens [, negative_anchors ] }, seeded from task 1's FROZEN negative_keep_list
        + the gate outcomes. Lean because per-file token presence already subsumes most co-location;
        anchors earn their place only in the multi-safety-rule files (run.md · 6-verify.md · SKILL.md).
  - Ship `semantic-inventory`: reads the FROZEN inventory (single source) and diffs it against the live
    surface (skill/add 18 + docs/appendix-b-prompts.md = 19 files). DETERMINISTIC. Three checks, each
    failing ONLY on a real regression:
    (S1) every frozen token still present IN ITS FILE        (a dropped / renamed / relocated code or outcome)
    (S2) every invariant's anchor tokens still CO-OCCUR in its file/window  (a silently dropped conjunct, or
         a removed scope-qualifier like "always" / "never")
    (S3) no invariant's NEGATIVE-ANCHOR co-occurs in its window  (opportunistic catch for an ADDED exception —
         e.g. {unless · except · waive · RISK-ACCEPTED} inside the security-always window)
  - Extract the token layer by a PRECISE deterministic rule (fixed gate-outcome vocab + backticked
    snake_case codes + the defined-vocabulary list), so the frozen snapshot is REPRODUCIBLE and reviewable —
    never a hand-typed list that silently misses a unit.
  - Cover every safety negative on task 1's frozen negative_keep_list with ≥1 anchored invariant (auditable
    curation — the gate self-checks this coverage at freeze, so an un-anchored safety rule can't slip through).
  - State EXPLICITLY what the gate does NOT prove (the cede-list, NAMED — never hidden): an INVERSION around
    surviving anchors (an added exception / negation / scope-narrowing that keeps every anchor token),
    positivity / scope JUDGMENT, and meaning beyond the anchors. These are caught by HUMAN REVIEW + the
    INDICATIVE behavioral eval — never by this deterministic gate. The gate proves preservation is
    NECESSARY-true (nothing dropped / renamed / relocated; anchors intact), not SUFFICIENT-true (meaning fully intact).
  - Design the gate for failure: a missing / malformed inventory or an unreadable surface file fails LOUD
    (exit 2, named error) — never a silent green pass.

Reject:
  - a proposed check that diffs VERBATIM prose text -> "verbatim_diff"   (false-positives on every legit
    reword — the metric trap one level up; this gate is token+anchor, not text)
  - a proposed check that asks a model "is this the same meaning?" -> "model_judged_gate"  (non-deterministic;
    that is the INDICATIVE eval, not the blocking gate)
  - a frozen token absent from its file on the live surface -> "unit_dropped"
  - a frozen token present on the surface but MOVED to a different file -> "unit_relocated"
  - an anchored invariant whose anchor tokens no longer co-occur in its window -> "invariant_broken"
  - a negative-anchor co-occurring inside an invariant's window -> "exception_introduced"
  - a safety negative (negative_keep_list) mapped to NO anchored invariant -> "invariant_uncovered"  (freeze-time)
  - the inventory doc claiming the gate proves SUFFICIENT preservation -> "overclaim_sufficient"  (the doc MUST
    name the cede-list; "provably preserved" without the cede-list is the overclaim this code forbids)

After:
  - The inventory is FROZEN (one doc — the single source the rewrite tasks' gate reads). `semantic-inventory`
    runs GREEN over the current surface (every unit present in-file · every invariant intact · no exception
    introduced · every safety negative covered). rewrite-core + rewrite-guides inherit a deterministic BLOCKING
    gate that fails on a real drop / rename / relocation / introduced-exception — with the INVERSION class
    explicitly ceded to human review + indicative eval, never silently claimed as proven.

Assumptions — least-sure first:
  ⚠ COMPLETENESS — the frozen inventory lists EVERY preservation-critical unit. Least sure because an OMITTED
    safety unit is the one failure that silently ships a weakened method (the gate guards only what it lists);
    if wrong: a rewrite drops/weakens an un-inventoried rule and the gate stays green. Mitigated by
    extraction-BY-RULE (not hand-typing) for tokens · negative_keep_list-seeded coverage + the freeze-time
    invariant_uncovered check for invariants — but the JUDGMENT "which propositions are safety-critical" wants
    your eyes on the FROZEN CONTENTS at the seam (the approval object here is the inventory list, not the tool shape).
  ⚠ NECESSARY-not-SUFFICIENT is the HONEST contract — least sure because it deliberately CANNOT prove "meaning
    fully intact", only "nothing dropped/renamed/relocated + anchors intact + no listed exception". If you expected
    the gate to BLOCK every meaning change, it provably can't — an inversion around surviving anchors is
    model-judgment, so it stays review + indicative eval. The milestone's "semantics provably preserved" =
    THIS gate (necessary) + review + indicative eval (the rest), NOT the gate alone. (See the §3 least-sure flag —
    this wants explicit ratification; a milestone shared-decision note records the operational definition.)
  - [ ] The surface is the same 19 files as wording-rubric (skill/add 18 + appendix-b); extraction reads the
        canonical tree (the _bundled & .claude mirrors are byte-identical via parity, so canonical suffices).
  - [ ] semantic-inventory and wording-lint share vocabulary but check different things (wording-lint: lexical
        idiom/emphasis regression; semantic-inventory: per-file unit preservation) — SEPARATE tools, SEPARATE
        frozen docs, per the v17 lexical/meaning seam. Numeric thresholds are near-absent on the surface
        (only a borderline `< 0.9` self-eval in streams.md; behavior numbers are code-enforced by the 488-suite) — CEDED.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the inventory is the single source the gate reads
  Given the token layer + anchored-invariant list are frozen in SEMANTIC_INVENTORY.md
  When semantic-inventory runs
  Then it loads its units/invariants FROM that doc (no hardcoded duplicate)
  And it prints the inventory path it read

Scenario: the extraction is reproducible (token layer is rule-derived, not hand-typed)
  Given the frozen token snapshot and the live surface
  When the extraction rule re-runs over the surface
  Then it reproduces the same per-file token set the snapshot froze
  And a unit added by the rule but absent from the snapshot is reported (drift, not a silent miss)

Scenario: a dropped unit is caught
  Given a frozen token "unguarded_high_risk_auto" in run.md
  When a rewrite removes it from run.md
  Then the gate reports "unit_dropped" with the file + the token
  And it exits non-zero

Scenario: a relocated unit is caught
  Given a frozen token present in 6-verify.md
  When a rewrite moves it to a different file
  Then the gate reports "unit_relocated" (present on the surface, wrong file)
  And it exits non-zero

Scenario: a clean reword around a unit does NOT false-positive
  Given a frozen token in its file and the prose around it reworded literally
  When the gate runs
  Then it reports zero findings for that file       # a good rewrite is never blocked
  And it exits zero

Scenario: a broken invariant is caught (dropped conjunct / removed scope-qualifier)
  Given the invariant "auto-pass conjunction" anchored in run.md
  When a rewrite drops the "no test weakened" conjunct (or removes "always" from security-always)
  Then the gate reports "invariant_broken" with the invariant id
  And it exits non-zero

Scenario: an introduced exception is caught (negative-anchor)
  Given the invariant "security-always-HARD-STOP" with negative-anchors {unless, except, waive, RISK-ACCEPTED}
  When a rewrite adds "unless RISK-ACCEPTED by an owner" inside its window
  Then the gate reports "exception_introduced"
  And it exits non-zero

Scenario: an inversion around SURVIVING anchors is NOT claimed as caught (the honest cede)
  Given a rewrite that keeps every anchor token but narrows a rule's scope in prose the negative-anchors miss
  When the gate runs
  Then it passes (green) — BY DESIGN, this class is ceded
  And the inventory doc + the run report NAME this limitation (human review + indicative eval own it, not the gate)

Scenario: a verbatim-text diff is refused by design
  Given a proposed check that compares pre/post prose text byte-for-byte
  When it is checked against the inventory contract
  Then it is rejected as "verbatim_diff"
  And the doc records WHY (it false-positives on a good reword)

Scenario: a model-judged gate is refused by design
  Given a proposed check that asks a model "do these mean the same?"
  When it is checked against the inventory contract
  Then it is rejected as "model_judged_gate"   # non-deterministic — that's the indicative eval, not the gate

Scenario: an uncovered safety negative is refused at freeze
  Given a safety negative on task 1's negative_keep_list mapped to NO anchored invariant
  When the freeze-time coverage check runs
  Then it reports "invariant_uncovered" with the negative
  And the freeze is refused until it is anchored

Scenario: an overclaiming inventory doc is refused
  Given a SEMANTIC_INVENTORY.md that claims "provably preserved" with no cede-list
  When the freeze-time self-check runs
  Then it reports "overclaim_sufficient"
  And the doc must name the inversion/judgment cede before it can freeze

Scenario: the gate fails loud on a broken inventory (design-for-failure)
  Given SEMANTIC_INVENTORY.md is missing or malformed
  When semantic-inventory runs
  Then it exits 2 with a named error
  And it does NOT report a false green   # no silent pass

Scenario: the live surface is green at freeze
  Given the frozen inventory seeded from the current surface
  When semantic-inventory runs over the live surface
  Then every unit is present in-file, every invariant intact, no exception introduced, every safety negative covered
  And it exits zero
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
INVENTORY  add-method/tooling/SEMANTIC_INVENTORY.md      # single source; engine/dev guard, NOT skill surface
  token_layer[]   : per-file stable identifiers that must survive a rewrite UNCHANGED. Three classes:
                    gate_outcomes = { PASS, RISK-ACCEPTED, HARD-STOP, ESCALATE, auto-resolved }   (fixed vocab)
                    named_codes   = backticked snake_case reject/error codes (unguarded_high_risk_auto ·
                                    metric_gate · frozen_scope · unescalated_security_note · already_locked ·
                                    setup_unlocked · split_required · no_evidence · …)   (RULE-extracted, reviewable)
                    defined_vocab = curated method terms whose loss changes meaning
                    each entry { token, file } — S1 asserts the token is still present IN that file
  invariants[]    : { id, file, anchors[], neg_anchors[] } — LEAN (one per safety negative + the conjunctions).
                    anchors[0] is the PRIMARY anchor (locates the window); the rest must co-occur within it.
                    seed (from task-1 FROZEN negative_keep_list + the gate outcomes; anchors[0]=PRIMARY;
                    ALL 7 verified GREEN at freeze under the list-item window — window line-counts in parens):
                      security-always-hardstop  { run.md · anchors[security, HARD-STOP, always] · neg[unless, except, waive, RISK-ACCEPTED] } (3L)
                      never-auto-pass-security  { run.md · anchors[auto-pass, security, never] · neg[unless, except] } (3L)
                      never-weaken-test         { SKILL.md · anchors[weaken, never, test] · neg[unless, except] } (2L)
                      never-self-fold           { fold.md · anchors[self-fold, never] } (2L)
                      never-prompt-field        { phases/1-specify.md · anchors[Never:] }   (the <prompt>-skeleton slot) (3L)
                      auto-pass-conjunction     { run.md · anchors[Auto-PASS, test, coverage, weaken, contract] } (2L)
                      unguarded-high-risk       { run.md · anchors[risk: high, conservative, refus] } (9L)
                    S2 asserts the anchors co-occur in the window; S3 asserts no neg_anchor sits in the window.
                    (auto-pass-conjunction + unguarded-high-risk are EXTRA invariants beyond the 5 negatives — they
                     guard the auto-gate conjunction + the high-risk guard, which token presence alone can't.)
  window          : S1 token-presence = per-FILE (a token present anywhere in its file = preserved).
                    S2 anchor-co-occurrence + S3 neg-anchor = ANCHOR-LOCAL — the smallest natural unit holding the
                    PRIMARY anchor: a markdown LIST-ITEM is its own unit, else the blank-line PARAGRAPH. Tighter
                    than a paragraph BY NECESSITY, proven by the data: run.md's auto-gate bullets are CONTIGUOUS —
                    bullet 2 holds "security…HARD-STOP, always", bullet 3 legitimately lists `RISK-ACCEPTED`; a
                    paragraph window leaks RISK-ACCEPTED into the security rule → S3 false-positives at freeze. The
                    list-item window keeps them apart. Verified: all 7 invariants GREEN at freeze (windows 2–9 lines).
  cede_list       : NAMED, never hidden — the gate does NOT prove these (human review + indicative eval do):
                    inversion-around-surviving-anchors (added exception / negation / scope-narrowing) ·
                    positivity / scope JUDGMENT · meaning beyond the anchors.
  coverage        : every negative_keep_list item -> ≥1 invariant (freeze-time `invariant_uncovered` check).
  reject_codes    : verbatim_diff · model_judged_gate · unit_dropped · unit_relocated · invariant_broken ·
                    exception_introduced · invariant_uncovered · overclaim_sufficient

GATE  python3 add-method/tooling/semantic_inventory.py [--inventory <path>] [--surface <glob>...] [--extract]
  reads   : SEMANTIC_INVENTORY.md (token_layer + invariants) + the surface files
  checks  : DETERMINISTIC diff — S1 token-present-in-file · S2 invariant-anchors-co-occur · S3 no-negative-anchor
            + freeze-time: invariant_uncovered (coverage) · overclaim_sufficient (cede-list present in the doc)
  --extract: re-derive token_layer from the surface (seeding / drift aid) — prints the snapshot; never auto-freezes
  proves  : NECESSARY preservation (nothing dropped / renamed / relocated; anchors intact; no listed exception).
            NOT sufficient — the cede_list goes to review + indicative eval (named, never silently claimed proven).
  exits   : 0 = no findings · 1 = findings (prints file · code · unit) · 2 = broken inventory / unreadable
            surface (LOUD, named error — never a false green)
  refuses : a verbatim-text or model-judged check -> verbatim_diff / model_judged_gate (either mis-gates a good reword)
Schema  : no DB — reads markdown. Surface = canonical add-method/skill/add/ (18) + docs/appendix-b-prompts.md (19);
          the _bundled & .claude mirrors are byte-identical (test_bundle_parity/test_tree_parity), so canonical
          suffices. SEMANTIC_INVENTORY.md + semantic_inventory.py are tooling/ guards (like wording_lint.py /
          test_xml_convention.py) — NOT mirrored, no parity copy.
```

Status: FROZEN @ v1 — approved by Tin Dang, 2026-06-06 (one-approval front; human chose "Freeze @ v1" at the contract seam)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

> **Bundle least-sure flag (read this at the freeze):** the approval object here is the FROZEN INVENTORY CONTENTS
> (the token snapshot + the 7 seeded invariants + the cede-list), not the tool shape. Two are most likely wrong —
> **[spec] COMPLETENESS:** a preservation-critical proposition I did NOT anchor (an omitted invariant silently
> ships a weakenable rule). I seeded from your task-1 `negative_keep_list` + the gate outcomes and the coverage
> check enforces that mapping — but YOUR eyes on the invariant list at the seam is the real safety check; and
> **[contract] NECESSARY-not-SUFFICIENT:** if you wanted the gate to block EVERY meaning change it provably can't
> (an inversion around surviving anchors is model-judgment, ceded to review + indicative eval). This also means
> the milestone's "semantics provably preserved" = this gate (necessary) + review + indicative eval (the rest) —
> I'll record that operational definition as a milestone shared-decision once you ratify it here. Everything else
> (the 8 reject codes · the three checks · exit codes · the separate-tool seam) I'm confident on.
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of check branches (S1 · S2 · S3 · freeze-time invariant_uncovered + overclaim_sufficient ·
  design-for-failure · the two refused-by-design codes). Small, deterministic surface — every code exercised.
Plan (one test per §2 scenario, asserting behavior not internals):
  - test_inventory_single_source: gate loads units/invariants FROM the doc + prints the inventory path
  - test_extraction_reproducible: `--extract` reproduces the frozen per-file token set; a rule-found unit absent
    from the snapshot is reported as drift (not silently swallowed)
  - test_unit_dropped: a frozen token removed from its file -> unit_dropped, exit 1
  - test_unit_relocated: a frozen token moved to another file -> unit_relocated (present, wrong file)
  - test_clean_reword_no_falsepositive: prose around a surviving token reworded -> zero findings, exit 0  (prime invariant)
  - test_invariant_broken: a dropped conjunct / a removed "always" -> invariant_broken with the id
  - test_exception_introduced: a neg-anchor ({unless…}) inside the security-always window -> exception_introduced
  - test_inversion_around_anchors_is_ceded: a scope-narrowing rewrite that KEEPS every anchor -> gate passes (green)
    BY DESIGN; assert the doc + report NAME the cede (necessary-not-sufficient boundary is explicit, not a silent miss)
  - test_verbatim_diff_refused: CHECK_KINDS exposes no text/verbatim kind; verbatim_diff is reject-by-design
  - test_model_judged_refused: no model-in-loop check exists; model_judged_gate is reject-by-design
  - test_invariant_uncovered_at_freeze: a negative_keep_list item with no invariant -> invariant_uncovered (freeze refused)
  - test_overclaim_refused: a doc claiming "provably preserved" with no cede-list -> overclaim_sufficient
  - test_broken_inventory_exits_2: a missing / malformed inventory -> exit 2, named error (no false green)
  - test_live_surface_green: the frozen inventory over the live surface -> 0 findings, exit 0
  - test_coverage_negative_keep_list: every task-1 negative_keep_list item maps to ≥1 frozen invariant (real coverage)

Tests live in: `add-method/tooling/test_semantic_inventory.py` (beside `wording_lint.py` / `test_xml_convention.py` —
  engine/dev guards, NOT the 3-mirror skill surface, so no parity copy). MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the gate must be GREEN at freeze AND fail only on a real regression.
  S2 anchor match = lenient (favours green on a reword); S3 neg-anchor match = strict word-boundary
  (so "except" never fires on "exception" — a false-positive on reinforcing prose). The window is the
  list-item (verified to keep run.md's RISK-ACCEPTED out of the security rule's window).
Code lives in: `add-method/tooling/` (NOT `./src/` — engine/dev guard beside `wording_lint.py`, not mirrored).
Constraints: stdlib only (argparse/re/dataclasses/pathlib) — no new dependency; reuses
  `wording_lint.surface_files()` + `.load_rubric().negative_keep` (single source for the 19-file surface
  and the 5 frozen negatives — no duplication). §3 contract honored; no test weakened.

Built:
- `SEMANTIC_INVENTORY.md` — FROZEN @ v1: token_layer (11 files · 5 gate-outcomes + 18 named codes) ·
  invariants (7, all green at freeze, list-item windows 2–9L) · coverage (5 negatives → invariants) ·
  cede_list (3 named cedes — satisfies the overclaim self-check).
- `semantic_inventory.py` — S1 (per-file token presence, case-sensitive) · S2 (anchor co-occur, lenient) ·
  S3 (neg-anchor absent, strict boundary) · freeze-time invariant_uncovered + overclaim_sufficient ·
  CHECK_KINDS = diff-only (verbatim/model refused structurally) · `--extract` drift aid · `--surface`
  scoped spot-check · exits 0/1/2 (loud on a broken inventory/unreadable surface).
- `test_semantic_inventory.py` — 20 tests (15 §2 scenarios + spot-check-scope regression + window-local +
  surface-contract + 2 load tests); red→green confirmed.

Deviation (disclosed, additive — NOT a contract/test weakening): added `test_spot_check_scopes_to_named_files`
  beyond the §4 plan after a self-found bug — `--surface <one file>` was flagging every OTHER file's tokens as
  unit_dropped; fixed with `_scope_to` (spot-check judges only the named files' units). Full mode unaffected.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_semantic_inventory` 20/20; full method suite 508/508; `add.py check` 190/0; `audit` clean (44)
- [x] coverage did not decrease — net +20 tests; every check branch (S1·S2·S3·coverage·cede·design-for-failure·2 refused codes) exercised
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; one ADDITIVE test added (spot-check-scope, disclosed §5) — never a weakening
- [x] concurrency / timing of the risky operation is safe — pure-function gate, no IO concurrency; reads guarded (exit 2 on failure)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; reads local markdown; no eval/network/secrets
- [x] layering & dependencies follow CONVENTIONS.md — guard in `tooling/` beside `wording_lint.py`; reuses its surface+negatives (single source); not mirrored
- [x] a person reviewed and approved the change — **risk:high · conservative → human gate (this is the escalation)**; Tin Dang chose PASS at the verify seam, 2026-06-06

### DISCLOSED (surfaced for your gate — not silent)
1. **Self-found bug, fixed + pinned (additive):** `--surface <one file>` flagged every OTHER file's tokens as
   `unit_dropped` (46 false findings). Root cause: spot-check checked ALL token_layer entries against a single
   file. Fixed with `_scope_to` (spot-check judges only the named files' units) + `test_spot_check_scopes_to_named_files`.
   Full mode (the rewrite-tasks' gate) was never affected. NO contract change, NO test weakened.
2. **Hygiene fix to a committed sibling (wording-rubric):** its §3 freeze stamp predated the audit's
   `FROZEN @ vN — approved by <name>` convention (latent `unstamped_freeze`, surfaced only post-gate). I aligned
   the stamp (preserving the v1.1 note); `audit` is now clean (44). The gate PASS itself is unchanged. NO security impact.
3. **Live end-to-end proof:** injecting "unless RISK-ACCEPTED" into run.md's security rule → the gate fires
   `exception_introduced` on both security invariants (not just a unit-test fixture). The gate catches a real inversion-via-exception.

### NOTE (gate reach — within the necessary bound, it is stronger than "anchors only")
A WRONGFUL POSITIVIZATION of a protected negative is caught, not ceded: rewording
`never auto-pass a security finding` → `always escalate a security finding` deletes the anchor tokens
`auto-pass` + `never` from the window, so S2 fires `invariant_broken` on never-auto-pass-security. The
ceded class (cede_list) is narrower than "any meaning change" — it is specifically an inversion that
KEEPS every anchor token. Drop or rephrase-away an anchor and the gate sees it.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-06

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->

- [ADD · folded] the gate is near-silent on the surface files that carry NO frozen unit — most phase guides hold
  zero token_layer entries + zero invariants, so a GREEN there means "nothing was checked", not "meaning preserved";
  rewrite-guides must inherit this as an explicit input — on those files review + wording-lint + the indicative
  behavioral eval are the ENTIRE safety net, the semantic gate adds nothing (evidence: SEMANTIC_INVENTORY.md
  token_layer names 11 files; the surface is 19 — the ~8 unnamed files have no semantic-gate coverage by construction).
