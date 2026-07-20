# TASK: docs-align

slug: docs-align · created: 2026-06-29 · stage: mvp · risk: high · sensitivity: architecture
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/skill/add/phases/6-verify.md` — Phase 6 guide (prose/doc); add "Advisor 3-lens" subsection documenting the sequential security→concurrency→architecture order, HARD-STOP short-circuit, binding vs advisory distinction, recording requirement, and `advisor_verdict_unrecorded` companion lint
  - `add-method/skill/add/advisor.md` — Advisor delegation guide (prose); add "The 3-lens sequential checklist at verify" section with CLEAR/HARD-STOP/RESIDUE format, run order, and §6 recording requirement (Verdict · Residue · Binding fields)
  - `add-method/skill/add/run.md` — Dynamic run guide (prose); amend the automated quality gate `<constraints>` block to document the advisor-gate-relax pathway (risk:high + sensitivity:mechanical + recorded Verdict:PASS + Residue:none → gate PASS without lowered autonomy dial) and name `advisor_verdict_unrecorded` alongside `refute_unrecorded`
  - `add-method/skill/add/sensitivity.md` — Sensitivity vocabulary (prose, line 14 mechanical definition); amend to specify the three §6 record fields the engine reads for the gate decision: Verdict · Residue · Binding
  - `add-method/skill/add/SKILL.md` — Main skill orchestration file; add one-line pointer to `advisor-gate-relax` near the autonomy/sensitivity bullet in the "Beyond the bundle" section
  - `add-method/tooling/templates/TASK.md.tmpl` — Task template shipped in 3 trees; the `### Advisor 3-lens verdict` block is already inserted by advisor-review-step; docs-align ensures the surrounding `<!-- -->` guidance prose in §6 is coherent (no stale references to the pre-advisor check list)
  - `.add/GLOSSARY.md` AND `add-method/tooling/templates/GLOSSARY.md.tmpl` — project GLOSSARY (live file + seeded template); add 4 new term definitions: `advisor-gate-relax` · `advisor 3-lens verdict` · `binding verdict` · `advisory verdict`
Context (working folder):
  - skill files ship across 3 GIT-TRACKED trees: canonical `add-method/skill/add/` → `add-method/src/add_method/_bundled/skill/add/` + `.claude/skills/add/`; all three must be byte-identical after each edit (parity guarded by `test_skill_parity` / `test_bundle_parity`)
  - template files ship across 3 trees: canonical `add-method/tooling/templates/` → `_bundled/tooling/templates/` + `.add/tooling/templates/`; parity guarded by `test_bundle_parity`
  - lean fence (`test_skill_lean.py`) enforces per-pool byte budgets; prose additions require same-pool byte reclaim
  - wording-lint (`test_ubiquitous_language`) bans certain slang (e.g., "blast radius" → "scope of impact") in all skill/prose files
  - this task is PROSE-ONLY: no `add.py`, `add_engine/`, or engine-pin change; those were made by advisor-review-step / advisor-verdict-audit / advisor-gate-relax engine tasks
Honors (patterns / conventions):
  - 3-tree byte-identical parity: any prose edit to canonical must be mirrored to both other trees before the suite is run
  - lean fence: net byte delta per pool must be ≤ 0; additions must be offset by same-pool reclaim of low-value wording
  - wording-lint: no banned slang in any added prose line
  - GLOSSARY one-line format: `<term>: <definition in one sentence or tight paragraph>` — consistent with existing entries; no markdown headers inside the definition
