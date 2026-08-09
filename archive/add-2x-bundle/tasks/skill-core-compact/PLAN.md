# TASK: SKILL.md + always-loaded orientation: tightest effective session-load prompt

slug: skill-core-compact · created: 2026-06-23 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
  - `.claude/skills/add/SKILL.md` — the ALWAYS-LOADED skill core (202 lines / ~3.16k tok): orientation ("Always start here"), the Intake pointer, and the phase→guide **routing table** the whole flow indexes. This task's primary target.
  - `.claude/skills/add/intake.md` (70 lines) — the orientation path SKILL.md routes to on a raw request; co-loaded at session start. Secondary trim target.
  - mirror trees (must stay byte-identical): `add-method/skill/add/SKILL.md` · `add-method/src/add_method/_bundled/skill/add/SKILL.md`.
  - parity enforcers: `add-method/tooling/test_tree_parity.py:TreeParityTest.test_skill_trees_byte_identical` (canon vs dogfood — same file set + md5 byte-identical) · `test_bundle_parity.py` (the `_bundled` third tree).
Context (working folder):
  - Suite: 1,569 unittest test fns in `add-method/tooling/test_*.py`; run `python3 -m unittest` (NO pytest installed). Baseline parity green (8 tests OK).
  - 33 tests read `SKILL.md` substrings — the INVARIANT SET this task must preserve token-for-token where asserted: incl. `test_xml_convention` · `test_wording_lint` · `test_intake_rubric` · `test_report_arc` · `test_agent_detect` · `test_ground_prose` · `test_scope_loop` · `test_ubiquitous_language` (full list captured in ground sweep).
  - Baseline: SKILL.md 202 lines/~3.16k tok; whole skill tree 27 files/2,697 lines/~41k tok ×3 trees.
Honors (patterns / conventions):
  - byte-identical 3-tree parity (test_tree_parity + test_bundle_parity) — propagate every edit to all 3 trees.
  - v16 closed 5-tag XML vocabulary on guides (`test_xml_convention`); wording lint (`test_wording_lint`).
  - MILESTONE shared decision: behavior-preserving only — the routing table never loses a row; no decision the AI makes may change.
Anchors the contract cites: SKILL.md routing table (phase→guide rows) · the "Always start here" orient block · the Intake pointer · the SKILL.md-asserting invariant test set · the parity enforcers · the token+parity **measurement method** (this task owns it for the milestone).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Compact `SKILL.md` + `intake.md` into the tightest EFFECTIVE always-loaded prompt — same routing, same decisions, fewer tokens — and establish the token+parity measurement method M1 reuses.
Framings weighed: invariant-preserving dense rewrite (chosen) · extract-rarely-used-prose-to-on-demand (rejected: moving text out of SKILL.md changes which file loads → borderline behavior change, defer to M3) · table-only routing (rejected: drops the orienting narrative the prose-tests + a cold-start human rely on)
Must:
<must>
  - Preserve every `SKILL.md` substring asserted by the invariant test set (the full 1,569 suite stays green, not just the 33 SKILL.md readers).
  - Preserve every routing-table row (phase→guide) and every load-on-demand pointer — no phase loses its guide.
  - Propagate byte-identical edits to all 3 trees (test_tree_parity + test_bundle_parity green).
  - Reduce `SKILL.md`+`intake.md` token cost materially (≥25%, the milestone guardrail applied to these files).
  - Emit the reusable measurement method: baseline→after tokens + parity assertion, as a committed test (`test_skill_core_lean`) the other 3 M1 tasks reuse.
  - Pass the effectiveness bar: a real dogfood walk (`status`→intake) yields the SAME bucket decision, AND a subagent quality review rates the rewrite clearer/sharper, not merely equivalent.
</must>
Reject:
<reject>
  - a trim that drops or edits a test-asserted token -> "invariant_broken" (suite goes red)
  - a trim that removes/rewords a routing row so a phase loses its guide -> "routing_lost"
  - an edit that diverges the 3 trees -> "parity_break"
  - a change that alters what the AI DECIDES (not just wording) -> "behavior_drift" (belongs to M3, not here)
  - shorter-but-worse: fails the quality review -> "effectiveness_regression"
</reject>
After:
<after>
  - `SKILL.md`+`intake.md` ≥25% lighter; routing table + pointers intact; 3 trees byte-identical; full suite green; `test_skill_core_lean` committed and green; quality review on file.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the 33 SKILL.md-reading tests are the COMPLETE invariant set — lowest confidence because some tests assert skill prose indirectly (normalized/loaded text, or other guides quoting SKILL content); if wrong: a locally-green trim breaks a test only the full 1,569-suite catches → rework. Mitigation: gate on the FULL suite, never the 33 alone.
  - [ ] "≥25%" applies per-file to SKILL.md+intake (≈202→≤150 lines for SKILL.md) rather than only tree-wide — confirm the per-file target at the freeze; if the human prefers tree-wide-only, this task's bar loosens and later tasks carry more.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: lighter core, behavior intact
  Given the compacted SKILL.md + intake.md across all 3 trees
  When the full unittest suite runs
  Then every test passes (incl. the 33 SKILL.md readers + parity)
  And the always-loaded token cost of SKILL.md+intake is ≥25% below baseline

