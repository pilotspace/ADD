# MILESTONE: Persona learning loop

goal: Let the ADD loop learn project-fit personas from the agency-agents library (a teacher, not a runtime dependency): the AI SEEDS the project's requirements personas during setup (a living doc the project uses live), grows them via the observe->fold self-improve loop, applies them to UDD/advisor/build, and exposes a cross-runner (Claude Code · Codex · ...) persona-aware subagent — with the engine staying NO-EXEC and the build path reading only local persona files.
rationale: new-major — a new pillar (project-fit personas learned from an external library) that no active milestone's goal covers, spanning authoring + UDD/advisor/build application + a self-improve loop + docs → several breadth-first tasks, too big for one. Reuses agency-agents (github.com/msitarzewski/agency-agents) as a TEACHER (its distilled critical-rules + measurable success-metrics), not as a runtime dependency.
stage: mvp · status: active · created: 2026-06-29T12:57:33+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) SEED at setup — phase 0-setup authors the project's requirements personas (from the 4-lens
     interview / brownfield map + PROJECT.md, using agency-agents skill contents as teacher) into
     `.add/personas/*` as a living doc, covered by the EXISTING setup baseline approval; re-runnable
     on-demand later as the project evolves. Personas are distilled to critical-rules +
     default-requirement + MEASURABLE success-metrics; upstream credited. (2) UDD application —
     `design.md`'s captured-screen confirm uses the matched persona's success-metrics as an evidence
     checklist; (3) self-improvement — the observe→delta→`fold` loop grows the project personas from
     real usage; (4) a SEEDED cross-runner persona-aware subagent PROMPT — ship a portable worker
     `PROMPT.md` template (built on the `streams.md` `<persona>`/`<expertise>` contract) that loads the
     active `.add/personas/<slug>.md`, PLUS a thin per-platform adapter stub for each supported coding
     agent (Claude Code verified reference; Codex/opencode/Cursor/… illustrative). The template is the
     shipped artifact; the engine seeds it locally (no spawn, no network); (5) application at the
     advisor/streams spawn, the orchestrator identity overlay, and the §5 build strategy;
     (6) book + skill + glossary.
Out: vendoring the full 232-agent library; any raw-file fetch / cache / refresh / SHA-pin machinery;
     the upstream 12-platform conversion installer; ANY engine-side network IO or spawning;
     non-software personas (Reddit/TikTok/game-dev/etc.). The engine stays NO-EXEC; the build path
     reads only local persona files; authoring is an off-build, human-gated agent action.

## Shared decisions & glossary deltas   (living — every task must honor these)
- PERSONA = an ADD-native file (`.add/personas/<slug>.md`) distilled from a teacher source to its
  critical-rules + default-requirement + measurable success-metrics. It is an in-repo artifact
  (reproducible); the LEARNING is dynamic, the APPLIED persona is recorded and frozen.
- Teacher, not dependency: agency-agents is read ONLY during the authoring step, by the agent, with
  fail-safe fallback (offline → use existing personas; never block a build).
- Self-improvement reuses ADD's EXISTING loop (observe→delta→`fold` + `confidence.md`); no new
  learning engine is invented.
- A persona NEVER lowers a gate: a security finding still HARD-STOPs; a persona's success-metric is a
  checklist the human/observe-loop confirms, not an auto-pass.
- Personas are a SETUP living doc (like PROJECT.md / GLOSSARY) — seeded in phase 0-setup from the
  project's requirements and covered by the setup baseline approval; no new approval gate is added.
- UDD sources TWO personas (agency-agents teachers): UI-Designer (visual + WCAG-AA accessibility
  success-metrics) AND UX-Researcher (methodology-first, evidence-not-assumption validation +
  inclusive-research default). The captured-screen confirm checklist carries BOTH dimensions —
  reinforcing ADD principle 2 (trust evidence, not assumptions). A UI-less project skips this.
- The cross-runner subagent stays agent-agnostic: the persona loads into the EXISTING `streams.md`
  worker `PROMPT.md` (`<persona>`/`<expertise>`); only the thin spawn adapter differs per runner.
