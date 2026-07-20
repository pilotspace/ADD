# Terms — the method's coined vocabulary (decode, don't guess)

The loop in `SKILL.md` uses a few compressed terms of art. This is their plain-language key —
load it once if a phrase reads opaque; it teaches nothing new about the flow, only names it.

| Term | Plain meaning |
|------|---------------|
| **the ARC** | the three-line frame every gate opens with — **A**im (the goal this serves) · **R**each (what is already covered) · **C**ourse (the plan the choice sets up). Engine-sourced, never invented. |
| **co-specify** | write the ranked ⚠ risk-flag *inside* §1 as you draft it — the flag and the rule it guards are specified together, not bolted on after. |
| **red for the right reason** | a §4 test fails because the behavior is genuinely absent, not because of a typo, bad import, or wrong fixture. Prove the failure message names the missing behavior before you build. |
| **covers: clause** | each §4 test bullet carries a `covers:` key naming the frozen §3 clause it proves — the link that lets `locate` map a failing test back to its contract clause. |
| **cross / re-cross** | *cross* = pass the one human approval that carries the task from direction into build (`freeze --cross`). *re-cross* = a post-freeze change reopened the contract, so the crossing must be earned again. |
| **compound-cross** | at `gate PASS`, the engine folds every open sub-check (evidence · lenses · target-hit) into one recorded crossing — you don't stamp each; the gate compounds them. |
| **earned-green refute-read** | before recording PASS, read the green suite *trying to disprove it* — is it green because the feature works, or because the test is weak? Green is earned, not assumed. |
| **auto-resolved PASS** | under `autonomy: auto`, a verify with complete, no-residue evidence records an explicit PASS without a human tap — an *auto-resolved* crossing, never a skip. Residue or lowered autonomy → a human decides. |

Everything else in `SKILL.md` is plain method language; when in doubt, the phase guide that owns the
beat (`phases/direction.md` · `phases/build.md` · `phases/verify.md`) defines it in full.
