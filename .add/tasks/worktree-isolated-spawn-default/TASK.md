# TASK: Prefer Worktree-Isolated Agent Spawning Per Task

slug: worktree-isolated-spawn-default · created: 2026-07-03 · stage: mvp
milestone: (none)
sensitivity: mechanical
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `.claude/skills/add/streams.md:52` ("wave is spawnable at once (`isolation="worktree"`)"), `:88` ("Isolation: spawn each worker with `isolation="worktree"`"), `:258` (spawn-adapter table row: `isolate | worktree | isolation="worktree" | ...`) — all 3 currently frame worktree isolation as tied to an explicitly-PARALLEL multi-task wave, never a single sequential subagent delegation; `add-method/docs/10-setup-and-stages.md:116` ("isolated in a git worktree, so concurrent builds cannot collide" — same parallel-wave framing). No file in `.claude/agents/*.md` or `add-method/agents/*.md` mentions isolation/worktree at all today (confirmed via grep) — the phase-agent roster prompts are silent on this.
Context (working folder): docs/skill prose only — no code, no test, no engine pin touched
Honors (patterns / conventions): none re-derived — this is a documentation-only convention change
Seams consulted: none cited
Anchors the contract cites: the 4 mention sites above
Issues/Risks (→ feed §1): a REAL, already-flagged tension exists between this task's resolved direction and the user's own separate, standing personal preference (recorded in the user's global CLAUDE.md, Rule 5's spawn-template comment): "isolation=\"worktree\", # worktree only for parallels mode. Sequential Mode are skip this option" — i.e. Tin Dang's own general cross-project habit is worktree-for-parallel-only, while THIS backlog task (resolved 2026-07-03, specific to ADD-the-methodology's own shipped guidance) says the opposite: worktree should be ADD's stated DEFAULT even for a single sequential phase-delegated spawn. These are different scopes (Tin Dang's personal Task-tool habit vs. what ADD-the-product tells its OWN users/agents to do) and can coexist without contradiction, but a future reader must not conflate them — this task changes ADD's shipped guidance, NOT the user's own global CLAUDE.md.
Related intent: seeded from phase-search-wiring spec-delta — this is the second documented incident of an in-place (non-worktree) concurrent agent-pair collision on shared engine-adjacent scope; Tin Dang confirmed this session that worktree isolation should become the default going forward, not merely a documented anti-pattern [← phase-search-wiring]
Ground SHA: `ba42053` (`git rev-parse --short HEAD`) — all cited line numbers current as of this commit

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: ADD's own guidance for spawning a phase-delegated subagent (build/verify, and the orchestrator's XML spawn-prompt convention) should PREFER worktree isolation (`isolation: "worktree"`) as the DEFAULT for a task's agent-spawned steps, not merely a documented anti-pattern or an opt-in reserved for explicitly-parallel multi-task runs (from phase-search-wiring spec-delta; resolved in favor of DEFAULT by Tin Dang, 2026-07-03)
Framings weighed: reword the 4 existing mention sites (streams.md ×3, docs/10-setup-and-stages.md ×1) to state worktree isolation as the default for ANY agent-spawned step, with "shared-tree needs a stated reason" as the opt-out condition, mirroring the exact wording pattern already used in this session's own TASK.md drafts' "Spawn isolation (default):" line (chosen — smallest change, reuses wording already proven this session) · add a NEW top-level "## Isolation" section to streams.md instead of editing the 4 inline mentions — rejected, creates a second source of truth that could drift from the inline mentions instead of updating them in place · leave the wording as-is and rely on task authors reading between the lines — rejected, this is exactly the "documented anti-pattern, not a stated default" gap the spec-delta named
Must:
<must>
  - each of the 4 existing mention sites states worktree isolation as the DEFAULT for any agent-spawned step (single sequential delegation OR a parallel wave), not only for explicitly-parallel multi-task runs
  - a shared-tree (non-worktree) spawn is still possible but requires a stated reason in the task's own TASK.md (mirrors this session's own "Spawn isolation (default):" line already added to newer TASK.md drafts)
  - the change is prose-only — no code, test, or engine pin is touched
</must>
Reject:
<reject>
  - the new wording could be read as contradicting the user's own separate global CLAUDE.md preference (worktree only for parallel mode, sequential skips it) -> the doc change must explicitly scope itself to ADD-the-product's own shipped guidance for ITS users/agents, not overwrite or reference the user's personal cross-project habit
