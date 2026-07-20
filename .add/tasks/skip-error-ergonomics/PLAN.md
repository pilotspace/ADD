# TASK: skip_not_allowed names the bad token, the allowed set, and the fix; pre-init error hands the exact init command

slug: skip-error-ergonomics · created: 2026-07-10 · stage: mvp
milestone: risk-proportional-ceremony
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:`_task_skip_set(hdr)` (~1501 — returns the BARE code "skip_not_allowed" on any malformed `skips:` element; the raw declaration and the bad tokens are computed right there and discarded) · `cmd_advance` die site (~1336, `_die(skip_err)` verbatim) · `_require_root`/no-project error ("no .add/ project found. Run `add.py init` first." — names the verb, not its flags)
Context (working folder): LOOP-2 re-measure transcripts (loop2-lever/rep0,rep1, 2026-07-10, pinned sonnet): skip_not_allowed fired 4-5×/rep as agents trial-and-errored a `skips:` header line (rep0 tried to skip `specify` — not skippable), plus greps + `check` + --help to diagnose; the pre-init `status` error triggered an `init --help` read in both reps
Honors (patterns / conventions): error-code prefix convention — keep the `skip_not_allowed` prefix so existing greps/tests keep matching; message-layer-only (enforcement untouched, the LOOP-2 pattern) · banned-slang string guard
Seams consulted: none new (skips grammar read from `_SKIPS_LINE_RE`/`_task_skip_set` docstrings in place)
Anchors the contract cites: `_task_skip_set` · `cmd_advance` skip die · the no-project error in `_require_root`
Issues/Risks (→ feed §1): (1) `_task_skip_set` is PURE and also feeds the read-only status path which DEGRADES on error — the enriched string must ride the same return channel without breaking the degrade. (2) tests may pin the bare code string — red-first enumeration. (3) `_SKIPPABLE_PHASES` membership listed in the message must be computed, not hardcoded, so a future skippable phase can't drift the text.
Related intent: milestone risk-proportional-ceremony LOOP-3 — the re-measure's dominant surviving repair loop; goal: mean add.py calls ≤12
Ground SHA: 1327e3b — line refs "as of" this commit

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: skip-error ergonomics — the two remaining bare orientation errors teach their own fix
Framings weighed: enrich-the-error-strings (chosen — message layer, LOOP-2 pattern, zero enforcement risk) · make skips: forgiving/partially-honored (rejected: fail-closed on garbled input is a deliberate frozen philosophy) · auto-strip a bad skips: line (rejected: silent mutation of a task header)
Must:
<must>
  - M1 a malformed `skips:` declaration dies with: the RAW declared value · the specific bad token(s) · the computed allowed set (from _SKIPPABLE_PHASES, not hardcoded) · the fix (correct or remove the `skips:` line, then re-run add.py advance) — keeping the `skip_not_allowed` prefix
  - M2 the no-project error names the exact command with flags: `add.py init --name "<project>" --stage <prototype|poc|mvp|production>`
  - M3 read-only status degrade path unchanged (empty-set reading, never raises); enforcement (fail-closed whole-declaration discard) byte-identical
  - M4 3-tree parity + ENGINE_MD5 re-pin + full suite green
</must>
Reject:
<reject>
  - partially honoring a garbled skips: declaration -> forbidden (fail-closed stands)
  - changing WHICH phases are skippable or the lane-eligibility rules -> out of scope
</reject>
After:
<after>
  - an agent with a bad skips: line repairs it from the error text alone — zero greps, zero --help, zero trial-and-error advances
  - a fresh-directory agent reaches a correct `init` from the no-project error alone
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the bare-code string is pinned by existing tests — lowest confidence because fast-lane-skips shipped with its own suite; if wrong: nothing (red-first enumeration catches it either way; prefix preserved so assertIn("skip_not_allowed") survives)
  - [x] _task_skip_set can name bad tokens without a signature change — yes: return the enriched string in the existing `str | None` error slot
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: malformed skips names its repair   # M1
  Given a task header declaring `skips: specify,scenarios` (specify not skippable)
  When advance reaches a skippable crossing
  Then the error names `specify` as the bad token, lists the allowed set, and says fix-or-remove the skips: line
  And the exit code and fail-closed discard are unchanged

Scenario: valid skips unaffected   # M1 guard
  Given a lane-eligible task declaring `skips: scenarios` with a rationale
  When advance crosses
  Then the skip fires exactly as today with no new output

