# MILESTONE: Persona teacher bundle

goal: Vendor the agency-agents teacher corpus as a pinned MIT-attributed local library, bundled into the ADD release and read at the persona phase, de-branded from method prose and kept current by a scheduled refresh — engine NO-EXEC, release builds zero-network.
rationale: sub-milestone of the persona major — the persona-learning-loop MILESTONE explicitly put "vendoring the full library / raw-file fetch / cache / refresh / SHA-pin machinery" OUT of scope; this milestone delivers exactly that deferred lane. Human-directed change: the teacher corpus moves from an externally-cited URL to a pinned, MIT-attributed local library shipped in the release and read at the persona phase, with the upstream name/URL removed from method prose (LICENSE + NOTICES retained per MIT).
stage: mvp · status: active · created: 2026-06-30T04:44:24+00:00
release: 1.15.0

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) VENDOR a pinned, raw snapshot of the teacher corpus — the agent-definition `.md` files +
     their domain folders + upstream `LICENSE` — committed under `add-method/personas-teacher/` with a
     recorded upstream commit pin; a deterministic `update-teacher` refresh script. (2) ATTRIBUTION —
     a repo-root `THIRD_PARTY_NOTICES.md` retaining the MIT notice (compliant redistribution), while
     the upstream name/URL is removed from method PROSE. (3) BUNDLE — the snapshot ships in the
     npm + pip artifacts (files-allowlist · package-data · prepare_bundle → `_bundled/personas-teacher/`)
     and `init`/`update` materialize it into a project's `.add/personas-teacher/`. (4) REFRESH CI — a
     SCHEDULED workflow re-fetches upstream, regenerates the snapshot + pin, opens a refresh PR
     (release builds keep using the committed snapshot — zero-network). (5) DE-BRAND + REUSE — strip the
     `agency-agents` URL/name from method prose (chapter 18 · glossary · `0-setup.md` · `constants.py`),
     repoint the persona phase at the local `.add/personas-teacher/` library, update the pinned tests.
Out: distilling the corpus into ADD persona shape at vendor time (raw verbatim — the AI distils at the
     persona phase, unchanged); vendoring upstream's OWN `.github/` CI, `scripts/`, or other-tool
     `integrations/` (trimmed to agent-definition payload + LICENSE/README); ANY engine-side network IO
     or spawn (the refresh is a CI/script action, never the engine); a live fetch in the RELEASE build
     (the committed snapshot is the build input); re-aiming either engine pin (vendoring + build wiring
     touch no engine code).

## Shared decisions & glossary deltas   (living — every task must honor these)
- TEACHER LIBRARY = a vendored, pinned, raw local corpus under `add-method/personas-teacher/` (the
  superset → `.add/personas-teacher/` in an installed project). It is the input the persona phase
  distils into project `.add/personas/*`. Distinct from a PERSONA (the distilled ADD-native file).
- License-compliant, name-free: MIT requires the notice be retained on redistribution → ship `LICENSE`
  + `THIRD_PARTY_NOTICES.md`; the upstream NAME/URL is removed from method PROSE only (not from the
  retained legal notice). "Don't mention" = method/marketing prose, never the license file.
- Hermetic release: the RELEASE build reads only the committed snapshot (zero-network). "Keep latest"
  is a SEPARATE scheduled CI refresh that opens a PR — never a fetch during the release build.
- Engine stays NO-EXEC: vendoring, bundling, and refresh are build/CI/script actions; the engine never
  fetches, never spawns, never reads the teacher on any path. The persona phase (AI-led, off-build)
  reads the local library.
- A persona still NEVER lowers a gate; the teacher library only widens the authoring source.

## Shared / risky contracts (freeze these first)
- the vendored-snapshot layout + pin format (`add-method/personas-teacher/` tree · `VENDOR.md`/pin file recording upstream commit + trim rules · `LICENSE`) -> owning task vendor-teacher-snapshot
- the bundle-inclusion contract (npm `files` glob · pip package-data · prepare_bundle copy target `_bundled/personas-teacher/` · `init`/`update` materialize path `.add/personas-teacher/`) -> owning task bundle-teacher

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] vendor-teacher-snapshot   depends-on: none                   — commit the pinned raw agent-def snapshot under `add-method/personas-teacher/` (+ LICENSE) + repo-root `THIRD_PARTY_NOTICES.md` + a deterministic `update-teacher` refresh script; record the upstream commit pin
- [ ] bundle-teacher            depends-on: vendor-teacher-snapshot — ship the snapshot in npm + pip (files-allowlist · package-data · prepare_bundle → `_bundled/personas-teacher/`); `init`/`update` materialize `.add/personas-teacher/`; fresh-install-test the tarball
- [ ] teacher-refresh-ci        depends-on: vendor-teacher-snapshot — a SCHEDULED GH Actions workflow that re-runs `update-teacher`, regenerates snapshot + pin, opens a refresh PR (release build stays zero-network)
- [ ] debrand-teacher-prose     depends-on: vendor-teacher-snapshot — strip the `agency-agents` URL/name from method prose (ch.18 · glossary · `0-setup.md` · `constants.py`), repoint the persona phase at `.add/personas-teacher/`, update pinned tests + add a guard test (no upstream URL in prose, LICENSE/NOTICES still ship)

