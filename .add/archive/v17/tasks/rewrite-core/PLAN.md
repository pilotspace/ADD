# TASK: Rewrite SKILL.md + 9 engine docs to the frozen rubric + 2 structural wins

slug: rewrite-core · created: 2026-06-06 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: rewrite SKILL.md + the 9 engine docs (the 10-file CORE touch-boundary) to the FROZEN
  WORDING_RUBRIC, plus the 2 structural wins — all behind both gates (wording-lint + semantic-inventory),
  with the run.md ENGINE_FILES guard update carried as a pre-declared, human-ratified change-request.
Framings weighed: ONE task, staged commits by risk (chosen — milestone froze rewrite-core as one front;
  re-decomposing into wording-pass + structural-pass reopens the decomposition for no gain) · two sub-tasks
  (rejected) · one mega-commit (rejected — couples the idiom-retirement, the trim, and the guard edit so a
  single gate failure can't localize).

Must:
  - REWRITE the 10 CORE files to the frozen rubric (phrasing only, never a rule): retire idioms per
    idiom_map · positivize ordinary negatives WHERE a clean positive exists · dial aggressive emphasis
    (CRITICAL / NON-NEGOTIABLE) down to plain imperative, reserving strong emphasis for ≤3 true hard-stops ·
    add explicit SCOPE qualifiers to phase-wide rules. The 10 files: SKILL.md · adopt.md · deltas.md ·
    fold.md · intake.md · report-template.md · run.md · scope.md · setup-review.md · streams.md.
  - HONOR the keep_list (reword AROUND load-bearing terms, never rename — F3 guards) and the
    negative_keep_list (the 5 protected negatives STAY, each keeps its `# why:`).
  - PROMOTE idioms SURFACE-WIDE: flip `[mapped]`→`[enforced]` in WORDING_RUBRIC.md in the SAME commit that
    removes the idiom's LAST occurrence from the WHOLE surface (checked via wording-lint's surface scan, not
    just the 10 core files). rewrite-core flips ONLY `blast radius` (streams.md-only); it removes
    `rubber-stamp` from streams.md but LEAVES it `[mapped]` (still in phases/1-specify.md + appendix-b, which
    rewrite-guides owns) — F1 checks only `enforced`, so the lint stays green.
  - STRUCTURAL WIN 1 — trim ~290 words of always-loaded summary from SKILL.md: remove only DUPLICATIVE
    on-demand content (the dynamic-run / parallel-streams / flow-footnote prose that run.md · streams.md
    already carry on demand), PRESERVING every frozen SKILL.md token (`auto-resolved` · PASS · RISK-ACCEPTED
    · HARD-STOP) AND the `never-weaken-test` invariant window AND every keep_list term. (semantic-inventory
    enforces the tokens + invariant; the conservative verify gate shows the diff for the meaning the gate cedes.)
  - STRUCTURAL WIN 2 — move run.md's `## The evidence auto-gate` + `## The autonomy dial` prose INTO
    `<constraints>` blocks. v16's 5-tag closed vocabulary is honored — wrap in the EXISTING `<constraints>`
    tag, never add or split a tag. This carries the ENGINE_FILES change-request (Must below).
  - CARRY the ENGINE_FILES change-request, pre-declared in §3 + human-ratified at the freeze + ISOLATED in
    its own commit: in test_xml_convention.py remove `## The evidence auto-gate` and `## The autonomy dial`
    from run.md's `narrative` tuple (they migrate from narrative-untagged to constraints-tagged). This is the
    ONLY legitimate edit to a frozen guard — never a silent test edit during build.
  - KEEP BOTH GATES GREEN after every commit: semantic-inventory (no unit dropped / renamed / relocated · no
    invariant broken · no exception introduced) AND wording-lint (F1–F4). Mirror PARITY: every `skill/add/`
    edit propagates to `_bundled/` + `.claude/skills/add` byte-identical IN THE SAME COMMIT.
  - At task close: whole suite + `add.py check` + `add.py audit` green over the rewritten surface.

