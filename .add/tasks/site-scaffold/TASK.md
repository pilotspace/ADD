# TASK: MkDocs Material site scaffold over the canonical book

slug: site-scaffold · created: 2026-06-24 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `mkdocs.yml` (repo root) — NEW · the site config: `site_name`, `docs_dir: add-method/docs`, `theme.name: material`, `nav:` (ordered), `plugins: [search]`, `theme.palette` (dark/light toggle). The riskiest contract.
- `add-method/docs/index.md` — NEW · the home/landing page (docs_dir currently has `README.md` H1 "AI-Driven Development" 4.1K but NO `index.md`; Material uses index.md as site root).
- `requirements-docs.txt` (repo root) — NEW · pins `mkdocs-material` (build-time only — keeps the published package zero-dep; see Honors).
- `.gitignore` (repo root) — EDIT · add `site/` (MkDocs default build output, currently un-ignored).
- READ-only source (the book, single source of truth): `add-method/docs/` = 17 chapters `00-introduction.md`→`16-releasing.md` + 7 appendices `appendix-a..g` + 4 PNG (`add-competencies/flow/foundation/hierarchy.png`). All 24 .md carry a clean `# ` H1 (nav labels). PNGs referenced `./<name>.png` (in-dir, relative). ~165 markdown links, ALL sibling-relative (`./x.md`/`#anchor`) — 0 parent/absolute/`.add/` links (grep-verified) → strict-build link resolution is in-tree.

Context (working folder):
- `add-method/pyproject.toml` — `pilotspace-add`, `dependencies = []` (the published package is zero-dep; do NOT add mkdocs there).
- `add-method/package.json` — `@pilotspace/add` 1.9.0, `homepage` → GitHub README (pages-deploy task updates this, not this task).
- `.gitignore` — already ignores `.add/docs/` (dogfood copy) + `add-method/.add/`; the site build reads `add-method/docs/` (canonical) only.
- `add-method/docs/README.md` — present in docs_dir; with an explicit `nav:` it must be included OR excluded, else `--strict` warns "not in nav".

Honors (patterns / conventions):
- (CONVENTIONS) lean-dependency posture — engine is stdlib-only; the published package stays `dependencies = []`. mkdocs-material is a BUILD-TIME dep, declared in one place (`requirements-docs.txt`), never a runtime/package dep.
- (PROJECT §Spec) "a new runtime dependency falsifies any zero-dep prose" — mkdocs is build-time, so it does NOT falsify the package's zero-dep claim; keep that boundary explicit.
- (MILESTONE shared decisions) single source = canonical `add-method/docs/` in place (no copy); `mkdocs build --strict` is the red/green seam.

Anchors the contract cites (the NEW config keys §3 freezes):
- `mkdocs.yml` keys: `site_name` · `docs_dir: add-method/docs` · `theme.name: material` · `theme.palette` (scheme toggle) · `plugins: [search]` · `nav:` (ordered: Home=index.md → 00..16 → appendix a..g)
- `add-method/docs/index.md` (site root) · `requirements-docs.txt` (mkdocs-material pin) · `.gitignore` += `site/`
- verifier: `mkdocs build --strict` exits 0 producing `site/index.html` + every chapter/appendix HTML + the 4 PNGs.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: MkDocs-Material site scaffold that renders the canonical AIDD book from `add-method/docs/` as a navigable, searchable static site.
Framings weighed: explicit `nav:` in mkdocs.yml (chosen — deterministic order/labels, handles README, no extra plugin) · auto-nav via awesome-pages plugin (adds a dep + per-dir `.pages`, less control) · directory-URLs with no nav (loses chapter ordering).
Must:
<must>
  - a `mkdocs.yml` at repo root sets `site_name`, `docs_dir: add-method/docs`, `theme.name: material`, a `theme.palette` dark/light scheme toggle, and `plugins: [search]`.
  - the EXISTING `add-method/docs/README.md` is the site home — MkDocs maps `README.md` → `index.html` at the site root; NO new file is added to the book (book source stays byte-unchanged).
  - `mkdocs.yml` carries an explicit ordered `nav:` — `Home: README.md` → chapters `00-introduction`…`16-releasing` (in number order) → appendices A…G. Every `docs_dir` book page is in nav (no orphan).
  - the 4 PNG diagrams render in their chapters (they are inside `docs_dir`, so the build copies them).
  - `requirements-docs.txt` at repo root pins `mkdocs-material` (build-time dependency only).
  - `.gitignore` ignores the MkDocs build output `site/`.
  - `mkdocs build --strict` exits 0 and writes `site/index.html` (from README.md) plus one HTML page per chapter and appendix.
