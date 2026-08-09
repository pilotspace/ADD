# MILESTONE: component-polish — close the component-pillar gaps and harden the cross-repo edges

goal: give the component pillar an end-to-end worked example, a components.toml validator, freeze-recency safety, and a path-confined federation source
rationale: sub-milestone — harvested from the component-aware-add SPEC deltas (component-method-docs, component-registry, cross-component-milestone, multirepo-federation). Grouped because they all close the "read it → did it" gap and harden the cross-repo edges of the component pillar.
stage: mvp · status: queued · created: 2026-06-26T10:28:42+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) an end-to-end multi-component worked example + a `components.toml` reader/validator surfaced at `check` time, (2) the `component:` affordance in the fast-lane template + `per-component-verify` consuming the green-bar/verify fields, (3) a freeze-RECENCY check so a stale leftover snapshot can't admit a consumer, (4) a path-confinement guard on the federation manifest `source` (traversal-safe).
Out: a remote federation transport (git URL / artifact registry resolve) and `federate publish` — recorded as forward deltas, deferred unless a real cross-machine need lands; any change to the opt-in / byte-identical-when-zero-components invariant.

## Shared decisions & glossary deltas   (living — every task must honor these)
- opt-in + byte-identical-when-zero-components stays invariant — nothing here changes single-component behavior.
- freeze = the cross-component gate; a consumer must never build against a guessed or stale shape.
- fail-loud transport: a path/validation failure HARD-STOPS, never silently lands a wrong file.

## Shared / risky contracts (freeze these first)
- the `add.py components` reader/validator output + `check`-time schema-lint shape -> owning task `components-validator`
- the federation manifest `source` path-confinement rule -> owning task `federation-harden`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] components-validator    depends-on: none                  — `add.py components` reader/validator + a `check`-time `components.toml` schema lint (catch typos early)
- [x] component-worked-example depends-on: none                 — multi-component BE→FE worked example (book ch.17 Appendix D end-to-end transcript)
- [x] component-registry-fill depends-on: components-validator  — `component:` hint in `TASK.fast.md.tmpl`; `per-component-verify` consumes `verify` + `green_bar` to run a bound task's own suite at the gate
- [x] cross-component-recency depends-on: none                  — freeze-recency check (snapshot existence admits a stale leftover); document/guard the `cmd_phase` HOLD bypass
- [x] federation-harden       depends-on: none                  — path-confinement guard on manifest `source` (reject `../`/absolute traversal under a sibling-repo allowlist)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py components` validates `components.toml`; `check` flags a malformed entry              (← components-validator)
- [x] the book carries a complete multi-component BE→FE worked example                              (← component-worked-example)
- [x] a fast-lane task in a monorepo can declare `component:`; per-component-verify runs its suite  (← component-registry-fill)
- [x] a stale leftover snapshot no longer admits a consumer into build                              (← cross-component-recency)
- [x] a manifest `source` resolving outside the sibling-repo allowlist is rejected, not landed      (← federation-harden)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add.py` gained `_components`/`cmd_components` reader+validator + a `check`-time schema lint (components-validator), `_federation_source_confined` + a HARD-STOP `federation_source_escapes` (federation-harden), `_producer_snapshot_stale`/`_consumer_contract_hold` freeze-recency holds + 2 never-red check WARNs (cross-component-recency), `_task_verify` + gate verify-surfacing + writeback (component-registry-fill). `TASK.fast.md.tmpl` (3 trees) gained the `component:` affordance. ENGINE_MD5 → 6cc73630; **ENGINE_PKG_MD5 795abe88 UNCHANGED** all milestone; component-worked-example was DOCS-ONLY (no engine touch).
- skill   : `skill/add/components.md` (3 trees) updated for the verify-surfacing + the new fail-loud codes (component-worked-example); lean fence respected (reclaimed from prose, budget unweakened).
- book    : ch.17, the glossary, and Appendix D (4 trees each) gained the multi-component BE→FE worked example + the 4 new codes + the verify-surfacing (component-worked-example).

### Cross-task evidence   (one row per task)
- components-validator     : gate=PASS · tests=full suite green · residue=none (opt-in, byte-identical-when-zero)
- federation-harden        : gate=PASS · tests=HardenConfine 6 green · residue=TOCTOU symlink-swap, LOW + outside threat model → forward delta (security-expert reviewed)
- cross-component-recency  : gate=PASS · tests=Recency 8 green · residue=none (R1 hashless-snapshot closed as a never-red WARN; refute EARNED)
- component-registry-fill  : gate=PASS · tests=TaskVerify 3 + VerifySurface 4 green · residue=none (surface-only/NO-EXEC; refute EARNED)
- component-worked-example : gate=PASS · tests=test_component_worked_example 11 green · residue=none (scope under-declaration self-healed: §5 corrected + declared re-snapshot, sidecar intact)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which): EC1←components-validator · EC2←component-worked-example (book) · EC3←component-registry-fill · EC4←cross-component-recency · EC5←federation-harden
- goal: give the component pillar an end-to-end worked example, a components.toml validator, freeze-recency safety, and a path-confined federation source — MET: all 5 tasks gate=PASS; suite 2235/0, check 470/0, audit clean; opt-in/byte-identical-when-zero-components held throughout.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
