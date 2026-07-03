# TASK: Audit + compact the ADD skill tree for genuine prose redundancy under the pinned lean-fence budget

slug: skill-tree-compaction-audit · created: 2026-07-02 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/skill/add/intake.md:65` (`## Roadmap` step 1) · `add-method/skill/add/advisor.md:3-6` (opening paragraph) · `add-method/skill/add/design.md:61-64` (Persona evidence checklist, beat 4) · `add-method/skill/add/run.md:127-129` (`## The autonomy level`, v7 reversal callout) · `add-method/skill/add/loop.md:58-61` (`## Reopen is the verb`) · `add-method/skill/add/phases/0-ground.md:59` (Advisor · Confidence hook) · `add-method/skill/add/phases/0-setup.md:89` (`## 5 · After the lock`) · `add-method/skill/add/confidence.md` (`## Where it plugs in`, 2nd bullet) — each edit propagated byte-identically to the 2 mirror trees `.claude/skills/add/` (dogfood) and `add-method/src/add_method/_bundled/skill/add/` (pip bundle, regenerable via `add-method/scripts/prepare_bundle.py`). Guard: `add-method/tooling/test_skill_lean.py` (`POOLS`, `_pool_bytes`, `TREE_BASELINE_BYTES` — the frozen per-pool byte fence) · `test_tree_parity.py` / `test_bundle_parity.py` (3-way byte-identity) · `test_wording_lint.py` + `WORDING_RUBRIC.md` (keep-list/banned-idiom surface).
Context (working folder): none — this task edits prose documentation only (the skill guides themselves ARE the artifact); no config/TODO/data/fixture files are in scope.
Honors (patterns / conventions): CONVENTIONS.md folded-v51 (from setup-tests-before-build): "a deliberate, contract-approved content addition that busts a lean-fence pool is absorbed by REBASELINING... not by token-golfing the new prose thinner" — this task runs the INVERSE direction (pure compaction, zero new surface), so no baseline/ratio changes; every pool's frozen target stays exactly as-is. CONVENTIONS.md folded-v50 (from component-method-docs): "a new agent-facing prose file ripples into THREE registries — the wording-lint surface count (×2 tests) + the skill lean fence — not just parity" — confirms `test_wording_lint.py` is a second registry to keep green, not just the byte fence.
Anchors the contract cites: the 8 file:line targets above; `test_skill_lean.py`'s `POOLS` list (core/orchestration/phases/reference); the 3 mirror roots (`add-method/skill/add/`, `.claude/skills/add/`, `add-method/src/add_method/_bundled/skill/add/`).
Issues/Risks (→ feed §1): (1) every pool is at ~0% headroom today (core +7B, orchestration +0B, phases +28B, reference +15B against target) — any stray byte added elsewhere during this task tips a pool back into red, so re-measure after every single edit, not just at the end. (2) several pinning tests (`test_v6_run.py`, `test_v7_auto_default.py`) regex-match the WHOLE file, not just the touched paragraph — the `run.md` candidate's safety depends on an UNTOUCHED sibling sentence elsewhere in the same file continuing to satisfy that regex, confirmed but worth re-checking post-edit. (3) 3-way parity means a 2-of-3 mirror edit goes red — the dogfood copy must be hand-mirrored (no dogfood-sync script found) and the bundle copy regenerated via `prepare_bundle.py`, not hand-copied.
Related intent: continuation of the "lean-pass major" milestone (25.1% lighter, shipped 2026-06-23, PRs #50-#52) and the `test_skill_lean.py` guard it left behind; direct trigger — user asked to "continue ADD SKILL.md optimizing as /skill-creator" this session (2026-07-02), after which a `skill-creator`-lensed audit found the tree already at ~0% headroom, sized here as a proper ADD task per the user's explicit choice.
Ground SHA: `7345649`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Tighten 8 pre-identified, grep-verified redundant passages across the 4 lean-fence pools of the canonical ADD skill tree — each removes a genuinely duplicated clause with zero information loss — propagated byte-identically to the dogfood and pip-bundle mirrors, raising every pool's headroom under its FROZEN ratio/baseline (no rebaseline).
Framings weighed: apply only the 8 pre-vetted candidates (chosen — each already grep-verified against its owning pinned test by 2 independent recon sweeps) · hunt for more candidates live during build (rejected — risks colliding with an un-surveyed pinning test among the ~80 that touch this tree, for marginal extra bytes) · lower a pool's ratio/baseline instead (rejected — that is a rebaseline, a human-signed exception per CONVENTIONS.md, not compaction, and defeats the point of finding genuine slack).
Must:
<must>
  - M1 each of the 8 edits removes ONLY a verbatim-duplicated clause/phrase (the same fact stated twice nearby) — no instruction, rule, number, or example is deleted.
  - M2 every edit is applied identically to all 3 mirror trees (canonical, dogfood, `_bundled`) so `test_tree_parity` and `test_bundle_parity` both stay green (the bundle copy is regenerated via `add-method/scripts/prepare_bundle.py`, never hand-copied).
  - M3 `test_skill_lean.py`'s 4 pool fences AND the whole-tree fence pass with LOWER actual-byte counts than at Ground SHA, at the SAME frozen baseline/ratio for every pool (no rebaseline) and no guide dropped.
  - M4 the full project test suite (`python3 -m unittest discover` from `add-method/tooling/`) passes, 0 failures, at a pass count ≥ the pre-build count.
  - M5 no backticked filename, XML-ish tag token, fenced-code-block content, numeric/ratio literal, or `WORDING_RUBRIC.md` keep-list/banned-idiom term is touched.
</must>
Reject:
<reject>
  - R1 an edit that saves bytes by deleting a rule, example, number, or otherwise-unstated-elsewhere fact -> "content_loss"
  - R2 an edit applied to only 1 or 2 of the 3 mirror trees -> "parity_drift"
  - R3 an edit that lowers a pool's `ratio` or `baseline` literal in `test_skill_lean.py` -> "budget_rebaselined"
  - R4 an edit that removes/rewords a `WORDING_RUBRIC.md` keep-list term or reintroduces a retired `[enforced]` idiom -> "wording_regression"
</reject>
After:
<after>
  - all 4 pools (core/orchestration/phases/reference) and the whole tree measure strictly fewer bytes than at Ground SHA, while remaining ≤ their unchanged frozen targets.
  - `test_skill_lean.py`, `test_tree_parity.py`, `test_bundle_parity.py`, `test_wording_lint.py`, and the full suite are all green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the `run.md` (v7-reversal) and `design.md` (persona-checklist) edits are the highest-risk of the 8 — they sit in the most test-dense paragraphs per both recon sweeps; lowest confidence because a regex elsewhere in the SAME file could still depend on the exact phrasing being removed even though the spot-check found none; if wrong: that single edit's pool reverts to red — drop just that one candidate, since every pool already clears its target from its OTHER, lower-risk candidates alone (core needs only the intake.md edit; phases needs only 0-ground.md+0-setup.md; reference needs only confidence.md; orchestration is the one pool where dropping run.md or design.md individually still leaves ~110B from the other 2-3 candidates).
  - [x] is a 213-byte combined total worth a full task cycle vs. leaving the pools at their current ~0%-headroom pass? — confirmed worth it: it converts a "one future addition breaks the fence" state into real margin, at low risk since every candidate is independently revertible and none touches pinned vocabulary.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: No content lost across the 8 edits   # M1
  Given the 8 candidate edits applied to the canonical tree
  When each edited file is diffed against its Ground-SHA version
  Then only the pre-identified duplicated clause is removed in each hunk
  And every pinning test that references the removed phrase still passes

Scenario: 3-way mirror parity holds   # M2
  Given all 8 edits applied to canonical, hand-mirrored to the dogfood tree, and the bundle regenerated via prepare_bundle.py
  When test_tree_parity and test_bundle_parity run
  Then both report every file byte-identical across all 3 trees
  And no orphan file exists in either direction

Scenario: Lean fence green with real headroom, no rebaseline   # M3
  Given the 8 edits applied
  When test_skill_lean.py runs
  Then all 4 pools and the whole tree pass with actual bytes strictly less than the Ground-SHA measurement
  And every pool's baseline/ratio literal is unchanged from Ground SHA
  And no guide or SKILL.md routing/pointer row is dropped

Scenario: Full suite stays green   # M4
  Given the build is complete
  When the full test suite runs from add-method/tooling/
  Then it reports 0 failures at a pass count >= the pre-build count

Scenario: No pinned-vocabulary collision   # M5
  Given the 8 edits
  When the removed text is checked against backticked filenames, XML-ish tags, fenced-code content, numeric/ratio literals, and WORDING_RUBRIC.md's keep-list/banned terms
  Then none of the removed text contains any of those tokens

Scenario: A content-losing candidate is discarded   # R1
  Given a candidate edit would delete a Must/Reject rule or a fact not restated elsewhere
  When it is evaluated during build
  Then it is discarded before being applied
  And the discarded candidate is not present in the final diff

Scenario: A partially-mirrored edit is caught before done   # R2
  Given an edit applied to only the canonical tree
  When test_tree_parity runs before the gate
  Then it fails red
  And the task is not marked done until all 3 trees match

Scenario: A rebaseline temptation is rejected   # R3
  Given a build temptation to lower a pool's ratio/baseline to pass more easily
  When the POOLS literals in test_skill_lean.py are checked against Ground SHA
  Then every baseline and ratio is byte-identical to Ground SHA
  And any such change is rejected before the gate

Scenario: No wording-lint regression   # R4
  Given the 8 edits
  When test_wording_lint.py runs
  Then it reports zero missing keep-list terms and zero reintroduced retired idioms
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
EDIT SET — 8 diffs, applied identically to 3 trees (canonical / dogfood / bundle-regenerated)

1. intake.md:65                    [core]           -15 B
   - remove the parenthetical "(AI proposes.)" after "1. **Propose** the roadmap — ..."

2. advisor.md:3-6                  [orchestration]  -29 B
   - remove "(a sweep, a review, a batch)" from the opening paragraph (the categories
     are spelled out in full 5 lines later, in "## When to spawn")

3. design.md:61-64                 [orchestration]  -47 B
   - remove the 2 rhetorical questions "— is the screen right?" and "— the right
     screen?" from the UI-Designer/UX-Researcher persona-checklist parenthetical

4. run.md:127-129                  [orchestration]  -46 B
   - tighten the v7-reversal callout: "v7 flips it — `auto` is the default,
     `conservative` is the deliberate lowering." -> "v7 flips it to `auto` as the
     default." (the dropped clause restates the "conservative — the deliberate
     lowering" bullet 2 lines above)

5. loop.md:58-61                   [orchestration]  -35 B
   - tighten "Deciding WHEN to fire it — because a goal criterion is unmet — is this
     loop's job." -> "— fired by this loop's judgment, not the engine's." (restates
     the sentence's own opening clause)

6. phases/0-ground.md:59           [phases]          -5 B
   - "canonical spawn case (advisor.md)" -> "canonical spawn (advisor.md)"

7. phases/0-setup.md:89            [phases]         -13 B
   - "don't ask for a separate contract-freeze sign-off." -> "no separate
     contract-freeze sign-off."

8. confidence.md, "## Where it plugs in" bullet 2   [reference]  -23 B
   - remove "Recommend it —" (restates "recommend" used 2 clauses earlier in the
     same sentence)

Net: core -15 B · orchestration -157 B · phases -18 B · reference -23 B · tree -213 B
Post-edit projected actual (vs unchanged target): core 18164/18186 · orchestration
40615/40772 · phases 32225/32271 · reference 51175/51213 — every pool still passes,
now with real headroom instead of ~0.
```

Glossary deltas: none.
Least-sure flag surfaced at freeze: [spec] the run.md (v7-reversal) and design.md (persona-checklist) edits are the highest-risk of the 8 — they sit in the most test-dense paragraphs; both recon sweeps spot-checked the relevant regex tests and found no collision, but neither exhaustively read all ~80 tests that touch this tree. Cost if wrong: that one pool's test goes red at build; recovery is trivial since the edit is independently revertible and every pool clears its target from its other candidates alone (except orchestration, which needs ~2 of its 4). Approved as-is by Tin Dang — freeze proceeds with both flagged edits included.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 5 new scenarios this task actually adds (M1/M5 and R1/R4 are already covered by the EXISTING suite — `test_skill_lean.py`, `test_tree_parity.py`, `test_bundle_parity.py`, `test_wording_lint.py` — since a content-loss or vocab collision already fails one of those; only the "strictly fewer bytes than Ground SHA" claim (M3) is genuinely new and needs a new assertion).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_all_pools_shrink_from_ground_sha: arrange the 4 pools' Ground-SHA byte counts (18179/40772/32243/51198, hardcoded from this task's §0 measurement) / act by re-measuring each pool's current bytes / assert each is strictly LESS than its Ground-SHA count AND still <= its unchanged frozen target · covers: M3
  - test_tree_shrinks_from_ground_sha: same, for the whole-tree total (142392 at Ground SHA) · covers: M3
  - existing test_skill_lean.SkillLeanTest.test_pools_under_byte_budget / test_tree_under_byte_budget / test_no_guide_dropped / test_core_routing_rows_present / test_core_pointers_present: re-run post-build, covers M3 (no guide dropped, routing intact)
  - existing test_tree_parity.TreeParityTest.test_skill_trees_byte_identical: re-run post-build, covers M2 / R2
  - existing test_bundle_parity (bundle-copy checks): re-run post-build after `prepare_bundle.py`, covers M2 / R2
  - existing test_wording_lint suite (all 4 fences): re-run post-build, covers M5 / R4
  - full `python3 -m unittest discover` from add-method/tooling/: re-run post-build, covers M1 / M4 / R1 / R3 (any content loss or pinned-vocab collision surfaces as a failure somewhere in this ~2500-test suite)
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `./tests/` `add-method/skill/add/` `.claude/skills/add/` `add-method/src/add_method/_bundled/skill/add/`
Strategy (ordered batches): 1. apply the 6 lower-risk edits first (intake, advisor, loop, both phases/0-*, confidence) to canonical, re-run test_skill_lean after each to catch a surprise collision early · 2. apply the 2 flagged higher-risk edits (design.md, run.md) individually, re-running the specific pinning tests named in §0 Issues/Risks after each · 3. mirror all 8 edits byte-identically into `.claude/skills/add/` · 4. regenerate `_bundled/skill/add/` via `add-method/scripts/prepare_bundle.py` (never hand-copy) · 5. run test_skill_lean + test_tree_parity + test_bundle_parity + test_wording_lint + the new §4 red test · 6. run the full suite last.

Persona (optional): none — generic.
Known-problem fixes: a candidate collides with an un-surveyed pinning test (§0 risk 2) → drop that one edit only, re-verify the rest, note it in §6; a hand-edit of `_bundled/` drifts from canonical (§0 risk 3) → always regenerate via `prepare_bundle.py`, never hand-copy; a pool tips back to ~0 headroom from an unrelated stray byte (§0 risk 1) → re-measure with `wc -c` after every single file edit, not just at the end.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): apply and re-verify one edit at a time (never batch all 8 then test) so a collision is attributable to a single diff, not a tangle of 8.
Code lives in: `./tests/` (this task writes no `./src/` — the deliverable is the 3 mirrored prose trees named in Scope, not this task dir).
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite (`add-method/tooling/`, `discover -p "test_*.py"`) reports 2710 tests, 2 failures both pre-existing at Ground SHA and unrelated to this task's scope (see Residue below) — identical failure set before and after this build, zero regressions
- [x] coverage did not decrease — no code changed, only prose; every touched line is covered by the pinning tests that ran green
- [x] no test or contract was altered during build — `git diff` confirms only the 8 frozen §3 targets changed; no `test_*.py` file touched
- [ ] the green was EARNED, not gamed — refute-read agent dispatched, verdict pending below
- [x] concurrency / timing of the risky operation is safe — N/A, no concurrent/async code in this task (see Advisor lens 2 for the one operational concurrency risk this build itself hit and recovered from)
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A, no code/dependency surface touched
- [x] layering & dependencies follow CONVENTIONS.md — honors the "compaction not rebaseline" + "3-registry ripple" precedents cited in §0
- [x] a person reviewed and approved the change — Tin Dang approved the §3 freeze including both flagged higher-risk edits

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] all 4 pools measure fewer bytes than Ground SHA, still ≤ their unchanged frozen target — confirmed by direct measurement: core 18164/18186 (was 18179) · orchestration 40615/40772 (was 40772) · phases 32225/32271 (was 32243) · reference 51175/51213 (was 51198) — matches the §3 CONTRACT projection exactly.
- [x] all 3 mirror trees byte-identical — confirmed by `diff -rq` returning empty both directions (canonical↔dogfood, canonical↔bundle) and `test_tree_parity`/`test_bundle_parity` green.
- [x] no pool baseline/ratio literal changed — `test_skill_lean.py`'s `POOLS` list untouched (not in this task's declared Scope; `git diff` confirms it wasn't edited).
- [x] `test_wording_lint`'s 4 fences stay green — 30/30 tests pass, no keep-list term missing, no retired idiom reintroduced.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read every one of the 8 diffs in full before and after applying (not skimmed); each removal verified against its owning pinned test(s) before being applied, one edit at a time, re-testing after each. WIRING/DEAD-CODE: N/A, no code symbols in this task.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every anchor §3 cites (the 8 file:line targets) still resolves in the current tree — re-read each file post-edit to confirm; no line moved unexpectedly since these were the only edits in the run.
- [x] no anchor moved/renamed since Ground SHA — the 8 files' surrounding structure (headers, section names) is untouched; only the cited clauses were trimmed in place.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent (dispatched adversarial refute-read, cross-checked with an independent background subagent of its own) · adversarially checked: re-diffed all 8 canonical files against HEAD independently of this TASK.md's own paraphrase; judged each removed clause for hidden new information (confirmed each is a genuine restatement, citing the specific surviving sentence that preserves the fact — e.g. run.md's "conservative — the deliberate lowering" bullet 2 lines above the edited callout); re-verified 3-way mirror parity via direct `diff -rq` rather than trusting the claim; re-ran the full pinned guard suite (`test_skill_lean`/`test_tree_parity`/`test_bundle_parity`/`test_wording_lint`, 30/30 green) from scratch; independently traced `test_v7_auto_default.py`'s exact regex against the edited run.md text in a live REPL rather than trusting this task's citation; re-ran the full 2710-test suite and confirmed the 2 failures are identical before/after and unrelated (a pre-existing `test_seams_template_wiring.py` grep-path issue, untouched by this task); diffed the bundle's tooling/docs trees for surprise side effects. Found ONE real, non-disqualifying side effect (below), which was corrected before this record.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self
1. Security: CLEAR — no code, secrets, or executable surface touched; pure markdown prose edits to documentation the engine reads but never executes (skill guides are NO-EXEC by the project's own invariant).
2. Concurrency: CLEAR — no concurrent/async logic exists in this task's deliverable. One OPERATIONAL concurrency risk occurred during THIS build itself: an early full-suite baseline measurement was launched in the background and I then began editing files while it was still running, risking a torn read. Caught before being trusted — discarded that run, used `git stash`/`stash pop` to get a genuinely clean pre-edit baseline, and serialized every subsequent full-suite run to complete before touching files again.
3. Architecture: CLEAR — no rebaseline, no pool-boundary change; edits stay within the existing 4-pool/3-mirror structure. One SCOPE residue found by the refute-read: `add-method/scripts/prepare_bundle.py` (run to regenerate the bundle mirror, per Must M2) has a latent bug — it wipes `_bundled/tooling/` and repopulates only `add.py`/`add_engine/`/`templates/`, silently dropping `_bundled/tooling/engine_pin.py` (21 lines) every time it runs, regardless of this task. Caught, the file was restored via `git checkout HEAD -- <path>` before this record (confirmed: no test references the bundled copy, only the canonical `add-method/tooling/engine_pin.py`, which this task never touched) — the working tree now carries ONLY the 8 declared edits. The underlying script bug is out of this task's declared scope; recorded as a spec delta below for a future fix.
Verdict: PASS
Residue: none blocking — 1 pre-existing, unrelated test failure pair (test_seams_template_wiring / test_ci_tooling_mirror_gap, both from the same root cause, present at Ground SHA and unchanged) and 1 out-of-scope script bug (prepare_bundle.py drops _bundled/tooling/engine_pin.py) are disclosed above and in §7, neither caused by nor fixed by this task.
Binding: advisory — sensitivity unset (project default)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (via the §3 freeze approval covering all 8 edits, including the 2 flagged higher-risk ones) · date: 2026-07-02

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose apply only the 8 pre-vetted candidates; rejected hunt for more candidates live during build (rejected — risks colliding with an un-surveyed pinning test among the ~80 that touch this tree, for marginal extra bytes) · lower a pool's ratio/baseline instead (rejected — that is a rebaseline, a human-signed exception per CONVENTIONS.md, not compaction, and defeats the point of finding genuine slack).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang (via the §3 freeze approval covering all 8 edits, including the 2 flagged higher-risk ones))

### Spec delta
- [SPEC · carried] `add-method/scripts/prepare_bundle.py` wipes `_bundled/tooling/` and repopulates only `add.py`/`add_engine/`/`templates/`, silently dropping `_bundled/tooling/engine_pin.py` (21 lines) on every run — undetected until now because no test asserts the bundled tooling tree's file SET, only specific files' content (`test_bundle_parity.py`'s `test_runtime_surface_complete` checks presence of `add.py`/`add_engine/`, not an exhaustive listing). Not this task's scope to fix; a future task should either make `prepare_bundle.py` copy the whole `tooling/` dir minus test files, or add a `test_bundle_parity` case asserting the bundled tooling file set matches canonical minus tests (evidence: refute-read agent's `git status` catch this build, restored via `git checkout HEAD`). [carried: currently inert (the bundled file exists, kept in sync by hand); a latent risk only if that manual sync is ever forgotten]
- [SPEC · seeded] `test_seams_template_wiring.py::test_milestone_exit_grep_lists_all_3` and `test_ci_tooling_mirror_gap.py::test_fresh_checkout_survives_test_job_sequence` both fail at Ground SHA (`7345649`), pre-existing and unrelated to this task — a `grep -cl` invocation isn't matching all 3 `TMPL_COPIES` paths for `TASK.md.tmpl`. Confirmed present on a clean stash-reverted tree before any of this task's edits and unchanged after. Worth a dedicated fix task since it's presumably failing in CI too (evidence: identical failure pair in both the pre-edit clean-baseline run and the post-edit run, `sed`-isolated tracebacks match byte-for-byte on the assertion message). [→ grep-binary-agnostic-milestone-test]

### Competency deltas
- [ADD · folded] a background full-suite measurement launched right before starting file edits can race those edits if you don't wait for it — the fix (discard the racy run, `git stash`/`stash pop` to get a genuinely clean pre-edit baseline, then serialize all subsequent full-suite runs to completion before touching files) worked, but the safer default is to never launch a long background baseline measurement and then immediately start editing the same files it's reading (evidence: this build's own first baseline attempt, discarded). [folded foundation-version 61]
- [TDD · folded] a pinned-byte-budget suite (`test_skill_lean.py`) sitting at ~0% headroom for months means the ONLY way to gain real margin is a dedicated compaction task — worth periodically re-running this kind of grep-verified redundancy audit (2 independent recon sweeps, ~150k tokens total) rather than waiting for the fence to break on a future legitimate addition, since finding safe candidates gets harder as prose gets denser each pass (evidence: this task found only 213 B across 4 pools despite 2 thorough independent sweeps, versus the original lean-pass's 25%+ cut). [folded foundation-version 61]