</must>
Reject:
<reject>
  - a `nav:` entry points to a file not in `docs_dir` -> "nav_target_missing"   (strict build fails)
  - a `.md` in `docs_dir` is in neither `nav:` -> "orphan_page"   (strict warns → fails under --strict; every book page must be listed)
  - `mkdocs-material` is added to the PUBLISHED package deps (`pyproject.toml` `dependencies` / `package.json` `dependencies`) -> "runtime_dep_leak"
  - the `site/` build output is left un-ignored (committable) -> "build_artifact_tracked"
</reject>
After:
<after>
  - running `mkdocs build --strict` from repo root produces a warning-free static `site/` containing the whole book (README home + 17 chapters + 7 appendices + 4 diagrams), with working client-side search and a dark/light toggle; the book source under `add-method/docs/` is byte-unchanged (no new file, no bundle/parity change), and the published package's dependency lists are unchanged (still empty).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ MkDocs maps `README.md` → the directory home (`index.html`) when no `index.md` is present, and a nav entry `Home: README.md` resolves to it — lowest confidence because this is MkDocs default behavior I should confirm on the installed version (not a config I set); if wrong: the site root 404s or README strict-warns, fixed by either adding a thin site-only `index.md` OUTSIDE the bundle path or setting the nav home explicitly (localized to mkdocs.yml).
  - [ ] `mkdocs-material` installs cleanly in the verify environment (it is on PyPI) — if the env is offline, the `--strict` verifier can't run; confirm pip access at tests/build.
  - [ ] every chapter/README `[x](./y.md)` link resolves under --strict — grounding found 0 parent/abs/`.add` links (all in-tree); confirm clean at build.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: strict build produces the whole book
  Given mkdocs.yml (docs_dir=add-method/docs) exists and README.md is the home
  When I run `mkdocs build --strict` from the repo root
  Then it exits 0 and site/index.html (from README.md) plus one HTML page per chapter (00..16) and appendix (a..g) is written
  And the 4 PNG diagrams are copied into site/

Scenario: nav is the full book in reading order
  Given mkdocs.yml has an explicit nav
  When I read the nav list
  Then the entries are Home (README.md) then chapters 00-introduction..16-releasing in number order then appendices A..G

Scenario: README is the home, book unchanged
  Given add-method/docs/README.md already exists and no index.md is added
  When site/index.html is rendered
  Then it is README.md (what ADD is + the book TOC) served at the site root
  And no new file was added to add-method/docs/ (the book source is byte-unchanged)

Scenario: search and dark/light are on
  Given the Material theme is configured
  When I inspect mkdocs.yml
  Then `plugins:` includes `search` and `theme.palette` defines a dark/light scheme toggle
  And the built site/ contains the search index (search/search_index.json)

Scenario: diagrams render in their chapters
  Given the 4 PNGs sit in docs_dir next to the chapters that reference them with ./<name>.png
  When the site builds
  Then each referenced PNG resolves (no missing-image warning under --strict)

Scenario: docs dependency is build-time only
  Given requirements-docs.txt pins mkdocs-material
  When I read add-method/pyproject.toml and add-method/package.json
  Then mkdocs-material appears in neither's dependency list (the published package stays zero-dep)

Scenario: build output is ignored
  Given MkDocs writes site/ on build
  When I read .gitignore
  Then site/ is listed so the build output is never committed