Scenario: no-project error hands the init command   # M2
  Given an empty directory
  When any project verb runs (e.g. status)
  Then the error contains `add.py init --name` and the --stage choices

Scenario: status degrade path silent   # M3
  Given a task with a malformed skips: line
  When plain status renders
  Then it degrades to the empty-set reading exactly as today (no raise, no new text)
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_task_skip_set(hdr) -> tuple[frozenset, str | None]        # signature unchanged
  malformed element(s) -> (frozenset(), "skip_not_allowed: `skips: <raw>` — <bad,tokens> not
      skippable; only <computed _SKIPPABLE_PHASES> may be skipped. Correct or remove the
      `skips:` line in the TASK.md header, then re-run add.py advance")
  no line / all-valid -> byte-identical to today

_require_root() no-project death
  -> 'no .add/ project found — run: add.py init --name "<project>" --stage
     <prototype|poc|mvp|production>' (single line, flags included)

status read path: consumes the same (frozenset(), err) tuple, still degrades silently
```

Glossary deltas: none
Least-sure flag surfaced at freeze: [spec] enriching the returned error STRING could break a caller that switches on exact equality (`== "skip_not_allowed"`) rather than prefix — census + red-first enumeration covers it; cost if wrong: one loud test failure, fixed in TESTS phase.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §2 scenario = 1 test
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_malformed_skips_names_repair: header `skips: specify,scenarios` / advance / assert "specify" + "scenarios, observe" (allowed set) + "remove" guidance + skip_not_allowed prefix + non-zero exit · covers: M1
  - test_valid_skip_unaffected: eligible task, skips: scenarios + rationale / advance / assert skip recorded as today · covers: M1 guard
  - test_no_project_error_hands_init: empty dir, run status / assert "add.py init --name" + "--stage" choices in stderr · covers: M2
  - test_status_degrades_silently: malformed skips / status / assert exit 0 + no skip_not_allowed text · covers: M3
  - (existing) fast-lane-skips suite pinned strings — red-first enumeration; update only equality-pinned asserts (prefix survives assertIn)
</test_plan>

Tests live in: `add-method/tooling/test_skip_error_ergonomics.py` (new, sibling convention) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/add_engine/io_state.py` `.add/tooling/add_engine/io_state.py` `add-method/src/add_method/_bundled/tooling/add_engine/io_state.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/test_skip_error_ergonomics.py` `add-method/tooling/test_fast_lane_skips.py`
Strategy (ordered batches): 1. red suite (new file + enumerate any equality-pinned asserts in test_fast_lane_skips.py). 2. enrich _task_skip_set's error string (compute bad tokens + allowed set in place). 3. enrich the no-project error. 4. twins sync + re-pin + full suite to file.
Approach (domain strategy): message-layer repair, third of the LOOP series — the engine hands the exact fix at the moment of failure; fail-closed philosophy untouched.
Data strategy: none — same return channels, no state shape.
Pattern: extends the exact-command surface to the last two bare orientation errors the re-measure surfaced.
Optimization stance: token-cost (turn-count) — kill the 4-5 skip trial-and-error calls + the pre-init --help; budget = LOOP criterion mean ≤12 calls. ⚠ least-trusted facet: equality-pinned assert census (flagged at freeze). correctness-first otherwise.

Persona (required): methodology-engine-dev
Spawn isolation (default): none — INLINE build by the orchestrator (standing speed directive)
Known-problem fixes: banned-slang string guard · `| tail` exit masking · prepare_bundle deletes bundled engine_pin (git-restore + re-pin) · __pycache__ parity flake · SEAMS line-pin drift (re-pin after) · unittest dotted-path hyphen trap (cd into tooling/)
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `add-method/tooling/add.py` (canonical; twins synced at build end)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass   (full suite Ran 3354 — OK; new suite 4/4; fast-lane 49 OK)
- [x] coverage did not decrease   (4 new tests; the 2 upgraded asserts are STRONGER — they now also require the bad-token name)
- [x] no test or contract was altered during build   (suite red-first in TESTS; §3 untouched; the 2 equality-pin updates were §4-named, done at the red stage)
- [x] the green was EARNED — refute-read below
- [x] concurrency safe   (advisor lens 2 — pure strings)
- [x] no secrets/injection/deps   (advisor lens 1)
- [x] layering per CONVENTIONS.md   (advisor lens 3)
- [ ] a person reviewed and approved the change   (human backstop — spot-audit welcome; auto-gate below)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] live smoke (smoke-see 2026-07-10): advance → ``skip_not_allowed: `skips: specify,scenarios` — 'specify' cannot be skipped; only observe, scenarios may be skipped...Correct or remove the `skips:` line...then re-run add.py advance``; fresh-dir status → `no .add/ project found — run: add.py init --name "<project>" --stage <prototype|poc|mvp|production>`
- [x] 3 trees byte-identical (add.py `2e85cbf4…` ×3 · io_state.py ×3) + ENGINE_MD5 AND ENGINE_PKG_MD5 re-pinned (pkg `5f60c0b2…` — io_state.py is package code)
- [x] full suite Ran 3354 in 261.2s — OK (/tmp/see-fullsuite2.txt; first run caught a REAL quoting bug my replace introduced at the 3 no_project sites — fixed, re-run clean)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — no new symbol; enriched strings ride the existing return/err channels (verified by the green M1/M2 tests + the 4 unified no_project sites)
- [x] DEAD-CODE (code) — none; both branches test-exercised
- [x] SEMANTIC (prose / non-code) — new strings read in full: no banned slang; allowed set COMPUTED from _SKIPPABLE_PHASES (drift-proof); `no .add/ project found` lead preserved for any external grep

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] anchors re-resolved: `_task_skip_set` (add.py ~1501) · the no-project death is `add_engine/io_state.py:_require_root` (NOT an add.py `_require_root` as §0 first guessed — disclosed here, §5 scope amended PRE-crossing to add the io_state twins) + 3 `no_project:` variants in add.py (~7377/7575/7635) unified to the same command text
- [x] `_declared_scope` did not move this time (edits were below it) — SEAMS pin x14 still valid (seams test green in targeted run)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self (orchestrator, inline build) · adversarially checked: M1 test asserts the allowed set via computed _SKIPPABLE_PHASES membership (not a hardcoded string that could drift); fail-closed discard still asserted non-zero + empty set; M3 proves status NEVER surfaces the enriched error (degrade intact); equality-pinned asserts in test_fast_lane_skips upgraded to prefix+bad-token asserts (stronger, not weaker — they now ALSO catch a missing token name)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self (orchestrator)
1. Security: CLEAR — string-content changes only; no new parsing, writes, or exits; fail-closed philosophy untouched
2. Concurrency: CLEAR — pure function + die-path strings; no state access changed
3. Architecture: CLEAR — same return channels; allowed-set computed not hardcoded; no_project variants UNIFIED (less drift, not more)
Verdict: PASS
Residue: none
Binding: advisory — mechanical (stdout/stderr messages only)

