---
type: Milestone
title: All-domain evidence — the trust spine, reachable from any domain
status: direction
generated: { by: add/3.1.0, at: 2026-08-12 }
verified: []
advised_by: method-steward
---
## CARD
goal: a finance, research or ops task earns the same bound `test-ids` receipt a code task does — with no engine change
why: the mechanism already works and nobody knows it. Proved on a live reconciliation node (materiality Must + citation Reject, checker in project space): `kind: test-ids`, both `covers:` referents bound, `freshness: content` blob-digested on a JSON data file, and BOTH refusals fired — stale data and a blown threshold. What is missing is that nothing in the skill tells an agent it may WRITE a checker instead of FIND a runner. The gap is documentation, not capability — so the honest fix is ~61 lines of skill surface, not an evidence-adapter engine feature.
next: add freeze all-domain-evidence

## SCOPE
In:  `skill/add/domains.md` (new ref) · `SKILL.md` profile-truth + checker pointer · `phases/verify.md` ladder honesty · finance/legal/academic corpus depth + routing index · all THREE skill trees
Out: engine bytes (`add.py` · `cli.py`) — including the one true residual, making `init` refuse an unknown `--profile`; deferred by human constraint, not because it is unreal · new profiles · new floor names · new evidence rungs · the book chapter (rides after)

## GROUND
touches: add-method/skill/add/{SKILL.md,domains.md,phases/verify.md} × 3 trees (`skill/add/`, `src/add_method/_bundled/skill/add/` — both git-tracked — and the GITIGNORED `.claude/skills/add/`, which needs a manual cp); add-method/personas-teacher/{finance,academic}/; add-method/personas-index/use-when.md; add-method/tests/skill/
risks:
  - a new ref file pushes total skill surface past the 1500 pin (1422 now — 78 free; the plan spends 61)
  - the checker recipe reads as "a pack may define what passes" — that inverts the additivity promise; the recipe must only ever show how to AUTHOR evidence, never how to earn a gate more cheaply
  - the gitignored `.claude/skills/add/` twin drifts silently — it has no parity test
  - `.add/personas/method-steward.md` still pins SKILL.md at 150; the real pin is 176 (re-pinned at 3.1.0, human call) — a stale persona will reject a conforming plan

## EXIT
- [ ] a non-code domain task earns `kind: test-ids` with `covers:`-bound checks, proved by a dogfood test that runs the recipe end-to-end — never by prose   (← domain-evidence-recipe)
- [ ] every evidence rung the skill documents is one the engine can actually stamp   (← ladder-honesty)
- [ ] `SKILL.md` ≤ 176 lines and total skill surface ≤ 1500 after every task   (← skill-pointer-truth)
- [ ] no floor sentence reworded and no floor name introduced outside `security · data · architecture`   (← domain-evidence-recipe)
- [ ] the three skill trees stay byte-identical   (← skill-pointer-truth)
- [ ] the routing index reaches finance/legal/academic at a pinned floor   (← corpus-depth)

## CLOSE
evidence: <one row per task>