Reject:
  - a reword that changes a RULE's meaning (drops / renames / relocates a unit · breaks an invariant ·
    introduces an exception) -> "semantics_changed"  (route as a change-request to SPECIFY, never a wording edit)
  - positivizing a negative_keep_list item -> "protected_negative_removed"  (a guardrail weakened — review-caught;
    semantic-inventory S2 also fires on the positivization that drops the anchors)
  - renaming a keep_list term instead of rewording around it -> "keep_term_renamed"  (F3 / global-rename break)
  - editing test_xml_convention.py ENGINE_FILES WITHOUT the pre-declared, ratified change-request, or folding it
    into a non-isolated commit -> "silent_guard_edit"  (the cardinal method sin — indistinguishable from cheating)
  - removing an idiom's last surface occurrence but NOT flipping `[mapped]`→`[enforced]` (or flipping one still
    present elsewhere) -> "idiom_unretired"  (promotion protocol broken; the lint goes trivially-green or red)
  - a `skill/add/` edit not mirrored to `_bundled/` + `.claude/` in the same commit -> "parity_drift"
  - adding or splitting an XML tag beyond the frozen 5-tag vocabulary -> "tag_vocab_violated"  (v16 reopened)

After:
  - The 10 core files carry the rubric (idioms retired per plan · emphasis dialed to ≤3 hard-stops · clean
    positives in · scope qualifiers added); keep_list + the 5 negatives intact; `blast radius` is `[enforced]`,
    `rubber-stamp` still `[mapped]` for rewrite-guides. SKILL.md is ~290W lighter with every frozen token +
    the never-weaken-test invariant preserved. run.md's auto-gate + autonomy-dial sit in `<constraints>` with
    the ratified ENGINE_FILES delta. Both gates + parity + the whole suite + audit are green. rewrite-guides
    inherits a clean, half-rewritten surface.

Assumptions — least-sure first:
  ⚠ THE SKILL.md TRIM is the bundle's lead flag — least sure because it is EXACTLY the necessary-not-sufficient
    class the semantic gate CEDES: a load-bearing sentence can be cut while every anchor token survives and the
    gate stays GREEN. If wrong: an agent loses a behavioral cue that was never a frozen token (e.g. the
    show-before-ask / never-pre-stamp-a-seam guidance, the depth-by-stage dial) and the method silently degrades.
    Mitigated by (a) the gate enforcing the frozen tokens + the never-weaken-test invariant, and (b) the
    conservative verify gate SHOWING the actual trim diff for human review — that human read is the real protection,
    not the gate. The exact lines to cut are pinned in §3, not guessed here.
  ⚠ THE ENGINE_FILES CHANGE-REQUEST is the second flag — least sure because editing a frozen guard is normally the
    cardinal method sin; it is legitimate ONLY as a pre-declared, exact, human-ratified delta isolated in its own
    commit. If it instead surfaces during build as a silent test edit, it is indistinguishable from cheating and
    breaks the method's integrity. Mitigated by declaring the exact two-line tuple deletion in §3 now and isolating it.
  - [ ] idiom promotion is SURFACE-WIDE (flip when the idiom leaves the whole surface) — rewrite-core flips only
        `blast radius`; `rubber-stamp` stays `[mapped]`. This wants ratification as a MILESTONE shared-decision
        (it binds rewrite-guides + clarity-greenstate), proposed at the freeze — never pre-written.
  - [ ] the 10-file touch-boundary is exact: SKILL.md + the 9 engine docs above (setup-review.md is the 9th);
        rewrite-guides owns the 8 phase guides + appendix-b. Confirmed against wording_lint.surface_files() (19).
  - [ ] positivization scope: positivize ordinary negatives with a clean positive; KEEP every hard floor/ceiling
        and security/safety boundary as a negative with a `# why:` (the rubric governs; research-grounded).

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
# --- one per Must ---
Scenario: the rewrite lands and both gates stay green
  Given the 10 core files reworded to the frozen rubric (idioms retired, ordinary negatives positivized,
        emphasis dialed to ≤3 hard-stops, scope qualifiers added)
  When semantic_inventory.py and wording_lint.py run over the surface
  Then both exit 0 (no unit dropped/renamed/relocated, no invariant broken, no exception introduced; F1–F4 green)
  And the method semantics (flow, gates, autonomy, CLI behavior) are unchanged

Scenario: load-bearing vocabulary survives
  Given the keep_list terms and the 5 negative_keep_list negatives
  When the rewrite completes
  Then F3 is green (every keep term still present) and each protected negative is still present with its `# why:`
  And no keep_list term was renamed

