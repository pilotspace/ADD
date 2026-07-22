# Domain — the DDD spec

project: AIDD / ADD Methodology · seeded: 2026-07-17 · stage: mvp

> Living document — what the system IS: entities, rules, ubiquitous language (DDD).
> Keep the sections below CURRENT (state, not history); lessons land under
> Deltas the moment they are learned: `add.py delta-append ddd "<lesson>"`.
> A delta that changes the standing picture is folded UP into the sections
> above it and marked `[folded]` — the Deltas list is the inbox, not the spec.

## Now
<!-- migrated from PROJECT.md §Domain @ fv66 (foundation-split) -->
- Core concepts: **task** (one feature), **milestone** (depth-bounded group of tasks),
  **phase** (direction→build→verify→done), **gate** (PASS·RISK-ACCEPTED·HARD-STOP),
  **contract** (frozen shape), **living documentation** (durable artifacts that outlive code),
  **stage** (prototype·poc·mvp·production).
- Bounded contexts / modules: **tooling** (`add.py` + `state.json` — the state engine),
  **skill** (router `SKILL.md` + on-demand `phases/*` — what the agent loads),
  **book** (`docs/*` — the trust layer users read).
- The hard invariants (phase-marker truth · frozen-seam discipline · atomic writes ·
  anti-context-rot) live in PROJECT.md §Domain — the read-first home the orient map surfaces.

## Decisions that bind
- "owner/assignee" (mutable, directive) is genuinely distinct from the "actor stamp" (immutable, historical) even though they share the `{name,email,source}` shape — `source:"assigned"` marks human-typed provenance vs git/os/override resolution (evidence: ownership-model needed the 4th source value to stay honest). [fv43 · ownership-model]
- The managed↔user-data boundary is a REUSED domain concept: heal-reconcile/global-install copy the MANAGED layer, global-data copies its COMPLEMENT (user-data) — name the boundary once (an explicit include/exclude rule) and share it (`_is_user_data` is the inverse of MANAGED). [fv38 · global-data]
- A done-tally over `state["milestones"]` has an all-archived blind spot — every milestone archived → empty map → `bool(ms)` False → a cue keyed on "every milestone done" never fires; count archived milestones toward such tallies or document why not. [fv22 · DDD]

## Deltas (newest first)
<!-- prepended by `add.py delta-append ddd "<text>"` — one line per lesson, `- [open · <date>] <lesson>` + the active-task stamp; fold a delta upward, then retag [open]->[folded] -->
