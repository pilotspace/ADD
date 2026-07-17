# TASK: Spec-delta grammar — separate resolution track

slug: spec-delta-grammar · created: 2026-06-16 · stage: mvp
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
  - `add-method/tooling/add.py:3731-3747` — the delta grammar constants (single source of truth): `_COMPETENCY_ORDER=("DDD","SDD","UDD","TDD","ADD")` · `_DELTA_STATUSES=("open","folded","rejected")` · `_DELTA_RE` (enumerated `- [COMP · status] <tail>`) · `_EVIDENCE_RE` (`(evidence: …)` split) · `_TAG_BROAD_RE` (competency-AGNOSTIC `- [tok · tok]` structural detector). The SPEC track adds parallel constants here.
  - `add-method/tooling/add.py:_task_prose` (3019-3063) — parses §7 OBSERVE: the free-text `Spec delta for the next loop:` field (line 3033) + the `### Competency deltas` entries; returns `(observe, deltas)`. SPEC track replaces the free-text read with a `### Spec delta` block read.
  - `add-method/tooling/add.py:_lint_task_deltas` (3749-3841) — lints the `### Competency deltas` block (open-only); uses `_TAG_BROAD_RE`/`_DELTA_RE`/`_COMPETENCY_ORDER`/`_DELTA_STATUSES`. Needs a tag-scoped status-set check so `[SPEC · folded]`/`[SDD · seeded]` are rejected.
  - `add-method/tooling/add.py:_collect_open_deltas` (3844-3896) — globs `tasks/*/TASK.md`, collects OPEN competency deltas by competency. SPEC gets a parallel `_collect_open_spec_deltas` (separate target — never folded).
  - `add-method/tooling/add.py:cmd_deltas` (4422) + `deltas` subparser (4722-4725) — read-only report of open competency learnings; surfaces open SPEC deltas in a SEPARATE section.
  - `add-method/tooling/add.py:cmd_check` lint wiring (1708-1714) — runs `_lint_task_deltas` per task, emits the `task '<slug>' deltas well-formed` check.
  - `add-method/tooling/templates/TASK.md.tmpl` (§7 OBSERVE block) + embedded fallback `_FALLBACK_TASK` (add.py:119) — both carry the free-text `Spec delta for the next loop:` line to be replaced by a `### Spec delta` block. Keep the two in sync.
Context (working folder):
  - tests (unittest): `add-method/tooling/test_*.py`; touching `test_delta_grammar_dedup.py` · `test_deltas_lint.py` · `test_deltas_report.py` · `test_ground_prose.py` (`_task_prose`) · `test_competency_deltas.py` · `test_template_form_tags.py`. NEW file: `test_spec_delta_grammar.py`. Baseline green: 1158 OK (3 skipped).
  - convention docs (the SDD spec for a method change, dogfood-mirrored): `.claude/skills/add/deltas.md` (delta grammar) + `phases/7-observe.md` (writes the spec delta) — add a SPEC-track section in a later doc-touch; canonical twins under `add-method/skill/add/`.
  - parity: the engine ships in 3 md5-identical copies — `add-method/tooling/add.py` (canonical, edit here) → `.add/tooling/add.py` (dogfood, `cp`) + `src/add_method/_bundled/tooling/add.py` (via `scripts/prepare_bundle.py`); guarded by `test_bundle_parity.py` + `test_tree_parity.py`.
Honors (patterns / conventions):
  - CONVENTIONS.md: delta-grammar is single-source — no parallel/duplicated grammar (`test_delta_grammar_dedup`); md5 tree+bundle parity after any add.py/template edit; newest-first append-only foundation; competency deltas require `(evidence: …)`.
  - MILESTONE shared decisions: SPEC is a SEPARATE track (own status set `open|seeded|dropped`, own collector, resolves into a task, never folded); status sets are tag-scoped (reject cross-set); SPEC is NOT a 6th competency.