Scenario: an idiom is promoted only when it leaves the WHOLE surface
  Given `blast radius` lives only in streams.md and `rubber-stamp` in streams.md + two guide files
  When rewrite-core rewords streams.md
  Then `blast radius` is removed AND flipped `[mapped]`→`[enforced]` in the same commit (gone surface-wide)
  And `rubber-stamp` is removed from streams.md but stays `[mapped]` (still in guide files) — wording-lint green

Scenario: SKILL.md trim preserves every frozen unit
  Given ~290 words of duplicative always-loaded summary in SKILL.md
  When the trim removes only on-demand-duplicated prose
  Then SKILL.md still contains auto-resolved · PASS · RISK-ACCEPTED · HARD-STOP and the never-weaken-test window
  And semantic_inventory.py exits 0 for SKILL.md      # the gate proves the tokens/invariant survived
  And the actual trim diff is shown at the verify gate for human review   # the ceded meaning is human-checked

Scenario: run.md auto-gate + autonomy-dial move into <constraints> within the frozen tag vocab
  Given the prose sections `## The evidence auto-gate` and `## The autonomy dial`
  When they are wrapped in the EXISTING <constraints> tag (no tag added or split)
  And test_xml_convention.py's run.md narrative tuple is updated by the ratified change-request
  Then test_xml_convention.py is green (those sections may now carry <constraints>; vocab still the 5-tag set)
  And semantic_inventory.py is still green (the auto-gate tokens/invariants survived the move)

Scenario: the frozen-guard edit is pre-declared and isolated
  Given the ENGINE_FILES change-request is specified verbatim in §3 and approved at the freeze
  When it is applied
  Then it lands in its OWN commit (only the two narrative-tuple lines removed), separate from the prose rewrites
  And the build never edits a frozen guard outside that ratified, isolated commit

Scenario: parity holds across the rewrite
  Given any edit to a `skill/add/` file
  When the commit is made
  Then `_bundled/` and `.claude/skills/add` are byte-identical (test_bundle_parity + test_tree_parity green)

Scenario: the surface is clean at task close
  Given every commit landed
  When the whole suite + `add.py check` + `add.py audit` run
  Then all are green over the rewritten surface

# --- one per Reject ---
Scenario: a meaning-changing reword is refused
  Given a reword that drops/renames/relocates a unit, breaks an invariant, or adds an exception
  When a gate or human review runs
  Then it is rejected as "semantics_changed" and routed back to SPECIFY as a change-request
  And no frozen contract or test is weakened to absorb it

Scenario: positivizing a protected negative is refused
  Given a rewrite that turns "never auto-pass a security finding" into "always escalate…"
  When semantic_inventory.py runs (anchors auto-pass/never dropped) and a human reviews
  Then it is flagged "protected_negative_removed" (S2 invariant_broken) and reverted

Scenario: renaming a keep-list term is refused
  Given a rewrite that renames a keep_list term globally
  When wording_lint.py runs
  Then F3 fails (keep term missing) — reported as "keep_term_renamed"

Scenario: a silent guard edit is refused
  Given a change to ENGINE_FILES made during build without the ratified §3 change-request, or folded into a prose commit
  When the change is reviewed
  Then it is rejected as "silent_guard_edit" (a frozen guard was edited outside the one ratified, isolated path)

Scenario: an un-retired idiom is caught
  Given `blast radius` removed from streams.md but NOT flipped to `[enforced]`
  When clarity-greenstate's exit check runs (enforced_banned == full idiom_map)
  Then it fails — reported as "idiom_unretired" (the promotion protocol did not run)

Scenario: parity drift is caught
  Given a `skill/add/` edit not propagated to `_bundled/`/`.claude/`
  When the suite runs
  Then test_bundle_parity / test_tree_parity fails — reported as "parity_drift"

