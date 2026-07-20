# TASK: Freeze XML prompt convention + 1-specify pilot

slug: xml-convention · created: 2026-06-06 · stage: mvp · risk: high
autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: XML prompt convention + 1-specify pilot — the frozen rule the other 4 tasks follow.
Framings weighed: targeted-on-actionable-structures (chosen) · wholesale-wrap-everything · markdown-only-no-XML

Must:
  - Define a CLOSED, BLOCK-LEVEL vocabulary — 5 tags marking block boundaries only (no field children,
    no nesting). Inside <prompt>, the appendix-b skeleton labels (Role:/Read first:/Steps:/Never:) stay
    PLAIN TEXT. Every tag maps to a real surveyed structure (the §3 first-use map) — none is speculative.
    CLOSED lean core, 5 tags, ALL-underscore:
    `<prompt>` · `<exit_gate>` · `<constraints>` · `<reject_codes>` · `<output_format>`.
  - State the dual-audience boundary: XML marks the 5 executable BLOCKS; prose, the in-<prompt> labels,
    `##` headers, tables, and the `## Next` step stay clean markdown.
  - FULLY convert `add-method/skill/add/phases/1-specify.md` as the complete worked reference —
    `## AI prompt`→`<prompt>` (plain-text labels inside), `## Produce`→`<output_format>`, `## Exit gate`→`<exit_gate>`;
    `## Co-specify…`, `## The least-sure flag…`, and `## Next` stay prose. Byte-for-byte mirrored to all 3 trees.
  - Preserve every section header the suite/cross-refs depend on (esp. `## AI prompt` — test_declare_grammar_doc).
Reject:
  - tag explanatory / teaching prose                       -> "narrative_tagged"
  - drop a header a test or cross-reference depends on      -> "header_dropped"
  - edit `skill/add/` without re-syncing the 3 mirrors      -> "mirror_drift"
  - introduce a tag outside the frozen vocabulary           -> "vocab_offmidiom"
  - put a field-level tag inside <prompt> (use plain labels) -> "field_tag_inside_prompt"
After:
  - The convention is frozen (TASK §3); `1-specify.md` is fully converted in all 3 mirrors; a content
    test enforces the convention on the pilot and is GREEN; the full suite + audit pass.
Assumptions — least-sure first:
  ⚠ Block-level (no field children) is enough structure for the agent — the boundary marks "adopt this",
    and appendix-b's plain-text labels (Role:/Steps:/Never:) already read clearly. Least sure because a
    field-level scheme would be more machine-parseable. If wrong: a later task amends the frozen list to
    re-introduce children (recorded change-request back here — never a silent new tag). Chosen for lean.
  - [ ] The 5 blocks cover every recurring structure across the 18+ files — grounded by the full-surface
        survey + first-use map (§3); residual: an engine doc needs a 6th block → one recorded amendment.
  - [ ] `.claude/skills/add/` stays a byte-exact mirror (no Claude-only divergence) — confirm: the
        empty `diff -rq` today says yes; `test_tree_parity` enforces it.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: pilot fully converted                  # Must: the complete worked reference
  Given add-method/skill/add/phases/1-specify.md
  When the convention is applied
  Then it has a <prompt> block whose body carries plain-text labels (Role:, Never:), an <output_format>, and an <exit_gate>
  And the "## AI prompt" header line still exists

Scenario: prompt block is block-level            # Reject: field_tag_inside_prompt
  Given the converted 1-specify.md
  When the body inside <prompt>…</prompt> is scanned
  Then it contains NO paired field tags (Role:/Read first:/… are plain text)
  And only block-boundary tags are used

Scenario: header preserved                       # Reject: header_dropped
  Given the converted 1-specify.md
  When test_declare_grammar_doc runs
  Then it still finds "## AI prompt" after the section heading it checks
  And the test passes unchanged

Scenario: vocabulary stays in-set               # Reject: vocab_offmidiom
  Given the converted 1-specify.md
  When every paired XML tag in the file is collected
  Then each tag name is one of the 5 frozen block tags
  And no out-of-set tag appears

Scenario: narrative stays prose                  # Reject: narrative_tagged
  Given the converted 1-specify.md
  When the genuinely-narrative sections are scanned
  Then "## Co-specify in three moves" and "## The least-sure flag is bundle-wide" carry NO XML tags
  And only the four actionable sections are tagged

Scenario: three mirrors agree                    # Reject: mirror_drift
  Given the converted skill/add tree
  When test_bundle_parity and test_tree_parity run
  Then _bundled/skill/add and .claude/skills/add match skill/add byte-for-byte
  And both parity tests pass
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