</reject>
After:
<after>
  - any reader of streams.md or docs/10-setup-and-stages.md sees worktree isolation presented as ADD's stated default for agent-spawned work, with the opt-out condition (a stated reason) made explicit rather than implicit
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ this task's resolved direction (worktree-as-default for ADD's own shipped guidance) does not conflict with, override, or need to reference the user's own separate global CLAUDE.md Task-tool habit (worktree only for parallel mode) — lowest confidence because these are genuinely different scopes (product guidance vs. personal habit) but a careless wording choice in the doc edit COULD blur that line for a future reader; if wrong: a future session might misread ADD's own docs as instructing IT to ignore the user's stated global preference, when the two were never meant to conflict
  - [x] no code path enforces or reads isolation mode today — confirmed via Ground: `isolation="worktree"` appears only in prose/examples, never as a config value the engine parses; this is purely a documentation/convention change with zero runtime effect
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: streams.md states worktree as default   # M1
  Given a reader opens .claude/skills/add/streams.md
  When they read the wave-spawn and worker-isolation sections (lines ~52, ~88, ~258)
  Then each states worktree isolation as the default for any agent-spawned step
  And a shared-tree spawn is presented as requiring a stated reason, not as an equal alternative

Scenario: docs/10-setup-and-stages.md states worktree as default   # M2
  Given a reader opens add-method/docs/10-setup-and-stages.md's hard-boundary section
  When they read the isolation sentence (line ~116)
  Then it states worktree isolation as the default, consistent with streams.md's wording

Scenario: no code or test is touched   # M3
  Given the full existing tooling test suite
  When it is run after this doc change
  Then every test still passes unmodified — this is a prose-only change

Scenario: the doc change does not reference or override the user's personal global preference   # R1
  Given the new wording in streams.md/docs/10-setup-and-stages.md
  When read in isolation from any user-specific config
  Then it scopes itself to ADD's own shipped guidance only, with no mention of or edit to any file outside this repo
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOC .claude/skills/add/streams.md   body: { 3 mention sites: L52, L88, L258 }
  each -> reworded to state isolation="worktree" as the DEFAULT for any agent-spawned step
    (single sequential OR parallel wave), shared-tree opt-out requires a stated reason

DOC add-method/docs/10-setup-and-stages.md   body: { 1 mention site: L116 }
  reworded consistently with streams.md's new wording

Schema: no data/code schema touched — pure prose edit, 4 sites across 2 files
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin Dang, 2026-07-05 ("freeze as drafted, start with the trivial mechanical fixes first")
Least-sure flag surfaced at freeze: [spec] whether this doc change could be misread as touching or overriding the user's own separate global CLAUDE.md preference (worktree only for parallel mode) — these are different scopes (ADD's shipped guidance vs. a personal cross-project habit) and the wording will explicitly avoid referencing the user's global config, but a future reader conflating the two is the residual risk; cost if wrong: confusion in a future session about which preference governs a given spawn decision.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: n/a — content-assertion tests on prose, not code coverage
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_streams_md_states_worktree_default: arrange read streams.md / act scan the 3 mention sites / assert wording states "default" (not merely an example tied to "wave"/parallel context) near each `isolation="worktree"` mention · covers: M1
  - test_setup_stages_states_worktree_default: same shape for docs/10-setup-and-stages.md's L116 · covers: M2
  - test_full_suite_unaffected: act run the full tooling suite after the doc edit / assert all existing tests still pass · covers: M3
</test_plan>

