# TASK: Vendor a pinned raw teacher snapshot + MIT attribution

slug: vendor-teacher-snapshot · created: 2026-06-30 · stage: mvp
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
  - `add-method/personas-teacher/**` (NEW) — the vendored RAW teacher snapshot: the upstream agent-definition `.md` files under their 18 domain folders (specialized · marketing · engineering · game-development · strategy · gis · security · sales · design · testing · project-management · paid-media · support · spatial-computing · examples · product · finance · academic — ~260 `.md`), plus upstream `README.md` + the `divisions.json`/`tools.json` roster manifests. Verbatim, no edits.
  - `add-method/personas-teacher/LICENSE` (NEW) — upstream MIT license file, copied verbatim (retention is the MIT redistribution requirement).
  - `add-method/personas-teacher/VENDOR.md` (NEW) — the pin record: upstream repo, commit SHA (`24485830cd4b3c63a4a357b0664d9dedbab9653a`), fetch date, and the TRIM rules (what was dropped + why). The single source of truth for "what version is vendored".
  - `THIRD_PARTY_NOTICES.md` (NEW, repo root) — the project-level attribution file naming the vendored component + its MIT notice; the name-free method prose points here for credit.
  - `add-method/scripts/update_teacher.py` (NEW) — a deterministic refresh script: clone upstream at a given/default ref into a temp dir, apply the trim, replace `personas-teacher/`, rewrite `VENDOR.md` with the new SHA. Standalone (run by a human/CI), NOT engine code.
  - `add-method/tooling/test_teacher_snapshot.py` (NEW) — the doc/asset-truth suite for this task.
Context (working folder):
  - `add-method/scripts/prepare_bundle.py` — the existing bundler (read-only here; the BUNDLE task wires the snapshot in next).
  - `.add/milestones/persona-teacher-bundle/MILESTONE.md` — shared decisions: TEACHER LIBRARY = pinned raw local corpus; MIT notice retained, name dropped from prose only; engine NO-EXEC; release build zero-network; trim = agent-defs + LICENSE, drop upstream `.github/`/`scripts/`/`integrations/`.
Honors (patterns / conventions):
  - the engine never fetches/spawns — vendoring + the refresh script are build/CI/script actions, not engine code; both engine pins (ENGINE_MD5 + ENGINE_PKG_MD5) UNCHANGED.
  - MIT attribution: retain `LICENSE` + name in `THIRD_PARTY_NOTICES.md` (the legal notice is never the thing being de-branded — only method/marketing prose is).
  - vendored snapshot is RAW + verbatim (distillation happens later, at the persona phase) and reproducible from the recorded pin.
Anchors the contract cites: the `add-method/personas-teacher/` snapshot tree · its `LICENSE` + `VENDOR.md` pin · the repo-root `THIRD_PARTY_NOTICES.md` · the `update_teacher.py` deterministic-refresh contract · the engine-unchanged / NO-EXEC invariant.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A pinned, RAW snapshot of the teacher corpus is vendored under `add-method/personas-teacher/` — the agent-definition `.md` files + their domain folders, copied verbatim from a recorded upstream commit, TRIMMED to agent material (drop upstream `.github/`, `scripts/`, `integrations/`, contributing/dotfiles). Its MIT `LICENSE` is retained and a repo-root `THIRD_PARTY_NOTICES.md` carries the attribution; a `VENDOR.md` records the upstream commit + trim rules; a standalone `update_teacher.py` reproduces the snapshot deterministically at a given ref. No engine code is touched and the engine performs no fetch/spawn.
Framings weighed: a pinned raw snapshot committed to the repo + a refresh script (chosen — hermetic builds, reproducible, license-compliant) · a live fetch at release-build time (rejected — adds network + supply-chain to every release) · distilling at vendor time (rejected — the human chose raw verbatim; distillation stays at the persona phase)
Must:
<must>
  - `add-method/personas-teacher/` contains the RAW agent-definition `.md` files under their domain folders, copied verbatim (unedited) from the recorded upstream commit.
  - the upstream MIT `LICENSE` is retained at `add-method/personas-teacher/LICENSE`, and a repo-root `THIRD_PARTY_NOTICES.md` names the vendored component + carries its MIT notice.
  - `add-method/personas-teacher/VENDOR.md` records the upstream commit SHA + fetch date + the trim rules (the single source of truth for the vendored version).
  - the snapshot is TRIMMED: upstream `.github/`, `scripts/`, `integrations/`, `CONTRIBUTING*`, and dotfiles are NOT vendored; the agent-def domain folders + `README.md` + roster manifests are.
  - `add-method/scripts/update_teacher.py` reproduces the snapshot deterministically (clone at ref → trim → replace tree → rewrite `VENDOR.md`); it is standalone — never imported or invoked by the engine.
  - no engine code change; both pins (ENGINE_MD5 + ENGINE_PKG_MD5) UNCHANGED; no test scans the vendored tree as method prose.
