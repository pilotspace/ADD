# TASK: XML form tags for ADD templates (v18 convention amendment)

slug: xml-prompt-structure · created: 2026-06-07 · stage: mvp
autonomy: auto
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: v18 FORM-TAG amendment to the frozen v16 XML convention — TASK.md.tmpl's fill
regions become machine-delimited paired XML blocks; templates get a lean pass; a
parse-seam suite proves the engine reads new scaffolds unchanged. Guides need nothing:
v16 already converted them under the very convention this task amends (intake corrected
2026-06-07 after discovering the v16 work; the human approved the amendment route).
Framings weighed: amend-with-separate-form-class (chosen) · reuse v16 instruction tags in templates · lean-only-no-tags · full-XML-conversion + engine rewrite
Must:
  - §3 carries the amendment: a CLOSED form-tag class of 6 (must · reject · after ·
    assumptions · scenarios · test_plan), templates-only — the sanctioned "never silent"
    extension of the frozen v16 list; the human freezes the amendment text itself.
  - TASK.md.tmpl wraps its six fill regions in paired, own-line form tags; every existing
    label line (`Must:` `Reject:` `After:` `Assumptions — lowest-confidence first:`
    `Framings weighed:`) survives — labels are never replaced by tags (extends v16's
    "headers survive" boundary rule to forms).
  - TASK.md.tmpl lean pass: §3's three instruction comments merge into one; §4's
    path-grammar comment tightens; comment volume shrinks; zero parsed-seam or
    pinned-literal changes.
  - MILESTONE.md.tmpl + PROJECT.md.tmpl: clarity-only edits (sharper placeholders);
    NO tags in v18; parsed rows/headings (`- [ ] <slug>`, `## Exit criteria`) untouched.
  - New parse-seam suite (test_template_form_tags.py) scaffolds from the NEW templates
    and proves the engine unchanged: `phase:` read + sync round-trip · `_phase_spans`
    finds §1–§7 · an UNFILLED scaffold keeps today's semantics (all 7 bodies show their
    labels, none flips to "(empty)"; a tag-only block alone reads "(empty)" — tags are
    placeholder-class, never fabricated content) · a FILLED tagged region reports
    non-empty · freeze stamp, gate outcome, §6 security-checklist regex, and
    `Tests live in:` counting parse as before.
  - The class-separation guard (in the new suite): form tags never in skill guides,
    instruction tags never in templates, the form set CLOSED; test_xml_convention.py
    (the v16 instrument) stays untouched.
  - Both template trees stay byte-identical (.add/tooling/templates ≡
    add-method/tooling/templates); parity coverage extends to ALL 7 .tmpl files
    (today only TASK.md.tmpl + add.py are pair-checked, test_cospecify_scaffold.py:105
    — the other six can drift silently).
  - Existing template-pinning tests (test_cospecify_scaffold · test_declared_fallback ·
    test_gate_audit · suite-wide) stay green UNWEAKENED; add.py itself is NOT modified.
Reject:
  - an engine-parsed seam line/heading altered in any template -> "parsed_seam_touched"
  - a filled value inlined in a one-line element (`<must>x</must>`) -> "inline_fill"
  - an instruction tag in a template, or a form tag in a guide -> "class_mixed"
  - a paired template tag outside the closed 6-tag set -> "form_vocab_offmidiom"
  - a label line replaced by a tag -> "label_dropped"
  - the two template trees diverging -> "template_drift"
After:
  - `add.py init`/`new-task` scaffold artifacts whose fill regions are machine-delimited;
    the engine's read of them is PROVEN unchanged (green seam suite, add.py untouched);
    templates are leaner; the amendment is frozen here as the versioned reference any
    future form-parsing feature builds against.