Scenario: a tag-vocabulary violation is caught
  Given a rewrite that introduces a 6th XML tag or splits an existing one
  When test_xml_convention.py runs
  Then the vocab check fails — reported as "tag_vocab_violated"
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
TOUCH-BOUNDARY  the run may edit ONLY these 10 CORE files (+ their _bundled/ + .claude/ mirrors) and the
                ONE ratified guard below. Everything else is out of bounds.
  skill/add/:  SKILL.md · adopt.md · deltas.md · fold.md · intake.md · report-template.md ·
               run.md · scope.md · setup-review.md · streams.md
  OUT (rewrite-guides owns): phases/0-setup … 7-observe (8) + docs/appendix-b-prompts.md
  Verified against wording_lint.surface_files() = 19 (10 core + 8 guides + appendix-b).

RUBRIC  add-method/tooling/WORDING_RUBRIC.md   # FROZEN — read-only EXCEPT the one promotion line below
  governs: idiom_map · keep_list · negative_keep_list · emphasis_tokens · scope_qualifier_rule
  rewrite-core writes EXACTLY ONE rubric change: in the commit that removes `blast radius` from streams.md,
    flip it `[mapped]`→`[enforced]` in idiom_map AND add it to enforced_banned. No other rubric edit.
    `rubber-stamp` is removed from streams.md but STAYS `[mapped]` (still in phases/1-specify.md + appendix-b,
    rewrite-guides' files). run.md ALSO carries the SPACE-form "rubber stamp" (L35, L43) — rewrite-core
    rewords it as part of run.md's wording pass (it is the same retired idiom in prose), but this does NOT
    promote `rubber-stamp`: the idiom string is the hyphen form and F1's matcher is hyphen-bound, so the
    eventual enforced fence is hyphen-ONLY. NOTE FOR rewrite-guides: when it flips `rubber-stamp`→`[enforced]`,
    F1 will not catch a surviving SPACE-form "rubber stamp" — clear both forms surface-wide before promoting.

WORDING PASS (the 10 files, phrasing only — semantics owned by the gates, never changed here)
  - retire idiom_map idioms found in-file · positivize ordinary negatives with a clean positive · dial
    CRITICAL / NON-NEGOTIABLE emphasis down to plain imperative (strong emphasis reserved for ≤3 hard-stops) ·
    add scope qualifiers to phase-wide rules.
  - keep_list terms reworded AROUND, never renamed (F3). The 5 negative_keep_list negatives STAY with `# why:`.

STRUCTURAL WIN 1 — SKILL.md trim (~290 W out)
  TARGET (compress to brief pointers): `## The dynamic run (v6–v7)` + `## Parallel streams …` (both restate
    run.md / streams.md, which the agent loads on demand) + the flow-table †/‡ footnotes. Each compressed
    section KEEPS a one-line pointer so the agent still knows to load run.md / streams.md.
  PROTECTED — never cut: the YAML frontmatter `description` · `## Always start here` · the
    `## Non-negotiable rules` <constraints> block VERBATIM · ≥1 `auto-resolved` occurrence (the only one is in
    the ‡ footnote — keep it) · PASS / RISK-ACCEPTED / HARD-STOP · every keep_list term.
  PROOF: semantic_inventory.py exit 0 for SKILL.md (S1 tokens + never-weaken-test invariant survive). The
    EXACT trim diff is shown at the conservative verify gate for human review (the ceded-meaning check).

STRUCTURAL WIN 2 — run.md prose → <constraints>
  WRAP each of `## The evidence auto-gate` and `## The autonomy dial` bodies in its OWN <constraints>
    block — TWO blocks, reusing the EXISTING tag NAME (the sections are NON-CONTIGUOUS: `## Emitting
    deltas` sits between them and is left untouched). v16 honored: NO tag added or split (the closed
    5-tag vocabulary is unchanged). Tokens unchanged: auto-resolved · PASS · RISK-ACCEPTED · HARD-STOP ·
    ESCALATE · unguarded_high_risk_auto all stay in run.md.
  BUILD-SAFETY (the densest invariant section): `## The evidence auto-gate` carries the
    `never auto-pass a security finding` protected negative + the Auto-PASS conjunction + the
    RISK-ACCEPTED-beside-the-security-rule list-item adjacency. When wrapping/rewording, PRESERVE the
    three separate list-items (merging them lets RISK-ACCEPTED leak into the security window → S3
    exception_introduced), keep `never auto-passed` as a negative (positivizing → S2 invariant_broken),
    keep the Auto-PASS conjunction inside ONE list-item (reflowing across items → S2). The gates CATCH
    all three (the build halts, never ships) — preserve them to avoid a confusing build-loop RED, and
    NEVER resolve such a RED by touching a gate.

RATIFIED GUARD CHANGE-REQUEST  (the ONLY edit to a frozen guard; lands in its OWN isolated commit)
  CR-1  test_xml_convention.py — ENGINE_FILES["run.md"]["narrative"]: delete these two entries verbatim
          "## The evidence auto-gate",
          "## The autonomy dial",
        (they migrate narrative-untagged → constraints-tagged via Win 2). Net: 2 lines removed; run.md's
        "tags": {"constraints"} is UNCHANGED (already satisfied). No other guard, matcher, or test is touched.

GATES — the run's standing invariant, GREEN after EVERY commit
  semantic_inventory.py exit 0 · wording_lint.py exit 0 (F1–F4) · test_xml_convention.py green ·
  test_bundle_parity + test_tree_parity green (every skill/add edit mirrored to _bundled/ + .claude IN-COMMIT) ·
  python3 .add/tooling/add.py check green.

COMMIT STAGING (by risk, so one gate failure localizes)
  per-file (or small group) wording rewrites → SKILL.md trim → run.md restructure → CR-1 (isolated). Each commit
  carries its mirror-parity propagation. blast-radius promotion rides the streams.md commit.

reject_codes: semantics_changed · protected_negative_removed · keep_term_renamed · silent_guard_edit ·
              idiom_unretired · parity_drift · tag_vocab_violated
```

Status: FROZEN @ v1 — approved by Tin Dang · date: 2026-06-06   <!-- trim target + CR-1 ratified; the surface-wide promotion RULE was HELD (see flag below). Changing a frozen contract = change request back to SPECIFY. -->

> **Bundle least-sure flag (read at the freeze):**
> **[spec] THE SKILL.md TRIM** is most likely wrong — it is the necessary-not-sufficient class the semantic gate
> CEDES: a load-bearing sentence can be cut while every anchor token survives and the gate stays green. The gate
> proves the tokens + never-weaken-test invariant survive; YOUR read of the actual trim diff at the verify gate is
> the real protection. (That is why this task is `conservative` — the verify gate stays human.)
> **[contract] THE ENGINE_FILES CR-1** is the second — editing a frozen guard is normally the cardinal method sin;
> it is legitimate ONLY as this pre-declared, exact, isolated, human-ratified delta. Approve CR-1 here and it
> rides its own commit; if it ever appears as a silent test edit during build, that is a HARD-STOP.
> **Also ratify (milestone shared-decision):** idiom promotion is SURFACE-WIDE — flip `[mapped]`→`[enforced]`
> when an idiom leaves the WHOLE surface. rewrite-core flips `blast radius`; `rubber-stamp` stays `[mapped]` for
> rewrite-guides. — **HELD at the 2026-06-06 freeze** (not ratified): this rewrite-core contract still flips
> `blast radius` (a per-task action inside the frozen shape), but the milestone-level RULE that binds
> rewrite-guides + clarity-greenstate is deferred. Logged as PENDING in MILESTONE.md; re-raise before rewrite-guides.
> **Build heads-up (not a decision — context for your verify read):** the highest-PROBABILITY build friction is
> Win 2 reworking `## The evidence auto-gate`, the densest invariant section (security-hardstop · Auto-PASS
> conjunction · the RISK-ACCEPTED-beside-security list adjacency you flagged at the semantic-inventory freeze).
> A wrong edit there trips a gate and HALTS the build — it never ships — so the worst case is loop friction, not
> a silent drift. §3 BUILD-SAFETY + §5 pin exactly what to preserve.
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of rewrite-core's NEW deliverables (the 2 structural wins + the blast-radius promotion).
  A pure reword keeps the existing fences green BY DESIGN, so the genuine RED lives only in the structural
  wins + the promotion. Each Reject scenario maps to an EXISTING gate (cited below, not rewritten) — those are
  the standing regression net that turns RED if a rewrite breaks meaning / renames a term / drifts a mirror.