Anchors the contract cites: `_DELTA_RE` · `_DELTA_STATUSES` · `_COMPETENCY_ORDER` · `_TAG_BROAD_RE` · `_lint_task_deltas` · `_collect_open_deltas` · `_task_prose` · `cmd_deltas` · `TASK.md.tmpl §7` · `_FALLBACK_TASK`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a SPEC-delta resolution grammar — a `### Spec delta` block in §7 OBSERVE whose entries follow `- [SPEC · open|seeded|dropped] <text>`, a SEPARATE track from `### Competency deltas`.
Framings weighed: separate-track grammar mirroring competency lines (chosen) · SPEC as a 6th competency tag in the same machine (rejected — a forward task hand-off is not a foundation lesson) · free-text field with a status suffix (rejected — not lintable, no collector)
Must:
<must>
  - Parse a `### Spec delta` block in §7 OBSERVE whose entries are `- [SPEC · <status>] <text>`, `<status>` ∈ `open | seeded | dropped`. The block may hold MULTIPLE entries (a list, like `### Competency deltas`), text may wrap onto continuation lines.
  - Tag-scoped status sets: the `SPEC` tag accepts ONLY `open|seeded|dropped`; the five competency tags accept ONLY `open|folded|rejected`. The grammar/lint treats the two sets as disjoint per tag.
  - `_task_prose` reads the new `### Spec delta` block; back-compat: when no block is present it still reads the legacy `Spec delta for the next loop:` field (archived tasks). The report's single per-task `observe` slot = the first OPEN SPEC delta's text from the block, else the legacy field, else `(unknown)`.
  - A new collector `_collect_open_spec_deltas(root)` returns OPEN SPEC deltas per task, SEPARATE from `_collect_open_deltas` (competency) — a SPEC entry is never bucketed under a competency.
  - `add.py deltas` surfaces open SPEC deltas under a section distinct from the competency learnings (and `--json` carries them under a separate key).
  - `_lint_task_deltas` (via `add.py check`) validates SPEC entries with the tag-scoped status set; a seeded entry MAY carry a trailing `[→ <slug>]` pointer which the grammar TOLERATES on read (writing that stamp is the seed-and-drop task).
  - The TASK.md template — `tooling/templates/TASK.md.tmpl` §7 AND the embedded `_FALLBACK_TASK` — replaces the free-text `Spec delta for the next loop:` line with a `### Spec delta` block (a commented `[SPEC · open]` example), kept byte-identical across both.
  - `(evidence: …)` is REQUIRED on an open SPEC entry (symmetric with competency deltas — a forward change names its prompt: the defect, surprise, or need); the entry text must be non-empty.
</must>
Reject:
<reject>
  - a SPEC tag carrying a non-SPEC status, e.g. `[SPEC · folded]` -> "unknown_status"
  - a competency tag carrying a SPEC status, e.g. `[SDD · seeded]` -> "unknown_status"
  - a `### Spec delta` entry whose text is empty after the tag -> "malformed_delta"
  - an OPEN SPEC entry with no `(evidence: …)` -> "no_evidence"   (symmetric with competency)
  - (existing competency lint codes unchanged: unknown_competency · no_evidence · unknown_status · malformed_delta)
