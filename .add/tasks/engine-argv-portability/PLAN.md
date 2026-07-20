# TASK: CLI accepts flags-before-slug on Python <=3.12 (argparse intermixing)

slug: engine-argv-portability · created: 2026-06-11 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/add.py` — `main()` parse seam (add.py:3283–3287: `build_parser()` → `parser.parse_args(argv)`); the `nargs="?"` slug positionals verified in source: phase:3186 · advance:3190 · gate:3195 · reopen:3202 · heal:3210 · guide:3235 · report:3241/3245. EMPIRICAL blast radius (py3.10 probe, 2026-06-11): ONLY the `gate <outcome> <value-flags…> <slug>` shape fails (`unrecognized arguments`) — the required positional is consumed in the first positional block, the optional slug matches EMPTY there, and the trailing slug lands unbound. Single-required-positional verbs (heal/reopen/guide/phase/report/new-task) bind the trailing block fine on 3.10. Works on 3.13+ (argparse rewrite). ENGINE change → pin bump ×3 + re-sync (`engine_pin.ENGINE_MD5`, copies: `add-method/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `.add/tooling/add.py`).
Context (working folder): found 2026-06-11 during PR #6 review; the test helpers used the broken order and were fixed to the natural order (commit 9d52302) — the engine itself was left as-is, so this is the deferred robustness half. Local interpreters available for the red run: py3.10/3.11/3.13/3.14 (repro confirmed on 3.10; parses clean on 3.14). CI matrix runs py3.10/3.12.
Honors (patterns / conventions): CLAUDE.md "MUST design for failure"; the release-gate pin-bump ×3 idiom; arrange-through-CLI-contracts test idiom + ASCII-safe asserts (house pattern, e.g. `test_reopen_transition.py`); probes against mutating verbs run ONLY in a sandbox (a live-state probe polluted state.json once during grounding — reverted via git).
Anchors the contract cites: `main()` (add.py:3283) · the gate subparser's slug positional (add.py:3195) · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: make the CLI accept flags-before-slug on Python ≤3.12. `add.py gate RISK-ACCEPTED --owner X --ticket Y --expires Z myslug` (waiver flags before the optional `slug`) fails `unrecognized arguments: myslug` on py3.10/3.11/3.12 — works on 3.13+ and on all versions when the slug PRECEDES the flags. Repro confirmed on py3.10 (2026-06-11). EMPIRICAL correction to the first grounding: gate's waiver shape is the ONLY broken shape today (required positional + value flags + trailing optional slug); all other optional-slug verbs bind fine — but the fix lands at the shared `main()` seam so any future subparser with the same shape is covered.
Framings weighed: parse_known_args + ordered re-bind of unfilled optional positionals, declared per subparser via `set_defaults(_opt_positionals=…)` (chosen — public API only, version-agnostic, probe-CONFIRMED on py3.10: broken shape yields `slug=None, extras=['myslug']`) · `parser.parse_intermixed_args` (rejected — argparse forbids it with subparsers/nargs=PARSER) · require the slug position / drop nargs="?" (rejected — breaks the ergonomic "defaults to active task")
Must:
<must>
  - `gate <outcome> --owner X --ticket Y --expires Z <slug>` binds `<slug>` and mutates THAT task's state, identically to the canonical `gate <outcome> <slug> --flags…` order, on every supported Python (3.10–3.14)
  - the slug may also sit BETWEEN value flags (`gate RISK-ACCEPTED --owner X <slug> --ticket Y --expires Z`) — same binding
  - the re-bind is general: extras fill UNFILLED (`is None`) optional positionals in declared order, for every subparser carrying the `_opt_positionals` marker (phase · advance · gate · reopen · heal · guide · report)
  - canonical orders and all currently-working shapes parse byte-identically to today (regression sweep)
</must>
Reject:
<reject>
  - extras remain after re-bind (more extras than unfilled slots, or slot already bound) -> argparse exit 2 "unrecognized arguments: <extras>" (unchanged behavior)
  - ANY extra is flag-like (starts with "-") -> NO re-bind at all -> argparse exit 2 (unchanged) — never bind a typo'd flag's value as a slug
