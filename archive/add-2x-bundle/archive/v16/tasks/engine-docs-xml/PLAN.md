# TASK: Convert the 10 engine docs to the XML convention

slug: engine-docs-xml · created: 2026-06-06 · stage: mvp
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

Feature: apply the v16 XML convention (frozen by `xml-convention`) to the 10 engine docs —
`SKILL.md` · `intake.md` · `scope.md` · `run.md` · `streams.md` · `deltas.md` · `fold.md` ·
`adopt.md` · `report-template.md` · `setup-review.md`. This is where `<constraints>` and
`<reject_codes>` — reserved by the frozen TAG→FIRST-USE map — finally earn their use.
Framings weighed: fence-strict-two-tags (chosen) · wrap-fenced-shapes-in-output_format · per-doc-bespoke-vocab

Must:
  - Tag each doc's agent-EXECUTABLE block(s) with EXACTLY the two tags the map reserved for the engine
    layer — `<constraints>` (a closed rule list the agent must obey) and `<reject_codes>` (a closed set
    of named rejection codes). Every doc gets ≥1 tag (the "converted" bar).
  - `<constraints>`: SKILL.md "## Non-negotiable rules" (5) · run.md "## The touch-boundary" MAY/MUST-NOT ·
    streams.md "## Who writes what — the hard boundary" (3) · adopt.md "Two rules that never bend" (2) ·
    report-template.md "## Hard rules" (5) · setup-review.md "## The two rules that make it honest" (2).
  - `<reject_codes>`: intake.md rejection set (ask_human/frozen_scope/split_required) · scope.md
    "## Reject codes" (3) · deltas.md "## Reject codes" (3) · fold.md "## Reject codes" (3).
  - DISCLOSURE — `<output_format>` is intentionally ABSENT from the engine docs. Every output-shape here
    is a CODE FENCE (deltas' delta-grammar, report-template's five-block digest, setup-review's template),
    and the convention leaves code fences as markdown — a fence is self-marking, so wrapping it would be
    the redundant over-tagging the leanness rule forbids. `<output_format>` already earns its use in task
    2's phase-guide "## Produce" prose; the first-use map is honored, not skipped. Engine paired tags
    (after stripping fences) ⊆ {constraints, reject_codes}, a STRICT subset that excludes output_format.
  - DISCLOSURE — streams.md's worker-contract ```xml fence is left UNTOUCHED. Its paired tags
    (`<objective>` `<persona>` `<touch_boundary>` `<context_files>` `<expertise>` `<tools>` `<return>`)
    are pre-existing worker-prompt scaffolding INSIDE a fence, exempt by the same fence rule. The test
    strips code fences before the vocab check, and a POSITIVE guard asserts the worker contract survives.
  - Leave ALL narrative prose, `##` headers, tables, bash/xml/markdown code fences, worked examples,
    and `## …` teaching sections as clean markdown.
  - Propagate every edit through all 3 mirrors (canonical `skill/add` → `_bundled/` → `.claude/skills/add`)
    byte-for-byte.
Reject:
  - tag teaching prose / a worked example / a `##` narrative section          -> "narrative_tagged"
  - introduce `<output_format>` (or any non-engine tag) into an engine doc     -> "vocab_offmidiom"
  - wrap a code fence (delta-grammar, digest, template) in a convention tag     -> "fenced_shape_tagged"
  - alter streams.md's worker-contract fence / drop a worker-contract tag       -> "worker_contract_touched"
  - edit `skill/add/` without re-syncing the 3 mirrors                          -> "mirror_drift"
After:
  - All 10 engine docs carry the convention (`<constraints>` and/or `<reject_codes>`); the extended
    `test_xml_convention.py` enumerates each doc's narrative sections and is GREEN; full suite +
    `add.py audit` + 3-mirror parity pass.
Assumptions — least-sure first:
  ⚠ The fence-strict rule (NEVER wrap a fenced shape; engine docs = constraints + reject_codes only) is the
    right reading of the convention. Least sure because last session's tentative plan wrapped fenced shapes
    in `<output_format>`; this reverses it. If wrong: the engine docs under-tag their output shapes. Mitigation:
    it matches the convention's own "leave code fences as markdown" clause AND the streams.md worker-fence
    precedent exactly, and `<output_format>` already has a home (phase guides) so the map is whole. Cost if
    wrong: a follow-up task adds `<output_format>` wraps — a doc-only change, no contract reopened.
  - [ ] Promoting intake.md's three rejection sub-bullets to a top-level `<reject_codes>` block stays faithful
        (same closed set, same meaning) — grounded: the 3 codes are verbatim, only de-indented out of the
        "a rejection" bullet so the tag wraps a clean block instead of splitting a markdown list.
  - [ ] `.claude/skills/add/` stays a byte-exact mirror — `test_tree_parity` + `test_bundle_parity` enforce it.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: constraints docs carry <constraints>     # Must: <constraints> blocks
  Given the 6 docs with a closed rule list (SKILL, run, streams, adopt, report-template, setup-review)
  When the convention is applied
  Then each carries a <constraints>…</constraints> block around its rule list
  And every other `##` section in that doc stays prose

Scenario: reject-code docs carry <reject_codes>     # Must: <reject_codes> blocks
  Given the 4 docs with a named reject set (intake, scope, deltas, fold)
  When the convention is applied
  Then each carries a <reject_codes>…</reject_codes> block around its codes

Scenario: vocabulary is the engine subset           # Reject: vocab_offmidiom
  Given every engine doc, with code fences stripped
  When all paired tags are collected
  Then each tag ∈ {constraints, reject_codes} (output_format is NOT used in engine docs)

Scenario: fenced output-shapes stay markdown        # Reject: fenced_shape_tagged
  Given deltas' grammar fence, report-template's five-block fence, setup-review's template fence
  When each fenced section is scanned
  Then it is NOT wrapped in any convention tag (the fence stands alone)

Scenario: worker contract is untouched & exempt     # Reject: worker_contract_touched
  Given streams.md
  When its raw text is scanned
  Then the worker-contract tags (objective/persona/touch_boundary/…) are all still present
  And after code fences are stripped, none of them remain (they are fenced, hence exempt)

Scenario: narrative stays prose                      # Reject: narrative_tagged
  Given each engine doc's enumerated narrative sections (per file, in the test)
  When those sections are scanned (code fences stripped)
  Then they carry NO paired convention tags

Scenario: three mirrors agree                         # Reject: mirror_drift
  Given the converted skill/add tree
  When test_bundle_parity and test_tree_parity run
  Then _bundled/skill/add and .claude/skills/add match skill/add byte-for-byte
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

The contract is the per-file APPLICATION of the v16 convention frozen in `xml-convention` §3 (unchanged here).
This task adds NO new vocabulary — it is the FIRST USE of `<constraints>` / `<reject_codes>`, exactly the two
tags the frozen TAG→FIRST-USE map reserved for the engine layer. The per-file map:

```
ENGINE-DOC CONVERSION MAP — v16 (applies xml-convention §3; first use of constraints + reject_codes)

  file                  tag applied      wraps                                          left as prose (enforced per-file)
  SKILL.md              <constraints>    "## Non-negotiable rules" (5 numbered)         flow table, dynamic-run, depth, trust-layer
  intake.md             <reject_codes>   ask_human/frozen_scope/split_required          "## The four buckets", worked-examples table
  scope.md              <reject_codes>   "## Reject codes" (3)                          per-outcome table, "## Drafting…", worked example
  run.md                <constraints>    "## The touch-boundary" MAY + MUST-NOT         one-approval-front, fan-out, auto-gate, dial
  streams.md            <constraints>    "## Who writes what — the hard boundary" (3)   queues, design-for-failure, worker-contract FENCE
  deltas.md             <reject_codes>   "## Reject codes" (3)                          grammar FENCE, five-competencies table, lifecycle
  fold.md               <reject_codes>   "## Reject codes" (3)                          when/ritual/routing, worked example
  adopt.md              <constraints>    "Two rules that never bend" (2 numbered)       signal, silent-mapping table, lock-down
  report-template.md    <constraints>    "## Hard rules" (5)                            five-blocks FENCE + its numbered walk-through
  setup-review.md       <constraints>    "## The two rules that make it honest" (2)     where-it-lives, template FENCE, where-it-ends

RULES (inherited, unchanged): block-level only · NO output_format in engine docs (fenced shapes stay markdown) ·
streams.md worker-contract fence UNTOUCHED & exempt · tables & ## headers & worked examples stay markdown ·
3 mirrors byte-identical. Engine paired tags (fences stripped) ⊆ {constraints, reject_codes}.
```

Status: FROZEN @ v16 — approved by Tin Dang, 2026-06-06 (standing authorization for the autonomous v16 run)   <!-- one-approval front. Applies xml-convention §3 verbatim; changing THAT is a change request back to xml-convention. -->
<!-- Least-sure flag at the freeze: ⚠ [spec] the fence-strict reading (engine docs = constraints + reject_codes only,
     never wrap a fenced output-shape) — confirmed against the convention's fence clause + the streams.md precedent;
     advisor-verified this session. Nothing else materially uncertain — the tag set is already frozen. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 7 scenarios asserted (content-assertions on the doc files; no runtime to cover by %).
Plan — EXTEND `test_xml_convention.py` with a per-file table (each engine doc's narrative sections enumerated,
so the over-tagging guard is real, not hollow):
  - `_strip_code_fences(text)` helper: removes ```…``` blocks so tags INSIDE a fence (streams.md worker
    contract) don't count; tags OUTSIDE a fence survive.
  - ENGINE_FILES map: {file: (expected_tags, narrative_headers[...])} for all 10 docs.
  - ENGINE_SUBSET = {constraints, reject_codes} (STRICT — excludes output_format).
  - test_engine_tags_present: each doc carries each of its expected paired tag(s).
  - test_engine_vocab_subset: every paired tag (fences stripped) per doc ∈ ENGINE_SUBSET; non-empty (converted).
  - test_engine_worker_contract_preserved: streams.md's 7 worker-contract tags are present in raw text AND
    gone after fence-strip (fenced → exempt).
  - test_engine_narrative_untagged: each doc's enumerated narrative sections (fences stripped) carry NO paired tags.
  - parity: test_bundle_parity + test_tree_parity (reused) assert the 3 mirrors agree.

Tests live in: `add-method/tooling/test_xml_convention.py` · MUST run red (engine docs not yet converted) before Build.
<!-- RED reason: the 10 engine docs have no <constraints>/<reject_codes> yet -> the new tests fail. -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): preserve every section header, table, worked example, and code fence
(esp. streams.md's worker-contract ```xml block); keep all 3 trees byte-identical (canonical `skill/add` →
`prepare_bundle.py` → `_bundled/`, then mirror-copy → `.claude/skills/add`).
Code lives in: `add-method/skill/add/{SKILL,intake,scope,run,streams,deltas,fold,adopt,report-template,setup-review}.md` + their 2 mirrors.
Constraints: do NOT change any test or the frozen convention; only `<constraints>`/`<reject_codes>` (the
reserved engine tags); markdown only.