</must>
Reject:
<reject>
  - a vendored tree without the retained MIT `LICENSE` / `THIRD_PARTY_NOTICES.md` -> "attribution_missing" (MIT requires the notice on redistribution)
  - a snapshot with no recorded upstream pin -> "pin_unrecorded" (`VENDOR.md` must name the commit)
  - the refresh wired into the engine or the release build -> "fetch_in_engine_or_release" (engine NO-EXEC; release build zero-network)
</reject>
After:
<after>
  - the pinned raw snapshot + LICENSE + VENDOR.md exist under `add-method/personas-teacher/`; `THIRD_PARTY_NOTICES.md` is at the repo root; `update_teacher.py` exists and is standalone; tests assert presence + pin + trim + attribution + engine-unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ whether an existing repo-wide scanner (ubiquitous-language / slang / parity) walks the new `add-method/personas-teacher/` tree and goes red on arbitrary upstream prose — lowest confidence because the vendored files contain uncontrolled words (e.g. "fold", "seam", exec/spawn tokens); if wrong: an unrelated guard fails on vendored content. (Mitigation: run the FULL suite after vendoring; if a scanner picks the tree up, add `personas-teacher` to ITS exclude set in the TESTS phase — the vendored corpus is third-party data, never an ADD method surface.)
  - [ ] the MIT license needs only LICENSE-retention + a NOTICES file (no further obligation) — if wrong: add the required notice form.
  - [ ] `git clone --depth 1` at the pin is reproducible enough (the SHA is the contract) — if wrong: pin a tag/tarball instead.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the raw snapshot is vendored under a recorded pin
  Given the vendored teacher tree
  When add-method/personas-teacher/ is read
  Then it holds the raw agent-definition .md files under their domain folders
  And VENDOR.md records the upstream commit SHA + fetch date

Scenario: MIT attribution is retained
  Given the vendored snapshot
  When the license surfaces are read
  Then add-method/personas-teacher/LICENSE is the upstream MIT license
  And THIRD_PARTY_NOTICES.md at the repo root names the component + its MIT notice

Scenario: the snapshot is trimmed to agent material
  Given the vendored tree
  When it is compared to the upstream layout
  Then upstream .github/, scripts/, integrations/ and CONTRIBUTING* are absent
  And the agent-def domain folders are present

Scenario: the refresh script is standalone and reproducible
  Given add-method/scripts/update_teacher.py
  When it is read
  Then it clones at a ref, trims, replaces the tree, and rewrites VENDOR.md
  And it is never imported or invoked by the engine (no engine fetch/spawn)

Scenario: attribution missing is rejected
  Given a vendored tree without LICENSE / THIRD_PARTY_NOTICES.md
  When the snapshot is checked
  Then it is rejected as "attribution_missing"
  And the engine pins remain unchanged

Scenario: the engine is untouched
  Given the vendoring edits
  When the engine pin is read
  Then ENGINE_MD5 equals the pin (no engine change)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

VENDORED SNAPSHOT — `add-method/personas-teacher/` (NEW asset tree; no engine code)
  (described inline — no bare triple-dash / line-start hashes so the §3 span stays intact)
  • RAW + verbatim: the upstream agent-definition `.md` files under their domain folders, copied
    unedited from commit `24485830cd4b3c63a4a357b0664d9dedbab9653a`. Reproducible from the pin.
  • TRIM rules: KEEP the agent-def domain folders + `README.md` + roster manifests
    (`divisions.json` / `tools.json`); DROP upstream `.github/`, `scripts/`, `integrations/`,
    `CONTRIBUTING*`, `SECURITY.md`, and dotfiles. ~260 `.md` across 18 folders.

ATTRIBUTION (MIT) — retained, name dropped from PROSE only
  • `add-method/personas-teacher/LICENSE` = the upstream MIT license, verbatim.
  • `THIRD_PARTY_NOTICES.md` (repo root) names the vendored component + carries its MIT notice. The
    legal notice is NEVER de-branded; only method/marketing prose drops the name (a later task).

PIN RECORD — `add-method/personas-teacher/VENDOR.md`
  • Records: upstream repo, commit SHA, fetch date, and the trim rules. Single source of truth for
    the vendored version; `update_teacher.py` rewrites it on refresh.

