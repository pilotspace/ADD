# SEAMS

> A seam is a symbol or convention cited or re-derived by tasks across ≥2 DIFFERENT milestones —
> a same-milestone repeat is ordinary cohesion, not a seam. Each entry below carries a resolvable
> `Anchor:` and a reproducible `Citations:` count so future work can point at the shared rule
> instead of re-deriving it inline. Cite an entry from a task's §0 GROUND as
> `Seams consulted: .add/SEAMS.md#<id>` — the heading text below is the anchor id, verbatim, so
> the link resolves the same way in GitHub, MkDocs, and plain grep alike.

## engine-md5-repin
Name: ENGINE_MD5 / ENGINE_PKG_MD5 re-pin checklist
Anchor: `add-method/tooling/engine_pin.py:20` (`ENGINE_MD5`) ·
  `add-method/tooling/engine_pin.py:21` (`ENGINE_PKG_MD5`) ·
  `add-method/tooling/test_engine_repin_parity.py:54` (`test_three_engines_byte_identical_and_current`)
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
  Anchor re-verified at build time against the current tree (`test_engine_repin_parity.py`
  unchanged since Ground SHA `c152945`) — `test_three_engines_byte_identical_and_current`
  resolves at `:54`, not the `:57` cited when this entry was drafted; disclosed here rather
  than shipped stale. `ENGINE_PKG_MD5` anchor re-corrected a second time (`:15` -> `:14`)
  after `fix-flag-fence-aware`'s own engine_pin.py re-pin shifted it — the exact class of
  drift this entry itself documents. Both anchors re-corrected a third time (`:13`/`:14` ->
  `:20`/`:21`) after engine_pin.py's docstring grew a "Trim policy" paragraph — same drift
  class, disclosed rather than shipped stale. Revises the milestone's seed estimate (~130 files/291
  mentions) — a substring count sweeps in every Scope-line mention, not only checklist runs;
  treat as an upper-bound signal. e.g. `rule-id-coverage`, `extract-predicates`, `gate-record-writeback`

## three-tree-parity
Name: Engine / skill / bundle / book tree parity convention
Anchor: `add-method/tooling/test_engine_repin_parity.py:40` (`ENGINE_COPIES`) ·
  `add-method/tooling/test_tree_parity.py:21` (`CANON_SKILL`) ·
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
  proxy count, not a precise invocation count. Anchor re-verified at build time against the
  current tree (`test_tree_parity.py` unchanged since Ground SHA `c152945`) — `CANON_SKILL`
  resolves at `:21`, not the `:20` cited when this entry was drafted; disclosed here rather
  than shipped stale. e.g. `rule-id-coverage`, `scope-decl-template`, `phase-agents-lean`

## scope-token-grammar
Name: §5 "Scope (may touch):" token-resolution grammar
Anchor: `add-method/tooling/add.py:5512` (`_declared_scope`)   <!-- re-pinned 2026-07-13 kickoff-truth: 5491→5512 (the kickoff-lane lines + new-task recipe block above it — the pin drifts on ANY upstream add.py change; symbol cited so the drift self-describes; todo #30 seams-symbol-pins retires this class) -->
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
  phase-agents-lean and template-structural-gaps." as of `c152945`. Anchor re-corrected a
  third time (`:4470` -> `:4494`) after `status-pagination`'s own `cmd_status` insertion
  shifted every symbol after it — the same class of drift this entry itself documents.

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
  `build-expectations-gate`, `advisor-review-step`, `extract-taskdoc`

## section-unfilled-truth-table
Name: `_section_unfilled`'s placeholder/grandfather truth table
Anchor: `add-method/tooling/add_engine/predicates.py:100` (`_section_unfilled`)   <!-- re-pinned 2026-07-09 x3: 47→60→80→100 (fast-lane-skips's own _skip_lane_eligible/_skip_set_allowed addition above it shifted the line) -->
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