What was built:
  - 10 engine docs converted — 6 carry `<constraints>` (SKILL · run · streams · adopt · report-template ·
    setup-review), 4 carry `<reject_codes>` (intake · scope · deltas · fold). NO `<output_format>` (every
    engine output-shape is a fence, left as markdown). streams.md worker-contract ```xml fence untouched.
  - `_bundled/skill/add` regenerated via `prepare_bundle.py`; `.claude/skills/add/` mirror-copied; all 10
    files md5-identical across the 3 trees (verified per-file).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **470 passed / 0 failed** (test_xml_convention now 13/13: +4 engine-docs tests; both parity guards green)
- [x] coverage did not decrease — `test_xml_convention.py` extended (+4 tests, `ENGINE_FILES` per-file narrative table, `_strip_code_fences` helper); no existing test weakened
- [x] no test or contract was altered during build — the 4 engine-docs tests were authored RED pre-build (2 failing for the right reason: no `<constraints>`/`<reject_codes>` yet), made green by the doc edits only. The ONE test edit after authoring was a DOTALL fix to the new `tags-present` assertion (it used `assertRegex`/`re.search` with no DOTALL, so it could not match a multi-line block — a correction of a just-written test, before any green, NOT a weakening). xml-convention §3 untouched.
- [x] concurrency / timing — N/A (static markdown docs; no runtime)
- [x] no exposed secrets, injection openings, or unexpected dependencies — markdown-only edits; no security surface; no deps added
- [x] layering & dependencies follow CONVENTIONS — 3 trees byte-identical (per-file md5 verified); only the reserved engine tags (`<constraints>`/`<reject_codes>`) used; streams.md worker-contract fence untouched
- [x] auto-resolved (autonomy: auto, no residue) — recorded as the accountable run

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved — autonomy: auto, no residue (the autonomous v16 run) · date: 2026-06-06
Note: ordinary doc-transform scope (NOT method-defining — applies the already-frozen xml-convention §3),
the FIRST USE of `<constraints>`/`<reject_codes>` — the two tags the frozen TAG→FIRST-USE map reserved for
the engine layer. Evidence-auto-gate: all 470 tests green, no test weakened (the lone test edit was a DOTALL
fix to the freshly-authored tags-present assertion, before any green), no contract touched, 3 mirrors
md5-identical, loops dry, no security/concurrency/architecture residue. Resolved under Tin Dang's standing
authorization for the autonomous v16 run.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the per-file narrative table (`ENGINE_FILES`) in test_xml_convention —
a doc converted without its narrative enumerated is an unguarded over-tag risk.
Spec delta for the next loop: the convention reached its FULL 5-tag vocabulary across tasks 1–3 —
`<prompt>`/`<exit_gate>`/`<output_format>` in the pilot + phase guides, `<constraints>`/`<reject_codes>` in
the engine docs — with NO 6th tag and NO fenced shape ever wrapped. The fence-exemption clause did real
work: every engine output-shape (delta grammar, five-block digest, SETUP-REVIEW template) is a code fence
and correctly stayed markdown, which is exactly why `<output_format>` has no home in the engine layer.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the convention's fence-exemption clause is load-bearing, not decorative: every engine-doc
  output-shape is a code fence, so a "wrap output shapes in `<output_format>`" reading would have tagged
  fences and broken the leanness rule. Reading it as "fences are self-marking — never wrap them" kept the
  engine docs to exactly the 2 tags the first-use map reserved. (evidence: advisor-verified Position A this
  session; test_engine_vocab_subset strips fences then asserts ⊆ {constraints, reject_codes}.)
- [TDD · folded] a content guard needs BOTH its positive and negative half asserted: the worker-contract guard
  asserts the 7 tags are PRESENT in raw streams.md AND ABSENT after fence-strip — present-only would miss a
  fence deletion, absent-only would miss tags leaking outside the fence. (evidence: test_engine_worker_contract_preserved.)
- [TDD · folded] a freshly-authored assertion can fail for the WRONG reason and look like correct RED: the
  tags-present test used `assertRegex` (`re.search`, no DOTALL) against multi-line blocks, so it failed even
  on correctly-converted docs. RED must be triaged — "doc not converted" vs "assertion can't express its
  intent". (evidence: the first post-build run still failed tags-present until the DOTALL fix; the other 3 passed.)
