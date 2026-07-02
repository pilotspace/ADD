# TASK: Wire add.py search into scope.md + intake.md drafting steps

slug: phase-search-wiring · created: 2026-07-02 · stage: mvp
milestone: context-search
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `.claude/skills/add/scope.md` step 2 "Relate to the milestone map" (+ its 3 tracked mirrors: `add-method/skill/add/scope.md`, `add-method/src/add_method/_bundled/skill/add/scope.md`) · `.claude/skills/add/intake.md` `## Interview before you size` section (+ same 3 mirrors) · `add-method/tooling/test_skill_lean.py`'s `core`/`reference` pool baselines (rebaseline candidate — see Issues/Risks) · a 4th, gitignored, unread build-artifact copy exists at `add-method/build/lib/add_method/_bundled/skill/add/` — never hand-edited.
Context (working folder): `.add/tasks/search-index/TASK.md` §3 (frozen, real, already-shipped `add.py search` CLI grammar — the source of truth this task cites) · `.add/milestones/context-search/MILESTONE.md` (frozen Scope naming this task's exit criterion) · `.add/CONVENTIONS.md` (~line 85, the rebaseline-precedent rule) · `.add/personas/book-technical-writer.md`.
Honors (patterns / conventions): 3-tree byte-identical mirror convention (guarded by `test_tree_parity.py`/`test_bundle_parity.py`) · `test_skill_lean.py`'s POOLS byte-budget convention (core = SKILL.md+intake.md, reference = 14 guides incl. scope.md; `TREE_TARGET_BYTES` is DERIVED from pool baselines × 0.75, never a separate hand-summed literal) · pinned-needle tests (`test_ground_wiring.py`, `test_scope_loop.py`, `test_intake_interview.py`) that assert exact section headers/phrases survive byte-exact.
Anchors the contract cites: `.claude/skills/add/scope.md` step 2 · `.claude/skills/add/intake.md` `## Interview before you size` · `add-method/tooling/test_skill_lean.py` POOLS dict · `.add/tasks/search-index/TASK.md` §3 (the real CLI grammar cited).
Issues/Risks (→ feed §1): both target pools are within single-digit-to-teens bytes of their ceiling — `core` pool has 6 bytes headroom, `reference` pool has 15 — naming a real CLI command (`add.py search <keyword> [<keyword> ...]`) in either file costs far more than that (~61 B in scope.md, ~140 B in intake.md), making pure compression-to-fit essentially infeasible without shortening unrelated, already-tight, heavily-pinned prose elsewhere · this creates a genuine tension between the loaded persona's own rule ("never edit the lean-pool test to make room") and `.add/CONVENTIONS.md`'s own folded, repeatedly-used precedent ("a deliberate, contract-approved content addition that busts a lean-fence pool is absorbed by REBASELINING... not by token-golfing the new prose thinner") — flagged for explicit human confirmation at freeze, not silently resolved either way · the milestone's frozen Scope text says "intake.md's Diverge step," but intake.md has no heading literally named "Diverge" — resolved as `## Interview before you size` (the only pre-classification step, sitting before `## The four buckets`), an interpretive fill flagged at freeze, same shape as `search-index`'s own goal/rationale interpretive gap.
Related intent: `.add/milestones/context-search/MILESTONE.md` goal + its Shared/risky-contracts line (this task depends on `search-index`'s frozen invocation grammar, already shipped) · the milestone's own literal exit criterion (`grep -cl "add.py search" .claude/skills/add/scope.md .claude/skills/add/intake.md`).
Ground SHA: `c152945`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Wire `add.py search <keyword> [<keyword> ...]` into `scope.md`'s "Relate to the milestone map" step and `intake.md`'s pre-classification step, so drafting new scope runs a keyword search first, before a manual re-read of every MILESTONE.md.
Framings weighed: minimal in-place sentence insertion at each step's existing anchor text, rebaseline the 2 busted lean-pool budgets (chosen — matches CONVENTIONS.md's own repeated precedent for a deliberate, contract-approved addition; the only way to fit real command-naming prose given 6-15 byte headroom) · compress unrelated existing prose elsewhere in the same pools to force-fit under the OLD budget (rejected at design time, pending human confirmation — conflicts with the loaded persona's own rule, and risks degrading other already-tight, heavily-pinned guides just to avoid a budget bump) · a shorter/vaguer reference to "search the corpus" instead of the real CLI grammar (rejected — R:invented_command_shape; the milestone's whole point is mechanizing the ACTUAL command, not gesturing at one).
Must:
<must>
  - M1: `scope.md` step 2 ("Relate to the milestone map") names `add.py search <keyword> [<keyword> ...]` as the FIRST action, before "read every existing goal" — exact insertion: replace "Read every existing goal —" with "Run `add.py search <keyword> [<keyword> ...]` first — then read every existing goal —".
  - M2: `intake.md`'s `## Interview before you size` section gains a new opening sentence naming the same command as the first action, before "When the request arrives...": "Run `add.py search <keyword> [<keyword> ...]` first — it surfaces overlapping/prior work in one command instead of a full manual re-read."
  - M3: the wired command grammar cites the REAL, frozen `search-index` §3 shape (`add.py search <keyword> [<keyword> ...] [--json]`) verbatim — never an invented shape.
  - M4: the edit propagates byte-identically to all 3 git-tracked mirrors of each file (`add-method/skill/add/`, `.claude/skills/add/`, `add-method/src/add_method/_bundled/skill/add/`); the 4th, gitignored `add-method/build/lib/...` copy is never hand-edited.
  - M5: every pre-existing pinned needle survives byte-exact — `scope.md`'s header + its two regex checks (`test_scope_loop.py`, `test_ground_wiring.py`); `intake.md`'s header + "explore it WITH the user" / "2–3 sized options" / "Only then emit" / "never guess a bucket", still positioned before `## The four buckets` (`test_intake_interview.py`).
  - M6: because the addition busts `test_skill_lean.py`'s `core` pool (SKILL.md+intake.md) and `reference` pool (14 guides incl. scope.md) byte ceilings, rebaseline BOTH pool literals using the pool's own formula (`new_baseline = old_baseline + ceil(new_surface_bytes / unchanged_ratio)`), never by shrinking unrelated prose to force-fit — per CONVENTIONS.md's folded precedent, PENDING EXPLICIT HUMAN CONFIRMATION at freeze (this is the bundle's top least-sure flag).
  - M7: §3 pre-records the exact target numbers build must land on, so build has a concrete target, not an ad hoc re-derivation.
