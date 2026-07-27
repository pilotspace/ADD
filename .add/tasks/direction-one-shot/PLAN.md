# PLAN: One engine call writes the whole direction bundle, and refuses a green suite

slug: direction-one-shot · created: 2026-07-27 · stage: mvp · risk: high
milestone: direction-velocity
autonomy: conservative
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py draft` writes §1 + §3 + §4 of a task's PLAN.md from one bundle in a single call, all-or-nothing, and — when asked to freeze — refuses unless the declared suite actually ran RED first.
Framings weighed: a new `draft` verb that reuses `--fill`'s all-or-nothing snapshot and the ONE canonical `^##\s*<n>\s*·` scan (chosen — `advance --fill` already proved the restore-on-any-refusal shape in production, and the bundle's own `## N ·` headings are a delimiter the engine already knows how to parse, so no second grammar enters the codebase) · generalize `advance --fill` to accept several sections (rejected — `--fill` is documented and tested as "ONE section for ONE crossing" and its refusal `fill_with_to_unsupported` depends on that; widening it would re-open a settled contract to buy a name) · a template/skill-prose change only, no verb (rejected — the measured cost is 45 successive PLAN.md Edits, i.e. 45 round-trips; prose can ask for fewer writes but only a verb can make one write sufficient, and `read-batching` is already the prose-only experiment)
Must:
<must>
  - one `draft --from <path|->` call replaces the §1, §3 and §4 bodies of the active task's PLAN.md; a bundle missing any of the three is refused before any write
  - the write is ALL-OR-NOTHING: any refusal on any path restores PLAN.md byte-identical, so a rejected draft never leaves a half-written bundle
  - `--freeze` chains the existing freeze in the same call, and the existing freeze floors (contract_not_drafted · unflagged_freeze · boundary_unfilled · scope) still decide — draft adds no bypass
  - with `--run-red`, the engine runs the suite declared in §4 and REFUSES to freeze if it passes; a suite that cannot be run is a refusal, never a silent skip
  - the red run is bounded: a timeout that fires is a refusal with the command and the limit named, never a hang
  - a §3 already FROZEN is refused — draft is a direction-phase verb, not a way to rewrite a settled contract
</must>
<reject>
  - a bundle without all of §1, §3, §4 -> "draft_sections_missing"
  - a bundle section that is not one of §1/§3/§4 -> "draft_unknown_section"
  - drafting onto a task whose §3 is already frozen -> "draft_onto_frozen"
  - `--run-red` and the suite exits 0 -> "red_suite_green"
  - `--run-red` and the suite cannot be run or exceeds its timeout -> "red_suite_unrunnable"
</reject>
After:
<after>
  - a direction phase's PLAN.md write count falls from tens of Edits to ONE engine call
  - "the red suite ran red before the freeze" stops being a discipline the agent asserts and becomes a fact the engine observed
  - `advance --fill` keeps working unchanged for the step-wise path a large or uncertain task still wants
</after>
Boundary: the bundle is UTF-8 text delimited by its own `## <n> ·` headings — the same grammar PLAN.md uses, read by the same `_phase_spans` scan; `-` reads stdin. `--run-red` takes an optional command string; absent, it is derived from §4's `Tests live in:` tokens. No other input shape is accepted, and a non-UTF-8 or unreadable bundle is a refusal.
<assumptions>
  ⚠ deriving the red command from §4's `Tests live in:` tokens is right often enough to be the default — if wrong (a project whose suite is not pytest, or whose tokens are not runnable paths): `--run-red "<cmd>"` takes an explicit command, and the derived form refuses with `red_suite_unrunnable` rather than guessing again; cost = the user types their command once. The engine RUNNING a suite is a genuinely new responsibility and the least-settled part of this design.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
add.py draft [<slug>] --from <PATH|->  [--run-red [CMD]]  [--freeze --by <name>] [--cross]

bundle grammar (UTF-8):
  ## 1 · <anything>      body...
  ## 3 · <anything>      body...
  ## 4 · <anything>      body...
  parsed by the SAME ^##\s*(\d+)\s*· scan PLAN.md uses — no second grammar

cmd_draft(args) -> None
  validate ALL (zero writes): sections present · sections in {1,3,4} · §3 not frozen
                              · phase within direction · bundle readable/decodable
  snapshot   original = PLAN.md bytes
  write      each §n body replaced in ONE atomic write
  --run-red  _run_red_suite(cmd, timeout) -> exit code
             exit 0            -> _die red_suite_green
             cannot run/timeout-> _die red_suite_unrunnable
  --freeze   cmd_freeze(args) unchanged — every existing floor still applies
  ANY BaseException after the snapshot -> restore original bytes, re-raise

