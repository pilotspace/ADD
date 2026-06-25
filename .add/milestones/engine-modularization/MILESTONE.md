# MILESTONE: Split the 7k-line add.py engine into a focused add_engine/ package

goal: the engine is a navigable package of focused modules behind a stable import surface, with the entry path, 3-tree mirror, and ENGINE_MD5 pin all preserved
rationale: new-major/sub-milestone (intake) — `add.py` is 7049 lines (42 commands, 177 helpers); it cannot be reviewed or tested per-concern as one atom, and any change re-pins the whole engine. The design pass (`tmp/design-split-engine-F12.md`, audit todo #12) sizes this as a milestone, not one task: the entry path, mirror, pin, and ~120 tests must stay green through each extraction.
stage: mvp · status: active · created: 2026-06-26

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  an `add_engine/` package whose modules map 1:1 to add.py's existing banner regions (constants · io_state · accessors · contracts · scope · audit · release · milestones · udd · render · guidelines · commands · cli); `add.py` kept as the runnable entry that re-exports the package's public surface; the `ENGINE_MD5` pin switched to a manifest digest over the whole package; `prepare_bundle` + both installers + the `.add` mirror shipping the package dir.
Out: any behavior change to the engine (pure refactor — same CLI, same gates, same outputs); renaming commands; touching the book/skill except where a path string names `tooling/add.py`; the optional final migration of test imports off the `import add` shim (its own deferred task).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Entry path is load-bearing** — `python3 .add/tooling/add.py …` must keep working unchanged (referenced 10× by the skill, in CLAUDE.md and the book). `add.py` stays the invoked file.
- **Pin = manifest digest (Option A, frozen)** — `ENGINE_MD5` stays a hard-coded literal (never self-computed); the test-side computation hashes a sorted manifest of `{filename: md5}` over `add.py` + every `add_engine/*.py`. One pin, one re-aim per task, covers the whole package.
- **Stable import surface** — `import add; add.<name>` keeps working (public AND `_`-prefixed) via re-export, so the ~120 test files are untouched by the split itself.
- **Monkeypatch hazard (validated)** — 54 sites in 11 test files patch `add._atomic_write` / `_fetch_latest_version` / `_render_template` / `_templates_dir`. A patch only intercepts internal calls while the function + its callers share a module, so the task that MOVES one of these 4 functions MUST, in the same task, repoint its patch sites to `add_engine.<module>.X`. No function may move ahead of its patch-site migration.
- **No behavior change** — the full suite (1815) is the regression gate; green after every task.

## Shared / risky contracts (freeze these first)
- the manifest-digest pin shape (`engine_files()` + `engine_digest()` semantics) -> owning task `engine-package-skeleton`
- the package layout + re-export surface -> owning task `engine-package-skeleton`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] engine-package-skeleton     depends-on: none                      — create `add_engine/` (`__init__` + first leaf module `constants`), keep `add.py` as the re-exporting entry, switch the pin to the manifest digest, teach `prepare_bundle` + both installers + the `.add` mirror to ship the dir; suite green, behavior byte-identical
- [ ] extract-io-state            depends-on: engine-package-skeleton   — move the low-level IO + state seam (`_atomic_write*`, load/save_state, `_require_root`/`find_root`, `_now`) to `add_engine/io_state.py`; repoint the `add._atomic_write` patch sites
- [ ] extract-accessors           depends-on: extract-io-state          — move the active milestone/task accessor seam
- [ ] extract-contracts           depends-on: extract-accessors         — move freeze/tripwire (`_build_entry`, `_contract_snapshot`, `_tripwire_snapshot`, heal)
- [ ] extract-scope               depends-on: extract-contracts         — move the scope gate + component helpers
- [ ] extract-audit               depends-on: extract-scope             — move the seam audit
- [ ] extract-release             depends-on: extract-audit             — move release/CHANGELOG/RELEASES + fold/compact
- [ ] extract-milestones          depends-on: extract-release           — move milestone/ledger/wave/archive
- [ ] extract-udd                 depends-on: extract-milestones        — move the UDD token/catalog/lint validators
- [ ] extract-render              depends-on: extract-udd               — move the report dashboard + md_section; repoint `_render_template`/`_templates_dir` patch sites
- [ ] extract-guidelines-cli      depends-on: extract-render            — move sync-guidelines + build_parser/main into `guidelines.py`/`cli.py`; `add.py` becomes the thin shim; repoint `_fetch_latest_version` patch site
- [ ] migrate-test-imports        depends-on: extract-guidelines-cli    — (optional, last) migrate test files from `import add` to `from add_engine import …`; drop the back-compat re-export

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `python3 .add/tooling/add.py status` (and every command) behaves byte-identically       (← engine-package-skeleton + every extract-*)
- [ ] `add.py` is a thin entry shim; the engine lives in `add_engine/*.py`, each a focused module  (← extract-guidelines-cli)
- [ ] `ENGINE_MD5` is a manifest digest; drift/tamper across the 3-tree mirror is still caught   (← engine-package-skeleton)
- [ ] the pip wheel + `bin/cli.js init` + `prepare_bundle` ship the whole `add_engine/` package    (← engine-package-skeleton)
- [ ] the full suite (≥1815) is green after every task; no test weakened                          (← every task)

## Close — ship review   (AI fills when every task is done)
### Ship by domain
- tooling : <add.py → add_engine/ package; engine_pin digest; prepare_bundle; installers>
- skill   : <untouched — only path strings, if any>
- book    : <untouched>

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS> · tests=<n green> · residue=<none|note>

### Goal met?
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: the engine is a navigable package, entry/mirror/pin preserved, suite green throughout

## Release steps   (AI-DEFINED — engine records, human gate)
- [ ] open a PR per task (or one stacked PR) from the Close ship-review; the human reviews + merges
- [ ] no version bump on its own — fold into the next release cut (release.md) as a Changed entry ("internal: engine modularized; no behavior change")
