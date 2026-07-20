# TASK: Wire grounding into the freeze checklist + status/check (measure)

slug: ground-bundle-wiring · created: 2026-06-10 · stage: mvp
autonomy: conservative   <!-- lowered from project default (auto): touches the engine (status/check ×3 + repin) AND conforms a cross-task test (test_review_checklist 6→7). conservative DISABLES auto-PASS — I own the verify gate (under Tin Dang's full-autonomy delegation). additive · measure-not-block, so NOT risk:high. -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add.py:cmd_status` (the `if active and active in tasks:` block prints `autonomy:`) · `add.py:cmd_check` (the `warnings` list; `goal_not_auto_ready` is the precedent) · `add.py:_raw_phase_bodies` / `_phase_spans` (read §0 by number; bound widened to capture §0 by ground-phase-engine) · `add.py:_contract_frozen` (the FROZEN signal) · `add.py:_decision_markers` · `skill/add/phases/3-contract.md` "## The freeze review checklist" (6 items) · `skill/add/run.md` ("six lines") · `tooling/templates/TASK.md.tmpl` §0 "Anchors the contract cites:" line.
Honors (patterns / conventions): the goal-ready surface is the exact mirror — measure-not-block, human-readable status line + a never-red WARN riding the `warnings` array (no new `--json` key); byte-identical add.py ×3 + engine_pin repin in lockstep; md_section slices the checklist (heading-inclusive → 15 non-blank now).
Anchors the contract cites: `_grounded_state` · `_section0_anchors` · `_task_grounded` · `cmd_status` grounded line · `cmd_check` `task_not_grounded` WARN · `3-contract.md` **Grounded** item · `run.md` "seven lines" · `test_review_checklist` 6→7.
<!-- grounded retroactively at build: this task was grandfathered at `specify` (created before the ground phase existed); the §0 records the grounding that actually informed §3. -->

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: wire grounding into the freeze checklist + surface it in status/check (measure-never-block)
Framings weighed: a 7th freeze-checklist bullet + a status/check measure mirroring goal-ready (chosen) · fold grounding into the existing "Shape" bullet (no new line, but buries the milestone's teeth) · a hard gate that blocks freeze until grounded (rejected — that is the deferred "mechanical gate", out of scope this milestone)
Must:
<must>
  - The freeze review checklist (`phases/3-contract.md`) gains a 7th item **Grounded** — "does §3 cite anchors that exist in the §0 GROUND map?"; the ⚠ flags item stays item ONE; the count word "six"→"seven"; the section stays ≤16 non-blank lines; synced byte-identical ×3.
  - `run.md`'s freeze-checklist reference "six lines"→"seven lines"; synced byte-identical ×3.
  - A PURE tri-state measure `_grounded_state(raw) -> True | False | None`: True = the §0 "Anchors the contract cites:" line is filled (real content); False = §0 present but the Anchors line is the `<…>` placeholder/empty; None = no §0 section (a pre-ground / legacy task). Fail-open: an unparseable §0 → None.
  - `add.py status` prints a `grounded:` line for the active task ONLY when §0 exists (True → "grounded ✓"; False → "not yet — fill §0 anchors"); a None (legacy) task prints NO line, so current status output is byte-unchanged. Printed AFTER the `--json` early-return (never on the machine surface).
  - `add.py check` emits a `task_not_grounded` WARN (never red) for the active task IFF its §3 is FROZEN AND `_grounded_state` is False ("you froze without grounding"). It rides the existing sanctioned `warnings` array (like `goal_not_auto_ready`) — no new `--json` key.
  - The 3 add.py trees stay byte-identical and `engine_pin.ENGINE_MD5` is re-aimed in lockstep; full suite green.
</must>
Reject:
<reject>
  - the `--json` status/check surface gains NO new top-level key -> a new key would be "json_surface_unsanctioned_key" (the frozen machine surface is guarded)
  - a pre-ground (legacy, no §0) task is NEVER warned by check -> warning it would be a false "task_not_grounded" on a grandfathered task (None is exempt)
  - grounding NEVER blocks advance / freeze / gate this milestone -> a block would be the deferred "mechanical gate" (out of scope; the chosen teeth are MEASURE)
</reject>
After:
<after>
  - status shows `grounded: …` for an active task that has a §0 map (silent for legacy tasks); check stays green (WARN at most) regardless of grounding; the freeze checklist walks seven items, ⚠ first; the §0 "Anchors the contract cites:" line is the single source the measure reads; 3 add.py trees identical; suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the check WARN should fire on **FROZEN-but-ungrounded** (not phase-based "contract..verify") — lowest confidence because both are defensible and it is a judgment call about when a nudge is a help vs a nag; FROZEN is the precise gap ("the freeze checklist asked, and you froze anyway") and never nags during pre-freeze drafting; if wrong: the WARN fires a phase too late/early → fallback is a phase-index gate. Cost: low (one `_contract_frozen` call I already make). PINNED in test_ground_wiring so the boundary is locked, not incidental.
  - [ ] "grounded" == the §0 "Anchors the contract cites:" line is filled is the right signal (not Touches/Honors) — the exit criterion literally says "grounded + cites anchors", so the Anchors line is the direct read; if wrong: also accept a filled Touches line (one more regex).
  - [ ] ≤16-non-blank-line headroom is EXACT: the checklist is 15 non-blank now (md_section includes the heading), +1 single-physical-line bullet = 16 ≤ 16 — the new bullet MUST be one physical line (self-checking: test_no_ceremony reds instantly on a spill).
  - [ ] editing `test_review_checklist.py` 6→7 is CONFORMANCE, not weakening — disclosed here before build; the ⚠-first + exact-count shape assertions are preserved, only the literal count moves to match this frozen contract.
  - [ ] the §3 template EXIT echo (TASK.md.tmpl ×3) is OPTIONAL reinforcement — inside the existing `<!-- -->` (no new comment), safe but extra ×3 sync; include only as an in-file echo, the criterion does not need it.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a filled §0 Anchors line is grounded
  Given a TASK.md whose §0 "Anchors the contract cites:" line names real symbols
  When _grounded_state reads its raw §bodies
  Then it returns True

Scenario: a placeholder §0 Anchors line is not grounded
  Given a TASK.md with a §0 section whose Anchors line is still the "<…>" placeholder
  When _grounded_state reads its raw §bodies
  Then it returns False

Scenario: a task with no §0 section is exempt (pre-ground / legacy)
  Given a TASK.md with NO "## 0 · GROUND" section
  When _grounded_state reads its raw §bodies
  Then it returns None

Scenario: status surfaces grounding for a §0 task
  Given an active task whose §0 Anchors line is filled
  When I run `add.py status`
  Then the output contains a "grounded:" line reading "grounded ✓"

Scenario: status is silent for a pre-ground task   # additive proof
  Given an active task with NO §0 section (legacy)
  When I run `add.py status`
  Then the output contains NO "grounded:" line
  And the rest of the status output is unchanged

Scenario: check warns (never red) when a frozen contract is ungrounded
  Given an active task whose §3 is FROZEN but whose §0 Anchors line is a placeholder
  When I run `add.py check --json`
  Then the warnings include "task_not_grounded"
  And the exit code is 0 (a WARN, never a red check)
  And "task_not_grounded" is NOT in the failed reasons

Scenario: check is silent before the freeze   # REJECT (no nag during drafting)
  Given an active task whose §3 is DRAFT and whose §0 is ungrounded
  When I run `add.py check --json`
  Then the warnings do NOT include "task_not_grounded"

Scenario: check never warns a pre-ground task   # REJECT (legacy exempt)
  Given an active task whose §3 is FROZEN but which has NO §0 section
  When I run `add.py check --json`
  Then the warnings do NOT include "task_not_grounded"

Scenario: the freeze checklist walks seven items, ⚠ first
  Given phases/3-contract.md
  When the "## The freeze review checklist" section is parsed
  Then it has exactly seven "- **…**" items
  And item one is the ⚠ least-sure-flags item
  And a "Grounded" item names the §0 anchors
  And the section stays ≤ 16 non-blank lines

Scenario: the freeze-checklist prose is byte-identical across trees
  Given 3-contract.md and run.md edited in canonical
  When the bundle/dogfood trees are synced
  Then md5 is identical ×3 for both files
  And run.md says the checklist is "seven lines"

Scenario: the engine stays byte-identical ×3 after the wiring
  Given add.py edited in canonical and synced
  Then md5(canonical) == md5(dogfood) == md5(bundled) == engine_pin.ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
GROUNDING MEASURE — the frozen shape (add-method/tooling/add.py, synced ×3)

PURE helpers (read-only; measure-never-block)
_section0_anchors(raw0: str) -> str | None
    # the value of the "Anchors the contract cites:" line in a §0 GROUND body, stripped;
    # None when no such line exists. Matches `^\s*Anchors the contract cites:\s*(.*)$`.
_grounded_state(raw: dict[int,str]) -> bool | None
    # True  — §0 present AND its Anchors line is filled (non-empty, not the "<…>" placeholder)
    # False — §0 present (key 0 in raw) AND Anchors empty / "<…>" placeholder
    # None  — no §0 section (key 0 absent) OR no Anchors line → pre-ground / legacy, EXEMPT
_task_grounded(root, slug) -> bool | None      # = _grounded_state(_raw_phase_bodies(root, slug))

STATUS surface (cmd_status, human-readable section — AFTER the `--json` early-return)
    in the existing `if active and active in tasks:` block, after the autonomy line:
      g = _task_grounded(root, active)
      if g is not None:                          # None (legacy) prints NOTHING → current output byte-unchanged
          print("grounded: " + ("grounded ✓ — §0 cites the anchors §3 names"
                                 if g else "not yet — fill the §0 GROUND anchors (add.py guide)"))

CHECK surface (cmd_check, rides the EXISTING `warnings` list — no new key)
    _at = state.get("active_task")
    if _at in tasks:
        _raw = _raw_phase_bodies(root, _at)
        if _contract_frozen(_raw.get(3, "")) and _grounded_state(_raw) is False:
            warnings.append(("task_not_grounded",
                             f"task '{_at}' froze its contract without grounding — fill the "
                             "§0 GROUND anchors the contract cites (add.py guide)"))
    # WARN, NEVER a check (never feeds `failed`); exit code stays 0. The active task only.

PROSE — the freeze review checklist (skill/add/phases/3-contract.md, synced ×3)
    "Walk these six"  -> "Walk these seven"
    + a 7th bullet, ONE physical line, placed after **Shape**, ⚠ stays item ONE:
      - **Grounded** — does §3 cite anchors that exist in the §0 GROUND map (real files/symbols),
        not invented ones? `status`/`check` surface this — measure, never block.
    INVARIANTS (test_review_checklist): exactly 7 "- **…**" items · ⚠ first · ≤16 non-blank lines ·
                "the freeze stays the only gate" retained · byte-identical ×3.
PROSE — run.md (synced ×3): "six lines that walk the human" -> "seven lines that walk the human".

CONFORMANCE (driven by THIS frozen contract; value-swap, not weakening)
    test_review_checklist.py::test_seam_guide_presents_checklist: assertEqual(len(items), 6) -> 7
        (the ⚠-first + count-shape assertions are UNCHANGED; only the literal count moves.)

OPTIONAL (in-file echo, inside the existing §3 `<!-- -->`; no new comment) — templates/TASK.md.tmpl ×3
    §3 EXIT line gains: "+ the contract is grounded (its §3 anchors exist in the §0 GROUND map)".

NO-TOUCH (frozen surfaces this task must not move)
    the `--json` status/check KEY SET (no new top-level key) · the spec-bundle / autonomy ladder ·
    PHASES / the ground phase itself (ground-phase-engine owns it) · CHANGELOG history ("six" stays).
TREE PARITY: md5(canonical)==md5(dogfood)==md5(bundled)==engine_pin.ENGINE_MD5; 3-contract.md + run.md byte-identical ×3.
```

Status: FROZEN @ v1 — approved by AI (autonomous, under Tin Dang's full-autonomy delegation) · 2026-06-11
Least-sure flag surfaced at freeze: [contract] the check WARN fires on FROZEN-but-ungrounded (not phase-based "contract..verify") — both are defensible; FROZEN is the precise "the freeze checklist asked, and you froze anyway" gap and never nags during pre-freeze drafting; fallback if wrong is a 1-line phase-index gate. PINNED in test_ground_wiring (test_draft_ungrounded_silent) so the boundary is locked, not incidental.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject scenario (behavior via the real CLI / the pure helper, not internals)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_filled_anchors_is_grounded: §0 Anchors filled -> _grounded_state True
  - test_placeholder_anchors_not_grounded: §0 Anchors "<…>" -> _grounded_state False
  - test_empty_anchors_not_grounded: §0 Anchors present but blank -> _grounded_state False
  - test_no_section0_is_none: no "## 0 ·" section -> _grounded_state None (legacy exempt)
  - test_status_surfaces_grounded_when_filled: active §0-filled task -> status output has "grounded ✓"
  - test_status_surfaces_not_yet_when_unfilled: active §0-placeholder task -> status has "not yet"
  - test_status_silent_for_pre_ground_task: active no-§0 task -> NO "grounded:" line in status (additive proof)
  - test_frozen_ungrounded_warns_not_red: FROZEN §3 + placeholder §0 -> "task_not_grounded" in warnings, code==0, NOT in failed
  - test_draft_ungrounded_silent: DRAFT §3 + placeholder §0 -> no "task_not_grounded" (no pre-freeze nag)
  - test_frozen_grounded_silent: FROZEN §3 + filled §0 -> no "task_not_grounded"
  - test_pre_ground_task_never_warned: FROZEN §3 + no §0 -> no "task_not_grounded" (None exempt)
  - test_checklist_has_seven_items_grounded: 3-contract.md checklist has 7 "- **" items, ⚠ first, a "Grounded" item naming §0/anchors
  - test_checklist_within_line_budget: the checklist section stays ≤16 non-blank lines
  - test_run_md_says_seven_lines: run.md says the checklist is "seven lines"
  - test_prose_three_trees_agree: 3-contract.md + run.md byte-identical ×3
  - test_engine_byte_identical: md5(canonical)==md5(dogfood)==md5(bundled)==engine_pin.ENGINE_MD5
</test_plan>

Tests live in: `test_ground_wiring.py` · run via `cd add-method/tooling && python3 -m unittest discover -p 'test_*.py'`.
RED baseline: the _grounded_state/_section0_anchors helpers don't exist yet (AttributeError) and the status/check surfaces are absent (assertion fail) — red for the right reason. The checklist/run.md/byte-identity tests are red until the prose+sync land. test_review_checklist 6→7 is conformed in BUILD (contract-driven, NOT weakening).
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): measure-not-block — grounding NEVER changes an outcome (no block on advance/freeze/gate); the status line prints AFTER the `--json` early-return; the check WARN rides the EXISTING `warnings` array (no new `--json` key). Edit canonical add.py once → sync byte-identical ×3 → re-aim engine_pin in lockstep; edit canonical 3-contract.md + run.md → sync ×3.
Code lives in: `add-method/tooling/add.py` (synced ×3) · `skill/add/phases/3-contract.md` (×3) · `skill/add/run.md` (×3) · `engine_pin.py`. Tests: `add-method/tooling/test_ground_wiring.py`.
Constraints: do NOT change the frozen §3 or weaken a test; conform test_review_checklist 6→7 only as the contract discloses; stdlib only.

Build note: engine pin re-aimed `ed725504…` → `e6b8c3da98ef092c38f5d1c78760c4ad`. Optional §3-template EXIT echo SKIPPED (recorded) — the criterion is met by the 3-contract.md checklist + the status/check measure; skipping keeps the blast radius tight (grep confirms 0 'grounded' in TASK.md.tmpl). Dogfood: a §0 GROUND map added to THIS task at build (it was grandfathered at specify) — so the live `status` now shows `grounded ✓`.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **780 OK** (was 761; +19 from test_ground_wiring); live dogfood `check: 264 passed, 0 failed`
- [x] coverage did not decrease — +19 new tests; every Must + Reject scenario covered (pure measure + status + check + prose + parity)
- [x] no test or contract was altered to pass — frozen §3 untouched; test_review_checklist 6→7 is the CONTRACT-DISCLOSED conformance (the ⚠-first + count-equality shape preserved); zero assertion weakened
- [x] concurrency / timing — N/A: stdlib, single-process read-only CLI; no concurrency surface added
- [x] no exposed secrets / injection / unexpected deps — stdlib-only; the measure is read-only (reads §0/§3 text); no new dependency; no new `--json` key (the frozen machine surface is unmoved)
- [x] layering & dependencies follow CONVENTIONS.md — additive · measure-not-block · mirrors the goal-ready precedent exactly · fail-open (unparseable §0 → None) · byte-identical ×3 + repin
- [x] a person reviewed and approved the change — see GATE RECORD (gate delegated to the AI under Tin Dang's explicit full-autonomy directive 2026-06-11; the §3 freeze itself was AI-under-delegation; security N/A)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced (grep-confirmed): `_section0_anchors` ← `_grounded_state` (add.py:2170) · `_grounded_state` ← `_task_grounded` (2178) + `cmd_check` (1103) · `_task_grounded` ← `cmd_status` (860) · `task_not_grounded` emitted at cmd_check (1104). All paths exercised by test_ground_wiring (19 green) + demonstrated live (`grounded ✓` on the real board).
- [x] DEAD-CODE (code) — no orphan: 3 new wired helpers + 2 wired call-sites (status line, check WARN). The §3-template EXIT echo was deliberately SKIPPED (grep: 0 'grounded' in TASK.md.tmpl) — no half-wired stub left behind.
- [x] SEMANTIC (prose) — read in full: the 3-contract.md checklist now walks SEVEN items (⚠ first, **Grounded** after **Shape**, 16 ≤ 16 non-blank lines, "the freeze stays the only gate" retained); run.md says "seven lines"; both byte-identical ×3. CHANGELOG "six" left as history (correct).

### GATE RECORD
Outcome: PASS
Reviewed by: AI (autonomous self-review under Tin Dang's explicit full-autonomy delegation — the human DELEGATED this gate; the §3 freeze was AI-under-delegation) · date: 2026-06-11
Evidence: full suite **780 OK**; md5(canonical)==md5(dogfood)==md5(bundled)==engine_pin `e6b8c3da` (re-aimed in lockstep); frozen §3 untouched; the only test edit (test_review_checklist 6→7) is contract-disclosed conformance, shape preserved; the new surfaces are purely additive (None/legacy → no status line, current output byte-unchanged; the WARN rides the existing `warnings` array, no new `--json` key). No security surface (read-only measure · stdlib · reference text) → HARD-STOP invariant not in play.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the `grounded:` status line for the active task; a `task_not_grounded` WARN after a freeze; the freeze checklist's 7-item / ≤16-line budget.
Spec delta for the next loop: the grounding measure now has TWO honest signals (status surface + freeze checklist); ground-prose-align should make the book/GLOSSARY name the surface so prose ≡ enforcement (the DocsAccord pattern), and may reconsider the optional §3-template echo.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the strongest position for an additive engine surface is to make CURRENT output byte-unchanged — suppressing the None/legacy case means every existing task's status is identical, so zero existing output-tests need conforming and the live dogfood `check` count is unmoved (evidence: status silent for legacy tasks; full suite 780 OK with no status/check output-test edits; dogfood check stayed 264/0)
- [ADD · folded] a measure-not-block surface has an established SHAPE worth copying verbatim — goal-ready's "human-readable status line + never-red WARN riding the existing warnings array, no new --json key" mirrored exactly avoided the json_surface_unsanctioned_key landmine and the design churn (evidence: test_no_new_json_key_on_check green; the WARN rides `warnings` like goal_not_auto_ready)
- [TDD · folded] a prose checklist guarded by an exact COUNT + a line BUDGET (test_review_checklist: ==6 items, ≤16 lines) makes "gains one line" a precise, self-checking change — the new bullet had to be ONE physical line and the count test had to move 6→7 in lockstep (evidence: 16 ≤ 16 non-blank held; test_review_checklist conformed 6→7, shape preserved)
- [ADD · folded] retrofitting a §0 GROUND map onto a grandfathered task at build dogfoods the new surface honestly (records the grounding that informed §3) WITHOUT claiming the task flowed through the ground phase — the "zero lived runs starting at ground" ceiling still stands for the next milestone (evidence: ground-bundle-wiring shows `grounded ✓` live yet started at `specify`, not `ground`)
