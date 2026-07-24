# Beyond the bundle — the full routing prose

SKILL.md's compact index names each trigger; this guide carries the full routing
prose. Load it (or the one guide you need) only when a trigger fires.

- **§3 CONTRACT FROZEN** → build→verify is a dynamic, auto-gated run (`autonomy: auto` default; lower to
  `conservative`/`manual` for a human gate) — `run.md`. Pipeline ready tasks behind frozen
  contracts — the stream-orchestrator persona owns the playbook. Delegate one piece of your plan to a subagent — the named roster
  (`add-worker` runs the beat — mode: direction/build/verify/persona; `add-advisor` is the second
  mind it spawns to propose a plan, pressure-test a draft, or decide a delegable ambiguity) is
  agent-call-preferred, the default over an ad-hoc spawn; when to spawn, the prompt template, the
  tier — the advisor spawn (`phases/verify.md`). Self-score a draft (0–1 across six dimensions,
  refine if any < 0.9) — the confidence self-score (`phases/direction.md`). Both advisory; the engine never spawns.
- **Small, low-risk task**, less ceremony → the ONE atomic template already IS the lean render:
  `new-task` scaffolds only the interface (contract · red suite · scope · verdict), bundle approved
  in one freeze. Floor held (frozen contract · red test · verify gate; freeze-gated under any
  milestone). Collapse, never skip — there is no separate lane to opt into.
- **UI feature** at specify → the **design-definition loop** (UDD): intake the design axes → review the
  domain → research and reuse components → wireframe → a captured screen the human confirms **before** build — `design.md`.
  Tool-agnostic; the engine never renders.
- Tasks all done but the milestone **goal** unmet → `milestone-done` holds it open; the loop turns open
  deltas + extras into the next tasks until the goal is met — `loop.md`.
- **A multi-task / high-uncertainty milestone** needs its task DAG sequenced before the tasks are built →
  the persona-framed **strategy loop** (DISCUSS → OPTIMIZE → CONVERGE): the persona loaded at intake fills
  the milestone's `## Strategy` slot with the optimized plan, converging on the six-dimension self-score —
  `strategy.md`. SOFT/advisory, never a gate; a micro / `--tiny` milestone skips it (drafted-blank).
- **Graduating mvp → production** — co-specify interview → draft ≥1 production milestone →
  human confirm → then `stage production`. Guarded (`stage_no_roadmap`); the FINAL step, never a
  bare flip. The quality-auditor persona carries the readiness playbook.
- **Cutting a release** — draft notes from the closed milestones' deltas → meet the readiness
  floor (security HARD-STOP is un-forceable) → the human confirms and runs the tag/publish/deploy.
  The release-manager persona carries the cut playbook; the engine records nothing.
- **Monorepo / multi-repo** — a milestone spans more than one green bar (a BE + its FE) → the
  platform-engineer seed persona carries the components playbook (declare the parts, gate each
  task on its part's green bar, hold a consumer until its producer's contract freezes). Opt-in.
- **Project-fit personas** — the **persona loop** seeds `.add/personas/<slug>.md`, grows them via
  observe→delta→consolidate, applies them in design/orchestration/advisor/build (advisory; never lowers a gate) — `docs/18-personas.md`.
- **Risk-class of a task** — declare `sensitivity:` in the TASK header (base `security|data|architecture|
  mechanical`, always valid). EXTEND it with your project's domain classes in `GLOSSARY.md`'s `## Sensitivity
  classes` section; freeze/status/check read base ∪ project. The AI keeps the domain vocabulary current —
  the Sensitivity section (`phases/verify.md`). Security is a human floor in every tier; only `mechanical` is advisor-gatable — see `advisor-gate-relax` in `run.md`.
