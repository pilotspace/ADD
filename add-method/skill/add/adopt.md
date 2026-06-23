# Adopt — map an existing repo into the foundation (silent)

When ADD is pointed at a repo that already has code, onboarding is **silent**: the code answers the questions a greenfield interview would ask, so you read it rather than ask. This is the **brownfield path** of setup. You fill the living-documentation files from evidence, then stop at the one human gate: the **baseline approval** (`add.py lock`).

## The signal — and arming the gate

Enter a brownfield repo with `--await-lock`:

```bash
python3 .add/tooling/add.py init --await-lock
```

`--await-lock` seeds an **unlocked** setup, *arming the baseline-approval gate* — the engine refuses crossing into build until you `lock`. Init prints:

```
brownfield: existing code detected — the `add` skill maps it into your foundation …
```

That line is your cue. **Always use `--await-lock` for brownfield**: a plain `init` is grandfathered-locked, so its gate never arms *and* the closing `lock` would refuse with `already_locked`.

## The silent mapping

Fill each living-doc file in `.add/` from what the code shows — **ask nothing**:

| Living doc | Read it from |
|----------|--------------|
| `PROJECT.md` (foundation) | domain nouns, entry points, README, first milestone the code implies |
| `CONVENTIONS.md` | languages, folder layout, naming, lint config, error style in the tree |
| `GLOSSARY.md` | recurring names in modules, models, and public APIs (one name per concept) |
| `MODEL_REGISTRY.md` | leave the active model record; note any AI-authored code you detect |
| `dependencies.allowlist` | manifests already in the repo (package.json, pyproject, go.mod, …) |

<constraints>
1. **Never clobber a living doc.** `init` already skips any living-doc file that exists; if a human already wrote `PROJECT.md`, READ it, do not overwrite it. Add, never replace.
2. **Tag every drafted decision `evidence-grounded` vs `guessed`.** A line you read from the code is *evidence-grounded* (cite the file). A line you inferred because the code was silent is *guessed*. The human's single baseline approval is only honest if they can see which is which — the guesses are what they actually need to check. (The tags feed `SETUP-REVIEW.md`.)
</constraints>

## Where it ends — the baseline approval

Brownfield onboarding draws no per-step approvals: map the foundation, draft the first milestone's scope and first task's candidate specification bundle, then present it all at **one** human gate. The human reviews decisions (`guessed` first) and confirms; you run the lock:

```bash
python3 .add/tooling/add.py lock --by "<name>"
```

`lock` freezes the foundation + scope + first contract in one atomic write and opens the build. Until it runs, the engine refuses crossing into build.
