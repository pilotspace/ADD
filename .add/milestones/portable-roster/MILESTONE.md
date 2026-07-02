# MILESTONE: Portable phase-roster for other coding agent tools

goal: non-Claude coding tools receive the ADD phase-roster's roles and boundaries through the AGENTS.md the installer already drops
rationale: new-milestone — a slice of the standing "any agent drives the CLI loop" goal. The installer already onboards ~10 tools via AGENTS.md + Claude's `.claude/rules/`, but the `add-method/agents/` phase-roster (design·build·verify·persona·advisor) is materialized ONLY for Claude Code (plugin auto-discovery); every other tool is blind to the 5 phase-roles and their boundaries. EXTENDS the multi-agent-installer line · DEPENDS-ON the canonical `agents/*.md` roster + `add_engine/guidelines.py` guideline block · OVERLAPS none live. Altitude A (universal via AGENTS.md), all tools — confirmed by Tin Dang 2026-07-02.
stage: mvp · status: active · created: 2026-07-02T08:58:18+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the ADD guideline block the installer / `sync-guidelines` drops into AGENTS.md (every non-Claude tool) carries a COMPACT, tool-agnostic phase-roster — the 5 roles, when to adopt each per phase, and the shared boundary floor — DERIVED from the canonical `add-method/agents/*.md` so it cannot drift, bound by a parity test, added leanly (no guideline-block / `test_skill_lean` budget bloat beyond the agreed compact form).
Out: native per-tool agent files — Cursor modes, Copilot `.github/chatmodes/*` (altitude B, deferred) · a full per-tool generator/exporter (altitude C, deferred) · onboarding NEW tools beyond the ~10 already registered · changing the Claude Code plugin roster mechanism (stays as-is) · duplicating full agent bodies into AGENTS.md (compact summary only, never the whole body).

## Shared decisions & glossary deltas   (living — every task must honor these)
- Single source of truth: `add-method/agents/*.md` stays canonical; the portable roster form is DERIVED, never hand-authored twice — a drift-guard test enforces it.
- Lean: the roster reaches AGENTS.md as a COMPACT section (roles + when + floor), not full bodies; compress, don't budget-bump (honors the guideline-block / `test_skill_lean` leanness).
- The boundary floor must survive into every tool's form: never weaken a test · never edit a frozen contract · a SECURITY finding is always HARD-STOP · the freeze is human-only · the advisor advises-never-decides.
- Glossary delta: **portable roster** — the tool-agnostic, derived representation of the 5 phase-roles (role · when-to-adopt-per-phase · shared floor) that reaches non-Claude tools through AGENTS.md.

## Shared / risky contracts (freeze these first)
- the portable-roster representation — inline-compact-in-block vs. a neutral materialized file + AGENTS.md reference — and its derivation/parity contract  ->  owning task `roster-portable-shape`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] roster-portable-shape       depends-on: none                  — define + freeze how the roster is represented for non-Claude tools (5 roles · when-to-adopt-per-phase · shared floor), derived from `agents/*.md`; resolve the mechanism (inline-compact vs neutral-file+reference). The riskiest contract.
- [x] roster-onboarding-wiring    depends-on: roster-portable-shape — the installer / `sync-guidelines` materializes that portable roster into AGENTS.md for every onboarded tool; parity test binds it to the canonical source; tool-agnostic (no Claude-only `Task(subagent_type=…)` / plugin-discovery leaks in).

## Exit criteria (observable; map each to the task that delivers it)
- [x] A non-Claude tool's onboarding file (AGENTS.md) names all 5 phase-roles + when to adopt each + the shared boundary floor        (← roster-onboarding-wiring) (verify: `test_roster_portable.py::test_roster_names_5_roles_and_spans` + `test_agent_detect.py::PointerTest::test_init_supersedes_cline_pointer` extends this to every GUIDELINE_FILES target incl. `.clinerules`)
- [x] The portable roster is DERIVED from `add-method/agents/*.md`, and a parity/drift test fails if the two diverge               (← roster-portable-shape) (verify: `test_roster_portable.py::test_roster_derived_from_agents` + `::test_drift_bidirectional`)
- [x] No Claude-only mechanism (`Task(subagent_type=…)`, plugin auto-discovery) appears in the tool-neutral roster form            (← roster-portable-shape) (verify: `test_roster_portable.py::test_no_claude_only_mechanism` + `::test_claude_leak_rejected`)
- [x] The guideline block stays lean — the roster is a compact section with no budget-bump beyond the agreed form                  (← roster-onboarding-wiring) (verify: `test_roster_portable.py::test_block_stays_lean`; unaffected by task 2's additive-only `.clinerules` wiring)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add_engine/constants.py` (roster in `_guideline_block()` + `GUIDELINE_FILES` gained `.clinerules`), `add_engine/guidelines.py` (`_INIT_EXCLUDE` gained `.clinerules`, docstring updated), `engine_pin.py` (`ENGINE_PKG_MD5` re-aimed twice, `ENGINE_MD5` untouched both times), mirrored byte-identical across canonical + `_bundled` + local `.add/tooling`; new test files `test_roster_portable.py` (10 tests) + additions to `test_guidelines.py`/`test_brownfield_scan.py`/`test_agent_detect.py`/`test_rule_file_mode.py` (6 tests)
- skill   : untouched — no `.claude/skills/add/` changes; the roster reaches non-Claude tools via the guideline block only, Claude Code keeps its existing plugin auto-discovery
- book    : untouched — no `.add/docs/` changes

### Cross-task evidence   (one row per task)
- roster-portable-shape    : gate=PASS · tests=10/10 new (`test_roster_portable.py`) + full suite green (2 pre-existing env-only failures) · residue=none
- roster-onboarding-wiring : gate=PASS · tests=6/6 new + full suite 2727/2727 green (2 pre-existing env-only failures) · residue=goal-line wording ("through the AGENTS.md the installer already drops") is narrower than shipped scope (task 2 also closed cline's `.clinerules` gap) — a deliberate, human-directed scope expansion (Tin: "fold cline fix into this task"), not an oversight; the Exit-criteria wording above already reflects the shipped scope

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — all 4 Exit criteria cite their verifying tests inline (above); both tasks PASS with 16 new tests (10 + 6) and zero regressions across a 2727-test suite
- goal: non-Claude coding tools receive the ADD phase-roster's roles and boundaries through the AGENTS.md the installer already drops — proven by `test_roster_portable.py` (roster content/derivation/leanness) + `test_agent_detect.py::test_init_supersedes_cline_pointer` (every registered tool, including the one whose `integration_file` isn't AGENTS.md, actually receives the block through its real onboarding path)

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] commit task 2's work (constants.py/guidelines.py/engine_pin.py `.clinerules` wiring + 6 new tests + MILESTONE.md close) on `feat/add-advisor-agent`
- [ ] open/update the PR (this branch already carries PR #126 — add-advisor + roster-portable-shape); human reviews + merges
- [ ] tag / publish / deploy — human-run, per `release.md`, when bundled with the next release cut