Anchors the contract cites: the 7 touch-point file paths · the 4 glossary term tokens (`advisor-gate-relax` · `advisor 3-lens verdict` · `binding verdict` · `advisory verdict`) · `sensitivity.md` line 14 `mechanical` definition · `### Advisor 3-lens verdict` block shape · the 3-tree parity model (canonical + _bundled + dogfood)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Align the GLOSSARY, skill prose (6-verify · advisor · run · sensitivity · SKILL), and the TASK template with the new risk-tiered advisor-gated-autonomy feature — adding the Advisor 3-lens checklist documentation, the advisor-gate-relax pathway, and 4 new GLOSSARY terms; keeping all 3 skill/template trees byte-identical under the lean budget and wording-lint.
Framings weighed: amend the 7 existing prose files in-place (chosen) · add a new standalone `advisor-gate.md` skill guide (rejected — a new file adds a new skill tree entry requiring parity registration across all 3 trees, unnecessary new parity surface when content fits the existing files) · defer docs until all engine tasks complete (rejected — docs-align is its own task in the milestone; deferred docs create a gap between engine behavior and the prose that describes it)
Must:
<must>
  - `add-method/skill/add/phases/6-verify.md`: add an "Advisor 3-lens" subsection documenting the sequential security→concurrency→architecture order; that a Security HARD-STOP short-circuits the remaining lenses; the Binding vs advisory distinction (sensitivity:mechanical = Binding:yes; all other classes = Binding:advisory); the recording requirement; and `advisor_verdict_unrecorded` as a companion notice to `refute_unrecorded`
  - `add-method/skill/add/advisor.md`: add "The 3-lens sequential checklist at verify" section with CLEAR/HARD-STOP/RESIDUE format, the security→concurrency→architecture run order, and the §6 recording requirement (Verdict · Residue · Binding fields); existing plan-following template and model-tier guidance are unchanged
  - `add-method/skill/add/run.md`: amend the automated quality gate `<constraints>` block to document the advisor-gate-relax pathway — risk:high + sensitivity:mechanical + recorded Verdict:PASS + Residue:none satisfies the gate without requiring a lowered autonomy level; name `advisor_verdict_unrecorded` alongside `refute_unrecorded` as a lint companion
  - `add-method/skill/add/sensitivity.md`: amend the `mechanical` definition (line 14) to specify the three §6 record fields the engine reads for the gate decision: Verdict · Residue · Binding; the base-four list and project-extension mechanics are unchanged
  - `add-method/skill/add/SKILL.md`: add a one-line pointer to `advisor-gate-relax` near the autonomy/sensitivity bullet in the "Beyond the bundle" section
  - `add-method/tooling/templates/TASK.md.tmpl`: ensure the `<!-- -->` guidance prose in §6 surrounding the `### Advisor 3-lens verdict` block (inserted by advisor-review-step) is coherent; remove any stale references to the pre-advisor §6 check list
  - `.add/GLOSSARY.md` AND `add-method/tooling/templates/GLOSSARY.md.tmpl`: add all 4 new term definitions in the one-line format: `advisor-gate-relax` · `advisor 3-lens verdict` · `binding verdict` · `advisory verdict`
  - every prose edit passes the 3-tree byte-parity guard: canonical + _bundled + dogfood trees are byte-identical after all edits
  - every prose addition stays within the lean fence: genuinely-new advisor surface is rebaselined into the pool budget (ratio kept exactly, baseline += surface ÷ ratio); reclaim by re-compacting guard-protected wording is forbidden (v2)
  - no banned slang term is introduced: wording-lint (`test_ubiquitous_language`) stays green
</must>
Reject:
<reject>
  - a prose edit applied to the canonical tree but not mirrored to both other trees → parity guard red (`test_skill_parity` / `test_bundle_parity`)
  - a pool grown WITHOUT a ratio-kept rebaseline, OR a reclaim that weakens guard-protected wording → lean fence red (`test_skill_lean.py`) / prose-guard red (v2)
  - a banned slang term in any added prose line → wording-lint red (`test_ubiquitous_language`)