## Exit criteria (observable; map each to the task that delivers it)
- [x] A pinned raw teacher snapshot (agent defs + LICENSE) is committed under `add-method/personas-teacher/` with a recorded upstream commit; a test asserts the LICENSE + pin file are present   (← vendor-teacher-snapshot · test_teacher_snapshot green)
- [x] `THIRD_PARTY_NOTICES.md` retains the MIT notice at the repo root and in the bundle; a test asserts it ships   (← vendor-teacher-snapshot / bundle-teacher · test_packaging PyWheelTest + test_bundle_teacher green)
- [x] The npm tarball AND the pip wheel contain the teacher library; a fresh install materializes `.add/personas-teacher/`; an acceptance check asserts the file is present post-install   (← bundle-teacher · real pack=259 files, fresh init=256 .md+LICENSE)
- [x] A scheduled CI workflow exists that refreshes the snapshot + pin and opens a PR (does not run in the release/tag build)   (← teacher-refresh-ci · test_teacher_refresh_ci green; publish.yml untouched)
- [x] No method-prose surface (ch.18 · glossary · `0-setup.md` · `constants.py`) names the `agency-agents` URL/name; the persona phase points at `.add/personas-teacher/`; a guard test asserts both, and the LICENSE/NOTICES still ship   (← debrand-teacher-prose · test_debrand_teacher_prose green)
- [x] Engine invariant held: no engine code path fetches, spawns, or reads the teacher; ENGINE_MD5 (add.py) unchanged; the release build performs no network IO   (← all tasks · ENGINE_PKG_MD5 re-pinned only for the de-branded comment, human-authorized)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `scripts/update_teacher.py` (NEW standalone refresh) + `scripts/prepare_bundle.py` (also copies the teacher tree + propagates THIRD_PARTY_NOTICES.md) + `package.json:files`/`bin/cli.js`/`src/add_method/_installer.py` (ship + materialize the teacher as an OPTIONAL MANAGED tree → `.add/personas-teacher/`) + `add_engine/constants.py` (persona comment de-branded → ENGINE_PKG_MD5 re-pinned fe09afcd→51671e2b; ENGINE_MD5/add.py UNCHANGED) + `_template.md.tmpl` de-branded + 5 new/edited test suites.
- skill   : `phases/0-setup.md` repointed at the local teacher library (de-branded, lean-pool held).
- book    : NEW vendored corpus `add-method/personas-teacher/` (256 agent-def .md + MIT LICENSE + VENDOR.md pin) + repo-root `THIRD_PARTY_NOTICES.md`; `docs/18-personas.md` + glossary persona headword de-branded → point at `.add/personas-teacher/`. NEW `.github/workflows/teacher-refresh.yml` (scheduled PR refresh).

### Cross-task evidence   (one row per task)
- vendor-teacher-snapshot : gate=PASS · tests=5 green (test_teacher_snapshot) · residue=none
- bundle-teacher          : gate=PASS · tests=7 green (test_bundle_teacher) + packaging/parity extended · residue=none (OPTIONAL soft-skip added so a malformed package still installs core)
- teacher-refresh-ci      : gate=PASS · tests=5 green (test_teacher_refresh_ci) · residue=none
- debrand-teacher-prose   : gate=PASS · tests=5 green (test_debrand_teacher_prose) + 2 pinned tests repointed · residue=ENGINE_PKG_MD5 re-pin (comment-only, human-authorized)
- whole-milestone suite   : 2491/0 green

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cited below)
- goal: vendor the teacher corpus as a pinned MIT-attributed local library, ship it in the release, read it at the persona phase, de-brand the prose, keep it current by a scheduled refresh — engine NO-EXEC, release zero-network. PROOF: a real `npm pack` carries 259 teacher files + NOTICES, a fresh `init` materialized 256 .md + LICENSE into `.add/personas-teacher/`, the prose grep is brand-clean while the keepers retain the URL, the scheduled refresh-PR workflow is decoupled from publish.yml, and ENGINE_MD5 (add.py) is byte-unchanged.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] review the diff (esp. the vendored `personas-teacher/` corpus + the ENGINE_PKG_MD5 re-pin), commit on a feature branch
- [ ] open a PR from the Close ship-review above; the human reviews + merges
- [ ] register the teacher-refresh workflow's first run (workflow_dispatch) once merged, to confirm the PR-open path
- [ ] bundle into the next release cut (per release.md) — a MINOR bump (new shipped corpus + materialized tree); human-run tag/publish