</reject>
After:
<after>
  - both argument orders produce the same namespace and the same state mutation across py3.10–3.14; the engine pin is re-aimed and the ×3 trees are byte-identical (`engine_pin.ENGINE_MD5`)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  - [x] (was the ⚠ freeze flag) binding extras to unfilled optional positionals can never capture a value argparse meant for a FLAG — CONFIRMED at verify: the flag-like-extra refusal is pinned by `test_flaglike_extra_never_rebinds`, and the independent refute-read's contract-violation attempts (incl. `--typo=x` =-syntax) all held; the freeze-time flag text stays recorded in §3
  - [x] parse_known_args on py3.10 returns the trailing slug in extras, ordered — CONFIRMED by sandbox probe 2026-06-11 (4 shapes)
  - [x] gate is the only broken shape today — CONFIRMED by probing all 7 optional-slug verbs on py3.10
  - [x] no caller depends on the OLD exit-2 for the waiver shape — CONFIRMED: the only known caller (test helpers) was fixed to house order in 9d52302, and the full 850-test suite is green on py3.10 + py3.14 (every in-repo caller exercised)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: waiver flags before slug bind the slug
  Given a sandbox project with task "t" at the verify phase
  When add.main runs gate RISK-ACCEPTED --owner T --ticket T-1 --expires 2099-01-01 t
  Then task "t" records gate=RISK-ACCEPTED with the waiver fields
  And no other task's state changes

Scenario: canonical order still works (regression)
  Given a sandbox project with task "t" at the verify phase
  When add.main runs gate RISK-ACCEPTED t --owner T --ticket T-1 --expires 2099-01-01
  Then task "t" records gate=RISK-ACCEPTED identically to the flags-first order

Scenario: slug between value flags binds
  Given a sandbox project with task "t" at the verify phase
  When add.main runs gate RISK-ACCEPTED --owner T t --ticket T-1 --expires 2099-01-01
  Then task "t" records gate=RISK-ACCEPTED with the waiver fields

Scenario: genuinely-unknown extra still rejected when the slug is already bound
  Given a sandbox project with task "t" at the verify phase
  When add.main runs gate PASS t extra-junk
  Then the call exits 2 with "unrecognized arguments: extra-junk"
  And task "t" state is unchanged   # required for every rejection

Scenario: a flag-like extra refuses the whole re-bind
  Given a sandbox project with task "t" at the verify phase
  When add.main runs gate PASS --typo x t
  Then the call exits 2 (unrecognized arguments)
  And task "t" state is unchanged — "x" is never mis-bound as a slug

Scenario: every optional-slug verb still parses its canonical shape (regression sweep)
  Given a sandbox project with tasks in suitable phases
  When phase/advance/heal/reopen/guide/report run their documented shapes
  Then each binds its slug exactly as today (no behavior change outside the broken shape)