</must>
Reject:
<reject>
  - inventing a different command shape than search-index's real frozen grammar -> "invented_command_shape"
  - editing only one of scope.md/intake.md, or only one mirror tree, leaving others stale -> "partial_wiring_left_stale"
  - silently dropping/rewording any M5 pinned needle or section header -> "pinned_needle_broken"
  - absorbing the new bytes by compacting unrelated existing prose to dodge a rebaseline (token-golfing) -> "budget_dodge_via_compaction"
  - landing the prose while leaving test_skill_lean.py's pool baseline(s) stale/red -> "stale_lean_budget_left_red"
</reject>
After:
<after>
  - `scope.md` + `intake.md` both name `add.py search <keyword...>` as the first action in their respective drafting steps, mechanizing a step the method already requires but today means a full manual re-read.
  - The milestone's own literal exit criterion (`grep -cl "add.py search" .claude/skills/add/scope.md .claude/skills/add/intake.md`) passes.
  - `test_skill_lean.py` is green at its new, deliberately rebaselined targets — no unrelated prose was shortened to dodge the budget.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The compress-vs-rebaseline choice (M6) overrides the loaded persona's own literal rule ("never edit the lean-pool test to make room") in favor of CONVENTIONS.md's documented, repeatedly-used precedent — lowest confidence because it's a genuine policy tension, not a formalization of settled prior art specific to THIS exact case; if wrong (human wants compression instead): the fix is a change request back to Specify with a much terser wording target, likely requiring cuts elsewhere in already-tight guides.
  - [ ] confirm "## Interview before you size" is the intended `intake.md` landing spot for the milestone's "Diverge step" reference — the milestone's own wording doesn't match any literal heading in the file.
  - [ ] confirm the exact inserted wording in both files reads well editorially — content is the design agent's draft, not yet human-reviewed prose.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: scope.md names the search command first in step 2   # M1
  Given the current .claude/skills/add/scope.md
  When step 2 "Relate to the milestone map" is read
  Then it contains "Run `add.py search <keyword> [<keyword> ...]` first" BEFORE "then read every existing goal"