_run_red_suite(cmd: list[str] | None, timeout: int) -> int
  cmd None -> derived from §4 "Tests live in:" backticked tokens: [python3, -m, pytest, *toks]
  bounded by timeout (default 300s); no retry (a suite run is not idempotent-cheap)
  TimeoutExpired | OSError | FileNotFoundError -> red_suite_unrunnable

refusals: draft_sections_missing · draft_unknown_section · draft_onto_frozen
          · draft_unreadable · red_suite_green · red_suite_unrunnable
```
Ground: `add-method/tooling/add.py::_fill_and_advance` — the all-or-nothing shape to reuse verbatim in structure: it snapshots `original = f.read_bytes()`, writes, runs the unchanged guard stack, and restores on `BaseException` (SystemExit included, which is what `_die` raises) before re-raising. Its payload guard refuses a line-start `## ` because a `--fill` payload is ONE body; for `draft` those headings are the delimiter, so that refusal is deliberately NOT inherited. `cmd_advance` :2197 dispatches `--fill` and refuses `--to` alongside it (`fill_with_to_unsupported`) — precedent that a batching flag owns its own incompatibilities. `cmd_freeze` :1178 is "validate-then-write: every refusal fires before any write", with the floor order frozen → `contract_not_drafted` → `unflagged_freeze` → `boundary_unfilled` → scope; `draft --freeze` calls it rather than reimplementing any floor. `_phase_spans` is the ONE canonical `^##\s*<n>\s*·` scan (`_fill_and_advance`'s docstring: "never a second parser"). `_PHASE_SECTIONS` :5508 maps `direction -> (1, 2, 3, 4)`; §2 is retired in place, so the bundle's required set is {1,3,4}. Parser registry: `sub.add_parser("freeze")` :6990 · `("new-task")` :7007 · `("advance")` :7145 — `draft` registers beside them. Engine twins, all four currently md5 `54aff8b8ce3b8ee9c1cda23ee4e06f79`: `.add/tooling/add.py` · `add-method/tooling/add.py` · `add-method/.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py`; `add-method/tooling/engine_pin.py::ENGINE_MD5` (and `ENGINE_PKG_MD5`) must be re-aimed in the same commit — a hard-coded literal, never computed. Evidence the defect is real: the pay1–4 flamegraph fold (2026-07-26) — 4.9 of direction's 31 minutes spent building PLAN.md through 45 successive Edits.

