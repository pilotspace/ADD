# TASK: Scheduled CI that refreshes the teacher snapshot + pin and opens a PR

slug: teacher-refresh-ci · created: 2026-06-30 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
- `.github/workflows/teacher-refresh.yml` — NEW scheduled workflow. Mirrors the structure of `.github/workflows/ci.yml` (setup-python + setup-node) but runs `add-method/scripts/update_teacher.py` then `add-method/scripts/prepare_bundle.py`, and opens a PR with the refreshed snapshot + pin.
- `add-method/scripts/update_teacher.py` — the standalone refresh (clone-at-ref → trim → replace → rewrite VENDOR.md pin); READ-ONLY here (invoked by the workflow).
- `add-method/scripts/prepare_bundle.py` — regenerates `_bundled/` (incl. personas-teacher + NOTICES) after a refresh; READ-ONLY here.
- `.github/workflows/publish.yml` — the release/tag pipeline. READ-ONLY anchor: the refresh must be DISTINCT from it (no schedule trigger there; the release build stays zero-network, reading only the committed snapshot).
- `add-method/tooling/test_teacher_refresh_ci.py` — NEW guard test.

Context (working folder): GitHub Actions; the existing ci.yml (push/PR) + publish.yml (tag) pattern; the milestone invariant — "keep latest" is a SEPARATE scheduled refresh PR, NEVER a fetch during the release build.
Honors (patterns / conventions): engine NO-EXEC (the fetch lives in CI/script, never the engine); zero-network release build; least-privilege workflow permissions; design-for-failure (the refresh PR is best-effort, a failed clone never corrupts the committed snapshot).
Anchors the contract cites: `.github/workflows/teacher-refresh.yml`, `on: schedule`, `update_teacher.py`, `prepare_bundle.py`, the PR-open step.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A scheduled GitHub Actions workflow that re-fetches upstream, regenerates the vendored teacher snapshot + pin (and the bundle), and opens a refresh PR — keeping the corpus current WITHOUT a fetch in the release build (which stays zero-network on the committed snapshot).
Framings weighed: a scheduled workflow that opens a PR (chosen — human reviews the diff before it lands; release build untouched; engine stays hands-off) · auto-commit to main on schedule (rejected — unreviewed third-party content straight to main) · fetch at release/tag time (rejected — breaks the zero-network release invariant + engine NO-EXEC).
Must:
<must>
  - A workflow `.github/workflows/teacher-refresh.yml` exists and is SCHEDULED (`on: schedule` cron) plus manually dispatchable (`workflow_dispatch`).
  - It runs `add-method/scripts/update_teacher.py` then `add-method/scripts/prepare_bundle.py` to regenerate the snapshot + pin + bundle.
  - It OPENS A PULL REQUEST with the refreshed files (never pushes the third-party content straight to a release/tag or to main unreviewed).
  - It declares least-privilege permissions (`contents: write` + `pull-requests: write`) for the PR-open step only.
  - It does NOT run in the release/tag pipeline (no `push: tags` / release trigger) — the release build keeps reading the committed snapshot (zero-network).
</must>
Reject:
<reject>
  - The workflow has no `schedule` trigger (would never auto-refresh) -> "not_scheduled"
  - The workflow auto-commits the refreshed corpus to main / a tag instead of a PR -> "unreviewed_push"
  - The workflow triggers on tag push / release (couples the refresh to the zero-network release build) -> "couples_release"
  - The workflow does not invoke update_teacher.py (refreshes nothing) -> "no_refresh_step"
</reject>
After:
<after>
  - A scheduled run regenerates snapshot+pin+bundle and leaves a reviewable PR; merging it is the human's call.
  - The release build still performs no network IO; both engine pins unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ A guard test should assert the workflow's TRIGGERS + steps by parsing the YAML literally (string match), not by executing Actions — lowest confidence because YAML structure can be expressed many ways (e.g. `on:` as a map vs the `True:` key PyYAML coerces) and a brittle assert could false-red; if wrong: the test pins surface text that a later valid edit breaks → reword the assert, no behavior cost.
  - [x] PR-open uses a maintained action (peter-evans/create-pull-request) or `gh pr create` — confirmed: both are standard; the test asserts a PR-open step exists, not which one.
  - [x] The refresh must stay OUT of ci.yml/publish.yml — confirmed by the milestone's hermetic-release decision.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the refresh workflow exists and is scheduled
  Given the .github/workflows directory
  When teacher-refresh.yml is parsed
  Then it declares an `on: schedule` (cron) trigger AND workflow_dispatch
  And the release pipeline (publish.yml) is unchanged

Scenario: the workflow refreshes via the standalone script
  Given teacher-refresh.yml
  When its steps are read
  Then it runs update_teacher.py AND prepare_bundle.py
  And it never references a fetch inside the engine (add.py/add_engine)

Scenario: the workflow opens a PR, not a direct push
  Given teacher-refresh.yml
  When its publish step is read
  Then it opens a pull request (create-pull-request / gh pr create)
  And it does not push the refreshed corpus straight to main or a tag

Scenario: least-privilege + decoupled from release
  Given teacher-refresh.yml
  When its triggers + permissions are read
  Then it grants only contents:write + pull-requests:write AND has no tag/release trigger
  And publish.yml gains no schedule/refresh step (release stays zero-network)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CI CONTRACT — scheduled teacher-refresh workflow

file: .github/workflows/teacher-refresh.yml
on:
  schedule: [ { cron: "<weekly>" } ]      # auto-refresh cadence
  workflow_dispatch: {}                    # manual trigger
  (NO push:tags / NO release trigger — decoupled from the zero-network release build)
