# MILESTONE: Docs site — ship the AIDD book to GitHub Pages

goal: a reader can browse and search the full AIDD book at a public GitHub Pages URL, built with MkDocs Material from the canonical add-method/docs/ and deployed automatically by CI
rationale: intake `new-major` — a public, hosted documentation website is a new product pillar no active milestone's goal covers. The AIDD book has only ever shipped *inside* the npm/PyPI package (`add-method/docs/`) as the trust layer people read on GitHub; it has never been a standalone browsable web presence. EXTENDS the book/trust-layer work; DEPENDS-ON nothing; OVERLAPS no live or archived milestone (verified against the milestone map — release-altitude ships *versions*, not a docs site).
stage: mvp · status: active · created: 2026-06-24

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A buildable MkDocs-Material site whose `docs_dir` is the canonical `add-method/docs/` (single source — no content copy, book byte-unchanged), with full nav over all 17 chapters (00→16) + 7 appendices (a–g), the 4 PNG diagrams rendering, client-side search, and dark/light mode; the EXISTING `README.md` serves as the home (MkDocs maps README→index.html — NO new book file, per the human's "keep the home out of the book" decision); and a GitHub Actions workflow that builds `--strict` and deploys to GitHub Pages on push to main, reachable at the project's public Pages URL.
Out: a custom domain / CNAME (default `*.github.io` for now) · versioned-docs (mike) · i18n/translations · blog/case-study pages (`blog-*`, `case-study-*` live at repo root, not in `add-method/docs/`) · API/reference autogeneration · editing the book's prose · syncing the `.add/docs/` dogfood copy or `_bundled/docs/` mirror into the site (canonical only).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Single source of truth:** the site builds from the canonical `add-method/docs/` in place (`docs_dir: add-method/docs`); NO copy into a `site/`/`content/` tree — no new parity surface to keep in sync.
- **Strict build is the gate:** `mkdocs build --strict` must pass (fails on a broken intra-book link or a nav entry missing a file) — it is the red/green seam for both tasks.
- **Lean-dependency posture:** the only new runtime dependency is `mkdocs-material` (pinned), declared in one place (a `requirements-docs.txt` or `[docs]` extra); the stdlib engine (`add.py`) is untouched.
- **Engine records, human ships:** enabling GitHub Pages in repo settings and the first live publish are human-owned (mirrors release.md) — CI builds + deploys, the human flips Pages on.

## Shared / risky contracts (freeze these first)
- **site config + nav contract** (`mkdocs.yml`: `docs_dir`, `site_name`, theme=material, the ordered `nav` over chapters+appendices, `index.md` as home) -> owning task `site-scaffold` — the riskiest decision; if the source/nav shape is wrong everything downstream reworks.
- **deploy contract** (the Pages workflow trigger + build command + deploy target) -> owning task `pages-deploy`.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] site-scaffold   depends-on: none           — `mkdocs.yml` (Material theme, `docs_dir: add-method/docs`, full ordered nav, search, dark/light), an `index.md` home page, diagrams rendering; `mkdocs build --strict` green locally; docs dependency pinned.
- [ ] pages-deploy    depends-on: site-scaffold   — GitHub Actions workflow building the site `--strict` and deploying to GitHub Pages on push to main (official Pages deploy); update `homepage`/README links to the Pages URL.

## Exit criteria (observable; map each to the task that delivers it)
- [x] `mkdocs build --strict` produces a static site with every chapter (00→16) + appendix (a–g) in the nav and all 4 diagrams rendering, no broken-link/nav warnings   (← site-scaffold)   (verify: `mkdocs build --strict` exits 0; live ch16/glossary/diagram all 200)
- [x] a home/landing page renders at the site root with search and dark/light mode working   (← site-scaffold)   (verify: live home 200 + search_index.json 200; README→index.html; palette toggle in mkdocs.yml)
- [x] pushing to main triggers a CI workflow that builds `--strict` and deploys the site to GitHub Pages   (← pages-deploy)   (verify: the `docs` workflow run on the #59 merge completed = success)
- [x] the published book is reachable at the project's public GitHub Pages URL and `homepage`/README point to it   (← pages-deploy)   (verify: `curl -sI https://pilotspace.github.io/ADD/` → 200; home/ch16/glossary/diagram/search all 200; links point to the URL)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : untouched (`add.py` / `state.json` engine unchanged — no engine edit this milestone; state.json only tracks the two tasks).
- skill   : untouched (`SKILL.md` / `phases/*` unchanged).
- book    : untouched at the SOURCE — `add-method/docs/` + `_bundled/docs/` byte-identical (parity held). The book is now also RENDERED as a site (new infra, not new content).
- site/CI (new surface) : `mkdocs.yml` (Material site over canonical `add-method/docs/`, README→home, full nav, search, dark/light) · `requirements-docs.txt` (build-time `mkdocs-material`) · `.gitignore` += `site/` · `.github/workflows/pages.yml` (build `--strict` → deploy to Pages) · link edits in `add-method/package.json`, `add-method/pyproject.toml`, repo-root `README.md` → the Pages URL.

### Cross-task evidence   (one row per task)
- site-scaffold : gate=PASS · tests=7 green · residue=none (strict build exit 0, 0 warnings; book/bundle/deps byte-unchanged; healed one false scope_violation via the `add-method/..` climb + re-anchor)
- pages-deploy  : gate=PASS · tests=7 green · residue=DISCLOSED — the LIVE deploy is CI-verified on push + needs the human to enable Settings ▸ Pages ▸ Source = "GitHub Actions" (engine/CI builds, human ships); workflow YAML + local strict build verified

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] criterion 1 (strict build, all chapters+appendices+diagrams, no warnings) — met by site-scaffold (local `mkdocs build --strict` exit 0; 24 pages + 4 PNG + search index)
- [x] criterion 2 (home/landing + search + dark/light) — met by site-scaffold (README→index.html; rendered HTML carries the search box + palette toggle)
- [x] criterion 3 (push triggers CI build+deploy) — MET: the human enabled Pages (Source = GitHub Actions) + merged #59; the `docs` workflow run completed = success
- [x] criterion 4 (reachable at the public URL + links point to it) — MET: https://pilotspace.github.io/ADD/ → 200 (home/ch16/glossary/diagram/search all 200); homepage/pyproject/README link to it
- goal: a reader can browse + search the full AIDD book at a public Pages URL — **MET, LIVE** at https://pilotspace.github.io/ADD/ (deploy run success; all spot-checked pages + the search index return 200). All 4/4 exit criteria satisfied.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from a `feat/docs-site` branch (the work: mkdocs.yml · requirements-docs.txt · .gitignore · pages.yml · the 3 link edits) — the human reviews + merges
- [ ] enable GitHub Pages: repo Settings ▸ Pages ▸ Build and deployment ▸ Source = "GitHub Actions" (one-time, human-owned)
- [ ] merge to main → the `docs` workflow builds `--strict` + deploys → confirm the run is green and the site is live at https://pilotspace.github.io/ADD/ (closes exit criteria 3–4)
- [ ] (optional, later) bundle this milestone into the next release cut (`release.md`) — docs-site is orthogonal to the package version; no version bump shipped here