### GATE RECORD
Reported: yes — smoke stdout + suite lines rendered to the user before recording
Outcome: PASS
Reviewed by: auto-gate (autonomy: auto — inline build, refute-read EARNED, advisor 3-lens CLEAR/PASS, residue none, sensitivity mechanical; the first full-suite run caught + fixed a real quoting regression before this gate) · date: 2026-07-10

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose enrich-the-error-strings; rejected make skips: forgiving/partially-honored (rejected: fail-closed on garbled input is a deliberate frozen philosophy) · auto-strip a bad skips: line (rejected: silent mutation of a task header)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: message-layer repair, third of the LOOP series — the engine hands the exact fix at the moment of failure; fail-closed philosophy untouched.
- [AI] build — data strategy: none — same return channels, no state shape.
- [AI] build — pattern: extends the exact-command surface to the last two bare orientation errors the re-measure surfaced.
- [AI] build — optimization stance: token-cost (turn-count) — kill the 4-5 skip trial-and-error calls + the pre-init --help; budget = LOOP criterion mean ≤12 calls. ⚠ least-trusted facet: equality-pinned assert census (flagged at freeze). correctness-first otherwise.
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by auto-gate (autonomy: auto — inline build, refute-read EARNED, advisor 3-lens CLEAR/PASS, residue none, sensitivity mechanical; the first full-suite run caught + fixed a real quoting regression before this gate))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] a blind str.replace on source can nest quotes into a VALID-parsing comparison expression that only fails at runtime — the full-suite gate caught it where import/parse checks could not (evidence: test_graduation_report NameError at add.py:7377, first suite run)
- [ADD · open] error messages are part of the method's cost surface: three message-layer tasks cut −24% turns/−34% cost without touching one enforcement path (evidence: LOOP-2 re-measure n=3)
