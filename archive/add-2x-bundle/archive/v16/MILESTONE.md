# MILESTONE: xml-prompt-structure

goal: XML-structure the agent-executable add-method prompt surface (Rule 5 idiom) without bloating lean prompts
stage: mvp · status: active · created: 2026-06-06

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  An XML convention applied to agent-executable structures across the prompt surface —
     `skill/add/` (18 files) · `docs/appendix-b-prompts.md` · `tooling/templates/*.tmpl`.
     Each edit propagated through all 3 mirrors with the full suite + `add.py audit` green.
Out: Method SEMANTICS (flow, gates, CLI behavior) — unchanged. Version/release bump — deferred.
     Narrative & teaching prose, markdown headers, and tables — stay clean markdown (NOT tagged).
     The book chapters `docs/00..14-*.md` — out (human-facing teaching, not agent prompts).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **XML prompt convention** (frozen by `xml-convention`): tag agent-executable structures only,
  with a fixed Rule-5-aligned vocabulary. The frozen spec lives in `xml-convention` §3 CONTRACT.
- **Dual-audience boundary** (glossary delta): a prompt file is agent-facing AND human-facing.
  XML wraps what the agent DOES (role · steps · constraints · gates · output shapes); explanatory
  prose, `##` headers, and tables stay markdown. Tagging narrative = reject `narrative_tagged`.
- **Mirror parity**: every `skill/add/` edit → `prepare_bundle.py` → `_bundled/`, then mirror-copy
  → `.claude/skills/add/`. `test_bundle_parity` + `test_tree_parity` are the backstop.
- **Header preservation**: never drop a section header a test or cross-ref depends on
  (e.g. `## AI prompt` — `test_declare_grammar_doc`). XML goes INSIDE the section.

## Shared / risky contracts (freeze these first)
- XML prompt convention (tag vocabulary + boundary rule + reject codes) -> owning task `xml-convention`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] xml-convention         depends-on: none            — freeze the convention + convert 1-specify pilot
- [x] phase-guides-xml       depends-on: xml-convention  — convert phases/0–7 (8 files)
- [x] engine-docs-xml        depends-on: xml-convention  — convert SKILL/intake/scope/run/streams/deltas/fold/adopt/report-template/setup-review (10 files)
- [x] appendix-templates-xml depends-on: xml-convention  — convert appendix-b-prompts.md + templates/*.tmpl
- [x] mirror-greenstate      depends-on: phase-guides-xml,engine-docs-xml,appendix-templates-xml — full-suite + parity + audit sweep

## Exit criteria (observable; map each to the task that delivers it)
- [x] The XML convention is frozen + the 1-specify pilot renders the `<prompt>` block   (← xml-convention)
- [x] Every phase guide's `## AI prompt` block is XML under the frozen convention        (← phase-guides-xml)
- [x] Every engine doc's agent-executable structures are XML; narrative stays prose       (← engine-docs-xml)
- [x] appendix-b prompts carry the convention (each a `<prompt>`-wrapped intact fence); templates ASSESSED — pure fill-in forms, nothing executable to tag  (← appendix-templates-xml)
- [x] `python3 -m unittest` (whole suite) + `add.py audit` pass across all 3 mirrors      (← mirror-greenstate)
