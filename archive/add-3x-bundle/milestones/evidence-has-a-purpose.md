---
type: Milestone
title: Evidence has a purpose
status: direction
generated: { by: add/3.6.0, at: 2026-09-16 }
verified: []
---
## CARD
goal: A receipt proves only the claim and subject it was gathered for
why: a green receipt currently has no declared purpose beyond the regression-floor marker, so a diagnostic support run can become the latest executable gate candidate; publishing also rebuilds npm and PyPI files in separate jobs after source tests, leaving the installed bytes outside the reviewed evidence chain.
next: author the receipt-purpose security contract and the local candidate-artifact gate independently; each gets its own approval and evidence.

## SCOPE
In: bound/floor/support receipt authorization and a local holdout refusal; backward-compatible legacy receipts; a build-once, hashed candidate artifact install/upgrade smoke; publish jobs consume the tested files.
Out: treating an actor name as authenticated identity, minting local protected holdout provenance, publishing a release in this task, or claiming registry delivery from a local smoke.

## GROUND
touches: add-method/tooling/add.py and CLI twins · add-method/FORMAT.md · .github/workflows/publish.yml · candidate artifact smoke script/tests · release notes
risks:
  - changing the latest-receipt selector without enumerating beat, refute, gate, remembered test command, Explore and release readers lets support evidence entitle a claim through another route
  - rebuilding after smoke makes even a correct local artifact test evidence for different bytes than a registry receives
  - the receipt entitlement path can affect security gates; its Task has a computed human floor and cannot enter Build on an inferred interview answer

## EXIT
- [ ] C1 a Run declares bound, floor, or support purpose; only the purpose authorized for a claim can feed its gate/refute/beat/release route, legacy receipts remain honest, and a local holdout claim refuses before execution   (← receipt-purpose-binds-claim)
- [ ] C2 wheel, sdist, and npm candidate files are built once, hashed, installed and upgraded in isolation; publish jobs consume those same verified files while local results state their external provenance limit   (← candidate-artifact-is-installed)

## CLOSE
evidence: one exact scoped receipt and independent review per completed Task, plus local artifact digests and smoke report for C2; external registry verification remains a separate claim.