Scenario: the engine pin is re-aimed and the trees are synced
  Given the build is complete
  When the ×3 add.py copies are hashed
  Then all equal the re-aimed engine_pin.ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py <verb> <required-positionals…> [value-flags…] [slug]   # slug may trail or sit between flags
  ok     -> identical namespace binding + identical state mutation as the canonical order
            `add.py <verb> <required-positionals…> [slug] [flags…]`, on every supported Python (3.10–3.14)
  exit 2 -> "unrecognized arguments: <extras>" when extras are NOT exactly the unfilled optional
            positionals: any flag-like extra (starts with "-") · more extras than unfilled slots ·
            slot already bound  (byte-compatible with today's argparse error path)
Seam: main() (add.py:3283) — parse_known_args + ordered re-bind into the subparser-declared
      `_opt_positionals` marker (set_defaults at: phase · advance · gate · reopen · heal · guide · report).
Schema: NO state.json change; parse seam only. ENGINE change -> engine_pin.ENGINE_MD5 re-aimed,
        ×3 trees byte-identical (canonical · _bundled · .add dogfood).
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-11, in-chat: "approve to freeze"; bundle presented lowest-confidence-first; autonomy stays `auto`)
Least-sure flag surfaced at freeze: ⚠ [spec] the re-bind must never capture a value argparse meant for a FLAG — because flag-arity edges vary across py3.10–3.14; if wrong: a silent mis-bind gates the WRONG task (wrong-record state mutation); mitigated by the flag-like-extra refusal + `test_flaglike_extra_never_rebinds`. ⚠ [contract] header keeps `autonomy: auto` on an every-verb parse seam — because I judge it ordinary robustness scope with the hazard test-pinned; if wrong: an auto-resolved gate on trust-adjacent scope the human would have wanted to hold.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: all 7 scenarios pinned; suite-level coverage not decreased. RED interpreter: `python3.10` (the CI floor) — on 3.13+ the broken shape parses natively, so red-for-the-right-reason is demonstrated on ≤3.12 (CI matrix runs 3.10/3.12 and stays the enforcer).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_waiver_flags_before_slug_binds: arrange sandbox board, task "t" at verify / act gate RISK-ACCEPTED --owner --ticket --expires t / assert waiver recorded on "t"
  - test_canonical_order_unchanged: same board / act gate RISK-ACCEPTED t --flags… / assert identical record
  - test_slug_between_flags_binds: act gate RISK-ACCEPTED --owner T t --ticket --expires / assert waiver on "t"
  - test_unknown_extra_with_slug_bound_exit2: act gate PASS t extra-junk / assert SystemExit 2 + "unrecognized arguments" + state unchanged
  - test_flaglike_extra_never_rebinds: act gate PASS --typo x t / assert SystemExit 2 + state unchanged ("x" never becomes a slug)
  - test_optional_slug_verbs_regression_sweep: act phase/advance/heal/reopen/guide/report canonical shapes / assert bindings unchanged
  - test_engine_pin_reaimed_x3: assert md5 of the ×3 add.py copies are identical and == engine_pin.ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_argv_portability.py` · MUST run red (missing implementation) before Build — red run executed with `/opt/homebrew/bin/python3.10`.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): NEVER bind an extra when ANY extra is flag-like, and ALWAYS re-error when extras remain after re-bind — a silent mis-bind mutates the WRONG task's gate record (the one property a green parse test may not force on every future shape).
Code lives in: the engine trees — `add-method/tooling/add.py` (canonical) synced byte-identical to `add-method/src/add_method/_bundled/tooling/add.py` + `.add/tooling/add.py`, pin re-aimed in `engine_pin.py`.
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib argparse only — no new deps); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — new suite 7/7 (py3.10) · full tooling suite 850/850 on BOTH py3.10 and py3.14
- [x] coverage did not decrease — 843 → 850 tests (+7, one per §2 scenario); no test removed or weakened
- [x] no test or contract was altered during build — tamper tripwire re-verified mechanically at the gate (tests→build snapshot)
- [x] the green was EARNED, not gamed — independent adversarial refute-read (subagent, outside build context): verdict EARNED; overfit CLEAR (generic getattr/setattr loop, arbitrary-slug probe binds), vacuous PARTIAL-non-blocking (the red test is fully load-bearing: code==0 + gate + waiver + bystander asserts; the conditional equivalence branch in test_canonical_order_unchanged is a deliberate cross-version regression guard), stubbed CLEAR (real parse_known_args exercised; py3.10 brokenness re-confirmed live); 4 contract-violation attempts all held
- [x] concurrency / timing of the risky operation is safe — parse runs single-process before any state read; state-write path unchanged; no shared in-memory state introduced
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib argparse only; parser.error echoes argv tokens exactly as stock argparse does; setattr writes only to names declared at parser-construction time, never user-supplied names
- [x] layering & dependencies follow CONVENTIONS.md — single-file engine, helper adjacent to main(); ubiquitous-language lint green (one 'seam' slang hit in the new docstring caught by test_ubiquitous_language and reworded before the gate)
- [x] a person reviewed and approved the change — the one human approval at the freeze (Tin Dang, 2026-06-11); the gate itself auto-resolved per `autonomy: auto` (run named in GATE RECORD)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_rebind_optional_positionals` called from `main()` (sole call site, add-method/tooling/add.py); `_opt_positionals` markers consumed via getattr in the helper and declared at 7 set_defaults sites (phase · advance · gate · reopen · heal · guide · report); pin re-aim consumed by 850-test suite (every pin guard re-anchored)
- [x] DEAD-CODE (code) — no new unused symbol: the helper + the 7 markers + the pin literal are each referenced; no debug residue in the diff (reviewed via git diff)
- SEMANTIC (prose / non-code) — n/a: this task produced code; the WIRING + DEAD-CODE path above is the filled deep check (the resolver judged the path)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-resolved — dynamic run `engine-argv-portability` (autonomy: auto; evidence complete, loops dry, no residue; refute-read verdict EARNED; security line clean) · date: 2026-06-11

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): CI matrix (py3.10/3.12) is the standing monitor — any future subparser whose required-positional + value-flag + optional-slug shape regresses fails `test_argv_portability` there.
Spec delta for the next loop: the refute-read surfaced two suite-hardening candidates that are POST-SNAPSHOT (the red suite is immutable once tests→build crossed): cover the `--flag=value` trailing-slug shape, and add a bystander canary task to the flag-like-extra test. Both are change-request material for a future loop, not edits now.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] a refute-read's residue includes COVERAGE GAPS the suite cannot absorb post-snapshot — route them as next-loop deltas instead of post-hoc test edits, or the tripwire reads hardening as tamper (evidence: refute-read on engine-argv-portability named the `--flag=value` shape + a canary-less exit-code assert; suite locked at tests→build)
- [ADD · folded] grounding probes against MUTATING engine verbs must run in a sandbox, never the live project — a `new-task`/`use` probe polluted live state.json during §0 and needed a git restore (evidence: zz-slug probe incident, this task's §0 Honors line)