NEW red suite — `add-method/tooling/test_rewrite_core.py` (RED now, green after build; permanent guards after):
  - test_runmd_autogate_in_constraints:   run.md `## The evidence auto-gate` body sits inside a <constraints> block
  - test_runmd_autonomy_dial_in_constraints: run.md `## The autonomy dial` body sits inside a <constraints> block
  - test_blast_radius_enforced_and_absent: `blast radius` ∈ enforced_banned AND absent from the whole surface
  - test_skill_summary_trimmed:            `## The dynamic run (v6–v7)` + `## Parallel streams` headers absent from
                                           SKILL.md AND `auto-resolved` still present (trim landed, token preserved)
  All four assert behavior (file state), not internals. They run RED now (rewrite not yet done).

Scenario → covering test (Reject scenarios ride EXISTING gates — the regression net):
  - rewrite lands / both gates green        -> semantic_inventory.py + wording_lint.py (existing) + the 4 new tests
  - load-bearing vocabulary survives        -> wording_lint F3 (existing)
  - idiom promoted only surface-wide        -> test_blast_radius_enforced_and_absent (new) + wording_lint F1 (existing)
  - SKILL.md trim preserves frozen units    -> test_skill_summary_trimmed (new) + semantic_inventory S1 (existing)
  - run.md sections → <constraints>         -> test_runmd_*_in_constraints (new) + test_xml_convention (post-CR-1)
  - frozen-guard edit pre-declared/isolated -> git review at verify (commit isolation) — process check, not a unit test
  - parity holds                            -> test_bundle_parity + test_tree_parity (existing)
  - clean at task close                     -> add.py check + add.py audit (existing)
  - semantics_changed                       -> semantic_inventory S1/S2/S3 (existing) + human review (the ceded class)
  - protected_negative_removed              -> semantic_inventory S2 (existing) + human review
  - keep_term_renamed                       -> wording_lint F3 (existing)
  - silent_guard_edit                       -> git review at verify (existing-guard integrity) — process check
  - idiom_unretired                         -> test_blast_radius_enforced_and_absent (new); clarity-greenstate's full check
  - parity_drift                            -> test_bundle_parity + test_tree_parity (existing)
  - tag_vocab_violated                      -> test_xml_convention vocab subset (existing)

