# TASK: Rule-ID coverage lint: §1 Musts/Rejects get stable IDs, add.py check WARNs on unscenarioed/untested rules

slug: rule-id-coverage · created: 2026-07-01 · stage: mvp
milestone: traceability-ids
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_check` (l.2666-3012) — the per-task read-only WARN loop; a new
    coverage-gap WARN is inserted here, reusing the already-read `_task_text` per task (same
    insertion pattern the M3 dangling-lineage WARN from `delta-task-backlink` used).
  - `add-method/tooling/add_engine/predicates.py` — pure-predicate module (`_persona_missing`,
    `_section_unfilled`, `_task_done`, `_phase_owner`, `_setup_locked`, `_milestone_confirmed`,
    `_persona_slug_valid`); the new pure function `_rule_coverage_gaps(bodies: dict[int, str]) ->
    list[str]` belongs here, same style/signature shape as its siblings.
  - `add-method/tooling/add_engine/constants.py:238-251` — the shared delta/tag regex block
    (`_DELTA_RE`, `_PERSONA_TAG_RE`, `_EVIDENCE_RE`, `_SPEC_DELTA_RE`, `_SEED_POINTER_RE`); new
    regexes join this block for a §1 Must-ID line (`- M#:`), a §1 Reject error-code
    (`-> "<error_code>"`), a §2 scenario tag (`# M1, R:code`), and the new §4 `covers:` line.
  - `add-method/tooling/add_engine/taskdoc.py:_raw_phase_bodies` (l.184-191, wraps `_phase_spans`)
    — returns `{1: <§1 text>, 2: <§2 text>, 4: <§4 text>, ...}` keyed by phase number; the new
    predicate consumes `_raw_phase_bodies(root, slug)` directly, no new reader needed.
  - `add-method/tooling/templates/TASK.md.tmpl` (3 trees: `add-method/tooling/templates/`,
    `.add/tooling/templates/`, `add-method/src/add_method/_bundled/tooling/templates/`) — §4
    TESTS' `test_<scenario>:` bullet (l.99-100 canonical) gains a `covers:` reference grammar; §2
    SCENARIOS' back-reference slot (l.60, `# <Must/Reject item this covers, e.g. M1 or R1>`) was
    already shipped by `template-structural-gaps` (M2, e4d287d) — this task CONSUMES it, does not
    re-build it.
  - `add-method/docs/03-step-1-specify.md`, `04-step-2-scenarios.md`, `06-step-4-tests.md` (path
    corrected from an earlier typo — confirmed the canonical book source is `add-method/docs/`,
    NOT `add-method/tooling/docs/`) + the repo-root `NN-*.md` twin (git-tracked, confirmed
    byte-identical today) — the 2 git-tracked book trees to extend with a short convention note;
    `.add/docs/` is a 3rd, gitignored, opportunistic local mirror (same class as `.add/tooling` /
    `.add/personas-teacher`) — never required for parity. The SKILL's own `phases/1-specify.md` /
    `2-scenarios.md` / `4-tests.md` are DELIBERATELY left untouched (see §1 Framings) to avoid the
    lean-pool byte budget those files carry (`test_skill_lean.py`) — the TASK.md.tmpl template's
    own inline placeholder is the primary teaching surface, per the co-specify Diverge below.
Context (working folder):
  - `.add/milestones/traceability-ids/MILESTONE.md` — this task's owning milestone doc: states the
    goal, scope (In/Out — "no blocking gate, all findings are WARNs"), shared decisions (rule IDs
    are AUTHOR-STABLE), and this task's exit criterion (#1 of 3).
  - `add-method/tooling/test_template_structural_gaps.py` — sibling test pinning the M2
    scenario-tag placeholder already shipped; must stay green, not be re-litigated.
  - `add-method/tooling/test_delta_task_backlink.py` — style precedent for a WARN-only,
    `cmd_check`-loop-inserted lineage-style check (closest sibling to what this task builds).
  - `.add/GLOSSARY.md` — checked for an existing "rule ID" / "coverage" entry; none found — a new
    domain term ("coverage gap") may need a Glossary delta at §3 freeze.
Honors (patterns / conventions):
  - warn-never-block: every new finding is a WARN (exit 0), never FAIL — MILESTONE.md's own scope
    ("Out: any blocking gate — all findings are WARNs") and the established `cmd_check` convention
    (`goal_not_auto_ready`, dangling-lineage, `contract_consumer_stale`, etc. are all WARNs, never
    added to the `checks`/`failed` list).
  - NO-EXEC: pure read + regex predicate, no network/spawn — mirrors `_persona_missing`'s
    FORBIDDEN_EXEC guarantee (test_persona_setup.py).
  - Rule IDs are AUTHOR-STABLE (MILESTONE.md Shared decisions): the engine reads `M#`/`R:<code>`,
    never renumbers them.
  - Engine parity: every `add.py` edit re-pins ENGINE_MD5 across all 3 copies (canonical /
    `.add/tooling` mirror / npm-bundled) — the standing ENGINE-CHANGE CHECKLIST invariant every
    prior engine-touching task honors.
  - Template parity across all 3 trees, same discipline as `template-structural-gaps` M4.
  - Phases lean pool stays within budget if guide prose changes — COMPRESS, never grow-and-rebase
    (the established lean-pass convention).