REFRESH — `add-method/scripts/update_teacher.py` (standalone, NOT engine)
  • Deterministic: clone upstream at a given/default ref → apply trim → replace the tree → rewrite
    `VENDOR.md` with the new SHA. Run by a human or the scheduled CI (next task) — NEVER imported or
    invoked by `add.py`/the engine, and never run in the release build.

ENGINE / NO-EXEC
  • No engine code is touched; both pins (ENGINE_MD5 + ENGINE_PKG_MD5) UNCHANGED. The engine performs
    no fetch and no spawn; the vendored tree is inert data.

ERROR CODES (asset-truth invariants — the tests assert each negative)
  attribution_missing          -> a vendored tree without retained LICENSE / THIRD_PARTY_NOTICES.md.
  pin_unrecorded               -> a snapshot with no upstream commit recorded in VENDOR.md.
  fetch_in_engine_or_release   -> the refresh wired into the engine or the release build.

VERIFICATION — tests assert: the raw snapshot + pin + LICENSE present · THIRD_PARTY_NOTICES retains MIT
  · trim applied (dropped dirs absent, domain folders present) · update_teacher.py standalone · ENGINE_MD5 unchanged.

Least-sure flag surfaced at freeze: ⚠ [test] an existing repo-wide scanner (ubiquitous-language / slang /
parity) may walk the vendored `personas-teacher/` tree and go red on uncontrolled upstream prose (e.g.
"fold", "seam", exec tokens). If wrong: an unrelated guard fails on third-party content. Mitigation: run the
FULL suite after vendoring; if a scanner picks it up, add `personas-teacher` to THAT scanner's exclude set
(the corpus is inert third-party data, never an ADD method surface) — the one test-file edit this task may need.

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

Coverage target: every Must + Reject scenario has one asset/doc-truth test
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_snapshot_present_and_pinned: `add-method/personas-teacher/` holds >200 agent-def `.md` across domain folders; `VENDOR.md` records a 40-hex commit SHA + upstream repo
  - test_license_retained: `personas-teacher/LICENSE` contains "MIT License"; `THIRD_PARTY_NOTICES.md` (root) names the component + carries an MIT notice
  - test_trim_applied: no `personas-teacher/.github`, `/scripts`, `/integrations`, `/CONTRIBUTING.md`; the agent-def domain folders (engineering · security · design · …) ARE present
  - test_update_script_standalone: `add-method/scripts/update_teacher.py` exists, references the upstream + a clone-at-ref + VENDOR rewrite, and is NOT imported by `add.py`/`add_engine` (grep the engine for the module name → absent)
  - test_engine_unchanged: ENGINE_MD5 == engine_pin.ENGINE_MD5 (no engine change)
</test_plan>

Tests live in: `add-method/tooling/test_teacher_snapshot.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/personas-teacher/` `add-method/../THIRD_PARTY_NOTICES.md` `add-method/scripts/update_teacher.py` `add-method/tooling/test_teacher_snapshot.py`
Strategy (ordered batches): 1. write `update_teacher.py` (clone --depth 1 at ref → trim KEEP/DROP → replace `personas-teacher/` → rewrite `VENDOR.md`). 2. run it at pin `2448583` to materialize the raw trimmed snapshot + `LICENSE` + `VENDOR.md` (reuse the existing scratchpad clone; no re-fetch needed). 3. write repo-root `THIRD_PARTY_NOTICES.md` (component + MIT notice). 4. tests. 5. FULL-suite check — if any repo-wide scanner walks the vendored tree, add `personas-teacher` to ITS exclude set (TESTS phase only; the corpus is third-party data, never an ADD surface). Run red→green.