# --- rejections ---

Scenario: a nav entry to a missing file fails the build   # nav_target_missing
  Given a nav entry points at a file not in docs_dir
  When I run `mkdocs build --strict`
  Then it fails with a missing-doc error and writes no site/
  And no partial/empty site/ is left committed (site/ stays ignored)

Scenario: an un-listed page fails strict   # orphan_page
  Given a book .md in docs_dir is absent from nav
  When I run `mkdocs build --strict`
  Then it fails on the not-in-nav warning
  And the fix is to add it to nav (every book page is listed; no book file is deleted)

Scenario: docs dep must not leak into the package   # runtime_dep_leak
  Given mkdocs-material is the docs build dependency
  When pyproject.toml `dependencies` and package.json `dependencies` are read
  Then mkdocs-material is absent from both
  And both dependency lists remain exactly as before this task (still empty)

Scenario: the build artifact must stay untracked   # build_artifact_tracked
  Given a `mkdocs build` has produced site/
  When I run `git status`
  Then site/ is ignored and shows no tracked files
  And no file under site/ is added to the index
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CONFIG CONTRACT — a MkDocs site over the canonical book (no HTTP; the "shape" is the files + build behavior)

FILES PRODUCED (exact paths):
  mkdocs.yml                       (repo root, NEW) — required keys:
      site_name: <string>
      site_url:  <string>                         # the Pages URL (filled/confirmed in pages-deploy; placeholder OK here)
      repo_url:  https://github.com/pilotspace/ADD
      docs_dir:  add-method/docs
      theme:
        name: material
        palette: [ {scheme: default,...}, {scheme: slate,...} ]   # dark/light toggle (≥2 entries)
      plugins: [ search ]
      nav:                                          # explicit + ordered, every book page listed:
        - Home: README.md                           # MkDocs maps README.md -> index.html
        - <17 chapters 00-introduction.md .. 16-releasing.md, in number order>
        - <7 appendices appendix-a..g, in letter order>
  requirements-docs.txt            (repo root, NEW) — exactly: mkdocs-material (pinned, e.g. >=9,<10)

FILES EDITED:
  .gitignore                       — add a line: site/

