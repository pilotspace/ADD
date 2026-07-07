# MILESTONE: Drain the 4 open SPEC deltas

goal: the 4 open SPEC deltas are each resolved into a shipped behavior — compact-foundation gains a read-only --propose preview, personas gain a dedicated `verify` flow value, the streams.md worker-contract `<persona>` block names the flow preference, and status/check render an engine-built persona roster line — leaving zero open SPEC deltas
rationale: intake bucket=sub-milestone (2026-07-07, Tin: "implement all directly"): 4 independent deltas from 3 prior tasks, each small but crossing engine+skill+guard surfaces; loose fast tasks would lose the shared roster/flow decisions, so a thin milestone binds them
stage: mvp · status: active · created: 2026-07-07T08:15:15+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  `compact-foundation --propose` read-only verb (per-spec settled-line preview, no writes) · `verify` added to the persona flow vocabulary + routing (schema, guides, roster frontmatter where a verify persona exists) · streams.md worker-contract `<persona>` block gains a flow-preference line (the pin-locked `<strategy>` block itself stays byte-identical — additions land OUTSIDE it, pins re-anchored honestly if line offsets move) · engine-rendered persona roster line (slug · flow · vibe) in status + check · resolve all 4 deltas via --from-delta seeding · lean budgets absorbed by compression first, contract-signed rebaseline only if compression is impossible
Out: no new gates (personas/flows stay advisory) · no persona file rewrites beyond frontmatter flow values · no compact-foundation WRITE-path changes · no change to the advisor flow's meaning (verify is added beside it, not carved out of its guide prose) · the 4 open LESSONS drain via `add.py fold` at milestone close, not as tasks

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Shared decisions & glossary deltas   (living — every task must honor these)
- Flow vocabulary after this milestone: `design · build · verify · advisor · persona` — glossary delta owned by verify-flow-value; every surface that enumerates flows (schema, guides, roster line) must render the SAME set.
- Everything here stays ADVISORY (strategy-soft-not-hard): --propose never writes, the roster line never gates, flow routing never lowers a bar.
- Pin discipline: streams.md `<strategy>` block byte-identical vs advisor.md (test_streams/test_xml_convention floor); SEAMS.md line-number pins re-anchored in the same task that moves them.

## Shared / risky contracts (freeze these first)
- persona flow value set (`verify` added) -> owning task verify-flow-value (roster-status-line consumes it)
- --propose output line grammar -> owning task compact-propose

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] compact-propose      depends-on: none              — `compact-foundation --propose` read-only verb: render the per-spec settled line for the eligible tail, zero writes
- [ ] verify-flow-value    depends-on: none              — add `verify` to the persona flow vocabulary + routing surfaces (schema/guides/frontmatter)
- [ ] streams-persona-flow depends-on: verify-flow-value — worker-contract `<persona>` block names the flow preference; `<strategy>` pin floor untouched
- [ ] roster-status-line   depends-on: verify-flow-value — engine renders a persona roster line (slug · flow · vibe) in status + check

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py compact-foundation --propose` (or the compact verb's --propose flag) prints the would-be settled line per spec and writes nothing        (← compact-propose; live dogfood rendered PROJECT.md fv21-fv35, tree unchanged)
- [x] a persona can declare `flow: verify` and every flow-enumerating surface agrees on the 4-value set (drafted "5-value" pre-freeze — the frozen contract is the 4-tuple design·build·advisor·verify)        (← verify-flow-value)
- [x] a spawned worker's `<persona>` block carries the flow preference while the `<strategy>` block stays byte-identical to advisor.md        (← streams-persona-flow)
- [x] `add.py status` and `add.py check` print one engine-built `slug · flow · vibe` line per persona        (← roster-status-line; live check renders the 6-persona roster row)
- [x] `add.py deltas` reports 0 open SPEC deltas (all 4 seeded --from-delta)        (← all; the 4 open lessons also drained via fold -> fv65)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py gains `compact-foundation --propose` (read-only, beside cmd_deltas) + `_persona_roster` and the status/check roster rendering (trio synced, ENGINE_MD5 → 9be0267f) · add_engine/constants.py PERSONA_FLOW_VALUES += "verify" (ENGINE_PKG_MD5 → a00e1d36) · personas/_template.md.tmpl flow hint → four surfaces (4 twins; a pre-existing drifted add-method/.add dogfood twin healed by mirroring canon) · 4 new guard suites (compact-propose 6 · verify-flow 11 · streams-flow 5 · roster 7) · sanctioned pin migrations: KNOWN_FLOWS + flow-values 4-tuple, min_pillar LIFECYCLE (+compact-foundation, the self-maintaining guard's designed path), ubiquitous-language machine spans for the contract-frozen "folded" grammar · SEAMS.md scope-token-grammar anchor 4786→4798
- skill   : streams.md `<persona>` block gains the flow-first selection sentence; paid by in-file compression (orchestration pool 41275/41300, whole tree 145973/145974) · phases/6-verify.md persona bullet names `flow: verify` (+7 B, phases pool 33282/33284) · 3 trees lockstep each
- book    : docs/18-personas.md "Apply — three surfaces" → "four surfaces" + a verify-lens bullet (3 git twins + .add/docs copy) · .add/personas/tdd-verifier.md → `flow: verify, advisor` (writer+reader in one milestone)

### Cross-task evidence   (one row per task)
- verify-flow-value    : gate=PASS · tests=11 new red-first + 79-test sibling run green (2 pins migrated forward, contract-signed) · residue=none
- streams-persona-flow : gate=PASS · tests=5 new red-first + 83-test guard run green · residue=the frozen sentence re-flowed for byte cost (the freeze's anticipated trim; meaning intact, disclosed in §5)
- roster-status-line   : gate=PASS · tests=7 new red-first + seams/mirror/nudge run green · residue=SEAMS.md anchor re-pin was a disclosed out-of-scope side-fix
- compact-propose      : gate=PASS · tests=6 new red-first + live dogfood · residue=2 post-gate ripples surfaced by the FULL suite (min_pillar LIFECYCLE entry + slang-guard machine spans + help reword) — fixed, disclosed here, full suite re-run green below

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied: criterion 1 ← compact-propose row (live dogfood) · criterion 2 ← verify-flow-value row · criterion 3 ← streams-persona-flow row · criterion 4 ← roster-status-line row (live check roster) · criterion 5 ← `add.py deltas` output (0 open SPEC deltas)
- goal: all 4 open SPEC deltas resolved into shipped behavior — proven by `add.py deltas` printing zero open SPEC deltas while every delta's target behavior renders live (propose preview · verify flow · worker flow sentence · roster lines)

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from `feat/delta-drain` (stacked on feat/build-strategy-facets / PR #139); the human reviews + merges after #139
- [ ] verify ENGINE_MD5 (9be0267f) + ENGINE_PKG_MD5 (a00e1d36) pins re-pinned honestly
- [ ] bundle into the next release cut (release.md); human runs tag/publish
