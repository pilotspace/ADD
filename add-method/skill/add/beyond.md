# Beyond the bundle — the full routing prose

SKILL.md's compact index names each trigger; this guide carries the full routing
prose. Load it (or the one guide you need) only when a trigger fires.

- **§3 CONTRACT FROZEN** → build→verify is a dynamic, auto-gated run (`autonomy: auto` default; lower to
  `conservative`/`manual` for a human gate) — `run.md`. Pipeline ready tasks behind frozen
  contracts — `streams.md`. Delegate one piece of your plan to a subagent — the named roster
  (the ONE `add` agent — mode: direction/build/verify/persona/advise) is agent-call-preferred, the
  default execution mode over an ad-hoc spawn; when to spawn, the prompt template, the tier —
  the advisor spawn (`phases/verify.md`). Self-score a draft (0–1 across six dimensions, refine if
  any < 0.9) — the confidence self-score (`phases/direction.md`). Both advisory; the engine never spawns.
- **Small, low-risk task**, less ceremony → the **fast lane**: `new-task --fast` renders TASK.md
  minus the deep-verify/observe sections (a derived subset of the ONE template), bundle approved in
  one freeze — routing lives in SKILL.md flag mode. Floor held (frozen contract · red test · verify
  gate; freeze-gated under any milestone). Collapse, never skip; opt-in.
- **UI feature** at specify → the **design-definition loop** (UDD): intake the design axes → review the
  domain → research and reuse components → wireframe → a captured screen the human confirms **before** build — `design.md`.
  Tool-agnostic; the engine never renders.
- Tasks all done but the milestone **goal** unmet → `milestone-done` holds it open; the loop turns open
  deltas + extras into the next tasks until the goal is met — `loop.md`.
- `status` prints **`MVP covered → propose graduation`** (every milestone done AND stage criteria all
  `[x]`) → `graduate.md`: `graduation-report` → co-specify interview → draft ≥1 production milestone →
  human confirm → then `stage production`. Guarded (`stage_no_roadmap`); the FINAL step, never a bare flip.
- `status` prints **`→ releasable: N milestone(s) closed since last release`** → `release.md` (the 5th
  scope level): `release-report` → draft notes from the consolidated deltas → meet the readiness floor
  (security HARD-STOP is un-forceable) → human confirms → `add.py release <version>` records the cut
  (CHANGELOG + `RELEASES.md` ledger + milestone attribution). The engine records; the human runs the
  tag/publish/deploy. A release bundles ≥1 milestone, orthogonal to stage.
- **Monorepo / multi-repo** — a milestone spans more than one green bar (a BE + its FE) → the
  **component pillar**: declare components in `.add/components.toml`, gate each task on its component's
  green-bar, freeze cross-component contracts (`produces:`/`consumes:`), hold the FE until the BE
  freezes, `federate pull` across repos — book chapter `docs/17-components.md` + the
  platform-engineer seed persona. Opt-in; no components = today.
- **Project-fit personas** — the **persona loop** seeds `.add/personas/<slug>.md`, grows them via
  observe→delta→consolidate, applies them in design/streams/advisor/build (advisory; never lowers a gate) — `docs/18-personas.md`.
- **Risk-class of a task** — declare `sensitivity:` in the TASK header (base `security|data|architecture|
  mechanical`, always valid). EXTEND it with your project's domain classes in `GLOSSARY.md`'s `## Sensitivity
  classes` section; freeze/status/check read base ∪ project. The AI keeps the domain vocabulary current —
  the Sensitivity section (`phases/verify.md`). Security is a human floor in every tier; only `mechanical` is advisor-gatable — see `advisor-gate-relax` in `run.md`.
