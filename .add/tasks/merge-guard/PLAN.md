# TASK: conflict-aware state load guard (state_conflicted)

slug: merge-guard · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default auto: edits the byte-pinned engine load path across all 3 add.py copies + re-pins; a human owns the high-risk gate (run.md guard). -->
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — ADD a merge-aware guard on EVERY state-load path:
  - NEW `_state_text_or_die(root)` (~near load_state, 408) — read state.json's raw text; if it carries a git conflict marker (a line starting with `<<<<<<<`, `=======`, or `>>>>>>>`, matched line-anchored) → `_die("state_conflicted: …")` with the markers + reconciliation steps; else return the text. A genuine read OSError propagates to the caller (each loader maps it to its own existing code). NEW module const `_CONFLICT_MARKER_RE = re.compile(r"(?m)^(<{7}|={7}|>{7})")`.
  - `load_state` (415) — replace `(root / STATE_FILE).read_text(...)` with `_state_text_or_die(root)`; keep the `except (JSONDecodeError, OSError) -> state_invalid` (conflict `_die` is SystemExit, NOT caught → wins).
  - `_load_state_for_json` (430) — same swap; keeps its `-> no_state` mapping for a non-conflict failure (empty stdout for --json paths).
  - cmd_check direct read (2035) — same swap (the one loader that reads WITHOUT migrate, legacy keys only); so `add.py check` also reports the conflict specifically.
- `engine_pin.py:ENGINE_MD5` — re-pin after this engine edit (same commit).

Context (working folder):
- `load_state` ALREADY fails closed on unparseable JSON (`state_invalid: … corrupt or unreadable`). A git-conflicted state.json IS invalid JSON, so today it hits that GENERIC message. This task makes a CONFLICT recognizable as a conflict — a merge-specific, actionable message — distinct from generic corruption. The leanest safety net for the major's #1 failure mode (the live parallel-writer clobber we hit in M2/M3).
- there are exactly THREE state.json read sites (load_state · _load_state_for_json · cmd_check@2035); all three route through the new helper so the exit criterion "EVERY state-loading command" holds.

