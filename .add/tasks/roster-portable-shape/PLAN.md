# TASK: Portable roster representation for non-Claude tools

slug: roster-portable-shape · created: 2026-07-02 · stage: mvp · risk: high · sensitivity: architecture
milestone: portable-roster
autonomy: conservative
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/agents/*.md` (5 files: add-design · add-build · add-verify · add-persona · add-advisor) — the CANONICAL roster, the derivation SOURCE. Each = frontmatter (`name` · `description` · `model` · `color`) + body (opening role paragraph · `## Become the persona` · `## What you own` · `## Boundary (the irreducible floor)` · `## Self-improve before you return` · `## Return` · a `Method depth:` footer). The `description` carries "Spawn at the <PHASE> step" + "Recommended tier — <tier>"; the boundary section carries the shared floor.
  - `add-method/tooling/add_engine/guidelines.py:_guideline_block()` — returns the marker-delimited ADD block written into every guideline file; PRIMARY host for the portable roster. Already agent-agnostic (docstring cites v14 agent-portability). `_inject_block(path)` / `_inject_guidelines(project_root, rule_file)` write it (idempotent, .bak-on-change, symlink-dedup, fail-soft).
  - `add-method/tooling/add_engine/constants.py` — `GUIDELINE_FILES = ("AGENTS.md","CLAUDE.md")` · `_GUIDE_BEGIN`/`_GUIDE_END` markers · `RULES_FILE_REL` (.claude/rules/add-workflows.md) · `WORKFLOW_HEADINGS`. The roster-source→AGENTS.md mapping (phase→role) lives conceptually alongside `test_agent_roster.py:AGENT_PHASES` (design=setup..contract · build=tests+build · verify=verify+observe · persona/advisor=()).
  - `add-method/tooling/test_agent_roster.py:AGENTS`/`AGENT_PHASES`/`CONTRACT_MARKERS` — the roster's existing invariants; the shared floor (`hard-stop` · `security` · `weaken` · `frozen contract`) the portable form must preserve. (Read-only reference; not edited here.)
Context (working folder):
  - `.add/milestones/portable-roster/MILESTONE.md` — the parent (goal · In/Out · shared decisions · the 2-task decomposition; this is task 1, the riskiest-contract task).
  - `add-method/bin/cli.js:AGENT_PROFILES` — the installer's ~11-tool registry; every non-Claude profile's `integration_file` is `AGENTS.md` (claude→CLAUDE.md, cline→.clinerules). This is WHERE the portable roster lands for other tools; wiring is task 2 (`roster-onboarding-wiring`), but the shape must fit here.
  - book: `.add/docs/` — no chapter yet names a cross-tool roster; `02-the-flow.md` is the nearest (the loop any agent drives).
Honors (patterns / conventions):
  - Single source of truth — `agents/*.md` stays canonical; the portable form is DERIVED, never a hand-authored twin (mirrors the 2-tree byte-identical roster convention + the `test_bundle_parity` DERIVED-not-duplicated stance).
  - Lean — the guideline block is deliberately tiny; add the roster as a COMPACT section, compress-don't-budget-bump ([[feedback_lean_over_budget_bump]]). NOTE: `test_guidelines.py` pins NO byte/length budget (only markers · idempotency · no-live-state · content-preservation), so there is freedom — honor the spirit anyway.
  - Agent-agnostic — `test_agent_portability.py::test_block_routes_any_agent` guards that the block routes ANY agent; the portable roster must carry NO Claude-only mechanism (`Task(subagent_type=…)`, plugin auto-discovery).
  - The boundary floor must survive into the portable form: never weaken a test · never edit a frozen contract · SECURITY is always HARD-STOP · the freeze is human-only · the advisor advises-never-decides.
Seams consulted: (none apply — no SEAMS.md entry governs the guideline block or roster derivation)
Anchors the contract cites: `add-method/agents/*.md` (the 5 roster files + their `description`/`Boundary` fields) · `add_engine/guidelines.py:_guideline_block()` · `add_engine/constants.py` (`GUIDELINE_FILES`, `_GUIDE_BEGIN`/`_GUIDE_END`) · `test_agent_roster.py:AGENT_PHASES` (the phase→role map) · `test_agent_portability.py::test_block_routes_any_agent` (the agent-agnostic invariant).
Issues/Risks (→ feed §1):
  - **The core decision to freeze: representation mechanism.** (a) INLINE a compact roster section inside `_guideline_block()` (simplest; grows the block, lands in AGENTS.md automatically for all tools) vs. (b) a NEUTRAL materialized file (e.g. `.add/roster.md` or `.add/agents/`) the installer drops + a ONE-LINE reference in the block (keeps the block leanest; adds a materialize step to cli.js/add.py). §1 must pick one and §3 freezes it.
  - **Derivation vs. drift.** If the portable form is derived from `agents/*.md`, a parity/drift test must fail when they diverge. But the agent bodies are prose (not structured data) — deriving a compact summary mechanically is non-trivial; the contract likely pins a HAND-WRITTEN-but-parity-CHECKED summary (assert every role name + each boundary keyword from `agents/*.md` appears in the portable form), not a full auto-generation. Name this at §1.
  - **Branch dependency.** This milestone derives from all 5 agents incl. `add-advisor.md`, which lives on branch `feat/add-advisor-agent` (PR #126, UNMERGED) — not yet on `main`. Ground SHA is on that branch. Decision deferred to build/commit time: rebase portable-roster onto `main` after #126 merges, or stack. Design phases (ground→tests) are branch-independent.
Related intent: milestone `portable-roster` rationale — give non-Claude tools the roster's value; serves PROJECT.md goal "any agent drives the CLI loop while the human owns direction/verification". Origin: user (2026-07-02) "enhance agents @add-method/agents/ to support other coding agent tools also" → altitude A (universal via AGENTS.md), all tools, confirmed. See [[project_portable_roster_intake_2026_07_02]].
Ground SHA: c970357   (branch feat/add-advisor-agent — has all 5 agents; cite symbols, not bare line numbers)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the ADD guideline block (dropped into AGENTS.md for every non-Claude tool, CLAUDE.md for Claude) gains a COMPACT, tool-agnostic phase-roster orientation — the 5 role-stances mapped to their phase span + recommended model tier, plus the 2 cross-cutting services (persona · advisor) that own no phase — DERIVED from `add-method/agents/*.md`, POINTING to the per-phase guides and the boundary floor (both already reachable by every onboarded tool) rather than restating them.
Framings weighed: inline-compact section inside `_guideline_block()` (chosen — the plain reading of "universal via AGENTS.md"; lands in every guideline file automatically; measured to fit lean) · neutral materialized file + one-line block reference (alternative — leanest block, adds an installer materialize step; the §3 fallback if the compact form cannot fit inline) · restate per-phase behavior + the floor in the roster (rejected — duplicates the already-installed phase guides and the block's existing floor; bloats the lean block for no new value)
Must:
<must>
  - M1 — the block names all 5 roles, each mapped to its phase span: design (setup→contract) · build (tests→build) · verify (verify→observe); and marks persona + advisor as cross-cutting services that own no phase (adopt on demand from any phase).
  - M2 — each role carries its recommended model tier (top at design · verify · advisor; mid at build · persona) — the one orientation fact that is NOT already in the per-phase guides.
  - M3 — the roster POINTS to the per-phase guides (block step 3 already routes any agent to `.claude/skills/add/phases/`) and to the boundary floor (already stated in the block), and does NOT restate a phase's steps or the floor text.
  - M4 — the roster content is DERIVED from `add-method/agents/*.md`: every role name, its phase span, its tier word, and the 2 service names are present in the block; a parity/drift test fails if a roster agent is added, removed, or re-tiered without the block updating in lockstep.
  - M5 — the portable form carries NO Claude-only mechanism: no `Task(subagent_type=…)`, no "plugin auto-discovery", no `.claude/agents` path; it orients ANY agent (honors `test_agent_portability::test_block_routes_any_agent`).
  - M6 — the roster reaches AGENTS.md the same way the block already does (`_guideline_block()` → `GUIDELINE_FILES`); the roster text is identical for every non-Claude tool and for Claude (tool-agnostic).
  - M7 — the block stays lean: the roster is a compact section (target ≤ ~10 added lines; the block carries no byte budget but the lean spirit is honored). If the compact form cannot fit inline, fall back to the neutral-file mechanism (decided at §3).
</must>
Reject:
<reject>
  - a roster agent added / removed / re-tiered in `agents/*.md` without the portable roster updating in lockstep -> "roster_portable_drift"
  - the portable form contains a Claude-only spawn mechanism (`Task(subagent_type`, "plugin auto-discovery", `.claude/agents`) -> "roster_claude_only_leak"
  - the roster's phase→role mapping contradicts `test_agent_roster.py:AGENT_PHASES` (e.g. names build as owning verify) -> "roster_phase_mismatch"
</reject>
After:
<after>
  - a non-Claude tool reading AGENTS.md sees the 5 roles + their phase spans + tiers + the 2 cross-cutting services + a pointer to the guides and the floor — enough to adopt the right stance per phase with no Claude-only mechanism.
  - a parity test binds the block's roster to `add-method/agents/*.md`; the drift-guard is green.
  - the guideline block is still lean; CLAUDE.md and every AGENTS.md carry the identical roster text.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ representation mechanism = INLINE-compact-in-block (not a neutral materialized file) — lowest confidence because it is the human's call at the §3 freeze and trades a slightly larger block for a leaner installer. Measured: the block is 26 lines / 1421 chars today; the compact form is ~8 lines (roles + spans + tiers + 2 services + 1 pointer) and `test_guidelines.py` pins NO byte budget, so inline fits without material bloat. If wrong (human wants neutral-file): task 2 (wiring) adds a materialize + reference step; the §1/§2 CONTENT rules survive unchanged. Cost: small, contained to wiring.
  - [ ] tier recommendations are useful even to single-model CLIs that cannot switch models per task — confirm at freeze; if not, the tier becomes advisory prose ("prefer your strongest model for design/verify/advisor") rather than a per-role marker. Content survives either way.
  - [ ] derivation is CHECK-not-generate: a parity test binds prose `agents/*.md` to the compact form by keyword PRESENCE (every role name · its phase-span tokens · its tier word · the 2 service names appear in the block) — full mechanical auto-generation from the prose bodies is out of scope.
  - [ ] the phase→role spans match each agent's `description` "Spawn at the … step" (add-design SETUP→CONTRACT · add-build TESTS/BUILD · add-verify VERIFY/OBSERVE · add-persona/add-advisor any-phase) — re-confirmed against the 5 descriptions before pinning.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: roster names all 5 roles + spans + the 2 services   # M1
  Given a project onboarded with the ADD guideline block written into AGENTS.md
  When I read the roster section of the block
  Then it names all 5 roles — design, build, verify, persona, advisor
  And design is mapped to setup→contract, build to tests→build, verify to verify→observe
  And persona and advisor are marked as cross-cutting services that own no phase

Scenario: each role shows its recommended tier   # M2
  Given the roster section of the block
  When I read each role's line
  Then design, verify, and advisor show a "top" tier
  And build and persona show a "mid" tier

Scenario: the roster points, it does not restate   # M3
  Given the block containing the roster section and the existing boundary floor
  When I scan the whole block
  Then the roster references the per-phase guides and the floor by pointer
  And the floor sentences (never weaken a test · HARD-STOP) still appear ONCE, not duplicated by the roster

Scenario: the roster is derived from the canonical agents   # M4
  Given the 5 canonical files under add-method/agents/ (each with name · phase-span · tier)
  When the parity test runs against the block
  Then every role name, its phase-span tokens, its tier word, and both service names from agents/*.md are found in the block's roster

Scenario: no Claude-only mechanism leaks into the portable form   # M5
  Given the portable roster text as written into AGENTS.md
  When I scan it for Claude-only tokens
  Then it contains no "Task(subagent_type", no "plugin auto-discovery", and no ".claude/agents" path
  And test_agent_portability::test_block_routes_any_agent stays green

Scenario: the roster text is identical across tools   # M6
  Given two onboarded tools — codex (AGENTS.md) and claude (CLAUDE.md)
  When the block is written into both files
  Then the roster section text is byte-identical between them

Scenario: the block stays lean   # M7
  Given the block before and after the roster is added
  When I count the added lines
  Then the roster adds no more than ~10 lines
  And test_guidelines still passes (markers · idempotency · no-live-state · content preserved)

Scenario: a roster agent changes without the block -> drift caught   # R1: roster_portable_drift
  Given a 6th roster agent added to agents/ (or an existing tier changed) without updating the block
  When the parity test runs
  Then it fails, naming "roster_portable_drift"
  And the shipped block is otherwise unchanged

Scenario: a Claude-only token in the roster is rejected   # R2: roster_claude_only_leak
  Given a draft roster whose text contains "Task(subagent_type=…)"
  When the agent-agnostic leak test runs
  Then it fails, naming "roster_claude_only_leak"
  And no such token ships in the committed block

Scenario: a phase→role mapping that contradicts AGENT_PHASES is rejected   # R3: roster_phase_mismatch
  Given a roster line mapping build to the verify phase
  When the parity test cross-checks phase→role against test_agent_roster.py:AGENT_PHASES
  Then it fails, naming "roster_phase_mismatch"
  And the shipped roster's mapping matches AGENT_PHASES
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_guideline_block() -> str   # the marker-delimited ADD block written into every GUIDELINE_FILES target
  carries a ROSTER SECTION (compact, <= ~10 added lines) that, for each of the 5 canonical agents/*.md:
    design   : setup -> contract   · tier top
    build    : tests -> build      · tier mid
    verify   : verify -> observe   · tier top
    persona  : any phase (cross-cutting service — owns no phase)  · tier mid
    advisor  : any phase (cross-cutting service — owns no phase)  · tier top
  + one POINTER line -> the per-phase guides (.claude/skills/add/phases/) and the floor already in the block; NO restatement
  identical roster text across every GUIDELINE_FILES target (AGENTS.md == CLAUDE.md); NO Claude-only token

parity check: a test binds the block <-> add-method/agents/*.md by PRESENCE
    (each role name · its phase-span tokens · its tier word · both service names appear in the block)
  agent added / removed / re-tiered, block not updated            -> "roster_portable_drift"
  roster text carries Task(subagent_type | plugin auto-discovery | .claude/agents)  -> "roster_claude_only_leak"
  phase -> role mapping contradicts test_agent_roster.py:AGENT_PHASES -> "roster_phase_mismatch"

Derivation: CHECK-not-generate — a hand-written compact form, parity-asserted; NOT mechanical auto-generation from prose bodies.
Host: INLINE in _guideline_block() (chosen); the neutral-file fallback applies only if the compact form cannot fit lean.
Schema: writes add_engine/guidelines.py:_guideline_block() (in-memory block -> GUIDELINE_FILES); reads add-method/agents/*.md (source, unedited); new parity test in add-method/tooling/. No state.json / template change.
```

Glossary deltas: `portable roster: the compact, tool-agnostic, DERIVED roster section in the guideline block — 5 roles (name · phase-span · tier) + the 2 cross-cutting services + a pointer to the guides and floor` (reaffirms the milestone glossary delta)
Least-sure flag surfaced at freeze: [contract] the representation mechanism — INLINE-compact-in-block vs a neutral materialized file + one-line reference; why-unsure: it trades block-leanness for installer-leanness and is the human's call; cost-if-wrong: task 2 (wiring) reshapes, the §1/§2 CONTENT rules survive either way. Resolved at freeze: INLINE (approved by Tin Dang).
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new roster invariants (10 scenarios → 10 tests); behavioral, asserting the block's observable content, not internals.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_roster_names_5_roles_and_spans: arrange call _guideline_block() / act read the roster section / assert all 5 role names present + design=setup→contract, build=tests→build, verify=verify→observe spans + persona/advisor marked cross-cutting (own no phase) · covers: M1
  - test_each_role_shows_tier: arrange the block / act read each role line / assert top for design·verify·advisor, mid for build·persona · covers: M2
  - test_roster_points_not_restates: arrange the block / act scan whole block / assert a pointer to .claude/skills/add/phases/ is present AND the floor sentence ("never weaken a test"/"HARD-STOP") occurs exactly ONCE (roster did not duplicate it) · covers: M3
  - test_roster_derived_from_agents: arrange parse each add-method/agents/*.md (name · Spawn-at span · Recommended-tier) / act compare to the block / assert every role name, span token, tier word, and both service names appear in the block · covers: M4
  - test_no_claude_only_mechanism: arrange the block / act scan the roster section / assert NO "Task(subagent_type", NO "plugin auto-discovery", NO ".claude/agents"; and test_agent_portability::test_block_routes_any_agent still green · covers: M5
  - test_roster_text_identical_across_tools: arrange _inject_block into a temp AGENTS.md and a temp CLAUDE.md / act extract each roster section / assert byte-identical · covers: M6
  - test_block_stays_lean: arrange line count with/without the roster / act diff / assert <= ~10 added lines AND test_guidelines invariants (markers · idempotency · no-live-state · preserved) still hold · covers: M7
  - test_drift_bidirectional: arrange a simulated 6th agent (or a re-tiered role) not reflected in the block / act run the parity check / assert it fails naming "roster_portable_drift" · covers: R1, R:roster_portable_drift
  - test_claude_leak_rejected: arrange a roster draft containing "Task(subagent_type=…)" / act run the leak check / assert it fails naming "roster_claude_only_leak" · covers: R2, R:roster_claude_only_leak
  - test_phase_mismatch_rejected: arrange a roster line mapping build→verify / act cross-check against test_agent_roster.py:AGENT_PHASES / assert it fails naming "roster_phase_mismatch" · covers: R3, R:roster_phase_mismatch
</test_plan>

Tests live in: `add-method/tooling/test_roster_portable.py` · MUST run red (missing roster section) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add_engine/guidelines.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add_engine/guidelines.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py`   (4 tracked mirror files — see the scope note below; the parity test file is authored in §4/TESTS, not here)
Scope note (why 4, discovered mid-build): editing guidelines.py changes the add_engine package digest, so ENGINE_PKG_MD5 in engine_pin.py must be re-aimed; test_engine_extract_md5 pins that digest byte-identical across the tracked canonical tree AND the _bundled tree, so BOTH copies of BOTH files move together. The gitignored .add/tooling dogfood mirror is synced locally so the 3-tree suite goes green, but it is excluded from the scope walk (.add is in _SCOPE_EXCLUDE_DIRS) — a local sync, never a committed token. §3 CONTRACT is unchanged (external roster shape identical); this is a §5 touch-set widening only, re-anchored by re-crossing tests→build.
Strategy (ordered batches): 1. add a compact ROSTER SECTION inside `_guideline_block()` (canonical `add-method/tooling` tree only) — 5 role lines (name · phase-span · tier) + persona/advisor marked cross-cutting + ONE pointer line to `.claude/skills/add/phases/` and the floor already in the block; place it after the flow paragraph, inside the existing `_GUIDE` markers. 2. keep it agent-agnostic — no `Task(subagent_type`, no "plugin auto-discovery", no `.claude/agents`. 3. byte-copy the edited guidelines.py verbatim into the `_bundled` tree AND the local `.add/tooling` mirror; md5-verify all three equal. 4. compute the new package digest and re-aim ENGINE_PKG_MD5 in engine_pin.py across all three trees (byte-identical); ENGINE_MD5 = md5(add.py) is UNTOUCHED. 5. verify idempotency/markers/no-live-state still hold (section is plain static text); do NOT restate the floor — reference it; keep floor keywords single-occurrence.
Persona (optional): none (method/tooling stance atop SOUL.md — the lean-roster + agent-portability conventions are the domain)
Known-problem fixes: ugrep/BSD-grep gotcha → the new parity test uses Python string search, NEVER shells out to `grep -cl` ([[project_add_advisor_agent_2026_07_02]]) · lean drift → keep the section ≤ ~10 lines (compress-don't-budget-bump) · duplication → reference the guides/floor, don't copy them.
Strategy actually used: as planned for batches 1–4, with one mid-build discovery + human decision. The 6-line roster overflowed a lean invariant the freeze-time measurement missed — `test_v8_onramp::test_block_stays_a_pointer` caps the whole block at ≤22 non-blank lines (the block was already AT 22); the inline roster pushed it to 28. The freeze had checked `test_guidelines` (no byte budget) but not this LINE budget. Not a contract change (external roster shape unchanged), so §3 stayed frozen; surfaced to the human as a §5-level fit decision (compress vs signed-bump vs change-request), with a verified compressed candidate shown. Tin chose COMPRESS-to-fit (honors compress-over-bump). Resolution: (a) stripped the roster to minimal test-mandated form `role · span · tier · [service]` (dropping prose descriptions that violated this task's own point-don't-restate insight); (b) genuinely trimmed verbose NON-pinned sub-clauses from the 3-step loop, flow paragraph, and closing — every pinned token preserved (`add.py status`/`guide`, `PROJECT.md`, `milestone`, `ONE human approval`, floor sentence, `security`, `.add/docs/`, `add skill`, `any agent`) — landing the block at exactly 22. Then the mirror+pin dance ONCE on the final text: byte-copied guidelines.py to the `_bundled` + local `.add` trees (md5 `fc0027c6…`), re-aimed ENGINE_PKG_MD5 `de43f6f8…→82297e49…` across all three engine_pin.py (md5 `2ddd647e…`); ENGINE_MD5 untouched.
Safety rule (feature-specific): the roster text lives in ONE place (`_guideline_block()`); no second hand-authored copy anywhere — single source, parity-guarded.
Code lives in: `add-method/tooling/add_engine/guidelines.py` (canonical roster edit) + its byte-identical `_bundled` mirror; the digest re-aim lands in `engine_pin.py` across both tracked trees (plus the local `.add/tooling` copy)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_roster_portable` 10/10 + full suite green EXCEPT 2 PRE-EXISTING env-only ugrep/BSD-grep failures (`test_seams_template_wiring::test_milestone_exit_grep_lists_all_3` + the fresh-checkout job that re-runs it) — green on CI, not this change ([[project_add_advisor_agent_2026_07_02]])
- [x] coverage did not decrease — +10 new tests (roster suite); no test removed or weakened
- [x] no test or contract was altered during build — §3 FROZEN untouched; no test file edited (the red suite was authored in TESTS; the ≤22 conflict was resolved by COMPRESSING the block to fit `test_v8_onramp`, never by editing that test)
- [x] the green was EARNED, not gamed — refute-read below (EARNED)
- [x] concurrency / timing of the risky operation is safe — N/A: the change is static block text + one constant literal (`ENGINE_PKG_MD5`); no runtime, IO, threads, or shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — static prose; no new imports/deps; `guidelines.py` cluster closure unchanged
- [x] layering & dependencies follow CONVENTIONS.md — `_guideline_block()` unchanged in shape (string content only); the pin is a literal in `engine_pin.py` (tooling level, not in the digest)
- [ ] a person reviewed and approved the change — **HELD for the human (conservative autonomy); not self-stamped**

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a fresh `add.py init` project's AGENTS.md carries a compact roster naming all 5 roles with their phase spans (design setup→contract · build tests→build · verify verify→observe) + persona/advisor marked cross-cutting services — CONFIRMED: eyeballed the generated block (dumped above); M1 green
- [x] each role line shows the tier DERIVED from that agent's `agents/*.md` description (design·verify·advisor top; build·persona mid) — CONFIRMED: roster lines read against the 5 descriptions (design top / build mid / verify top / persona mid / advisor top); M2/M4 green
- [x] AGENTS.md and CLAUDE.md carry byte-identical roster text, with NO Claude-only token (`Task(subagent_type`, `plugin auto-discovery`, `.claude/agents`) — CONFIRMED: M6 (byte-identical across the two GUIDELINE_FILES targets) + M5/R2 (no Claude-only token) green
- [x] the block stays lean and still opens with "## ADD — how to work in this repo" and points at `add.py status`/PROJECT.md/the phase guides; the floor sentence appears exactly ONCE (not restated) — CONFIRMED: block is exactly 22 non-blank lines (honors `test_v8_onramp` ≤22 pointer-budget); M3/M7 + `test_v8_onramp` green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — no NEW symbol added: the roster is string content inside the existing `_guideline_block()`, already wired via `_inject_block` → `_inject_guidelines` → `init`/`sync-guidelines`, so it ships to every GUIDELINE_FILES target automatically. `ENGINE_PKG_MD5` is consumed by `test_engine_extract_md5`/`test_shared_engine_pin` (both green).
- [x] DEAD-CODE (code) — none: no new function/constant/parameter; only string content + one re-aimed literal.
- [x] SEMANTIC (prose / non-code) — read the full 22-line generated block (dumped above): roster reads correctly, every pinned token present, floor stated once, no Claude-only mechanism.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — CONFIRMED by import/resolve at verify: `guidelines._guideline_block()` OK · `constants.GUIDELINE_FILES`=('AGENTS.md','CLAUDE.md') · `_GUIDE_BEGIN`/`_GUIDE_END` OK · `test_agent_roster.AGENT_PHASES` (design setup→contract · build tests→build · verify verify→observe · persona/advisor ()) · 5 `agents/add-*.md` present · `test_agent_portability::test_block_routes_any_agent` green
- [x] any anchor that moved/renamed since Ground SHA is named here, not left silent — NONE moved (Ground SHA c970357; all anchors resolve unchanged). NOTE: Ground SHA is on branch `feat/add-advisor-agent` (PR #126, unmerged) — the 5th agent `add-advisor.md` is not yet on main; the commit/branch step (deferred) rebases portable-roster onto main after #126 merges.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (1) the red suite failed for the RIGHT reason before build (9 fail "block carries no roster section" + 1 pass — the M5 negative guard — as predicted), so green means the roster was really added, not the test bent; (2) tiers are DERIVED at test time from each agent's `description` (`TIER_RE`), not hard-coded — re-tiering an agent moves the assertion, so a stale roster fails; (3) the drift check R1 is a BIDIRECTIONAL set-equality (`_roster_roles == set(AGENTS)`) — add/remove/rename an agent and it fails, no overfit to today's 5; (4) M3 asserts the floor sentence count == 1 across the WHOLE block, so the roster cannot silently duplicate it; (5) the ≤22 pointer-budget was satisfied by real compression (verified: every pinned token still present), not by weakening `test_v8_onramp`.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self (frontier advisor() tool consulted twice during build — on the §5 blast-radius scope + on the compress-vs-bump conflict; its guidance shaped the resolution)
1. Security: CLEAR — no attack surface; static block text + a hash literal. No input parsing, no IO, no eval. The block is agent-instruction prose; no secret/credential path touched.
2. Concurrency: CLEAR — no runtime, threads, or shared mutable state; `_guideline_block()` is pure and returns a constant string. The 3-tree mirror write is done sequentially by the build, not at runtime.
3. Architecture: CLEAR with a noted residue — the inline roster leaves the guideline block at EXACTLY the ≤22 pointer-budget (zero headroom); any future inline addition to `_guideline_block()` must compress or bump. Recorded as an OBSERVE delta. The engine-pin blast radius (digest re-aim across 3 mirror trees) is inherent to any `add_engine/*.py` change and was handled correctly (byte-identical, pin matches).
Verdict: PASS
Residue: zero-headroom on the ≤22 block budget (future guideline-block additions blocked until compressed/bumped) — captured as a §7 spec delta, not a blocker for this ship.
Binding: advisory — architecture sensitivity (advisor-gate-relax does NOT apply; verify is human-led)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-02

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose inline-compact section inside `_guideline_block()`; rejected neutral materialized file + one-line block reference (alternative — leanest block, adds an installer materialize step; the §3 fallback if the compact form cannot fit inline) · restate per-phase behavior + the floor in the roster (rejected — duplicates the already-installed phase guides and the block's existing floor; bloats the lean block for no new value)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned for batches 1–4, with one mid-build discovery + human decision. The 6-line roster overflowed a lean invariant the freeze-time measurement missed — `test_v8_onramp::test_block_stays_a_pointer` caps the whole block at ≤22 non-blank lines (the block was already AT 22); the inline roster pushed it to 28. The freeze had checked `test_guidelines` (no byte budget) but not this LINE budget. Not a contract change (external roster shape unchanged), so §3 stayed frozen; surfaced to the human as a §5-level fit decision (compress vs signed-bump vs change-request), with a verified compressed candidate shown. Tin chose COMPRESS-to-fit (honors compress-over-bump). Resolution: (a) stripped the roster to minimal test-mandated form `role · span · tier · [service]` (dropping prose descriptions that violated this task's own point-don't-restate insight); (b) genuinely trimmed verbose NON-pinned sub-clauses from the 3-step loop, flow paragraph, and closing — every pinned token preserved (`add.py status`/`guide`, `PROJECT.md`, `milestone`, `ONE human approval`, floor sentence, `security`, `.add/docs/`, `add skill`, `any agent`) — landing the block at exactly 22. Then the mirror+pin dance ONCE on the final text: byte-copied guidelines.py to the `_bundled` + local `.add` trees (md5 `fc0027c6…`), re-aimed ENGINE_PKG_MD5 `de43f6f8…→82297e49…` across all three engine_pin.py (md5 `2ddd647e…`); ENGINE_MD5 untouched.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] the guideline block now sits at EXACTLY its ≤22 lean-pointer budget — the next inline addition to `_guideline_block()` must compress existing prose OR the human signs a budget bump; consider a `test_guidelines` byte/line budget assertion so the constraint is discoverable at freeze, not build (evidence: this task's roster forced a whole-block compression to net ≤22, zero headroom remains) [carried: a standing caution for whoever next touches _guideline_block(), not an action in itself]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] the guideline block has TWO lean guards, not one — `test_guidelines` pins NO byte budget but `test_v8_onramp::test_block_stays_a_pointer` caps the WHOLE block at ≤22 non-blank lines (markers included); a freeze that measures only the first mis-sizes an inline addition (evidence: this bundle froze inline-compact against `test_guidelines` and missed the ≤22 line budget, surfacing only at build as `30 not ≤ 22`) [folded foundation-version 61]
- [ADD · folded] a §5-scope widening discovered mid-build is NOT a contract change — an `add_engine/*.py` edit moves `ENGINE_PKG_MD5` across 3 mirror trees, so expand §5 + re-cross tests→build to re-anchor while §3 stays frozen (the external shape is unchanged) (evidence: the 1-file scope became 4 tracked files + a pin re-aim, resolved without reopening the freeze) [folded foundation-version 61]
- [ADD · folded] surface the TRUE blast radius at the human verify gate, not the original one-file story — the human gates on the real scope (evidence: the widened 4-file + engine-pin touch-set was disclosed in §6 FLAGS + the gate report, and Tin gated PASS on that scope) [folded foundation-version 61]

