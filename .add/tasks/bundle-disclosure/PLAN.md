# TASK: Disclose phase guides into the bundle agents

slug: bundle-disclosure · created: 2026-07-14 · stage: mvp
milestone: six-phase-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: bundle-disclosure — phase guides disclose INTO the roster bundle agents (six-phase-loop 4/6, the user's directive: "instead load all step's skill in main agent, we can disclose it into subagents"): each roster agent loads its own bundle guides at spawn; the orchestrator reads SKILL.md only when delegating; the inline lane stays first-class (work inline -> load the one phase guide yourself, unchanged)
Must:
  - add-design.md instructs loading `phases/0-setup.md` (fresh project) + `phases/1-specify.md` + `phases/3-plan.md` at spawn, and its span prose re-cuts to the merged reality (setup · specify · plan — grounding/scenarios/contract live inside them, not as step names)
  - add-build.md instructs loading `phases/4-tests.md` + `phases/5-build.md` at spawn
  - add-verify.md instructs loading `phases/6-verify.md` at spawn, and its prose re-cuts (it owns verify end-to-end incl the post-gate Observe duties; OBSERVE is no longer a spawn step)
  - SKILL.md states the disclosure split in one sentence: delegated -> the roster agent loads its own bundle guides (the orchestrator reads SKILL.md only); inline -> load the one phase guide yourself (unchanged, first-class); ≤9500 B held
  - agents sync: canonical `add-method/agents/` -> `_bundled/agents/` byte-identical (the existing roster pin) + the installed `.claude/agents/` copies refreshed
Reject:
  - a roster agent naming a deleted guide (2-scenarios.md/7-observe.md) or a retired step name (GROUND/SCENARIOS/CONTRACT/OBSERVE) as a spawn step -> the doc-truth test goes red
  - the orchestrator instructed to pre-read a phase guide before delegating -> the disclosure sentence pin goes red
Accept: Given a delegated phase, When the orchestrator spawns the roster agent named by the SKILL.md table, Then the agent's own file names the exact bundle guide(s) it loads and the orchestrator needed only SKILL.md.
Boundary: none — no external input (agent prose + one SKILL.md sentence; the engine is untouched)
Assumptions: ⚠ agent prose edits ripple into surface registries (method-ergonomics precedent: "new agent prose ripples into 3 surface registries") — why: roster descriptions are pinned by CLAUDE.md sync-guidelines/roster tests; if wrong (more registries pin the old span wording): each is a fence-named doc-truth ripple (cost: fence rounds)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/agents/add-design.md · add-build.md · add-verify.md (span prose + NEW bundle-guides instruction) · add-method/src/add_method/_bundled/agents/ (byte-parity twin) · .claude/agents/ (installed copies) · add-method/skill/add/SKILL.md (one disclosure sentence, ≤9500 ceiling) ×3 skill trees · roster surface registries (CLAUDE.md block? test_roster_shipped, fence-named)
Context (working folder): engine untouched (no MD5 re-aim); test_roster_shipped pins bundled↔canonical byte parity; test_skill_orient_split pins the 9500 ceiling; SKILL.md pinned-phrase census binds any trim
Honors (patterns / conventions): inline-over-heavy-spawns (the inline lane stays first-class, never demoted) · don't override an agent's native Return contract (extend only) · progressive disclosure (the milestone's thesis)
Anchors the contract cites: add-design.md · add-build.md · add-verify.md · SKILL.md flow section
Ground SHA: 7ffdd2d — stamped by freeze

### Contract

```
add-design.md:  span -> "setup · specify · plan"; + "## Load your bundle guides"
  (phases/0-setup.md fresh-project · phases/1-specify.md · phases/3-plan.md,
  from the project's skill tree, at spawn, before the persona); description
  spawn steps -> "SETUP, SPECIFY, or PLAN step"
add-build.md:   + same section (phases/4-tests.md · phases/5-build.md);
  description spawn steps stay "TESTS or BUILD"
add-verify.md:  span -> verify end-to-end incl post-gate Observe duties (§7);
  + same section (phases/6-verify.md); description -> "Spawn at the VERIFY
  step" (no OBSERVE step name)
SKILL.md (flow section): one added sentence — delegating? the roster agent
  loads its own bundle guides; you read ONLY SKILL.md. Inline? load the one
  phase guide yourself (unchanged). <= 9500 B
sync: agents canonical -> _bundled byte-identical + .claude/agents refresh;
  SKILL.md x3 trees
NEW test_bundle_disclosure.py pins: per-agent guide census · no retired step
  name in descriptions · the SKILL.md disclosure sentence · parity · ceiling
```

`Least-sure flag surfaced at freeze:` [contract] the SKILL.md sentence placement under the 145-byte headroom — why: the ceiling is 9500 and the table section already carries pinned phrases on both sides; if wrong (no room without touching a pinned phrase): trim the equally-unpinned "Load only the phase you are in" lead-in and fold the sentence into it (cost: one lean-fence round)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/agents/` `add-method/src/add_method/_bundled/agents/` `.claude/agents/` `add-method/skill/` `add-method/src/add_method/_bundled/skill/` `.claude/skills/add/` `add-method/tooling/` `.add/tooling/` `add-method/.add/`
Strategy & known-problem fixes: red test_bundle_disclosure -> add-design re-cut -> add-build add-section -> add-verify re-cut -> SKILL.md sentence under ceiling -> sync agents + skill trees -> fence. Traps: bundled agents byte-parity pin · the pinned-phrase census on SKILL.md (trim nothing pinned) · agent Return contracts NEVER change (extend-only rule) · description lines feed the Agent-tool picker (keep capability wording, change only step names).
Approach (domain strategy): disclose don't duplicate — agents point at the SAME guide files the inline lane reads; one source of truth per phase

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (all three agent files + SKILL.md flow section read this session)
- [x] §1 every Must + every Reject present, each paired with its outcome
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (the 145-byte SKILL.md headroom risk)
Verified by: claude-fable-5 (orchestrator, inline) · at: 2026-07-14T02:30:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_each_agent_names_its_bundle_guides · test_no_agent_names_a_deleted_guide_or_retired_step · test_skill_states_the_disclosure_split · test_agents_bundled_parity_after_recut · test_skill_ceiling_held.
Tests live in: `add-method/tooling/test_bundle_disclosure.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned, plus two step-back corrections: the deleted-guide pin had to be PATH-qualified (`phases/2-scenarios.md`) because the docs CHAPTERS keep the old names (docs/04-step-2-scenarios.md lives on — a book pointer is not a guide pointer); and both re-cut agents' native Return enums updated to the merged phases (add-design setup|specify|plan · add-verify verify) — the agent's own file in a sanctioned task, not a spawn-prompt override.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): each roster bundle agent's file names the exact guides it loads at spawn (add-design: 0-setup+1-specify+3-plan · add-build: 4-tests+5-build · add-verify: 6-verify incl the Observe block); no agent names a deleted guide or retired spawn step; SKILL.md states the disclosure split (9442 B ≤ 9500); agents byte-identical canonical↔bundled + .claude refreshed — confirmed by test_bundle_disclosure 6/6 (3 red first) + the FULL fence 3541 tests OK / REAL_EXIT=0 (fence-bd-r1.log, zero ripple beyond the task suite itself, zero tests weakened). Engine untouched (no MD5 re-aim).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