Assumptions — lowest-confidence first:
  ⚠ Form-tag lines surviving into `report`/phase-detail renders are acceptable noise —
    lowest confidence because it is a taste call you have not yet seen rendered; if wrong:
    stripping them needs a change-request against the frozen v9-1 phase-detail shape
    (an engine edit this task deliberately avoids).
  ⚠ The 6-tag closure is right (tags only where AI fills + future parsing concentrate:
    §1/§2/§4; §5–§7 stay untagged — §6 is the engine's densest parse surface) — because
    real usage may show §7 deltas deserve a tag; if wrong: one more amendment cycle
    (another freeze approval).
  - [ ] No consumer outside add.py + the named tests reads template text (cli.js copies,
    never parses) — verify in build.
  - [ ] `_FALLBACK_TASK` (embedded circuit-breaker template in add.py) stays untagged by
    design and stays consistent — verify in build.
  - [ ] `docs/appendix-a-templates.md` does not reproduce template bodies verbatim —
    verify in build; sync it if it does.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: amendment frozen as the convention's extension          # Must 1
  Given the v16 convention frozen in xml-convention §3
  When this task's §3 is approved
  Then the form-tag class exists as a CLOSED 6-tag list in a frozen artifact
  And the v16 five-tag instruction list is unchanged

Scenario: scaffold carries form tags                              # Must 2
  Given a project scaffolded from the new TASK.md.tmpl
  When the rendered TASK.md is read
  Then all six fill regions are wrapped in paired own-line form tags
  And every label line (Must:/Reject:/After:/Assumptions —/Framings weighed:) survives

Scenario: leaner template, same seams                             # Must 3
  Given the new TASK.md.tmpl beside the old
  When instruction comments are compared
  Then §3 carries ONE merged comment and total comment volume shrank
  And every parsed seam and pinned literal is byte-identical

Scenario: milestone/project templates clarity-only                # Must 4
  Given the new MILESTONE.md.tmpl and PROJECT.md.tmpl
  When their paired tags are counted
  Then the count is zero
  And `- [ ] <slug>` rows + `## Exit criteria` parse exactly as before

Scenario: unfilled scaffold keeps today's semantics               # Must 5a
  Given a freshly scaffolded, unfilled TASK.md from the new template
  When task_phases parses it
  Then all seven bodies show their labels exactly as on the old template
  And a tag-only block alone reads "(empty)" — bare form-tag lines never count as content

Scenario: filled region reads non-empty                           # Must 5b
  Given a `- behavior` line between <must> and </must>
  When task_phases parses §1
  Then the body is non-empty and contains the line
  And phase sync, freeze stamp, gate outcome, §6 checklist and
      `Tests live in:` counting behave exactly as on the old template

Scenario: class separation enforced                               # Must 6
  Given the converted templates and the v16-converted guides
  When the extended xml-convention guard runs
  Then no instruction tag appears in any template and no form tag in any guide
  And the guide-side v16 checks still pass untouched

Scenario: template trees cannot drift                             # Must 7
  Given .add/tooling/templates and add-method/tooling/templates
  When the new parity test runs
  Then every .tmpl is byte-identical across both trees
  And a single diverged byte fails the suite

Scenario: existing pins stay green unweakened                     # Must 8
  Given the full existing tooling suite
  When it runs against the new templates
  Then test_cospecify_scaffold, test_declared_fallback, test_gate_audit pass
  And no existing test file was edited to make that true

Scenario: reject parsed_seam_touched                              # Reject 1
  Given a template edit that alters a parsed seam (e.g. the §6 checklist line)
  When the parse-seam suite runs
  Then it fails naming "parsed_seam_touched"
  And the engine's read contract is restored before merge

Scenario: reject inline_fill                                      # Reject 2
  Given a one-line element `<must>debit+credit atomic</must>` in a scaffold
  When the inline-fill guard checks it
  Then it fails naming "inline_fill"
  And the multi-line form (tag · lines · close-tag) is required

Scenario: reject class_mixed                                      # Reject 3
  Given a `<constraints>` block pasted into TASK.md.tmpl
  When the class-separation guard runs
  Then it fails naming "class_mixed"
  And the template carries only form-class tags after the fix

Scenario: reject form_vocab_offmidiom                             # Reject 4
  Given a paired `<notes>` tag added to a template
  When the closed-set guard runs
  Then it fails naming "form_vocab_offmidiom"
  And additions happen only by amending the frozen list

Scenario: reject label_dropped                                    # Reject 5
  Given a template where <must> replaced the `Must:` label line
  When the label-survival guard runs
  Then it fails naming "label_dropped"
  And label + tag coexist in the fixed template

Scenario: reject template_drift                                   # Reject 6
  Given an edit landing in only one of the two template trees
  When the parity test runs
  Then it fails naming "template_drift"
  And the same commit must carry both trees
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

The contract is the AMENDMENT (not an HTTP shape) — the versioned extension of the
convention frozen by `xml-convention` §3 @ v16. The v16 text is NOT edited; this
artifact extends it, exactly as its "additions only by amending this frozen list,
never silent" clause sanctions.

```
XML CONVENTION — v18 FORM-TAG AMENDMENT  (extends FROZEN v16; the v16 five are unchanged)

CLASS RULE (two disjoint tag classes — never mixed; reject class_mixed):
  INSTRUCTION tags (v16): prompt · exit_gate · constraints · reject_codes · output_format
    — skill guides only ("this block is the instruction to adopt").
  FORM tags (v18, this amendment): fill-region boundaries — template-scaffolded
    artifacts only ("this block is where the content goes").

FORM VOCABULARY (CLOSED — additions only by amending this list, never silent;
                 reject form_vocab_offmidiom):
  <must>         §1 required behaviors      wraps the list under the `Must:` label
  <reject>       §1 refusals + error codes  wraps the list under `Reject:`
  <after>        §1 success state           wraps the list under `After:`
  <assumptions>  §1 ranked assumptions      wraps the ⚠-ranked list under its label
  <scenarios>    §2 gherkin                 wraps the INTACT ```gherkin fence
                                            (appendix-b wrap pattern: tag · blank ·
                                             fence · blank · close-tag)
  <test_plan>    §4 per-scenario test list  wraps the plan list; `Tests live in:`
                                            stays OUTSIDE the tag (parsed seam)

FORMATTING (inherits v16: paired · own-line open/close · no nesting/attributes ·
            content is markdown lines BETWEEN tags) + two form-specific rules:
  - NEVER inline a filled value into a one-line element (`<must>x</must>`): add.py's
    placeholder detection reads any full-line `<...>` as scaffold — an inline fill
    reports the section "(empty)".                                reject inline_fill
  - Labels are never replaced by tags: `Must:` / `Reject:` / `After:` /
    `Assumptions — lowest-confidence first:` / `Framings weighed:` stay plain text
    (v16's "headers survive" extended to form labels).            reject label_dropped

SEAM INVARIANT (engine-parsed lines/headings byte-compatible; reject parsed_seam_touched):
  `phase:` line · `## N ·` headings · `Status:` · `Outcome:` · `Tests live in:` ·
  the §6 checklist lines · `# TASK:` title · milestone `- [ ] <slug>` rows ·
  `## Exit criteria` · `goal:` line. add.py itself is NOT modified by this task.

SCOPE: TASK.md.tmpl carries all six form tags; MILESTONE / PROJECT / GLOSSARY /
  CONVENTIONS / MODEL_REGISTRY / dependencies.allowlist templates carry NO tags in
  v18 (clarity edits only). TASK §5/§6/§7 stay untagged (§6 is the densest parse
  surface). `_FALLBACK_TASK` (embedded circuit breaker) stays untagged.

MIRRORS: .add/tooling/templates ≡ add-method/tooling/templates, byte-identical,
  parity check extended to all 7 .tmpl files (today: TASK.md.tmpl + add.py
  only).                                                        reject template_drift

REJECT CODES: parsed_seam_touched · inline_fill · class_mixed · form_vocab_offmidiom ·
  label_dropped · template_drift

ENFORCEMENT: test_template_form_tags.py (NEW) carries the parse-seam suite, the
  class-separation guard, AND the all-7 template parity check; test_xml_convention.py
  (the v16 instrument) stays untouched — class separation is a v18 concern.
```

Status: FROZEN @ v18 — approved by Tin Dang, 2026-06-07 (one-approval front; autonomy: auto)   <!-- Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's lowest-confidence flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first input; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must and every Reject has a test (15 tests for 14 scenarios — Must 5
splits into empty/filled); behavior-level (the suite scaffolds REAL projects via add.py and
asserts engine output, never add.py internals).
Plan (one test per scenario, asserting behavior not internals):
  - test_amendment_frozen_artifact: arrange this §3 / act read / assert closed 6-list present + v16 five unchanged
  - test_scaffold_carries_form_tags: arrange scaffold via new-task / act read TASK.md / assert 6 paired own-line tags + assert labels survive
  - test_lean_same_seams: arrange new vs old tmpl / act diff seams+pins / assert comments shrank + assert seams byte-identical
  - test_milestone_project_untagged: arrange new tmpls / act count paired tags / assert zero + assert rows/criteria parse
  - test_unfilled_scaffold_reads_empty: arrange fresh scaffold / act task_phases / assert 7×"(empty)" + assert tag lines uncounted
  - test_filled_region_reads_nonempty: arrange line inside <must> / act task_phases / assert body holds line + assert sync/freeze/gate/checklist/declared-count unchanged
  - test_class_separation: arrange guides+templates / act guard / assert no cross-class tag + assert v16 checks untouched
  - test_template_tree_parity: arrange both trees / act compare / assert byte-identical + assert single-byte divergence fails
  - test_existing_pins_green: arrange full suite / act run / assert green + assert no existing test edited
  - test_reject_parsed_seam_touched: arrange seam-altered tmpl fixture / act suite / assert fail names code + assert restored passes
  - test_reject_inline_fill: arrange one-line filled element / act guard / assert fail names code + assert multi-line passes
  - test_reject_class_mixed: arrange <constraints> in tmpl fixture / act guard / assert fail names code + assert clean passes
  - test_reject_form_vocab_offmidiom: arrange paired <notes> fixture / act guard / assert fail names code + assert closed set passes
  - test_reject_label_dropped: arrange tag-replaced-label fixture / act guard / assert fail names code + assert label+tag passes
  - test_reject_template_drift: arrange one-tree edit fixture / act parity / assert fail names code + assert synced passes

Tests live in: `add-method/tooling/test_template_form_tags.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): both template trees change byte-identically in the SAME
commit; every edit re-runs the full existing tooling suite (the parsed-seam safety net),
never just the new tests; add.py is read-only for this task.
Code lives in: `.add/tooling/templates/` + `add-method/tooling/templates/` (the .tmpl files) ·
`add-method/tooling/test_template_form_tags.py` + `test_xml_convention.py` (guards)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full tooling suite 551/551 OK (533 pre-existing + 18 new); `add.py audit` clean (46 tasks); `check` 198 passed, 0 failed
- [x] coverage did not decrease — suite grew by 18 behavior tests; zero tests removed or skipped
- [~] no test or contract was altered during build — DISCLOSED RESIDUE (1): the new suite's
      own lean-threshold assert was corrected at build start (speculative `≤8` → the
      contracted "shrank below 12") because the §4 grammar comment + header risk comment are
      pinned immovable by test_declare_grammar_doc / test_high_risk_signal; the frozen §3 was
      NOT touched. (2): a THIRD template tree (src/add_method/_bundled, discovered in build)
      was propagated — §3's MIRRORS clause named two; a superset already enforced by the
      existing triplet tests.
- [x] concurrency / timing of the risky operation is safe — N/A: templates + tests only, no runtime paths
- [x] no exposed secrets, injection openings, or unexpected dependencies — text templates only; zero new packages; add.py untouched
- [x] layering & dependencies follow CONVENTIONS.md — tags additive; every engine seam byte-compatible (proven by the seam suite)
- [x] a person reviewed and approved the change — Tin Dang at this gate, both residues quoted verbatim in chat

### GATE RECORD
Outcome: PASS
Residues accepted as disclosed: (1) lean-threshold correction in the NEW suite implements the
frozen plan's "shrank" against immovable pins; (2) third template tree (_bundled) propagated —
contracted-superset, already triplet-enforced. No security finding.
Reviewed by: Tin Dang · date: 2026-06-07

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): every future task scaffold is production for this feature —
watch: do agents fill INSIDE the tags (scenario "filled region reads non-empty") · inline-fill
occurrences caught by the guard · report-render noise complaints (the accepted ⚠ flag) ·
template_drift failures across the three trees.
Spec delta for the next loop: form tags delimit fill regions but the engine does not yet parse
them — goal #4 (machine-parseable rules) is the natural v-next: a `report` view that reads
<must>/<reject> blocks. If render noise annoys, a tag-stripping change-request against the
v9-1 phase-detail shape is the named path.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] contracts that name mirror trees must enumerate ALL copies — the v18 MIRRORS clause missed the _bundled third tree (evidence: §6 residue 2, discovered in build)
- [TDD · folded] never pin a speculative number before counting the baseline — pin the contracted semantics ("shrank") or count first (evidence: §6 residue 1, the ≤8 lean threshold)
- [ADD · folded] form tags (v18) make fill regions machine-delimited — a future engine feature can parse <must>/<reject> for rule-level reporting without touching templates again (evidence: frozen §3 amendment)
- [DDD · folded] "instruction tags" vs "form tags" entered the ubiquitous language — GLOSSARY should carry both terms at the next fold (evidence: §3 CLASS RULE)
