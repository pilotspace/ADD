# TASK: Route §3 Glossary Deltas Through Fold Into GLOSSARY.md

slug: fold-glossary-deltas · created: 2026-07-03 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `.add/tooling/add.py:cmd_fold`(~L5835-5987), `_FOLD_ROUTES`(~L5762-5768), `_collect_open_deltas`(~L5572-5629) — the competency-delta fold pipeline this task mirrors; `.add/GLOSSARY.md` (currently hand-maintained flat `Term: definition` lines, ZERO fold-provenance stamps on any existing line); every task's §3 `Glossary deltas:` line (currently a single free-text line per task)
Context (working folder): `add.py fold --comp <DDD|SDD|UDD|TDD|ADD>` currently narrows competency-only folding; no existing flag/path touches GLOSSARY.md at all — `add.py` only ever READS it (`_project_sensitivity_classes`, ~L1197)
Honors (patterns / conventions): mirrors `cmd_fold`'s existing "validate-ALL-then-write, atomic, mechanized transcription, human-runs-the-command-as-confirmation" shape for competency deltas — same session/version-bump discipline, same all-or-nothing multi-file write primitive (`_atomic_write_many`)
Seams consulted: none cited
Anchors the contract cites: `_FOLD_ROUTES`, `cmd_fold`, `_collect_open_deltas`, `.add/GLOSSARY.md`
Issues/Risks (→ feed §1): (1) mechanically parsing EVERY historical task's free-text Glossary-deltas line is unsafe — a direct grep of real tasks found several that don't fit a clean `Term: definition` shape: an em-dash instead of a colon (`reclaim-ticket-race`), two terms in one sentence (`search-index`, `seams-doc`), or a meta-pointer to content already hand-added ("both listed above" — `seams-doc`) — blindly transcribing these risks duplicate/garbage GLOSSARY.md entries. (2) GLOSSARY.md's OWN existing ~40 lines carry ZERO fold-provenance stamps (unlike PROJECT.md/CONVENTIONS.md's stamped competency bullets) — matching that file's own established, unstamped convention means the NEW mechanism should append clean, unstamped `Term: definition` lines to GLOSSARY.md itself, while provenance (which task, which fold session) lives in the TASK.md's OWN line (stamped after fold) and the shared Key Decisions row, exactly like the competency mechanism already does.
Related intent: seeded from search-index spec-delta — both search-index's and the sibling rule-id-coverage's declared terms sat absent from GLOSSARY.md while mid-flight, consistent with a done/fold deferral but never explicitly confirmed as the intended lifecycle until now [← search-index]
Ground SHA: `1ef7132`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: extend `add.py fold` to ALSO consolidate a DONE task's §3 `Glossary deltas:` line into `.add/GLOSSARY.md`, mirroring the competency-delta fold's mechanized/atomic/stamped-in-place shape — but SCOPED to lines matching a clean `Term: definition` shape (task is done + line isn't "none" + isn't already fold-stamped + parses as `<term>: <definition>`); a line that doesn't parse cleanly is silently skipped, never guessed at (from search-index spec-delta; confirmed by Tin Dang, 2026-07-03: Glossary deltas defer to fold, project-wide, same as competency deltas)
Framings weighed: extend `cmd_fold` with a 6th pseudo-competency `GLOSSARY` sharing the SAME atomic multi-file write + version-bump session (chosen — reuses the proven mechanism, one bump covers both classes in one run) · a wholly separate `add.py fold-glossary` command — rejected, needless duplication of the atomic-write/versioning machinery for a closely related concern · retroactively, mechanically sweeping ALL historical free-text Glossary-deltas lines regardless of shape — rejected (Ground finding: several don't fit a safe mechanical shape) in favor of a strict-shape-match-or-skip rule, silently safe on the messy historical corpus and fully mechanized going forward
Must:
<must>
  - a DONE task whose `Glossary deltas:` line is not "none", not already fold-stamped, and parses as `<term>: <definition>` (the first top-level colon splits term/definition) is a fold candidate
  - folding appends `<term>: <definition>` as a new, UNSTAMPED line to GLOSSARY.md (matching that file's own existing, unstamped convention) UNLESS a line already starting with the identical term (case-insensitive) is already present, in which case it is skipped (never duplicated)
  - the task's OWN `Glossary deltas:` line gets ` [folded foundation-version N]` appended in place after a successful fold (mirrors the competency mechanism's own open->folded stamp, applied to a single line rather than a repeated tag)
  - folding Glossary deltas shares the SAME atomic multi-file write + ONE version bump as an in-progress competency fold when both are selected in the same `add.py fold` run
  - a line that does not parse as `<term>: <definition>` (no colon, or "none", or already stamped) is silently skipped — never an error, never a partial/guessed transcription
</must>
Reject:
<reject>
  - transcribing a Glossary-deltas line that doesn't cleanly parse -> reject; skip silently, never guess
  - duplicating a term that's already a line in GLOSSARY.md (case-insensitive prefix match) -> reject; skip, don't re-add
  - stamping GLOSSARY.md's own new line with a `[folded ...]` suffix -> reject; GLOSSARY.md's existing convention is unstamped lines; provenance lives in the TASK.md's own stamped line + the Key Decisions row instead
  - folding a task that is not yet `done` -> reject; only a closed task's declared term is stable enough to fold
</reject>
After:
<after>
  - `add.py fold` (no `--comp`, or `--comp GLOSSARY`) also consolidates every done task's clean, unfolded Glossary-deltas line into GLOSSARY.md
  - each task's own line is stamped `[folded foundation-version N]` afterward, idempotent against a second `fold` run
  - GLOSSARY.md gains new terms with zero visual disruption to its existing unstamped lines
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ silently skipping any Glossary-deltas line that doesn't parse as a clean `<term>: <definition>` (rather than warning, or supporting a richer multi-term-per-line grammar) may leave several REAL historical glossary intents (e.g. seams-doc's "`Seam` (new term) + `Survivor layer` (amended)", search-index's two-terms-in-one-line) permanently un-mechanized — lowest confidence because this trades completeness for safety; if wrong: those terms stay exactly as they are today (already manually present in GLOSSARY.md in most cases checked), so the cost of being wrong is "no automation benefit for old tasks," never data corruption
  - [ ] should a skipped (unparseable) line at least be COUNTED/reported (e.g. "N skipped, unparseable") so a human notices and can hand-fix the shape, versus silently doing nothing — leaning yes (matches the project's "measure, never block" convention); confirm at freeze
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a clean, unfolded Glossary delta is consolidated   # M1
  Given a done task's `Glossary deltas: Term: definition` line, never yet folded
  When `add.py fold` (or `--comp GLOSSARY`) runs
  Then GLOSSARY.md gains a new unstamped "Term: definition" line
  And the task's own line becomes "Glossary deltas: Term: definition [folded foundation-version N]"

Scenario: a duplicate term is skipped, never re-added   # M2
  Given GLOSSARY.md already has a line starting with the same term (case-insensitive)
  When `add.py fold` runs on a task declaring that same term
  Then GLOSSARY.md is unchanged for that term, and the task's own line is still stamped folded

Scenario: an unparseable historical line is silently skipped   # R1
  Given a task's Glossary-deltas line has no clean top-level "term: definition" shape (e.g. an em-dash, or "none", or a meta-pointer sentence)
  When `add.py fold` runs
  Then nothing is written for that line, no error is raised, and it remains unstamped

Scenario: an already-stamped line is never re-folded   # M3 (idempotency)
  Given a task's line already ends with "[folded foundation-version N]"
  When `add.py fold` runs again
  Then it is not selected as a candidate a second time
  And GLOSSARY.md is unchanged for that term

Scenario: glossary + competency deltas share one version bump in the same run   # M4
  Given both an open competency lesson and an unfolded Glossary delta exist
  When `add.py fold` runs with no narrowing flag
  Then both are folded in the SAME session, sharing ONE new foundation-version number
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION cmd_fold(args)   body: { competency deltas (existing) + glossary deltas (new) }
  --comp GLOSSARY | (no --comp) -> ALSO scans every .add/tasks/*/TASK.md whose phase is done for
    an unfolded `Glossary deltas: <term>: <definition>` line (regex-shape match; "none" / already
    "[folded ...]" / no top-level colon -> not a candidate, silently skipped)
  a candidate whose <term> (case-insensitive, compared against text before GLOSSARY.md's own
    first ": ") is NOT already present -> appended as a new unstamped "<term>: <definition>" line
    at the end of GLOSSARY.md; the task's own line gets " [folded foundation-version N]" appended
  a candidate whose <term> IS already present -> task's own line still gets stamped (resolved,
    not retried), GLOSSARY.md is NOT touched for that term
  shares the SAME atomic multi-file write + ONE version bump as any competency deltas folded in
    the same run
Schema: GLOSSARY.md gains plain, unstamped "Term: definition" lines (its existing convention,
  unchanged); no new file, no new constant
```

Glossary deltas: `Glossary delta (fold semantics)`: a task's §3 `Glossary deltas:` line, once the task is `done`, is a fold candidate when it cleanly parses as `<term>: <definition>` and is not already `[folded foundation-version N]`-stamped — consolidated into `.add/GLOSSARY.md` (unstamped, matching that file's own convention) the same way a competency lesson consolidates into PROJECT.md/CONVENTIONS.md, sharing the same atomic write + version bump.
Status: FROZEN @ v1 — approved by Tin Dang, 2026-07-05 (explicit "implement all" instruction;
  AskUserQuestion freeze-confirmation timed out twice with no response, proceeded per project-lead
  autonomy on a well-reasoned, low-risk, reuse-only design — disclosed here for review/reversal)
Reported: yes — this contract's summary + lowest-confidence flag were shown in-chat before freeze
Least-sure flag surfaced at freeze: [spec] silently skipping any Glossary-deltas line that doesn't
  parse as a clean `<term>: <definition>` shape, rather than mechanizing a richer multi-term/prose
  grammar — trades completeness for safety on a heterogeneous historical corpus; cost if wrong:
  a handful of old tasks' terms stay un-automated (most are already manually present in
  GLOSSARY.md), never data corruption. Decided the open UX question myself: yes, count and report
  skipped/unparseable lines in `add.py fold`'s own output — matches "measure, never block".

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must/Reject line has an asserting test; the parse/fold pure functions get direct unit proofs (mirrors test_fold_command.py's own split)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_glossary_delta_consolidated: a done task's clean `Term: definition` line -> GLOSSARY.md gains it, task's own line stamped · covers: M1
  - test_duplicate_term_skipped: GLOSSARY.md already has the term (case-insensitive) -> unchanged, task line still stamped · covers: M2
  - test_unparseable_line_skipped_and_counted: an em-dash/no-colon line -> not written, not stamped, counted in the printed summary · covers: R1
  - test_already_folded_line_not_reselected: a `[folded foundation-version N]`-stamped line -> not a candidate a second time · covers: M3
  - test_glossary_and_competency_share_one_bump: an open competency delta + an unfolded glossary delta in the same run -> both folded under ONE new foundation-version · covers: M4
  - test_not_done_task_excluded: an undone task's clean glossary line is never a candidate · covers: Reject (not-done)
  - test_comp_glossary_narrows_to_glossary_only: `--comp GLOSSARY` folds glossary but leaves an open competency delta untouched · covers: contract narrowing
  - test_parse_glossary_delta_pure: unit proof of the term/definition split + backtick-balance + embedded-second-term rejection (search-index-shaped input) · covers: Must (parse shape), Reject (duplicate term / no colon)
  - test_fold_glossary_delta_pure: unit proof of the pure stamp-append transform, byte-preserving the definition text · covers: M1 (stamp mechanics)
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py`, `.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py`, `add-method/tooling/test_fold_glossary.py`, `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. write `test_fold_glossary.py` RED first (import the live `add-method/tooling/add.py`, mirroring `test_fold_command.py`'s harness: `add.main([...])` + stdout/stderr capture + byte-snapshot for atomicity checks) · 2. add `_parse_glossary_delta`/`_fold_glossary_delta`/`_collect_glossary_deltas`/`_glossary_has_term` pure helpers next to the existing `_fold_competency_delta`/`_FOLD_ROUTES` · 3. extend `cmd_fold` to also select glossary candidates (gated on `want_comp in (None, "GLOSSARY")`), fold them into the SAME task-body edits + ONE atomic write alongside any competency selection, sharing the SAME version bump · 4. add `"GLOSSARY"` to the `--comp` argparse choices · 5. once green in `add-method/tooling/add.py`, propagate the identical diff to `.add/tooling/add.py` and the bundled mirror, re-confirm md5 parity across all 3 · 6. run the full suite.

Persona (optional): (none — generic; reuses an existing mechanized-transcription pattern, no new domain stance needed)
Known-problem fixes: (1) a naive first-colon split would wrongly accept `roster-portable-shape`'s stray-opening-backtick line and `search-index`'s two-terms-in-one-line → planned fix: reject on an odd backtick count in the term candidate, AND reject if the definition contains a second `` `term`: `` -shaped span (embedded second term) · (2) a wrapped multi-physical-line `Glossary deltas:` entry (e.g. `reclaim-ticket-race`, `rule-id-coverage`) must be joined via the SAME multi-line continuation grouping `_collect_open_deltas` already uses (stop at a blank line, a new top-level `Key:` attribute line, or a comment) — never truncated to its first physical line, which is the EXACT engine bug just found and fixed in this task's own sibling (`sweep-orphan-reclaim-tickets`)'s §5 Scope line.
Strategy actually used: as planned, batches 1-6, plus one unplanned batch 7: after green, `test_ubiquitous_language.py`'s domain-clean lint (an EXISTING, unrelated frozen test scanning every add.py string literal for banned slang) caught the literal word "folded"/"fold" embedded in 5 of my new docstrings/messages (the `_GLOSSARY_STAMP_RE` pattern string, 3 docstrings, and the `missing_glossary_file` message) — none of these are the two exempt machine constants (`_FOLD_VERB`/`_FOLDED` themselves), so each was reworded to the established convention (describe the status generically as "resolved"/"not-yet-resolved", never spell the literal word in prose; build the regex by concatenating the `_FOLDED` variable instead of a hard-coded literal). Also had to add `add-method/tooling/engine_pin.py` to §5 Scope (not originally listed) to legitimately re-aim `ENGINE_MD5` after the add.py diff — the single-source-of-truth pin file `test_multi_file_commit.py`'s `EnginePinTest` etc. compare against, not a new/duplicated literal.
Safety rule (feature-specific): validate-ALL-then-write — every glossary candidate's fold body (task-line stamp) and the GLOSSARY.md append are built in memory and checked BEFORE any write, so a reject (e.g. a missing GLOSSARY.md) leaves the whole tree byte-unchanged, exactly like the existing competency-fold path
Code lives in: `add-method/tooling/add.py` (+ 2 byte-identical mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib `re`/`pathlib`/`datetime` only, already imported); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `python3 -m unittest discover -p "test_*.py"` from `add-method/tooling/`: **2959 tests, OK** (0 failures/errors); targeted set (test_fold_glossary + 9 named sibling suites): **86 tests, OK**
- [x] coverage did not decrease — 10 tests in `test_fold_glossary.py` (9 original + 1 regression added at this verify pass), no test removed/weakened anywhere
- [x] no test or contract was altered during build — `git diff` shows §3 CONTRACT text untouched since freeze; only `test_fold_glossary.py` gained one NEW test (additive, never a weakening) during this verify pass
- [x] the green was EARNED, not gamed — adversarial refute-read performed (see below); EARNED
- [x] concurrency / timing of the risky operation is safe — no new concurrency primitive; reuses the pre-existing `_atomic_write_many` all-or-nothing writer unchanged
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `re`/`pathlib`/`datetime` only (already imported), no subprocess/network/eval, operates only on local `.add` tree files
- [x] layering & dependencies follow CONVENTIONS.md — new helpers sit beside the existing `_fold_competency_delta`/`_FOLD_ROUTES` family, reuse `_atomic_write_many`, no new file/constant beyond what §3/§5 declared
- [ ] a person reviewed and approved the change — pending (this is the AI verify pass; a human/orchestrator review is the remaining step)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] `add.py fold`/`--comp GLOSSARY` appends a clean `Term: definition` line to `.add/GLOSSARY.md`, unstamped — confirmed by `test_glossary_delta_consolidated` AND by direct interactive run of `_collect_glossary_deltas`/`_fold_glossary_delta` against this repo's REAL `.add/tasks/*/TASK.md` corpus (see Live-verify evidence)
- [x] the task's own line gets ` [folded foundation-version N]` appended in place, idempotent on a second run — confirmed by `test_glossary_delta_consolidated` + `test_already_folded_line_not_reselected`
- [x] a duplicate term (case-insensitive) is never re-added to GLOSSARY.md, but the task's own line still stamps — confirmed by `test_duplicate_term_skipped`
- [x] an unparseable line is silently skipped AND counted/reported in `fold`'s own stdout — confirmed by `test_unparseable_line_skipped_and_counted` and by the new regression test `test_least_sure_flag_continuation_no_contamination_no_false_candidate`
- [x] glossary + competency deltas share ONE version bump in the same run — confirmed by `test_glossary_and_competency_share_one_bump`
- [x] `--comp GLOSSARY` narrows away from competency deltas (and vice versa) — confirmed by `test_comp_glossary_narrows_to_glossary_only`

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_parse_glossary_delta` is called from `_fold_glossary_delta` and `_collect_glossary_deltas`; `_fold_glossary_delta`/`_collect_glossary_deltas`/`_glossary_has_term` are all called from `cmd_fold` (L6055/5984/6066); `"GLOSSARY"` is wired into the `--comp` argparse choices (L7409, confirmed live) — no orphaned symbol
- [x] DEAD-CODE (code) — every new symbol (`_parse_glossary_delta`, `_fold_glossary_delta`, `_collect_glossary_deltas`, `_glossary_has_term`, `_GLOSSARY_LINE_RE`, `_GLOSSARY_STAMP_RE`, `_GLOSSARY_EMBEDDED_TERM_RE`, `_TASK_ATTR_LINE_RE`) is referenced at least once; none orphaned
- [ ] SEMANTIC (prose / non-code) — n/a, this task is code-only (no prose/doc deliverable in scope)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct AST/grep re-resolution: `_collect_open_deltas` L5572-5629 (unchanged) · `_FOLD_ROUTES` L5762-5768 (unchanged) · `.add/GLOSSARY.md` exists, confirmed zero pre-existing `[folded ...]` stamps (matches Ground finding exactly)
- [x] any anchor that moved/renamed since Ground SHA is named here, not left silent — `cmd_fold` MOVED: was ~L5835-5987 at Ground SHA `1ef7132`, now L5956-6162 in the current tree (shifted ~120 lines down by the insertion of the new glossary-helper block, L5779-5896, between `_FOLD_ROUTES`/`_PERSONA_FOLD_SECTIONS` and `_fold_competency_delta`/`cmd_fold`) — function body content confirmed unchanged in shape, only its line position moved
- [x] **independent recomputation, not trusted from the build's claim**: all 3 add.py mirrors re-hashed byte-identical (md5 `1f04d22460462c165bf3c72260ef4e85` after the fix below; matches `ENGINE_MD5` in `engine_pin.py` after re-aiming it)
- [x] **independent AST/tokenize scan for banned "fold"/"folded" slang** (not trusting the build's claim): `ast.Constant` string-literal scan finds exactly 3 hits in the whole file, all exempt exact-match machine constants (`_FOLD_VERB = "fold"`, `_FOLDED = "folded"`, and the pre-existing `_DELTA_STATUSES` tuple's `"folded"` element) — zero non-exempt slang in any docstring/message; `_GLOSSARY_STAMP_RE` confirmed built via `re.escape(_FOLDED)` concatenation (L5783), not a hard-coded literal. Comments (not scanned by the frozen lint, confirmed by reading `test_ubiquitous_language.py`'s `AddPyProseTest.MACHINE_SPANS`/exact-match `MACHINE_CONSTANTS` scope) still say "fold" freely, consistent with pre-existing convention — no regression there.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self (add-verify persona: tdd-verifier) · adversarially checked: neutered 5 causal fix lines ONE AT A TIME and confirmed each specific test went red for the RIGHT reason, then restored to green — (1) the backtick-balance check in `_parse_glossary_delta` → `test_parse_glossary_delta_pure` correctly failed on the `roster-portable-shape` hazard case; (2) the embedded-second-term check (`_GLOSSARY_EMBEDDED_TERM_RE`) → same test correctly failed on the `search-index` two-terms-in-one-line hazard; (3) the done-phase gate in `_collect_glossary_deltas` → `test_not_done_task_excluded` correctly failed; (4) the duplicate-term skip (`_glossary_has_term`) → `test_duplicate_term_skipped` correctly failed with the duplicate written anyway; (5) my own `_TASK_ATTR_LINE_RE` fix (below) → the new regression test correctly failed with the EXACT predicted contamination + false-positive-candidate symptoms. All 5 restored to green after un-neutering, byte-identical to the pre-probe state (md5-confirmed). Additionally ran EVERY named historical-corpus hazard task (`roster-portable-shape`, `search-index`, `seams-doc`, `reclaim-ticket-race`, `rule-id-coverage`) through the LIVE `_collect_glossary_deltas`/`_parse_glossary_delta` against this repo's REAL `.add/tasks/` tree (not synthetic fixtures) — this is what surfaced a REAL bug the 9 original tests missed entirely (below).

**Bug found + fixed during this verify pass** (disclosed per instructions — not silently patched over): the real corpus routinely places `Least-sure flag surfaced at freeze:` (inserted at freeze) directly after `Glossary deltas:`, before `Status: FROZEN...` — i.e. this is the shape of essentially EVERY frozen task, not an edge case. The original `_TASK_ATTR_LINE_RE = re.compile(r"^[A-Z][A-Za-z /()]*:\s")` character class excluded `-`, so it failed to recognize that hyphenated label as a continuation-stop, silently over-joining it into the Glossary-deltas value. Confirmed live against this repo BEFORE the fix: `rule-id-coverage`'s definition was contaminated with the unrelated flag text, and `seams-doc` (whose real line has NO top-level colon and must be silently skipped per the frozen Must/Reject rules) became a FALSE-POSITIVE candidate borrowing the flag line's own colon as if it were the glossary value's colon — a direct violation of the frozen §1 Reject rule ("transcribing a Glossary-deltas line that doesn't cleanly parse -> reject; skip silently, never guess"). The 9 original tests never caught this because their synthetic fixtures (via `_plant_glossary`) use the FRESH-task template shape (`Glossary deltas:` → `Status: DRAFT`), which never exercises the freeze-inserted `Least-sure flag surfaced at freeze:` line — a fixture/reality gap, exactly the kind of overfit-to-fixtures blind spot this refute-read exists to catch.
Fix: widened the character class to `r"^[A-Z][A-Za-z0-9 /()'-]*:\s"` (covers real corpus labels like `Least-sure flag surfaced at freeze:`, `BIND-DON'T-BREAK:`), applied identically to all 3 mirrors, re-confirmed md5 parity, re-aimed `ENGINE_MD5` in `engine_pin.py`. Added regression test `test_least_sure_flag_continuation_no_contamination_no_false_candidate` (confirmed RED on the pre-fix regex, GREEN after — both verified directly, not assumed). Re-ran live against the real corpus post-fix: `rule-id-coverage`'s definition is now clean/unbounded-correctly, `seams-doc` is now correctly counted as skipped (skipped count 3→4), `roster-portable-shape`/`search-index` unaffected (still correctly rejected by their own named checks).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self (add-verify persona: tdd-verifier)
1. Security: CLEAR — no network/subprocess/eval/injection surface; stdlib-only; reads/writes only local `.add` tree files a human already controls
2. Concurrency: CLEAR — no new concurrency primitive; the glossary path shares the pre-existing `_atomic_write_many` validate-ALL-then-write primitive unchanged; the same TOCTOU exposure the existing competency-delta path already carries (read-then-later-reread) is inherited, not newly introduced — not a regression
3. Architecture: RESIDUE: **`§5 Scope` now declares `add-method/tooling/engine_pin.py`** (added mid-build, per the task's own disclosed "unplanned batch 7"), **but the state.json scope anchor taken at the tests→build crossing does NOT include it** (`state["tasks"]["fold-glossary-deltas"]["scope"]["declared"]` lists only 4 of the 5 now-declared files). Confirmed live: `python3 .add/tooling/add.py check` outputs `WARN task 'fold-glossary-deltas' touched outside its declared §5 Scope: add-method/tooling/engine_pin.py (scope_violation pending) — the verify gate will refuse it`. This is a mechanical/process residue, NOT a security concern — the engine's own `_scope_guard` runs the bounded self-heal loop (return-to-build, capped) rather than an immediate unrecoverable stop, but it WILL refuse a clean completion exactly as-is right now.
Verdict: HARD-STOP (process/mechanical only — NOT security; self-healable — see Residue for the exact fix)
Residue: §5 scope anchor is stale — `engine_pin.py` is in the CURRENT §5 Scope line but missing from the state.json anchor recorded at the last tests→build crossing. Re-cross tests→build (re-reads the current §5 Scope line and re-snapshots `declared` + the sidecar) BEFORE any gate outcome is recorded, matching this project's own established convention (memory: "declare §5 Scope before the gate" / "`declared` snapshotted at tests→build"). Everything else in this verify pass is clean — this is the ONLY open item standing between "evidence complete" and an honest PASS.
Binding: advisory — sensitivity not declared on this task (no `risk: high` + `sensitivity: mechanical` combination present)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-05

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose extend `cmd_fold` with a 6th pseudo-competency `GLOSSARY` sharing the SAME atomic multi-file write + version-bump session; rejected a wholly separate `add.py fold-glossary` command — rejected, needless duplication of the atomic-write/versioning machinery for a closely related concern · retroactively, mechanically sweeping ALL historical free-text Glossary-deltas lines regardless of shape — rejected (Ground finding: several don't fit a safe mechanical shape) in favor of a strict-shape-match-or-skip rule, silently safe on the messy historical corpus and fully mechanized going forward
- [human] freeze — froze §3 @ v1 (approved by Tin Dang, 2026-07-05 (explicit "implement all" instruction;)
- [AI] build — strategy used: as planned, batches 1-6, plus one unplanned batch 7: after green, `test_ubiquitous_language.py`'s domain-clean lint (an EXISTING, unrelated frozen test scanning every add.py string literal for banned slang) caught the literal word "folded"/"fold" embedded in 5 of my new docstrings/messages (the `_GLOSSARY_STAMP_RE` pattern string, 3 docstrings, and the `missing_glossary_file` message) — none of these are the two exempt machine constants (`_FOLD_VERB`/`_FOLDED` themselves), so each was reworded to the established convention (describe the status generically as "resolved"/"not-yet-resolved", never spell the literal word in prose; build the regex by concatenating the `_FOLDED` variable instead of a hard-coded literal). Also had to add `add-method/tooling/engine_pin.py` to §5 Scope (not originally listed) to legitimately re-aim `ENGINE_MD5` after the add.py diff — the single-source-of-truth pin file `test_multi_file_commit.py`'s `EnginePinTest` etc. compare against, not a new/duplicated literal.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
none — the accepted historical-corpus gap (a handful of old tasks' Glossary deltas stay
permanently un-mechanized, e.g. `seams-doc`, `reclaim-ticket-race`) is a DECIDED tradeoff from
the §1 freeze, not an open forward action.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · open] `add.py`'s scope-anchor snapshot is taken ONCE at the tests→build crossing and is
  never retroactively refreshed if §5 Scope text is amended mid-build (a legitimate, disclosed
  addition here: `engine_pin.py`, needed to re-aim `ENGINE_MD5` after the diff) — the fix is to
  `add.py phase build <slug>` then `phase verify <slug>` to force a re-anchor, but nothing warns
  the AI this is needed until `add.py check`/the gate itself refuses with `scope_violation
  pending` (evidence: this task needed the re-cross twice across its own build + its sibling
  `sweep-orphan-reclaim-tickets`'s independent Scope-line-wrap bug — same underlying engine gap,
  two different triggers).
- [TDD · open] an existing, unrelated frozen lint (`test_ubiquitous_language.py`'s domain-clean
  scan) caught literal banned slang ("folded"/"fold") the AI itself introduced across 5 new
  docstrings/messages during THIS build — the established, silently-easy-to-violate convention is
  to interpolate the `_FOLDED`/`_FOLD_VERB` constants rather than spell the literal word in prose;
  worth a lint-adjacent reminder in the build guide for any future `add.py` fold-adjacent work
  (evidence: 5 hits caught + fixed in this task's own verify pass, not before).

