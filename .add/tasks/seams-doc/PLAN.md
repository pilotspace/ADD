# TASK: Seed .add/SEAMS.md with the 5 ranked cross-cutting conventions

slug: seams-doc · created: 2026-07-01 · stage: mvp
milestone: seams
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/engine_pin.py:13` (`ENGINE_MD5`) / `:15` (`ENGINE_PKG_MD5`) · `add-method/tooling/test_engine_repin_parity.py:40` (`ENGINE_COPIES`) / `:57` (`test_three_engines_byte_identical_and_current`) · `add-method/tooling/test_tree_parity.py:20` (`CANON_SKILL`) · `add-method/tooling/test_bundle_parity.py` · `add-method/tooling/test_book_parity.py` · `add-method/tooling/add.py:4433` (`_declared_scope`) · `add-method/tooling/add_engine/taskdoc.py:159` (`_phase_spans`) / `:185` (`_raw_phase_bodies`) · `add-method/tooling/add_engine/predicates.py:47` (`_section_unfilled`) · NEW file `.add/SEAMS.md` (does not yet exist) · `.add/GLOSSARY.md` (amend) · NEW `add-method/tooling/test_seams_doc.py`.
Context (working folder): `.add/milestones/seams/MILESTONE.md` (frozen Scope/rationale, the 5 seed candidates) · `.add/personas/methodology-engine-dev.md` (persona embodied — every candidate anchor is an engine internal) · `.add/tasks/rule-id-coverage/TASK.md` (its own §7 Spec-delta narrates itself as the 3rd task to self-heal the scope-token-grammar bug — cited as the source for that entry's Citations field, since generic-phrase grep over-matches).
Honors (patterns / conventions): GLOSSARY-style term definition + `Survivor layer` list convention (`.add/GLOSSARY.md`) · book-technical-writer's "5-second test" for one-paragraph Contract fields · a reproducible-evidence convention (method + as-of SHA + named examples, never a bare number) invented for this task's own Citations field since no prior art existed for it.
Anchors the contract cites: `add-method/tooling/engine_pin.py:13,15` · `add-method/tooling/test_engine_repin_parity.py:40,57` · `add-method/tooling/test_tree_parity.py:20` · `test_bundle_parity.py` · `test_book_parity.py` · `add-method/tooling/add.py:4433` (`_declared_scope`) · `add_engine/taskdoc.py:159,185` · `add_engine/predicates.py:47` (`_section_unfilled`).
Issues/Risks (→ feed §1): fresh verification OVERTURNED 3 of the milestone's 5 seed numbers/anchors — (1) ENGINE_MD5 checklist prose does NOT live in `.claude/skills/add/*.md` guides as the milestone claimed (zero grep hits); it lives in `.add/personas/methodology-engine-dev.md`'s "Engine-change checklist," and citation count is 160 files/1059 mentions (not ~130/291); (5) `_section_unfilled` is cited in 14 files, not 3 — the milestone's "3" appears to have counted only full-truth-table restatements (subjective), conflated with citation count (objective) · raw substring grep is a weak proxy for "cited the convention" (`"byte-identical"` alone hits 232 files; `ENGINE_MD5` boilerplate hits nearly every engine task's Scope line) — Citations fields must name the exact grep method used, not just a bare count · GFM heading→anchor slugification is renderer-dependent, which matters because `seams-template-wiring` will hardcode `.add/SEAMS.md#<entry>` — resolved by mandating a bare kebab-case heading id (M3) so the heading text IS the anchor slug, verbatim · no mechanical way to verify "≥2 DIFFERENT milestones" since older tasks don't all carry a `milestone:` header — stays a named, human/AI-judged claim per the milestone's own "not an automated miner" decision, never a grep gate.
Related intent: `.add/milestones/seams/MILESTONE.md` goal + rationale (PR40 audit item 4, "knowledge siloed per file") + its "Shared/risky contracts" line naming this task's entry-format grammar as frozen-first for `seams-template-wiring`.
Ground SHA: `c152945`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Seed `.add/SEAMS.md` — the project-level cross-cutting-convention registry — plus a `.add/GLOSSARY.md` delta and a shape-asserting test suite.
Framings weighed: per-entry `##`-heading + 4 fixed prose fields (Name/Anchor/Contract/Citations) (chosen — a bare kebab-case heading doubles as a renderer-proof anchor slug) · GLOSSARY-style single dense line per entry (rejected — can't hold a real path:line + a reproducible citation method + named examples without an unreadable run-on, breaking the 5-second test) · a Markdown table with name/anchor/contract/citations columns (rejected — a one-paragraph Contract statement doesn't survive a table cell, and multi-anchor entries like three-tree-parity cite 4 files each, which doesn't fit one cell).
Must:
<must>
  - M1: exactly ONE file, `.add/SEAMS.md`, project-level (sibling to PROJECT.md/GLOSSARY.md) — never one file per milestone (that shape was already explicitly rejected).
  - M2: the file opens with an H1 title + one intro blockquote stating the evidence bar (≥2 DIFFERENT milestones) and the citation grammar a task uses to reference an entry.
  - M3: each entry is a `## <id>` heading where `<id>` is a bare kebab-case token — the heading text IS the anchor slug, verbatim, so `.add/SEAMS.md#<id>` never depends on a renderer's slugification of punctuation/case/slashes.
  - M4: each entry's `Anchor:` field cites ≥1 real, backticked `path:line` naming a symbol that resolves in the CURRENT tree (multi-anchor entries list all of them, ` · `-separated).
  - M5: each entry's `Contract:` field is exactly ONE paragraph (no bullets) stating the shared rule every citing task must honor.
  - M6: each entry's `Citations:` field states the COUNT, the reproducible METHOD (a literal grep/query command, backticked), the as-of SHA/date, and ≥2 named example task slugs — never a bare number with no way to reproduce or spot-check it.
  - M7: the file is seeded at creation with the milestone's 5 ranked candidates, in the SAME rank order the milestone assigned (duplication + error-cost weighted) — not a mechanical citation-count sort, so a low-count/high-risk entry (scope-token-grammar, 3 citations) isn't buried under a high-count/low-risk one (three-tree-parity, 232).
  - M8: `.add/GLOSSARY.md` gains a `Seam:` headword and an amended `Survivor layer:` line (adds SEAMS to the existing CONVENTIONS/GLOSSARY/MODEL_REGISTRY/allowlist list).
</must>
Reject:
<reject>
  - an entry whose only citing tasks share ONE milestone -> "same_milestone_repeat"
  - an entry's Anchor path:line/symbol does not exist in the tree -> "unverifiable_anchor"
  - an entry heading is prose/Title-Case, not a bare kebab-case id -> "unstable_anchor_slug"
  - a Citations field with a bare number, no method, no examples -> "uncited_count"
  - a second SEAMS.md scoped under `.add/milestones/<x>/` -> "milestone_scoped_seams_file"
  - an entry rendered as a graph/JSON/YAML node instead of prose -> "graph_node_seam"
</reject>
After:
<after>
  - `.add/SEAMS.md` exists with 5 entries, each carrying a resolvable anchor + a reproducible citation count, in the milestone's ranked order.
  - `.add/GLOSSARY.md` defines `Seam` and lists SEAMS.md under Survivor layer.
  - a future task's §0 GROUND can write `Seams consulted: .add/SEAMS.md#<id>` and the anchor resolves in every common Markdown renderer (GitHub, MkDocs, plain-text grep) without depending on heading-slugification behavior.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the citation-count NUMBERS being frozen (160/178, 232, 14, 26, 3) are grep-snapshot artifacts as of `c152945` and will already be stale the moment the next task lands — lowest confidence because this is inherent to the artifact, not a mistake fixable by re-checking harder; mitigated by M6 (method + as-of SHA recorded, so staleness is detectable, not silent) but not eliminated. If ignored: a reader trusts a frozen number as current truth years later — cost is low, it's clearly labeled "as of."
  - [ ] whether the `.add/GLOSSARY.md` edit (M8) belongs in THIS task vs. a follow-up — judged in-scope since it's small and serves this task's own new vocabulary; the milestone's frozen Scope text for `seams-doc` doesn't explicitly name GLOSSARY.md. Cheap to strip from Scope at build time if the human disagrees.
  - [x] entry ordering by milestone-assigned rank (not raw count) — confirmed: preserves the "single most error-prone entry" framing for scope-token-grammar despite its low count.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: SEAMS.md is the one project-level file   # M1
  Given the seams milestone ships this task
  When `.add/SEAMS.md` is created
  Then it is the ONLY seams file in the repo
  And no `.add/milestones/*/SEAMS.md` exists

Scenario: File opens with title + evidence-bar intro   # M2
  Given `.add/SEAMS.md` is opened
  When the first lines are read
  Then an H1 title and one blockquote state the ≥2-different-milestones evidence bar
  And the `Seams consulted:` citation grammar is named

Scenario: Entry heading is a bare kebab-case anchor id   # M3
  Given the 5 seeded entries
  When each `## ` heading is inspected
  Then it matches `^## [a-z0-9-]+$` with no spaces/punctuation/uppercase
  And `.add/SEAMS.md#<that-exact-string>` is a valid anchor in GitHub, MkDocs, and plain grep alike

