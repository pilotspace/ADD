# TASK: Risk sensitivity taxonomy in the TASK header

slug: risk-sensitivity-taxonomy · created: 2026-06-29 · stage: mvp · risk: high · sensitivity: architecture
autonomy: conservative   <!-- LOWERED: method-defining (advisor-gated-autonomy milestone) — the human owns the verify gate; engine refuses an unguarded high-risk auto completion. Original note: inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add.py:_RISK_HIGH_RE` (~959) / `_RISK_ANY_RE` (~5390) — the anchored header-dimension grammar (`(?:^|·)[ \t]*<key>:` , read from the header region only so a title/prose substring is never a declaration). `sensitivity:` mirrors this exactly, with a `([^\s<#|]+)` capture.
  - `add.py:_task_header(root, slug)` — returns the header region (text before the first `## ` heading) with HTML comments stripped; the source `_task_sensitivity` reads from.
  - `add_engine/autonomy.py:_autonomy_level(hdr)` + `_AUTONOMY_LINE_RE` + `constants._AUTONOMY_LEVELS` (~221) / `_STREAMS_POSTURES` (~225) — the closed-enum token reader pattern (returns a member · None when absent · "?" for a real-but-unknown token). `_task_sensitivity` + `_SENSITIVITY_VALUES` are the exact mirror.
  - `add.py:cmd_freeze` (672) — the human's declaration point; its validate-then-write precedence block (already_frozen → contract_not_drafted → unflagged_freeze, lines 693-701) is where `sensitivity_invalid` slots in (after unflagged_freeze, before any write).
  - `add.py:cmd_status` (1475) — surfaces the active task's autonomy/effective level; the line `sensitivity:` joins. `cmd_check` (2328) / `cmd_audit` (5419, the `risk_unset` glint ~5442) — the MEASURE template for surfacing sensitivity / sensitivity-unset (never blocks).
Context (working folder): milestone shared decisions (the human declares sensitivity at freeze; the engine NEVER classifies) + PROJECT.md. The downstream `advisor-gate-relax` task consumes a validated `sensitivity: mechanical`, so a garbage token must not survive to a frozen contract.
Honors (patterns / conventions): anchored declaration grammar (title/prose substring is never a declaration) · closed-enum reader returning member|None|"?" (mirrors autonomy/streams) · engine validates a HUMAN-declared token, never infers it · validate-then-write in cmd_freeze (every refusal before any write). BUILD TARGET = engine parity (3 git-tracked trees, ENGINE_MD5+ENGINE_PKG_MD5 pinned): edit CANONICAL `add-method/tooling/add.py` + `add-method/tooling/add_engine/{constants,taskdoc-or-new}.py`, then re-sync `_bundled/tooling/` + `.add/tooling/` byte-identical + re-pin BOTH digests (add_engine changes → ENGINE_PKG_MD5 moves too).
Anchors the contract cites: `_SENSITIVITY_VALUES` (new, constants) · `_SENSITIVITY_RE` + `_task_sensitivity(hdr)` (new) · `cmd_freeze` `sensitivity_invalid` precedence step · `cmd_status` sensitivity render · `cmd_check`/`cmd_audit` sensitivity surface

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `sensitivity:` task-header dimension — the human's freeze-time risk-class declaration
Framings weighed: anchored header token mirroring `risk:` (chosen) · a state.json `sensitivity` field · a §3 contract line
Must:
<must>
  - `_SENSITIVITY_VALUES = ("security", "data", "architecture", "mechanical")` — a closed enum in constants.py (sibling of `_AUTONOMY_LEVELS`/`_STREAMS_POSTURES`).
  - `_task_sensitivity(hdr)` reads an ANCHORED `sensitivity:` declaration from the task header region (line-start or `·`; value stops at space/`<`/`#`/`|`): returns the enum member · None when no declaration line is present · "?" for a real-but-unknown token. PURE; the engine NEVER infers sensitivity (human-declared only).
  - `add.py freeze` validates the header's sensitivity in its validate-then-write block (after `unflagged_freeze`, before any write): a present-but-unknown token ("?") refuses; absent (None) or a valid member lets the freeze proceed (absent is grandfathered).
  - `add.py status` surfaces the active task's sensitivity — a `sensitivity: <member>` line, or an explicit unset cue when absent.
  - `add.py check` surfaces each task's sensitivity and MEASURES (never blocks) a task that reached verify with no sensitivity declaration (mirrors the `risk_unset` audit glint).
</must>
Reject:
<reject>
  - `freeze` on a task whose header declares `sensitivity: <x>` with x ∉ `_SENSITIVITY_VALUES` -> "sensitivity_invalid" (the §3 `Status: DRAFT` and TASK.md are left byte-unchanged — nothing is frozen)
</reject>
After:
<after>
  - a frozen task carries at most one `sensitivity:` token and it is always a valid enum member (an unknown token can never reach a FROZEN contract).
  - `status`/`check` render the declared sensitivity; a verify-reached task with no sensitivity is surfaced as a measure, never a block.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ rejecting INVALID at freeze but ALLOWING absent (grandfather + measure) — lowest confidence because it is the enforcement-strictness call (the §3 flag): too strict would block a freeze on a typo with no escape; too loose would let a bad token survive to `advisor-gate-relax`. If wrong: re-tune which of {invalid, absent} hard-blocks. (Resolved with the human: invalid hard-blocks at freeze; absent is allowed + measured.)
  - [ ] the reader returns "?" (not None) for a real-but-unknown token so freeze can distinguish "garbage" (reject) from "absent" (allow) — confirmed by mirroring `_autonomy_level`.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: read a valid declared sensitivity
  Given a task header line "... · sensitivity: mechanical"
  When _task_sensitivity(header) runs
  Then it returns "mechanical"

Scenario: absent sensitivity reads as None
  Given a task header with no sensitivity: line
  When _task_sensitivity(header) runs
  Then it returns None

Scenario: an unknown token reads as "?"
  Given a task header line "... · sensitivity: spicy"
  When _task_sensitivity(header) runs
  Then it returns "?"

Scenario: a prose/title substring is never a declaration
  Given a header whose H1/prose contains "sensitivity: data" only mid-line (not line-start, not after ·)
  When _task_sensitivity(header) runs
  Then it returns None

Scenario: freeze refuses an invalid sensitivity
  Given a drafted, well-flagged §3 on a task whose header declares "sensitivity: spicy"
  When add.py freeze runs
  Then it exits non-zero with "sensitivity_invalid"
  And the §3 Status line stays "DRAFT" and TASK.md is byte-unchanged

Scenario: freeze proceeds with a valid sensitivity
  Given the same task but header declares "sensitivity: security"
  When add.py freeze runs
  Then §3 becomes "FROZEN @ v1 — approved by <name>"

Scenario: freeze proceeds when sensitivity is absent (grandfathered)
  Given a drafted, well-flagged §3 on a task with no sensitivity: line
  When add.py freeze runs
  Then §3 freezes (absent sensitivity never blocks the freeze)

Scenario: status surfaces the active task's sensitivity
  Given the active task header declares "sensitivity: architecture"
  When add.py status runs
  Then the output contains "sensitivity: architecture"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
constants.py
  _SENSITIVITY_VALUES = ("security", "data", "architecture", "mechanical")   # closed enum

add.py  (next to _RISK_HIGH_RE / _RISK_ANY_RE)
  _SENSITIVITY_RE = re.compile(r"(?:^|·)[ \t]*sensitivity:[ \t]*([^\s<#|]+)", re.MULTILINE)
  _task_sensitivity(hdr: str) -> str | None
     member of _SENSITIVITY_VALUES   (a valid declaration)
     None                            (no sensitivity: line in the header)
     "?"                             (a real token outside the enum)
     PURE — reads the header region only; never inferred.

add.py cmd_freeze  (validate-then-write precedence, after unflagged_freeze)
  _task_sensitivity(hdr) == "?"  -> _die("sensitivity_invalid: <slug> declares an unknown
                                          sensitivity '<tok>' — one of security|data|
                                          architecture|mechanical")   # no write
  None or a valid member          -> freeze proceeds (absent grandfathered)

add.py cmd_status   -> prints "sensitivity: <member>" for the active task (or an unset cue)
add.py cmd_check / cmd_audit
  surfaces each task's sensitivity; a verify-reached task with no sensitivity -> a MEASURE
  (glint, mirrors risk_unset) — never blocks.

Schema: TASK.md header gains an optional `sensitivity:` token (human-declared). state.json
  is NOT a source of truth for sensitivity (read live from the header, like risk/autonomy).
```

`Least-sure flag surfaced at freeze:` [contract] invalid sensitivity hard-blocks at freeze while absent is grandfathered + measured — resolved with the human (Approve-as-proposed); if wrong, re-tune which of {invalid, absent} hard-blocks. Cost: a re-freeze of the predicate, no data migration.
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

Coverage target: every Must + the named Reject
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_reads_valid_member: header "· sensitivity: mechanical" -> _task_sensitivity == "mechanical"
  - test_absent_reads_none: header with no sensitivity line -> _task_sensitivity is None
  - test_unknown_token_reads_question: header "· sensitivity: spicy" -> _task_sensitivity == "?"
  - test_prose_substring_not_a_declaration: mid-line/title "sensitivity: data" -> _task_sensitivity is None
  - test_freeze_refuses_invalid_sensitivity: drafted+flagged §3, header "sensitivity: spicy"; freeze -> exit!=0 + "sensitivity_invalid"; assert §3 still "Status: DRAFT" + TASK.md bytes unchanged
  - test_freeze_proceeds_valid_sensitivity: header "sensitivity: security"; freeze -> §3 "FROZEN @ v1"
  - test_freeze_proceeds_absent_sensitivity: no sensitivity line; freeze -> §3 frozen (absent never blocks)
  - test_status_shows_sensitivity: active task header "sensitivity: architecture"; status stdout contains "sensitivity: architecture"
</test_plan>

Tests live in: `add-method/tooling/test_sensitivity_taxonomy.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`
Strategy (ordered batches): 1. write the 8 red tests (test_sensitivity_taxonomy.py) · 2. add `_SENSITIVITY_VALUES` to constants.py (+ import into add.py) · 3. add `_SENSITIVITY_RE` + `_task_sensitivity(hdr)` next to `_RISK_ANY_RE` in add.py · 4. hook `sensitivity_invalid` into cmd_freeze's validate-then-write block (after unflagged_freeze, before any write) · 5. render `sensitivity:` in cmd_status (active task) + surface in cmd_check/cmd_audit as a measure · 6. green on canonical · 7. prepare_bundle + dogfood-sync byte-identical · 8. re-pin BOTH ENGINE_MD5 (add.py) AND ENGINE_PKG_MD5 (constants.py changed) · 9. full suite green.
Known-problem fixes: a new CLI surface/measure may need a test_min_pillar lifecycle touch → run the full suite, fix any min-pillar/exclude-set assertion (do test edits in the TESTS phase; re-cross tests→build to re-baseline the tamper snapshot) · constants change moves ENGINE_PKG_MD5 → re-pin it too (not only ENGINE_MD5) · the freeze reject must fire BEFORE any write (validate-then-write) so TASK.md stays byte-unchanged on reject.
Strategy actually used: as planned — 8 red tests → `_SENSITIVITY_VALUES` (constants) → `_SENSITIVITY_RE`+`_task_sensitivity` (add.py, beside the risk regexes) → cmd_freeze `sensitivity_invalid` (validate-then-write) → cmd_status render + cmd_audit `sensitivity_unset` measure → sync + re-pin BOTH digests. As the known-problem note predicted, the new `sensitivity_unset` measure made 2 clean-board tests (test_gate_audit, test_audit_ci) and the IMPORTERS meta-test (test_md_section) red — fixed by adding `· sensitivity: mechanical` beside the existing `· risk: normal` in their clean-board arrangements (done in the TESTS phase, then tests→build re-crossed to re-baseline the tamper snapshot).
Safety rule (feature-specific): sensitivity_invalid is validate-then-write — no TASK.md/state mutation on a rejected freeze.
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

- [x] all tests pass — full suite **2303 passed, OK**
- [x] coverage did not decrease — net-new code with 8 net-new tests covering every Must + the named Reject
- [x] no test or contract was altered during build — §3 frozen untouched; the only test edits (2 sibling clean-board arrangements) were made in the TESTS phase and tests→build re-crossed to re-baseline the tamper snapshot
- [x] the green was EARNED — refute-read below (real CLI freeze runs + byte-compares + the anchor test)
- [x] concurrency / timing safe — cmd_freeze stays validate-then-write (the reject fires before any write; TASK.md byte-unchanged on reject); the reader is PURE/read-only
- [x] no exposed secrets, injection openings, or unexpected dependencies — closed enum, anchored regex, zero new deps
- [x] layering & dependencies follow CONVENTIONS.md — enum in constants.py, reader + command edits in add.py beside the risk dimension — exact mirror of the risk/autonomy layering
- [ ] a person reviewed and approved the change — **YOUR gate (conservative)**

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `_task_sensitivity` returns the member for a `· sensitivity: mechanical` header, None when absent, "?" for an unknown token, None for a prose/title substring — confirmed by the 4 reader tests + live (data/None/?/None)
- [x] `add.py freeze` on a `sensitivity: spicy` task exits non-zero with `sensitivity_invalid` and leaves TASK.md byte-unchanged; a valid or absent sensitivity freezes to `FROZEN @ v1` — confirmed by the 3 freeze tests
- [x] `add.py status` prints a `sensitivity: architecture` line for the active task — confirmed by the status test + live (this task's own header)
- [x] `add.py audit` measures (never blocks) a verify-reached task with no `sensitivity:` — confirmed live: `sensitivity_unset — 97 task(s)`, audit still exit 0 (this task NOT flagged, it declares architecture)
- [x] all 3 engine trees byte-identical (0c38c169…); BOTH ENGINE_MD5 + ENGINE_PKG_MD5 (0617c719…) re-pinned; full suite green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_SENSITIVITY_VALUES` (constants) → imported into add.py, used by `_task_sensitivity` + the freeze error message; `_task_sensitivity` → used by cmd_freeze + cmd_status + `_guarantee_lint_notices`; `_SENSITIVITY_RE` → used by `_task_sensitivity`; `sensitivity_unset` glint → returned + printed + in the clean-condition. All referenced.
- [x] DEAD-CODE (code) — no orphaned symbol; every new name has a caller / surface
- [ ] SEMANTIC (prose / non-code) — n/a (code task; the docs-align task carries the book/glossary prose)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (a) overfit — freeze tests run the real `freeze` command against arranged temp tasks, not hardcoded fixtures; (b) vacuous — the invalid-freeze test asserts BOTH the error string AND §3-still-DRAFT AND TASK.md byte-equality (a no-op impl would fail the byte/DRAFT asserts); (c) anchor bypass — the reader-anchor test proves a prose/title `sensitivity:` substring is not read as a declaration; (d) stub — `_task_sensitivity` is a real anchored parser, validated live (data/None/?/None).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose anchored header token mirroring `risk:`; rejected a state.json `sensitivity` field · a §3 contract line
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — 8 red tests → `_SENSITIVITY_VALUES` (constants) → `_SENSITIVITY_RE`+`_task_sensitivity` (add.py, beside the risk regexes) → cmd_freeze `sensitivity_invalid` (validate-then-write) → cmd_status render + cmd_audit `sensitivity_unset` measure → sync + re-pin BOTH digests. As the known-problem note predicted, the new `sensitivity_unset` measure made 2 clean-board tests (test_gate_audit, test_audit_ci) and the IMPORTERS meta-test (test_md_section) red — fixed by adding `· sensitivity: mechanical` beside the existing `· risk: normal` in their clean-board arrangements (done in the TESTS phase, then tests→build re-crossed to re-baseline the tamper snapshot).
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