Tests live in: `add-method/tooling/test_skill_lean.py` (extend — this file already scans streams.md content/budget) or a new small `add-method/tooling/test_worktree_default_wording.py` (decide at Build time) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/streams.md`, `.claude/skills/add/streams.md`, `add-method/src/add_method/_bundled/skill/add/streams.md` (3 tracked mirrors), `add-method/docs/10-setup-and-stages.md`, `10-setup-and-stages.md` (repo root), `add-method/src/add_method/_bundled/docs/10-setup-and-stages.md` (3 tracked mirrors), `.add/docs/10-setup-and-stages.md` (untracked dogfood copy), `add-method/tooling/test_worktree_default_wording.py` (new test file, per this task's own §4 "decide at Build time" option)
Strategy (ordered batches): 1. draft the reworded sentences for all 4 mention sites, minimizing byte delta · 2. check the net byte change against streams.md's current pinned budget (orchestration pool, baseline 56040 @ ratio 0.75, per `test_skill_lean.py`) · 3a. if the wording fits within budget via an equivalent compression elsewhere in streams.md, no rebaseline needed · 3b. if it doesn't, follow this file's own established rebaseline convention (cite exact delta bytes, add a new dated comment entry, bump the baseline — same pattern as every prior entry in `test_skill_lean.py`'s comment trail) · 4. write the RED content-assertion tests · 5. apply the doc edits · 6. confirm green + `add.py check`

Persona (optional): book-technical-writer — prose clarity + this project's own documented budget-discipline conventions
Known-problem fixes: growing streams.md's byte count without either compressing elsewhere or an explicit, cited rebaseline would silently break `test_skill_lean.py`'s pinned budget assertion → planned fix: measure the exact delta before committing to wording, per [[feedback_lean_over_budget_bump]] (COMPRESS to absorb under budget is the default; a rebaseline is the human-approved exception, not the default move)
Strategy actually used: as planned — drafted terse wording for all 4 sites (+115 B total), measured the exact orchestration-pool byte delta before committing to wording (41887 -> 42002 vs target 42030, 28 B to spare), so no rebaseline was needed; wrote the content-assertion tests in a new dedicated file (`test_worktree_default_wording.py`) rather than extending `test_skill_lean.py`, keeping budget concerns and content concerns in separate files; discovered mid-build that streams.md and 10-setup-and-stages.md each have 3 (not the originally-cited 1) tracked mirror copies and propagated to all of them, correcting this task's own §5 Scope line accordingly
Safety rule (feature-specific): the doc wording must not reference or attempt to override the user's own separate global CLAUDE.md preference — scope the language to ADD's own shipped guidance only
Code lives in: n/a — docs only
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_worktree_default_wording.py` 3/3, `test_skill_lean.py` 7/7, full tooling suite 2929/2929 (OK, exit 0)
- [x] coverage did not decrease — 3 new tests added, 0 removed
- [x] no test or contract was altered during build — §3 CONTRACT text unchanged
- [x] the green was EARNED, not gamed — add-verify agent refute-read confirmed the wording reads naturally (not test-magic-word stuffing), the paragraph-anchor regexes in the new test are unique substrings with no false-positive/negative extraction risk, and every §1 Must/Reject traces to a §2 scenario
- [x] concurrency / timing of the risky operation is safe — n/a, doc-only change (Advisor: CLEAR)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure prose (Advisor: CLEAR)
- [x] layering & dependencies follow CONVENTIONS.md — change stays inside doc/skill prose, no new coupling (Advisor: CLEAR)
- [x] a person reviewed and approved the change — Tin Dang via explicit freeze + sequencing instruction; auto-gated at Verify per `autonomy: auto` + `sensitivity: mechanical`

### Build expectations — what "correct" looks like
- [x] each of streams.md's 3 mention sites reads "worktree is the default for any spawn/agent-spawned step, not just a wave" — confirmed by `test_streams_md_states_worktree_default` + add-verify's direct read of all 3 paragraphs in full context
- [x] docs/10-setup-and-stages.md's hard-boundary sentence states the same default, consistent wording — confirmed by `test_setup_stages_states_worktree_default`
- [x] neither file references or overrides the user's separate personal global CLAUDE.md preference — confirmed by `test_no_reference_to_user_global_config` AND an add-verify adversarial reread grepping for paraphrased leaks (`personal|preference|~/.claude|habit|cross-project|override`) — zero hits

### Deep checks
- [x] SEMANTIC (prose) — add-verify read all 4 edited paragraphs in full surrounding context (not just diff hunks); confirmed natural, unambiguous wording, not keyword-stuffed to pass tests

### Live-verify evidence — confirm the §0 GROUND anchors still resolve
- [x] all 4 mention sites (streams.md ×3, 10-setup-and-stages.md ×1) confirmed present and edited in the current tree; re-grepped for the correct current line numbers post-edit
- [x] anchor correction disclosed: this task's own §5 Scope line originally cited only 1 mirror each for streams.md/10-setup-and-stages.md; Build discovered 3 tracked mirrors each and corrected the Scope line before gating (see §5 Strategy actually used)