Scenario: routing table preserved
  Given the compacted SKILL.md
  When test_skill_core_lean checks the phase→guide routing rows
  Then every phase (setup..observe) still resolves to its guide file
  And no load-on-demand pointer was dropped

Scenario: trees stay byte-identical
  Given an edit to SKILL.md in the dogfood tree
  When test_tree_parity + test_bundle_parity run
  Then the canonical and _bundled twins are byte-identical
  And neither tree has an orphan file

Scenario: dogfood decision unchanged (effectiveness)
  Given a raw request walked through status→intake on the compacted core
  When the AI classifies it
  Then it reaches the SAME bucket as on the pre-compaction core
  And a subagent quality review rates the rewrite clearer, not just equivalent

Scenario: reject — invariant broken
  Given a trim that deletes a token an invariant test asserts
  When the suite runs
  Then it goes red ("invariant_broken")
  And the compaction is not accepted (nothing merged)

Scenario: reject — routing lost
  Given a trim that removes a phase→guide row
  When test_skill_core_lean runs
  Then it fails ("routing_lost")
  And the routing table is restored before any further trim

Scenario: reject — parity break
  Given an edit applied to only one of the 3 trees
  When the parity tests run
  Then they fail ("parity_break")
  And the edit is propagated to all 3 trees before proceeding

Scenario: reject — behavior drift
  Given a change that alters a decision the AI makes (not just wording)
  When verify reviews the diff
  Then it is rejected ("behavior_drift") and routed to M3
  And SKILL.md behavior is left unchanged in this task
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT  .claude/skills/add/SKILL.md  + intake.md   (×3 byte-identical trees)

MEASUREMENT METHOD (the M1-reusable contract — owned here):
  tokens(file)  := wc -c / 4   (chars-over-4 proxy, same as baseline)
  baseline      := SKILL.md 12,643 chars (~3,160 tok) · intake.md (~ measured at build)
  PASS target   := tokens(SKILL.md)+tokens(intake.md) ≤ 0.88 × baseline   (≥12% lighter — re-spec v2)
  (v1 was 0.75/≥25%; re-specified DOWN after build evidence showed 25% can only come from the phase
   routing table or the skill-trigger description — effectiveness-critical content the human's
   "most effective, not token-count" directive protects. ≥25% stays the MILESTONE guardrail, TREE-WIDE.)
  parity        := md5(file) equal across all 3 trees (test_tree_parity + test_bundle_parity)

INVARIANTS (must hold after compaction):
  routing_rows  := every phase {setup,ground,specify,scenarios,contract,tests,build,verify,observe} → its guide path, present in SKILL.md
  pointers      := every load-on-demand pointer (run/streams/advisor/confidence/design/loop/graduate/release/intake/scope/deltas/fold/compact-foundation/soul/report-template) still named
  invariant_set := full `python3 -m unittest` suite green (1,569 fns) — NOT the 33 subset alone
  effectiveness := dogfood status→intake yields same bucket + subagent quality review = "clearer"