Anchors the contract cites: `add.py:cmd_check`, `add_engine/taskdoc.py:_raw_phase_bodies`, `add_engine/predicates.py`, `add_engine/constants.py:238`, `templates/TASK.md.tmpl` §2/§4
  - `add.py:cmd_check` (l.2666)
  - `add_engine/taskdoc.py:_raw_phase_bodies` (l.184)
  - `add_engine/predicates.py` (new `_rule_coverage_gaps`)
  - `add_engine/constants.py:238` (new regex additions, same block as `_DELTA_RE` et al.)
  - `templates/TASK.md.tmpl` §2 (l.60, already-shipped tag slot) and §4 (l.99-100, new `covers:`
    line)
Issues/Risks (→ feed §1):
  ⚠ Two DIFFERENT reject-ID grammars currently coexist: §2's own template placeholder text reads
    `# M1 or R1` (a bare `R1`), while MILESTONE.md's prose specifies `R:<error_code>` and the ONE
    real shipped example (`delta-task-backlink`'s §2, e.g. `# M2, R:backlink_clobbers_authored`)
    actually uses the `R:<code>` form — a Reject's ID IS its literal error_code string from
    `-> "<error_code>"` in §1, not a positional `R1`/`R2` sequence number. The parser MUST follow
    the real, already-shipped convention (`R:<error_code>`), not the template's own stale example
    text — building against the wrong grammar would make the WARN never fire on real Reject lines.
  - Retroactive scope: dozens of existing closed/archived tasks predate this convention and use
    M#/R:code inconsistently or not at all — the WARN must be measure-only and never retro-flag a
    done/archived task (mirrors the `implicit_autonomy` guard's existing "done/observe predecessors
    are SKIPPED" precedent).
  - The `covers:` line is a brand-new template field with NO existing real-task precedent (unlike
    M#/R:code, which are "already used by convention") — its exact grammar/placement is this
    task's own design decision, not a formalization of prior art.
Related intent:
  - `.add/milestones/traceability-ids/MILESTONE.md` — `rule-id-coverage` is task 1 of the
    milestone's 2-task plan; satisfies exit criterion 1 ("A §1 Must or Reject with no §2 scenario
    tag and no §4 test covering its ID makes `add.py check` print a coverage WARN, exit 0").
  - MILESTONE.md rationale — the PR40 audit found a rule restated 5× downstream (§1/§2/§3/§5/§6)
    with no machine link, so a Must can silently ship unscenarioed or untested; this task closes
    that gap for the §1→§2→§4 chain specifically.
  - `template-structural-gaps` (M2, commit e4d287d) — already shipped the §2 scenario-tag
    placeholder slot this task's parser consumes; this task does not redo that work.
Ground SHA: c152945

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py check` gains a rule-ID coverage WARN — a §1 Must/Reject ID with no §2 scenario tag
  and no §4 `covers:` reference is a coverage gap, surfaced as a never-blocking WARN; §4 TASK.md.tmpl
  gains the `covers:` grammar; the check is OPT-IN PER TASK (grandfathered unless the task already
  uses the tagging convention at all), so 50+ legacy tasks are never retro-flagged.
Framings weighed: opt-in keyed on §2/§4 TAG PRESENCE (chosen — human-confirmed 2026-07-01: a task
  with zero `# M…`/`# R:…` tags in §2 and zero `covers:` lines in §4 is fully legacy-silent; any
  task with at least one tag is coverage-checked in full, including after it reaches `done` so an
  already-shipped gap still surfaces — matches the existing milestone-backlink-drift grandfather
  precedent) · opt-in keyed on §1 `M#:` prefix presence (rejected — Reject lines have ALWAYS carried
  an error code by pre-existing convention, so this signal would immediately put every historical
  Reject in scope regardless of whether that task ever adopted §2/§4 tagging — the exact noise the
  human asked to avoid) · live-tasks-only (rejected — a Must that ships without coverage would stop
  being flagged the moment its task closes, defeating the PR40 audit finding that motivated this
  milestone) · check ALL tasks unconditionally (rejected — floods `check` with warnings for dozens
  of pre-existing tasks never meant to follow this grammar).
Must:
<must>
  - M1: a §1 Must line matches `- M<n>: <text>` (its author-stable ID is `M<n>`); a §1 Reject line
    matches `- <situation> -> "<error_code>"` (its ID is `R:<error_code>`, the literal code string —
    never a positional `R1`/`R2` sequence number).
  - M2: a task is COVERAGE-CHECKED iff its §2 SCENARIOS carries at least one back-reference tag
    (`# ...M<n>...` or `# ...R:<code>...` trailing a `Scenario:` line) OR its §4 TESTS carries at
    least one `covers:` line — i.e. it has adopted the tagging convention at all. A task with NEITHER
    is GRANDFATHERED: fully silent, regardless of how many `M<n>:`-prefixed Musts or coded Rejects
    its own §1 has.
  - M3: for a coverage-checked task, each §1 Must ID (`M<n>`) and Reject ID (`R:<code>`) is COVERED
    if it appears in at least one §2 scenario tag OR at least one §4 `covers:` line (either satisfies
    it — not both required). An ID in neither is a coverage gap.
  - M4: `add.py check` emits one WARN per coverage-gap ID, naming the task slug, the rule ID, and
    whether it is a Must or Reject (e.g. `rule 'M3' (Must) has no §2 scenario tag and no §4 test
    covering it`); the WARN never turns `check` red (exit 0 unaffected) — same discipline as every
    other WARN already in `cmd_check`.
  - M5: `templates/TASK.md.tmpl`'s §4 `test_<scenario>:` bullet gains an optional trailing `covers:`
    reference (e.g. `- test_foo: arrange … / act … / assert … · covers: M1, R:code`), landed
    byte-identically across all 3 template trees.
  - M6: the coverage check runs for a coverage-checked task in ANY phase (including `done`/
    `observe`) — no phase-based skip — so a gap in already-shipped work still surfaces; this is
    deliberately UNLIKE the tripwire/scope-violation build-integrity checks (which are live-only by
    design, since they stop mattering once a task is gated done).
  - M7: invariants — every `add.py` copy stays byte-identical == the re-pinned `engine_pin.ENGINE_MD5`;
    templates parity holds across all 3 trees; the phases lean pool stays within budget; full suite
    green.
</must>
Reject:
<reject>
  - a coverage WARN fires for a task with zero §2/§4 tags (never opted in) -> "coverage_check_ungrandfathered"
  - a coverage WARN (or any accumulation of them) turns `check`'s exit code non-zero -> "coverage_warn_blocks"
  - a Must/Reject ID that IS covered (a tag or a `covers:` line names it) is still flagged as a gap -> "false_coverage_gap"
  - a coverage-checked task's gap stops being flagged once the task reaches `done`/`observe` -> "gap_skipped_on_done"
  - an unreadable or malformed TASK.md raises instead of degrading silently (mirrors the existing `_task_text = None` degrade-safe pattern elsewhere in `cmd_check`) -> "check_crashes_on_malformed_task"
  - the build edits add.py without re-pinning ENGINE_MD5 across all copies -> "engine_pin_drift"
</reject>
After:
<after>
  - `add.py check` on a coverage-checked task (any §2 tag or §4 `covers:` line present) WARNs once
    per Must/Reject ID that has neither a §2 tag nor a §4 `covers:` reference; a task using no
    tagging at all stays completely silent; `TASK.md.tmpl`'s §4 carries the new `covers:` grammar
    across all 3 trees; add.py re-pinned ×3; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Gating "coverage-checked" on §2/§4 TAG PRESENCE (not on §1 `M<n>:` prefix presence) is the right
    opt-in signal — lowest confidence because it is a design choice, not yet verified against the
    real task corpus: it assumes no existing task has `M<n>:`-prefixed Musts in §1 while its §2/§4
    remain fully untagged in a way that SHOULD still be checked. If wrong: a real gap in such a task
    would go unflagged. Mitigate: at build time, grep all `.add/tasks/*/TASK.md` (live) for `# M\d`
    or `# R:` in §2 and `covers:` in §4, confirm the corpus splits cleanly into "zero tags anywhere"
    vs. "at least one tag" with no in-between case that this predicate would mis-handle.
  - [ ] the §2 tag regex (`# M1`, `# M2, R:backlink_clobbers_authored`, `# R:false_dangling_warn`,
    `# M5, R:engine_pin_drift` — comma-separated mixed Must/Reject IDs) captures every real form —
    confirm against `delta-task-backlink`'s and `template-structural-gaps`' actual §2 text during build.
  - [ ] the `covers:` line's trailing free-form placement on a `test_<scenario>:` bullet parses
    unambiguously without a stricter delimiter — confirm by hand-authoring one example and running
    the regex against it before wiring `cmd_check`.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a Must/Reject line's ID grammar is recognized   # M1
  Given a §1 Must line `- M3: some behavior` and a Reject line `- bad input -> "code_x"`
  When the task's §1 is parsed
  Then the Must's ID resolves to `M3` and the Reject's ID resolves to `R:code_x`

Scenario: a fully untagged task is grandfathered   # M2, R:coverage_check_ungrandfathered
  Given a task whose §2 has zero `# M…`/`# R:…` tags and whose §4 has zero `covers:` lines
  When `add.py check` runs
  Then no coverage WARN is printed for that task, regardless of how many M#-prefixed Musts or
       coded Rejects its §1 has

Scenario: one tag anywhere opts the task in   # M2
  Given a task whose §2 has exactly one `# M1` tag and nothing else tagged
  When `add.py check` runs
  Then the task is coverage-checked in full — every other untagged Must/Reject ID in its §1 is
       evaluated for coverage

Scenario: a §4 covers: line alone satisfies coverage   # M3
  Given a Must `M2` with no §2 scenario tag naming it, but a §4 test-plan line `covers: M2`
  When `add.py check` runs
  Then `M2` is NOT flagged as a coverage gap

Scenario: an ID in neither §2 nor §4 is a gap   # M3, R:false_coverage_gap
  Given a coverage-checked task whose Must `M4` appears in no §2 tag and no §4 covers: line
  When `add.py check` runs
  Then `M4` is flagged as a coverage gap
  And a Must `M1` that IS tagged in §2 is not flagged

Scenario: the coverage gap prints as a WARN, never red   # M4, R:coverage_warn_blocks
  Given a coverage-checked task with one real coverage gap and no other red findings
  When `add.py check` runs
  Then it prints `WARN` naming the task slug, the rule ID, and Must-or-Reject
  And the process exits 0

Scenario: the covers: grammar lands in the template across all 3 trees   # M5
  Given the build has edited `templates/TASK.md.tmpl`
  When the 3 template trees (canonical, `.add/tooling` mirror, npm-bundled) are diffed
  Then all 3 are byte-identical and each carries the new `covers:` line on the `test_<scenario>:` bullet

Scenario: a gap in a done task still surfaces   # M6, R:gap_skipped_on_done
  Given a coverage-checked task whose phase is `done` and whose Must `M2` has no §2 tag or §4 covers: line
  When `add.py check` runs
  Then the coverage WARN for `M2` is still printed — not suppressed because the task is done

Scenario: a malformed TASK.md degrades silently   # R:check_crashes_on_malformed_task
  Given a task whose TASK.md is unreadable or whose §1/§2/§4 sections fail to parse
  When `add.py check` runs
  Then no exception is raised — the task is skipped for the coverage check, the same way other
       degrade-safe checks in `cmd_check` already skip an unreadable TASK.md

Scenario: a duplicate rule ID in §1 does not crash the check   # edge case
  Given a §1 with two Must lines both accidentally labeled `M1`
  When `add.py check` runs
  Then it does not raise, and `M1` is treated as covered if EITHER occurrence's ID appears in a
       §2 tag or §4 covers: line — inventing a duplicate-ID WARN is explicitly out of this task's scope

Scenario: engine parity holds   # M7, R:engine_pin_drift
  Given the build edited add.py / add_engine / templates
  When every add.py copy and every template tree is compared
  Then all are byte-identical, add.py == the re-pinned engine_pin.ENGINE_MD5, and the full suite is green
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
rule-id-coverage — frozen shape @ v1   (engine measures; NO-EXEC, warn-only, never blocks)

add_engine/constants.py — new regex constants, joining the existing _DELTA_RE/_SPEC_DELTA_RE block:
    _MUST_ID_RE     = re.compile(r"^\s*-\s*(M\d+)\s*:", re.MULTILINE)
    _REJECT_CODE_RE = re.compile(r'^\s*-\s.*->\s*"([^"]+)"\s*$', re.MULTILINE)
    _SCENARIO_TAG_RE = re.compile(r"^\s*Scenario:.*#\s*(.+?)\s*$", re.MULTILINE)
    _COVERS_LINE_RE  = re.compile(r"covers:\s*(.+?)\s*$", re.MULTILINE)
    _TAG_TOKEN_RE    = re.compile(r"(M\d+|R:[A-Za-z0-9_]+)")

add_engine/predicates.py — new pure function (PURE, IO-free, mirrors _seeded_delta_pointers style):
    def _rule_coverage_gaps(sec1: str, sec2: str, sec4: str) -> list[tuple[str, str]]:
        tag_ids = set()
        for m in _SCENARIO_TAG_RE.finditer(sec2 or ""):
            tag_ids.update(_TAG_TOKEN_RE.findall(m.group(1)))
        for m in _COVERS_LINE_RE.finditer(sec4 or ""):
            tag_ids.update(_TAG_TOKEN_RE.findall(m.group(1)))
        if not tag_ids:
            return []                                  # grandfathered — never adopted tagging
        musts   = [(mid, "Must") for mid in _MUST_ID_RE.findall(sec1 or "")]
        rejects = [(f"R:{code}", "Reject") for code in _REJECT_CODE_RE.findall(sec1 or "")]
        gaps = [(rid, kind) for rid, kind in musts + rejects if rid not in tag_ids]
        return list(dict.fromkeys(gaps))                # de-dup a repeated/typo'd ID

add.py cmd_check — in the existing per-task WARN loop, reusing the already-read `_task_text`
  (imports `_phase_spans` from add_engine.taskdoc alongside the existing taskdoc imports):
    if _task_text is not None:
        _spans = _phase_spans(_task_text)
        for _rid, _kind in _rule_coverage_gaps(_spans.get(1, ""), _spans.get(2, ""), _spans.get(4, "")):
            warnings.append((f"task '{slug}'", f"rule '{_rid}' ({_kind}) has no §2 scenario tag "
                             "and no §4 test covering it (coverage gap) — add a scenario tag or "
                             "a covers: line"))
  -> WARN only (feeds `warnings`, never `checks`/`failed`); runs for a task in ANY phase (no
     done/observe skip — M6); degrade-safe (unreadable TASK.md -> _task_text None -> skipped,
     same as the existing dangling-lineage check reusing the same read).

templates/TASK.md.tmpl (all 3 trees) — §4 TESTS test_plan bullet gains an optional trailing field:
    - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
        · covers: <M#, R:code — optional>
  -> additive only; introduces no new bracketed <tag> (still exactly test_plan's existing form).

add-method/docs/03-step-1-specify.md, 04-step-2-scenarios.md, 06-step-4-tests.md (+ repo-root
  twin) — each gains ONE short paragraph naming the M#/R:code/covers: convention and pointing at
  the template's own inline example as the authoritative grammar. `.claude/skills/add/phases/*.md`
  is NOT touched (avoids the lean-pool byte budget; the template placeholder + book chapter are
  the teaching surface, not the skill guide prose).

Invariants: add.py ×3 byte-identical == re-pinned engine_pin.ENGINE_MD5; templates ×3 byte-identical;
  phases lean pool (skill/add/phases/*.md) UNTOUCHED; full suite green.
```

Glossary deltas: Coverage gap: a §1 Must/Reject ID with no §2 scenario tag and no §4 `covers:`
  reference, surfaced by `add.py check` as a WARN (never a blocking failure). [folded foundation-version 64]
Least-sure flag surfaced at freeze: [spec] opt-in gating on §2/§4 tag presence rather than §1
  `M<n>:`-prefix presence — unverified against the real task corpus. Risk: a live task whose §1
  already uses `M<n>:`-prefixed Musts but whose §2/§4 remain fully untagged would go unflagged if
  this framing is wrong. Mitigated: human confirmed opt-in-by-usage 2026-07-01; build step 1 (§5
  Strategy) re-verifies against the real corpus via a grep sweep before wiring `cmd_check`, and
  `_rule_coverage_gaps` stays an independently adjustable pure function if the sweep contradicts it.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete (one test per Must + per Reject + the pure-regex unit tests)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_id_grammar_recognized: §1 `M<n>:`/`-> "<code>"` lines resolve to `M<n>`/`R:<code>` IDs · covers: M1
  - test_zero_tags_grandfathers_the_task: no §2/§4 tags anywhere / check prints no coverage gap · covers: M2, R:coverage_check_ungrandfathered
  - test_one_tag_opts_the_task_in: one §2 tag present / the untagged sibling Must is flagged · covers: M2
  - test_covers_line_alone_covers_a_must: a §4 covers: line with no matching §2 tag / not flagged · covers: M3
  - test_uncovered_must_is_flagged_tagged_must_is_not: mixed tagged/untagged §1 IDs / only the untagged one flagged · covers: M3, R:false_coverage_gap
  - test_gap_prints_as_warn_and_exits_zero: a real gap / prints WARN naming Must-or-Reject, exit 0 · covers: M4, R:coverage_warn_blocks
  - test_covers_field_present_and_trees_match: templates/TASK.md.tmpl 3-tree parity + covers: field present · covers: M5
  - test_gap_still_warns_once_task_is_done: a coverage-checked task forced to phase=done / gap still WARNs · covers: M6, R:gap_skipped_on_done
  - test_check_does_not_crash_on_malformed_task: unreadable/garbage TASK.md / check runs without raising · covers: R:check_crashes_on_malformed_task
  - test_duplicate_id_deduped_not_double_warned: a duplicated §1 ID / reported once, not twice · covers: (edge case)
  - test_real_shipped_tag_grammar: the regex against delta-task-backlink's REAL §2 tag form · covers: (edge case)
  - test_engine_byte_identical_to_pin / test_phases_pool_untouched · covers: M7, R:engine_pin_drift
</test_plan>

Tests live in: `add-method/tooling/test_rule_id_coverage.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` · `add-method/tooling/add_engine/constants.py` · `add-method/tooling/add_engine/predicates.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/templates/TASK.md.tmpl` · `.add/tooling/add.py` · `.add/tooling/add_engine/` · `.add/tooling/templates/TASK.md.tmpl` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add_engine/` · `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` · `add-method/docs/03-step-1-specify.md` · `add-method/docs/04-step-2-scenarios.md` · `add-method/docs/06-step-4-tests.md` · `add-method/../03-step-1-specify.md` · `add-method/../04-step-2-scenarios.md` · `add-method/../06-step-4-tests.md` · `add-method/tooling/test_rule_id_coverage.py`
Strategy (ordered batches):
  1. Add the 5 regex constants to `constants.py`, joining the existing `_DELTA_RE`/`_SPEC_DELTA_RE`
     block.
  2. Add `_rule_coverage_gaps` to `predicates.py`; unit-test the regexes directly against
     `delta-task-backlink`'s REAL §2 text (the `R:<code>` form), not the template's stale
     `# M1 or R1` example.
  3. Wire the WARN into `cmd_check`'s existing per-task loop (import `_phase_spans` alongside the
     existing `add_engine.taskdoc` imports); end-to-end test via a temp `.add/` project, same
     harness style as `test_delta_task_backlink.py`.
  4. Extend `templates/TASK.md.tmpl` §4 with the `covers:` field across all 3 trees; re-run
     `test_template_structural_gaps.py` / `test_template_form_tags.py` / `test_bundle_parity.py`
     to confirm no regression.
  5. Extend the 3 book chapters + repo-root twin with one short convention paragraph each.
  6. Re-pin `engine_pin.ENGINE_MD5` across all 3 `add.py` copies; re-verify template 3-tree parity;
     run the FULL suite.

Persona (optional): `methodology-engine-dev` — this build is pure `add.py`/engine work (regex +
  predicate + cmd_check wiring), the persona's own home turf.
Known-problem fixes:
  - trap: building the regex against the template's own stale `# M1 or R1` example instead of the
    REAL, already-shipped `R:<code>` convention -> fix: pin the regex test against
    `delta-task-backlink`'s actual §2 text first.
  - trap: a second file-read of TASK.md inside `cmd_check` (duplicating the loop's `_task_text`)
    -> fix: call `_phase_spans(_task_text)` directly (pure, no IO) — never `_raw_phase_bodies`
    (which re-reads the file).
  - trap: retroactively flooding `check` with warnings for 50+ legacy tasks -> fix: the
    opt-in-by-tag-presence gate (`if not tag_ids: return []`) in `_rule_coverage_gaps` itself.
Strategy actually used: as planned (the 6 ordered batches), with one extra self-heal cycle beyond
  the plan — TDD caught that the §4 `covers: <M#, R:code — optional>` template placeholder text
  itself false-matched `_TAG_TOKEN_RE` (it contains the literal substring `R:code`), defeating the
  grandfather gate for every freshly-scaffolded task. Fixed by stripping bracketed `<...>`
  placeholder spans from §2/§4 before tag extraction (mirrors `_section_unfilled`'s own
  placeholder convention), then re-synced + re-verified across all 3 engine trees. Also needed a
  second self-heal beyond the plan's 6 batches: the §5 Scope declaration itself was authored
  wrong twice — first as a multi-line `·`-joined list (the engine's scope-token parser reads only
  the Scope line's FIRST physical line) and second with bare repo-root tokens (`03-step-1-
  specify.md`) that the bare-token grammar resolves as a *sibling of the previous token's dir*
  (`add-method/docs/`), not project root — fixed by collapsing Scope to one physical line and using
  the `add-method/../<name>` project-root-climb form for the repo-root doc twins, then re-crossing
  tests->build to re-snapshot the anchor.
Safety rule (feature-specific): `cmd_check` stays strictly read-only — the new coverage-gap code
  path must not write any file (matches its own docstring: "Read-only integrity check").
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `python3 -m unittest discover` over `add-method/tooling`: 2635 passed, 0 failed (incl. the 13 new `test_rule_id_coverage.py` tests)
- [x] coverage did not decrease — every new symbol (`_rule_coverage_gaps`, the 5 regex constants, the `cmd_check` wiring) has a dedicated test; no existing test removed or weakened
- [x] no test or contract was altered during build — `add.py check` reported no `build_tampered` WARN for this task throughout the build (tamper tripwire silent)
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe — N/A: `_rule_coverage_gaps` is a pure, IO-free function over already-loaded strings; no shared mutable state, no I/O, no async path
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure regex over text already read by the caller; no new dependency, no subprocess/network/eval
- [x] layering & dependencies follow CONVENTIONS.md — new regexes join `constants.py`'s existing tag-regex block; `_rule_coverage_gaps` lives in `predicates.py` beside its pure siblings (`_persona_missing`, `_section_unfilled`), same shape/signature convention
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py check` on the LIVE task corpus prints a real, correctly-gated coverage-gap WARN for
  already-tagged tasks (e.g. `phase-agents-lean`'s 6 untagged Reject codes — all 6 of its §1
  Rejects, corrected from an initial miscount of 5 by the VERIFY refute-read — and `nested-suite-
  skip-count-tolerance`'s 3) while `check` still exits 0 (`618 passed, 0 failed` alongside the
  WARNs) — confirmed by running `python3 .add/tooling/add.py check` against this repo's real 50+
  tasks
- [x] a task with zero §2/§4 tags anywhere stays completely silent (grandfather holds) — confirmed
  by `test_zero_tags_grandfathers_the_task` (green) AND by the live corpus run above surfacing
  zero WARNs for the dozens of legacy untagged tasks
- [x] `templates/TASK.md.tmpl`'s §4 `covers:` field is present and byte-identical across all 3
  trees — confirmed by `diff` across `add-method/tooling/templates/`, `.add/tooling/templates/`,
  `add-method/src/add_method/_bundled/tooling/templates/`

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_rule_coverage_gaps` is imported at `add.py:301` and called at `add.py:2742-
  2746` inside `cmd_check`'s per-task loop; confirmed by `grep -n _rule_coverage_gaps add.py` and
  by the live `add.py check` run actually emitting the WARN it produces
- [x] DEAD-CODE (code) — no orphaned symbol: the 5 new regex constants are each referenced from
  `_rule_coverage_gaps`; `_rule_coverage_gaps` itself is referenced from `cmd_check`; confirmed by
  `grep` for each constant name (`_MUST_ID_RE`, `_REJECT_CODE_RE`, `_SCENARIO_TAG_RE`,
  `_COVERS_LINE_RE`, `_TAG_TOKEN_RE`) showing exactly one definition + >=1 use site
- [x] SEMANTIC (prose / non-code) — read in full: the 3 book-chapter additions (03/04/06) and the
  `TASK.md.tmpl` `covers:` line; confirmed each names the `M#`/`R:code`/`covers:` grammar and
  points at the template's own inline example, consistent with the frozen §3 commitment

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct
  import (`add_engine.predicates._rule_coverage_gaps`, `add_engine.constants._MUST_ID_RE` /
  `_REJECT_CODE_RE`) and by `grep -n "^def cmd_check"` (now l.2667, was l.2666 at Ground SHA
  c152945 — a 1-line drift from an earlier insertion, not a rename) and `grep -n
  _rule_coverage_gaps add.py` (import l.301, call site l.2742-2746)
- [x] anchor drift named, not left silent — `cmd_check`'s def line moved 2666 -> 2667 (net +1 line
  from an unrelated earlier insertion in this same build); every other cited anchor
  (`add_engine/taskdoc.py:_raw_phase_bodies`, `add_engine/predicates.py`,
  `add_engine/constants.py:238`, `templates/TASK.md.tmpl` §2/§4) resolved at its cited location
  with no rename

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent (add-verify, tdd-verifier persona) · adversarially checked: (1) mutation testing —
  deleted the grandfather gate (`if not tag_ids: return []`) and separately reverted only the
  `<...>` placeholder-strip fix; both times exactly `test_zero_tags_grandfathers_the_task` failed
  with the same assertion, confirming that regression test is load-bearing, not decorative; (2)
  corpus spot-check — hand-read `phase-agents-lean` and `nested-suite-skip-count-tolerance`'s real
  §1/§2/§4 against the live `add.py check` WARN output, every printed gap matched hand analysis;
  (3) edge-case fuzzing beyond the suite (nested/unclosed `<...>` spans, mixed placeholder+real
  tags) — no false "covered" (silenced) result found. No vacuous asserts, no stubbed logic, no
  mocked `add.py check` — tests run the real CLI end-to-end against a real temp `.add/` project.
  🟡 concern (fixed): the Build-expectations evidence line above originally undercounted
  `phase-agents-lean`'s untagged Rejects as 5; the live corpus + hand count show 6 — corrected.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: agent (add-verify, tdd-verifier persona)
1. Security: CLEAR — read-only/NO-EXEC confirmed by code read; fuzzed all 5 new regexes with
   adversarial payloads (200k-char dash runs, 20k unterminated `->` sequences, an 18.5MB combined
   worst case) — all completed <0.4s, no catastrophic backtracking (ReDoS clear).
2. Concurrency: CLEAR — `_rule_coverage_gaps` is pure/IO-free over already-loaded strings; no
   shared mutable state, confirmed by reading the function and its call site.
3. Architecture: CLEAR — every new symbol (5 regexes + `_rule_coverage_gaps`) has exactly one
   definition and >=1 real call site (grep-verified, no dead code); both engine pins independently
   RECOMPUTED (not trusted from comment) and matched; template + 3 book chapters byte-identical
   across all git-tracked trees (md5-verified).
Verdict: PASS
Residue: none blocking. 💭 notes (no action required on this task): `nested-suite-skip-count-
  tolerance` uses a third, older positional tag dialect (`M4/R2`) the frozen contract correctly
  does not recognize — worth flagging when a future backfill task is scoped; an untracked,
  byte-identical `_bundled/tooling/engine_pin.py` sits in the working tree, traced via the scope
  sidecar to a pre-existing file from an earlier, uncommitted task — not this task's residue,
  flagged for whoever commits next.
Binding: yes — mechanical (NO-EXEC, read-only engine change)

### GATE RECORD
Outcome: PASS
Reviewed by: agent (add-verify, tdd-verifier persona, auto-resolved under autonomy: auto — no
  residue, full evidence) · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the coverage-gap WARN count in `add.py check` over time (per-
  task and aggregate) — rising adoption (more tasks tagging §2/§4) should show as more WARNs on
  genuinely uncovered IDs, not a flood on tasks that never opted in; any `coverage_check_
  ungrandfathered`-shaped false positive (a WARN on a task with zero tags) is a regression.

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned (the 6 ordered batches), with one extra self-heal cycle beyond
- [AI] verify — gate PASS (reviewed by agent (add-verify, tdd-verifier persona, auto-resolved under autonomy: auto — no)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] `nested-suite-skip-count-tolerance` uses a third, older POSITIONAL tag dialect [carried: grandfathering nested-suite-skip-count-tolerance's older positional M#/R# dialect is explicitly allowed by this convention; migrating it is a real but non-urgent backfill — no functional gap, just dialect inconsistency]
  (`M4/R2`, `M6/R1/R3`) this convention deliberately does not recognize — decide whether a future
  backfill task migrates it to `M#`/`R:<code>` or leaves it grandfathered (evidence: add-verify's
  refute-read spot-check, 3 correctly-fired gap WARNs against that task's real §1/§2/§4).
- [SPEC · dropped] an untracked, byte-identical `add-method/src/add_method/_bundled/tooling/
  engine_pin.py` sits in the working tree, traced via this task's own scope sidecar to a
  pre-existing file from an earlier, uncommitted task — not this task's residue, but worth
  reconciling with `git status` before the next commit so it isn't lost or double-committed
  (evidence: add-verify's architecture-lens trace).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a new regex-based convention that scans §2/§4 prose must be tested against the [folded foundation-version 60]
  template's own UNFILLED placeholder default, not just filled examples — this task's `covers:
  <M#, R:code — optional>` placeholder contained the literal substring `R:code`, false-matching
  the tag regex and defeating the grandfather gate for every freshly-scaffolded task, until a
  regression test (`test_zero_tags_grandfathers_the_task`) caught it before build closed (evidence:
  the fix — stripping bracketed `<...>` placeholder spans before tag extraction — was driven
  entirely by that one regression, confirmed load-bearing by add-verify's mutation test).
- [ADD · folded] the §5 "Scope (may touch):" parser reads ONLY its first physical line, and a BARE [folded foundation-version 60]
  repo-root filename token resolves as a sibling of the PREVIOUS token's directory, not project
  root (use the `add-method/../<name>` climb form) — this is the THIRD task in this project's
  history to independently hit the multi-line-Scope truncation (after `phase-agents-lean` and
  `template-structural-gaps`), each needing the same `phase tests <slug>` → `phase build` re-anchor
  recovery; worth a future task making the parser read the whole declaration, not just line one
  (evidence: this task's own §5 Scope needed that exact recovery twice — once for the line-wrap
  truncation, once for the bare-token repo-root resolution).
- [ADD · folded] an orchestrator doing unrelated parallel work (this session: editing `add-verify.md` [folded foundation-version 60]
  to fix a persona-loading gap) inside the SAME repo while a task's build-scope snapshot is active
  gets caught by the scope-lock tripwire as an out-of-scope touch on that OTHER task, even though
  it shares no code with it — the recovery (re-cross tests→build to refresh the baseline) is
  correct but consumes one of the bounded `HEAL_CAP` attempts; worth deciding whether cross-task
  noise like this should count against the same cap as a real cheat, or be distinguished from one
  (evidence: this task's `gate PASS` was returned to BUILD once for exactly this reason, attempt
  1 of 3, before the true redo succeeded).

