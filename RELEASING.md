# Releasing

One version tag publishes both packages: **`@pilotspace/add`** (npm) and
**`pilotspace-add`** (PyPI). The pipeline is `.github/workflows/publish.yml`,
triggered by a `v*.*.*` tag. It runs the test suite, refuses to ship if the tag
disagrees with either manifest, then publishes to both registries — idempotently,
so re-running a tag is always safe.

## One-time setup

### npm — `NPM_TOKEN` (only needed to publish a *new* npm version)
Settings ▸ Secrets and variables ▸ Actions ▸ New repository secret:
- **Name:** `NPM_TOKEN`
- **Value:** an npm **Automation** token (Account ▸ Access Tokens ▸ Generate ▸
  *Automation*). It must be the *Automation* type — a Classic/Publish token fails in
  CI with `EOTP` because no 2FA prompt can be answered.

> The npm job *skips* when the version is already on the registry, so for a release
> that only adds the PyPI side it needs no token at all.

### PyPI — Trusted Publisher (required, no token stored)
PyPI ▸ your account ▸ **Publishing** ▸ **Add a pending publisher** (use the
*pending* form for the very first release, before the project exists), matching
**exactly**:

| Field | Value |
|---|---|
| PyPI Project Name | `pilotspace-add` |
| Owner | `pilotspace` |
| Repository name | `ADD` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

> A mismatch surfaces as `invalid-publisher: ... no corresponding publisher`. The
> OIDC claims the job presents are `repo:pilotspace/ADD` + `environment:pypi` —
> the form above must match them.
>
> Token fallback (if you prefer a secret over OIDC): add a `PYPI_API_TOKEN` secret,
> remove `environment:`/`id-token` from the `pypi` job, and pass
> `password: ${{ secrets.PYPI_API_TOKEN }}` to the publish action.

## Cutting a release

1. **Bump the version** — every declaration moves together
   (`add-method/tests/test_version_parity.py` enforces it):
   - `add-method/package.json` → `version`
   - `add-method/package-lock.json` → `version` (top level and the root package entry)
   - `add-method/pyproject.toml` → `version`
   - `add-method/src/add_method/__init__.py` → `__version__`
   - `add-method/.claude-plugin/plugin.json` → `version`
   - `metadata: { … version: "X.Y.Z" … }` in each of the three `SKILL.md` trees:
     `add-method/skill/add/`, `add-method/src/add_method/_bundled/skill/add/` and
     `.claude/skills/add/` (edit the first, then regenerate and copy as in
     [`CONTRIBUTING.md`](./CONTRIBUTING.md))
2. **Update `add-method/CHANGELOG.md`** — add the new version section and date.
   The root `GETTING-STARTED.md` is a pointer and needs no per-release edit.
3. **Open a PR**, let CI go green, **merge to `main`**.
4. **Tag from `main`** and push:
   ```bash
   git checkout main && git pull
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```
5. Watch **Actions ▸ publish**. The flow is:
   `guard` (tests + tag/version match) → `npm` (publish, or skip if that version
   already exists) → `pypi` (publish; `skip-existing` makes re-runs safe).

## Verify

```bash
npm view @pilotspace/add version
pip index versions pilotspace-add
```

Then install the new version into a scratch git repository (`npx @pilotspace/add@X.Y.Z init`) and
check that `.claude/skills/add/SKILL.md` declares the new version.

## If a publish job fails

Both jobs are idempotent (npm skips an existing version; PyPI uses `skip-existing`),
so once the cause is fixed you can re-run **without** a new tag:

```bash
gh run rerun <run-id> --failed
```

Most common failure is the PyPI `invalid-publisher` above — configure the Trusted
Publisher, then re-run the failed job; the build re-runs and the upload succeeds.
