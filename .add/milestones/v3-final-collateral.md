---
type: Milestone
title: v3.0.0 final collateral
status: archived
generated: { by: add/3.0.0, at: 2026-08-11 }
verified: []
---
## CARD
goal: everything 3.0.0 needed that was not the engine itself — the docs that teach it, the post that announces it, and the four defects a real first run trips over.
why: authored retrospectively 2026-09-03. The milestone was scaffolded 2026-08-11 and driven to six closed tasks without its CARD or EXIT ever being filled in — `freeze` did not refuse a template Milestone until the `authoring-beat-named` task shipped that guard, so nothing ever asked. Its work is done and released; this records what it was.

## SCOPE
In:  the 3.0.0 release collateral — docs site, launch post — and the engine defects a first run hits: digest root, `--scope` append, `upgrade` leaving a working bundle, Persona scaffold keys
Out: the 3.0 graft itself, and every method change after it — those are their own milestones

## GROUND
touches: add-method/docs/, blog/, add-method/tooling/add.py, add-method/tooling/templates/
risks:
  - collateral is the part a release forgets; a shipped engine nobody can start is not shipped

## EXIT
- [x] the receipt digest and the gate's freshness check resolve `scope:` from the same root, and a degrade is said out loud   (← run-digest-root)
- [x] `add new Persona` scaffolds every contract-recommended routing key plus OKF description/sources   (← okf-persona-template)
- [x] the mkdocs book teaches the engine that ships   (← docs-beta2-refresh)
- [x] repeated `--scope` flags append in order, and the comma form keeps working   (← scope-flag-append)
- [x] a launch post a normal user can act on, with the honest numbers   (← launch-blog)
- [x] after `add upgrade` the very next `add status` runs   (← upgrade-working-bundle)

## CLOSE
| task | verdict | receipt |
|---|---|---|
| run-digest-root | PASS | closed 2026-08 — one digest root, degrade stated |
| okf-persona-template | PASS | closed 2026-08 — routing keys + OKF fields scaffolded |
| docs-beta2-refresh | PASS | closed 2026-08 — book teaches the shipped engine |
| scope-flag-append | PASS | closed 2026-08 — repeated flags append, comma form kept |
| launch-blog | PASS | closed 2026-08 — post written against the honest numbers |
| upgrade-working-bundle | PASS | closed 2026-08 — upgrade leaves a runnable bundle |