</reject>
After:
<after>
  - all 7 touch-point files contain coherent prose describing the advisor-gated-autonomy feature; no file describes the pre-advisor state (e.g., `run.md` names the advisor-gate-relax pathway; `sensitivity.md` names the §6 Verdict/Residue/Binding fields)
  - all 4 glossary terms are defined in both GLOSSARY files with the one-line format
  - the suite is green: 3-tree parity · lean fence · wording-lint all pass
  - no engine file (`add.py`, `add_engine/`) was modified; this task is prose/docs only
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [scope] whether the book chapter for advisor-gated-autonomy content is a NEW standalone file or folds into an existing chapter (e.g., `docs/08-step-6-verify.md`) — lowest confidence because the book has dedicated chapter files per phase; if the new content does not fit any existing chapter without awkward padding, a new chapter file becomes necessary, adding a new book-parity tree entry and registration cost; I assume FOLD INTO the closest existing chapter to avoid new parity surface; if wrong: a new chapter file + registration across all 3 book trees must be added to the touch-point inventory, expanding this task's scope
  - [ ] lean fence headroom: whether the byte additions across the 7 files can each be offset by reclaim within the same pool's existing prose without weakening any guarantee — if the per-pool budget is too tight for the required content volume, a focused reclaim pass is needed before the gate; resolve during build
  - [ ] GLOSSARY template format: whether `GLOSSARY.md.tmpl` uses the same one-line definition format as the live `.add/GLOSSARY.md` and accepts the same append pattern — if the template uses a different framing-sensitive structure, a format-specific approach is needed for the template vs the live file; resolve by reading both files at build start
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: 6-verify.md gains Advisor 3-lens subsection
  Given add-method/skill/add/phases/6-verify.md at its current state
  When the Advisor 3-lens subsection is added with sequential order, HARD-STOP short-circuit, binding/advisory distinction, recording requirement, and advisor_verdict_unrecorded mention
  Then the file contains the subsection coherently placed; all 3 trees are byte-identical after mirroring
  And the lean fence for the file's pool holds (net byte delta ≤ 0) and wording-lint is green

Scenario: advisor.md gains 3-lens checklist section
  Given add-method/skill/add/advisor.md at its current state
  When "The 3-lens sequential checklist at verify" section is added with CLEAR/HARD-STOP/RESIDUE format, run order, and §6 recording requirement
  Then the file contains the new section; the existing plan-following template is byte-identical to before
  And all 3 trees byte-identical; lean fence holds; wording-lint green

Scenario: run.md auto-gate block documents advisor-gate-relax and advisor_verdict_unrecorded
  Given add-method/skill/add/run.md automated quality gate constraints block at its current state
  When the advisor-gate-relax pathway and advisor_verdict_unrecorded companion lint are added
  Then the block states that risk:high + mechanical + recorded Verdict:PASS + Residue:none satisfies the gate via advisor-gate-relax and names advisor_verdict_unrecorded alongside refute_unrecorded
  And all 3 trees byte-identical; lean fence holds; wording-lint green

Scenario: sensitivity.md mechanical definition specifies the three §6 record fields
  Given add-method/skill/add/sensitivity.md line 14 mechanical definition referencing advisor-gate-relax
  When the Verdict, Residue, Binding fields are named in the definition
  Then the definition specifies all three fields the engine reads; the base-four list and project-extension section are unchanged
  And all 3 trees byte-identical; lean fence holds; wording-lint green

Scenario: SKILL.md gains advisor-gate-relax pointer
  Given add-method/skill/add/SKILL.md near the autonomy/sensitivity bullet in "Beyond the bundle"
  When a one-line pointer to advisor-gate-relax is inserted
  Then the pointer is present in the correct section; surrounding text is unchanged
  And all 3 trees byte-identical; lean fence holds; wording-lint green

Scenario: TASK.md.tmpl §6 guidance prose is coherent with the Advisor 3-lens verdict block
  Given the ### Advisor 3-lens verdict block already inserted by advisor-review-step in TASK.md.tmpl
  When the surrounding <!-- --> guidance prose is updated for coherence
  Then no stale references remain to the pre-advisor §6 check list; the block itself is unchanged
  And all 3 template trees byte-identical