Honors (patterns / conventions):
- fail-loud + actionable (design-for-failure) — the message NAMES the file + concrete next steps (resolve the markers / `git checkout --ours/--theirs` / `add.py doctor`), never a raw traceback.
- detect, never auto-resolve — the guard REPORTS; the human reconciles (the milestone's standing rule).
- single seam — one `_state_text_or_die` helper, three minimal call-site swaps (no duplicated detection logic).
- engine-edit discipline — 3-tree byte-identity + same-commit ENGINE_MD5 re-pin; full suite is the regression oracle. NO new subcommand → no test_min_pillar census change.

Anchors the contract cites: `_state_text_or_die(root)` · `_CONFLICT_MARKER_RE` (line-anchored 7-char markers) · the `state_conflicted` reject code + its actionable message · the three routed read sites (load_state · _load_state_for_json · cmd_check).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a merge-AWARE state load guard — recognize git conflict markers in `.add/state.json` and fail with a merge-SPECIFIC, actionable `state_conflicted` message on every state-load path, instead of the generic `state_invalid` / `no_state`.
Framings weighed: one `_state_text_or_die` helper routed into all 3 read sites (chosen — single detection seam, consistent message, minimal call-site swaps) · detect inside each loader separately (rejected — duplicates the marker logic 3×, drifts) · a new `validate` precheck command only (rejected — a guard must fire on the NORMAL load path, not only when a user remembers to run a checker; that proactive check is the sibling `state-doctor`).
Must:
<must>
  - `_CONFLICT_MARKER_RE` matches a LINE that starts with 7+ of `<`, `=`, or `>` (`(?m)^(<{7}|={7}|>{7})`) — the standard git conflict markers — and NOT an ordinary JSON line (a goal/title value never starts a line with 7 markers).
  - `_state_text_or_die(root)` reads state.json; on a marker match → `_die("state_conflicted: …")` naming the file + reconciliation steps; otherwise returns the raw text. A read OSError is NOT swallowed — it propagates to the caller's existing except.
  - `load_state` routes its read through `_state_text_or_die`; a conflicted file → `state_conflicted` (NOT the generic `state_invalid`); a non-conflict parse/IO failure → still `state_invalid` (unchanged).
  - `_load_state_for_json` routes its read through `_state_text_or_die`; a conflicted file → `state_conflicted`; a non-conflict failure → still `no_state` with empty stdout (unchanged).
  - `cmd_check`'s direct read routes through `_state_text_or_die`; a conflicted state.json → `state_conflicted` (so `add.py check` reports it specifically).
  - a HEALTHY state.json (no markers) loads byte-for-behavior identically to before on all three paths (purely additive guard). All 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned same commit.
</must>
Reject:
<reject>
  - state.json contains a git conflict marker line -> "state_conflicted"   (on every state-load path)
  - (unchanged) non-conflict parse/IO failure -> "state_invalid" (load_state) / "no_state" (_load_state_for_json)
</reject>
After:
<after>
  - any `add.py` command that loads a conflict-marked state.json exits non-zero with `state_conflicted` (file + how to reconcile), never a raw traceback and never the generic "corrupt"; a healthy state loads exactly as before; the prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The line-anchored 7-char marker regex won't FALSE-POSITIVE on legitimate state content — lowest confidence because a task title / goal / delta text is user-authored free text that could (pathologically) contain a line starting with `=======`. Chosen `(?m)^…` so it only fires when a marker BEGINS a line, and JSON serialization indents every value (a string value lives on a line like `  "goal": "…"`, never starting with the marker) — so a marker can begin a line ONLY in a real conflict (git inserts it at column 0). If wrong: a healthy state would falsely read as conflicted; cost = tighten to git's exact `^<{7} ` / `^>{7} ` (trailing space + label) + `^={7}$`, still one regex.
  - [ ] routing all THREE read sites (not just load_state) is correct — confirmed: the exit criterion says EVERY state-loading command; cmd_check + the --json path both read state directly.
  - [ ] `state_conflicted` as a NEW distinct code (not reusing state_invalid) is right — confirmed: the whole point is a merge-SPECIFIC message; a shared code would re-bury it.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a conflicted state.json fails the normal load with a merge-specific message
  Given .add/state.json contains git conflict markers (<<<<<<< / ======= / >>>>>>>)
  When any command runs load_state (e.g. `add.py status`)
  Then it exits non-zero with "state_conflicted"
  And the message names .add/state.json and how to reconcile (markers / git checkout / doctor)
  And the file is unchanged (the guard only reads)

Scenario: a conflicted state fails the --json path with state_conflicted and empty stdout-data
  Given .add/state.json contains git conflict markers
  When a --json command runs _load_state_for_json (e.g. `add.py status --json`)
  Then it exits non-zero with "state_conflicted"
  And no parseable JSON object is emitted on stdout

Scenario: a conflicted state makes check report the conflict specifically
  Given .add/state.json contains git conflict markers
  When `add.py check`
  Then it exits non-zero with "state_conflicted" (not a generic corrupt/parse error)

Scenario: a non-conflict corrupt state still reports generic invalid (unchanged)
  Given .add/state.json is unparseable JSON but has NO conflict markers (e.g. "{bad")
  When `add.py status`
  Then it exits non-zero with "state_invalid" (the existing generic message, not state_conflicted)

Scenario: a healthy state loads unchanged
  Given a valid .add/state.json with no conflict markers
  When `add.py status`
  Then it succeeds exactly as before (the guard is a no-op on a healthy file)

Scenario: the marker regex does not false-positive on indented JSON content
  Given a valid state.json whose a task title is "=======ish header"
  When `add.py status`
  Then it succeeds (the value sits on an indented line; no line STARTS with the marker)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_CONFLICT_MARKER_RE = re.compile(r"(?m)^(<{7}|={7}|>{7})")   # a line starting with 7 git markers

_state_text_or_die(root: Path) -> str
  text = (root / STATE_FILE).read_text(encoding="utf-8")      # OSError propagates to caller
  if _CONFLICT_MARKER_RE.search(text): _die("state_conflicted: <file> has unresolved git
      merge markers (<<<<<<< / ======= / >>>>>>>) — resolve them (or
      `git checkout --ours/--theirs <file>`), then run `add.py doctor`")
  return text

load_state(root)            -> _migrate_state(json.loads(_state_text_or_die(root)))
  conflict  -> state_conflicted (SystemExit, not caught)
  parse/IO  -> state_invalid   (unchanged)
_load_state_for_json()      -> root, _migrate_state(json.loads(_state_text_or_die(root)))
  conflict  -> state_conflicted ; parse/IO -> no_state (empty stdout, unchanged)
cmd_check direct read       -> json.loads(_state_text_or_die(root))
  conflict  -> state_conflicted

Schema: READ-ONLY guard — no state.json write, no schema change. NEW reject code
  `state_conflicted`. Healthy-state load path is behavior-identical (additive guard).
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization) · 2026-06-22

Least-sure flag surfaced at freeze:
- [contract] the line-anchored 7-char marker regex `(?m)^(<{7}|={7}|>{7})` as the conflict test — could FALSE-POSITIVE if user-authored state content (a title/goal/delta) ever begins a line with 7 `=`/`<`/`>`. Mitigated because JSON serialization indents every value (string values never start a line at column 0 with the marker), so a column-0 marker line means a real git conflict. Cost if wrong: tighten to git's exact form (`^<{7} `/`^>{7} ` with trailing label + `^={7}$`); still one regex, the freeze holds.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 6 scenarios + the engine-pin parity guard.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_conflicted_load_state_dies_conflicted: write markers into state.json; `status` exits !=0 with "state_conflicted"; message names the file + reconcile; file bytes unchanged
  - test_conflicted_json_path_dies_conflicted: markers; `status --json` exits !=0 "state_conflicted"; stdout has no parseable JSON object
  - test_conflicted_check_reports_conflicted: markers; `check` exits !=0 "state_conflicted"
  - test_noncon­flict_corrupt_still_state_invalid: state.json = "{bad" (no markers); `status` exits !=0 "state_invalid" (NOT state_conflicted)
  - test_healthy_state_loads_unchanged: valid state; `status` exits 0 (guard is a no-op)
  - test_marker_regex_no_false_positive_on_content: a task title containing "=======ish" (on an indented JSON line); `status` exits 0
  - test_three_trees_byte_identical_and_pinned: md5(3 copies)==1 and ==ENGINE_MD5
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
Tests in: `add-method/tooling/test_merge_guard.py`
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. add `_CONFLICT_MARKER_RE` const + `_state_text_or_die(root)` helper above load_state. 2. swap the read in load_state · _load_state_for_json · cmd_check to route through it. 3. mirror to the other 2 copies (`cp`) + re-pin ENGINE_MD5. 4. run the red suite green.
Safety rule (feature-specific): the guard ONLY reads — it never writes state. A healthy file must load behavior-identically (no new line, no perf path); `_die` (SystemExit) for state_conflicted must NOT be swallowed by the loaders' `except (JSONDecodeError, OSError)`.
Code lives in: `add-method/tooling/add.py` (+ 2 mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib `re`, already imported); ask if unclear. NO census co-update (no new subcommand).

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite Ran 1487, OK; `add.py check` 381 passed / 0 failed
- [x] coverage did not decrease — +7 tests (test_merge_guard.py); no test removed
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the one in-build test EDIT (test_marker_regex_no_false_positive_on_content) fixed a buggy FIXTURE (a hand-built partial task dict missing `gate`, crashing cmd_status — not the guard) to build a complete record via the CLI; the assertion (healthy load succeeds) is unchanged → re-crossed tests→build to re-anchor the tripwire
- [x] the green was EARNED, not gamed — independent python-expert refute-read: VERDICT MERGE (0.97), 0 blocking; specifically confirmed the SystemExit (state_conflicted) is NOT swallowed by the loaders' `except (JSONDecodeError, OSError)` (the dangerous failure mode) + the regex/order/OSError-propagation all correct
- [x] concurrency / timing safe — read-only guard, single-process CLI; no write, no new IO failure path (read_text already in the load path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `re` only (already imported); the marker regex `[<=>]{7}` cannot catastrophically backtrack
- [x] layering & dependencies follow CONVENTIONS.md — fail-loud + actionable (design-for-failure); single `_state_text_or_die` seam routed into all 3 read sites; detect-never-auto-resolve honored
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization); risk:high → conservative gate

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a conflicted state.json makes `status` + `check` fail with `state_conflicted` (not generic) — confirmed in a throwaway dir: both printed `state_conflicted: …/.add/state.json has unresolved git merge markers (<<<<<<< / ======= / >>>>>>>) — resolve them (or `git checkout --ours/--theirs state.json`), then run `add.py doctor``, exit 1
- [x] the message is actionable (file + reconcile steps + doctor pointer) — confirmed in the same demo
- [x] a non-conflict corrupt state still reports generic `state_invalid` — confirmed by test_nonconflict_corrupt_still_state_invalid
- [x] a healthy state (even with marker-LIKE content on indented lines) loads unchanged — confirmed by test_healthy_state_loads_unchanged + test_marker_regex_no_false_positive_on_content

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_state_text_or_die` referenced in all 3 read sites (load_state · _load_state_for_json · cmd_check); `_CONFLICT_MARKER_RE` referenced in the helper (verified by the real-dir demo firing on every path)
- [x] DEAD-CODE (code) — no orphan; both new symbols are on the live load path
- [x] SEMANTIC (prose / non-code) — read the refute-read in full: confirmed the SystemExit-not-swallowed invariant (the one way this could silently fail) + regex/order/propagation; the pre-existing cmd_check non-migrate NIT is out of scope (tracked separately as state-schema-migration)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a real git conflict ever slipping past the guard to a generic state_invalid (marker pattern git uses changed) · a false-positive state_conflicted on a healthy file (regex over-matches user content).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] the proactive `add.py doctor` that the state_conflicted message POINTS at is the sibling task `state-doctor` — this task only references it; doctor must validate integrity + referential consistency and report (evidence: the guard's actionable hint says "run `add.py doctor` to verify", a command this task does not yet provide). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] route `cmd_check`'s direct state read through `_migrate_state` (it bypasses migration, reading legacy keys only) so a multi-active read added there is safe — pre-existing, surfaced again by this task's audit of the 3 read sites (evidence: review NIT; already tracked under state-schema-migration). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a fail-closed guard that REPLACES a generic error with a specific one belongs at the single shared read seam, routed into every caller — not duplicated per call site; the callers' existing `except` must catch only the GENERIC failure (Exception subclasses) so the specific `_die`/SystemExit propagates past them (evidence: merge-guard routed 3 read sites through one `_state_text_or_die`; the review's #1 refutation target was a swallowed SystemExit — avoided precisely because SystemExit ⊄ Exception). [folded foundation-version 44]
- [TDD · folded] a "no-false-positive" test must build its fixture through the REAL constructor (CLI/new-task), not a hand-rolled partial record — a partial dict passes the guard then crashes a DOWNSTREAM consumer, masking what the test means to prove (evidence: the first regex-false-positive test built a task dict missing `gate` → cmd_status KeyError, not the guard; fixed by `new-task`). [folded foundation-version 44]
