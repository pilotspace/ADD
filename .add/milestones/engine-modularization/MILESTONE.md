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
- [x] `python3 .add/tooling/add.py status` (and every command) behaves byte-identically       (verify: full suite 1959/0 on main @693779b; every extract-* carries an identity test asserting `add.<name> is add_engine.<module>.<name>` + an output/behaviour test; AST source-segment diff of every moved symbol vs pre-move = verbatim)
- [x] the engine lives in `add_engine/*.py` as **13 focused modules** (constants · io_state · accessors · predicates · identity · guidelines · render · milestones · components · version · release · taskdoc · autonomy); `add.py` is the runnable **orchestrator entry** that re-exports the package's public + `_`-prefixed surface  (verify: `ls add_engine/*.py` = 13 modules; `add.py` 7049→5640 lines, −20%; the residual is the load_state/save_state/report_data/cmd_*/main spine — a connected web around the central state I/O that, per the closure analysis, IS the entry module. SCOPE DELTA: the original "thin entry shim / extract-guidelines-cli / migrate-test-imports" framing is superseded — load_state/save_state are pinned by the `_atomic_write` patch tests and deliberately kept, so the cmd_* dispatch above them stays; human-approved end-state 2026-06-26)
- [x] `ENGINE_MD5` (md5 of add.py) **and** `ENGINE_PKG_MD5` (manifest digest over `add_engine/*.py`) are literal pins; drift/tamper across the 3-tree mirror is still caught   (verify: engine_pin.py holds both as literals, never self-hashes (vacuous-pin guard); `engine_manifest.package_digest` == ENGINE_PKG_MD5 across all 3 trees every task; the tamper tripwire fired correctly in extract-autonomy on a mid-build test edit)
- [x] the pip wheel + `bin/cli.js init` + `prepare_bundle` ship the whole `add_engine/` package    (verify: `prepare_bundle.py` copies `tooling/` recursively incl. `add_engine/`; 3-tree byte-identical (canonical · `.add` · `_bundled`) green each task; `test_bundle_parity` passing)
- [x] the full suite is green after every task; no test weakened                          (verify: 1815→**1959** green across the 16 extractions; the ONE guard-test edit (`test_delta_grammar_dedup` scope-widen for the relocated `_DELTA_RE`) PRESERVED its `== 1` DRY invariant — search domain widened to the engine, assertion unchanged; seam audit clean 102)

## Close — ship review   (AI fills when every task is done)
> NOTE: the executed decomposition diverged from the breadth-first plan above. 16 tasks shipped
> (not the 13 planned slugs) — driven by transitive-closure AST closure analysis rather than the
> banner-region guess. Each was its own CI-green squash-merged PR. The 13 `add_engine` modules are
> the achieved layout; `add.py` is the orchestrator entry (spine kept — see exit-criterion #2).

### Ship by domain
- tooling : add.py 7049→5640; 13 `add_engine/*.py` modules behind a stable re-export surface; two-pin model (ENGINE_MD5 + ENGINE_PKG_MD5 manifest digest); `prepare_bundle` + `.add` mirror ship the package; engine NO-EXEC preserved
- skill   : untouched
- book    : untouched

### Cross-task evidence   (16 PRs, all CI-green admin-merged)
- engine-package-skeleton + extract-io-state/accessors/predicates/identity (tasks 1–6) : gate=PASS · suite green · residue=none
- extract-pure-leaves (7) : gate=PASS · residue=none (scope_violation self-corrected: test declared in §5 then re-crossed)
- extract-guidelines (8) : gate=PASS · suite green · residue=none
- extract-render (9, PR #85) : gate=PASS · 1893 green · residue=none (CONSTANT-BY-KIND: _ANSI private / _DEFAULT_WIDTH shared→constants)
- extract-milestones (10, #86) : gate=PASS · 1901 green · residue=none
- extract-components (11, #87) : gate=PASS · 1909 green (py3.10+3.12) · residue=none (tomllib guard replicated)
- extract-md5 (12, #88) : gate=PASS · 1919 green · residue=none (folded into io_state)
- extract-version (13, #89) : gate=PASS · 1928 green · residue=none (rebind-safe re-export)
- extract-release (14, #90) : gate=PASS · 1938 green · residue=none
- extract-taskdoc (15, #91) : gate=PASS · 1948 green · residue=none (3 shared regexes→constants; one DRY guard-test scope-widened, invariant preserved)
- extract-autonomy (16, #92) : gate=PASS · 1959 green · residue=none (tamper tripwire fired + honest re-baseline)

### Goal met?
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (all 5 cited with `(verify: …)`)
- goal: the engine is a navigable package, entry/mirror/pin preserved, suite green throughout — **MET** (13 focused modules + orchestrator entry; ENGINE_MD5/PKG pins + 3-tree mirror preserved; 1815→1959 green throughout)

## Release steps   (AI-DEFINED — engine records, human gate)
- [ ] open a PR per task (or one stacked PR) from the Close ship-review; the human reviews + merges
- [ ] no version bump on its own — fold into the next release cut (release.md) as a Changed entry ("internal: engine modularized; no behavior change")