Scenario: 4 glossary terms defined in both GLOSSARY files
  Given .add/GLOSSARY.md and add-method/tooling/templates/GLOSSARY.md.tmpl at their current states
  When advisor-gate-relax, advisor 3-lens verdict, binding verdict, advisory verdict are appended in one-line format
  Then both files contain all 4 definitions consistent with existing GLOSSARY style
  And no existing definition is modified

Scenario: parity guard catches an incomplete mirror
  Given a prose edit applied only to the canonical add-method/skill/add/ tree
  When the suite runs
  Then test_skill_parity or test_bundle_parity fails identifying the mismatched file
  And the edit to the canonical file is the only change

Scenario: lean fence catches a budget overrun without reclaim
  Given a prose addition to a skill file pool that increases the pool's byte total with no same-pool reclaim
  When the suite runs
  Then test_skill_lean.py fails for that pool naming the file
  And no other lean pool is affected

Scenario: wording-lint catches a banned slang term
  Given an added prose line containing a banned slang term
  When the suite runs
  Then test_ubiquitous_language fails naming the offending file and term
  And no other test is affected
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE-ONLY task — no engine logic change (no add.py / add_engine/ edit)

Touch-point inventory (all 7 must be complete for the gate to PASS):

  1. add-method/skill/add/phases/6-verify.md
       ADD subsection "Advisor 3-lens"
       Required content: sequential security→concurrency→architecture; Security HARD-STOP
         short-circuits remaining lenses; Binding:yes for sensitivity:mechanical / Binding:advisory
         for all other classes; §6 recording requirement; advisor_verdict_unrecorded as companion
         notice to refute_unrecorded

  2. add-method/skill/add/advisor.md
       ADD section "The 3-lens sequential checklist at verify"
       Required content: CLEAR / HARD-STOP / RESIDUE format; run order
         security→concurrency→architecture; §6 record fields (Verdict · Residue · Binding);
         existing plan-following template and model-tier text unchanged

  3. add-method/skill/add/run.md
       AMEND automated quality gate <constraints> block
       Required content: advisor-gate-relax pathway — risk:high + sensitivity:mechanical +
         recorded Verdict:PASS + Residue:none → gate PASS without a lowered autonomy level;
         advisor_verdict_unrecorded named alongside refute_unrecorded

  4. add-method/skill/add/sensitivity.md
       AMEND mechanical definition (currently line 14)
       Required content: specify the three §6 record fields the engine reads: Verdict · Residue ·
         Binding; base-four list and project-extension section unchanged

  5. add-method/skill/add/SKILL.md
       ADD one-line pointer to advisor-gate-relax
       Position: near the autonomy/sensitivity bullet in the "Beyond the bundle" section

  6. add-method/tooling/templates/TASK.md.tmpl
       AMEND <!-- --> guidance prose in §6 surrounding ### Advisor 3-lens verdict block
       Required content: coherent with the block inserted by advisor-review-step; no stale
         references to the pre-advisor §6 check list; the ### Advisor 3-lens verdict block
         shape itself is unchanged

  7. .add/GLOSSARY.md  AND  add-method/tooling/templates/GLOSSARY.md.tmpl
       ADD 4 new term definitions in existing one-line format:

       advisor-gate-relax: a risk:high + sensitivity:mechanical task with a recorded
         Verdict:PASS and Residue:none in the §6 Advisor 3-lens verdict may auto-complete
         via gate PASS without requiring a lowered autonomy level; security and all
         non-mechanical sensitivity classes are never relaxed via this pathway.

       advisor 3-lens verdict: the sequential security→concurrency→architecture
         non-functional sweep recorded in §6 (Verdict · Residue · Binding fields); Verdict
         is PASS or HARD-STOP only; a Security HARD-STOP short-circuits the remaining lenses.

       binding verdict: a §6 Advisor 3-lens verdict with Binding:yes — engine-enforced for
         risk:high + sensitivity:mechanical tasks (gates auto-completion via advisor-gate-relax);
         tasks carrying any other sensitivity class receive an advisory verdict instead.

       advisory verdict: a §6 Advisor 3-lens verdict with Binding:advisory — surfaced for
         human awareness but not engine-enforced (the gate is not relaxed by it); applies to
         all sensitivity classes other than mechanical.

