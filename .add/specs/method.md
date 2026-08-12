---
type: Spec
title: Method
lens: method
project: AIDD-Book
generated: { by: add/3.0.0, at: 2026-08-08 }
---
## Now
how work proceeds, and what a gate costs

## Decisions that bind
- <the first decision that constrains the rest>

## Deltas
- <what changed, and the evidence that changed it>
- [ADD · open] an engine change invalidates PROSE, and the skill is prose: profile-refusal made init refuse, which turned two shipped skill sentences false across three trees within minutes. The dangerous instance was the one used as a RULE'S REASON — domains.md said 'do not invent a profile BECAUSE it fails silently'; the rule survived, its reason did not, and a reader who tests a false reason has cause to discard the rule (evidence: .add/tasks/skill-profile-truth.md)
- [ADD · open] reopen refuses anything not done, so a task caught mid-build repairs by re-freeze; reopen is for a task already CLOSED — and it takes --to plus --reason, which puts the miss on the permanent record instead of hiding it in a silent second gate (evidence: .add/tasks/front-door-truth.md)
- [ADD · open] a gate PASS proves the checks you DECLARED ran and bound — it cannot prove the rule was fully covered. M5 said 'every engine command a README shows' and its check executed only <engine>.py <verb> forms, so the same commit that fixed four false claims shipped a fifth (npx init --profile doc) straight through a green gate. When a rule quantifies over a set, enumerate the set in the check (evidence: .add/tasks/front-door-truth.md)
- [ADD · open] gate refuses with R:UNBRIEFED when no `brief` ran since the last (re)freeze — a refreeze invalidates the compiled prompt, so the repair order is refreeze -> brief -> run -> gate, not refreeze -> run -> gate (evidence: .add/tasks/front-door-truth.md)
- [ADD · open] a doc that shows a command must have that command EXECUTED by a check — the root README told readers to run `add.py status` three times, which exits 0 and prints nothing because add.py is the library the CLI dispatches into; the package README said so on its own install table while the root README contradicted it (evidence: .add/tasks/front-door-truth.md)
- [ADD · open] guard the ORPHAN direction for refs, not just verbs — a doc naming a missing verb was already caught, but a ref no always-loaded file names shipped unreachable and passed ten bound checks; the new guard immediately found a SECOND orphan (terms.md) nobody knew about (evidence: add-method/tests/skill/test_router_pointers.py::test_no_orphan_refs)
- [ADD · open] an `n/a` retires a sweep DIMENSION, never an EDGE — an E<n> line is a gate referent whatever it says, so a 'dissolved' edge must be DELETED or given a check; writing 'E1 n/a' still holds the PASS (evidence: /tasks/receipt-artifact-leak.d/runs/1.md)
- [ADD · open] a task's scope: MUST include the directory its own CHECKS live in — otherwise a defective check cannot be repaired during build, and the only in-scope 'fix' is to reshape the artifact around the broken test (evidence: /tasks/receipt-artifact-leak.md scope: omits add-method/tests/skill)
- [ADD · open] a frozen contract on a not-yet-done task is repaired by a bare re-freeze (the engine records act: refreeze with a fresh direction hash) — reopen refuses a non-done task and replan seals untouched, and no skill doc names the real path (evidence: /tasks/domain-evidence-recipe.md verified[])
- [ADD · open] a covers: citation must be the exact qualified ID or a BARE test name — the path.py::name form resolves to neither, so nothing binds and the gate refuses every rule (evidence: add-method/tooling/add.py:3008)
- [ADD · open] the gate binds EVERY covers referent, EDGES included — an E<n> authored with no covering check refuses the PASS just as a Must would (evidence: /tasks/domain-evidence-recipe.d/runs/2.md)
- [ADD · open] a persona that hard-codes a budget number rots when the budget is re-pinned — method-steward still says SKILL.md <=150 while the real pin is 176; personas should cite the pin's test, not copy its value (evidence: add-method/tests/skill/test_surface.py:37)
- [ADD · folded] edge-list frontmatter (depends_on/needs) must be BLOCK lists — inline [a, b] flow parses in the engine's T0 but not in the M0 validator; the parity oracle catches it on the live bundle (evidence: /tasks/sources-receipt.md)
- [ADD · folded] any angle-bracketed text in a gives: entry — even inside a backticked example path — reads as unauthored scaffold and blocks freeze; keep gives: literals bracket-free (evidence: /tasks/explore-lane.md)