The contract is the CONVENTION (not an HTTP shape). The other 4 tasks build against this frozen spec.

```
XML PROMPT CONVENTION — v16

VOCABULARY (CLOSED lean core — 5 BLOCK-LEVEL tags, ALL-underscore; additions only by amending this frozen list, never silent).
Tags mark block BOUNDARIES only: NO field-level child tags, NO nesting. Inside <prompt>, the appendix-b
master skeleton labels stay PLAIN TEXT (Role:/Read first:/Objective:/Steps: with "# why:"/Never:/Evidence:).
The XML's whole job is to say "this block is the instruction to adopt"; the proven labels stay readable.
  <prompt>        an "## AI prompt" / playbook role block — adopt-this-instruction. Plain-text skeleton labels inside.
  <exit_gate>     a phase exit checklist             (the "## Exit gate" section / skeleton "Exit:")
  <constraints>   hard rules / a MUST·MUST-NOT boundary (subsumes method-level non-negotiables)
  <reject_codes>  an enumerated reject/error-code set the agent emits/chooses
  <output_format> the shape to emit or reproduce      (subsumes the old "## Produce"; freeform content)

TAG → FIRST-USE MAP (every tag is grounded in a real surveyed structure — none speculative):
  <prompt>        phases/1-specify.md "## AI prompt" (PILOT) · all 6 phase AI-prompts · appendix-b playbook
  <exit_gate>     phases/1-specify.md "## Exit gate" (PILOT) · all 7 "## Exit gate" sections
  <output_format> phases/1-specify.md "## Produce" (PILOT) · phases 2,3,4 "## Produce" · report-template "five blocks" · intake `{ bucket, rationale, command }`
  <constraints>   SKILL.md "Non-negotiable rules" · run.md touch-boundary (MAY/MUST NOT) · streams.md "MUST NOT"
  <reject_codes>  intake.md reject codes · scope.md "Reject codes" · run.md unguarded_high_risk_auto · deltas.md statuses

BOUNDARY RULE (dual-audience):
  TAG only the 5 agent-EXECUTABLE BLOCKS above. LEAVE clean markdown: prose, the in-<prompt> skeleton labels,
  "##" section headers, tables, code fences, the "## Next" step. A "## AI prompt" header stays; the <prompt>
  block goes INSIDE it. Headers are never replaced by tags.

DISAMBIGUATION (convention tags vs prose placeholders — they never collide):
  A convention tag is ALWAYS PAIRED — an opening <x> with a matching closing </x>.
  The ADD docs already use single, UNPAIRED angle-brackets as prose placeholder notation
  (`<name>`, `<why>`, `<cost>`, `<error_code>`, `<assumption>`). These are NOT convention tags
  and are left untouched. Enforcement keys on the pair: only a paired tag is checked against VOCAB.

FORMATTING:
  - Each of the 5 tags occupies its own line (open and close); the block content sits between, as markdown.
  - No XML declaration, no namespaces, no attributes, no nesting.
  - Preserve existing inline markdown (bold, `code`, "·", "# why:") inside the block.

REJECT CODES: narrative_tagged · header_dropped · mirror_drift · vocab_offmidiom · field_tag_inside_prompt

ENFORCEMENT: add-method/tooling/test_xml_convention.py asserts the pilot's block-level <prompt> (plain-text
  labels, no field tags) + header survival + in-set vocabulary; test_bundle_parity + test_tree_parity assert
  the 3 mirrors agree.
```

