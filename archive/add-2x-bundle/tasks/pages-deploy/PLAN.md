# TASK: GitHub Actions workflow: build --strict + deploy the docs site to Pages

slug: pages-deploy · created: 2026-06-24 · stage: mvp
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
- `.github/workflows/pages.yml` — NEW · the build+deploy workflow (triggers `push: main` + `workflow_dispatch`; jobs build [`pip install -r requirements-docs.txt` → `mkdocs build --strict`] → deploy via `actions/deploy-pages`).
- `add-method/package.json` — EDIT · `homepage` currently `https://github.com/pilotspace/ADD#readme` → the Pages URL `https://pilotspace.github.io/ADD/`.
- `add-method/pyproject.toml` — EDIT · `[project.urls]` (Homepage/Repository/Issues) → add `Documentation = "https://pilotspace.github.io/ADD/"`.
- `README.md` (repo root, 6.6K) — EDIT · add a "Read the book online" link to the Pages site (the GitHub landing).
- `mkdocs.yml` (repo root) — READ · `site_url: https://pilotspace.github.io/ADD/` is already set (site-scaffold); the workflow builds it.

Context (working folder):
- `.github/workflows/` — existing: `ci.yml` (unittest suite), `codeql.yml`, `publish.yml` (tag→npm/PyPI). The Pages workflow is a NEW sibling; reuse the `actions/checkout@v5` + `actions/setup-python@v6` pin style from ci.yml.
- `add-method/README.md` — the PUBLISHED (npm/PyPI) README; line 11–12 already links the bundled `docs/`; can add an "online" link too.
- the GitHub Pages source = "GitHub Actions" (not a branch) — set in repo Settings ▸ Pages (HUMAN-owned, one-time).

