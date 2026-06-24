# MILESTONE: Component-aware ADD

goal: ADD treats every codebase as a graph of components — each owning its source root, green-bar, and produced/consumed contracts — so a single milestone can ship a vertical slice across components living in one repo or many.
rationale: new-major (intake-confirmed 2026-06-24, Tin chose "one big new-major, ~6 tasks").
  A net-new pillar no active milestone's goal covers: ADD today assumes ONE project = ONE source
  tree = ONE green-bar, so a feature spanning a backend + a frontend is forced into separate
  milestones (the recurring BE-then-FE split observed in ai-proxy v31/v32/v36 → v37). This major
  makes the **component** — a bounded context with its own root + verify profile + contracts — the
  unit, and folds monorepo vs multi-repo into one model where only state-location + snapshot-transport
  differ. Relationship to the map: *extends* the §5 Scope anchor model (build-scope-lock) and the
  verify gate (verify-expectations); *depends-on* the existing "Shared / risky contracts" milestone
  section it promotes to a first-class artifact; no existing milestone delivers cross-component scope.

stage: mvp · status: active · created: 2026-06-24

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
  - **Component registry** (`.add/components.toml` or a PROJECT.md block): named components, each with
    a `root` (a §5 scope anchor) + a `verify` command + a `green_bar` phrase + language. Parsed by the
    engine; a task may declare `component: <name>`.
  - **Per-component verify**: the verify gate runs the task's component `verify` profile + checks its
    `green_bar`, instead of one project-wide suite. Close "Ship by domain" auto-derives per component.
  - **Cross-component contract as a first-class artifact**: a named seam with a producer component +
    consumer components + a frozen snapshot file (`.add/contracts/<id>.json`). Producer §3 freeze WRITES
    the snapshot; consumers PIN it; a producer re-freeze auto-flags every consumer stale (a §7 delta).
  - **Cross-component milestone**: milestone tasks carry `component:` + `depends-on:`; the engine HOLDS
    a consumer task from entering §3 until its producer's contract is frozen — so BE→FE ships in one
    milestone with the FE still downstream of the frozen endpoint.
  - **Multi-repo federation**: per-repo git-native `.add/` is kept; a federation manifest joins one
    milestone across repos BY contract id — producer freeze publishes the immutable snapshot, consumer
    repo pins the version. Only state-location + snapshot-transport differ from monorepo.
  - **Method docs**: book chapter + skill guide + GLOSSARY deltas for the component pillar.
Out:
  - A central server / shared mutable state across repos — federation transports only the frozen
    (immutable) snapshot; each repo's `state.json` stays git-native and independent.
  - Auto-discovery of components (scanning for `apps/*`) — components are DECLARED, not inferred, this
    milestone.
  - Per-component autonomy / ownership policy (multi-user owns identity; this milestone is structure).
  - Polyrepo CI orchestration / cross-repo merge-train automation — federation defines the contract
    join, not the pipeline that runs it.

## Shared decisions & glossary deltas   (living — every task must honor these)
- GLOSSARY delta: a **component** is a bounded context with its own source `root`, `verify` green-bar,
  and the contracts it produces/consumes — the unit a task and the verify gate are scoped to. A
  monorepo component is a subpath; a multi-repo component is a whole repo. Topology is addressing only.
- GLOSSARY delta: a **cross-component contract** is a named seam (id · producer · consumers · frozen
  snapshot) — distinct from a task's internal §3 contract; it is the API boundary BETWEEN components.
- INVARIANT — backward-compatible default: a project with NO components declared behaves byte-identically
  to today (one implicit component = project root, one green-bar). Components are opt-in; never retro-red
  a pre-component task (grandfathered, mirrors the §5 scope grandfather).
- INVARIANT — freeze is the cross-component gate: a consumer task may not enter §3 (contract) until its
  producer's cross-component contract is frozen; a producer re-freeze that changes the snapshot opens a
  stale delta on every consumer (never silently breaks a downstream leg).
- INVARIANT — designed-for-failure: snapshot transport (mono file read or multi-repo publish/pin) has a
  bounded, fail-loud path — a missing/mismatched pinned snapshot HARD-STOPS the consumer, never builds
  against a guessed shape.

## Shared / risky contracts (freeze these first)
- **Component registry schema** (`components.toml` shape: name · root · verify · green_bar · language;
  + how a task declares `component:`) -> owning task `component-registry`  (tasks 2–4 build against this)
- **Cross-component contract artifact protocol** (snapshot file format · producer-freeze-writes ·
  consumer-pin · stale-delta-on-refreeze) -> owning task `cross-component-contract`  (tasks 4–5 build on this)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] component-registry        depends-on: none                    — define + parse `.add/components.toml`; a task may declare `component:`; §5 scope anchors to the component `root`; zero-components ⇒ byte-identical to today. (freezes the registry schema)
- [ ] per-component-verify      depends-on: component-registry       — verify gate runs the task's component `verify` profile + green-bar; Close "Ship by domain" auto-derives per component. (the unlock for mixed milestones)
- [ ] cross-component-contract  depends-on: component-registry       — contract-as-artifact: producer §3 freeze writes `.add/contracts/<id>.json`, consumer pins it, producer re-freeze flags consumers stale. (freezes the seam protocol)
- [ ] cross-component-milestone depends-on: cross-component-contract — milestone tasks carry `component:` + `depends-on:`; engine HOLDS a consumer's §3 until the producer contract is frozen (intra-milestone BE→FE).
- [ ] multirepo-federation      depends-on: cross-component-contract — federation manifest joins a milestone across repos by contract id; producer publishes the immutable snapshot, consumer repo pins the version; bounded fail-loud transport.
- [ ] component-method-docs      depends-on: per-component-verify, cross-component-milestone — book chapter + skill guide + GLOSSARY entries for the component pillar (component · cross-component contract · federation).

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A project can declare ≥2 components (root + verify + green-bar) in `.add/components.toml`, and a task can be tagged to one; a project with zero components behaves exactly as today   (← component-registry)
- [ ] At verify, a task gates against ITS component's suite + green-bar — two tasks in one milestone can pass on two different toolchains (e.g. pytest and vitest)   (← per-component-verify)
- [ ] A producer task's §3 freeze writes a contract snapshot; a consumer task pins it; changing the producer's frozen shape flags every consumer stale via a §7 delta   (← cross-component-contract)
- [ ] One milestone holds a producer (BE) and consumer (FE) task where the consumer cannot enter §3 until the producer's contract is frozen — proving a full-stack vertical slice in one milestone   (← cross-component-milestone)
- [ ] A milestone spans two repos: the producer repo publishes a frozen snapshot, the consumer repo pins that version, and a missing/mismatched pin hard-stops rather than building blind   (← multirepo-federation)
- [ ] The book + skill + glossary document the component / cross-component-contract / federation model; method suite green   (← component-method-docs)

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
