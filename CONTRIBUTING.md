# Contributing — repo layout & the edit-then-sync model

This repo is three things at once: the **ADD book**, the **`add` skill**, and the **shippable
package** (`@pilotspace/add` on npm, `pilotspace-add` on PyPI). A few artifacts are mirrored across
trees, and **every mirror is either generated or guarded by a test**, so none can silently drift.
Read this before editing, so you change the canonical copy and let the rest follow.

## The trees

| Tree | Role | Canonical? | Kept honest by |
|---|---|---|---|
| `add-method/skill/add/` — `SKILL.md`, `references/`, `persona-author/` | **The method** | ✅ **edit here** | `tests/test_skill_only.py` |
| `add-method/personas/`, `personas-teacher/`, `personas-index/` | starter personas, the vendored teacher corpus, its routing index | ✅ **edit here** | `scripts/build_persona_index.py`, `scripts/update_teacher.py` |
| `add-method/docs/` | **The book**, published by MkDocs (`mkdocs.yml` at the root) | ✅ **edit here** | `tests/book/` · `scripts/book_lint.py` |
| `add-method/src/add_method/_bundled/` | what ships inside the Python wheel | ❌ generated | `scripts/prepare_bundle.py` → `tests/test_npm_pip_parity.py` |
| `.claude/skills/add/` | the dogfood skill — this repo runs `/add` on itself | ❌ byte mirror of `add-method/skill/add/` | `tests/test_skill_only.py` |
| `.add/` | the **live dogfood bundle** — real ADD work on this repo, not a copy | ✅ its own data | — |
| `archive/` | earlier bundles (2.x, 3.x), kept as history | read-only | — |
| root `GETTING-STARTED.md` | a **pointer** to the package's guide — deliberately not a copy | ❌ pointer | — |

## The one rule

**Edit the canonical tree (`add-method/`), then propagate.** Never hand-edit a generated tree
(`_bundled/`) or one side of a mirror in isolation — a test will fail in CI.

After changing anything under `add-method/skill/` or `add-method/personas*/`:

```bash
# 1. regenerate the wheel bundle
python3 add-method/scripts/prepare_bundle.py

# 2. refresh the dogfood skill mirror
rm -rf .claude/skills/add && cp -R add-method/skill/add .claude/skills/add

# 3. verify nothing drifted
cd add-method && python3 -m pytest -q
```

After changing the book, run `python3 add-method/scripts/book_lint.py` (nav, links, and no
instructions that point at the retired 3.x CLI) and, if you have MkDocs installed,
`mkdocs build --strict` from the repo root.

## Working on this repo with ADD

This repository dogfoods the method. Orient on `.add/PROJECT.md` and the open task files, size
the change, and follow the skill: Quick for small edits; a task file sealed with a
`freeze(<slug>)` commit for anything worth a contract; a `verify(<slug>): <verdict>` commit with
the evidence. `invariants:` in `.add/PROJECT.md` bind every change.

## Running the suite

CI (`.github/workflows/ci.yml`) runs the package suite on Python 3.10 and 3.12:

```bash
cd add-method && python3 -m pytest -q
```

A few tests shell out to `node` / `npm` / `pip` to exercise the installers, so they need those
tools installed.

## Releasing

One version tag publishes both registries; the recipe is in [`RELEASING.md`](./RELEASING.md).