Parity invariant (suite-enforced):
  canonical add-method/skill/add/ ←byte-identical→ _bundled/skill/add/ AND .claude/skills/add/
  canonical add-method/tooling/templates/ ←byte-identical→ _bundled/tooling/templates/ AND .add/tooling/templates/

Lean-fence invariant (test_skill_lean.py) — v2:
  genuinely-NEW advisor surface is REBASELINED into the pool budget (the repo's established
  method, ~15 prior rebaselines): the RATIO is kept EXACTLY and the baseline grows by
  new-surface ÷ ratio, so the won compaction on existing prose is pinned untouched. Reclaim by
  re-compacting GUARD-PROTECTED wording (the verbatim safety/cross-surface-identity sentences the
  prose-guards pin) is FORBIDDEN — restoring that wording takes priority over byte budget.
  [v1 said "net delta ≤ 0 via same-pool reclaim"; corrected at v2 — reclaiming the advisor
   touch-points would have re-compacted the guide prose docs-align exists to restore.]

Wording-lint invariant (test_ubiquitous_language):
  no banned slang term in any added prose line
```

Least-sure flag surfaced at freeze: [contract] whether the book chapter for advisor-gated-autonomy narrative is a NEW standalone file or folds into an existing chapter (e.g., `docs/08-step-6-verify.md`) — lowest confidence because a new book chapter adds a parity-tree entry requiring registration across all 3 book trees; preference is FOLD INTO the closest existing chapter to avoid expanding the parity surface; if wrong: a new chapter file plus its registration in all 3 book trees must be added to the touch-point inventory, expanding scope beyond the 7 listed above.

Status: FROZEN @ v2 — approved by Tin Dang
<!-- v1→v2 change request (approved at the docs-align verify gate): (1) lean-fence invariant
     corrected from "reclaim, net ≤0" to "rebaseline-for-new-surface, ratios kept" — reclaim
     would re-compact the guard-protected guide prose this task restores; (2) "lowered autonomy
     dial" → "lowered autonomy level" (×2: run.md required-content + the advisor-gate-relax
     glossary def) — §3 also requires wording-lint green and "dial" is a banned term. No
     touch-point added/removed; the 7-point inventory is unchanged. -->
<!-- v1 — approved by Tin Dang (superseded) -->
<!-- Least-sure flag at v2 re-freeze: [contract] the lean approach itself — rebaseline raises the
     pool budget; the risk is budget-creep over many milestones. Mitigation: ratios are kept
     EXACTLY (the won per-guide compaction is never given back) and reclaim-by-weakening is banned,
     so the fence still pins the won ground; if wrong, a future lean-audit milestone re-compacts
     low-value prose deliberately rather than as a gate side effect. -->

Also amended for the v2 wording fix (spec bundle consistency):
  §1 Must (run.md line): "lowered autonomy dial" → "lowered autonomy level"
  Reject list: the "without a same-pool reclaim → lean fence red" reject is superseded by the
    v2 lean invariant — the live reject is "reclaim by weakening guard-protected wording, OR a
    pool grown without a ratio-kept rebaseline → lean fence / prose-guard red".
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §2 content scenario asserted; parity/lean/wording guarded by their own modules.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_docs_align.test_6verify_advisor_recording: the §6 `### Advisor 3-lens verdict` recording +
    `advisor_verdict_unrecorded` + Binding distinction + sequential order present in all 3 skill trees
  - test_docs_align.test_advisor_3lens_section: advisor.md "The 3-lens sequential checklist at verify"
    with CLEAR/RESIDUE + Verdict·Residue·Binding fields, all 3 trees
  - test_docs_align.test_runmd_gate_relax_pathway: run.md names `advisor-gate-relax` + `advisor_verdict_unrecorded`
    + the "never relaxed" safety clause, all 3 trees
  - test_docs_align.test_sensitivity_three_fields: sensitivity.md mechanical names `Verdict · Residue · Binding`
  - test_docs_align.test_skill_pointer: SKILL.md carries the `advisor-gate-relax` pointer
  - test_docs_align.test_template_advisor_block: the §6 block ships in all 3 template trees
  - test_docs_align.test_glossary_four_terms: both GLOSSARY surfaces define the 4 terms
  - test_docs_align.test_glossary_relax_def_uses_level_not_dial: the relax def uses "autonomy level"
    (wording-lint conformance) — the bridge "(formerly autonomy dial)" entry is exempt and stays
  - parity → test_skill_parity / test_bundle_parity · lean → test_skill_lean (rebaselined, see §6 delta) ·
    wording → test_ubiquitous_language — all green
