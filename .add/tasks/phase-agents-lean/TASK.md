# TASK: Lean 3-agent phase roster + adaptive persona agent

slug: phase-agents-lean · created: 2026-07-01 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/agents/` and `.claude/agents/` — do NOT exist on this branch (`feat/artifact-trust`). A 9-agent "phase-agent roster" (`add-setup` … `add-observe`) exists ONLY on a separate, unmerged branch `feat/persona-distillation-depth` (PR #120, commit `a316696`, still OPEN) — confirmed via `git merge-base --is-ancestor a316696 HEAD` -> not an ancestor, and via `ls add-method/agents .claude/agents` -> both absent here. This task builds a NEW, leaner roster directly on this branch rather than merging that foreign branch's work.
  - `add-method/.claude-plugin/plugin.json` — no `"agents"` key; Claude Code plugins auto-discover subagents from an `agents/` dir adjacent to `.claude-plugin/`. Confirmed empirically on the roster branch: the commit that added 9 agent files never touched `plugin.json`.
  - `add-method/tooling/add_engine/engine_manifest.py:package_digest()` / `package_files()` — scoped EXCLUSIVELY to `add_engine/*.py` (globs that dir only). Adding files under `add-method/agents/` does NOT require re-pinning `ENGINE_MD5`/`ENGINE_PKG_MD5` — confirmed by reading the glob directly.
  - `add-method/tooling/add.py:2841-2860` (`_persona_missing`, `_persona_slug_valid` via `add_engine/predicates.py:73-96`) — the engine's OWN persona-schema validator: `.add/personas/*.md` is OPTIONAL/INFO-only (grandfathered if absent), never a hard gate. Schema (`add_engine/constants.py:99-100`): frontmatter keys `name`, `vibe`; required section headers `## Identity`, `## Critical Rules`, `## Default Requirement`, `## Success Metrics`.
  - `.claude/skills/add/phases/0-setup.md:55` — "Seed personas (`.add/personas/`): `init` scaffolds `_template.md` (the schema). Author one per role from PROJECT.md + the vendored teacher library `.add/personas-teacher/` (read off-build; engine never fetches). Covered by the baseline approval; `add.py check` validates; never clobber." — the exact convention the new `add-persona` agent formalizes into a dedicated, adaptive (per-task, not just at-setup) selector/drafter.
  - `.claude/skills/add/advisor.md` (full, 78 lines) — today's ad-hoc single-subagent spawn convention: the worker-contract XML template (`<objective>`/`<persona>`/`<strategy>`/`<context_files>`/`<return>`), the 3-lens verdict recording shape, and "Persona for the refute-read: select a Code-Reviewer persona." No dedicated `add-refute`/`add-advisor`/`add-design`/`add-build`/`add-verify` agent name exists anywhere in git history on any branch (checked via `git log --all -S`).
  - `.claude/skills/add/confidence.md` (32 lines) — the six self-score dimensions (Completeness · Clarity · Practicality · Optimization · Edge cases · Self-evaluation), advisory-only, refine-if-<0.9.
  - `.claude/skills/add/streams.md:152-227` — the portable worker-contract XML (`<touch_boundary>` MAY/MUST NOT/STOP-and-escalate shape; `<return>` structured verdict) and the tier table (`mid` = ordinary/well-tested scope -> `sonnet`-equivalent; `top` = complex/ambiguous/cross-cutting -> `opus`-equivalent).
  - `.claude/skills/add/phases/{0-setup,0-ground,1-specify,2-scenarios,3-contract,4-tests,5-build,6-verify,7-observe}.md` — all 9 read in full; each phase's "Produce"/"AI prompt"/"Exit gate" sections are the single source of truth this task's 4 consolidated agent bodies must faithfully compress from (not re-derive independently).
  - `add-method/tooling/test_skill_lean.py` — pins a frozen per-tree byte BUDGET over `.claude/skills/add/` (an "orchestration" pool including `advisor.md`/`streams.md`); per prior-session convention (`feedback_lean_over_budget_bump`), new prose in that tree must COMPRESS to absorb under the unchanged budget, never grow it, without an explicit human-approved rebaseline. This task does NOT touch any file under `.claude/skills/add/` — it only adds new files under `agents/`, which that budget test does not scan (confirmed: `test_skill_lean.py` enumerates specific `.md` pool files, `agents/*.md` is not among them) — so no rebaseline is needed, and updating `advisor.md` to cross-reference the new roster is explicitly OUT of this task's scope (see Reject).
Context (working folder): `add-method/agents/` (new dir) · `.claude/agents/` (new dir, mirror) · a new `add-method/tooling/test_agent_roster.py` (parity/shape test, sibling convention to the roster branch's `test_phase_agents.py`, read via `git show feat/persona-distillation-depth:add-method/tooling/test_phase_agents.py` for its exact invariant shapes — NOT copied verbatim, since this roster has 4 agents not 9).
Honors (patterns / conventions): the EXACT frontmatter/body shape used by the (foreign-branch) phase-agent roster — `name`/`description`/`model: inherit`/`color`, then `## Become the persona` → `## What you own` → `## Boundary (the irreducible floor)` → `## Self-improve before you return` → `## Return (disclose progress)` → a `Method depth:` footer line — reused here so a future merge of that branch's 9-agent set and this branch's 3+1-agent set stays visually/structurally consistent even though they group phases differently. Reuses `streams.md`'s `MAY`/`MUST NOT`/`STOP-and-escalate` boundary vocabulary verbatim. Reuses `confidence.md`'s six-dimension self-score verbatim.
Anchors the contract cites: `add-method/agents/add-design.md` · `add-method/agents/add-build.md` · `add-method/agents/add-verify.md` · `add-method/agents/add-persona.md` · their 4 byte-identical `.claude/agents/` mirrors · `add-method/tooling/test_agent_roster.py`.
Issues/Risks (→ feed §1):
  - **grouping choice already made by the human**: setup+ground+specify+scenarios+contract → `add-design`; tests+build → `add-build`; verify+observe → `add-verify`; a 4th, cross-cutting `add-persona` for adaptive persona selection/drafting (confirmed via AskUserQuestion: "3-way: Design / Build / Verify" + the persona agent, both explicit).
  - **`add-persona` is unlike the other 3** — it is not one phase-worker among nine, but a cross-cutting SERVICE the other 3 (or the orchestrator) can consult mid-phase ("which persona should this piece adopt?"). Its boundary must mirror the "never clobber" rule from `0-setup.md` (write a NEW `.add/personas/<slug>.md` only when none exists; never overwrite).
  - **no re-pin needed** — confirmed `engine_manifest.package_digest()` never globs `agents/`; `ENGINE_MD5`/`ENGINE_PKG_MD5` stay untouched by this task.
  - **advisor.md cross-reference deferred** — a short "spawn one of these instead of the generic ad-hoc template" pointer in `advisor.md` would be a nice-to-have, but touching that file re-opens the lean-budget compaction dance (`test_skill_lean.py`) for a non-essential addition; deferred to a future SPEC delta rather than scope-creeping this task (see Reject: `scope_creep_skill_or_engine`).
Related intent: user, mid-session (2026-07-01, while the `ci-tooling-mirror-gap` refute-read subagent ran in the background): "meanwhile, you should add ADD agents for Refute/advisor tasks" → discovered the 9-phase roster this would extend doesn't exist on this branch (only on unmerged `feat/persona-distillation-depth`) → user, via AskUserQuestion follow-up note: "are can we combine & optimize all agent in to single agent for all phases" → then explicit follow-up message: "we will just need 2-3 agents for all phases and a specific agent for personas in adaptive" → confirmed grouping via AskUserQuestion: "3-way: Design / Build / Verify (Recommended)".
Ground SHA: c22a43c

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: ADD ships a lean 4-agent roster as a registered Claude Code plugin surface — `add-design` (setup → ground → specify → scenarios → contract), `add-build` (tests → build), `add-verify` (verify → observe), and `add-persona` (a cross-cutting adaptive persona selector/drafter the other 3 — or the orchestrator — can consult mid-phase). Auto-discovered from `add-method/agents/`, mirrored byte-identically into `.claude/agents/` for this repo's own dogfooding, spawned as `add:add-<name>` (plugin) or bare `add-<name>` (project copy).
Framings weighed: **chosen — 3 phase-group agents + 1 cross-cutting persona agent**, confirmed twice via AskUserQuestion (grouping: "3-way: Design / Build / Verify") · 9 separate one-per-phase agents, mirroring the unmerged `feat/persona-distillation-depth` roster (rejected by the user directly: "we will just need 2-3 agents for all phases") · 1 single mega-agent covering all 9 phases + persona duties (considered per the user's own follow-up note "can we combine & optimize all agent in to single agent for all phases" — rejected in favor of the 3+1 split because the 2 human-gated boundaries — the contract freeze and an escalated verify — sit at different points in the flow than a single agent could honor cleanly: `add-design` must STOP at the freeze (never self-approve), `add-build` must STOP on a scope/contract gap, `add-verify` must STOP on any security finding; collapsing all three into one agent blurs exactly the STOP-and-escalate boundaries `streams.md`/`run.md` treat as load-bearing) · pulling in the foreign branch's 9-agent commit first (considered, rejected — unrelated branch history, and the user's own direction moved past a 9-agent shape entirely once informed it doesn't exist here).
Must:
<must>
  - M1: `add-method/agents/add-design.md` covers phases setup+ground+specify+scenarios+contract — drafts the foundation (brownfield-silent or greenfield 4-lens interview) and the full specification bundle (§0 GROUND → §1 SPECIFY → §2 SCENARIOS → §3 CONTRACT), ranks the bundle-wide lowest-confidence flag, and presents the freeze as a decision for the human — it drafts, it never self-approves the freeze.
  - M2: `add-method/agents/add-build.md` covers phases tests+build — writes one executable test per scenario, confirms RED for the right reason, then implements until every test is green, honoring the frozen §5 Scope/Strategy, never touching a test or the frozen contract.
  - M3: `add-method/agents/add-verify.md` covers phases verify+observe — confirms evidence against the pre-declared §6 Build expectations, runs the security→concurrency→architecture 3-lens checklist (security HARD-STOP ends it), runs the earned-green adversarial refute-read, records exactly one GATE RECORD outcome, then (observe) proposes release/monitors and drafts the next SPEC delta.
  - M4: `add-method/agents/add-persona.md` — a cross-cutting service agent: given a piece of work's domain, selects the best-fit existing `.add/personas/<slug>.md`, or drafts a NEW one (schema: frontmatter `name`/`vibe`; sections `## Identity`/`## Critical Rules`/`## Default Requirement`/`## Success Metrics`, sourced from PROJECT.md + the vendored `.add/personas-teacher/` library) when none fits — never overwriting an existing persona file. Returns the chosen/drafted slug + a one-line rationale for the calling agent to load and become.
  - M5: all 4 files are mirrored byte-identically into `.claude/agents/` (the same 2-tree convention the (foreign-branch) phase-agent roster used) — 8 files total.
  - M6: every one of the 4 agent bodies carries the SAME shared worker-contract markers (case-insensitive substring, mirroring the foreign branch's own `test_phase_agents.py::SharedContractTest` invariant, adapted): `.add/personas` (or the persona-specific equivalent for `add-persona` itself), `hard-stop`, `security`, `weaken`, `frozen contract`, `confidence`, `return`, `.add/docs`.
  - M7: a new `add-method/tooling/test_agent_roster.py` pins: presence in both trees, frontmatter shape (`name` == `add-<agentname>`, non-empty `description`, `model` absent-or-one-of `inherit|sonnet|opus|haiku|fable`), the M6 shared-contract markers, each agent naming its own phases, byte-identical parity across the 2 trees, and NO stray `add-*.md` file beyond the declared 4.
  - M8: `add-method/tooling/engine_pin.py`'s `ENGINE_MD5`/`ENGINE_PKG_MD5` are UNCHANGED (confirmed: neither pin's digest scans `agents/`).
</must>
Reject:
<reject>
  - an agent frontmatter's `name` does not exactly match its filename stem (`add-<agentname>`) -> "agent_name_mismatch"
  - `add-method/agents/` and `.claude/agents/` diverge (not byte-identical) for any of the 4 files -> "agent_roster_drift"
  - a 5th/stray `add-*.md` file appears in either tree beyond the declared 4 -> "agent_roster_stray"
  - `add-design.md` (or any agent) contains language implying it can itself mark §3 `Status: FROZEN` without a human decision -> "agent_self_approves_freeze"
  - `add-persona.md`'s body allows overwriting an EXISTING `.add/personas/<slug>.md` -> "persona_agent_clobbers"
  - this task edits any file under `.claude/skills/add/` (e.g. `advisor.md`) or re-pins `ENGINE_MD5`/`ENGINE_PKG_MD5` -> "scope_creep_skill_or_engine"
</reject>
After:
<after>
  - a user (or the orchestrator) can `Task(subagent_type="add:add-design")` (plugin) or `Task(subagent_type="add-design")` (this repo's dogfood copy) to delegate the whole direction-setting span up to the frozen contract; `add-build` to delegate red→green; `add-verify` to delegate the evidence/3-lens/refute-read/gate span; `add-persona` to delegate "which persona fits this piece" from any of the other 3 or from the main conversation. All 4 ship in the plugin (auto-discovered, no `plugin.json` edit) and are mirrored for this repo's own dogfooding. `ENGINE_MD5`/`ENGINE_PKG_MD5` unchanged; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the shared worker-contract markers (M6) — lifted from the foreign branch's own `test_phase_agents.py` pattern — are the right invariant to enforce for a DIFFERENT (3+1, not 9) grouping; lowest confidence because that pattern was designed for one-agent-per-phase, and `add-design`/`add-build`/`add-verify` each now span MULTIPLE phases while `add-persona` isn't a phase-worker at all. If wrong: a marker chosen for phase-granularity (e.g. "names its own phase") may not cleanly generalize to a multi-phase or non-phase agent. Mitigate: `test_agent_roster.py`'s "each agent names its own phases" check uses a LIST of phase-name substrings per agent (not a single phase name), and `add-persona` is exempted from that specific check (it names no ADD phase) while still carrying the other shared markers.
  - [x] no `plugin.json` edit needed for auto-discovery — confirmed empirically (the foreign branch's commit never touched it) and by the absence of an `"agents"` key today.
  - [x] no `ENGINE_MD5`/`ENGINE_PKG_MD5` re-pin needed — confirmed by reading `engine_manifest.py`'s glob directly (scoped to `add_engine/*.py` only).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: add-design covers the direction span and never self-approves the freeze   # M1
  Given add-method/agents/add-design.md
  When its body is read in full
  Then it names setup, ground, specify, scenarios, and contract as phases it owns
   And it drafts the bundle-wide lowest-confidence flag and presents the freeze as a
       decision for the human — no sentence claims it can itself mark Status: FROZEN

Scenario: add-build covers tests+build and honors the frozen scope   # M2
  Given add-method/agents/add-build.md
  When its body is read in full
  Then it names tests and build as the phases it owns
   And it states one executable test per scenario, RED-for-the-right-reason before
       green, and a MUST NOT clause against touching a test or the frozen contract

Scenario: add-verify covers verify+observe with the full evidence chain   # M3
  Given add-method/agents/add-verify.md
  When its body is read in full
  Then it names verify and observe as the phases it owns
   And it states the security → concurrency → architecture 3-lens order (security
       HARD-STOP ends it), the earned-green refute-read, exactly one GATE RECORD
       outcome, and (for observe) release/monitors + the next SPEC delta

Scenario: add-persona selects or drafts without ever overwriting   # M4
  Given add-method/agents/add-persona.md and an existing `.add/personas/backend.md`
  When the body is read in full
  Then it states it selects the best-fit existing persona OR drafts a NEW file
       (frontmatter name/vibe; sections Identity/Critical Rules/Default
       Requirement/Success Metrics) only when none fits
   And it states it returns a slug + one-line rationale, never overwriting an
       existing persona file

Scenario: the 4-file roster mirrors byte-identically into .claude/agents/   # M5
  Given the 4 files under add-method/agents/ and their .claude/agents/ counterparts
  When each pair is diffed
  Then all 4 pairs are byte-identical
   And exactly 8 files exist across the two trees (4 + 4)

Scenario: every agent body carries the shared worker-contract markers   # M6
  Given each of the 4 agent bodies
  When scanned case-insensitively for the shared marker set
  Then each contains `.add/personas` (or its persona-specific equivalent for
       add-persona), `hard-stop`, `security`, `weaken`, `frozen contract`,
       `confidence`, `return`, and `.add/docs`

Scenario: test_agent_roster.py enforces the roster's shape   # M7
  Given add-method/tooling/test_agent_roster.py
  When `python3 -m unittest test_agent_roster -v` runs
  Then presence, frontmatter (name == add-<agentname>, non-empty description,
       model absent-or-one-of inherit|sonnet|opus|haiku|fable), the M6 markers,
       each agent naming its own phase(s), 2-tree parity, and no stray add-*.md
       beyond the declared 4 all pass

Scenario: the engine pins stay untouched   # M8
  Given add-method/tooling/engine_pin.py before and after this build
  When ENGINE_MD5 and ENGINE_PKG_MD5 are compared
  Then both values are byte-identical to their pre-build state
   And the full add-method test suite still reports OK

Scenario: a frontmatter name that does not match its filename is rejected
  Given add-design.md declares `name: add-designer` instead of `add-design`
  When test_agent_roster.py's frontmatter test runs
  Then it fails with "agent_name_mismatch"
   And the other 3 agent files are unaffected

Scenario: a drifted mirror between the two trees is rejected
  Given `.claude/agents/add-build.md` differs by even one byte from
        `add-method/agents/add-build.md`
  When test_agent_roster.py's parity test runs
  Then it fails with "agent_roster_drift"
   And no other agent pair is reported

Scenario: a 5th stray agent file is rejected
  Given a file `add-method/agents/add-refute.md` appears alongside the declared 4
  When test_agent_roster.py's presence test runs
  Then it fails with "agent_roster_stray"
   And the declared 4 files remain valid and unaffected

Scenario: an agent claiming self-approval authority over the freeze is rejected
  Given add-design.md's body contains a sentence implying it can mark
        `Status: FROZEN` without a human decision
  When test_agent_roster.py's boundary test runs
  Then it fails with "agent_self_approves_freeze"
   And add-build.md / add-verify.md / add-persona.md are unaffected

Scenario: a persona agent that allows clobbering an existing file is rejected
  Given add-persona.md's body permits overwriting an EXISTING
        `.add/personas/<slug>.md`
  When test_agent_roster.py's boundary test runs
  Then it fails with "persona_agent_clobbers"
   And the other 3 agent files are unaffected

Scenario: touching the skill tree or re-pinning the engine is rejected
  Given this task's diff touches a file under `.claude/skills/add/` (e.g.
        advisor.md) or edits ENGINE_MD5/ENGINE_PKG_MD5 in engine_pin.py
  When the build is reviewed against its declared §5 Scope
  Then it is rejected with "scope_creep_skill_or_engine"
   And `.claude/skills/add/` and the engine pins remain exactly as they were
       before this task started
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
phase-agents-lean — frozen shape @ v1

add-method/agents/add-design.md — new file. Frontmatter:
  name: add-design
  description: the ADD design specialist — drafts the whole direction span
    (foundation/ground map through the frozen contract) to the one human
    freeze decision. Recommended tier — top.
  model: inherit
  color: blue
Body, condensed from phases/{0-setup,0-ground,1-specify,2-scenarios,3-contract}.md,
exact section order:
  opening role paragraph naming all 5 phases it owns (setup, ground, specify,
    scenarios, contract)
  ## Become the persona
  ## What you own (the design span)
  ## Boundary (the irreducible floor)
  ## Self-improve before you return
  ## Return (disclose progress)
  Method depth: the AIDD book in .add/docs/ — 02-the-flow.md ·
    03-step-1-specify.md · 04-step-2-scenarios.md · 05-step-3-contract.md.
Boundary MUST explicitly state it drafts the freeze and never marks the
  contract's Status line as FROZEN itself — that is always the human's decision.

add-method/agents/add-build.md — new file. Frontmatter: name: add-build,
  color: green, same field set. Body condensed from phases/{4-tests,5-build}.md,
  same section order, owns tests -> build. States: one executable test per
  scenario, RED for the right reason, then green without touching a test or
  the frozen contract.

add-method/agents/add-verify.md — new file. Frontmatter: name: add-verify,
  color: red, same field set. Body condensed from phases/{6-verify,7-observe}.md,
  same section order, owns verify -> observe. States: fill/confirm the §6
  Build expectations against real evidence, the security -> concurrency ->
  architecture 3-lens order (security HARD-STOP ends it), the earned-green
  refute-read (EARNED | NOT-EARNED), exactly one GATE RECORD outcome, then
  (observe) release/monitors + the next SPEC delta.

add-method/agents/add-persona.md — new file. Frontmatter: name: add-persona,
  color: purple, same field set (description notes it is a cross-cutting
  SERVICE, not a phase-worker). Body:
  opening role paragraph: selects or drafts the best-fit persona for a piece
    of work, on request from any of the other 3 agents or the orchestrator
  ## Become the persona — reworded (no self-referential regress): reads
    PROJECT.md + the vendored `.add/personas-teacher/` library to judge fit,
    rather than loading a persona for itself
  ## What you own (persona selection/drafting) — the schema (frontmatter
    name/vibe; sections Identity/Critical Rules/Default Requirement/Success
    Metrics) and the never-clobber rule from 0-setup.md
  ## Boundary (the irreducible floor) — MAY select an existing persona or
    draft a brand-new file; MUST NOT overwrite an existing
    `.add/personas/<slug>.md`; STOP-and-escalate if PROJECT.md gives no
    usable domain signal to draft from
  ## Self-improve before you return
  ## Return (disclose progress) — { phase: persona, slug, drafted: bool,
    rationale, confidence, open_questions }
  Method depth: the AIDD book in .add/docs/ — 0-setup.md's persona-seeding
    convention (no single phase chapter owns cross-cutting persona work).

Each of the 4 files above is mirrored byte-identical into `.claude/agents/`
(8 files total across the 2 trees).

add-method/tooling/test_agent_roster.py — new file. Adapted from
feat/persona-distillation-depth's test_phase_agents.py (NOT copied verbatim —
that fixture keys everything off one-agent-per-phase; this one keys off
AGENTS = ("design", "build", "verify", "persona") plus a PHASES-per-agent map,
e.g. design -> {setup, ground, specify, scenarios, contract}):
  - RosterPresenceTest — all 4 files exist in both trees; each tree's
    `add-*.md` glob equals exactly the declared 4 names (no 5th/stray)
  - FrontmatterTest — name == add-<agentname>, lowercase+hyphen regex,
    non-empty description, model absent-or-one-of
    inherit|sonnet|opus|haiku|fable
  - SharedContractTest — every body contains (case-insensitive) all 8 M6
    markers (.add/personas, hard-stop, security, weaken, frozen contract,
    confidence, return, .add/docs); add-design/add-build/add-verify each
    name every phase in their own PHASES-per-agent list; add-persona is
    exempted from the phase-name check (documented in-test — it owns no ADD
    phase) but still asserted for every M6 marker
  - BoundaryTest — add-design's body contains no phrase implying it can
    itself mark `Status: FROZEN`; add-persona's body states it never
    overwrites an existing persona file
  - ParityTest — byte-identical across the 2 trees for all 4 files

Invariants: `ENGINE_MD5`/`ENGINE_PKG_MD5` in both `engine_pin.py` copies
receive NO edits; no file under `.claude/skills/add/` is touched;
`add-method/.claude-plugin/plugin.json` receives no edits (auto-discovery,
confirmed at GROUND); full add-method test suite green.
```

Least-sure flag surfaced at freeze: [spec] whether the shared worker-contract markers
(M6) — designed on the foreign branch for one-agent-per-phase — generalize cleanly to
this task's multi-phase (add-design/add-build/add-verify) and non-phase (add-persona)
grouping. Cost if wrong: a marker/check chosen for phase-granularity may need a re-freeze
once test_agent_roster.py is actually written; low functional risk since M6 is additive
prose requirements, not behavior.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the frozen §3 shape (presence · frontmatter · shared markers · phase-naming · boundary phrasing · 2-tree parity) — a prose/config roster, not a code path with branch coverage.
Plan (one test class per scenario group, asserting body content not internals):
<test_plan>
  - RosterPresenceTest.test_all_four_agents_exist_in_both_trees: arrange nothing (fresh repo state) / act glob for `add-{design,build,verify,persona}.md` in both trees / assert all 8 files exist (M1-M5)
  - RosterPresenceTest.test_no_stray_agents_in_roster: arrange the declared 4-name set / act glob `add-*.md` per tree / assert the glob equals exactly the 4 (Reject: agent_roster_stray)
  - FrontmatterTest.test_required_frontmatter_fields: arrange each agent file's frontmatter / act parse `name`/`description`/`model` / assert `name == add-<agent>`, lowercase+hyphen, non-empty description, model absent-or-known-tier (M7, Reject: agent_name_mismatch)
  - SharedContractTest.test_each_agent_carries_the_worker_contract: arrange each body lower-cased / act scan for the 8 M6 markers / assert all 8 present per agent (M6)
  - SharedContractTest.test_each_agent_names_its_phases: arrange the AGENT_PHASES map / act scan add-design/add-build/add-verify bodies / assert each names every phase in its own list; add-persona exempted (M1-M3)
  - BoundaryTest.test_add_design_never_self_approves_freeze: arrange add-design's body / act regex-search for a "never marks ... FROZEN" phrase / assert present (Reject: agent_self_approves_freeze)
  - BoundaryTest.test_add_persona_never_clobbers: arrange add-persona's body / act regex-search for a "never overwrites an existing" phrase / assert present (Reject: persona_agent_clobbers)
  - ParityTest.test_roster_byte_identical_across_trees: arrange both trees' 4 files / act diff by content / assert byte-identical (M5, Reject: agent_roster_drift)
</test_plan>

Tests live in: `add-method/tooling/test_agent_roster.py` · confirmed red (8 tests: 2 failures + 6 errors, all `FileNotFoundError`/`AssertionError` on missing `add-method/agents/add-*.md` — the right reason, no implementation exists yet) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/agents` · `.claude/agents` · `add-method/tooling/test_agent_roster.py`
Strategy (ordered batches): 1. write `add-method/agents/add-design.md` (setup..contract span) 2. `add-method/agents/add-build.md` (tests+build) 3. `add-method/agents/add-verify.md` (verify+observe) 4. `add-method/agents/add-persona.md` (cross-cutting persona service) — each condensed from its phase guide(s) + the shared worker-contract shape (Become the persona → What you own → Boundary → Self-improve → Return → Method depth) 5. copy all 4 byte-identical into `.claude/agents/` 6. run `test_agent_roster.py` + the full add-method suite, iterate until green.

Persona (optional): none seeded for this build (method/tooling authorship, not a domain feature) — generic technical-writer-engineer stance atop SOUL.md.
Known-problem fixes: risk of an agent body accidentally re-deriving phase-guide prose instead of compressing it (bloat) → lift verbatim from `phases/*.md` "Produce"/"AI prompt" language, condensed not rewritten from scratch. risk of `add-persona`'s "Become the persona" section causing self-referential regress (a persona-selector selecting a persona for itself) → reworded per §3: it reads PROJECT.md + `.add/personas-teacher/` directly rather than loading a fit persona for itself.
Strategy actually used: as planned.
Safety rule (feature-specific): none (no runtime/data-mutating code — this build only adds static prompt/config markdown + a test file).
Code lives in: `add-method/agents/` (+ `.claude/agents/` mirror) · `add-method/tooling/test_agent_roster.py`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full add-method suite: 2586 tests, `OK` (refute-read subagent's independent full-suite run confirms this, not just the 8 new tests)
- [x] coverage did not decrease — +8 new tests (`test_agent_roster.py`), 0 removed/skipped
- [x] no test or contract was altered during build — `git diff --stat` confirms only new files under `add-method/agents/`, `.claude/agents/`, `add-method/tooling/test_agent_roster.py`
- [x] the green was EARNED, not gamed — refute-read subagent (agent-id `a4143805c9ecf9415`) mutated all 4 axes and confirmed each reject-code fires; verdict EARNED (see Refute-read verdict below)
- [x] concurrency / timing of the risky operation is safe — n/a, static prompt/config markdown + a pure-content unittest, no concurrent/async/timing-sensitive code introduced
- [x] no exposed secrets, injection openings, or unexpected dependencies — CLEAR, no new dependency, no secret, no I/O beyond reading existing repo files
- [x] layering & dependencies follow CONVENTIONS.md — follows the established `agents/` mirror-pair convention and the sibling `tooling/test_*.py` pattern; no new coupling introduced
- [x] a person reviewed and approved the change — auto-resolved under `autonomy: auto` (no residue); reviewed by Tin Dang at the gate below

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] each of the 4 new agent bodies, read start to finish, states its own owned phase(s) in
      plain prose (not merely as a frontmatter/filename tag) — confirmed by manual read of all 4.
- [x] add-design's Boundary section names the contract freeze as always the human's decision,
      never its own — confirmed by manual read.
- [x] add-persona's body states it never overwrites an existing persona file, and its "Become
      the persona" section avoids the self-referential regress flagged in §0 Issues/Risks (a
      persona-selector selecting a persona for itself) — confirmed by manual read.
- [x] the 4 files are truly byte-identical across `add-method/agents/` and `.claude/agents/` —
      confirmed independently of the unittest via a shell `diff -q` (zero output = identical).
- [x] `ENGINE_MD5`/`ENGINE_PKG_MD5` (both copies), `add-method/.claude-plugin/plugin.json`, and
      every file under `.claude/skills/add/` are untouched — confirmed via `git diff --stat` on
      those exact paths (zero output).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — all 4 agent bodies read in full, twice (once while drafting
      against the phase guides they condense, once again at verify against the frozen §3 shape
      and the M6/boundary invariants); confirmed each names its phases, carries all 8 shared
      markers, and states its specific boundary rule (self-approval / clobber) in real prose,
      not just a keyword dropped in isolation.
- [ ] WIRING (code) — n/a, no executable src beyond the test file (see test_agent_roster.py's
      own green run as its wiring proof)
- [ ] DEAD-CODE (code) — n/a, no executable src beyond the test file

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent-id `a4143805c9ecf9415` · adversarially checked: mutated 4 scratch-copied artifacts across the
4 highest-risk axes and confirmed each corresponding reject-code fires — a renamed frontmatter `name`
(`agent_name_mismatch`), a 1-byte mirror drift (`agent_roster_drift`), a stray 5th agent file
(`agent_roster_stray`), and a diluted self-approval sentence (`agent_self_approves_freeze` correctly
still failed, proving the regex doesn't false-positive on adjacent boilerplate). Read all 32 M6-marker
instances (8 markers × 4 files) in situ — none is an isolated keyword drop. Confirmed exactly one
`FROZEN` hit across all 4 files (the correct non-self-approving sentence, no contradiction elsewhere).
Independently re-verified byte-parity via plain shell `diff` (not the unittest). Confirmed scope
discipline via `git status --porcelain -uall` + `git diff HEAD` (only declared paths touched; engine
pins, `plugin.json`, and `.claude/skills/add/` show zero diff). Ran the full suite: 2586 tests, `OK`.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — no new dependency, no secret, no runtime/data-mutating code; static prompt/config
   markdown + a pure-content unittest only.
2. Concurrency: CLEAR — no concurrent, async, or timing-sensitive code introduced.
3. Architecture: CLEAR — follows the established `agents/` mirror-pair convention (2 trees) and the
   sibling `tooling/test_*.py` pattern; no new coupling; confirmed `engine_manifest.py`'s digest globs
   never scan `agents/` so `ENGINE_MD5`/`ENGINE_PKG_MD5` stay correctly unpinned by this change.
Verdict: PASS
Residue: none
Binding: advisory — mechanical (no `risk: high` declared; prose/config-only change, not routed through
  the high-risk gate-relax path)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-resolved under `autonomy: auto` — no residue: no security/concurrency/
  architecture finding; refute-read EARNED via adversarial subagent, independently corroborated by a
  full 2586-test suite run) · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned.
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-resolved under `autonomy: auto` — no residue: no security/concurrency/)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

