# TASK: add-advisor consultative frontier-model agent (5th roster agent)

slug: add-advisor · created: 2026-07-02 · stage: mvp · risk: high · sensitivity: architecture
milestone: (none)
autonomy: conservative
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/agents/add-advisor.md` — NEW file. The 5th roster agent. Frontmatter shape read from `add-method/agents/add-design.md` (the "top tier" sibling): keys `name` / `description` / `model` / `color`, then body sections `## Become the persona` → `## What you own` → `## Boundary (the irreducible floor)` → `## Self-improve before you return` → `## Return (disclose progress)` → a `Method depth:` footer. UNLIKE the 4 current agents (all `model: inherit`), this one declares `model: opus` (the human wants a frontier model for medium-hard advice).
  - `.claude/agents/add-advisor.md` — NEW file, byte-identical mirror (the 2-tree convention every roster agent holds — plugin `add-method/agents/` auto-discovered + repo `.claude/agents/` dogfood).
  - `add-method/tooling/test_agent_roster.py:24` `AGENTS = ("design", "build", "verify", "persona")` — must become `(..., "advisor")`. This is the single tuple that drives `RosterPresenceTest.test_all_four_agents_exist_in_both_trees`, `test_no_stray_agents_in_roster` (asserts the `add-*.md` glob == exactly the declared set → today REJECTS a 5th file with `agent_roster_stray`), `FrontmatterTest`, `SharedContractTest`, `ParityTest`.
  - `add-method/tooling/test_agent_roster.py:28` `AGENT_PHASES = {...}` — must gain `"advisor": ()` (empty tuple). `add-advisor` owns NO ADD phase (consultative, like `add-persona`'s `()`), so the empty tuple exempts it from `SharedContractTest.test_each_agent_names_its_phases` (that method `continue`s on a falsy tuple). Missing this key = KeyError at test time.
  - `add-method/tooling/test_agent_roster.py:CONTRACT_MARKERS` — the 8 shared-contract markers (`.add/personas`, `hard-stop`, `security`, `weaken`, `frozen contract`, `confidence`, `return`, `.add/docs`) `add-advisor.md` must all carry (case-insensitive), same as every roster agent.
  - `add-method/tooling/test_agent_roster.py:BoundaryTest` — needs a NEW per-agent boundary test for advisor (siblings: `test_add_design_never_self_approves_freeze`, `test_add_persona_never_clobbers`). Advisor's invariant: it ADVISES but never decides/records/edits, and never lowers a gate (security advice still HARD-STOPs).
  - `add-method/tooling/test_agent_roster.py:2` — the module docstring says "LEAN 4-agent roster … (add-design, add-build, add-verify, add-persona)"; update to 5 naming advisor + its consultative role.
Context (working folder):
  - `.claude/skills/add/advisor.md` (78 lines) — today's guide means "spawn ONE subagent to EXECUTE a piece of the orchestrator's plan and return a verdict" — a DIFFERENT concept from a consultative advisor. NAMING COLLISION to disclose (→ §1). DEFERRED out of scope this task (matches how `phase-agents-lean` deferred the advisor.md cross-reference as a future SPEC delta) to avoid re-opening the `test_skill_lean` byte budget.
  - `.claude/skills/add/confidence.md` — the six self-score dimensions (Completeness · Clarity · Practicality · Optimization · Edge cases · Self-evaluation), advisory, refine-if-<0.9 — the `confidence` marker source.
  - `.add/tasks/phase-agents-lean/TASK.md` — the FROZEN @ v1 contract that shipped the lean-4 roster; its §3 + §2 (scenario "a 5th stray agent file is rejected") + Reject `agent_roster_stray` are the invariant this task deliberately extends 4→5.
Honors (patterns / conventions):
  - CONVENTIONS/PROJECT: the 2-tree byte-identical `agents/` mirror convention; a registered phase agent mirrors its guide (but advisor owns no phase — it is a cross-cutting SERVICE like `add-persona`); the shared worker-contract markers; `confidence.md` six-dimension self-score verbatim; `streams.md` MAY/MUST NOT/STOP-and-escalate boundary vocabulary.
  - the irreducible floor every agent holds: never weaken/skip a test · never edit a frozen contract · a SECURITY finding is always HARD-STOP · PROPOSE, never write shared state (never run add.py).
Anchors the contract cites: `add-method/agents/add-advisor.md` · `.claude/agents/add-advisor.md` (mirror) · `add-method/tooling/test_agent_roster.py` (`AGENTS`, `AGENT_PHASES`, `CONTRACT_MARKERS`, `BoundaryTest`).
Issues/Risks (→ feed §1):
  - **Frozen-invariant extension (the headline flag).** `phase-agents-lean` froze "exactly 4" three ways (the `test_no_stray_agents_in_roster` equality, the `agent_roster_stray` reject code, an explicit "5th stray agent rejected" scenario). Adding `add-advisor` is DECLARED spec-evolution of that invariant (4→5), re-frozen at THIS task's contract gate — not a silent test edit in build. This is the human's decision at the freeze.
  - **Naming collision** with `.claude/skills/add/advisor.md` (executor-subagent) vs. the consultative `add-advisor` agent — disclosed, advisor.md touch deferred (see Context).
  - **Model tier is a first for the roster** — `model: opus` (all 4 current agents use `inherit`). The `FrontmatterTest` already allows `opus` in its known-tier set, so no test change is needed for the tier itself.
  - **Engine pins do NOT move** — confirmed by reading `add-method/tooling/engine_manifest.py:package_files()` (globs `add_engine/*.py` ONLY, never `agents/`) and `engine_pin.py` (`ENGINE_MD5 = md5(add.py)`, untouched). `test_skill_lean.py`'s pools are `.claude/skills/add/*` guides only — `agents/` is not scanned, so no byte-budget rebaseline.
  - **Role boundary vs. add-verify** — advisor advises on DECISIONS; it does NOT absorb add-verify's earned-green refute-read (that stays with verify). Keep them distinct.
Related intent: PROJECT.md goal "any agent drives the CLI loop while the human owns direction/verification" — an on-demand frontier advisor helps a driving agent make medium-hard calls without lowering any human gate. Origin: user (2026-07-01, phase-agents-lean §0) "add ADD agents for Refute/advisor tasks" → consolidated to lean-4, advisor cross-ref DEFERRED as a SPEC delta → user (2026-07-02) explicit follow-up: "new add-advisor agent (in frontier model like opus to get advise when need for medium-hard cases — capture idea from claude code advisor)".
Ground SHA: b75eed6

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: ADD ships a 5th roster agent — `add-advisor`: a CONSULTATIVE, frontier-model (`model: opus`) agent any phase agent or the orchestrator can spawn on demand for a medium-hard decision. Given a situation + context, it returns ADVICE — a recommendation, the tradeoffs/alternatives weighed, risks/edge-cases, and a confidence self-score (modeled on Claude Code's advisor tool). It executes nothing, records nothing, edits nothing, and never lowers a gate. It owns NO ADD phase (a cross-cutting service, like `add-persona`).
Framings weighed: consultative advisor — sees the situation/context, returns advice + tradeoffs + a recommendation, executes/records/edits nothing, `model: opus` (chosen — the plain reading of "get advise for medium-hard cases" + "capture idea from claude code advisor") · executor-subagent formalized — the existing `advisor.md` "spawn one subagent to EXECUTE a plan piece" pattern as a registered agent (rejected: `advisor.md` already covers execution-delegation; the user wants ADVICE, not execution) · absorb add-verify's earned-green refute-read into add-advisor (rejected: adversarial verification stays with add-verify; the advisor advises on decisions, it is not a verifier).
Must:
<must>
  - M1: `add-method/agents/add-advisor.md` exists — a NEW roster agent carrying the shared body shape used by all roster agents: an opening role paragraph, then `## Become the persona` -> `## What you own` -> `## Boundary (the irreducible floor)` -> `## Self-improve before you return` -> `## Return (disclose progress)` -> a `Method depth:` footer. Frontmatter: `name: add-advisor`, a non-empty `description`, `model: opus`, `color`.
  - M2: the body states add-advisor is CONSULTATIVE — given a decision/situation + context it returns a recommendation, the tradeoffs/alternatives weighed, risks/edge-cases, and a confidence self-score; it owns NO ADD phase and is spawnable on demand from any phase or the orchestrator (a cross-cutting service, like add-persona). It states it advises on DECISIONS and does NOT perform add-verify's earned-green refute-read.
  - M3: the body carries the SAME 8 shared worker-contract markers (case-insensitive): `.add/personas`, `hard-stop`, `security`, `weaken`, `frozen contract`, `confidence`, `return`, `.add/docs`.
  - M4: the Boundary section states add-advisor ADVISES but never DECIDES — it never runs add.py or writes shared state (state.json, MILESTONE.md, a sibling's files), never edits a test or the frozen contract, and NEVER lowers a gate: a SECURITY finding it surfaces is always HARD-STOP, and high-risk scope still escalates to the human whatever the advice.
  - M5: the file is mirrored byte-identically into `.claude/agents/add-advisor.md` (the 2-tree convention every roster agent holds — 10 agent files total across the 2 trees).
  - M6: `add-method/tooling/test_agent_roster.py` is extended so the roster is now FIVE: `AGENTS` gains `"advisor"`; `AGENT_PHASES` gains `"advisor": ()` (owns no phase — exempt from the phase-naming check, like persona); the module docstring updates 4->5 naming advisor + its consultative role; and a NEW `BoundaryTest.test_add_advisor_advises_never_decides` asserts the body states it advises but never decides/records/edits (mirroring the design/persona boundary tests). All existing roster tests (presence, frontmatter, shared markers, 2-tree parity, no-stray) then pass for 5 agents.
  - M7: `model: opus` is accepted by `FrontmatterTest` unchanged (`opus` is already in its known-tier set `inherit|sonnet|opus|haiku|fable`) — no frontmatter-test edit for the tier itself.
  - M8: `ENGINE_MD5`/`ENGINE_PKG_MD5` (both copies) UNCHANGED; no file under `.claude/skills/add/` touched (advisor.md cross-reference deferred); `add-method/.claude-plugin/plugin.json` untouched (auto-discovery); full add-method suite green.
</must>
Reject:
<reject>
  - a 6th/stray `add-*.md` file appears in either tree beyond the declared 5 -> "agent_roster_stray"
  - `add-method/agents/add-advisor.md` and its `.claude/agents/` mirror diverge (not byte-identical) -> "agent_roster_drift"
  - `add-advisor.md` frontmatter `name` != its filename stem `add-advisor` -> "agent_name_mismatch"
  - `add-advisor.md` is missing any of the 8 shared worker-contract markers -> (SharedContractTest failure)
  - `add-advisor.md` body implies it can DECIDE / record state / edit a test-or-contract, or lower a gate (auto-pass a security finding) -> "advisor_decides"
  - this task edits any file under `.claude/skills/add/` (e.g. advisor.md) or re-pins `ENGINE_MD5`/`ENGINE_PKG_MD5` -> "scope_creep_skill_or_engine"
</reject>
After:
<after>
  - a user or the orchestrator can `Task(subagent_type="add:add-advisor")` (plugin) or `Task(subagent_type="add-advisor")` (this repo's dogfood copy) to get frontier-model advice on a medium-hard decision — a recommendation + tradeoffs + a confidence self-score — with NO shared state changed and NO gate lowered. The roster is now 5; presence/frontmatter/markers/parity/no-stray all hold for 5; `ENGINE_MD5`/`ENGINE_PKG_MD5` unchanged; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ extending the frozen "exactly 4" roster invariant to 5 is the human's decision to approve at the freeze — lowest confidence because `phase-agents-lean` froze exactly-4 THREE ways (the `test_no_stray_agents_in_roster` equality, the `agent_roster_stray` reject code, and an explicit "5th stray agent rejected" scenario), so this task deliberately EVOLVES a shipped contract. If wrong (the human wants to keep exactly-4, or wants the advisor housed as an `advisor.md` guide rather than a registered agent, or wired to a phase rather than cross-cutting): the whole task is mis-shaped. This is the bundle's headline flag at the freeze.
  - [x] `model: opus` is the right way to express "frontier tier" (vs. `model: inherit` + a "Recommended tier — top" description line, the pattern add-design uses) — the user said "frontier model like opus" explicitly, so declare `model: opus`. CONFIRMED at freeze @ v1 (human approved the frozen §3, which declares `model: opus`).
  - [x] add-advisor owns NO ADD phase (cross-cutting, on-demand from any phase — like add-persona) rather than being bound to a specific phase — confirmed by the consultative "advise when need" reading.
  - [x] the `advisor.md` skill-guide touch is DEFERRED (matches phase-agents-lean's own deferral of the advisor.md cross-reference) — the naming collision (executor-subagent vs. consultative advisor) is disclosed and resolved in a later SPEC delta, not this task.
  - [x] engine pins do not move — confirmed by reading `engine_manifest.py:package_files()` (globs `add_engine/*.py` only) + the `engine_pin.py` literals; `test_skill_lean` pools scan `.claude/skills/add/*` only, not `agents/`.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: add-advisor exists with the shared body shape and frontier tier   # M1, M7
  Given add-method/agents/add-advisor.md
  When its frontmatter and body are read in full
  Then frontmatter has name: add-advisor, a non-empty description, model: opus, and a color
   And the body has the sections Become the persona, What you own, Boundary
       (the irreducible floor), Self-improve before you return, Return (disclose
       progress), and a Method depth: footer

Scenario: add-advisor is consultative and owns no ADD phase   # M2
  Given add-method/agents/add-advisor.md
  When its body is read in full
  Then it states it returns ADVICE — a recommendation, the tradeoffs/alternatives
       weighed, risks/edge-cases, and a confidence self-score — for a medium-hard decision
   And it states it owns no ADD phase and is spawnable on demand from any phase or the
       orchestrator (a cross-cutting service, like add-persona)
   And it states it advises on decisions and does NOT perform add-verify's earned-green refute-read

Scenario: add-advisor carries every shared worker-contract marker   # M3
  Given add-method/agents/add-advisor.md
  When scanned case-insensitively for the shared marker set
  Then it contains .add/personas, hard-stop, security, weaken, frozen contract,
       confidence, return, and .add/docs

Scenario: add-advisor advises but never decides, records, edits, or lowers a gate   # M4
  Given add-method/agents/add-advisor.md
  When its Boundary section is read in full
  Then it states it never runs add.py or writes shared state, never edits a test or the
       frozen contract, and never lowers a gate — a security finding it surfaces is always
       HARD-STOP and high-risk scope still escalates to the human whatever the advice

Scenario: the advisor agent mirrors byte-identically into .claude/agents/   # M5
  Given add-method/agents/add-advisor.md and .claude/agents/add-advisor.md
  When the pair is diffed
  Then they are byte-identical
   And exactly 10 add-*.md files exist across the two trees (5 + 5)

Scenario: test_agent_roster.py enforces the 5-agent roster including advisor   # M6
  Given add-method/tooling/test_agent_roster.py with AGENTS including "advisor" and
        AGENT_PHASES including "advisor": ()
  When `python3 -m unittest test_agent_roster -v` runs
  Then presence, frontmatter, the 8 shared markers, 2-tree parity, and no-stray all pass
       for 5 agents
   And a new BoundaryTest.test_add_advisor_advises_never_decides passes
   And add-advisor is exempt from the phase-naming check (it names no ADD phase, like persona)

Scenario: the engine pins and skill tree stay untouched   # M8
  Given engine_pin.py (both copies) and every file under .claude/skills/add/ before this build
  When ENGINE_MD5, ENGINE_PKG_MD5, and the skill tree are compared after the build
  Then all are byte-identical to their pre-build state
   And add-method/.claude-plugin/plugin.json is unchanged
   And the full add-method test suite reports OK

Scenario: a 6th stray agent file is rejected   # R: agent_roster_stray
  Given a file add-method/agents/add-refute.md appears alongside the declared 5
  When test_agent_roster.py's presence test runs
  Then it fails with "agent_roster_stray"
   And the declared 5 files remain valid and unaffected

Scenario: a drifted advisor mirror is rejected   # R: agent_roster_drift
  Given .claude/agents/add-advisor.md differs by even one byte from add-method/agents/add-advisor.md
  When test_agent_roster.py's parity test runs
  Then it fails with "agent_roster_drift"
   And no other agent pair is reported

Scenario: an advisor frontmatter name that does not match its filename is rejected   # R: agent_name_mismatch
  Given add-advisor.md declares name: add-adviser instead of add-advisor
  When test_agent_roster.py's frontmatter test runs
  Then it fails with "agent_name_mismatch"
   And the other 4 agent files are unaffected

Scenario: an advisor body claiming decide/record authority is rejected   # R: advisor_decides
  Given add-advisor.md's body contains a sentence implying it can itself decide, record
        state, edit a test/contract, or auto-pass a security finding
  When test_agent_roster.py's boundary test runs
  Then it fails with "advisor_decides"
   And add-design.md / add-build.md / add-verify.md / add-persona.md are unaffected

Scenario: touching the skill tree or re-pinning the engine is rejected   # R: scope_creep_skill_or_engine
  Given this task's diff touches a file under .claude/skills/add/ (e.g. advisor.md) or
        edits ENGINE_MD5/ENGINE_PKG_MD5 in engine_pin.py
  When the build is reviewed against its declared §5 Scope
  Then it is rejected with "scope_creep_skill_or_engine"
   And .claude/skills/add/ and the engine pins remain exactly as they were before this task

Scenario: an advisor missing a shared marker is rejected   # edge: SharedContractTest
  Given add-advisor.md omits the "hard-stop" marker
  When test_agent_roster.py's SharedContractTest runs
  Then it fails naming the missing shared-contract marker
   And the other 4 agent files are unaffected
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add-advisor — frozen shape @ v1  (extends the phase-agents-lean roster invariant 4 -> 5)

add-method/agents/add-advisor.md — new file. Frontmatter:
  name: add-advisor
  description: The ADD advisor — a consultative, frontier-model service any phase
    agent or the orchestrator can consult for a medium-hard decision. Returns a
    recommendation + tradeoffs + a confidence self-score; advises, never decides.
    Spawn on demand from any phase. Recommended tier — top (frontier).
  model: opus
  color: cyan
Body, exact section order (the shared roster shape used by all agents):
  opening role paragraph — a consultative advisor (modeled on Claude Code's advisor
    tool): given a situation + context it returns ADVICE, executes/records/edits
    nothing, owns NO ADD phase, spawnable on demand from any phase or the orchestrator
    (a cross-cutting service like add-persona). Names the medium-hard-decision trigger.
  ## Become the persona — loads the fit .add/personas/<slug>.md stance for the domain
    it is advising on (a generic senior-engineer/architect stance when none matches —
    the generic body never blocks).
  ## What you own (consultative advice — a cross-cutting service, not an ADD phase) —
    given a decision/situation + context, return: a recommendation, the tradeoffs /
    alternatives weighed, risks + edge-cases, and a confidence self-score. States it
    advises on DECISIONS and does NOT perform add-verify's earned-green refute-read.
  ## Boundary (the irreducible floor) —
    MAY: read the diff, the real code, the task/plan files; weigh options; recommend.
    MUST NOT: run add.py or write shared state (state.json, MILESTONE.md, a sibling's
      files) · edit a test or the frozen contract · mark a freeze/gate · lower a gate.
    STOP-and-escalate (advise; never decide): a SECURITY finding is always HARD-STOP,
      surfaced to the human; high-risk scope still escalates whatever the advice — a
      stronger model never buys back a human gate.
  ## Self-improve before you return — confidence.md six dimensions (Completeness ·
    Clarity · Practicality · Optimization · Edge cases · Self-evaluation); refine if
    any < 0.9. You PROPOSE advice; the caller/orchestrator decides and records.
  ## Return (disclose progress) — a structured verdict the caller parses:
    { role: advisor, persona, recommendation, tradeoffs, risks, confidence:
      {per-dimension 0-1}, open_questions }.
  Method depth: the AIDD book in .add/docs/ — no single phase chapter owns cross-cutting
    advice; nearest is 09-the-loop.md (deciding what to do next).

.claude/agents/add-advisor.md — byte-identical mirror of the file above
  (the 2-tree convention; 10 add-*.md files total across the two trees).

add-method/tooling/test_agent_roster.py — extended (NOT a rewrite):
  - AGENTS gains "advisor" -> ("design", "build", "verify", "persona", "advisor")
  - AGENT_PHASES gains "advisor": ()  (owns no ADD phase; exempt from the
    phase-naming check exactly as add-persona is)
  - module docstring updated 4 -> 5, naming add-advisor + its consultative role
  - a NEW BoundaryTest.test_add_advisor_advises_never_decides — asserts add-advisor's
    body states it advises but never decides / records / edits / lowers a gate
    (reject code "advisor_decides"), mirroring the design/persona boundary tests
  - all existing tests (RosterPresenceTest incl. no-stray, FrontmatterTest,
    SharedContractTest incl. the 8 markers, ParityTest) now range over 5 agents
    with no per-test rewrite beyond the AGENTS/AGENT_PHASES data change

Invariants: ENGINE_MD5 / ENGINE_PKG_MD5 (both engine_pin.py copies) receive NO edits
  (confirmed: package_files() globs add_engine/*.py only; ENGINE_MD5 = md5(add.py));
  no file under .claude/skills/add/ is touched (advisor.md cross-reference deferred);
  add-method/.claude-plugin/plugin.json receives no edits (auto-discovery); full
  add-method suite green.
```

Least-sure flag surfaced at freeze: [spec] extending the frozen "exactly 4" roster invariant to 5.
`phase-agents-lean` froze exactly-4 three ways (the `test_no_stray_agents_in_roster` equality, the
`agent_roster_stray` reject code, and a scenario titled "a 5th stray agent file is rejected"), so this
task deliberately EVOLVES a shipped contract rather than adding within one. Cost if wrong: if you want
to keep exactly-4, house the advisor as an `advisor.md` guide instead of a registered agent, or bind it
to a phase, the whole task is mis-shaped and re-enters Specify. Second flag: [contract] `model: opus`
as the literal frontier declaration (vs. `model: inherit` + a "Recommended tier — top" note like
add-design) — low cost if wrong (a one-word frontmatter edit).

Glossary deltas: advisor (agent): a consultative, frontier-model ADD roster agent that returns advice on a medium-hard decision — a recommendation, tradeoffs, and a confidence self-score — and never decides, records, edits, or lowers a gate. Distinct from `advisor.md` (the skill guide for spawning a subagent to EXECUTE a plan piece).
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the frozen §3 shape (presence · frontmatter · shared markers · phase-exemption · boundary phrasing · 2-tree parity · no-stray) — a prose/config roster extended 4->5, not a code path with branch coverage.
Plan (extend the existing test_agent_roster.py; one assertion group per scenario, asserting body content not internals):
<test_plan>
  - AGENTS gains "advisor" + AGENT_PHASES gains "advisor": () — the data change that ranges every existing test over 5 agents
  - RosterPresenceTest.test_all_four_agents_exist_in_both_trees: act glob add-{...,advisor}.md in both trees / assert all 10 files exist (M1/M5)
  - RosterPresenceTest.test_no_stray_agents_in_roster: assert the add-*.md glob == exactly the declared 5 (R: agent_roster_stray)
  - FrontmatterTest.test_required_frontmatter_fields: assert add-advisor name==add-advisor, non-empty description, model in known-tier set (accepts opus unchanged) (M1/M7, R: agent_name_mismatch)
  - SharedContractTest.test_each_agent_carries_the_worker_contract: assert add-advisor carries all 8 markers (M3)
  - SharedContractTest.test_each_agent_names_its_phases: add-advisor exempt via the empty tuple (M2)
  - BoundaryTest.test_add_advisor_advises_never_decides (NEW): assert add-advisor's body states it advises but never decides, and never runs add.py / writes shared state (R: advisor_decides)
  - ParityTest.test_roster_byte_identical_across_trees: assert add-advisor.md byte-identical across the 2 trees (M5, R: agent_roster_drift)
</test_plan>

Tests live in: `add-method/tooling/test_agent_roster.py` · confirmed RED before Build: 9 tests, 2 failures + 4 errors — all `FileNotFoundError`/`AssertionError` on the missing `add-method/agents/add-advisor.md` (the right reason; no implementation exists yet).

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/agents` · `.claude/agents` · `add-method/tooling/test_agent_roster.py`
Strategy (ordered batches): 1. write `add-method/agents/add-advisor.md` (the shared roster body shape, condensed; `model: opus`, all 8 shared markers, the advises-never-decides boundary) 2. copy it byte-identical into `.claude/agents/add-advisor.md` 3. extend `add-method/tooling/test_agent_roster.py` — add "advisor" to AGENTS, `"advisor": ()` to AGENT_PHASES, update the docstring 4->5, add BoundaryTest.test_add_advisor_advises_never_decides — confirm RED first (missing add-advisor.md), then GREEN 5. run the full add-method suite; confirm ENGINE_MD5/ENGINE_PKG_MD5 and `.claude/skills/add/` are byte-unchanged (`git diff --stat`).

Persona (optional): none seeded (method/tooling authorship, not a domain feature) — generic technical-writer/architect stance atop SOUL.md.
Known-problem fixes: bloat by re-deriving prose → lift the shared roster shape from the sibling agent files (add-design/add-persona), condensed not reinvented. · forgetting `AGENT_PHASES["advisor"] = ()` → KeyError in `test_each_agent_names_its_phases`; add it in the same edit as the AGENTS change. · a mirror-drift byte diff → write once, copy verbatim, `diff -q` the pair before the gate.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): none (no runtime/data-mutating code — static prompt/config markdown + a pure-content unittest only).
Code lives in: `add-method/agents/` (+ `.claude/agents/` mirror) · `add-method/tooling/test_agent_roster.py`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — this task's suite `test_agent_roster` is 9/9 green. Full add-method suite: 1 PRE-EXISTING, environment-only failure (`test_seams_template_wiring.test_milestone_exit_grep_lists_all_3`, appearing twice — once nested in its own fresh-checkout clone) NOT caused by this task; disclosed in the 3-lens Residue below.
- [x] coverage did not decrease — added prose (2 agent files) + 1 test method; removed nothing.
- [x] no test or contract was altered during build — `add.py audit` reports no tamper finding; the only files written during build were the two `add-advisor.md` bodies. `test_agent_roster.py` + §3 have been frozen since the tests→build snapshot.
- [x] the green was EARNED, not gamed — see the Refute-read verdict below: EARNED.
- [x] concurrency / timing of the risky operation is safe — N/A: the deliverable is a static markdown agent definition; no concurrency surface.
- [x] no exposed secrets, injection openings, or unexpected dependencies — CLEAR: prose only, no secrets/exec/new deps; the agent itself HARD-STOPs on security findings and never lowers a gate.
- [x] layering & dependencies follow CONVENTIONS.md — the 2-tree byte-identical roster convention is honored; `agents/` is not a bundled tree (confirmed against `test_bundle_parity`); engine/skill/plugin surface byte-unchanged.
- [ ] a person reviewed and approved the change — PENDING: this gate is presented to the human (method-defining + non-mechanical → human-led; see the header autonomy note).

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
> (Filled AT the gate, not before build — disclosed honestly; the outcomes below are the observable ones a correct build must produce.)
- [x] `Task(subagent_type="add-advisor")` / `add:add-advisor` resolves to a real agent — confirmed: `add-method/agents/add-advisor.md` + `.claude/agents/add-advisor.md` both present, md5 identical (`0923c1d2…`).
- [x] the agent declares the frontier tier — confirmed: frontmatter `model: opus` parsed green by `FrontmatterTest`; `color: cyan`.
- [x] the roster is now exactly 5 and still rejects a stray — confirmed: `test_no_stray_agents_in_roster` + `test_all_four_agents_exist_in_both_trees` green (glob == the declared 5).
- [x] the body is consultative & bounded — confirmed: all 8 shared markers present (`SharedContractTest`), and it states advises-never-decides + never-runs-add.py (`test_add_advisor_advises_never_decides`), owns no phase (exempt like persona), does NOT absorb add-verify's refute-read.
- [x] the ADD engine/skill/plugin surface is untouched — confirmed: `git diff --stat` empty on `add.py`, `add-method/skill/**`, `.claude/skills/**`, `plugin.json`, `src/add_method/`; both ENGINE pins hold.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [n/a] WIRING (code) — the deliverable is prose (agent-definition markdown), not code.
- [n/a] DEAD-CODE (code) — n/a for prose.
- [x] SEMANTIC (prose / non-code) — read `add-method/agents/add-advisor.md` in FULL (not skimmed): all 8 CONTRACT_MARKERS carry genuine meaning (not keyword-stuffing) — `.add/personas` in Become-the-persona, HARD-STOP/security in the escalate clause, weaken/frozen-contract in MUST-NOT, confidence in Self-improve, the `## Return` shape, `.add/docs` footer; both boundary clauses are real guidance ("advise; you never decide", "never run add.py or write shared state"); frontmatter name=add-advisor / non-empty description / model=opus / color=cyan; body section order matches the roster shape; the `.claude/agents/` mirror is byte-identical. Confirms M1–M6; no orphan/contradictory prose.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — the anchors are the two `add-advisor.md` files (now created) and `test_agent_roster.py` symbols `AGENTS` / `AGENT_PHASES` / `CONTRACT_MARKERS` / `BoundaryTest` (all present and green in the current tree).
- [x] no anchor moved/renamed since Ground SHA — the ADD engine (`add.py`) and skill tree are byte-unchanged (`git diff --stat` empty), so no cited symbol drifted.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self (frontier advisor consulted for the gate verdict) · adversarially checked: probed the 3 earned-green cheats against a PROSE deliverable — (1) overfit-to-fixtures: the markers/regexes are semantic content requirements, and the prose genuinely MEANS what it asserts (it is not special-cased to literal test tokens — every marker maps to a real, coherent sentence); (2) vacuous asserts: the roster tests are real regex/set assertions (presence, frontmatter, 8 markers, 2 boundary regexes, byte parity, no-stray), so green reflects genuine content, not tautology; (3) stubbed-away logic: n/a for prose — the agent body is complete and internally consistent, not a stub. Green is earned.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self (frontier advisor consulted for this gate)
1. Security: CLEAR — prose agent definition; no secrets, no injection surface, no exec, no new dependency. The agent's own boundary keeps every SECURITY finding a HARD-STOP and never lowers a gate.
2. Concurrency: CLEAR — static markdown; no concurrency/timing surface.
3. Architecture: CLEAR — lives in the two declared roster trees byte-identically, mirrors the shared worker-contract, owns no ADD phase (cross-cutting service, like add-persona), and `agents/` is not a bundled tree; the lean-roster convention holds and engine/skill/plugin are untouched.
Verdict: PASS (recommended — the human records the gate)
Residue: none FROM THIS TASK. NOTE (pre-existing, OUT OF SCOPE — not caused here): the full add-method suite has 1 failing test on this machine — `test_seams_template_wiring.test_milestone_exit_grep_lists_all_3` (counted twice: once nested inside its own fresh-checkout clone). Root cause: the test's `subprocess.run(["grep","-cl",…])` resolves to BSD `/usr/bin/grep`, which emits extra `filename:1` lines where GNU `grep` (Linux/CI) emits `filename` only, so the matched set carries `:1` suffixes. The 3 `TASK.md.tmpl` files it greps are git-clean and untouched by this task; inferred to pass under GNU grep (the semantics were reproduced locally — not observed on CI this session). → recorded as an observe SPEC delta (make the grep assertion binary-agnostic, or pin the grep binary).
Binding: advisory — architecture (non-mechanical; gate-relax does not apply, so verify is human-led).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: — · ticket: — · expires: —   (n/a — this is a PASS, not a RISK-ACCEPTED)
Reviewed by: Tin Dang · date: 2026-07-02   (human-led gate: method-defining + non-mechanical; build faithful to frozen §3, own suite 9/9 green, no residue from this task; the 1 pre-existing env-only grep failure queued as an observe SPEC delta)

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): no runtime telemetry — the deliverable is a static agent-definition file. Monitors: `test_agent_roster` stays green (roster == 5, parity, markers, boundary) · the plugin keeps auto-discovering `add-advisor` as a spawnable agent type (confirmed live this session) · no regression in `ENGINE_MD5`/`ENGINE_PKG_MD5` or the `test_skill_lean` byte budget.

### Decisions (ADR)
- [AI] specify — chose consultative advisor — sees the situation/context, returns advice + tradeoffs + a recommendation, executes/records/edits nothing, `model: opus`; rejected executor-subagent formalized — the existing `advisor.md` "spawn one subagent to EXECUTE a plan piece" pattern as a registered agent (rejected: `advisor.md` already covers execution-delegation; the user wants ADVICE, not execution) · absorb add-verify's earned-green refute-read into add-advisor (rejected: adversarial verification stays with add-verify; the advisor advises on decisions, it is not a verifier).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · seeded] make `test_seams_template_wiring.test_milestone_exit_grep_lists_all_3` grep-binary-agnostic — assert on the set of matched filenames independent of `grep -cl` output format, or pin the grep binary in the subprocess call (evidence: full add-method suite red on this task's verify run — BSD `/usr/bin/grep -cl` on multiple files emits extra `filename:1` lines vs GNU grep on CI; the 3 `TASK.md.tmpl` files it greps are git-clean and untouched by add-advisor) [→ grep-binary-agnostic-milestone-test]
- [SPEC · carried] resolve the `advisor.md` naming collision — `.claude/skills/add/advisor.md` (executor-subagent guide) vs. the consultative `add-advisor` agent: rename or cross-reference so the two concepts are unambiguous to a reader (evidence: add-advisor §0 Context + §1 Framings flagged it; the advisor.md touch was deferred to avoid re-opening the `test_skill_lean` byte budget) [carried: cosmetic doc-clarity fix, no functional urgency; revisit when next touching advisor docs]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a method-defining roster change escalates verify to a human gate even under `autonomy: auto` — auto-PASS is foreclosed by BOTH the 6-verify "every test green" precondition and non-mechanical sensitivity (evidence: add-advisor verify declared `risk: high`/`sensitivity: architecture`/`autonomy: conservative`; the human recorded PASS, not the run) [folded foundation-version 61]
- [ADD · folded] `agents/` is not a bundled tree — a roster agent moves neither ENGINE pin (`ENGINE_MD5`=md5(add.py) · `ENGINE_PKG_MD5`=digest of `add_engine/*.py` only) nor the `test_skill_lean` byte budget (`.claude/skills/add/*` only), and needs no `_bundled/agents/` third mirror; only the 2 declared trees (evidence: `test_bundle_parity` canon = skill/add · tooling/add.py · tooling/templates · docs · personas-teacher; `git diff --stat` empty on engine/skill/plugin/src) [folded foundation-version 61]
- [TDD · folded] on this macOS box `grep` is aliased to ugrep, but a test's `subprocess.run(["grep", …])` bypasses the alias and resolves to BSD `/usr/bin/grep`, whose `-cl` output differs from GNU grep — prefer binary-agnostic assertions or a pinned binary in any test that shells out to grep/sed/awk (evidence: reproduced BSD `/usr/bin/grep -cl` vs the ugrep alias this session) [folded foundation-version 61]

