# 13 · Files and commits

[← 12 The .add/ bundle — ABF-1 format](./12-bundle-format.md) · [Contents](./README.md) · Next: [14 The foundation and the five living specs →](./14-foundation.md)

---

ADD has no commands of its own. Everything it does is a file edit, a git command, or the project's test command. This page is the quick reference: which file each step writes, and which commit records it.

## Orient

| step | how |
|---|---|
| read the project | `.add/PROJECT.md` — `goal:`, `invariants:`, `test_cmd:`, and the CARD's `state:`/`next:` |
| find open work | `grep -lE '^status: (direction\|build\|active)' .add/tasks/*.md .add/milestones/*.md` |
| recent history | `git log --oneline -15` |
| one task's history | `git log --oneline --grep='(<slug>)'` |

In Claude Code, `/add status` asks the skill to do the above and summarize.

## The commits the method writes

| commit message | when | what it contains |
|---|---|---|
| `freeze(<slug>): <goal>` | end of Direction, checks red | the task file (`status: build`) and every check file named in CHECKS — the seal |
| `refreeze(<slug>): <why>` | the contract was wrong and changed | the edited task file and checks, with the reason under `## LOG` |
| *(ordinary commits)* | during Build | code and non-sealed tests, any message style the repo uses |
| `verify(<slug>): <verdict>` | end of Verify | the task file with `## EVIDENCE` written and `status: done` (or `build` on a `HARD-STOP`) |
| `<type>(<scope>): <what>` | a Quick change | the test and the fix, with a one-line why |

An Explore task uses the same `freeze` and `verify` commits; its `## FINDINGS` are committed with the verify commit.

## The seal check

```bash
F=$(git log -1 --format=%H --grep='freeze(<slug>)')     # also matches the latest refreeze(<slug>)
git diff $F HEAD -- .add/tasks/<slug>.md <check files>   # must print nothing
```

## The fresh run

On a clean tree (`git status` shows nothing), run the task's `check:` command, then its `regression:` command, and record each as `` `<command>` → exit <code> · <counts> `` in `## EVIDENCE`.

## Which file holds what

| you want | it is in |
|---|---|
| the project's goal and invariants | `.add/PROJECT.md` |
| what a task must do and refuse | the task file, `## RULES` |
| what the agent guessed | the task file, `## ASSUMPTIONS` |
| why the contract changed | the task file, `## LOG`, and the `refreeze` commit |
| whether it was verified, and on what | the task file, `## EVIDENCE`, and the `verify` commit |
| what a milestone must prove | the milestone file, `## EXIT` |
| decisions every task must follow | `.add/specs/<lens>.md`, `## Decisions that bind` |
| lessons not yet settled | `.add/specs/<lens>.md`, `## Deltas` |
| an expert lens | `.add/personas/<name>.md` |
