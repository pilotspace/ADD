# TASK: WAVE.md — durable wave ledger for parallel streams

slug: wave-ledger · created: 2026-06-07 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- risk: high — this task amends the method's own orchestration rubric (streams.md);
     autonomy lowered to conservative: the verify gate stops for the human. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: WAVE.md — transient, evidence-bearing wave-ledger convention for parallel streams
Framings weighed: evidence-bearing ledger convention, no engine change (chosen) · engine-guarded ledger via `add.py check` (rejected: breaks streams.md's shipped "changes no add.py code" promise — change-request territory) · template-only appendix pointer (rejected: leaves the EXECUTE gap that recurred in v12-1)
Must:
<must>
  - streams.md (canonical `add-method/skill/add/streams.md`, synced copy `.claude/skills/add/streams.md`) gains a `## Wave ledger` section defining `.add/milestones/<m>/WAVE.md`: orchestrator-owned, ONE live wave per milestone, the wave's resume point — the analog of `state.json` for a wave
  - the ledger template homes the semantic mapping `streams.md:75` mandates but never houses: task ↔ lease (worker id · spawned · timeout) ↔ fork-base ↔ autonomy ↔ merge-order, plus a `Mid-wave decisions` section
  - evidence cells, not ticks: the fork-base cell holds the PASTED output of `git -C <worktree> rev-parse HEAD`, equal to the recorded wave base — a roster row is fillable only by EXECUTING the pre-spawn check (closes the v12-1 "words-exist ≠ method-works" recurrence)
  - worker visibility rule: workers never read WAVE.md; the orchestrator folds relevant mid-wave decisions into each worker's PROMPT.md at spawn/respawn
  - lifecycle: created at wave open → consumed by the serial integration Verify → evidence digest (wave base · roster→fork-base evidence · merge order · integration-Verify outcome) absorbed into MILESTONE.md as an append-only `## Wave log` block — doubling as the integration-Verify record, today homeless → only then deleted
  - WAVE.md joins the merge-back exclusion clause (`state.json` · `MILESTONE.md` · `WAVE.md` — never merged back from a worktree)
  - resume rule: on session start, a live WAVE.md is the orchestrator's wave resume point — re-orient from the file, never from conversational memory
  - guard tests in `add-method/tooling/` pin every clause above words-exist style (the established `test_streams.py` pattern); skill-tree parity stays green
</must>
Reject:
<reject>
  - streams.md without the wave-ledger section or its template -> "wave_ledger_clause_missing"  (guard test fails)
  - a template whose fork-base cell permits a bare tick instead of pasted command output -> "wave_evidence_cell_optional"  (guard pins the paste-the-output rule)
  - WAVE.md absent from the merge-back exclusion clause -> "wave_merge_exclusion_missing"  (guard test fails)
  - convention refusals the section must document (prose rules; guards pin their existence): opening a second wave while one is live -> "wave_already_live" · spawning a worker whose roster row lacks base evidence -> "unverified_fork_base" · deleting WAVE.md before the digest is absorbed -> "digest_not_absorbed"
</reject>
After:
<after>
  - both streams.md trees document the convention (template · lifecycle · refusal rules · resume rule); the new guard suite ran red before build and green after; the next parallel wave has a named, evidence-bearing, resumable ledger — wave state no longer lives only in the orchestrator's chat context
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ words-exist guards are enforcement enough (no runtime check, by design) — lowest confidence because F1 deliberately keeps the engine untouched; if wrong: an undisciplined orchestrator can still skip the ledger — v12-1's risk class, narrowed by evidence-cells but not eliminated
  ⚠ the Wave log block's grammar stays prose-loose (no lint) — second-lowest because only its existence is pinned, not its shape; if wrong: digests drift across waves and lose comparability (cheap to tighten later with a deltas-lint-style guard)
  - [x] digest home = append-only `## Wave log` block in MILESTONE.md, doubling as the integration-Verify record — confirmed by Tin 2026-06-07 (resolved from former ⚠1)
  - [x] one live wave per milestone suffices (READY-QUEUE refills between waves; overlapping waves stay out of scope)
  - [x] book chapter 10 needs no edit — it explicitly defers the operational recipe to streams.md
  - [x] guards live in a new `add-method/tooling/test_wave_ledger.py` beside `test_streams.py` (either home satisfies parity)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: wave-ledger clause present
  Given the canonical add-method/skill/add/streams.md
  When the wave-ledger guard suite runs
  Then it finds the "Wave ledger" section defining .add/milestones/<m>/WAVE.md as the wave's resume point
  And every pre-existing streams.md safety clause still passes its guard (test_streams.py untouched, green)

Scenario: template homes the full semantic mapping
  Given the WAVE.md template inside the new section
  When the guard inspects it
  Then the roster names task · lease · fork-base · autonomy · spawned · timeout, and the file names base · Mid-wave decisions · Merge order
  And a missing element fails the guard ("wave_ledger_clause_missing")

Scenario: evidence cell requires pasted output
  Given the template's fork-base column
  When the guard runs
  Then the convention requires the pasted `git -C <wt> rev-parse HEAD` output equal to the recorded wave base
  And a bare tick is named refused ("wave_evidence_cell_optional")

Scenario: merge-back exclusion extended
  Given the "Merge is serial" clause
  When the guard runs
  Then WAVE.md is named alongside state.json and MILESTONE.md as never merged back from a worktree
  And dropping it fails the guard ("wave_merge_exclusion_missing")

Scenario: lifecycle and refusal rules documented
  Given the wave-ledger section
  When the guard runs
  Then open → consume (integration Verify) → digest into the MILESTONE.md `## Wave log` block (doubling as the integration-Verify record) → delete is stated in that order
  And the three refusals are named: "wave_already_live" · "unverified_fork_base" · "digest_not_absorbed"

Scenario: worker visibility and resume rules stated
  Given the wave-ledger section
  When the guard runs
  Then "workers never read WAVE.md" (PROMPT-folded decisions) is stated
  And the session-resume rule (re-orient from the live ledger, never from memory) is stated

Scenario: skill-tree parity holds
  Given the canonical and installed skill trees
  When the existing parity guard runs
  Then .claude/skills/add/streams.md matches add-method/skill/add/streams.md
  And no other skill file drifted
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FILE add-method/skill/add/streams.md  +  synced .claude/skills/add/streams.md
  SECTION "## Wave ledger — the wave's resume point"
    defines : .add/milestones/<m>/WAVE.md  (orchestrator-owned · one live wave per milestone)
    template: wave · opened · status(live|merging) · base: <sha>
              roster row: task · lease(worker) · fork-base(pasted `git -C <wt> rev-parse HEAD` output) ·
                          autonomy · spawned · timeout
              sections : Mid-wave decisions · Merge order
    rules   : workers-never-read (PROMPT-folded) · merge-back exclusion += WAVE.md ·
              lifecycle open→consume→digest→delete, digest = append-only "## Wave log" block in
              MILESTONE.md (wave base · roster→fork-base evidence · merge order · integration-Verify
              outcome — doubling as the integration-Verify record) · resume-from-ledger on session start
    refusals: "wave_already_live" | "unverified_fork_base" | "digest_not_absorbed"
GUARDS add-method/tooling/test_wave_ledger.py   (words-exist pattern of test_streams.py)
  fail codes -> "wave_ledger_clause_missing" | "wave_evidence_cell_optional" | "wave_merge_exclusion_missing"
Schema: markdown only — NO add.py change, NO state.json field (streams.md's no-engine promise holds)
```

Status: FROZEN @ v1 — approved by Tin (2026-06-07; one-approval bundle gate, ⚠ flags presented lowest-confidence first)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every contracted clause has a pinning guard (clause coverage 100%); existing suites stay green
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_wave_ledger_section_present: arrange canonical streams.md / act read / assert "wave ledger" section + WAVE.md path + resume-point wording
  - test_template_homes_semantic_mapping: arrange section text / act inspect / assert task·lease·fork-base·autonomy·spawned·timeout·base·mid-wave decisions·merge order all named
  - test_evidence_cell_requires_pasted_output: arrange section text / act inspect / assert rev-parse paste rule + tick refusal named
  - test_merge_back_exclusion_names_wave: arrange "merge is serial" clause / act inspect / assert WAVE.md beside state.json·MILESTONE.md
  - test_lifecycle_and_refusals_documented: arrange section text / act inspect / assert open→consume→digest→delete order + "wave log" named as the digest home + the three refusal codes
  - test_worker_visibility_and_resume_rules: arrange section text / act inspect / assert never-read + PROMPT-folded + resume-from-ledger wording
  - test_existing_streams_guards_still_green: arrange / act run test_streams.py clauses / assert no pre-existing safety clause regressed
</test_plan>

Tests live in: `add-method/tooling/test_wave_ledger.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the new section is ADDITIVE — no existing streams.md safety clause may be reworded or removed (test_streams.py is the tripwire); canonical edits first, then sync the installed skill tree.
Code lives in: `add-method/skill/add/streams.md` (+ synced `.claude/skills/add/streams.md`)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full tooling suite 569 OK; 7/7 wave-ledger guards green (red-first 6F/1P, every failure an AssertionError on the missing section)
- [x] coverage did not decrease — suite grew 562→569 (+7 guards); no test removed or weakened
- [x] no test or contract was altered during build — post-freeze: zero edits to test_wave_ledger.py and §3; the one wording change ("folds"→"copies", forced by the ubiquitous-language guard) altered prose, not the contracted rule ("PROMPT-folded" realized as copy-into-PROMPT.md — disclosed, not silent)
- [x] concurrency / timing of the risky operation is safe — WAVE.md is single-writer by construction (orchestrator-only; workers never read NOR write it) → race-free; the contract's own merge-back exclusion keeps it out of worktree merges
- [x] no exposed secrets, injection openings, or unexpected dependencies — markdown + stdlib unittest only; no new packages
- [x] layering & dependencies follow CONVENTIONS.md — convention layer only, engine untouched (streams.md's no-engine promise holds); three trees byte-identical (tree+bundle parity guards green); one in-scope-ADDITIVE edit beyond §3's enumerated list: the Lease+timeout bullet now points at the ledger (disclosed)
- [x] a person reviewed and approved the change — Tin, at this gate (conservative; flags + disclosed deltas presented first)

Evidence altitude (honest limit): 569 green proves the convention is DOCUMENTED and
regression-guarded — not that it works in use; proof-of-function is the next dogfood
wave (§7 Watch). And `add.py status` does NOT surface a live WAVE.md (no engine change,
by design) — the resume-point promise still leans on the orchestrator looking in the
milestone dir. Standing ⚠ residues carried from the freeze: words-exist-only enforcement ·
Wave-log grammar prose-loose.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-07
Residue routed: status-blind-spot → new intake (wave-status-hint); words-exist-only enforcement + Wave-log grammar → open deltas, next fold.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the next parallel wave — was WAVE.md actually opened, evidence-filled, digested into a Wave log block, deleted?
Spec delta for the next loop: the next streams wave must dogfood the ledger end-to-end (open → evidence cells → mid-wave decisions → digest → delete); what it teaches feeds back here.

### Competency deltas
- [SDD · folded] reserved-term discipline reaches prose VERBS, not just nouns — "fold" used for PROMPT injection collided with the method's fold ritual; same-concept-same-name applies to actions too (evidence: test_slang_absent_extended_surface red on streams.md:92; reworded to "copy")
- [TDD · folded] a fenced example inside a guarded section can silently truncate a words-exist guard — `_section` cuts at "\n## ", so any template embedded in a guarded section must use ### headings or the guard scans a prefix while claiming the whole (evidence: WAVE.md template authored with ### for exactly this; the hazard rhymes with v16's inline-XML-placeholder lesson)
- [ADD · folded] `add.py status` does not surface a live WAVE.md — the wave resume-point still leans on the orchestrator looking in the milestone dir; a status hint is NEW engine scope for intake, precedent v12-1's cmd_status-hint (evidence: F1 framing deliberately excluded engine changes; residue disclosed at the verify gate)