Target (measurable): a bundle drafted + frozen in ONE `draft` call produces a PLAN.md byte-identical to the same bundle applied section-by-section; every one of the 5 Reject codes has a test that observes PLAN.md UNCHANGED after the refusal; `--run-red` on a green suite refuses and on a red suite proceeds; all four engine twins stay md5-identical and `ENGINE_MD5`/`ENGINE_PKG_MD5` are re-aimed; `add-method/tooling/` (2868 currently green across both floors) stays green with `advance --fill`'s own tests untouched and passing.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `.add/tooling/add.py` `add-method/tooling/` `add-method/.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.claude/skills/add/` `add-method/skill/add/` `add-method/src/add_method/_bundled/skill/add/`
Regression floor: `add-method/tooling/` — the whole method suite, in particular `test_engine_batch_ops.py` (`advance --fill`'s own all-or-nothing contract, which must keep passing UNCHANGED), `test_ci_tooling_mirror_gap.py` (pinned skip count), `test_corpus_slim.py` (ENGINE_MD5 lives in ≤3 test files) and every twin/pin parity guard.
Persona (optional): `.add/personas/tdd-verifier.md` — the refusal set is the deliverable; the happy path is one atomic write.

Least-sure flag surfaced at freeze: [contract] the engine RUNNING a test suite. Every other `add.py` verb reads and writes files it owns; `--run-red` shells out to an arbitrary command, which means a timeout, a non-zero exit that is not a test failure, and a suite with side effects are all now the engine's problem. The bounded-no-retry design is deliberate — a suite run is not idempotent-cheap, so retrying a timeout could double a side effect — but if this proves fragile the honest fallback is to make `--run-red` advisory (report red/green, never refuse) and keep the red discipline where it is today, in the agent's hands. I would rather ship the refusal and learn it is too strict than ship an observation nobody acts on.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_one_call_writes_all_three_sections: a bundle with §1/§3/§4 lands all three bodies in one call · covers: M1  [GATED]
  - test_bundle_missing_a_section_is_refused_before_any_write: PLAN.md is byte-identical after the refusal · covers: M1, R:draft_sections_missing  [GATED]
  - test_unknown_section_is_refused: a §5 in the bundle refuses, PLAN.md unchanged · covers: M1, R:draft_unknown_section  [GATED]
  - test_refusal_restores_bytes_on_every_reject_path: parametrized over all 5 Reject codes — each leaves PLAN.md byte-identical · covers: M2  [GATED]
  - test_freeze_floors_still_decide: a bundle with no lowest-confidence flag still hits unflagged_freeze under --freeze · covers: M3  [GATED]
  - test_run_red_refuses_a_green_suite: a suite that exits 0 refuses and does not freeze · covers: M4, R:red_suite_green  [GATED]
  - test_run_red_proceeds_on_a_red_suite: a suite that exits non-zero lets the freeze stamp · covers: M4  [GATED]
  - test_unrunnable_suite_is_a_refusal_not_a_skip: a command that does not exist refuses · covers: M4, R:red_suite_unrunnable  [GATED]
  - test_red_run_is_bounded_by_a_timeout: a sleeping command refuses with the limit named, and does not hang · covers: M5, R:red_suite_unrunnable  [GATED]
  - test_draft_onto_a_frozen_contract_is_refused: covers: M6, R:draft_onto_frozen  [GATED]
  - test_draft_from_stdin: `--from -` reads the bundle from stdin · covers: M1  [edge]
  - test_same_bundle_one_call_equals_section_by_section: byte-identical PLAN.md either way · covers: M1  [edge]
  - test_advance_fill_is_untouched: the existing one-section path still passes its own contract · covers: M3  [edge]
  - test_engine_files_byte_identical (EXISTING, test_tree_parity.py): the four-way mirror parity the lock-reclaim class taught — it already sweeps add.py + engine_pin.py + add_engine/* + templates/**, strictly wider than a new add.py-only check, and test_corpus_slim's census refuses a duplicate · covers: M1  [edge]
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Build-guidance (prose, not gated): the red-run subprocess must inherit no shell — pass an argv list, never `shell=True`; a bundle path that escapes the project root follows the existing scope-token fail-closed convention. Skill prose gains ONE line naming `draft` as the direction default with `advance --fill` kept for the step-wise path; it must be funded by compressing existing text, not appended.

Tests live in: `add-method/tooling/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, with three corrections the plan did not foresee. (a) Section bodies are bounded at the next `## ` OR bare `---`, exactly as `_fill_and_advance` bounds its one section — replacing heading-to-heading would have swallowed the `---` rules between sections. (b) `_bundle_sections` keeps EVERY numbered heading, including out-of-range ones, where `_phase_spans` clamps to 0..7 — otherwise a §9 in a bundle would be silently dropped instead of refused. (c) `engine_pin.py` is a four-way twin in its own right, not just a pin; mirroring add.py alone left it diverged. The skill cookbook gained the verb at a NET −118 bytes, funded by compressing the freeze line's parenthetical.
Code lives in: `add-method/tooling/`
Spawn (multi-agent): solo — one engine change mirrored to four twins; parallel workers on the same file is the divergence class this project has already been bitten by.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite)
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) every refusal test asserts PLAN.md is BYTE-IDENTICAL after the refusal, not merely that the command exited non-zero — the all-or-nothing claim is observed, not asserted; (2) `test_freeze_floors_still_decide` strips the lowest-confidence flag and confirms `unflagged_freeze` still fires under `--freeze`, so the new verb demonstrably adds no bypass; (3) the timeout test runs a 30s command under a 2s limit inside a 60s harness ceiling — if the engine ever hangs it fails on the ceiling rather than passing slowly; (4) `test_run_red_proceeds_on_a_red_suite` is the positive control that stops `red_suite_green` passing for the wrong reason (a `--run-red` that refused everything would satisfy the negative test alone); (5) `test_advance_fill_is_untouched` holds the settled `--fill` contract this task deliberately did not widen. Three of my OWN defects were caught by existing guards rather than by me: `test_tree_parity` caught the unmirrored `engine_pin.py`, and `test_corpus_slim`'s census caught that my twin-parity test duplicated a strictly wider existing sweep — both removed rather than accommodated, and neither ceiling was raised. Two failing assertions of mine were narrowed after confirming the ENGINE behaviour was correct: the pristine template carries both "FROZEN @ vN" and "Status: FROZEN" in explanatory prose, so the check is now anchored at line-start exactly as `_contract_frozen` anchors it. NOT claimed: that `--run-red`'s derived command is right for non-pytest projects — see the §1 assumption.

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-27

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, with three corrections the plan did not foresee. (a) Section bodies are bounded at the next `## ` OR bare `---`, exactly as `_fill_and_advance` bounds its one section — replacing heading-to-heading would have swallowed the `---` rules between sections. (b) `_bundle_sections` keeps EVERY numbered heading, including out-of-range ones, where `_phase_spans` clamps to 0..7 — otherwise a §9 in a bundle would be silently dropped instead of refused. (c) `engine_pin.py` is a four-way twin in its own right, not just a pin; mirroring add.py alone left it diverged. The skill cookbook gained the verb at a NET −118 bytes, funded by compressing the freeze line's parenthetical.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
