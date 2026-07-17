# TASK: Define + check an auto-ready goal (machine-checkable acceptance criteria)

slug: goal-auto-ready-gate · created: 2026-06-10 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered (risk: high): method-defining — this DEFINES the auto-ready-goal concept + its check, the trust-layer that earns autonomy. A human owns the verify gate; the engine refuses an unguarded high-risk completion (unguarded_high_risk_auto). -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an "auto-ready goal" — a milestone goal whose every exit criterion CITES a verifier
`(verify: <test|command|metric>)`, so the engine can self-verify the result against the goal
without human judgement. The engine CLASSIFIES the active milestone's goal (auto-ready / not),
WARNs when not, surfaces it in `status`, and names the term across GLOSSARY + book + skill.
Autonomy is EARNED by goal-clarity — but the freeze gate + autonomy behavior stay UNCHANGED
this milestone (the gate-relaxation is the deferred spine decision).
Framings weighed: verifier-citation (chosen) · shape-lint (observable + no vague words) · task-test mapping
<!-- verifier-citation: each exit criterion must end-cite HOW it is checked — the same discipline as
     the §7 delta `(evidence: …)` convention; the engine lints for a non-empty `(verify: …)`.
     shape-lint (rejected): require an artifact token + ban vague words — lexical, no citation discipline.
     task-test mapping (rejected): resolve each criterion to a covering task's §4 tests — strongest but
     couples to decomposition + is heavier; revisit if citation-theater proves too weak. -->
Must:
<must>
  - the engine classifies a milestone goal AUTO-READY iff its `## Exit criteria` has total >= 1 AND every criterion line carries a non-empty `(verify: <citation>)`
  - a goal with NO exit criteria, or with ANY bare (uncited) criterion, reads NOT-auto-ready
  - `add.py check` emits a WARN (NEVER red) for the ACTIVE milestone when it HAS exit criteria but not all cite a verifier (total >= 1 AND cited < total), naming the cited/total tally — a zero-criteria milestone is CLASSIFIED not-auto-ready but is NOT warned (writing criteria is milestone-shaping's nudge, separable from citing them)
  - the WARN is LIVE-ONLY — a closed/archived/non-active milestone is NEVER flagged (no retro-redding predecessors)
  - `add.py status` surfaces the active milestone's auto-ready status (auto-ready ✓ / NOT auto-ready cited/total)
  - GLOSSARY + the book + the skill NAME "auto-ready goal" + the goal→autonomy link (prose ≡ enforcement), synced across the canonical · dogfood · bundled trees
</must>
Reject:
<reject>
  - a milestone exit criterion with no `(verify: …)` citation -> that criterion is uncited -> the goal reads NOT-auto-ready, SURFACED as a WARN (measurement, never a hard die — the loop is not blocked) -> "goal_not_auto_ready"
</reject>
After:
<after>
  - the active milestone's goal is observably classified auto-ready / not by an engine-computed rule (not a human checkbox)
  - the human sees the goal-clarity gap (which criteria are uncited) every session
  - the freeze gate, the per-task autonomy contract, and `milestone_goal_unmet` (the checkbox tally) are UNCHANGED
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] Verifier-citation RAISES THE FLOOR but cannot PROVE the citation is real — a human can write `(verify: it works)` and pass the lint (citation-theater). Lowest confidence because if you expected the engine to RESOLVE/RUN the cited verifier (a test that exists, a command that passes), this under-delivers. If wrong: the bar becomes a stronger check (resolve a test name in the suite / shell a command) — a materially bigger build. (Chosen the slot-forcing lint per the irreducible-floor rule: the engine raises the floor; the human still owns whether the citation is honest — autonomy is EARNED, not mechanically proven.)
  - [ ] [contract] Surface-only (WARN + status), NOT red and NOT an autonomy/gate change — per "clarify with human, your recommendation." If wrong (you want teeth now): escalate the WARN to a red `check` failure, or wire not-auto-ready → lowered autonomy (but that edges into the deferred gate-relaxation).
  - [ ] [contract] Scope = the MILESTONE goal (its `## Exit criteria` section), per the living doc — not the per-task §1/§4 or the project goal. If wrong: extend the classifier to those surfaces.
  - [ ] [contract] LIVE-ONLY (active milestone): closed/archived milestones predate the citation convention and must never be retro-flagged (the verified-marker / never-retro-red convention). If wrong: widen to all active+open milestones.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: every criterion cited -> auto-ready
  Given the active milestone's every exit criterion ends with `(verify: <citation>)`
  When I run `check` (and `status`)
  Then the goal reads AUTO-READY
  And no `goal_not_auto_ready` warning is emitted