permissions:
  contents: write          # commit the refreshed snapshot on a branch
  pull-requests: write     # open the refresh PR
steps (order):
  1. checkout
  2. setup-python (+ setup-node if needed)
  3. run  python3 add-method/scripts/update_teacher.py        # re-fetch + re-pin
  4. run  python3 add-method/scripts/prepare_bundle.py        # regenerate _bundled/
  5. open a Pull Request with the diff (create-pull-request / gh pr create)

INVARIANTS:
  engine hands-off — the fetch lives ONLY in the workflow/script, never add.py/add_engine
  zero-network release — publish.yml unchanged; release reads the committed snapshot
errors: not_scheduled · unreviewed_push · couples_release · no_refresh_step
```

Least-sure flag surfaced at freeze: ⚠ [test] the guard parses teacher-refresh.yml as text/YAML to assert triggers+steps (not by running Actions) — why: YAML `on:` is coerced by PyYAML to the boolean key `True`, so the test must tolerate that; cost if wrong: reword the assertion, no behavior change.

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavioral — one test per scenario (YAML parsed, not Actions executed).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_workflow_exists_and_scheduled: parse teacher-refresh.yml / assert schedule(cron) + workflow_dispatch triggers present
  - test_runs_refresh_scripts: assert the workflow body invokes update_teacher.py AND prepare_bundle.py
  - test_opens_pr_not_push: assert a PR-open step (create-pull-request / `gh pr create`) is present + no direct push to main/tag
  - test_least_priv_and_decoupled: assert permissions ⊆ {contents:write, pull-requests:write}, no tag/release trigger, and publish.yml has no schedule/refresh step
  - test_engine_handsoff: assert no engine module references update_teacher (reuse the guard surface)
</test_plan>

Tests live in: `add-method/tooling/test_teacher_refresh_ci.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `.github/workflows/teacher-refresh.yml` `add-method/tooling/test_teacher_refresh_ci.py`
Strategy (ordered batches): 1. write test_teacher_refresh_ci.py (red). 2. author teacher-refresh.yml (schedule + workflow_dispatch, run update_teacher.py + prepare_bundle.py, open PR via peter-evans/create-pull-request, least-priv perms). 3. green + full suite.

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2486/0 (+5 new teacher-refresh-ci tests)
- [x] coverage did not decrease — 5 new tests added; none removed
- [x] no test or contract was altered during build — only teacher-refresh.yml authored in build; the test was written in TESTS phase
- [x] the green was EARNED, not gamed — the guard parses the REAL workflow YAML (triggers, steps, permissions) + reads publish.yml for decoupling; not a vacuous assert
- [x] concurrency / timing of the risky operation is safe — scheduled job; create-pull-request reuses a single branch (chore/teacher-refresh) so concurrent runs update one PR, not a fork-bomb
- [x] no exposed secrets, injection openings, or unexpected dependencies — uses the default GITHUB_TOKEN via least-priv permissions; no untrusted input in any `run:`; no secret stored
- [x] layering & dependencies follow CONVENTIONS.md — the fetch stays in CI/script, never the engine; release pipeline untouched (zero-network)
- [x] a person reviewed and approved the change — Tin Dang (contract frozen @ v1; auto-driven build authorized)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] teacher-refresh.yml parses as valid YAML with a `schedule` cron + `workflow_dispatch`, and NO tag/release trigger — confirmed: test green; cron "0 6 * * 1"
- [x] the workflow body invokes update_teacher.py AND prepare_bundle.py, then opens a PR (not a direct push) — confirmed: peter-evans/create-pull-request@v7 on branch chore/teacher-refresh
- [x] permissions are least-privilege (contents:write + pull-requests:write only); publish.yml unchanged (release stays zero-network) — confirmed: test green + `git diff --stat publish.yml` empty

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the workflow's steps reference the real scripts (update_teacher.py, prepare_bundle.py) at their actual paths; the guard test exercises every assertion
- [x] DEAD-CODE (code) — no orphaned symbol; the workflow has a single job with ordered steps
- [x] SEMANTIC (prose / non-code) — read the full teacher-refresh.yml + re-read publish.yml: triggers are schedule+dispatch only, permissions are least-priv, the PR-open is reviewed-not-pushed, release pipeline carries no refresh

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: probed whether the guard could pass on a broken workflow — it parses real YAML structure (schedule, workflow_dispatch, permissions set-difference, push.tags absence) and cross-reads publish.yml, so a missing/over-privileged/coupled workflow fails. Probed whether the PR-open could secretly be a direct push — asserted create-pull-request/gh-pr-create presence. Could not execute Actions in-test (acceptable — the contract scopes the guard to structure, flagged at freeze).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — workflow uses least-priv permissions (contents+pull-requests write only), the default GITHUB_TOKEN, and NO untrusted event input in any `run:` (no injection surface); it clones a fixed upstream via the vetted update_teacher.py. No secret stored.
2. Concurrency: CLEAR — scheduled/dispatch only; create-pull-request reuses one branch so overlapping runs converge on a single PR.
3. Architecture: CLEAR — the fetch stays in CI/script (engine hands-off); the refresh is decoupled from the zero-network release build (publish.yml untouched).
Verdict: PASS
Residue: none
Binding: advisory — sensitivity mechanical/CI-config (a workflow file + a guard test; no method/contract/engine/security surface changed)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose a scheduled workflow that opens a PR; rejected auto-commit to main on schedule (rejected — unreviewed third-party content straight to main) · fetch at release/tag time (rejected — breaks the zero-network release invariant + engine NO-EXEC).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