### Refute-read verdict — the earned-green check
Verdict: EARNED
By: add-verify agent · adversarially checked: paragraph-anchor regex uniqueness (no false-positive/negative extraction), natural-reading test of the wording vs. keyword-stuffing, a grep-based adversarial reread for paraphrased leaks toward the user's personal global CLAUDE.md preference (beyond the test's crude "CLAUDE.md"/"global" string check), independently re-summed the orchestration-pool byte total via its own `wc -c`, independently reran `test_fresh_checkout_survives_test_job_sequence` end-to-end (101.7s) to confirm it genuinely passes and traced why (commit `731755f`'s anchor fix, unrelated to this task's diff)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: add-verify agent
1. Security: CLEAR — pure prose, no code/config/engine surface touched
2. Concurrency: CLEAR — n/a, doc-only
3. Architecture: CLEAR — one non-blocking 💭 note: stating the default in 4 separate prose spots (vs. one canonical definition) is a mild duplication smell, but matches streams.md's existing convention of restating isolation multiple times, and is exactly what the frozen contract scoped; §0 GROUND already discloses this is a documentation/convention change with zero runtime effect, so it's an honest limit, not a false expectation
Verdict: PASS
Residue: none blocking. Disclosed: stating "worktree is the default" in 4 prose locations rather than one canonical cross-referenced definition is a minor duplication; no code enforces or reads isolation mode today (unchanged from Ground), so this is pure guidance, not an operational claim readers could be misled by.
Binding: yes — mechanical

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gated per `autonomy: auto` + `sensitivity: mechanical`, per the project's advisor-gate-relax rule; the add-verify agent's refute-read + 3-lens check recorded above as the evidence trail) · date: 2026-07-05

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose reword the 4 existing mention sites (streams.md ×3, docs/10-setup-and-stages.md ×1) to state worktree isolation as the default for ANY agent-spawned step, with "shared-tree needs a stated reason" as the opt-out condition, mirroring the exact wording pattern already used in this session's own TASK.md drafts' "Spawn isolation (default):" line; rejected add a NEW top-level "## Isolation" section to streams.md instead of editing the 4 inline mentions — rejected, creates a second source of truth that could drift from the inline mentions instead of updating them in place · leave the wording as-is and rely on task authors reading between the lines — rejected, this is exactly the "documented anti-pattern, not a stated default" gap the spec-delta named
- [human] freeze — froze §3 @ v1 (approved by Tin Dang, 2026-07-05 ("freeze as drafted, start with the trivial mechanical fixes first"))
- [AI] build — strategy used: as planned — drafted terse wording for all 4 sites (+115 B total), measured the exact orchestration-pool byte delta before committing to wording (41887 -> 42002 vs target 42030, 28 B to spare), so no rebaseline was needed; wrote the content-assertion tests in a new dedicated file (`test_worktree_default_wording.py`) rather than extending `test_skill_lean.py`, keeping budget concerns and content concerns in separate files; discovered mid-build that streams.md and 10-setup-and-stages.md each have 3 (not the originally-cited 1) tracked mirror copies and propagated to all of them, correcting this task's own §5 Scope line accordingly
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-gated per `autonomy: auto` + `sensitivity: mechanical`, per the project's advisor-gate-relax rule; the add-verify agent's refute-read + 3-lens check recorded above as the evidence trail))

### Spec delta
- [SPEC · dropped] a canonical single-definition-with-cross-references restructure of the "worktree is the default" statement (vs. today's 4 separately-worded prose spots) — dropped: Advisor flagged this as only a mild, non-blocking duplication smell that matches streams.md's existing convention of restating isolation multiple times; not worth a follow-up task on its own (evidence: add-verify Architecture lens, PASS with disclosed non-blocking residue)

### Competency deltas
- [ADD · folded] a task's own declared §5 Scope line can undercount real mirror-tree fan-out (this task's Ground/Build initially assumed 1 tracked copy each for streams.md/10-setup-and-stages.md; Build discovered 3 tracked copies each) — worth a lighter-weight Ground-phase habit of grepping `find . -name "<file>" | xargs git ls-files` before declaring Scope on any doc/skill file, not just engine-tree files (evidence: this task's own §5 Scope correction, same class of miss as the earlier `3 pinned engine-tree mirrors` imprecision noted in strip-scaffold-backtick-comment-fix/adr-harvester-multiline-fields) [folded foundation-version 64]
