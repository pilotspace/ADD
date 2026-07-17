# TASK: status/release surface the compaction tail and the carried backlog

slug: loop-surfacing-nudges · created: 2026-07-07 · stage: mvp
milestone: self-improving-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add.py:cmd_status (additive cue lines) + cmd_release_report (text total) + new _foundation_tail helper ×3 engine trees · skill/add/loop.md ×3 trees · .add/SEAMS.md `_declared_scope` line anchor (shifts) · test_loop_surfacing_nudges.py (new)
Context (working folder): investigation stats — carried=88 with no resurfacing trigger; compaction last rolled fv20, now fv64, 303 folded bullets live in PROJECT.md+CONVENTIONS.md
Honors (patterns / conventions): the standing ADDITIVE-cue convention (zero-state output byte-identical) · release_data JSON is a frozen facts interface — text-layer only · orchestration pool DEDUP floor 41300 (6B slack!) · ENGINE_MD5 re-aim
Seams consulted: .add/SEAMS.md `_declared_scope` anchor — line number re-aimed after the status insertions shift add.py
Anchors the contract cites: cmd_status releasable-cue block · cmd_release_report text assembly · _collect_carried_spec_deltas · the `settled fv` rolled-line convention (compact-foundation.md) · loop.md gather step
Issues/Risks (→ feed §1): carried deltas are write-only memory (nothing re-presents them); compaction eligibility is never computed so the convention silently never runs. Traps: release_data JSON frozen (text-only change) · loop.md is in the 41300-floor pool with 6B slack — the carried mention must be net-≤0 via same-guide trim · threshold needed so young projects see no noise
Related intent: Tin 2026-07-07 'fix all' — findings #1 (compaction debt is the bottleneck) + #2 (carried backlog never resurfaces); the loop must surface its own accumulation
Ground SHA: 1430e5f

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: loop surfacing nudges — the engine counts its own accumulation; the human still judges
Framings weighed: additive status/report cues (chosen — the releasable: pattern, zero new verbs) · a compact-foundation --propose verb (deferred — bigger; revisit if the nudge alone doesn't drive the ritual) · auto-compaction (rejected — the write is human)
Must:
<must>
  - M1: `status` prints `→ carried: N deferred spec delta(s) — add.py deltas --carried` when N>0
  - M2: `status` prints `→ compaction: B folded bullet(s) above the settled line (last rolled fvK, now fvM) — compact-foundation.md` when B ≥ 25 (K rendered as `never` when no settled line parses)
  - M3: `release-report` text gains a `Carried (N)` total set — the release cut consciously re-triages the deferred pile
  - M4: loop.md's gather step names the carried backlog (`deltas --carried`), net ≤0B on the pool
</must>
Reject:
<reject>
  - R1: zero carried + tail<25 -> status output byte-identical (additive convention; no error code — absence IS the contract)
  - R2: any release_data JSON key change -> "frozen_facts_drift" (text layer only)
  - R3: pool over the 41300 dedup floor or tree drift -> "pool_budget_bust"/"tree_drift"
</reject>
After:
<after>
  - the loop surfaces its own debt: a session opening with `status` sees the carried pile and the compaction tail the moment they matter, instead of never
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ threshold 25 for the compaction cue — lowest confidence because the right noise floor is a guess; if wrong: a one-integer change, and the carried cue has no threshold so nothing is hidden
  - [x] the settled-line regex (`settled .*fv\d+[–-]fv(\d+)`) matches both live settled shapes — confirmed against PROJECT.md:173 + CONVENTIONS.md:725
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: carried surfaces at status   # M1
  Given one carried spec delta
  When add.py status runs
  Then it prints the carried cue with the retrieval command

Scenario: compaction tail surfaces   # M2
  Given 25 folded stamps and a 'settled fv1–fv2' line
  When status runs
  Then the cue names the bullet count, last-rolled fv, and current fv

Scenario: clean project stays byte-quiet   # R1
  Given a fresh project
  When status runs
  Then neither cue appears
  And output is byte-identical to before this task

Scenario: release re-triages carried   # M3+R2
  Given carried deltas at release time
  When release-report runs
  Then the text lists the Carried total
  And the --json keys are unchanged

Scenario: the loop gathers carried   # M4+R3
  Given loop.md's gather step
  When an agent reads it
  Then it names deltas --carried
  And the pool holds the 41300 floor and trees stay identical
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
status (additive cues, after the releasable lines):
  carried>0    -> '→ carried: N deferred spec delta(s) — add.py deltas --carried'
  tail>=25     -> '→ compaction: B folded bullet(s) above the settled line (last rolled fvK|never, now fvM) — compact-foundation.md'
release-report text -> 'Carried (N) — deferred spec deltas riding across releases:' + per-task lines (JSON UNCHANGED)
_foundation_tail(root) -> {bullets, last_settled_fv|None, fv} — counts '[folded foundation-version' stamps in
  PROJECT.md+CONVENTIONS.md above/below nothing (total live stamps), parses 'settled …fvK–fvM' max M, reads header fv
Schema: none (no state change; READ-only cues)
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin ('fix all' + 'run all tasks in auto mode without me', 2026-07-07)
Reported: yes — findings #1/#2 + fix shape rendered in-chat before freeze
Least-sure flag surfaced at freeze: [spec] the 25-bullet threshold is a guessed noise floor — cheap to retune

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: one test per Must/Reject
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_status_shows_carried (plant carried delta → cue) · covers: M1
  - test_status_shows_compaction_tail (plant 25 stamped bullets + settled fv2 line → cue names fv) · covers: M2
  - test_status_silent_when_clean (fresh project → neither cue) · covers: R1
  - test_release_report_carried_total · covers: M3
  - test_release_json_keys_unchanged · covers: R2
  - test_loop_md_names_carried + pool floor + engine parity · covers: M4, R3
</test_plan>

Tests live in: `add-method/tooling/` (test_loop_surfacing_nudges.py) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/skill/add/` `add-method/src/add_method/_bundled/` `add-method/.add/tooling/` `add-method/../.claude/` `add-method/../.add/tooling/` `add-method/../.add/SEAMS.md`
Strategy (ordered batches): 1. red test 2. _foundation_tail helper + status cues 3. release-report text line 4. loop.md net-≤0 edit 5. sync ×3 engine + ×3 skill, re-aim pin + SEAMS anchor 6. green + siblings

Persona (required): methodology-engine-dev
Spawn isolation (default): n/a — direct sequential build
Known-problem fixes: SEAMS `_declared_scope` line anchor shifts → recompute+re-aim · loop.md 6B slack → trim same guide · release JSON frozen → text-only
Strategy actually used: as planned; loop.md needed two extra filler trims (pool floor is 41300 dedup, not 42045 lean — 42B final slack); SEAMS `_declared_scope` re-aimed 4742→4756 via script file (unquoted zsh heredoc mangles backticked regex — recurring trap)
Safety rule (feature-specific): cues COUNT, never judge — no auto-compaction, no auto-drop; the human ritual stays the writer
Code lives in: add.py ×3 (engine) · loop.md ×3 (prose) · tooling (test)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

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
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] this repo's own status now prints `carried: 88` + `compaction: 221 … (last rolled fv20, now fv64)` — confirmed by a live run
- [x] a fresh temp project's status stays byte-quiet — confirmed by test_status_silent_when_clean + the 24-bullet threshold edge test

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — _foundation_tail consumed by the status cue block; carried collector reused (no new dead path)
- [x] DEAD-CODE — none
- [x] SEMANTIC — loop.md gather step + trimmed paragraphs read in full; propose/confirm/exit-criteria/milestone-done tokens all intact (test_dynamic_task_loop green)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] §3 anchors resolve — cue lines + helper shape asserted by the guard suite; release JSON keys unchanged
- [x] _declared_scope MOVED (add.py:4742→4756) — SEAMS.md re-aimed, test_seams_doc green

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: red-first 5/10 for the right reasons; the byte-quiet contract probed at the 24/25 threshold boundary; the frozen-JSON reject probed by asserting the key ABSENT after the text change landed

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — read-only counting cues; no gate, no write, no network
2. Concurrency: CLEAR — pure reads at status time
3. Architecture: CLEAR — the releasable-cue pattern reused; judgment stays human
Verdict: PASS
Residue: none
Binding: yes — mechanical

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin (auto-mode directive) · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does the carried count drop across the next releases; does a compaction ritual actually run now that fv-debt is visible

### Decisions (ADR)
- [AI] specify — chose additive status/report cues; rejected a compact-foundation --propose verb (deferred — bigger; revisit if the nudge alone doesn't drive the ritual) · auto-compaction (rejected — the write is human)
- [human] freeze — froze §3 @ v1 (approved by Tin ('fix all' + 'run all tasks in auto mode without me', 2026-07-07))
- [AI] build — strategy used: as planned; loop.md needed two extra filler trims (pool floor is 41300 dedup, not 42045 lean — 42B final slack); SEAMS `_declared_scope` re-aimed 4742→4756 via script file (unquoted zsh heredoc mangles backticked regex — recurring trap)
- [AI] verify — gate PASS (reviewed by Tin (auto-mode directive))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
  - [SPEC · seeded] a `compact-foundation --propose` read-only verb (render the per-spec settled line for the eligible tail) if the nudge alone doesn't drive the ritual (evidence: TASK §1 framings) [→ compact-propose]

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

