# TASK: Brownfield code-scan: detect existing code + the silent-mapping guide

slug: brownfield-scan · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- high-risk: method/trust-layer scope; `auto` refused (unguarded_high_risk_auto). Front seam released by the human for the v12 tail — I self-freeze §3 and STOP at verify. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: brownfield detection in `cmd_init` + a silent code-mapping skill guide. When `init` runs in
a repo that already has content, it emits a STABLE brownfield signal so the autonomous-onboarding flow
knows to map the existing code into the survivor files silently. A new `adopt.md` skill guide defines
that mapping — read code → fill survivors, never-clobber, evidence-vs-guess tags — ending at the human
lock-down (`add.py lock`, task 1).

Framings weighed: detect-and-signal (chosen) · auto-fill-in-engine · flag-gated brownfield
  - chosen: `cmd_init` MECHANICALLY detects a non-empty base (judgment-free) and prints a stable token;
    the AI reads the code and fills survivors per `adopt.md`. Engine stays judgment-free (task 1's principle).
  - auto-fill-in-engine (rejected): `cmd_init` reads code and writes PROJECT.md — injects judgment into
    the engine; ADD keeps `add.py` judgment-free, the human signature is the gate.
  - flag-gated (rejected): require `init --brownfield` — pushes a mechanical fact onto the human; the tool
    can see existing content itself.

Must:
  - `cmd_init` detects brownfield: the base dir holds an entry whose name is NOT in `_INIT_EXCLUDE`
    (the frozen membership is in §3 — excludes the tool's own scaffolding + VCS/CI/editor + legal boilerplate).
  - On brownfield, `init` prints a STABLE signal line whose first token is `brownfield:` and names the
    silent-map-then-lock flow; the greenfield closing is replaced by this brownfield-tailored next-step.
  - On greenfield (empty / excluded-only base), `init` prints the existing message BYTE-FOR-BYTE unchanged.
  - A new canonical skill guide `skill/add/adopt.md` defines the silent mapping: read existing code →
    fill EACH survivor → NEVER clobber an existing survivor (cmd_init already skips survivors that exist)
    → tag every filled decision `evidence-grounded` vs `guessed` → end at `add.py lock`.
  - `adopt.md` is byte-identical across the canonical + dogfood skill trees (+ the bundle).

Reject:
  - none material — detection is non-failing; `init` never refuses on brownfield. The single biggest risk
    is a FALSE brownfield positive on re-init (init's own AGENTS.md/CLAUDE.md/.add), mitigated by
    `_INIT_EXCLUDE`. Flagged ⚠ below.

After:
  - A repo with prior content makes `init` emit the brownfield signal; an empty repo is unchanged;
    `adopt.md` ships in all skill trees; greenfield behavior is byte-for-byte unchanged.

Assumptions — least-sure first:
  ✓ [contract] RESOLVED @ gate (change-request v2): `_INIT_EXCLUDE` widened to also exclude VCS/CI/editor
    scaffolding (.gitignore, .gitattributes, .github, .editorconfig) + legal boilerplate (LICENSE*, COPYING)
    — none carry domain signal, so a boilerplate-only repo now reads greenfield. README/docs/source are
    deliberately NOT excluded: a README is domain content adopt.md maps, so it MUST still trigger brownfield.
  ⚠ [spec] `cmd_init` detects + signals ONLY; it does NOT read code or fill survivors (the AI does, per
    adopt.md). Least sure because the milestone phrases this task as "fill survivors"; chose engine-
    judgment-free per task 1's frozen principle. If wrong (you want the engine to fill), that re-opens
    the judgment-free invariant — cost: large re-cut, contradicts task 1.
  - [ ] `adopt.md` is a NEW top-level guide (not an edit to 0-setup.md) so task 4 owns routing — confirm
    vs folding into 0-setup now (would collide with autonomous-setup-guide).

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: a repo with existing code emits the brownfield signal
  Given a base dir containing main.py (prior content)
  When I run init
  Then stdout has a line whose first token is "brownfield:"
  And the greenfield "say what you want to build" closing is NOT printed

Scenario: an empty repo is unchanged (greenfield)
  Given an empty base dir
  When I run init
  Then stdout has NO "brownfield:" line
  And the existing greenfield closing prints unchanged

Scenario: a re-init (only the tool's own files) is not brownfield
  Given a base dir holding only .add/, AGENTS.md, CLAUDE.md
  When I run init --force
  Then stdout has NO "brownfield:" line (the exclusion set prevents a false positive)

Scenario: a survivor is never clobbered (the guarantee adopt.md relies on)
  Given a base with a hand-edited .add/PROJECT.md
  When I run init --force
  Then PROJECT.md keeps its hand-edited content

Scenario: adopt.md ships byte-identical in every skill tree
  Given the repo
  Then skill/add/adopt.md == .claude/skills/add/adopt.md == _bundled/skill/add/adopt.md
  (asserted by the existing tree-parity + bundle-parity guards, not a new test)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# add.py — engine, JUDGMENT-FREE detection only
_INIT_EXCLUDE = {".add", "AGENTS.md", "CLAUDE.md", ".git",
                 ".gitignore", ".gitattributes", ".github", ".editorconfig",   # VCS/CI/editor scaffolding
                 "LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"}              # legal boilerplate
  # README/docs/source are NOT excluded — domain content adopt.md maps -> brownfield

_is_brownfield(base: Path) -> bool
    := any(child.name not in _INIT_EXCLUDE for child in base.iterdir())   # existing content present
       (False on a missing/empty base)

cmd_init: after scaffolding survivors + state, branch on _is_brownfield(base):
    brownfield -> print "brownfield: existing code detected — the `add` skill maps it into your"
                        " foundation (silent), then you lock it down: add.py lock"
    greenfield -> print the existing closing, BYTE-FOR-BYTE unchanged
  init never refuses on brownfield (detection is non-failing; exit 0 either way)

# skill guide (PROSE — gated by parity + human read, NO unit test; TDD binds only where there is code)
skill/add/adopt.md  — the silent brownfield mapping:
  read existing code -> fill each survivor -> NEVER clobber an existing survivor
  -> tag each decision `evidence-grounded` | `guessed` -> end at `add.py lock`
  Synced: .claude/skills/add/adopt.md + src/add_method/_bundled/skill/add/adopt.md  (byte-identical)
```

Status: FROZEN @ v2 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- v1 self-frozen 2026-06-04 (human released the front seam for the v12 tail). v2:
     change-request at the verify gate — human chose to widen `_INIT_EXCLUDE` (flag #1) so boilerplate-only
     repos read greenfield; re-cut the constant + added 2 test rows (TDD red→green), re-synced 3-tree. -->
<!-- Remaining least-sure flag for the gate: the engine-detect-only boundary (no code-reading /
     survivor-filling in add.py — that stays with the AI per adopt.md). -->
<!-- Also fixed at verify (advisor): adopt.md's brownfield entry is `init --await-lock` (arms the lock-down
     gate + signals) — a plain init is grandfathered-locked, so its gate never armed and the closing `lock`
     would error `already_locked`. Pinned by an integration test. Contract unchanged: adopt.md still ends at `lock`. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + least-sure flag surfaced. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all new branches — `_is_brownfield` (true / false / excluded-only) and cmd_init's
brownfield-vs-greenfield message branch. The `adopt.md` parity is asserted by the EXISTING tree-parity +
bundle-parity guards (no new test — prose, not code).
Plan (one test per code scenario):
  - test_brownfield_dir_emits_signal: base with main.py / init / assert "brownfield:" token + no greenfield closing
  - test_greenfield_dir_unchanged: empty base / init / assert no "brownfield:" + greenfield closing present
  - test_excluded_only_not_brownfield: re-init (only .add/AGENTS.md/CLAUDE.md) / init --force / assert no signal
  - test_survivor_never_clobbered_on_reinit: hand-edited PROJECT.md / init --force / assert content kept
  - test_brownfield_await_lock_arms_gate_then_lock_succeeds: integration — `init --await-lock` on a brownfield
    base / assert signal + setup.locked=false / then `lock` succeeds (pins the entry adopt.md prescribes)
  - test_boilerplate_only_is_greenfield (v2): only LICENSE/.gitignore/.github/.editorconfig / init / assert no signal
  - test_readme_still_triggers_brownfield (v2): LICENSE + README.md / init / assert "brownfield:" (README = domain)

Tests live in: `add-method/tooling/test_brownfield_scan.py` · MUST run red (no `_is_brownfield`) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): detection is a PURE read of `base.iterdir()` names — no new writes in
cmd_init beyond the existing scaffolding; the engine stays judgment-free. Code lands in canonical
`add-method/tooling/add.py` (sync to `.add/tooling/add.py` + `_bundled/tooling/add.py`); the guide lands
in canonical `add-method/skill/add/adopt.md` (sync to `.claude/skills/add/adopt.md` +
`_bundled/skill/add/adopt.md`). The greenfield message MUST stay byte-identical.
Code lives in: `add-method/tooling/add.py` + `add-method/skill/add/adopt.md` (+ synced copies)
Constraints: stdlib only; do NOT change a test or the contract; keep the greenfield path byte-for-byte.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `Ran 318 tests … OK` (8 `test_brownfield_scan` + the prior 310);
      `test_greenfield_dir_unchanged` proves the greenfield closing is byte-for-byte non-breaking.
- [x] coverage did not decrease — `_is_brownfield` (true / false / excluded-only) and cmd_init's
      brownfield-vs-greenfield branch are both asserted, incl. the negative (greenfield closing absent on brownfield);
      an integration test pins the entry adopt.md prescribes (`init --await-lock` → signal + armed gate → `lock` succeeds).
      CHANGE-REQUEST v2 (human, at the gate): `_INIT_EXCLUDE` widened — TDD red→green (test_boilerplate_only_is_greenfield
      was RED on the v1 set, green after the widen; test_readme_still_triggers_brownfield guards the kept README trigger).
- [x] no test or contract was weakened to pass a build — NO existing test modified or weakened (only ADDED tests:
      a new file `test_brownfield_scan.py` + 3 tests across this gate); `test_v8_install`'s source-regex guard stays green.
      §3 WAS re-cut to v2, but via the legitimate path — an explicit HUMAN change-request at the verify gate (not a
      silent build-time edit): the widened constant was driven red→green by a new test, not by relaxing an assertion.
      VERIFY-TIME FIX (disclosed): the advisor caught a cross-task defect — adopt.md's prose described a plain `init`,
      which is grandfathered-locked, so the gate never armed AND the guide's closing `lock` would error `already_locked`.
      Fixed in-scope by changing adopt.md's brownfield entry to `init --await-lock` (arms the gate + still signals);
      re-synced 3-tree (md5 `864c7b137bc69189e37593f80b3cf2a8`) and pinned with the integration test above. adopt.md
      still ends at `add.py lock` — the contract is unchanged; the guide is now consistent with task 1's engine.
- [x] concurrency / timing safe — detection is a PURE read of `base.iterdir()`; no writes added to cmd_init
      beyond the existing scaffolding; no partial state.
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports (stdlib `Path.iterdir`);
      `_INIT_EXCLUDE` is a fixed set; no eval, no secrets.
- [x] layering & dependencies follow CONVENTIONS.md — stdlib-only; add.py 3-tree md5 parity AND adopt.md 3-tree
      md5 parity verified; `test_tree_parity` + `test_bundle_parity` green (adopt.md ships in all skill trees).
- [x] a person reviewed and approved the change   <!-- autonomy: conservative — Tin reviewed at the verify gate;
      directed change-request v2 (widen _INIT_EXCLUDE), then approved PASS with flag #2 (engine-detect-only) accepted. -->

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-04
Note: human change-request v2 at the gate (widened `_INIT_EXCLUDE`, TDD red→green) + a disclosed verify-time
      cross-task fix to adopt.md (`init --await-lock`). 318 tests green; 3-tree md5 parity (add.py + adopt.md).
      No security finding. Flag #2 (engine stays detect-only, judgment-free) accepted by design.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): rate of brownfield signals on real onboardings (is detection firing
when it should?); false-positive reports (a greenfield repo flagged brownfield).
Spec delta for the next loop: <what dogfooding the scan taught>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