Honors (patterns / conventions):
- (PROJECT §Spec, release-altitude) engine/CI RECORDS + builds; the HUMAN ships — enabling Pages (Settings ▸ Pages ▸ Source = GitHub Actions) + the first publish are human-owned, never automated.
- (CONVENTIONS) reuse the existing workflow action pins (`checkout@v5`, `setup-python@v6`); least-privilege `permissions:` (the Pages deploy needs `pages: write` + `id-token: write`, scoped to this workflow).
- (ci.yml precedent) CI must `pip install -r requirements-docs.txt` so the `--strict` build has mkdocs-material (mirrors ci.yml's node-deps lesson: a missing build dep silently degrades a job).
- bundle parity: `_bundled/` mirrors only `docs/ skill/ tooling/` — package.json/pyproject/README.md edits are NOT mirrored (parity untouched).

Anchors the contract cites (the §3 names):
- `.github/workflows/pages.yml` keys: `on.push.branches:[main]` + `on.workflow_dispatch` · `permissions: {contents: read, pages: write, id-token: write}` · `concurrency: pages` · job `build` (`mkdocs build --strict` + `upload-pages-artifact`) · job `deploy` (`environment: github-pages` + `deploy-pages`).
- `add-method/package.json#homepage` · `add-method/pyproject.toml [project.urls].Documentation` · `README.md` site link · the Pages URL `https://pilotspace.github.io/ADD/`.
- verifier: workflow YAML parses + asserts the keys above; the published packages' VERSIONS are unchanged; the live deploy is human/CI-verified on push (can't run GitHub Actions locally).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A GitHub Actions workflow that builds the MkDocs site `--strict` and deploys it to GitHub Pages on every push to main, plus homepage/README links pointing at the live site.
Framings weighed: official GitHub Pages deploy actions (chosen — `configure/upload-pages-artifact` + `deploy-pages`, OIDC, no extra branch, matches publish.yml's modern style) · the `gh-pages` branch via `mkdocs gh-deploy`/peaceiris (older, pushes a build branch) · Netlify/Vercel (external host, off-platform).
Must:
<must>
  - `.github/workflows/pages.yml` triggers on `push` to `main` AND `workflow_dispatch` (manual re-deploy).
  - the build job runs `pip install -r requirements-docs.txt` then `mkdocs build --strict` and uploads `site/` via `actions/upload-pages-artifact`.
  - the deploy job uses `actions/deploy-pages` with `environment: github-pages`, `permissions: {pages: write, id-token: write}`, and a `concurrency: pages` group (no overlapping deploys).
  - `add-method/package.json` `homepage`, `add-method/pyproject.toml` `[project.urls]` (a `Documentation` entry), and the repo-root `README.md` point at the Pages URL `https://pilotspace.github.io/ADD/`.
  - the published packages' VERSIONS (`package.json` `version`, `pyproject` `version`) are unchanged by this task; `add-method/docs/` + `_bundled/` stay byte-unchanged.
</must>
Reject:
<reject>
  - the workflow's deploy job lacks `pages: write` or `id-token: write` -> "insufficient_pages_permissions"   (the Pages deploy fails)
  - the build job omits `pip install -r requirements-docs.txt` before `mkdocs build` -> "missing_build_dep"   (strict build fails in CI — the ci.yml node-deps lesson, applied)
  - this task changes a package `version` field -> "version_drift"   (it touches URLs only; releasing is a separate scope)
  - `homepage`/README still point only at the old `github.com/...#readme` with no Pages link -> "stale_homepage"
</reject>
After:
<after>
  - pushing to main runs `pages.yml`, which builds the book `--strict` and deploys it to GitHub Pages; the site is reachable at `https://pilotspace.github.io/ADD/`; `homepage`/README link to it; package versions are unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract/test] the LIVE deploy cannot be verified locally — there is no GitHub Actions runner here, so I can only assert the workflow YAML shape + the link edits; lowest confidence on whether the deploy job's environment/permissions exactly match THIS repo's Pages once enabled; if wrong: the first push's deploy job fails (visible in the Actions tab), fixed by a workflow tweak — and it REQUIRES the human to first set Settings ▸ Pages ▸ Source = "GitHub Actions".
  - [ ] the Pages URL is `https://pilotspace.github.io/ADD/` (org `pilotspace`, project repo `ADD` — note the repo name's casing in the path) — confirm against the repo's actual Pages settings.
  - [ ] `mkdocs-material` installs on the ubuntu CI runner via pip (it does on PyPI) — high confidence; the workflow pins setup-python to 3.12 (matches ci.yml).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: workflow triggers on push to main and manual dispatch
  Given .github/workflows/pages.yml exists
  When I read its `on:` block
  Then it lists push to branch main AND workflow_dispatch

Scenario: build job builds the site strictly with its deps
  Given the build job
  When I read its steps
  Then it installs requirements-docs.txt, runs `mkdocs build --strict`, and uploads site/ via actions/upload-pages-artifact

Scenario: deploy job has Pages permissions and environment
  Given the deploy job
  When I read its config
  Then permissions include pages: write and id-token: write, environment is github-pages, and a concurrency: pages group is set

Scenario: homepage and README point at the live site
  Given the Pages URL https://pilotspace.github.io/ADD/
  When I read package.json, pyproject.toml, and the repo-root README.md
  Then each references the Pages URL (homepage / a Documentation url / a "read online" link)

Scenario: the local strict build still passes (the workflow's build step)
  Given the same `mkdocs build --strict` the workflow runs
  When I run it locally
  Then it exits 0 (the workflow's build step is real, not aspirational)

# --- rejections ---

Scenario: deploy without Pages permissions is rejected   # insufficient_pages_permissions
  Given a pages.yml whose deploy job omits pages: write or id-token: write
  When the workflow is validated
  Then it is rejected as insufficient_pages_permissions
  And the committed pages.yml DOES grant both (the guard test asserts presence)

Scenario: build without its deps is rejected   # missing_build_dep
  Given a build job that runs `mkdocs build` without installing requirements-docs.txt
  When the workflow is validated
  Then it is rejected as missing_build_dep
  And the committed pages.yml DOES install requirements-docs.txt before mkdocs build

Scenario: a version bump is out of scope   # version_drift
  Given this task edits only URLs/links
  When package.json and pyproject.toml are read
  Then their `version` fields equal the pre-task values (1.9.0)
  And no version field was changed

Scenario: a stale-only homepage is rejected   # stale_homepage
  Given homepage/README that link only to github.com/...#readme
  When the link targets are checked
  Then the absence of the Pages URL is rejected as stale_homepage
  And the committed files DO include the Pages URL
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CI/CONFIG CONTRACT — a GitHub Pages deploy workflow + homepage/README links (no HTTP; shape = the workflow + link edits)

FILE PRODUCED:
  .github/workflows/pages.yml      (NEW)
    name: docs
    on:
      push: { branches: [main] }
      workflow_dispatch:
    permissions: { contents: read, pages: write, id-token: write }
    concurrency: { group: pages, cancel-in-progress: false }
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v5
          - uses: actions/setup-python@v6   with: { python-version: '3.12' }
          - run: pip install -r requirements-docs.txt
          - run: mkdocs build --strict           # writes ./site
          - uses: actions/configure-pages@v5
          - uses: actions/upload-pages-artifact@v3   with: { path: site }
      deploy:
        needs: build
        runs-on: ubuntu-latest
        environment: { name: github-pages, url: ${{ steps.deployment.outputs.page_url }} }
        steps:
          - uses: actions/deploy-pages@v4   id: deployment

FILES EDITED (link targets -> PAGES_URL = https://pilotspace.github.io/ADD/):
  add-method/package.json     homepage -> PAGES_URL
  add-method/pyproject.toml   [project.urls]  Documentation = PAGES_URL
  README.md (repo root)       add a "Read the book online: PAGES_URL" line

REJECTS (guard-test enforced on the committed files):
  insufficient_pages_permissions — deploy lacks pages:write OR id-token:write
  missing_build_dep              — build runs mkdocs without `pip install -r requirements-docs.txt` first
  version_drift                  — package.json/pyproject `version` != 1.9.0 (unchanged)
  stale_homepage                 — no file references PAGES_URL

INVARIANTS (must hold):
  - package.json.version == "1.9.0"  AND  pyproject.version == "1.9.0"  (unchanged)
  - add-method/docs/ + add-method/src/add_method/_bundled/ byte-unchanged (no book/bundle touch)
  - `mkdocs build --strict` (the workflow's build step) exits 0 locally
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: ⚠ [contract/test] the live GitHub Pages deploy cannot be verified locally (no Actions runner) — I assert the workflow YAML shape + the homepage/README link edits + a local `mkdocs build --strict`; the real deploy is CI-verified on the first push AND requires the human to set Settings ▸ Pages ▸ Source = "GitHub Actions" first (engine/CI builds, human ships). Secondary [contract]: the Pages URL casing `https://pilotspace.github.io/ADD/` should be confirmed against the repo's Pages settings.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject has one test (workflow YAML shape + link edits; the live deploy is CI-verified, not local).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_workflow_triggers: parse pages.yml / assert on.push.branches==[main] AND on has workflow_dispatch
  - test_build_job_strict_with_deps (missing_build_dep): build steps install requirements-docs.txt BEFORE `mkdocs build --strict`; uploads via actions/upload-pages-artifact
  - test_deploy_job_permissions (insufficient_pages_permissions): permissions has pages: write AND id-token: write; deploy uses actions/deploy-pages; environment github-pages; concurrency group pages
  - test_links_point_at_pages (stale_homepage): package.json homepage == PAGES_URL; pyproject [project.urls] has Documentation==PAGES_URL; repo-root README contains PAGES_URL
  - test_versions_unchanged (version_drift): package.json version == "1.9.0" AND pyproject version == "1.9.0"
  - test_book_and_bundle_unchanged: add-method/docs/ and _bundled/ git-status clean (no book/bundle touch)
  - test_local_strict_build_ok: if mkdocs importable -> `mkdocs build --strict` exits 0 (the workflow's build step is real); else skip with reason
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `.github/workflows/pages.yml` `add-method/package.json` `add-method/pyproject.toml` `add-method/../README.md`   <slash-bearing tokens resolve at project root; README.md uses the `add-method/..` climb (a bare name would resolve to the task dir — the site-scaffold scope_violation lesson). No book/bundle/engine edit.>
Strategy (ordered batches):
  1. write `.github/workflows/pages.yml` (build job: checkout → setup-python 3.12 → pip install requirements-docs.txt → mkdocs build --strict → configure-pages → upload-pages-artifact; deploy job: deploy-pages with github-pages env + pages/id-token perms + concurrency pages).
  2. edit `add-method/package.json` `homepage` → PAGES_URL (leave `version` untouched).
  3. edit `add-method/pyproject.toml` `[project.urls]` → add `Documentation = PAGES_URL` (leave `version` untouched).
  4. edit repo-root `README.md` → add a "Read the book online: PAGES_URL" link.
  5. confirm `mkdocs build --strict` still exits 0 locally (the workflow's build step is real).
Safety rule (feature-specific): touch NO `version` field, NO file under `add-method/docs/` or `_bundled/`; never edit a test or the §3 contract to make a check pass.
Code lives in: `.github/workflows/pages.yml` + the 3 link-target files (package.json, pyproject.toml, repo-root README.md).
Constraints: do NOT change any test or the contract; no version bump; allow-list only (no new dependency); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 7/7 green (workflow YAML shape, link edits, versions, book-unchanged, local strict build)
- [x] coverage did not decrease — new task; 7 tests added (4 behavior + 3 invariant guards)
- [x] no test or contract was altered during build — only §5-scoped files written; tamper snapshot intact
- [x] the green was EARNED, not gamed — tests parse the REAL workflow (perms/triggers/step order) + assert exact URLs + run a REAL `mkdocs build --strict`; honest open item: the LIVE deploy is CI-verified on push (disclosed in the freeze ⚠ flag), not faked green here
- [x] concurrency / timing — the workflow sets `concurrency: {group: pages, cancel-in-progress: false}` so deploys don't overlap (the one timing concern, handled)
- [x] no exposed secrets, injection openings, or unexpected dependencies — least-privilege `permissions` (contents:read, pages:write, id-token:write); the only `${{ }}` is the trusted `steps.deployment.outputs.page_url`; NO untrusted event input in any `run:`; no secrets; no new dep
- [x] layering & dependencies follow CONVENTIONS.md — action pins match ci.yml style (checkout@v5, setup-python@v6); the build-dep install mirrors the ci.yml node-deps lesson
- [~] a person reviewed and approved the change — AUTO-RESOLVED under `autonomy: auto` (no security finding); the HUMAN owns the residual ship step (enable Settings ▸ Pages ▸ Source = GitHub Actions, then merge) — surfaced in the report, not hidden

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `.github/workflows/pages.yml` parses as valid YAML with the build+deploy jobs, push:main + workflow_dispatch triggers, and pages/id-token permissions — confirmed: yaml.safe_load → jobs [build, deploy], perms {contents:read, pages:write, id-token:write}, on {push.branches:[main], workflow_dispatch}
- [x] the build job installs requirements-docs.txt before `mkdocs build --strict` and uploads `site/` — confirmed by reading the step list (install → strict build → configure-pages → upload-pages-artifact path: site)
- [x] package.json `homepage`, pyproject `Documentation` url, and repo-root README all contain `https://pilotspace.github.io/ADD/` — confirmed by grep (3/3)
- [x] package versions still `1.9.0` and `add-method/docs/`+`_bundled/` byte-unchanged — confirmed: both versions == 1.9.0; `git status --porcelain` on docs/+_bundled clean
- [x] `mkdocs build --strict` still exits 0 locally (the workflow's build step is honest) — confirmed: exit 0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read `.github/workflows/pages.yml` end-to-end (two jobs; deploy `needs: build`; env github-pages; the page_url is the only template expr — trusted; paths-filter scopes re-deploys to docs/config changes) · read the package.json/pyproject/README hunks (Pages URL exactly, versions untouched) · confirmed the freeze ⚠: the live deploy needs the human to set Pages Source = GitHub Actions
- [n/a] WIRING / DEAD-CODE (code) — no Python/JS symbols; artifacts are workflow YAML + URL string edits

### GATE RECORD
Outcome: PASS
Auto-resolved: yes (run: pages-deploy verify; autonomy: auto) — evidence complete, residue checks clear (security reviewed: least-privilege perms, no untrusted-input injection, no secrets; the only timing concern — overlapping deploys — is handled by `concurrency: pages`). RESIDUAL human ship-step (NOT a gate failure): enable Settings ▸ Pages ▸ Source = "GitHub Actions" + merge to publish — surfaced to the human, engine/CI builds the rest.
Reviewed by: auto-gate (autonomy: auto) · date: 2026-06-24

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the `docs` workflow's run status on each push to main (a red build = a broken book link before it ships) · the deploy job's published URL matching the homepage/README links · package versions staying decoupled from this URL-only task.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] the docs `pages.yml` and the suite `ci.yml` both rebuild on docs changes; a future polish could fold the strict-build check into ci.yml so a broken book link fails a PR BEFORE merge, not only on the post-merge deploy (evidence: pages.yml only runs on push to main + dispatch, not PRs). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] consider adding `requirements-docs.txt` (mkdocs-material) to Dependabot/renovate so the docs toolchain stays patched like the npm/pip deps (evidence: it's a new, separately-pinned dep file). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a deploy task whose final step is inherently human-and-remote (enable Pages, merge, live publish) is honestly verified by asserting the ARTIFACT shape (workflow YAML keys + a real local strict build) + DISCLOSING the un-local-verifiable deploy in the freeze flag — not by faking a green; the residual ship-step belongs to the human (release-altitude's "engine records, human ships") (evidence: gate PASS auto-resolved with the live-deploy residual surfaced, not hidden). [folded foundation-version 49]
- [SDD · folded] YAML 1.1 parses a bare `on:` key as the boolean True — a workflow-shape test must read `cfg.get("on", cfg.get(True))` or it silently asserts against a missing key (evidence: the trigger test needed the True-key fallback to see the `on:` block). [folded foundation-version 49]
- [TDD · folded] for a deploy task, the invariant guards (versions unchanged · book/bundle clean) are GREEN at red-time by design — they assert preservation; only the artifact-shape tests are red pre-build, and that mix is honest red (evidence: 4 behavior tests red + 3 invariant tests green before build → all 7 green after). [folded foundation-version 49]