Scenario: intake.md names the search command first in its interview step   # M2
  Given the current .claude/skills/add/intake.md
  When "## Interview before you size" is read
  Then its first sentence names the command, BEFORE "When the request arrives as a question"

Scenario: milestone's own exit-criterion grep passes   # M1, M2
  Given both edited files
  When `grep -cl "add.py search" .claude/skills/add/scope.md .claude/skills/add/intake.md` runs
  Then both filenames are listed, each count >= 1

Scenario: wired grammar matches the real shipped command   # M3, R:invented_command_shape
  Given search-index's frozen §3: `add.py search <keyword> [<keyword> ...] [--json]`
  When the new text is compared
  Then it cites that exact shape — no --query, no `add.py find`, no single-phrase form

Scenario: all 3 mirror trees stay byte-identical   # M4, R:partial_wiring_left_stale
  Given the 3 tracked copies of each file
  When the edit lands
  Then `python3 -m unittest test_tree_parity test_bundle_parity` passes
  And add-method/build/lib/.../{scope,intake}.md (gitignored) is left untouched

Scenario: pre-existing pinned needles survive   # M5, R:pinned_needle_broken
  Given the frozen needles named in M5
  When the edit lands
  Then `python3 -m unittest test_ground_wiring test_scope_loop test_intake_interview` stay green

Scenario: lean-fence budget is rebaselined, not dodged   # M6, R:budget_dodge_via_compaction, R:stale_lean_budget_left_red
  Given +61 B lands in the reference pool, +140 B in the core pool
  When test_skill_lean.py's POOLS baselines are rebaselined per the pool's own formula, ratios unchanged
  Then `python3 -m unittest test_skill_lean` passes at the new targets
  And no unrelated sentence elsewhere was shortened to force-fit the OLD budget

Scenario: contract's pre-recorded numbers match what build lands on   # M7
  Given §3 states the exact target byte numbers
  When build runs the rebaseline
  Then the landed numbers match, or any drift is disclosed with why

Scenario: stale build-artifact copy is never mistaken for a real target   # edge case
  Given add-method/build/lib/.../{scope,intake}.md exists as a leftover local build artifact
  When build audits "add.py search" landed everywhere required
  Then that gitignored path is excluded from the audit, never hand-edited

Scenario: whole-tree headline guardrail still holds after rebaseline   # edge case
  Given TREE_TARGET_BYTES is DERIVED (sum of pool baselines x 0.75), not a hand-summed literal
  When core+reference baselines rebaseline per M6
  Then the whole-tree byte-budget test passes automatically, no separate literal to touch
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE CONTRACT — phase-search-wiring @ v1   (no code/engine change; ENGINE_MD5 untouched)

FILE 1 — scope.md (+61 B, all 3 trees):
  anchor (before): "2. **Relate to the milestone map.** Read every existing goal — `.add/milestones/*/MILESTONE.md` and `.add/archive/*` — and name THIS request's relationship: *extends* X · *depends-on* Y · *overlaps* Z. Record in the `rationale` line."
  replace with:    "2. **Relate to the milestone map.** Run `add.py search <keyword> [<keyword> ...]` first — then read every existing goal — `.add/milestones/*/MILESTONE.md` and `.add/archive/*` — and name THIS request's relationship: *extends* X · *depends-on* Y · *overlaps* Z. Record in the `rationale` line."

FILE 2 — intake.md (+140 B, all 3 trees):
  anchor (before): "## Interview before you size\n\nWhen the request arrives as a question, or its intent is not sharp enough to place in one bucket:\nexplore it WITH the user before classifying. ..."
  replace with:    "## Interview before you size\n\nRun `add.py search <keyword> [<keyword> ...]` first — it surfaces overlapping/prior work in one\ncommand instead of a full manual re-read. When the request arrives as a question, or its intent is\nnot sharp enough to place in one bucket: explore it WITH the user before classifying. ..."

