# TASK: Convert phase guides 0,2-7 to the XML convention

slug: phase-guides-xml · created: 2026-06-06 · stage: mvp
autonomy: auto
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: apply the v16 XML convention (frozen by `xml-convention`) to the 7 remaining phase guides
(`phases/0,2,3,4,5,6,7`). `phases/1-specify.md` is already the converted pilot.
Framings weighed: same-3-tags-as-pilot (chosen) · introduce-constraints/reject_codes-here · per-file-bespoke-vocab

Must:
  - Use ONLY the three tags the pilot uses — `<prompt>` · `<output_format>` · `<exit_gate>`. Reserve
    `<constraints>` / `<reject_codes>` for the engine docs (task 3) per the frozen TAG→FIRST-USE map; do
    not introduce them here (every phase guide's executable blocks are exactly these three shapes).
  - `## AI prompt` → `<prompt>` with PLAIN-TEXT skeleton labels inside (Role:/Read first:/Objective:/
    Steps:/Never:), NO field tags. Convert the existing `>` blockquote FAITHFULLY — every directive
    preserved, none invented; the `## AI prompt` header stays.
  - `## Produce` → `<output_format>` (2-scenarios, 3-contract, 4-tests). `## Exit gate` → `<exit_gate>`
    (all 7 files; 6-verify's combined "## Exit gate / Next" wraps only its `- [ ]` checklist).
  - Files with no `## AI prompt`/`## Produce` (0-setup, 6-verify) get only `<exit_gate>`.
  - Leave ALL narrative prose, `##` headers, tables (e.g. 6-verify's outcome table, 0-setup's lens
    table), bash fences, and every `## Next` as clean markdown.
  - Propagate every edit through all 3 mirrors (canonical `skill/add` → `_bundled/` → `.claude/skills/add`)
    byte-for-byte.
Reject:
  - tag explanatory / teaching prose (e.g. 5-build "The cardinal rule")  -> "narrative_tagged"
  - drop a header a test or cross-ref depends on (esp. `## AI prompt`)    -> "header_dropped"
  - introduce `<constraints>`/`<reject_codes>` or any non-pilot tag here  -> "vocab_offmidiom"
  - put a field-level tag inside `<prompt>` (use plain labels)            -> "field_tag_inside_prompt"
  - edit `skill/add/` without re-syncing the 3 mirrors                    -> "mirror_drift"
After:
  - All 7 guides carry the convention; the extended `test_xml_convention.py` enumerates each file's
    narrative sections and is GREEN; full suite + `add.py audit` + 3-mirror parity pass.
Assumptions — least-sure first:
  ⚠ Restructuring each `> Role: …` blockquote into multi-line skeleton labels stays FAITHFUL (no directive
    added or lost). Least sure because it is a prose rewrite, not a mechanical wrap — meaning could drift.
    If wrong: a phase prompt subtly changes what the agent does. Mitigation: every directive in the source
    blockquote maps 1:1 to a label line; the diff is reviewable per file. Cost if wrong: one doc-only fix.
  - [ ] The three pilot tags cover every executable block in all 7 guides (no guide needs a 4th shape) —
        grounded by the header survey above; residual: 0-setup/6-verify are exit_gate-only, confirmed.
  - [ ] `.claude/skills/add/` stays a byte-exact mirror — `test_tree_parity` + `test_bundle_parity` enforce it.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: every AI prompt converted               # Must: <prompt> blocks
  Given phases 2,3,4,5,7 (the guides that HAVE a "## AI prompt")
  When the convention is applied
  Then each has a <prompt>…</prompt> block whose body carries a plain-text "Role:" label
  And the "## AI prompt" header line still exists in each

Scenario: prompt blocks are block-level           # Reject: field_tag_inside_prompt
  Given any converted phase guide
  When the body inside <prompt>…</prompt> is scanned
  Then it contains NO paired field tags (Role:/Read first:/Steps:/Never: are plain text)

Scenario: produce → output_format                 # Must: <output_format> blocks
  Given phases 2,3,4 (the guides that HAVE a "## Produce")
  When the convention is applied
  Then each "## Produce" section body is wrapped in <output_format>…</output_format>

Scenario: exit gate → exit_gate                    # Must: <exit_gate> blocks
  Given all 7 guides (0,2,3,4,5,6,7)
  When the convention is applied
  Then each carries an <exit_gate>…</exit_gate> block

Scenario: vocabulary stays in the pilot subset     # Reject: vocab_offmidiom
  Given every converted phase guide
  When all paired tags are collected
  Then each tag ∈ {prompt, output_format, exit_gate} (no constraints/reject_codes here)

Scenario: narrative stays prose                    # Reject: narrative_tagged
  Given each guide's enumerated narrative sections (per file, in the test)
  When those sections are scanned
  Then they carry NO paired convention tags
  And every "## Next" and every table stays clean markdown

Scenario: three mirrors agree                       # Reject: mirror_drift
  Given the converted skill/add tree
  When test_bundle_parity and test_tree_parity run
  Then _bundled/skill/add and .claude/skills/add match skill/add byte-for-byte
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

The contract is the per-file APPLICATION of the v16 convention frozen in `xml-convention` §3 (unchanged here).
This task adds NO new vocabulary — it applies the pilot's 3 tags to the 7 guides. The per-file map:

```
PHASE-GUIDE CONVERSION MAP — v16 (applies xml-convention §3; no new tags)

  file                tags applied                        narrative left as prose (enforced per-file)
  phases/0-setup.md   <exit_gate>                         §1·2a·2b·3·4·5 procedure, lens table, ## Next
  phases/2-scenarios  <output_format> <prompt> <exit_gate>  the And-clause note text, ## Next
  phases/3-contract   <output_format> <prompt> <exit_gate>  "## The freeze review checklist", ## Next
  phases/4-tests      <output_format> <prompt> <exit_gate>  "## The must-fail principle", "## Declaring where tests live", ## Next
  phases/5-build      <prompt> <exit_gate>                 "## Work in small batches", "## The cardinal rule", ## Next
  phases/6-verify     <exit_gate>                          Part one, Part two, the outcome TABLE, ## Next (exit_gate wraps only the - [ ] line)
  phases/7-observe    <prompt> <exit_gate>                 "## Do" procedure, ## Next

RULES (inherited, unchanged): block-level only · plain-text labels inside <prompt> · tables & ## headers
& ## Next stay markdown · 3 mirrors byte-identical · every ## AI prompt header preserved.
```

Status: FROZEN @ v16 — approved by Tin Dang, 2026-06-06 (standing authorization for the autonomous v16 run)   <!-- one-approval front. Applies xml-convention §3 verbatim; changing THAT is a change request back to xml-convention. -->
<!-- Least-sure flag at the freeze: ⚠ [spec] the blockquote→skeleton rewrite stays faithful (§1 top assumption);
     a per-file diff review is the cheap check. Nothing else materially uncertain — the tag set is already frozen. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 7 scenarios asserted (content-assertions on the doc files; no runtime to cover by %).
Plan — EXTEND `test_xml_convention.py` with a per-file table (each guide's narrative sections enumerated, so the
over-tagging guard is real, not hollow):
  - PER_FILE map: {file: (has_prompt, has_output_format, narrative_headers[...])} for 0,2,3,4,5,6,7.
  - test_phase_prompts_converted: every guide with has_prompt has a <prompt> block with a plain-text "Role:"
    label and NO field tags, and its "## AI prompt" header survives.
  - test_phase_output_format: every guide with has_output_format wraps "## Produce" in <output_format>.
  - test_phase_exit_gate: all 7 guides carry an <exit_gate> block.
  - test_phase_vocab_subset: every paired tag across the 7 guides ∈ {prompt, output_format, exit_gate}.
  - test_phase_narrative_untagged: each file's enumerated narrative_headers carry NO paired tags.
  - parity: test_bundle_parity + test_tree_parity (reused) assert the 3 mirrors agree.

Tests live in: `add-method/tooling/test_xml_convention.py` · MUST run red (guides not yet converted) before Build.
<!-- RED reason: phases 0,2-7 have no <prompt>/<output_format>/<exit_gate> yet -> the new tests fail. -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): preserve every section header (esp. each `## AI prompt`); keep all 3 trees
byte-identical (canonical `skill/add` → `prepare_bundle.py` → `_bundled/`, then mirror-copy → `.claude/skills/add`).
Code lives in: `add-method/skill/add/phases/{0,2,3,4,5,6,7}.md` + their 2 mirrors.
Constraints: do NOT change any test or the frozen convention; no new tags beyond the pilot's 3; markdown only.

What was built:
  - (filled at build) 7 guides converted; `_bundled/` regenerated; `.claude/skills/add/` copied; md5 identical.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **466 passed / 0 failed** (xml-convention 9/9 incl. 5 new phase-guide tests, test_declare_grammar_doc, both parity guards)
- [x] coverage did not decrease — `test_xml_convention.py` extended (+5 assertions, per-file narrative table); no existing test weakened
- [x] no test or contract was altered during build — the 5 phase-guide tests were authored RED pre-build, made green by the doc edits only; xml-convention §3 untouched
- [x] concurrency / timing — N/A (static markdown docs; no runtime)
- [x] no exposed secrets, injection openings, or unexpected dependencies — markdown-only edits; no security surface; no deps added
- [x] layering & dependencies follow CONVENTIONS — 3 trees byte-identical (per-file md5 verified); only the pilot's 3 tags used
- [x] auto-resolved (autonomy: auto, no residue) — recorded as the accountable run

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved — autonomy: auto, no residue (the autonomous v16 run) · date: 2026-06-06
Note: ordinary doc-transform scope (NOT method-defining — semantics unchanged, only prompt formatting),
applying the already-frozen xml-convention §3. Evidence-auto-gate: all 466 tests green, no test weakened,
no contract touched, 3 mirrors md5-identical, loops dry, no security/concurrency/architecture residue.
Resolved under Tin Dang's standing authorization for the autonomous v16 run.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the per-file narrative table (`PHASE_FILES`) in test_xml_convention — keep it
in sync as task 3 (engine docs) lands; a file converted without its narrative enumerated is an unguarded over-tag risk.
Spec delta for the next loop: the convention scaled to 7 non-uniform guides with NO 6th tag needed — evidence the
frozen 5-tag core (3 used here) holds; task 3's engine docs are where `<constraints>`/`<reject_codes>` first earn use.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] a per-file narrative-enumeration table is the only thing that makes an over-tagging guard real:
  without it a content test sees "tags present" but is blind to tags on prose. (evidence: test_phase_narrative_untagged
  enumerates each guide's narrative sections; the RED run had 0 tags so it trivially passed — the guard only bit once
  conversion added tags, exactly where the table pointed.)
- [TDD · folded] RED-before-build held across 7 files at once: 5 new tests authored failing (no blocks yet) → made green
  by the doc edits alone, no test weakened, suite 461→466. (evidence: the staged RED run showed 4 failures for the
  right reason.)
- [ADD · folded] applying a frozen contract is genuinely lower-risk than authoring it: task 1 was risk:high+conservative
  (defining the convention); task 2 is autonomy:auto (applying it), and the evidence-auto-gate resolved cleanly with
  no residue. The dial tracked the actual risk gradient. (evidence: this gate auto-resolved; task 1's did not.)