Status: FROZEN @ v16 — approved by Tin Dang, 2026-06-06 (standing authorization for the autonomous v16 run)   <!-- one-approval front. Changing this = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 6 scenarios asserted (content-assertions; no behavior to cover by %).
Plan (asserting the file content not internals; test_pilot_fully_converted covers both the "fully
converted" and "block-level" scenarios via its plain-text-labels + no-field-tags checks):
  - test_pilot_fully_converted: read 1-specify.md / assert a <prompt> block whose body has plain-text
    Role:/Never: labels and NO field tags, AND an <output_format> and an <exit_gate> ("## Next" stays markdown).
  - test_ai_prompt_header_preserved: assert the literal "## AI prompt" header line still exists
    (guards test_declare_grammar_doc's precondition).
  - test_vocab_in_set: collect every PAIRED tag in the file / assert each ∈ the 5-tag frozen VOCAB.
    (This also enforces block-level: a stray <role>/<objective> would fail here.)
  - test_narrative_untagged: assert "## Co-specify in three moves" and "## The least-sure flag is
    bundle-wide" carry no paired tags (genuine narrative stays prose).
  - parity: test_bundle_parity + test_tree_parity already assert the 3 mirrors agree (reused, not re-authored).

Tests live in: `add-method/tooling/test_xml_convention.py` · MUST run red (pilot not yet converted) before Build.
<!-- token with "/" = project root: the durable guard ships with the package suite + runs in CI. -->
<!-- RED reason: 1-specify.md has no <prompt> block yet -> test_pilot_fully_converted / test_vocab_in_set fail. -->

<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): preserve every section header; keep all 3 trees byte-identical
(canonical `skill/add` → `prepare_bundle.py` → `_bundled/`, then mirror-copy → `.claude/skills/add`).
Code lives in: `add-method/skill/add/phases/1-specify.md` (the converted pilot) + its 2 mirrors.
Constraints: do NOT change any test or the frozen convention; no new deps (markdown only).

What was built:
  - `## AI prompt`→`<prompt>` (plain-text Role:/Read first:/Objective:/Steps:/Never: inside, no field tags)
  - `## Produce`→`<output_format>` · `## Exit gate`→`<exit_gate>`
  - `## Co-specify…`, `## The least-sure flag…`, `## Next`, all headers → unchanged prose
  - regenerated `_bundled/` + copied to `.claude/skills/add/` → md5 identical across all 3 trees

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **461 passed / 0 failed** (incl. `test_xml_convention` 4/4, `test_declare_grammar_doc`)
- [x] coverage did not decrease — `test_xml_convention.py` ADDED (+4 assertions); no existing test weakened
- [x] no test or contract was altered during build — test authored RED pre-build, made green by the doc edit only; convention frozen, untouched
- [x] concurrency / timing — N/A (static markdown doc; no runtime, no concurrency)
- [x] no exposed secrets, injection openings, or unexpected dependencies — markdown-only edit; no security surface; no deps added
- [x] layering & dependencies follow CONVENTIONS — the new convention IS the artifact; 3 trees byte-identical (md5 dc52f13…)
- [x] a person reviewed and approved the change — Tin Dang gave standing authorization for the
      autonomous v16 run ("fully autonomous … until archive milestone", 2026-06-06); the
      conservative + risk:high gate stays human-owned and is resolved under that decision, NOT a
      per-diff sign-off

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved under standing authorization (Tin Dang, 2026-06-06) · date: 2026-06-06
Note: conservative + risk:high keeps the gate human-owned; resolved under Tin Dang's standing
authorization for the autonomous v16 run, NOT a per-diff sign-off. Doc-only refactor — no runtime,
secret, or injection surface (security line clean, unmarked). Suite 461 passed / 0 failed incl.
test_xml_convention 4/4 and test_declare_grammar_doc; 3 mirrors md5-identical. The autonomous run
is the accountable owner; the human authorized the cadence, not each diff.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->
<!-- No security finding: doc refactor, no runtime/secret/injection surface — a normal gate, not a HARD-STOP. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the per-file narrative enumeration in `test_xml_convention.py` —
as tasks 2–4 convert more files, does over-tagging creep in (a tag on a section the guard never
enumerated)? The guard is only as strong as the narrative list it knows about.
Spec delta for the next loop: the 5-tag vocabulary may need a 6th block if an engine doc carries a
recurring executable structure none of the 5 cover — that is a recorded change-request back to this
frozen list (`vocab_offmidiom`), never a silent new tag.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] a CLOSED notation needs a disambiguation rule when it collides with notation already in
  the prose — the convention tags `<x>…</x>` collided with existing `<name>`/`<why>`/`<cost>` prose
  placeholders; resolved by the PAIRED-tag rule (a convention tag is the intersection of open∩close).
  (evidence: test_vocab_in_set first flagged 3 placeholders before the rule was added.)
- [ADD · folded] tests-green ≠ faithful conversion: a content-shape guard cannot see over-tagging the
  spec never enumerated, so for non-uniform engine docs the sole-reviewer risk is real — the per-file
  narrative list must GROW with each task or the over-tagging guard is hollow. (evidence: advisor
  flagged this as the live risk for autonomous tasks 3–4.)
- [UDD · folded] a prompt file is dual-audience (agent + human); over-tagging hurts the human reader, so
  leanness is a UX constraint, not only a style one — the vocabulary was driven from a field-level
  scheme down to 5 block-level tags to keep the prose readable. (evidence: the chosen block-level core.)
- [TDD · folded] RED-before-build holds even for a doc refactor with no runtime: the guard was authored
  failing (pilot unconverted) then made green by the doc edit alone, no test weakened. (evidence:
  test_xml_convention RED→GREEN, suite 461/0, no existing test touched.)