FILE 3 — add-method/tooling/test_skill_lean.py (pool rebaseline, per M6, human-confirmed at freeze):
  core:      {"baseline": 20506  ->  20666}   (ratio 0.88 unchanged; target 18045 -> 18186)
  reference: {"baseline": 75224  ->  75314}   (ratio 0.68 unchanged; target 51152 -> 51213)
  each preceded by a narrated-history comment in the file's existing style, citing this task slug + CONVENTIONS.md precedent.

Propagation: canonical add-method/skill/add/{scope,intake}.md -> cp to .claude/skills/add/ and add-method/src/add_method/_bundled/skill/add/. Never touch add-method/build/lib/... (gitignored, unread by any test).

Schema: no data/API schema — this is a documentation-only contract (2 prose files + 1 test-pool baseline rebaseline).
```

Glossary deltas: none (no new domain term; search-index already declared "search corpus"/"indexed line(s)").
Status: FROZEN @ v1 — approved by Tin Dang (both flags confirmed: rebaseline over compression; "Interview before you size" confirmed as the Diverge-step landing spot)
Least-sure flag surfaced at freeze: [spec/contract] M6's rebaseline-vs-compress choice overrides the loaded persona's own literal rule ("never edit the lean-pool test to make room") in favor of CONVENTIONS.md's documented, repeatedly-used precedent — lowest confidence because it's a genuine policy tension, not a formalization of settled prior art specific to this exact case; if wrong, the fix is a change request back to Specify with a much terser wording target, likely requiring cuts elsewhere in already-tight guides. Second flag: [spec] "Interview before you size" as the intake.md landing spot for the milestone's "Diverge step" wording — the milestone's own text doesn't match any literal heading in the file; both flags confirmed acceptable by Tin Dang at freeze.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/scope.md` · `add-method/skill/add/intake.md` · `.claude/skills/add/scope.md` · `.claude/skills/add/intake.md` · `add-method/src/add_method/_bundled/skill/add/scope.md` · `add-method/src/add_method/_bundled/skill/add/intake.md` · `add-method/tooling/test_skill_lean.py`
Strategy (ordered batches): 1. edit canonical `add-method/skill/add/scope.md` + `intake.md` with the exact anchor-replace text from §3; 2. copy byte-identically into `.claude/skills/add/` and `add-method/src/add_method/_bundled/skill/add/` (diff/md5-confirmed, not by eye) — never touch the gitignored `add-method/build/lib/...` copy; 3. rebaseline `test_skill_lean.py`'s `core`/`reference` POOLS baselines per the pre-recorded §3 numbers, each preceded by a narrated-history comment citing this task slug + CONVENTIONS.md's rebaseline-precedent line; 4. run `test_skill_lean test_ground_wiring test_scope_loop test_intake_interview test_tree_parity test_bundle_parity`; 5. run the milestone's own exit-criterion grep; 6. `git diff --stat` confirms only the 7 declared files changed.