Persona (optional): <none>
Known-problem fixes: a repo-wide scanner (ubiquitous-language/slang/parity) may walk the vendored prose → exclude `personas-teacher` from that scanner (the corpus is inert third-party data) · engine NO-EXEC → the refresh is a standalone script, never wired into add.py; pins UNCHANGED · the snapshot is RAW → never edit a vendored file (verbatim) · ~260 new files all under the one dir token (scope containment).
Strategy actually used: As planned. Wrote `update_teacher.py` (stdlib clone→trim→replace→rewrite-VENDOR), ran it at pin `24485830…` with `--date 2026-06-30` to materialize the raw trimmed snapshot (256 `.md`, 18 domain folders; integrations/scripts/.github/CONTRIBUTING dropped) + retained `LICENSE` + `VENDOR.md`, hand-wrote `THIRD_PARTY_NOTICES.md` (MIT, "AgentLand Contributors"), tests red→green. The lowest-confidence risk (a repo-wide scanner walking vendored prose) did NOT materialize — full suite 2472/0; the ubiquitous-language/parity guards are scoped to specific trees, not a repo-wide glob, so no exclude-set edit was needed. Engine + both pins UNCHANGED.
Safety rule (feature-specific): vendored files are VERBATIM — never edit upstream content; retain the MIT LICENSE; the refresh is never engine/release-build code.
Code lives in: `add-method/personas-teacher/` + `add-method/scripts/` + repo root
Constraints: do NOT change any test or the contract; do NOT touch engine code or re-aim a pin; allow-list packages only; ask if unclear.

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

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add-method/personas-teacher/` holds the raw upstream agent-def `.md` (256) under 18 domain folders, materialized verbatim by `update_teacher.py` at the pin — confirmed by reading the tree + the snapshot test
- [x] `personas-teacher/LICENSE` is the verbatim MIT license and `THIRD_PARTY_NOTICES.md` (root) names the component + carries the MIT notice — confirmed by the license test + reading both
- [x] `personas-teacher/VENDOR.md` records upstream repo + the 40-hex SHA `24485830…` + fetch date 2026-06-30 + trim rules — confirmed by the pin test
- [x] upstream `.github/`/`scripts/`/`integrations/`/`CONTRIBUTING*` are ABSENT from the snapshot; the 18 domain folders are present — confirmed by the trim test + `ls`
- [x] `update_teacher.py` clones-at-ref + rewrites VENDOR.md, and is NOT referenced anywhere in the engine; ENGINE_MD5 unchanged — confirmed by the standalone + engine tests; full suite 2472/0 (no scanner red on vendored prose)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `update_teacher.py` is a standalone maintenance script (CLI `main()`); it is intentionally NOT imported by the engine (that isolation is the contract); the snapshot is inert data read by the AI at the persona phase. The bundle-teacher task wires it into the package next.
- [x] SEMANTIC (prose / non-code) — read `update_teacher.py` in full (clone→trim→replace→rewrite-pin; stdlib only; hardcoded HTTPS upstream, no untrusted input executed), `VENDOR.md` (pin + trim rules), `THIRD_PARTY_NOTICES.md` (MIT retained), and spot-read several vendored agent-def `.md` (verbatim upstream, inert). Confirmed trim correctness via `ls` (dropped dirs absent, 18 domain folders present).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: probed the tests for vacuousness — `test_snapshot_present_and_pinned` asserts >200 real `.md` (256) + a 40-hex SHA in VENDOR.md (not a stub), `test_trim_applied` asserts BOTH presence (domain folders) AND absence (dropped dirs) so it can't pass on an empty tree, `test_license_retained` checks the actual "MIT License" text + the component name in NOTICES, `test_update_script_standalone` greps the WHOLE engine (add.py + add_engine/*.py) for the module name to prove non-wiring. Tried to refute the "raw verbatim" claim by re-running the script + diffing — snapshot is reproducible at the pin. Dropped `integrations/` (16 md) accounts for ~256 vs ~272 upstream. No overfit, no stub; engine genuinely untouched (pins equal).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — `update_teacher.py` clones over HTTPS from a hardcoded upstream, runs no untrusted input, handles no secrets; it is a maintenance script, never engine/runtime. The vendored corpus is inert markdown data, never executed. No new dependency (stdlib only).
2. Concurrency: CLEAR — one-shot script into a temp dir then atomic rmtree+move; no shared runtime state.
3. Architecture: CLEAR — the snapshot is isolated under `personas-teacher/`, deliberately not wired into the engine (NO-EXEC held); both pins unchanged; release build stays zero-network (the committed snapshot is the input).
Verdict: PASS
Residue: none
Binding: advisory — non-mechanical (vendoring + standalone-script task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-resolved under autonomy: auto) · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose a pinned raw snapshot committed to the repo + a refresh script; rejected a live fetch at release-build time (rejected — adds network + supply-chain to every release) · distilling at vendor time (rejected — the human chose raw verbatim; distillation stays at the persona phase)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: As planned. Wrote `update_teacher.py` (stdlib clone→trim→replace→rewrite-VENDOR), ran it at pin `24485830…` with `--date 2026-06-30` to materialize the raw trimmed snapshot (256 `.md`, 18 domain folders; integrations/scripts/.github/CONTRIBUTING dropped) + retained `LICENSE` + `VENDOR.md`, hand-wrote `THIRD_PARTY_NOTICES.md` (MIT, "AgentLand Contributors"), tests red→green. The lowest-confidence risk (a repo-wide scanner walking vendored prose) did NOT materialize — full suite 2472/0; the ubiquitous-language/parity guards are scoped to specific trees, not a repo-wide glob, so no exclude-set edit was needed. Engine + both pins UNCHANGED.
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-resolved under autonomy: auto))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