Tests live in: `test_rewrite_core.py` `add-method/tooling/` (engine/dev guard beside wording_lint.py /
  semantic_inventory.py — NOT the 3-mirror skill surface, so no parity copy). MUST run red before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): Win 2 reworks `## The evidence auto-gate` — the densest invariant section
  on the surface. Preserve its THREE separate list-items, keep `never auto-passed` as a protected negative,
  and keep the Auto-PASS conjunction inside ONE list-item (see §3 BUILD-SAFETY). A gate RED here is a
  meaning-drift signal — fix the prose, NEVER the gate. Run both gates + parity after EVERY commit.
Code lives in: the 10 core surface files + their `_bundled/` + `.claude/` mirrors (no `src/`); the one
  ratified guard edit (CR-1) lands isolated. Stage by risk per §3 COMMIT STAGING.
Constraints: do NOT weaken a test or edit the frozen contract; the ONLY frozen-guard edit is CR-1, isolated;
  mirror every skill/add edit in-commit; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

Build = 5 commits (1 was a documented no-op): c8e3754 streams idioms + `blast radius` promotion ·
[no-op: 7 core files already literal/positive — no manufactured rewrites] · c463a33 SKILL.md trim ·
64ebe30 CR-1 (isolated) · 5fbb21d run.md Win 2 + idiom reword.

Part one — evidence:
- [x] all tests pass — whole tooling suite 512 OK · test_rewrite_core 4/4 · wording_lint 0 · semantic_inventory 0 · test_xml_convention OK · bundle+tree parity OK · add.py check 194 passed/0 failed (4 pre-existing legacy warnings, not this task) · add.py audit clean (45 tasks)
- [x] coverage did not decrease — ADDED test_rewrite_core.py (4 tests); weakened/deleted nothing
- [~] no test or contract was altered during build — the FROZEN §3 contract is untouched; the ONLY guard edit is the ratified CR-1 (test_xml_convention.py, isolated commit 64ebe30); the ONLY rubric edit is the contract-authorized `blast radius` promotion (WORDING_RUBRIC.md). No unauthorized/silent test weakening. ⚠ the human confirms CR-1 was legitimate (it was pre-declared in §3 + ratified at the freeze).

