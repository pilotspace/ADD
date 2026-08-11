# Beat 2 · Build — code to green, inside the frozen lines

Everything you need is fixed. Build runs fast and safe because Direction already set it.

## The entry is the brief

`add brief <slug>` is Build's FIRST verb, not a convenience: on a frozen task it records an
`act: brief` stamp — the sealed direction becoming the working prompt — and the gate refuses
a PASS whose receipts predate that entry (a brief compiled after the build entered nothing;
the fix is a re-run under it). Compile it, work from it. `depth: quick` is exempt.

## The one job

Write code in the repo until **every red check is green**. That is the whole target — not "code that
looks done", but "the suite the human froze now passes".

## The three lines you may not cross

1. **Change no check.** A check that is hard to pass is telling you something about the code, not about
   the check. Weakening it to get green inverts the method.
2. **Move no frozen `gives:`.** Its internals may change freely; its external interface may not. A real
   interface change is a change-request back to Direction (a `refreeze` stamp; dependents that `need:`
   it go stale) — never a silent edit.
3. **Stay inside `scope:`.** The paths in the node's `scope:` are the freshness set the gate will hash.
   Touching a path outside scope means the node is mis-scoped — fix the scope in Direction, don't sneak
   the edit.

## Steering vs contract — record the turn, keep the seal

Mid-build discovery that changes NO frozen surface — strategy, sequencing, a discovered
constraint, a scope observation — is **steering**: record it with `add replan <slug> --note
"<what changed and why>"` and keep building. The stamp lands on the node's trail at process
authority; the seal never moves, and the gate is indifferent to it. Anything that would move a
frozen `gives:` or a check is a **change-request** back to Direction (a `refreeze` stamp),
exactly as the three lines above demand. Consult the split at the moment of discovery, before
any edit — an unrecorded steer is where method-bypassing starts.

## When a check outside your suite fails

A failure in a test your node does not own means you crossed a boundary. Locate its owning node and the
frozen clause it proves before continuing; if a settled contract genuinely must move, that is a
change-request with its own re-verification, not a quiet patch here.

## Batch small, stay legible

Direct the build in small batches so the human can follow it. Progress for a node in `build` is read
from the working tree (`git status` intersected with `scope:`) — not stored, always current. When every
check is green and the residue is clean → `phases/verify.md`.