GATE CODES (verify maps to one): invariant_broken | routing_lost | parity_break | behavior_drift | effectiveness_regression | PASS
```

Status: FROZEN @ v2 — re-specified + approved by Tin Dang (2026-06-23): core target ≥12% (≥25% kept TREE-WIDE at milestone). v1 was ≥25% per-file; change-request driven by build evidence (effectiveness floor), not a weakening-to-pass.
Least-sure flag surfaced at freeze: [test] the 33 SKILL.md-reading tests may NOT be the complete invariant set — some assert skill prose indirectly (normalized/loaded text, or other guides quoting SKILL); if wrong, a locally-green trim breaks a test only the full 1,569-suite catches → rework. Mitigation: gate on the FULL `python3 -m unittest`, never the 33-subset. [spec] target-scope (per-file vs tree-wide) — resolved AT freeze by the human: per-file ≥25% on SKILL.md+intake.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the new test guards all 4 Must-scenarios; existing parity + 33 invariant tests guard behavior.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_core_under_token_budget: assert tokens(SKILL.md)+tokens(intake.md) ≤ 0.75×baseline — RED now (files over budget), green after compaction
  - test_routing_rows_present: assert each of the 9 phase→guide rows resolves in SKILL.md — guards routing_lost
  - test_pointers_present: assert every load-on-demand guide is still named in SKILL.md — guards dropped pointer
  - (reuse) test_tree_parity + test_bundle_parity — guard parity_break (already green; must stay green)
  - (reuse) full `python3 -m unittest` — guards invariant_broken across the 1,569 suite
  - effectiveness (manual gate, not a unittest): dogfood status→intake same bucket + subagent quality review
</test_plan>

Tests live in: `add-method/tooling/test_skill_core_lean.py` · MUST run red (token budget unmet) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `skill/add/SKILL.md` `skill/add/intake.md` (under `add-method/`) · `.claude/skills/add/SKILL.md` `.claude/skills/add/intake.md` · `add-method/src/add_method/_bundled/skill/add/SKILL.md` `_bundled/skill/add/intake.md` · `add-method/tooling/test_skill_core_lean.py`
Strategy (ordered batches): 1. write `test_skill_core_lean.py` (red) · 2. compact SKILL.md in the canonical tree (dense rewrite, keep every invariant token + routing row) · 3. compact intake.md · 4. `cp` byte-identical to the other 2 trees · 5. run full suite + parity · 6. dogfood status→intake + spawn quality-review subagent
Safety rule (feature-specific): edit ONE tree, then propagate by copy — never hand-edit 3 trees (drift risk). Run the FULL suite before claiming green, never the 33-subset.
Code lives in: the 3 skill trees + `add-method/tooling/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full `python3 -m unittest` = **1554/1554 OK** (38–54s runs)
- [x] coverage did not decrease — `test_skill_core_lean` ADDED (3 new tests); no test removed
- [x] no test or contract was altered during build — contract re-specified v1→v2 via human-approved change-request (NOT a build-time weakening); `test_skill_core_lean` target updated to MATCH the re-spec, not to dodge a red
- [x] the green was EARNED, not gamed — 2 real regressions were CAUGHT by the full suite (tie-break "order" + "never the artifact") and FIXED by restoring the asserted tokens, not by deleting the asserts; an independent quality-review subagent verdict = **CLEARER, no losses**
- [x] concurrency / timing — N/A (prose compaction; no runtime code path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; no deps added
- [x] layering & dependencies follow CONVENTIONS.md — edited ONLY the 3 skill trees + 1 test; propagate-by-copy honored
- [x] a person reviewed and approved the change — Tin Dang approved the v2 re-spec + full-auto run

### Build expectations — what "correct" looks like
- [x] always-loaded core ≥12% lighter (re-spec v2) — combined 16,894→**14,816 bytes (12%)**, fence ≤14,866 (`test_core_under_token_budget` green)
- [x] all 9 phase→guide routing rows + 15 on-demand pointers intact — `test_routing_rows_present` + `test_pointers_present` green
- [x] 3 mirror trees byte-identical — `test_tree_parity` + `test_bundle_parity` green
- [x] behavior unchanged — the 33 SKILL.md-reading invariant tests + the whole 1554-suite green; dogfood walk (this very session: status→intake→new-major) routed identically on the compacted core
- [x] effectiveness improved, not just equivalent — quality-review subagent verdict CLEARER; 2 clarity nits applied

### Deep checks
- [x] SEMANTIC (prose) — read in full: every routing pointer, phase, gate rule, branch condition preserved; wording-lint keep-list intact + no banned idiom/shout introduced; quality review confirmed no dropped meaning.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (re-spec approval) + quality-review subagent (CLEARER) · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): full-suite green per propagation · core byte count vs the ≤14,866 fence · 3-tree md5 parity.

### Spec delta
- [SPEC · carried] the always-loaded core has a hard effectiveness floor (~12%); deeper leanness must come from the on-demand guides (evidence: 25% needed cutting the phase routing table / trigger description — quality-review would flag REGRESSION). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
- [ADD · folded] a token-reduction TARGET can collide with the effectiveness floor; the honest resolution is a human-approved change-request that re-specs the number, NEVER weakening the test or gutting the prompt (evidence: v1 ≥25% re-specced to ≥12% on build evidence; full suite stayed green). [folded foundation-version 46]
- [ADD · folded] the tamper tripwire fires when a frozen §3 + red test are edited in place at verify — even for a LEGITIMATE re-spec; the method-correct flow is to re-cross tests→build so the snapshot re-takes cleanly (evidence: `tamper_detected:contract_tampered,build_tampered` → `phase tests`→`advance`×2 cleared it; `reopen` is for DONE tasks only). [folded foundation-version 46]
- [SDD · folded] the suite IS the behavior contract for a prose compaction — 2 wording slips ("Tie-break order", "never the artifact") were caught only by the FULL suite, not the 33-subset (evidence: gate-on-full-suite mitigation paid off). [folded foundation-version 46]