</reject>
After:
<after>
  - `add.py check` emits a well-formed verdict over `### Spec delta` entries with tag-scoped statuses; `add.py deltas` lists open SPEC deltas in their own section; a fresh `add.py new-task` scaffolds a `### Spec delta` block; the legacy free-text field still parses for archived tasks; the full unittest suite + md5 tree/bundle parity stay green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ legacy back-compat + the report `observe` slot — replacing the free-text field changes what `_task_prose` returns as `observe` and the report's per-task "spec delta" column, while archived tasks still carry the old line. Lowest confidence because a single-string slot must now map onto a LIST. If wrong: historical `report` reads show nothing or crash. Proposed map: first-open-from-block → legacy-field → `(unknown)`.
  ⚠ SPEC evidence is OPTIONAL (unlike competency's required `(evidence:…)`) — a forward "new need" often has no prod signal. If wrong (you want symmetry): the lint gains a `no_evidence` check for SPEC and every template example must carry evidence.
  - [ ] the SPEC block holds a LIST of entries (confirmed by your three-line preview), not a single line.
  - [ ] the block heading is exactly `### Spec delta` (singular), parallel to `### Competency deltas`.
  - [ ] the `[→ <slug>]` seeded pointer is parsed/tolerated here but WRITTEN by the seed-and-drop task.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a SPEC block holds a list; only open entries collect   # Must 1, 4
  Given a TASK.md §7 with a "### Spec delta" block of three entries — [SPEC · open], [SPEC · seeded], [SPEC · dropped]
  When _collect_open_spec_deltas scans the task
  Then it returns exactly the one open entry under the SPEC track
  And _collect_open_deltas (competency) returns nothing for that task

Scenario: a SPEC tag with its own status lints clean, [→ slug] tolerated   # Must 2, 6
  Given a "### Spec delta" entry "- [SPEC · seeded] rate-limit retry [→ fix-herd]"
  When add.py check lints the task
  Then the "deltas well-formed" check passes
  And the [→ fix-herd] pointer does not trip the lint

Scenario: a cross-set status on a SPEC tag is rejected   # Reject 1
  Given a "### Spec delta" entry "- [SPEC · folded] something"
  When add.py check lints the task
  Then the check fails with reason starting "unknown_status -> - [SPEC · folded]"
  And a well-formed competency block in the same file still lints independently

Scenario: a cross-set status on a competency tag is rejected   # Reject 2
  Given a "### Competency deltas" entry "- [SDD · seeded] x (evidence: y)"
  When add.py check lints the task
  Then the check fails with reason starting "unknown_status -> - [SDD · seeded]"
  And the SPEC block in the same file is unaffected

Scenario: an empty SPEC entry text is malformed   # Reject 3
  Given a "### Spec delta" entry "- [SPEC · open]" with no text after the tag
  When add.py check lints the task
  Then the check fails with reason starting "malformed_delta -> - [SPEC · open]"
  And a well-formed sibling SPEC entry is named-but-not-blamed (the reason cites the offending line)

Scenario: SPEC evidence is required, same as competency   # Must 7, Reject 4
  Given a "### Spec delta" entry "- [SPEC · open] surface 429s in the UI" with no (evidence: …)
  When add.py check lints the task
  Then the check fails with reason starting "no_evidence -> - [SPEC · open]"
  And the same entry WITH "(evidence: prod 429 spikes)" lints clean

Scenario: the observe slot derives from the new block   # Must 3
  Given a TASK.md §7 with a "### Spec delta" open entry "rate-limit retry" and no legacy line
  When _task_prose reads the task
  Then observe == "rate-limit retry"
  And the competency deltas it returns keep their existing shape

Scenario: the legacy free-text field still parses   # Must 3 (back-compat)
  Given an archived-style §7 with only "Spec delta for the next loop: X" and no "### Spec delta" block
  When _task_prose reads the task
  Then observe == "X"
  And _collect_open_spec_deltas returns nothing for that task

Scenario: add.py deltas lists SPEC deltas in their own section   # Must 5
  Given a task with one open SPEC delta and one open competency delta
  When add.py deltas runs
  Then the competency learning prints under its competency AND the SPEC delta prints under a separate spec section
  And add.py deltas --json carries the two under separate keys

Scenario: a fresh task scaffolds a "### Spec delta" block   # Must (template)
  Given a fresh ADD project
  When add.py new-task foo scaffolds its TASK.md
  Then §7 contains a "### Spec delta" block and NOT the free-text "Spec delta for the next loop:" line
  And the canonical template TASK.md.tmpl and the embedded _FALLBACK_TASK render that block byte-identically
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
GRAMMAR (new constants, beside _DELTA_RE @ add.py:3731-3747 — single source, no parallel duplicate):
  _SPEC_STATUSES = ("open", "seeded", "dropped")                 # disjoint from _DELTA_STATUSES
  _SPEC_DELTA_RE = re.compile(r"\s*-\s*\[\s*(SPEC)\s*·\s*(open|seeded|dropped)\s*\]\s*(.+)$")
  _STATUS_SETS   = { **{c: _DELTA_STATUSES for c in _COMPETENCY_ORDER}, "SPEC": _SPEC_STATUSES }
  block heading  = "### Spec delta"   (singular; parallel to "### Competency deltas")
  tolerated      : a seeded entry may end " [→ <slug>]" — parsed-but-not-required text (WRITTEN by seed-and-drop)

FUNCTIONS:
  _collect_open_spec_deltas(root: Path) -> list[dict]            # NEW; mirror of _collect_open_deltas
    scans tasks/*/TASK.md "### Spec delta" blocks; returns OPEN entries
      [ { "task": <slug>, "text": <str>, "evidence": <str|""> } ]   READ-ONLY, never mutates.

  _task_prose(root, slug) -> tuple[str, list[str]]               # signature UNCHANGED (back-compat)
    observe = first OPEN "### Spec delta" entry text
              else legacy "Spec delta for the next loop:" field
              else "(unknown)".            second element (competency deltas) unchanged.

  _lint_task_deltas(root, slug) -> tuple[bool, str] | None       # signature UNCHANGED
    lints BOTH "### Competency deltas" AND "### Spec delta". For each entry:
      skip if status ∈ RESOLVED-for-its-tag  (competency: folded|rejected · SPEC: seeded|dropped)
      else validate the (open / invalid) entry:
        tag ∉ (_COMPETENCY_ORDER ∪ {"SPEC"})  -> (False, "unknown_competency -> <tag line>")
        status ∉ _STATUS_SETS[tag]            -> (False, "unknown_status -> <tag line>")
        empty text after the tag              -> (False, "malformed_delta -> <tag line>")
        open entry (competency OR SPEC) w/o "(evidence:" -> (False, "no_evidence -> <tag line>")   # symmetric
      None when no entries found · (True, "") when all pass · fail-closed on an unparseable attempt.

  cmd_deltas(args)                                               # text + --json, additive
    text : existing competency sections, THEN  "spec deltas (N):" listing open SPEC entries "- <text>  [<task>]"
    --json: existing { total, by_competency } PLUS  "spec": [ {task,text,evidence} ],  "spec_total": N
    exit 0 always; writes nothing.

TEMPLATE (byte-identical across canonical + fallback):
  TASK.md.tmpl §7 AND _FALLBACK_TASK (add.py:119): the line
    "Spec delta for the next loop: <…>"
  is REPLACED by a "### Spec delta" block (one-line intro + a commented
    "- [SPEC · open] <change> (evidence: <pointer>)" example).

PARITY: after edits — cp canonical add.py -> .add/tooling/add.py · run scripts/prepare_bundle.py ·
        test_bundle_parity + test_tree_parity stay green (3 md5-identical add.py copies).

Reject responses (lint reason string = "<code> -> <offending tag line>"):
  unknown_status · malformed_delta · unknown_competency · no_evidence (competency + open SPEC)
```

Least-sure flag surfaced at freeze: [contract] the back-compat observe-slot map — _task_prose collapses a LIST to one string via first-open → legacy → "(unknown)"; if wrong, historical `report` reads show the wrong line or nothing. Pinned by test_observe_legacy_fallback. (Runner-up [spec]: SPEC evidence — resolved to REQUIRED at this freeze, symmetric with competency.)

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-16
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject has a test (10 scenarios → ≥10 tests); full suite stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_spec_block_lists_only_open_collects: write a TASK.md with [SPEC·open/seeded/dropped] / assert _collect_open_spec_deltas → 1 open; _collect_open_deltas → none
  - test_spec_status_lints_clean_arrow_tolerated: "[SPEC·seeded] x [→ fix-herd]" / add.py check / assert deltas-well-formed PASS
  - test_spec_cross_set_status_rejected: "[SPEC·folded] x" / check / assert fail reason startswith "unknown_status -> - [SPEC · folded]"
  - test_competency_cross_set_status_rejected: "[SDD·seeded] x (evidence: y)" / check / assert fail "unknown_status -> - [SDD · seeded]"
  - test_spec_empty_text_malformed: "[SPEC·open]" no text / check / assert fail "malformed_delta -> - [SPEC · open]"
  - test_spec_evidence_required: SPEC open w/o evidence FAIL "no_evidence"; same entry WITH (evidence:…) PASS; competency open w/o evidence still FAIL
  - test_observe_from_spec_block: §7 block open "rate-limit retry", no legacy / _task_prose / assert observe == "rate-limit retry"
  - test_observe_legacy_fallback: §7 only legacy "Spec delta for the next loop: X" / _task_prose / assert observe == "X"; spec collector empty
  - test_deltas_lists_spec_section: one open SPEC + one open competency / cmd_deltas text has both sections; --json has separate keys (spec, by_competency)
  - test_new_task_scaffolds_spec_block: new-task / TASK.md §7 has "### Spec delta", NOT "Spec delta for the next loop:"; tmpl≡fallback for that block
  - (regression) existing delta tests + test_delta_grammar_dedup + bundle/tree parity stay green
</test_plan>

Tests live in: `add-method/tooling/test_spec_delta_grammar.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/templates/TASK.md.tmpl` `add-method/tooling/test_spec_delta_grammar.py` `add-method/tooling/test_ground_prose.py` `add-method/tooling/test_template_form_tags.py` `add-method/tooling/test_deltas_report.py` `add-method/tooling/test_report.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `.add/tooling/add.py` `.add/tooling/templates/TASK.md.tmpl`
<!-- §5 EXPANDED mid-build (disclosed @ verify, re-anchored by re-crossing tests→build): the §7 observe-format change rippled into (a) test_report.py — 2 downstream observe tests consumed the removed legacy placeholder; updated to the new SPEC block, intent preserved · (b) engine_pin.py — the routine ENGINE_MD5 re-pin every engine task does · (c) the TASK.md.tmpl mirror copies (.add + _bundled). Behavioral contract (§3) UNCHANGED. -->

Strategy (ordered batches): 1. write the red suite test_spec_delta_grammar.py · 2. add grammar constants (_SPEC_STATUSES, _SPEC_DELTA_RE, _STATUS_SETS) · 3. _collect_open_spec_deltas + _task_prose observe-from-block + legacy fallback · 4. tag-scoped _lint_task_deltas · 5. cmd_deltas SPEC section + --json key · 6. template swap (TASK.md.tmpl + _FALLBACK_TASK) · 7. update any old-field regression tests · 8. sync .add/tooling + prepare_bundle, assert parity
Safety rule (feature-specific): the grammar is SINGLE-SOURCE — _SPEC_DELTA_RE/_STATUS_SETS are defined ONCE beside _DELTA_RE; the lint/collector/parser all import them (no second SPEC regex). Validate-all-then-write across the 3 add.py copies (parity is byte-exact or the edit is incomplete).
Code lives in: `add-method/tooling/` (engine) — NOT this task's `./src/`.
Constraints: do NOT change any test's intent or the frozen contract; allow-list packages only (stdlib re only); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1169 OK (3 skipped); baseline was 1158 → +11 new
- [x] coverage did not decrease — +11 SPEC tests, 35 assertions; no test removed
- [~] no test or contract was altered during build — CONTRACT untouched. TWO test edits DISCLOSED: (1) test_spec_delta_grammar.py — isolation fix to test_spec_evidence_required (the 2nd check ran over a project that still held the bad task; overwrite the SAME task — intent preserved, re-anchored by re-crossing tests→build); (2) test_report.py — 2 downstream observe tests consumed the removed legacy placeholder, updated to the new SPEC block (scoping + multi-line-join assertions kept equally strong)
- [x] the green was EARNED — adversarial refute on the LIVE dogfood engine: a fresh project with `- [SPEC · folded]` → `add.py check` → `FAIL unknown_status -> - [SPEC · folded]` (not just fixtures). No vacuous asserts, no stubbed logic
- [x] concurrency / timing — N/A: pure stdlib `re` parsing, read-only collectors, no shared state, no IO races
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `re` only; no new dependency; no eval/shell/network
- [x] layering & dependencies follow CONVENTIONS.md — grammar SINGLE-SOURCE (_SPEC_DELTA_RE/_STATUS_SETS defined once beside _DELTA_RE; lint/collector/parser share them); md5 parity restored across all 3 add.py + 3 template copies; engine_pin re-aimed
- [x] a person reviewed and approved the change — Tin Dang, 2026-06-16 (gate PASS, deviations disclosed below)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: _SPEC_STATUSES ×2 · _SPEC_DELTA_RE ×5 · _STATUS_SETS ×6 · _spec_delta_entries ×3 (def + _collect_open_spec_deltas + _task_prose) · _collect_open_spec_deltas ×2 (def + cmd_deltas)
- [x] DEAD-CODE (code) — no orphaned symbol; each new constant/function has a live call site (confirmed by the ref counts above)
- [x] SEMANTIC (prose) — TASK.md.tmpl §7 + _FALLBACK_TASK read in full: legacy line gone, `### Spec delta` block present, comment count held at 11 (<12 lean-pass); engine_pin trail prepended newest-first

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-16   (deviations disclosed: 2 test edits [isolation + downstream], §5 scope expansion, wording reword — no contract/security)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `check` red-rate on malformed SPEC lines · `deltas --json` open-spec count drift

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task.
  - [SPEC · dropped] add `new-task --from-delta <prior>` to seed an open SPEC delta into the next task's §1 Feature, flipping it `seeded` with a `[→ <new>]` stamp (evidence: this loop landed the grammar but `seeded`/`dropped` have no writer yet — seed-and-drop, task 2)
  - [SPEC · dropped] `compact` must block open SPEC deltas, symmetric with the open-competency `open_deltas_unfolded` guard, and status/report must nudge unconsumed ones (evidence: an open SPEC line can currently be lost at compaction with no warning — spec-delta-guards, task 3)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [ADD · folded] a §5 BUILD scope for an `add.py` parser change must pre-list the test mirrors, `engine_pin.py`, and the 3 byte-identical dogfood copies up front — the change ripples to all of them (evidence: scope under-declared mid-build forced a tests→build re-cross to re-anchor the tripwire) [folded foundation-version 36]
  - [TDD · folded] before removing a template/placeholder field, grep its downstream consumers first — observe-reading tests broke on the removed legacy `Spec delta for the next loop:` line (evidence: test_report.py 2 regressions surfaced only at full-suite run) [folded foundation-version 36]
  - [SDD · folded] the domain wording-lint rejects status-name slang in new docstrings — document the grammar abstractly, not by spelling the status words (evidence: test_sync_guidelines_domain_clean failed twice before the reword) [folded foundation-version 36]