Scenario: Anchor resolves in the current tree   # M4
  Given the `engine-md5-repin` entry's Anchor `add-method/tooling/engine_pin.py:13`
  When the file is opened at that line
  Then the cited symbol (`ENGINE_MD5`) is present at that location
  And the same check passes for all 5 seeded entries' anchors

Scenario: Contract field is one paragraph   # M5
  Given any seeded entry
  When its `Contract:` field is read
  Then it is a single paragraph (no bullet list, no sub-headings)

Scenario: Citations field is reproducible   # M6
  Given the `engine-md5-repin` entry's Citations field
  When the stated grep command is re-run
  Then the count matches what's recorded, the as-of SHA is present, and ≥2 named example task slugs (e.g. `rule-id-coverage`, `extract-predicates`) are listed

Scenario: Seed set preserves the milestone's ranked order   # M7
  Given the 5 candidates ranked 1-5 in MILESTONE.md
  When `.add/SEAMS.md`'s entries are read top to bottom
  Then they appear in that same order, NOT sorted by raw citation count
  And `scope-token-grammar` (3 citations) still outranks `phase-body-extraction` (26 citations)

Scenario: GLOSSARY gains the Seam term   # M8
  Given `.add/GLOSSARY.md`
  When it is grepped for "^Seam:" and "Survivor layer:"
  Then "Seam:" is defined and "Survivor layer:" now lists SEAMS