NOT TOUCHED (decision: keep the home OUT of the book):
  add-method/docs/**               — NO new file; README.md (existing) is the home; book source byte-unchanged
  _bundled/docs/ + scripts/prepare_bundle.py — untouched (no bundle/parity change, since the book is unchanged)

BUILD BEHAVIOR (the verifier):
  `mkdocs build --strict`  (run from repo root)
     exit 0  -> writes site/index.html (README.md) + 1 HTML page per chapter (00..16) + per appendix (a..g) + copies the 4 PNGs + search/search_index.json
     exit !=0 -> on any of:  nav_target_missing (nav entry ∉ docs_dir) | orphan_page (docs_dir book .md ∉ nav) | a broken in-tree link

INVARIANTS (must hold after build):
  - add-method/pyproject.toml `dependencies` == []           (no runtime_dep_leak)
  - add-method/package.json   `dependencies` unchanged       (no runtime_dep_leak)
  - .gitignore contains `site/`                              (no build_artifact_tracked)
  - add-method/docs/ is byte-unchanged — no file added, renamed, or deleted (README.md stays as-is)
  - add-method/src/add_method/_bundled/docs/ untouched → test_bundle_parity stays green with no regeneration
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: ⚠ [contract] README.md → site home relies on MkDocs' default README→index.html mapping (no index.md added) — if the installed MkDocs version doesn't map it, the site root 404s / strict-warns; fix is a thin site-only index.md outside the bundle path or an explicit nav home, localized to mkdocs.yml. Secondary [spec]: mkdocs-material must be pip-installable in the verify env (the build test skips + records if absent).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject scenario has one test (config + build assertions; no Python src to cover).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_mkdocs_config_keys: parse mkdocs.yml / assert site_name, docs_dir=="add-method/docs", theme.name=="material", plugins includes "search", theme.palette has ≥2 schemes (dark/light)
  - test_nav_is_full_book_in_order: parse nav / assert order == Home(README.md) then 00..16 then appendix a..g; every nav target file exists in docs_dir
  - test_readme_is_home_book_unchanged: assert nav home == README.md AND no index.md was added to add-method/docs/ (the book .md set is exactly the 24 known files — README + 17 chapters + 6... i.e. 7 appendices)
  - test_search_and_palette_present: assert mkdocs.yml plugins has search AND palette toggle (two schemes with a switch)
  - test_docs_dep_build_time_only (runtime_dep_leak): assert requirements-docs.txt pins mkdocs-material; assert "mkdocs" absent from pyproject.toml [project].dependencies AND package.json dependencies
  - test_site_gitignored (build_artifact_tracked): assert ".gitignore" contains a "site/" line
  - test_strict_build_produces_site (strict build + nav_target_missing + orphan_page + diagrams): if `mkdocs` importable -> run `mkdocs build --strict` in a tmp site_dir; assert exit 0, index.html (from README) + every chapter/appendix .html + the 4 PNGs + search_index.json present; else pytest.skip("mkdocs not installed") with a recorded reason
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/../mkdocs.yml` `add-method/../requirements-docs.txt` `add-method/../.gitignore`   <repo-root files via the `add-method/..` climb — a slash-bearing token resolves at project root; a BARE name would resolve to the task dir (the cause of the first scope_violation). No add.py/engine/book/bundle edit.
Strategy (ordered batches):
  1. write `mkdocs.yml` (site_name · docs_dir: add-method/docs · material theme + palette toggle · search plugin · explicit ordered nav with `Home: README.md` first).
  2. write `requirements-docs.txt` (`mkdocs-material` pinned).
  3. add `site/` to `.gitignore`.
  4. `pip install -r requirements-docs.txt` (or confirm mkdocs present) and run `mkdocs build --strict`; resolve any orphan/link warning by adjusting nav in mkdocs.yml only.
Safety rule (feature-specific): touch NO file under `add-method/docs/` — the book (incl. README.md) stays byte-unchanged, so `_bundled/docs/` + bundle parity need no regeneration; never edit a test or the §3 contract to make strict pass — fix the config.
Code lives in: repo root (`mkdocs.yml`, `requirements-docs.txt`, `.gitignore`) only.
Constraints: do NOT change any test or the contract; allow-list packages only (mkdocs-material build-time only); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 7/7 green (docs venv: mkdocs 1.6.1, mkdocs-material 9.x, PyYAML 6.0.3)
- [x] coverage did not decrease — new task; 7 tests added (was 0), one per Must/Reject + a real strict build
- [x] no test or contract was altered during build — only §5-scoped files written; tamper tripwire snapshot intact
- [x] the green was EARNED, not gamed — the strict-build test runs a REAL `mkdocs build --strict` and asserts 24 chapter/appendix pages + README home + 4 PNGs + search index; config tests assert exact nav order + key values (no vacuous/overfit/stub)
- [x] concurrency / timing — N/A (static site build, no concurrent/timed operation)
- [x] no exposed secrets, injection openings, or unexpected dependencies — mkdocs.yml carries no secrets; one declared build-time dep (mkdocs-material) in requirements-docs.txt; no runtime dep added
- [x] layering & dependencies follow CONVENTIONS.md — dep is build-time only; published packages stay `dependencies = []`; book/bundle untouched
- [~] a person reviewed and approved the change — AUTO-RESOLVED under `autonomy: auto` (no security / no residue: infra/config, not a method/trust-layer edit); presented to the human as FYI; milestone CLOSE + pages-deploy remain human gates

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `mkdocs build --strict` exits 0 with NO warnings — confirmed: exit=0; build log grepped, zero nav/link/image WARNINGs (the only red text is Material's MkDocs-2.0 vendor banner, not a build warning)
- [x] the built `site/` has `index.html` + one page per chapter (00..16) + per appendix (a..g) + the 4 PNGs + `search/search_index.json` — confirmed by listing site/: index.html + 24 chapter/appendix pages + 4 PNGs + search/search_index.json
- [x] opening the site shows a working dark/light toggle and a search box — confirmed by HTML grep of the rendered site/index.html: `data-md-component="search"` + `md-search__input`; `__palette` + `data-md-color-scheme` + "Switch to dark/light mode"
- [x] `add-method/pyproject.toml`/`package.json` dependency lists are unchanged (still empty) — confirmed by `git status --porcelain` clean on both
- [x] `add-method/docs/` is byte-unchanged (no new/renamed/deleted file) — confirmed by `git status --porcelain add-method/docs/ _bundled/docs/` clean; README is the home (MkDocs maps README→index.html), so no bundle regeneration was needed and parity holds untouched

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read mkdocs.yml end-to-end (every nav target maps to a real `add-method/docs/*.md`; docs_dir is canonical; palette has both schemes; only `search` plugin) · read requirements-docs.txt (mkdocs-material build-time only, pinned >=9,<10) · read the .gitignore hunk (`site/` added under Node block) · resolved the freeze ⚠ flag: MkDocs 1.6.1 DID map README.md→index.html (the site root is README), so no thin index.md fallback was needed
- [n/a] WIRING / DEAD-CODE (code) — no Python/JS symbols produced; the artifacts are declarative config (mkdocs.yml, requirements-docs.txt, .gitignore)

### GATE RECORD
Outcome: PASS
Auto-resolved: yes (run: site-scaffold verify; autonomy: auto) — evidence complete, residue checks clear (no security · no concurrency · no architecture/trust-layer residue: this is build-time docs infra). The freeze ⚠ flag was retired by the live strict build (README→home confirmed). Security: none found (declarative config, no secrets, no runtime dep).
Reviewed by: auto-gate (autonomy: auto) · date: 2026-06-24

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `mkdocs build --strict` exit code (must stay 0 as the book grows) · new book .md added to `add-method/docs/` without a matching nav entry (would orphan_page) · the published packages' dep lists staying empty.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · seeded] pages-deploy (task 2) — GitHub Actions workflow building `--strict` + deploying to Pages on push to main; set `site_url` + update `homepage`/README links (evidence: site builds locally; needs CI + the public URL to satisfy exit criteria 3–4).
- [SPEC · carried] a new book chapter/appendix added later must also be added to `mkdocs.yml` nav or `--strict` orphan-fails — consider a tiny guard test (assert every `add-method/docs/*.md` is in nav) so the book and site can't drift (evidence: nav is an explicit hand-maintained list). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] nav labels are hand-typed in mkdocs.yml and duplicate each chapter's H1 — a future polish could derive them, low priority (evidence: 24 labels maintained by hand). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] repo-root files in §5 Scope MUST use the `add-method/../<file>` climb — a bare token (`mkdocs.yml`) resolves to the TASK dir, not project root, tripping a false `scope_violation` at the gate; re-cross tests→build to re-anchor after fixing the declaration (evidence: gate returned-to-build attempt 1/3, healed by re-declaring + re-snapshot — reaffirms the close-book-align convention). [folded foundation-version 49]
- [UDD · folded] keeping the site home OUT of the book (README→index.html via MkDocs default) is the lean choice for a book whose source is mirror-guarded — it adds zero new file, zero bundle/parity work, and the existing README already carries an intro + linked TOC that makes a good landing (evidence: human chose it over a new index.md; strict build confirmed README is the site root). [folded foundation-version 49]
- [TDD · folded] a docs/config task with no Python src is still red/green-testable by asserting the declarative config shape + running the REAL `mkdocs build --strict` in a tmp dir (skip-with-reason if the tool is absent) — the strict build is the behavior seam, not a mock (evidence: 7 stdlib-unittest tests, RED before config existed → GREEN after). [folded foundation-version 49]