Scenario: one bare criterion -> NOT auto-ready (surfaced, not blocked)
  Given the active milestone has one exit criterion lacking `(verify: …)`
  When I run `check`
  Then a `goal_not_auto_ready` WARNING names the active milestone with its cited/total tally
  And `check` does NOT go red (exit unaffected — measurement, not a gate)

Scenario: no exit criteria -> NOT auto-ready, but NOT warned (shaping's concern)
  Given the active milestone has an empty `## Exit criteria` section
  When I run `check`
  Then the goal reads NOT auto-ready (total 0)
  And no `goal_not_auto_ready` warning is emitted (the WARN needs >= 1 criterion to nudge)

Scenario: a closed / non-active milestone is never flagged   # LIVE-ONLY
  Given a non-active milestone whose exit criteria are bare
  When I run `check`
  Then NO `goal_not_auto_ready` warning is emitted for it
  And only the ACTIVE milestone's readiness is surfaced

Scenario: status surfaces the auto-ready status
  Given an active milestone
  When I run `status`
  Then the output names the active milestone's auto-ready status (cited/total)

Scenario: the term is named across the docs (prose ≡ enforcement)
  Given GLOSSARY + the book + the skill
  When I read each named surface
  Then each names "auto-ready goal" and the goal→autonomy link, synced ×3 trees
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_exit_criteria_cited(root, mslug) -> (cited, total)
  # tally over MILESTONE.md `## Exit criteria`: total = `- [ ]|[x]` lines; cited = those
  # carrying a non-empty `(verify: <citation>)`. Read-only, PURE; missing/sectionless -> (0, 0).

_goal_auto_ready(root, mslug) -> bool
  # total >= 1 AND cited == total. PURE.

citation grammar (additive to the exit-criteria line):
  - [ ] <observable criterion> (verify: <test name | `command` | metric>)
  cited := the criterion line contains `(verify: <non-empty>)`   (non-empty avoids the
           known mid-text substring trap — an empty `(verify:)` does NOT count)

add.py check
  -> WARN (NEVER red) "goal_not_auto_ready: milestone '<active>' goal not auto-ready
     (<cited>/<total> exit criteria cite a verifier) — add (verify: <test|command|metric>) …"
     for the ACTIVE milestone ONLY, fired IFF total >= 1 AND cited < total
     (a zero-criteria milestone is silent — that gap is milestone-shaping's, not this
      nudge's; closed/non-active milestones are never flagged — live-only).

add.py status
  -> a line surfacing the active milestone's readiness, e.g.
     `goal-ready: auto-ready ✓`  |  `goal-ready: NOT auto-ready (2/3 criteria cite a verifier)`

docs (prose ≡ enforcement; the named surfaces — every one, not a sample — the v23 DocsAccord lesson):
  - .add/GLOSSARY.md (survivor) + GLOSSARY.md.tmpl (×3 template trees): DEFINE "auto-ready goal"
  - book appendix-c-glossary.md (×3 doc trees: add-method · .add · _bundled): the glossary entry
  - book 11-governance.md (×3): the goal→autonomy link (goal-clarity earns autonomy)
  - skill run.md: name "auto-ready goal" in the loop flow

Schema (files touched): add.py (+2 read-paths, check WARN, status line) ×3 engine trees;
  the docs surfaces above; engine_pin re-pinned ×3.
NO change to: the freeze gate, the per-task autonomy contract, or `milestone_goal_unmet`
  (the human checkbox tally stays — auto-readiness is an ADDITIVE classification beside it).
```

Status: FROZEN @ v1

Least-sure flag surfaced at freeze: [spec] verifier-citation forces a citation SLOT but the
engine cannot prove the citation is REAL (`(verify: it works)` passes) — citation-theater; the
irreducible-floor rule accepts this (raise the floor, human still owns honesty), but if you
wanted the engine to RESOLVE/RUN the verifier, this under-delivers — highest cost (a much bigger
build). Secondary: [contract] surface-only WARN, no teeth/gate-change this milestone (your call);
[contract] milestone-level + active-only scope.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 95% of the new read-paths (`_exit_criteria_cited`, `_goal_auto_ready`) + the check WARN + status line
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_all_cited_is_auto_ready: arrange every criterion cited / act `_goal_auto_ready` + `check` / assert auto-ready + NO warn
  - test_one_bare_criterion_not_auto_ready: arrange one bare criterion / act `check` / assert `goal_not_auto_ready` WARN (cited/total) + assert check NOT red
  - test_no_criteria_not_auto_ready: arrange empty exit criteria / act `_goal_auto_ready` / assert False (total 0)
  - test_zero_criteria_does_not_warn: arrange empty exit criteria / act `check` / assert classified not-ready BUT no `goal_not_auto_ready` WARN (the firing-condition boundary: total >= 1 AND cited < total)
  - test_check_warns_active_only: arrange active milestone not-ready + a non-active milestone bare / act `check` / assert WARN names ONLY the active one
  - test_status_surfaces_auto_ready: arrange active milestone / act `status` / assert output names auto-ready status (cited/total)
  - test_empty_verify_paren_does_not_count: arrange a criterion ending `(verify:)` (empty) / assert it is NOT cited (substring-trap guard)
  - test_goal_auto_ready_helper: unit — `_goal_auto_ready` over all-cited (True) · one-bare (False) · none (False)
  - test_docs_name_auto_ready_goal: assert EVERY named surface contains "auto-ready goal" — .add/GLOSSARY.md · GLOSSARY.md.tmpl ×3 · appendix-c-glossary.md ×3 · 11-governance.md ×3 (the goal→autonomy link) · skill run.md — and the ×3 book/template twins stay byte-synced (the v23 DocsAccord "pin every surface" lesson)
</test_plan>

Tests live in: `add-method/tooling/test_goal_auto_ready_gate.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the auto-ready classifier is ADDITIVE + read-only — it NEVER blocks the loop (WARN, never red) and NEVER touches the freeze gate / autonomy / `milestone_goal_unmet`. Live-only: the active milestone, never closed predecessors. Apply the v23 DocsAccord lesson — pin EVERY doc surface the contract names, not just one.
Code lives in: `add-method/tooling/add.py` (+ ×3 engine sync) · GLOSSARY.md + book + skill
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — new suite `test_goal_auto_ready_gate` 13/13; full suite 747 OK (was 734 + 13 new − 0)
- [x] coverage did not decrease — purely ADDITIVE: 2 read-paths + 1 regex + a WARN branch + a status line; nothing removed
- [x] no test or contract was altered during build — §1–§3 FROZEN @ v1 untouched since freeze; the lone appendix fix changed a DOC (capitalized header → kept, lowercase literal added to the body), never a test. VERIFY-STAGE GAP-CLOSE (close-gap-before-gate): the adversarial pass found the live-only WARN keyed only on the active-pointer + dict-membership, so it fired on a done-but-not-yet-archived active milestone (status=done stays the active pointer until `archive`) — a Must #4 violation. Closed by ADDING `test_done_active_milestone_not_flagged` (red→green) + a `status != "done"` guard; no existing test weakened, §1–§3 unchanged, the fix only makes the code match the frozen contract.
- [x] concurrency / timing — N/A: `_exit_criteria_cited`/`_goal_auto_ready` are PURE read-only; single read of MILESTONE.md, no shared state, no concurrency path
- [x] no exposed secrets / injection / unexpected deps — stdlib only (`re`, `pathlib`); the WARN f-string interpolates only the milestone slug + two ints into stdout — no shell/eval/sink; reads text, writes nothing
- [x] layering & dependencies follow CONVENTIONS.md — mirrors `_exit_criteria` + `_project_autonomy` (pure read-paths beside the existing ones); additive to `cmd_check`/`cmd_status`; never touches the freeze gate, the autonomy contract, or `milestone_goal_unmet`
- [x] a person reviewed and approved the change   ← HUMAN reviewed the evidence + the verify-stage gap-close and recorded PASS at the gate (conservative + risk: high; auto-PASS disabled)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_VERIFY_CITE_RE` → used by `_exit_criteria_cited`; `_exit_criteria_cited` → called by `_goal_auto_ready` + `cmd_check` (WARN) + `cmd_status` (goal-ready line); `_goal_auto_ready` → `cmd_status` + the suite. The WARN guard `_active_ms in milestones and milestones[_active_ms].get("status") != "done"` makes it fire only for the OPEN active milestone (archived ones are already out of the dict; done-but-unarchived ones are excluded by status). Confirmed live: `status` prints `goal-ready: auto-ready ✓ (3/3 …)` and `check` emits/clears `goal_not_auto_ready` on the dogfood milestone; the done-exclusion is pinned by `test_done_active_milestone_not_flagged`.
- [x] DEAD-CODE (code) — no new unused/orphaned symbol; all 3 new symbols referenced (above), all exercised by green tests.
- [x] SEMANTIC (prose / non-code) — read in full: the "auto-ready goal" entry in `.add/GLOSSARY.md` + `GLOSSARY.md.tmpl` ×3, `appendix-c-glossary.md` ×3, the goal→autonomy paragraph in `11-governance.md` ×3, and the skill `run.md` ×3 — each names the term + the goal→autonomy link; all twins byte-synced (DocsAccordTest + tree-parity green).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-10

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-`goal_not_auto_ready`-WARN rate across milestones (a proxy for goal-clarity discipline); any milestone reaching `milestone done` while `status` still reads `goal-ready: NOT auto-ready` (a citation-discipline gap the human waved through).
Spec delta for the next loop: the deferred SPINE decision — wire not-auto-ready → lowered autonomy and/or escalate the WARN to teeth (a red `check`), its own later milestone; plus the stronger citation bar (RESOLVE a cited test name in the suite / SHELL a cited command) to retire citation-theater.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] a "live-only" guard must key on the milestone's terminal STATUS, not just the active-pointer + dict-membership — the build missed the done-but-not-yet-archived window (status=done stays the active pointer until `archive` clears it), so the WARN briefly fired on a closed milestone; the verify adversarial pass caught the Must #4 violation and closed it test-first (evidence: `test_done_active_milestone_not_flagged` RED before the `status != "done"` guard → full suite 747 OK after).
- [ADD · folded] verifier-citation RAISES the goal-clarity floor but cannot PROVE a citation is honest — `(verify: it works)` passes the lint (citation-theater); the irreducible-floor rule accepts this, and the stronger bar (resolve a cited test in the suite / shell a cited command) is the deferred upgrade (evidence: §3 freeze flag; `test_empty_verify_paren_does_not_count` guards only emptiness, never honesty).
- [ADD · folded] `_exit_criteria_cited` guards `exists()` but not `read_text()` against OSError, diverging from the sibling `_project_autonomy_token` which DOES (the design-for-failure rule); left as a recorded ceiling — it mirrors the `_exit_criteria` convention, so hardening one read-path without the other would split the convention (evidence: advisor non-blocking note; both classifier read-paths currently unguarded).