Scenario: Same-milestone-only repeat is rejected   # R:same_milestone_repeat
  Given a candidate symbol cited only by tasks inside one milestone
  When promotion to SEAMS.md is considered
  Then it is rejected with "same_milestone_repeat"
  And SEAMS.md's entry count is unchanged

Scenario: Unverifiable anchor is rejected   # R:unverifiable_anchor
  Given a candidate anchor `path:line` that does not exist in the tree
  When the entry is drafted
  Then it is rejected with "unverifiable_anchor"
  And the candidate is dropped from the seed set, not shipped with a guessed line number

Scenario: Prose heading is rejected   # R:unstable_anchor_slug
  Given a drafted heading like "## ENGINE_MD5 re-pin checklist"
  When it is checked against `^## [a-z0-9-]+$`
  Then it is rejected with "unstable_anchor_slug"
  And the heading is rewritten to a bare kebab-case id before it ships

Scenario: Bare-number citation is rejected   # R:uncited_count
  Given a Citations field reading only "291 mentions"
  When it is checked for a method + as-of + named examples
  Then it is rejected with "uncited_count"
  And the field is rewritten with the reproducible grep command + 2 named slugs

Scenario: Milestone-scoped seams file is rejected   # R:milestone_scoped_seams_file
  Given a proposal to create `.add/milestones/seams/SEAMS.md`
  When it is reviewed against the frozen shape
  Then it is rejected with "milestone_scoped_seams_file"
  And the entry is folded into the single project-level `.add/SEAMS.md` instead

Scenario: Graph-node seam is rejected   # R:graph_node_seam
  Given a proposal to represent an entry as a JSON/YAML backlink node
  When it is reviewed
  Then it is rejected with "graph_node_seam"
  And the entry ships as prose + a citation count only