</test_plan>

Tests live in: `test_docs_align.py` · MUST run red (missing implementation) before Build.
Red→green proof: at HEAD (pre-touch-points) advisor.md lacked "The 3-lens sequential checklist at verify"
and 6-verify.md lacked the §6 recording instruction → the content guard ran red; green after the build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/6-verify.md` `add-method/skill/add/advisor.md` `add-method/skill/add/run.md` `add-method/skill/add/sensitivity.md` `add-method/skill/add/SKILL.md` `add-method/tooling/templates/TASK.md.tmpl` `.add/GLOSSARY.md` `add-method/tooling/templates/GLOSSARY.md.tmpl` `add-method/tooling/test_skill_lean.py` `add-method/tooling/test_docs_align.py` `add-method/src/add_method/_bundled/skill/add/` `.claude/skills/add/`
Strategy (ordered batches): 1. restore the guard-protected verbatim guide wording (6-verify · run · sensitivity) the mid-session compaction had dropped (git checkout HEAD on the 3 guides). 2. re-add ONLY the advisor touch-points (1·3·4) as non-destructive additions on top of the restored baseline, leaving every guard-protected sentence intact. 3. sync all 3 skill + 3 template trees (prepare_bundle + cp to .claude). 4. rebaseline test_skill_lean for the genuinely-new advisor surface (ratios kept exactly). 5. add test_docs_align content guard.

Known-problem fixes: reclaiming bytes by compacting guide prose → re-breaks the prose-guards (this is exactly what the compaction did) → so RESTORE wording + REBASELINE for new surface instead of reclaim · editing a guard-protected sentence → guard red → additions only, never touch the pinned phrases · "dial" in copied §3 wording → wording-lint red → ship "autonomy level".
Strategy actually used: as planned. The build was a reconciliation: the mid-session compaction (external/IDE) had broken 8 prose-guards by dropping verbatim safety/identity sentences; restored to the green HEAD baseline, re-added the advisor touch-points, rebaselined lean (+433 phases · +928 orchestration · +52 reference ÷ ratio) rather than reclaim — see §6 delta.
Safety rule (feature-specific): never weaken a security-guarantee or cross-surface-identity guard to make the suite pass; restore the verbatim wording the guard pins, and never reclaim by re-compacting the just-restored prose.
Code lives in: the 7 prose touch-points + the 2 mirror trees (prose-only; no add.py / add_engine / engine-pin change).
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] all 7 prose touch-points state their required advisor content — confirmed by test_docs_align (8/8) + manual read of 6-verify/advisor/run/sensitivity/SKILL + both GLOSSARY files
- [x] the guard-protected verbatim safety/identity sentences SURVIVE (no security guarantee weakened) — confirmed by the 8 prose-guards green (test_security_escalation_disclosure · test_stale_guide_sync · test_rewrite_guides · test_verify_deepen · test_earned_green_rubric · test_gate_audit · test_high_risk_signal)
- [x] all 3 skill trees + all 3 template trees byte-identical — confirmed by test_skill_parity / test_bundle_parity green (md5 1-distinct spot-check on the 3 guides)
- [x] wording-lint green — no banned "dial" usage in shipped prose (GLOSSARY relax def uses "autonomy level"; bridge "(formerly autonomy dial)" exempt) — confirmed by test_ubiquitous_language + test_docs_align.test_glossary_relax_def_uses_level_not_dial
- [x] full suite green — confirmed by `python3 -m unittest discover` → Ran 2407, OK

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read HEAD-vs-working diffs of all 3 guides to confirm the compaction (not my edits) dropped the verbatim sentences; read each of the 8 failing guards to confirm the new prose still states the full guarantee BEFORE restoring; confirmed the advisor touch-points (1·3·4) are additions that do not alter any guard-pinned sentence; confirmed advisor.md (touch-point 2) already carries the 3-lens checklist. No code symbols introduced (prose-only); WIRING/DEAD-CODE N/A.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: probed whether the green is gamed — (a) is test_docs_align vacuous? No: it asserts specific advisor phrases across all 3 trees and was red at HEAD (advisor.md lacked the section). (b) did I "pass" the 8 prose-guards by weakening them? No: I edited ZERO guards — I restored the verbatim wording they pin (git checkout HEAD on the guides), the strictly safe direction. (c) did the lean rebaseline hide a reclaim that re-broke a guard? No: ratios kept exactly, baselines raised only by new-advisor-surface÷ratio, and the 8 guards are green. (d) is the advisor content real or stubbed? Read each touch-point — all present and coherent.

### Advisor 3-lens verdict
Advisor: self (independent read at verify)
1. Security: CLEAR — prose-only task; the security-guarantee guards (HARD-STOP always, never-waiver, missed-finding spot-audit disclosure) are RESTORED verbatim, not weakened. No secrets/injection/deps surface.
2. Concurrency: CLEAR — no runtime/concurrent code path (documentation).
3. Architecture: CLEAR — additions respect each guide's structure; 3-tree parity + lean fence hold.
Verdict: PASS
Residue: none (the two frozen-§3 deltas below are contract-truth items for the human, not technical residue)
Binding: advisory (sensitivity: architecture, not mechanical → not engine-gated; advisor-gate-relax does not apply)

### Frozen-§3 deltas surfaced for the human gate (not silently resolved)
> docs-align is risk:high + method-defining → human-gated at verify (conservative). Two points where
> the build departs from the frozen §3 v1 — each needs the human's call (re-freeze v2 vs honor v1):
- DELTA 1 (lean approach): §3 froze "net byte delta per pool ≤ 0 — additions offset by same-pool
  RECLAIM" and rejects any pool increase. The build REBASELINED instead (ratios kept; +433 phases /
  +928 orchestration / +52 reference ÷ ratio). Reason: reclaim = re-compacting the very guide prose the
  prose-guards pin (that compaction is what broke 8 guards); rebaseline-for-new-surface is the repo's
  established method (~15 prior rebaselines in test_skill_lean) and the user's live "restore + rebaseline
  if needed" instruction. Honest read: this contradicts §3 v1's reclaim-only invariant → re-freeze v2.
- DELTA 2 (wording): §3 v1 text says "lowered autonomy DIAL" (lines 177/200); the build shipped "lowered
  autonomy LEVEL" because §3 ALSO requires wording-lint green and "dial" is banned (internal §3
  inconsistency). The shipped prose is lint-correct; §3's frozen wording should be corrected at re-freeze.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose amend the 7 existing prose files in-place; rejected add a new standalone `advisor-gate.md` skill guide (rejected — a new file adds a new skill tree entry requiring parity registration across all 3 trees, unnecessary new parity surface when content fits the existing files) · defer docs until all engine tasks complete (rejected — docs-align is its own task in the milestone; deferred docs create a gap between engine behavior and the prose that describes it)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: as planned. The build was a reconciliation: the mid-session compaction (external/IDE) had broken 8 prose-guards by dropping verbatim safety/identity sentences; restored to the green HEAD baseline, re-added the advisor touch-points, rebaselined lean (+433 phases · +928 orchestration · +52 reference ÷ ratio) rather than reclaim — see §6 delta.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