Part two — blind-spots:
- concurrency / timing — N/A: a prose/docs rewrite, no runtime path. The architectural invariant here is 3-mirror parity (skill/add ↔ _bundled ↔ .claude byte-identical) — GREEN.
- ⚠ SECURITY (escalates to human, by design): this rewrite touches the method's SAFETY-rule prose — run.md's evidence-auto-gate / security-always-escalates / never-auto-pass-security, and SKILL.md's never-weaken-test. The DETERMINISTIC gate proves every protected negative + invariant survived (semantic_inventory 0 findings: S1 tokens present, S2 anchors co-occur, S3 no exception introduced). But the CEDED class — an INVERSION around surviving anchors (an added "unless"/negation/scope-narrowing that keeps every anchor word) — is gate-blind and needs the HUMAN's read of the actual diff. No weakened guard or removed invariant was DETECTED; this is an escalation-for-review, not a HARD-STOP finding. The SKILL.md trim is the highest-consequence slice (the necessary-not-sufficient class) — review its diff first.
- architecture / layering — N/A (no code layers changed); CONVENTIONS.md mirror-parity rule honored (parity green).

### GATE RECORD
Outcome: PASS   <!-- human-led conservative gate; recorded only after the human answered -->
Reviewed by: Tin Dang · date: 2026-06-06
Human read the SKILL.md trim diff (the necessary-not-sufficient / ceded class) and the run.md Win-2 diff; judged the one dropped safety sentence ("never edits a frozen contract / never auto-passes a security finding") and the ‡ footnote clause to be duplicated in Non-negotiable rules 3+4 + run.md (no unique loss). PASS also ratifies the two resolved execution calls (promotion=tag-flip-only · CR-1-before-Win-2) and the 180-vs-290 word variance. No security HARD-STOP: the escalated CEDED-class review found no inversion.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the two FROZEN freeze gates are the live monitors — `wording_lint`
  (F1–F4) and `semantic_inventory` (S1–S3) must stay 0-findings as rewrite-guides + clarity-greenstate
  touch the rest of the surface; a regression in either is the alert (the §2 scenarios re-run on every commit).
Spec delta for the next loop: RE-RAISE the HELD surface-wide idiom-promotion rule (logged PENDING in
  v17/MILESTONE.md) at/ before rewrite-guides — it binds rewrite-guides + clarity-greenstate. Also clear BOTH
  forms of `rubber-stamp` (the F1 matcher is hyphen-bound, so the space-form in run.md L35/L43 and the
  hyphen-form in phases/1-specify.md + appendix-b are distinct) so the idiom can be promoted to `[enforced]`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

- [ADD · folded] build ORDER must be derived from a frozen contract's BINDING PROPERTIES, not its prose
  staging order: §3 staged "run.md restructure → CR-1", but the binding invariants (CR-1 isolated AND gates
  green after every commit) uniquely forced CR-1 to land BEFORE Win 2 — tagging the sections while still
  listed as narrative would have tripped test_engine_narrative_untagged (evidence: commit 64ebe30 + the
  green-after-every-commit verification trail)
- [TDD · folded] a deterministic preservation gate is NECESSARY-not-SUFFICIENT and must be paired with a
  human-led conservative verify: semantic_inventory proves tokens/anchors survived but is blind to an
  inversion AROUND surviving anchors (an added "unless"/scope-narrowing that keeps every anchor word), so the
  conservative verify gate's human diff-read is the real protection for that class (evidence: §6 GATE RECORD —
  semantic_inventory 0 findings while the SKILL.md trim still required the human's read)
- [SDD · folded] a word-count figure in a contract ("trim ~290 words") is an ESTIMATE, not a spec obligation:
  the safe trim was 180 words and stopping short of the number to avoid cutting load-bearing prose was correct —
  express such targets as "remove duplicative content" not a hard count (evidence: trim variance disclosed at
  the verify gate, 180 removed vs ~290 estimated; remainder rolls to rewrite-guides)
- [ADD · folded] a staged-by-risk plan can have a LEGITIMATE no-op stage and it must be recorded as a finding,
  not silently skipped: 7 of the 10 core files were already rubric-clean, so the planned "positivize the other
  core files" commit was a true no-op (evidence: commit-2 no-op — 0 wording_lint findings on those 7 files
  before any edit)
