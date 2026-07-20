# TASK: CHANGELOG, version bump, npm + PyPI publish

slug: release-1-1-0 · created: 2026-06-05 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.
> A publish is HARD TO REVERSE (the high-risk rubric's own example) — `risk: high`
> declared, dial at `conservative`: the human gate IS the ship decision.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: version 1.1.0 live on npm (@pilotspace/add) and PyPI (pilotspace-add)
  with a CHANGELOG — v14 exit criterion 6, the last one; everything v14 built
  (audit · CI enforcement · high-risk guard · portability · checklist) ships
Framings weighed: tag-driven autonomous publish (chosen: publish.yml already
  guards the release closed — full suite green + tag ≡ package.json ≡ pyproject
  — and is idempotent on re-runs; the only human act is the tag) · manual local
  npm/twine publish (rejected: bypasses the guard job and provenance/OIDC; the
  enforcement milestone should not ship around its own enforcement) · defer the
  Node-20 action bumps (rejected: GitHub forces Node 24 on June 16, 2026 — 11
  days; a release that knowingly ships deprecated runners isn't production-ready)
Must:
  - CHANGELOG.md (Keep-a-Changelog shape) at add-method/: [1.1.0] entry naming
    the five v14 features (`add.py audit` · seam-audit CI job + consumer
    workflow · `risk: high` grammar + unguarded_high_risk_auto guard/finding ·
    `guide  :` playbook line + agent-agnostic AGENTS.md block · the freeze
    review checklist) + a [1.0.0] baseline entry. SHIPPED in both channels:
    package.json "files" + MANIFEST.in include.
  - Workflow hygiene before the tag: actions/checkout v4→v5, setup-python
    v5→v6, setup-node v4→v5 in ci.yml AND publish.yml (the Node-20 forcing,
    June 16 2026); seam-audit's canonical run line byte-unchanged.
  - [CHANGE REQUEST v2, 2026-06-05 — approved by Tin] the npm job provisions
    its own Python build environment (setup-python@v6 + setuptools>=77, the
    floor pyproject.toml itself declares): the first v1.1.0 tag failed closed
    when prepublishOnly's in-process wheel build hit the runner's apt
    setuptools (pre-77, can't parse PEP 639 `license = "MIT"`). Evidence:
    run 27007111170 — guard ✓ pypi ✓ npm ✗.
  - [CHANGE REQUEST v3, 2026-06-05 — approved by Tin] npm switches from
    NPM_TOKEN to OIDC trusted publishing: the second tag (run 27008257640)
    passed prepublishOnly but failed `npm publish` with EOTP — the stored
    token cannot publish under 2FA, and token rotation re-breaks (~90-day
    expiry). Tin configured the Trusted Publisher on npmjs.com; the workflow
    upgrades npm to >=11.5.1 and drops NODE_AUTH_TOKEN — both registries now
    publish token-less via OIDC. ⚠1 (registry credentials) materialized
    exactly as flagged: visible failure, nothing partial shipped.
  - [CHANGE REQUEST v4, 2026-06-05 — plan B as shown to Tin at the v3 rerun
    question] drop setup-node's registry-url in the npm job: it writes an
    .npmrc _authToken=${NODE_AUTH_TOKEN} line, and ANY token config makes
    npm skip the OIDC exchange — the 404-on-PUT persisted even with the
    Trusted Publisher form byte-exact (run 27008622520, attempts 1+2).
    With no token config npm 11 falls through to trusted publishing;
    registry defaults to registry.npmjs.org.
  - [CHANGE REQUEST v5, 2026-06-05 — Tin's pivot: "I just update CI with new
    token which bypass mfa for deploying"] v4 surfaced ENEEDAUTH (the OIDC
    mint never engaged even with no token config and the form byte-exact),
    so Tin minted a granular access token with 2FA-bypass and updated the
    NPM_TOKEN secret. The npm job returns to token auth (registry-url +
    NODE_AUTH_TOKEN restored; OIDC scaffolding removed — upgrade step +
    diagnostics dropped for minimal moving parts). The v2 setuptools
    provisioning stays. Known cost, recorded for observe: granular tokens
    expire (~90 days) — the npm job will need a fresh secret then.
  - GETTING-STARTED refresh: the orient section mentions the `guide  :`
    playbook line and that the loop works for any agent (one short paragraph).
  - Versions: package.json ≡ pyproject.toml ≡ 1.1.0 (already true — guarded by
    test, mirrored by publish.yml's guard job).
  - Bundle fresh: prepare_bundle.py run -> zero drift (verified pre-front).
  - THE RELEASE ACT (human-gated): after Tin confirms at the verify gate, push
    tag v1.1.0 -> publish.yml (guard -> npm + pypi) -> confirm BOTH registries
    serve 1.1.0 -> only then record the gate evidence.
Reject:
  - tag pushed before the human gate -> never (conservative dial + this spec)
  - tag ≠ manifest versions -> publish.yml guard fails the release closed
  - registries unreachable post-publish -> task stays open at verify; no PASS
    without live-version evidence
Assumptions — least-sure first:
  ⚠ [spec] the registry credentials still work — NPM_TOKEN secret valid and the
    PyPI OIDC pending-publisher matched at 1.0.0; least sure because tokens
    expire and 1.0.0 was the only prior exercise; if wrong: the publish job
    fails visibly, nothing partial ships (npm and pypi jobs are independent;
    skip-existing/idempotent re-tag covers a re-run after fixing secrets)
  ⚠ [contract] action major bumps (checkout@v5 · setup-python@v6 · setup-node@v5)
    are drop-in — least sure because majors can change defaults; if wrong: CI
    goes visibly red on this PR-less push and the bump reverts in one line;
    the publish guard re-runs the full suite on the tag, failing closed
  - [x] versions already 1.1.0 in both manifests — verified
  - [x] bundle drift zero after prepare_bundle.py — verified

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the changelog exists and ships
  Given add-method/CHANGELOG.md
  When the [1.1.0] entry is read
  Then it names audit, CI enforcement, the high-risk guard, portability, and
       the checklist
  And package.json "files" and MANIFEST.in both include CHANGELOG.md

Scenario: no deprecated runners ship the release
  Given ci.yml and publish.yml
  When their action versions are listed
  Then no actions/checkout@v4 and no actions/setup-python@v5 remain
  And seam-audit's run line is byte-identical to the canonical command

Scenario: versions agree (the guard's precondition)
  Given package.json and pyproject.toml
  Then both read 1.1.0

Scenario: the release is human-gated then live
  Given the build is green and Tin confirms at the verify gate
  When tag v1.1.0 is pushed
  Then publish.yml runs guard -> npm + pypi to success
  And `npm view @pilotspace/add version` returns 1.1.0
  And PyPI serves pilotspace-add 1.1.0

Scenario: nothing ships without the human
  Given the dial is conservative and risk: high is declared
  When any completion of this task is attempted without the human gate
  Then the engine refuses it (unguarded completions are impossible by v14's own
       guard, and the dial routes the gate to Tin)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add-method/CHANGELOG.md        NEW — Keep-a-Changelog; [1.1.0] five features +
                               [1.0.0] baseline; added to package.json "files"
                               AND MANIFEST.in (ships in tarball + sdist/wheel)
.github/workflows/ci.yml       checkout@v5 · setup-python@v6 (seam-audit run
                               line BYTE-UNCHANGED: python3 .add/tooling/add.py audit)
.github/workflows/publish.yml  checkout@v5 · setup-python@v6 · setup-node@v5
                               (guard/tag/publish logic byte-unchanged);
                               v2: npm job += setup-python@v6 + setuptools>=77
                               provisioning (prepublishOnly builds the wheel
                               in-process — the job must satisfy pyproject's
                               own declared build floor);
                               v3: npm job publishes via OIDC trusted
                               publishing (npm upgraded >=11.5.1, NODE_AUTH_TOKEN
                               dropped — token-less like the pypi job);
                               v4: setup-node registry-url dropped (its .npmrc
                               token line preempts the OIDC exchange);
                               v5: back to token auth — granular NPM_TOKEN with
                               2FA-bypass (Tin minted); registry-url +
                               NODE_AUTH_TOKEN restored, OIDC scaffolding
                               removed (the mint never engaged at v4)
add-method/GETTING-STARTED.md  orient section: + `guide  :` line mention + any-agent sentence
RELEASE ACT                    human gate (Tin) -> git tag v1.1.0 + push ->
                               publish.yml -> BOTH registries at 1.1.0 -> §6
                               records live evidence -> gate PASS
ENGINE UNTOUCHED: add.py byte-identical ×3 (md5 ccb0aa1589c09d3238d7e7fbca1e0240).
GUARD: add-method/tooling/test_release_1_1_0.py — changelog presence/shipping ·
no deprecated actions · version agreement · canonical audit line survival.
```

Status: FROZEN @ v3 — approved by Tin, 2026-06-05 (v1: one-approval front via AskUserQuestion — first live walk of the freeze review checklist; ⚠ registry-credentials + action-major-bumps flags surfaced and accepted; tag deferred to the human verify gate. v2: change request after the first tag failed closed — npm job gains setup-python@v6 + setuptools>=77 provisioning; diff shown to Tin, approved via AskUserQuestion. v3: change request after EOTP — npm switches to OIDC trusted publishing, Tin configured npmjs.com and chose "I configured in publish.yaml then give CI does it". v4: the plan-B fallback Tin was shown at the v3 rerun question — registry-url dropped so no token config preempts OIDC; applied after the 404 persisted with the form byte-exact. v5: Tin's pivot to a granular 2FA-bypass token after v4's ENEEDAUTH proved the OIDC mint never engaged — token auth restored, OIDC scaffolding removed)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every in-repo Must has a test (the live-registry halves are
verify-gate EVIDENCE, not unit tests — a unit test must not depend on registry
reachability).
Plan (one test per scenario, asserting behavior not internals):
  - test_changelog_has_1_1_0_entry: [1.1.0] heading + the five feature anchors
    (audit · seam-audit · unguarded_high_risk_auto · agent · checklist) (RED)
  - test_changelog_ships_in_both_channels: package.json "files" lists
    CHANGELOG.md AND MANIFEST.in includes it (RED)
  - test_no_deprecated_actions: ci.yml + publish.yml contain no checkout@v4 /
    setup-python@v5 tokens (RED)
  - test_audit_line_survives_bumps: seam-audit run line still the canonical
    command (green-by-design; red if the bump edit drifts it)
  - test_versions_agree_at_1_1_0: package.json ≡ pyproject ≡ "1.1.0"
    (green-by-design guard — mirrors publish.yml's guard job locally)
  - test_getting_started_mentions_guide_line: orient section names `guide  :`
    (RED)
  - test_engine_untouched: add.py md5 ccb0aa1589c09d3238d7e7fbca1e0240 ×3

Tests live in: `add-method/tooling/test_release_1_1_0.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the tag is NEVER pushed during build — it is the
human-gated release act at verify; the seam-audit run line and the engine are
byte-frozen; action bumps change versions only, never logic.
Code lives in: `add-method/CHANGELOG.md` · `.github/workflows/ci.yml` · `.github/workflows/publish.yml` · `add-method/package.json` (files list) · `add-method/MANIFEST.in` · `add-method/GETTING-STARTED.md`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 433/433 OK (was 426; +7 in test_release_1_1_0.py);
      CI on the bumped actions LIVE-GREEN (run 27006320438: tests ×2 +
      seam-audit, commit 7198bd0) — the ⚠ action-bumps flag verified in practice
- [x] coverage did not decrease — 4 red→green + 3 green-by-design guards;
      check 206/0 (4 pre-existing warnings)
- [x] no test or contract was altered during build — §3 untouched; prose/config
      written to the §4 anchors as frozen
- [x] concurrency / timing of the risky operation is safe — publish.yml is
      idempotent by design (npm skip-if-published · pypi skip-existing); the
      guard job fails the release closed on any tag/version drift; npm and pypi
      jobs are independent, no partial-state coupling
- [x] no exposed secrets, injection openings, or unexpected dependencies —
      NOTE (security line, human-gated here by the conservative dial): after
      the v5 pivot npm publishes with a STORED granular token (NPM_TOKEN,
      2FA-bypass, ~90-day expiry — rotation noted in §7); scope is publish-only
      on @pilotspace/add, referenced solely via secrets context, never echoed;
      PyPI remains OIDC (no stored token); workflows remain
      static-command-only; engine md5 pinned ×3
- [x] layering & dependencies follow CONVENTIONS.md — CHANGELOG ships through
      both channels' existing manifests; bundle drift zero; versions agree
- [x] a person reviewed and approved the change — THE SHIP DECISION:
      conservative dial + risk: high → Tin confirmed "Ship — push the tag",
      approved every change request (v2–v5; v5 his own token pivot), and
      confirmed PASS at this gate with the security note surfaced

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-05
Live evidence: publish run 27009563639 fully green (guard · npm · pypi) on
  tag v1.1.0 @ 02e0d1c — `npm view @pilotspace/add version` -> 1.1.0
  (registry.npmjs.org/@pilotspace/add/-/add-1.1.0.tgz) · PyPI JSON API ->
  pilotspace-add 1.1.0. Five release attempts, each failing CLOSED one layer
  deeper (setuptools env -> EOTP -> npmrc-preempts-OIDC -> ENEEDAUTH ->
  green); zero partial state at every step — the guard design held.
Security note (escalated per the security-line rule, human-gated): stored
  granular NPM_TOKEN (2FA-bypass, publish-only, ~90-day expiry) back in use
  after Tin's v5 pivot; PyPI stays OIDC. Rotation watch recorded in §7.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): npm install @pilotspace/add / pip install
pilotspace-add succeed for newcomers (scenario "human-gated then live" as the
monitor); NPM_TOKEN expiry ~2026-09 — the npm job failing auth is the signal
to mint + update the secret (rotation note lives in publish.yml's header).
Spec delta for the next loop: the release pipe's failure surface was ALL
environment/credentials, never code — future release tasks should ⚠-flag the
publish ENVIRONMENT (job toolchains + auth mode end-to-end) as the least-sure
assumption, above code-level risks.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a hard-to-reverse release act under the conservative dial absorbs
  REPEATED change requests cleanly — five contract versions, each human-worded,
  no test weakened, zero partial state (evidence: v1–v5 trail in §1/§3, runs
  27007111170/27008622520/27009193988/27009563639)
- [SDD · folded] a CI job that runs another ecosystem's tests must provision THAT
  ecosystem's declared floor itself — pyproject's `setuptools>=77` was honored
  by build isolation everywhere except the in-process npm-job path (evidence:
  attempt-1 traceback in apt setuptools)
- [TDD · folded] the prepublishOnly seam (tests-as-publish-precondition) caught a
  real env gap no local run could see — keep tests in the publish path even
  when they "duplicate" the guard job (evidence: attempt 1 failed closed
  before npm accepted anything)
- [ADD · folded] when an external service's silent auth fallback hides the broken
  layer (OIDC mint never engaging -> 404/ENEEDAUTH), pivoting the MECHANISM on
  the human's word beats deeper debugging of an opaque seam (evidence: v5
  token pivot went green on the first try after two OIDC-shaped failures)