Scenario: Boundary — exactly 5 entries at creation   # edge case
  Given the freshly created `.add/SEAMS.md`
  When `grep -c "^## " .add/SEAMS.md` is run
  Then it reports exactly 5 (matches the milestone's "≥5 entries" exit criterion)

Scenario: A seed candidate's stale citation count is caught and disclosed, not silently shipped   # edge case
  Given the milestone's seed claim "ENGINE_MD5 — 130 files, 291 mentions"
  When the count is freshly re-verified via `grep -rl "ENGINE_MD5\|ENGINE_PKG_MD5" --include=TASK.md .add/tasks`
  Then the actual count (160 files / 1059 mentions) is what ships in the Citations field
  And the divergence from the milestone's original estimate is named in the same field, not silently overwritten with no trace

Scenario: Two seed candidates would collide on one anchor   # edge case
  Given a hypothetical future promotion where two candidate names point at the same path:line
  When the entries are drafted
  Then they are merged into ONE entry (never two entries citing an identical anchor)
  And the merged entry's Name field notes both original names

Scenario: An anchor moved since the milestone's original research   # edge case
  Given a candidate symbol whose line number shifted between grounding-research time and this task's Ground SHA
  When the current anchor is re-resolved (as this Ground pass did for all 5)
  Then the CURRENT path:line ships, not the stale one from the research note
  And if the symbol can no longer be found at all, the candidate is dropped, not guessed

Scenario: Concurrency is explicitly ruled out   # edge case
  Given `.add/SEAMS.md` is a single human/AI-edited static document
  When considering concurrent-write scenarios
  Then none applies — this is a single-writer document task, explicitly ruled out rather than silently omitted
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT CONTRACT — .add/SEAMS.md creation + .add/GLOSSARY.md delta (docs; content shape frozen, no code API)

ENTRY GRAMMAR (frozen — seams-template-wiring's citation grammar depends on this exactly):
  ## <kebab-id>
  Name: <human-readable name>
  Anchor: `<path:line>` (`<symbol>`) [· `<path:line>` (`<symbol>`) ...]
  Contract: <one paragraph>
  Citations: <count> <files|tasks> — method: `<reproducible command>` · as of `<short-SHA>` ·
    e.g. `<slug>`, `<slug>`[, `<slug>`]

.add/SEAMS.md — H1 + evidence-bar intro, then 5 entries in this exact order:

  ## engine-md5-repin
  Name: ENGINE_MD5 / ENGINE_PKG_MD5 re-pin checklist
  Anchor: `add-method/tooling/engine_pin.py:13` (`ENGINE_MD5`) ·
    `add-method/tooling/engine_pin.py:15` (`ENGINE_PKG_MD5`) ·
    `add-method/tooling/test_engine_repin_parity.py:57` (`test_three_engines_byte_identical_and_current`)
  Contract: Any change to `add-method/tooling/add.py` re-aims ENGINE_MD5; any change under
    `add_engine/` re-aims ENGINE_PKG_MD5 — both hard-coded literals (never runtime-computed,
    or a pin could never detect its own drift), each carrying a prepended changelog comment
    naming the task and prior digest. The new digest propagates byte-identically to all 3
    engine trees before the next gate; test_engine_repin_parity.py's ENGINE_COPIES +
    test_three_engines_byte_identical_and_current mechanically enforce byte-identity and
    pin-currency, but never choose the digest for you — skipping the re-pin after a real
    engine edit is this project's single most common self-heal.
  Citations: 160 files / 1059 mentions in `.add/tasks/` (+18/71 in `.add/archive/`) — method:
    `grep -rl "ENGINE_MD5\|ENGINE_PKG_MD5" --include=TASK.md .add/tasks` · as of `c152945`.
    Revises the milestone's seed estimate (~130 files/291 mentions) — a substring count sweeps
    in every Scope-line mention, not only checklist runs; treat as an upper-bound signal.
    e.g. `rule-id-coverage`, `extract-predicates`, `gate-record-writeback`

  ## three-tree-parity
  Name: Engine / skill / bundle / book tree parity convention
  Anchor: `add-method/tooling/test_engine_repin_parity.py:40` (`ENGINE_COPIES`) ·
    `add-method/tooling/test_tree_parity.py:20` (`CANON_SKILL`) ·
    `add-method/tooling/test_bundle_parity.py` · `add-method/tooling/test_book_parity.py`
  Contract: Four independent parity guards hold the byte-identical-twin invariant:
    test_engine_repin_parity (the 3 add.py/add_engine copies), test_tree_parity (canonical
    skill vs `.claude/skills/add/` dogfood), test_bundle_parity (whole `_bundled/` package vs
    canonical, plus zero-test/zero-bytecode), and test_book_parity (book canonical vs repo-root
    chapters, with `.add/docs/` as a 4th gitignored, non-git-tracked copy). Any engine, skill,
    template, or book edit must propagate to every one of its own twins before the gate —
    hand-editing one tree in isolation is the recurring trap all four suites exist to catch.
  Citations: 232 files reference "byte-identical" in `.add/tasks/` — method:
    `grep -rl "byte-identical" --include=TASK.md .add/tasks` · as of `c152945` — a broad
    proxy count, not a precise invocation count. e.g. `rule-id-coverage`, `scope-decl-template`,
    `phase-agents-lean`

  ## scope-token-grammar
  Name: §5 "Scope (may touch):" token-resolution grammar
  Anchor: `add-method/tooling/add.py:4433` (`_declared_scope`)
  Contract: `_declared_scope` reads ONLY the first physical line after the §5 header — a
    wrapped multi-line list silently truncates. Each backticked token then resolves
    independently: `./...` = this task's dir, any token containing `/` = project-root-relative,
    a BARE token = sibling of the PREVIOUS token's directory (not project root) — citing a
    repo-root file after a nested one needs the explicit `add-method/../<name>` climb form, or
    the token silently resolves wrong and drops out of scope (fail-closed, no error). Three
    separate tasks (`phase-agents-lean`, `template-structural-gaps`, `rule-id-coverage`) each
    independently rediscovered and self-healed this exact bug via the same
    `phase tests <slug>` -> `phase build` re-anchor recovery.
  Citations: 3 tasks, named not grep-derived (generic phrases like "bare token" over-match this
    project's own template boilerplate present in nearly every TASK.md) — source:
    `rule-id-coverage`'s own §7 Spec-delta, which names itself "the THIRD task... after
    phase-agents-lean and template-structural-gaps." as of `c152945`.

  ## phase-body-extraction
  Name: `_raw_phase_bodies` / `_phase_spans` phase-body extraction
  Anchor: `add-method/tooling/add_engine/taskdoc.py:159` (`_phase_spans`) ·
    `add-method/tooling/add_engine/taskdoc.py:185` (`_raw_phase_bodies`)
  Contract: `_phase_spans` is the ONE canonical §1–§7 heading scanner
    (`^##\s*(\d+)\s*·`, case/locale-proof): a body runs from its heading to the next
    line-starting `## ` or bare `---`, RAW/byte-faithful (no cleanup) because the
    decision-marker/ADR extractor depends on verbatim text. `_raw_phase_bodies` wraps it
    per-task, returning `{}` on any read failure (fail-closed). KNOWN LIMIT: a §body
    containing its OWN line-start `## ` or bare `---` truncates early.
  Citations: 26 files / 93 mentions — method:
    `grep -rl "_raw_phase_bodies\|_phase_spans" --include=TASK.md .add/tasks` · as of
    `c152945` — matches the milestone's original seed count exactly. e.g.
    `build-expectations-gate`, `advisor-review-step`, `extract-predicates`

  ## section-unfilled-truth-table
  Name: `_section_unfilled`'s placeholder/grandfather truth table
  Anchor: `add-method/tooling/add_engine/predicates.py:47`
  Contract: A pure 3-way predicate reused across every fill-gate: header ABSENT -> False
    (grandfathered legacy task); header PRESENT but empty or a bare `<...>` placeholder ->
    True (unfilled, gate fires); header PRESENT with ≥1 real bullet -> False (filled, gate
    passes). Angle brackets INSIDE a backtick span (e.g. `` `<persona>` ``) are literal
    notation, never a placeholder — only a bare, unfenced `<...>` counts.
  Citations: 14 files cite/reuse the symbol — method: `grep -rl "_section_unfilled"
    --include=TASK.md .add/tasks` · as of `c152945`. Revises the milestone's "3 files"
    framing, which appears to have counted only full truth-table restatements (subjective);
    this reports the objective citation count instead. e.g. `guarantee-audit-lints`,
    `advisor-verdict-audit`, `contract-fill-gate`

GLOSSARY DELTA — `.add/GLOSSARY.md`:
  new:    Seam: a symbol/convention cited or re-derived by tasks in ≥2 DIFFERENT milestones (a
          same-milestone repeat is ordinary cohesion, not a seam); promoted into `.add/SEAMS.md`
          as a Name/Anchor/Contract/Citations entry so a task's §0 GROUND can cite it
          (`Seams consulted: .add/SEAMS.md#<id>`) instead of re-deriving the fact inline.
  amend:  Survivor layer: documents kept for the whole project (CONVENTIONS, GLOSSARY,
          MODEL_REGISTRY, allowlist, SEAMS).

TEST  add-method/tooling/test_seams_doc.py (new) — asserts SHAPE not verbatim prose:
  - .add/SEAMS.md exists; exactly 5 `## ` headings, each `^[a-z0-9-]+$`, in the frozen order
  - each entry has Name/Anchor/Contract/Citations in that field order
  - each Anchor's `path:line` resolves in the current tree (open file, check line count/symbol)
  - Citations field matches a pattern requiring a digit count + "method:" + ≥2 backticked slugs
  - .add/GLOSSARY.md contains "^Seam:" and "Survivor layer:" mentions SEAMS
  -> ok 200: {entries: 5/5, anchors_resolve: 5/5, glossary_delta: applied}
  -> red  : { error: "same_milestone_repeat" | "unverifiable_anchor" | "unstable_anchor_slug"
                    | "uncited_count" | "milestone_scoped_seams_file" | "graph_node_seam" }
```

Glossary deltas: `Seam` (new term) + `Survivor layer` (amended) — both listed above.
Least-sure flag surfaced at freeze: [contract] Citations-field numbers are grep snapshots as of `c152945`, inherently stale the moment the next task lands (mitigated, not eliminated, by method+as-of-SHA); [spec] the GLOSSARY.md edit's scope-membership is a judgment call, not explicit in the milestone's frozen Scope text — confirmed by Tin 2026-07-01, keep it in this task's scope, ship as drafted.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the frozen entry-grammar Musts/Rejects (shape-only assertions, never verbatim prose)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_seams_md_exists: arrange fresh tree / act read `.add/SEAMS.md` / assert file exists · covers: M1
  - test_no_milestone_scoped_seams_file: arrange fresh tree / act glob `.add/milestones/*/SEAMS.md` / assert empty · covers: R:milestone_scoped_seams_file
  - test_h1_title_and_evidence_bar_blockquote: arrange file / act read head / assert H1 + evidence-bar blockquote present · covers: M2
  - test_exactly_five_headings_bare_kebab_case_frozen_order: arrange file / act scan `## ` headings / assert 5, `^[a-z0-9-]+$`, frozen rank order · covers: M3, M7, R:unstable_anchor_slug
  - test_grep_c_heading_count_is_five: arrange file / act `grep -c "^## "` / assert 5 · covers: edge (exactly-5 boundary)
  - test_every_entry_has_fields_in_order: arrange each entry / act parse fields / assert Name→Anchor→Contract→Citations order · covers: field-order shape
  - test_every_anchor_resolves: arrange each Anchor path:line / act open file at line / assert symbol present in CURRENT tree · covers: M4, R:unverifiable_anchor
  - test_no_two_entries_share_an_identical_anchor: arrange all anchors / act compare / assert no duplicate path:line across entries · covers: edge (anchor collision)
  - test_contract_is_single_paragraph_no_bullets: arrange each Contract field / act check for bullet markers / assert none · covers: M5
  - test_citations_pattern_count_method_sha_examples: arrange each Citations field / act regex match / assert digit count + method/source + as-of + ≥2 examples · covers: M6, R:uncited_count
  - test_engine_md5_repin_citations_command_is_reproducible: arrange the engine-md5-repin entry's grep command / act re-run it / assert count matches recorded · covers: M6 (re-run the grep)
  - test_stale_estimate_divergence_is_disclosed_not_silent: arrange engine-md5-repin entry / act read Citations / assert the milestone's original seed estimate divergence is named inline · covers: edge (stale count disclosed)
  - test_no_entry_rendered_as_json_or_yaml_node: arrange file / act check for JSON/YAML block per entry / assert none · covers: R:graph_node_seam
  - test_seam_defined_and_survivor_layer_lists_seams: arrange `.add/GLOSSARY.md` / act grep `^Seam:` and `Survivor layer:` / assert both present, SEAMS listed · covers: M8
  - test_entry_set_is_closed_to_the_vetted_five: arrange file / act count entries / assert exactly the 5 vetted candidates, documented as a judgment proxy (no mechanical same_milestone_repeat test exists by design) · covers: R:same_milestone_repeat (documented, not silently skipped)
</test_plan>

Tests live in: `add-method/tooling/test_seams_doc.py` · ran red (missing `.add/SEAMS.md`, 9/15 failing) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `.add/SEAMS.md` · `.add/GLOSSARY.md` · `add-method/tooling/test_seams_doc.py`
Strategy (ordered batches): 1. write `.add/SEAMS.md` verbatim per the frozen entry grammar above (5 entries, milestone-ranked order); 2. add the `Seam` GLOSSARY term + amend the `Survivor layer` line in `.add/GLOSSARY.md`; 3. write `add-method/tooling/test_seams_doc.py` — shape/anchor-resolution assertions, never pinning exact prose wording (so a future light copyedit doesn't false-fail); 4. run the new suite + `add.py check`; confirm zero ripple into book/skill/bundle parity guards (SEAMS.md is new, not a twin of anything).

Persona (optional): `methodology-engine-dev` — accuracy of the 5 anchors is the dominant risk.
Known-problem fixes: stale/unverified citation counts shipped as fact → re-verify every number against the current tree at build time, disclose any divergence from the seed estimate inline in the Citations field (already done once at design time for 3 of 5 entries) · a prose/Title-Case heading breaking anchor-slug stability → enforce bare kebab-case `## <id>` headings only.
Strategy actually used: Diverged from the preferred order mainly by writing the TEST FIRST (red before green) per red/green TDD: (1) read TASK.md §3 frozen contract + GLOSSARY.md + precedent `test_rule_id_coverage.py` + the persona; (2) swept the working tree, confirmed the concurrent `search-index` task's in-flight edits sit outside this task's 3-file Scope; (3) re-verified all 5 frozen Anchor path:line citations against the CURRENT tree (not just trusting the frozen text) — surfaced 2 pre-existing drifted lines (`test_engine_repin_parity.py:57`→54, `test_tree_parity.py:20`→21), corrected + disclosed inline in Citations per the contract's own "anchor moved" edge-case rule, did NOT touch frozen §3 text; (4) wrote `test_seams_doc.py` first, confirmed RED for the right reason (9/15 failing, missing `.add/SEAMS.md`); (5) wrote `.add/SEAMS.md` verbatim per the frozen entry grammar; (6) amended `.add/GLOSSARY.md`; (7) found 2 of the test's own assertions over-fit to the majority pattern (assumed every entry uses "method:"+"e.g."), false-failing against the legitimate scope-token-grammar entry's "source:"+prose-examples form (already explained in §0 Issues/Risks) — corrected the TEST, not the contract or shipped file; (8) reran to 15/15 GREEN; (9) ran the full `add-method/tooling` suite — 2650/2650 GREEN, zero ripple into the 4 byte-identical parity guards despite 2 entries anchoring directly into their own test files; (10) git-diff-confirmed only the 3 declared Scope files changed.
Safety rule (feature-specific): none — single-writer static-document task, concurrency explicitly ruled out (see §2 scenario).
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (`test_seams_doc.py` 15/15; full `add-method/tooling` suite 2680/0)
- [x] coverage did not decrease (prose-only artifact + additive-only test file — structurally cannot decrease)
- [x] no test or contract was altered during build (the build agent's test-assertion generalization at build-time widened the Citations regex to accept the frozen contract's OWN already-specified `source:`-based form for `scope-token-grammar` — not a weakening; confirmed by the verify agent)
- [x] the green was EARNED after one bounded heal cycle — see Refute-read verdict below (first pass found a real defect the green did not cover; fixed, re-verified)
- [x] concurrency / timing of the risky operation is safe (single-writer static doc, explicitly ruled out; empirically validated — every anchor still resolved live despite real concurrent `add.py` churn from `search-index` during this build)
- [x] no exposed secrets, injection openings, or unexpected dependencies (💭 note: `test_engine_md5_repin_citations_command_is_reproducible` extracts a shell command from SEAMS.md's own text via regex and runs it via `subprocess.run(["bash","-c",...])` — safe today since the source is a git-tracked, reviewed static doc, not attacker input; worth naming if SEAMS.md's provenance ever loosens)
- [x] layering & dependencies follow CONVENTIONS.md (no new dependency; docs + one new test file)
- [x] a person reviewed and approved the change (contract freeze — Tin Dang, 2026-07-01)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] `.add/SEAMS.md` exists with exactly 5 entries in the frozen rank order, each with a resolvable anchor — confirmed by `test_seams_doc.py`'s shape tests + independent live re-verification of all 9 path:line + 2 bare-file anchors during VERIFY
- [x] `.add/GLOSSARY.md` gains the `Seam` term + amended `Survivor layer` line — confirmed by `test_seam_defined_and_survivor_layer_lists_seams`, git diff +5/-1

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every helper in `test_seams_doc.py` (`_read`, `_entry_blocks`, `_field`, `_anchor_citations`) referenced by ≥1 test; no orphaned symbol — confirmed by add-verify
- [x] DEAD-CODE (code) — none introduced
- [x] SEMANTIC (prose) — `.add/SEAMS.md` and the GLOSSARY delta read in full by add-verify, not skimmed — this full read is what surfaced the phase-body-extraction defect below

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the CURRENT tree — independently re-verified by add-verify (not trusting the build agent's own disclosure): all 9 path:line anchors + 2 bare-file anchors across all 5 entries, right down to `add.py:4461` (`_declared_scope`), held despite active concurrent edits to `add.py` from `search-index` during this exact check
- [x] anchors that moved since Ground SHA `c152945`: 2, both caught and corrected DURING build (not silently) — `test_engine_repin_parity.py:57`→`:54`, `test_tree_parity.py:20`→`:21`; zero further drift found at VERIFY

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED (after one bounded heal cycle — see below)
By: agent (add-verify / tdd-verifier persona) · adversarially checked: independently re-ran all 5 entries' stated Citations grep commands (not just the one `test_citations_pattern_count_method_sha_examples` spot-checks live, `engine-md5-repin`) and cross-checked every named example against its own entry's live grep output.
First pass: **NOT-EARNED**. Found `phase-body-extraction`'s Citations field named `extract-predicates` as an example, but that task has ZERO occurrences of `_phase_spans`/`_raw_phase_bodies` — it genuinely cites `_section_unfilled` instead (9 hits), i.e. it belongs under `section-unfilled-truth-table`, not here. Root cause: `test_citations_pattern_count_method_sha_examples` only validated example strings are kebab-case-*shaped*, never that they're genuine matches, for 4 of the 5 entries (a vacuous assert on those 4) — a textbook "shape-only test misses a factual defect" case.
Heal: replaced `extract-predicates` with `extract-taskdoc` (confirmed via `grep -n "_raw_phase_bodies\|_phase_spans" .add/tasks/extract-taskdoc/TASK.md` — genuine hits) in `.add/SEAMS.md`'s `phase-body-extraction` entry. Re-ran `test_seams_doc.py`: 15/15 green. `git status` confirms only the 3 declared Scope files remain touched.
Second pass: EARNED — the specific defect found is fixed and re-verified; no other entry's examples showed the same defect (the other 4 were independently cross-checked and confirmed genuine in the same refute-read pass).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: agent (add-verify / tdd-verifier persona)
1. Security: CLEAR (💭 note: SEAMS.md-sourced shell command in one test — safe today, provenance-dependent, see checklist above)
2. Concurrency: CLEAR — empirically validated against real concurrent churn from `search-index` during this exact build/verify window
3. Architecture: CLEAR after heal (was RESIDUE — misattributed Citations example, `phase-body-extraction`; fixed, re-verified, no other entry affected)
Verdict: PASS
Residue: none — the one finding (misattributed citation example) was fixed and re-verified before this record; two prior spec deltas proposed for follow-up (parametrize the reproducibility re-run across all 5 entries, not just 1) are captured below in §7, not left as open residue on this gate.
Binding: advisory (task carries no `risk: high` / `sensitivity: mechanical` line)

### GATE RECORD
Outcome: PASS
Reviewed by: agent (add-verify) + orchestrator, one bounded heal cycle applied before this record · date: 2026-07-02

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): watch whether `seams-template-wiring`'s `Seams consulted:` citations actually get used by future tasks' §0 GROUND sections (validates the whole milestone's premise); watch each entry's Citations count for continued drift beyond the "as of c152945" framing — a periodic re-verify task is a candidate if drift becomes noisy.

### Decisions (ADR)
- [AI] specify — chose per-entry `##`-heading + 4 fixed prose fields (Name/Anchor/Contract/Citations); rejected GLOSSARY-style single dense line per entry (rejected — can't hold a real path:line + a reproducible citation method + named examples without an unreadable run-on, breaking the 5-second test) · a Markdown table with name/anchor/contract/citations columns (rejected — a one-paragraph Contract statement doesn't survive a table cell, and multi-anchor entries like three-tree-parity cite 4 files each, which doesn't fit one cell).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: Diverged from the preferred order mainly by writing the TEST FIRST (red before green) per red/green TDD: (1) read TASK.md §3 frozen contract + GLOSSARY.md + precedent `test_rule_id_coverage.py` + the persona; (2) swept the working tree, confirmed the concurrent `search-index` task's in-flight edits sit outside this task's 3-file Scope; (3) re-verified all 5 frozen Anchor path:line citations against the CURRENT tree (not just trusting the frozen text) — surfaced 2 pre-existing drifted lines (`test_engine_repin_parity.py:57`→54, `test_tree_parity.py:20`→21), corrected + disclosed inline in Citations per the contract's own "anchor moved" edge-case rule, did NOT touch frozen §3 text; (4) wrote `test_seams_doc.py` first, confirmed RED for the right reason (9/15 failing, missing `.add/SEAMS.md`); (5) wrote `.add/SEAMS.md` verbatim per the frozen entry grammar; (6) amended `.add/GLOSSARY.md`; (7) found 2 of the test's own assertions over-fit to the majority pattern (assumed every entry uses "method:"+"e.g."), false-failing against the legitimate scope-token-grammar entry's "source:"+prose-examples form (already explained in §0 Issues/Risks) — corrected the TEST, not the contract or shipped file; (8) reran to 15/15 GREEN; (9) ran the full `add-method/tooling` suite — 2650/2650 GREEN, zero ripple into the 4 byte-identical parity guards despite 2 entries anchoring directly into their own test files; (10) git-diff-confirmed only the 3 declared Scope files changed.
- [AI] verify — gate PASS (reviewed by agent (add-verify) + orchestrator, one bounded heal cycle applied before this record)

### Spec delta
- [SPEC · seeded] parametrize `test_seams_doc.py`'s Citations reproducibility re-run across all 5 entries, not just `engine-md5-repin` — the current spot-check design let a misattributed example (`extract-predicates` under `phase-body-extraction`, actually belongs under `section-unfilled-truth-table`) ship with a 15/15 green suite (evidence: this task's own refute-read, first pass NOT-EARNED)
- [SPEC · dropped] a mechanical `same_milestone_repeat` test — the frozen contract already ruled this out by design (no reliable `milestone:` header across older tasks); not revisited, no new evidence changes that call

### Competency deltas
- [TDD · folded] a shape-only test suite (asserts field ORDER + kebab-case-shaped strings) went 15/15 green while shipping a factual defect (a Citations example that doesn't actually match its own entry's stated grep method) — the assert validated the SHAPE of "≥2 named examples" but never that the examples are genuine; a spot-checked scenario (only 1 of 5 entries got a live re-run) is not equivalent to full coverage of a mechanically-checkable claim (evidence: `phase-body-extraction`'s `extract-predicates` misattribution, caught only by the verify agent's independent re-run of all 5, not by the build's own green suite) [folded foundation-version 60]
- [ADD · folded] running two `add-build` agents in parallel in the same working tree (no worktree isolation) caused a real anchor drift mid-build and a scope-lock false-positive at gate time — recovered both times via the established `phase tests`→`phase build`→`advance` re-cross (evidence: `_declared_scope`'s line number shifted mid-build from `search-index`'s concurrent edit to `add.py`; `add.py gate PASS` rejected once with `scope_violation: ... test_min_pillar.py`, a file entirely inside `search-index`'s own declared Scope, not this task's) [folded foundation-version 60]
- [ADD · folded] a milestone's own seed research should be treated as a strong LEAD, not ground truth, and "verify, don't trust" needs to apply recursively at every stage, not just once at grounding (evidence: this task's build+verify stages together overturned 3 of 5 seed numbers from the milestone AND found one further defect, a misattributed Citations example, that had survived into the frozen contract itself) [folded foundation-version 60]

