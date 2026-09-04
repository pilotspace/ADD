---
type: Milestone
title: The walk tells the truth, and the checks that say so can fail
status: direction
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "Tin Dang", at: 2026-09-04, act: freeze, authority: human, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
  - { by: "plan:walk-truth", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
---
## CARD
goal: the walk emits every edge that exists, the payload can say which lesson declared each one, and the four checks that were supposed to prove the read is bounded and honest can actually fail.
why: okf-graph-lookup shipped a green 7/7 on a walk that silently loses concept edges, and on checks that pass for the defect they name. Two reviewers found it by injecting the defects rather than reading the tests. The loss is live: `.add/specs/method.md` declares M8 and M31 both refining #M4, and one of them is invisible through both new read verbs. That is the whole trust model inverted — a green gate proving nothing — so it is repaired before 3.5.0 ships, not after.
next: add freeze walk-truth

## SCOPE
In:  the relation row's identity and the FORMAT §11 `edges[]` schema that carries it · the four checks that cannot fail and the two defaults nothing compares · ref resolution for a name an operator actually types, and a bound on the ambiguity refusal.
Out: the JSON envelope's other guarantees (byte-stability, refusal exit codes, absent-key omission) — probed and holding. The membership arm and the two oracles' parity — attacked and clean. Engine minimisation, which is its own ask.

## GROUND
touches: add-method/tooling/add.py and its three twins · add-method/tooling/cli.py and its three twins · add-method/FORMAT.md §11 · add-method/tests/engine
risks:
  - the fix moves a schema this repo just pinned and told consumers to rely on. §11 is one release old and unpublished, so the window to change it without a migration closes when 3.5.0 ships — which is the argument for doing this first, not the argument for rushing it.
  - repairing a check that cannot fail may turn up further real defects it was hiding. That is the point; the budget has to allow for it.
  - the collapse is invisible by construction: nothing red today. A repair with no failing check to chase is exactly where a vacuous check gets written, so each repair here is proven by injecting the defect it names.

## EXIT
- [ ] a relation is identified by the lesson that declared it: two lessons refining one target emit two rows, and the payload names which lesson each came from   (relation-identity-in-the-walk)
- [ ] the walk's edge count on the live bundle equals what relations() and edges() together report, proven by comparing the two rather than by pinning a number   (relation-identity-in-the-walk)
- [ ] the four checks that could not fail now fail when their defect is injected: the cap's value, the refusal's verb, the cache independence, and the payload's present fields   (checks-that-cannot-fail)
- [ ] the CLI's --expand default and the engine's NEIGHBORHOOD_DEFAULT are compared by a check that reads both declarations   (checks-that-cannot-fail)
- [ ] a filename that names exactly one node resolves to it, and an ambiguity refusal is bounded the way the depth cap is bounded   (ref-resolution-accepts-what-an-operator-types)

## CLOSE
evidence: one row per task
