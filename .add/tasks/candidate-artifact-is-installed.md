---
type: Task
title: Candidate artifact is installed
status: done
depth: standard
kind: feature
milestone: evidence-has-a-purpose
scope:
  - .github/workflows/publish.yml
  - add-method/scripts/candidate_artifact_smoke.py
  - add-method/tests/test_candidate_artifact_smoke.py
  - RELEASES.md
gives:
  - S1 `candidate_artifact_smoke.py` — an offline candidate gate reporting exact artifact digests, fresh install, upgrade, and a verdict
  - S2 `publish.yml` — both publishers consume the same checked files without rebuilding
generated: { by: add/3.6.0, at: 2026-09-16 }
verified:
  - { by: "agent:codex", at: 2026-09-16, act: freeze, authority: process, direction: "sha256:56e0662a3552cf08", binding: "sha256:531d95a1d41b601f", gives: "sha256:d1087787df75f30e" }
  - { by: "agent:codex", at: 2026-09-16, act: brief, authority: process, brief: "sha256:42260c7c701dbf9b" }
  - { by: "process:run", at: 2026-09-16, act: run, authority: process, outcome: PASS, receipt: /tasks/candidate-artifact-is-installed.d/runs/1.md }
  - { by: "agent:codex", at: 2026-09-16, act: refreeze, authority: process, direction: "sha256:0b1346e8fcb7b778", binding: "sha256:bb86e15103bdfd2b", gives: "sha256:d1087787df75f30e" }
  - { by: "agent:codex", at: 2026-09-16, act: brief, authority: process, brief: "sha256:28eeb66e67510cfa" }
  - { by: "process:run", at: 2026-09-16, act: run, authority: process, outcome: PASS, receipt: /tasks/candidate-artifact-is-installed.d/runs/2.md }
  - { by: "agent:gpt-5.6-candidate-artifact-t2", at: 2026-09-16, act: refute, authority: process, outcome: held, probes: 4, receipt: /tasks/candidate-artifact-is-installed.d/runs/2.md, tier: T2, note: "Previous-wheel mutant refused; backfill tag selected older version; failed smoke upload preserved report while publishers stayed blocked; local real 3.5-to-3.6 install and upgrade held with provenance limits." }
  - { by: "agent:codex", at: 2026-09-16, act: gate, authority: process, outcome: PASS, receipt: /tasks/candidate-artifact-is-installed.d/runs/2.md, brief: "sha256:176e7346c960b1e9" }
---
## CARD
goal: Build once, hash, install, and upgrade the exact release-candidate files before either registry receives them
why: source tests and tag/version agreement cannot prove what packaging filters or installers drop into a user's project; current publisher jobs rebuild independently after the source gate
beat: done · next: add status

## RULES
<must>
- M1 The candidate gate takes explicit local wheel, sdist, npm tarball, and older wheel/tarball paths. It calculates SHA-256 from file bytes before installation and reports tag commit/tree, artifact paths/digests, tool versions, stages and outcome. Missing, unreadable or changed files refuse.
- M2 Install the candidate wheel by path with no index and npm tarball by path in isolated environments. Run each installed launcher to initialize a fresh project, then the dropped `.add/tooling/cli.py status`. Assert candidate version stamp and representative engine, skill, persona-index and corpus files.
- M3 Seed separate projects from older local artifacts, add a user file under `.add/` and user prose outside the managed AGENTS.md block, then update through candidate launchers. `update --check` reports drift before and current after; managed files advance; user state survives.
- M4 Compare installed shared npm and pip managed payloads by relative path and content digest. Any absent or different shared file refuses by path; source-tree parity alone is insufficient.
- M5 At the tag's committed tree, one workflow job builds and smokes the three candidate files, records their digests, and uploads them. Both publisher jobs download, rehash and publish those same files; neither rebuilds.
- M6 The report and ledger call this local candidate-byte evidence. Registry-served bytes, CI identity and npm/PyPI attestation are separate external observations; the ADD release stamp does not verify them.
</must>
<reject>
- R:HASHMISMATCH expected SHA-256 differs from candidate bytes, or bytes change before install -> "HASHMISMATCH"
- R:HEADLESS installed archive lacks runnable dropped `.add/tooling/cli.py` -> "HEADLESS"
- R:STATELOSS upgrade removes or overwrites user state -> "STATELOSS"
- R:PACKAGE_DIVERGENCE installed shared npm and pip payload differs -> "PACKAGE_DIVERGENCE"
- R:REBUILD publisher produces new bytes after candidate smoke -> "REBUILD"
- R:PROVENANCE_LIE local digest is described as registry or CI attestation -> "PROVENANCE_LIE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · local builder and tag CI run without registry credentials; temporary projects are allowed, publication is not · probe: fixture run needs no network
- A2 [which] covers: S1, S2 · wheel, sdist and npm tarball are required; installed-user proof uses wheel and tarball while sdist inclusion is checked against wheel · probe: missing one refuses
- A3 [when] covers: S1, S2 · the boundary is before publish; registry retrieval and attestation are later evidence · probe: report describes only local installation
- A4 [absent] covers: S1, S2 · missing older files or shared payload fail closed; upgrade is never silently skipped · probe: no PASS with absent previous artifact
- A5 [order] covers: S1, S2 · hash precedes install, install precedes smoke, upgrade precedes publish · probe: hash mismatch performs no installation
- A6 [experience] covers: S1, S2 · release planner needs one report naming file, digest, stage, failure path and recovery; vague green output obstructs half-release diagnosis · probe: refusal names a stage and path