Persona (optional): `.add/personas/book-technical-writer.md` (prose/skill-guide work — the same persona search-index's Ground context cites for wiring the doc side of the milestone).
Known-problem fixes: bare `` imbalance corrupting the freeze-flag parser (search-index's own retro lesson) → neither insertion introduces an HTML comment, plain prose only · lean-pool budget drift left red → rebaseline lands in the SAME build batch as the prose edit, never a follow-up · silently editing the wrong mirror first → canonical `add-method/skill/add/` is always the edit-of-record, copied outward, never edited in place in `.claude/skills/add/`.
Strategy actually used: as planned — verified against the evidence, not trusted from disclosure: the canonical `add-method/skill/add/{scope,intake}.md` carry the edit-of-record (git diff shows only the single frozen anchor-replace insertion in each, nothing else touched), both mirrors are byte-identical by md5 (confirmed independently, not by eye), the `test_skill_lean.py` rebaseline lands in the same build batch with a narrated-history comment matching the file's own established style and citing this task slug + the exact CONVENTIONS.md precedent line, the declared 6-suite (58 tests) is green, the milestone's own exit-criterion grep passes, and `git diff --stat` confirms exactly the 7 declared files changed (no more, no less) — no deviation from the planned batch order.
Safety rule (feature-specific): none — documentation-only edit, no transactional/atomicity concern.
Code lives in: `./src/` (not applicable — this task ships no `./src/` code; prose lands in the Scope paths above)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (declared suite `test_skill_lean test_ground_wiring test_scope_loop test_intake_interview test_tree_parity test_bundle_parity`: 58/0, independently re-run by add-verify; full `add-method/tooling` regression: 2710 tests, 10 pre-existing/unrelated failures — see Live-verify note below, none touch this task's declared §5 Scope)
- [x] coverage did not decrease (docs-only edit; no test weakened, none removed)
- [x] no test or contract was altered during build (§3 CONTRACT text byte-matches the shipped prose exactly; `test_skill_lean.py`'s only change is the pre-authorized POOLS rebaseline, not a weakened assertion)
- [x] the green was EARNED — see Refute-read verdict below
- [x] concurrency / timing of the risky operation is safe — N/A, docs-only edit, no runtime code path touched (confirmed via `git diff --stat`: only `.md` prose + one test-pool literal changed)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose-only insertion, confirmed no shell-exec/eval/network primitive introduced in either file (grep-clean)
- [x] layering & dependencies follow CONVENTIONS.md — the rebaseline follows CONVENTIONS.md's own folded precedent verbatim (line 85, foundation-version 51: "a deliberate, contract-approved content addition that busts a lean-fence pool is absorbed by REBASELINING the baseline by surface÷ratio... not by token-golfing the new prose thinner")
- [x] a person reviewed and approved the change (contract freeze — Tin Dang, 2026-07-01, both flags confirmed)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `scope.md` step 2 and `intake.md`'s "Interview before you size" both name `add.py search <keyword> [<keyword> ...]` as the first action, verbatim per §3's anchor-replace text — confirmed by `grep -n "add.py search" add-method/skill/add/scope.md add-method/skill/add/intake.md` matching M1/M2 exactly, byte-diffed against the frozen contract text
- [x] the edit is byte-identical across all 3 tracked mirrors of each file, and the milestone's own exit-criterion grep (`grep -cl "add.py search" .claude/skills/add/scope.md .claude/skills/add/intake.md`) returns both files — confirmed by md5 comparison across trees + the literal grep command
- [x] `test_skill_lean.py`'s core/reference pool baselines land on the exact pre-recorded targets (core 18186, reference 51213) with zero unrelated prose shortened to force-fit — confirmed by the build agent's disclosed byte-delta match (scope.md +61B, intake.md +140B, exact match to §3's pre-recorded numbers) and a clean `git diff --stat` showing only the 7 declared Scope files changed

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — N/A, no new code symbol introduced (docs-only task)
- [ ] DEAD-CODE (code) — N/A, no code
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read all 3 tracked mirrors of `scope.md` (step 2 in context — "Position the goal" numbered list) and `intake.md` (full "## Interview before you size" section plus its neighbors "## The four buckets" and the milestone-scope "Brainstorm" section) end to end, not just the diff hunks; confirmed the inserted sentence reads naturally in place, the pre-existing pinned needles (`explore it WITH the user`, `2–3 sized options`, `Only then emit`, `never guess a bucket`) sit undisturbed after the new opening clause, and the section ordering (`## Interview before you size` before `## The four buckets`) is unchanged — also read `test_skill_lean.py`'s full POOLS list end to end to confirm the new narrated-history comment matches the file's own established style (same "pool X→Y @ task-slug" phrasing, same rebaseline-formula citation as every prior entry) and that no other pool's baseline was silently touched

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct `grep -n`/byte-diff against the CURRENT tree, not the Ground SHA: `scope.md` step 2 anchor text (line 23, all 3 trees, md5 `6010fd34c5cfd9ec3aa6e8ca81b75ef0`), `intake.md`'s `## Interview before you size` anchor (line 7-11, all 3 trees, md5 `4ec88ed925646726abadb7dcdb2ff401`), `test_skill_lean.py`'s POOLS `core`/`reference` dicts (lines re-resolved live, baselines 20666/75314 confirmed present) — all match §3's frozen text verbatim, no drift since Ground SHA `c152945`
- [x] anchor that moved/renamed since Ground SHA: none in this task's own 7-file scope. NOTE (disclosed, not silent): `add.py check` transiently flagged a `scope_violation` against `add-method/tooling/templates/TASK.md.tmpl` (× its 2 tracked mirrors) — this is the SIBLING task `seams-template-wiring`'s own declared-scope file (milestone `seams`, `phase: tests`, mid-flight in the same working tree), NOT a file this task touched or declared. Root cause: both tasks' scope snapshots shared timestamp/md5 `14a54385d6faebf70e28f69e054cc8cd`, so `add.py check`'s global touched-vs-declared scan attributed the sibling's build activity to this task too. Recovered per the prescribed playbook: `add.py phase tests phase-search-wiring` → `phase build` → `phase verify`, which re-snapshotted this task's `scope.declared` (unchanged, still the correct 7 files) against the current tree (new `snapshot_md5` `3f868cae08412840d52602bf3731c2a4`); re-ran `add.py check` after — the `scope_violation` warning against this task is gone (56→55 warnings), §6's pre-filled Build-expectations checkmarks and all TASK.md content survived the round-trip untouched (verified by re-reading the file), and none of this task's 7 declared-scope files changed content during the recovery (`git diff --stat` identical before/after). The sibling's own files were never touched by this verify pass.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent-id (add-verify / tdd-verifier persona, cross-referencing book-technical-writer persona) · adversarially checked: (1) byte-computed the actual insertion deltas independently rather than trusting the disclosed numbers — `scope.md` +61 B, `intake.md` +140 B, both match §3's pre-recorded figures exactly; (2) re-derived the rebaseline arithmetic from the pool's own stated formula (`new_baseline = old_baseline + ceil(surface/ratio)`) independently in Python — `ceil(140/0.88)=160` → core 20506→20666, `ceil(61/0.68)=90` → reference 75224→75314 — both match the shipped literals to the byte, ruling out a fudged/under-shot rebaseline that would trivially pass regardless of real content; (3) full `git diff` of both canonical prose files end to end — confirmed the ONLY change in each file is the single anchor-replace insertion; no unrelated sentence anywhere else in either file was quietly shortened to dodge the budget (the specific overfit angle the book-technical-writer persona warns against); (4) md5-compared all 4 copies of each file (3 tracked + 1 gitignored build artifact) — the 3 tracked mirrors are byte-identical to each other and DIFFERENT from the untouched 4th, confirming propagation landed exactly where required and nowhere it shouldn't; (5) ran the declared 6-suite (58 tests) live, green; (6) checked `test_skill_lean.py`'s narrated-history comment against the file's own established convention (11 prior entries) — same shape, same rebaseline-precedent citation, not a fabricated-looking one-off; (7) confirmed the CONVENTIONS.md line the task's §1/§3 cite (~line 85) is real and says exactly what the task claims it says (foundation-version 51, verbatim rebaseline formula) — not a misquoted or invented precedent. No overfit, no vacuous assertion, no stubbed logic found — this is a small, honestly-scoped prose change with real arithmetic behind its one non-trivial claim (the rebaseline), and that arithmetic checks out independently.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: agent-id (add-verify / tdd-verifier persona)
1. Security: CLEAR — prose-only insertion in 2 skill-guide markdown files + one Python test-literal rebaseline; no shell-exec/eval/network primitive, no new dependency, no secret, no user-input handling touched; ENGINE_MD5 untouched (confirmed — this task's diff never touches `add.py`/`add_engine/*`)
2. Concurrency: CLEAR — no runtime code path exists in this change; N/A by construction (docs + one test-pool byte-budget literal)
3. Architecture: CLEAR, with one disclosed nuance — the rebaseline-over-compression choice correctly applies CONVENTIONS.md's foundation-version-51 precedent (line 85, cited verbatim and confirmed accurate) for a genuinely-new-surface addition. Noted for the record: a LATER, narrower CONVENTIONS.md lesson (foundation-version 57, "when an honest-REFRAME adds prose bytes, reclaim from the same guide's own gloss rather than rebaselining") exists but does not apply here — that lesson is scoped to reframe/clarity edits with an available same-guide gloss to trim, not to a genuinely new CLI-command reference being wired in for the first time, which is what this task does. This was not re-litigated because the human already confirmed rebaseline-over-compression at freeze with full knowledge of the general precedent; flagging only so a future reader doesn't mistake the v57 lesson as silently overlooked.
Verdict: PASS
Residue: none (security/concurrency clear; the architecture nuance above is informational, not a residue — it does not change the freeze-time decision or require escalation)
Binding: advisory — task carries no `risk: high` / `sensitivity: mechanical` line

### GATE RECORD
Outcome: PASS
Reviewed by: agent (add-verify) · date: 2026-07-02

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether drafting agents actually run `add.py search` before a manual milestone re-read in real intake/scope sessions (validates the milestone's own theory of change — mechanizing a step vs. merely documenting it); whether `test_skill_lean.py`'s core/reference pools stay within their new rebaselined ceilings across the next few prose-touching tasks, or need another rebaseline soon (a signal the pools are chronically undersized, not just this-task-sized).

### Decisions (ADR)
- [AI] specify — chose minimal in-place sentence insertion at each step's existing anchor text, rebaseline the 2 busted lean-pool budgets; rejected compress unrelated existing prose elsewhere in the same pools to force-fit under the OLD budget (rejected at design time, pending human confirmation — conflicts with the loaded persona's own rule, and risks degrading other already-tight, heavily-pinned guides just to avoid a budget bump) · a shorter/vaguer reference to "search the corpus" instead of the real CLI grammar (rejected — R:invented_command_shape; the milestone's whole point is mechanizing the ACTUAL command, not gesturing at one).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (both flags confirmed: rebaseline over compression; "Interview before you size" confirmed as the Diverge-step landing spot))
- [AI] build — strategy used: as planned — verified against the evidence, not trusted from disclosure: the canonical `add-method/skill/add/{scope,intake}.md` carry the edit-of-record (git diff shows only the single frozen anchor-replace insertion in each, nothing else touched), both mirrors are byte-identical by md5 (confirmed independently, not by eye), the `test_skill_lean.py` rebaseline lands in the same build batch with a narrated-history comment matching the file's own established style and citing this task slug + the exact CONVENTIONS.md precedent line, the declared 6-suite (58 tests) is green, the milestone's own exit-criterion grep passes, and `git diff --stat` confirms exactly the 7 declared files changed (no more, no less) — no deviation from the planned batch order.
- [AI] verify — gate PASS (reviewed by agent (add-verify))

### Spec delta
- [SPEC · seeded] `add.py check`'s touched-vs-declared scope scan can mis-attribute a SIBLING task's in-flight file change to an unrelated task when both tasks' scope snapshots share the same tree-state md5 — the scan should exclude files that ARE in another active task's own declared scope before flagging `scope_violation` against a task that never declared them (evidence: this verify pass hit a transient `scope_violation` against `phase-search-wiring` for `TASK.md.tmpl`, a file exclusively owned by sibling `seams-template-wiring`; recovered via the documented tests→build→verify re-cross, but the false-positive cost a full extra round-trip)
- [SPEC · open] confirm whether running `add-build`/`add-verify` agent pairs concurrently in ONE shared working tree (no `isolation: "worktree"`) should become a documented anti-pattern with a standing recovery playbook, or whether worktree isolation should be the DEFAULT for any two tasks with overlapping shared-engine-adjacent scope (evidence: this is now the second documented incident of this exact collision shape, per `search-index`'s own §7 competency delta from the same milestone)

### Competency deltas
- [ADD · open] a verify pass that independently re-derives a build's own disclosed arithmetic (not just re-running its tests) catches a class of error fixture-based refute-reads miss: here the rebaseline formula (`old + ceil(surface/ratio)`) was recomputed from scratch in a fresh Python shell against the raw byte-deltas, confirming the shipped literals (20666/75314) to the byte rather than trusting the disclosed match — worth keeping as a standing verify-agent habit whenever a gate's evidence includes a formula-derived number, not just a test-pass count (evidence: this verify pass; no discrepancy found, but the check was substantive, not rubber-stamped)
- [ADD · open] `.add/CONVENTIONS.md`'s append-only newest-first ordering means a task's Ground-time citation of an older precedent (here foundation-version 51, line ~85) can coexist with a NEWER, narrower refinement of the same topic (here foundation-version 57's "reclaim from the guide's own gloss" carve-out for reframe-only edits) without either being wrong — a verify pass should check whether a newer entry NARROWS or CONTRADICTS the cited precedent before accepting the citation at face value, not just confirm the cited line exists (evidence: this verify pass found both entries, confirmed they address different edit shapes — new-surface addition vs. reframe-only — and neither invalidates the other for this task's case)