- ONE canonical portable PROMPT body + thin per-platform adapter stubs (not N divergent prompts).
  Platform set = the agents ADD already onboards (Claude Code · Codex · opencode · Cursor · Windsurf ·
  Copilot · Cline · Aider · Gemini CLI). HONESTY RULE: only Claude Code is verified in-repo; every
  other stub is labelled illustrative until confirmed via `find-docs` — never claim verified untested.

## Shared / risky contracts (freeze these first)
- the persona file schema (frontmatter · identity · critical-rules · default-req · success-metrics) -> owning task persona-setup
- the UDD captured-screen confirm-checklist shape (success-metrics → confirmable items)            -> owning task udd-persona-loop
- the persona-injection point in the `streams.md` worker contract (`<persona>`/`<expertise>` load `.add/personas/<slug>.md`; cross-runner) -> owning task persona-subagent-prompt
- the portable persona-worker PROMPT template + per-platform adapter-stub schema (one canonical body, thin per-runner mapping) -> owning task persona-subagent-prompt

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
### Spine — prove the seed→apply→improve cycle on UDD first
- [ ] persona-setup            depends-on: none              — phase 0-setup SEEDS the project's requirements personas to `.add/personas/*` (living doc, schema frozen here, covered by the setup baseline approval); re-runnable on-demand; agency-agents as teacher
- [ ] udd-persona-loop         depends-on: persona-setup     — `design.md` captured-screen confirm uses TWO sourced personas as an evidence checklist: UI-Designer (visual/accessibility metrics — is the screen right?) + UX-Researcher (methodology-first validation — validated by user data, not assumed?). HEADLINE — improves UDD
- [ ] persona-self-improve     depends-on: persona-setup     — observe→delta→`fold` grows the project personas from real usage (the self-improving core)
### Back half — widen to the other surfaces once the spine proves out
- [ ] persona-subagent-prompt  depends-on: persona-setup     — SEED a portable persona-aware worker `PROMPT.md` template + thin per-platform adapter stubs (Claude Code verified; Codex/opencode/Cursor/… illustrative) that load `.add/personas/<slug>.md`
- [ ] advisor-persona-select   depends-on: persona-subagent-prompt — advisor/streams SELECT which persona per delegated piece (Code-Reviewer 🔴/🟡/💭 → verify refute-read)
- [ ] orchestrator-build-persona depends-on: persona-setup   — orchestrator identity overlay atop `SOUL.md` + §5 build-strategy persona hook
- [ ] persona-method-docs      depends-on: persona-setup     — book chapter + skill pointer + glossary + 3-tree/4-tree parity

## Exit criteria (observable; map each to the task that delivers it)
- [ ] Setup seeds ≥1 requirements persona to `.add/personas/` matching the frozen schema, covered by the setup baseline approval; a test asserts the schema   (← persona-setup)
- [ ] With no network the seeding degrades gracefully (uses existing personas / project requirements, never blocks); a test asserts the fail-safe              (← persona-setup)
- [ ] UDD's captured-screen confirm renders BOTH the UI-Designer success-metrics (visual/accessibility) AND the UX-Researcher validation metrics (methodology-first, evidence-not-assumption) as an evidence checklist; a test asserts both dimensions (← udd-persona-loop)
- [ ] An observe-phase persona lesson flows through delta→`fold` and updates a persona file without clobbering it; a test asserts the merge                     (← persona-self-improve)
- [ ] A seeded portable `PROMPT.md` template + per-platform adapter stubs exist; the Claude Code path injects the active persona's identity+rules+success-metrics; a test asserts the injection (← persona-subagent-prompt)
- [ ] The advisor/streams selection picks a persona per delegated piece and records it in the verdict; a test/doc-truth check asserts it                        (← advisor-persona-select)
- [ ] The orchestrator overlay + §5 build hook reference a persona; a doc-truth/test check asserts both                                                         (← orchestrator-build-persona)
- [ ] book + skill + glossary describe the persona loop and stay in parity across trees; the parity test passes                                                (← persona-method-docs)
- [ ] Engine invariant held: no engine code path performs network IO or spawns; the build path reads only local persona files                                  (← all tasks)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