## PLAN
contract: CLI `python3 add-method/scripts/candidate_artifact_smoke.py --manifest <json> --report <json>`; manifest names `tag_commit`, `tag_tree`, `candidate.{wheel,sdist,npm}`, `previous.{wheel,npm}`, and expected SHA-256 for each file. Exit 0 only for `outcome: PASS`; otherwise nonzero with `outcome: REFUSED`, `reason`, `stage`, `path`. `--fixture-manifest` checks digest and archive/payload controls on tiny local bytes, including whether previous files carry an upgradeable managed payload; its `fresh_install` and `upgrade` fields say NOT_RUN. Real release mode installs the actual files and verifies fresh and upgrade behavior. Report digests are measured from bytes, never copied from manifest.
regression: affected · `python3 -m pytest add-method/tests/test_candidate_artifact_smoke.py add-method/tests/test_release_gate.py add-method/tests/test_npm_pip_parity.py -q` · packaging and installer contracts; full suite before tag

## EDGES
- E1 Valid local archives and equal shared payload -> fixture gate PASS reports measured digests and archive controls, while installed CLI and upgrade state say NOT_RUN
- E2 Wrong expected tarball digest -> R:HASHMISMATCH before install
- E3 Tarball omits `tooling/cli.py` while wheel carries it -> R:HEADLESS despite source green
- E4 Candidate upgrade loses older project's user file -> R:STATELOSS naming path
- E5 Wheel and tarball differ at one shared managed path -> R:PACKAGE_DIVERGENCE naming path
- E6 Candidate or previous file missing -> refusal, never vacuous smoke/upgrade
- E7 Successful local report in ledger -> local evidence only, no registry or attestation claim
- E8 An older wheel or npm archive has no upgradeable managed payload -> refusal rather than fixture PASS
- E9 Rerunning an older tag chooses the nearest strictly earlier tag, never a later one
- E10 A failed candidate smoke still uploads its refusal report; both publishers remain blocked

## CHECKS
- test_fixture_candidate_pass_reports_measured_digests · covers: M1, M2, M3, E1, A1, A3 · acceptance · positive archive control explicitly says install/upgrade NOT_RUN
- test_hash_mismatch_refuses_before_install · covers: M1, R:HASHMISMATCH, E2, A5 · acceptance · wrong hash stops all later stages
- test_missing_dropped_cli_refuses · covers: M2, R:HEADLESS, E3 · acceptance · a headless archive fails
- test_upgrade_user_state_loss_refuses · covers: M3, R:STATELOSS, E4 · acceptance · arbitrary user data survives
- test_installed_package_divergence_refuses · covers: M4, R:PACKAGE_DIVERGENCE, E5 · acceptance · same version, different shared bytes fails
- test_missing_artifact_never_passes · covers: M1, M3, E6, A2, A4, A6 · acceptance · every file is required; refusal names its stage and path
- test_local_report_does_not_claim_external_attestation · covers: M6, R:PROVENANCE_LIE, E7 · acceptance · evidence boundary is explicit
- test_publish_consumes_smoked_artifacts_without_rebuild · covers: M5, R:REBUILD · workflow contract · shared build/upload, download/rehash, file publish
- test_unusable_previous_archive_refuses · covers: M3, E8, A4 · acceptance · an old archive with no managed payload cannot claim upgrade
- test_previous_tag_is_strictly_older · covers: M5, E9 · workflow execution · backfill tag v3.5.0 selects v3.4.0
- test_refusal_report_is_uploaded_on_failure · covers: M5, E10, A6 · workflow contract · failure upload preserves actionable refusal without enabling publish
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/candidate-artifact-is-installed.d/runs/2.md · kind: test-ids · 29/29 reported · exit 0 · 2026-09-16
refute: held · 4 probe(s) · tier T2 · by agent:gpt-5.6-candidate-artifact-t2 · against /tasks/candidate-artifact-is-installed.d/runs/2.md · 2026-09-16 · Previous-wheel mutant refused; backfill tag selected older version; failed smoke upload preserved report while publishers stayed blocked; local real 3.5-to-3.6 install and upgrade held with provenance limits.
gate: PASS · authority process · by agent:codex · receipt /tasks/candidate-artifact-is-installed.d/runs/2.md · 2026-09-16

## LESSONS
- pending
- none filed — no lesson cites /tasks/candidate-artifact-is-installed.md (add learn <lens> "<lesson>" --evidence /tasks/candidate-artifact-is-installed.md)
