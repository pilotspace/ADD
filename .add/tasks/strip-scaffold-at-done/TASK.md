# TASK: At phase done, strip the live-phase instruction comments from TASK.md

slug: strip-scaffold-at-done · created: 2026-06-30 · stage: mvp
milestone: drift-guard
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_gate` (the `completing` branch — sets `phase="done"`, `_sync_task_marker(... "done")`, then `_stamp_gate_record` + `_stamp_adr_record`) — AFTER those stampers, STRIP the live-phase `` instruction comments from the task's TASK.md.
  - `add-method/tooling/add.py` — new `_strip_live_scaffold(text) -> str` helper: remove `` spans (DOTALL), trim trailing whitespace a removal leaves on a line, collapse 3+ blank lines to one. Content-safe (only comments), idempotent.
  - `add-method/tooling/add.py:_stamp_gate_record` / `:_stamp_adr_record` — anchor on `### GATE RECORD` / `Outcome:` / section headings (NOT on comments), so the strip is safe to run after them.
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` — re-pinned ×2 (canonical + dogfood).
  - `add-method/tooling/test_strip_scaffold_at_done.py` — NEW test (via the `add.main` harness: gate a task PASS, assert its TASK.md lost `` but kept authored content).
Context (working folder): a fresh TASK.md carries 11 `` instruction blocks (header autonomy/risk, the phase marker tail, each section's `EXIT:`/token-rule hints). They guide the LIVE phase; once `done` they are dead weight (PR40 audit). The gate verdict is mirrored into §6/§7 by the two stampers FIRST; the strip is the last step so it never races them.
Honors (patterns / conventions): atomic write (`_atomic_write`); degrade-safe (unreadable TASK.md → skip, never block the gate); state-first (strip only mirrors the file, never touches state.json); engine NO-EXEC; idempotent (a re-gate on an already-stripped file is a no-op).
Anchors the contract cites: cmd_gate completing branch · `_strip_live_scaffold` helper · `_atomic_write` · engine_pin.ENGINE_MD5
Issues/Risks (→ feed §1):
  - **ordering** — the strip MUST run after `_stamp_gate_record` + `_stamp_adr_record` (they edit §6/§7 and could be confused by mid-edit state); placing it last in the completing branch avoids any race.
  - **content-safety** — only `` spans may be removed; authored text (incl. code fences, the frozen §3, gate record) stays byte-exact. Clean only the trailing whitespace + blank-line runs the removal itself introduces.
  - **one-way** — once `done`, the comments are gone (Tin confirmed "yes, strip at done"); the template still ships them for live tasks, so new tasks are unaffected. Not reversible by the engine — acceptable.
  - **sibling tests** — some guards may assert a comment token in a TASK.md fixture; a fixture that is `done` would now lack it. Resolve by pointing such a guard at a live (non-done) task, never by weakening it.
Related intent: PROJECT.md drift-guard rationale ("a closed TASK.md stays true to the code"; lean) · GLOSSARY "task" · originating PR40 (api-proxy) audit — "strip the repeated `` instruction blocks from completed tasks (scaffolding for the live phase, dead weight at done)"; milestone drift-guard M3, task 2 (sibling to ground-anchor-sha).
Ground SHA: 1dbbca9

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: at `phase: done`, the engine strips the live-phase `` instruction comments from a task's TASK.md
Framings weighed: strip in cmd_gate's completing branch, after the §6/§7 stampers (chosen — single completing chokepoint, no race) · strip in _sync_task_marker (rejected — it runs for every phase, not just done) · a separate `add.py tidy` command (rejected — manual, drifts; the audit wants it automatic at close)
Must:
<must>
  - M1: a COMPLETING gate (`add.py gate PASS` / `RISK-ACCEPTED`, which sets `phase: done`) strips the `` instruction comments from that task's TASK.md.
  - M2: the strip is CONTENT-SAFE — every non-comment byte is preserved, and any fenced code block (```…```, e.g. the frozen §3) is left entirely untouched (a `` inside a fence survives). Only the trailing whitespace + 3+ blank-line runs that a removal itself introduces are cleaned.
  - M3: the strip runs AFTER `_stamp_gate_record` + `_stamp_adr_record`, via `_atomic_write`, is degrade-safe (unreadable TASK.md → skip, the gate never blocks) and idempotent (re-running on a stripped file is a no-op).
  - M4: invariants — every `add.py` copy byte-identical == the RE-PINNED `engine_pin.ENGINE_MD5`; the phases lean pool is UNTOUCHED; full suite green.
  - M5 (v2 — change request): the tamper guard's §3 fingerprint (`_tripwire_snapshot` + `_tripwire_divergence`) is computed on the COMMENT-NORMALIZED §3 (`_strip_live_scaffold(raw3)`) on BOTH sides — so the at-done strip is invisible to it and a reopen→re-gate of a stripped task is CLEAN (no false `contract_tampered`). A real fenced-shape edit still trips the guard.
</must>
Reject:
<reject>
  - a NON-completing gate (HARD-STOP — task not done) strips the file -> "strip_on_noncompleting"
  - the strip removes/alters authored (non-comment) text, or edits inside a fenced code block -> "strip_corrupts_content"
  - the strip is non-atomic, or a write fault blocks/aborts the gate -> "strip_not_safe"
  - the build edits add.py without re-pinning ENGINE_MD5 across all copies -> "engine_pin_drift"
  - a reopened, re-gated task is flagged contract_tampered solely because its §3 comment was stripped -> "strip_trips_tamper"
</reject>
After:
<after>
  - After a completing gate, the task's TASK.md has no `` instruction comments, all authored content (incl. fenced blocks) is byte-intact; a HARD-STOP leaves them; add.py re-pinned ×3; phases pool unchanged; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Fenced-block safety — lowest confidence: that splitting on```…``` and stripping comments only OUTSIDE fences keeps the frozen §3 (and any fenced sample) byte-exact. If wrong: a strip could mutate frozen contract text = the cardinal sin. Mitigate: `re.split(r"(```.*?```)", text, DOTALL)` → strip only the non-fence segments; a dedicated scenario asserts a `` inside a fence survives.
  - [ ] Running the strip AFTER both stampers is safe — confirmed: `_stamp_gate_record`/`_stamp_adr_record` anchor on `### GATE RECORD`/`Outcome:`/section headings, never on ``, so removing comments after they run cannot disturb them.
  - [ ] Only PASS/RISK-ACCEPTED set `phase: done` (`completing`) — confirmed: cmd_gate's `completing` flag; HARD-STOP leaves the phase, so the strip never fires on it.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a completing gate strips the instruction comments   # M1
  Given a task whose TASK.md carries `<!-- … -->` instruction comments
  When I run `add.py gate PASS <slug>`
  Then the task's TASK.md has no `<!-- … -->` comment
  And its authored content (headings, §1 rules) is intact

Scenario: a fenced code block is left untouched   # M2, R:strip_corrupts_content
  Given a task whose TASK.md has a ```fence``` containing a `<!-- keep -->` and a `<!-- strip -->` outside it
  When I run `add.py gate PASS <slug>`
  Then the `<!-- keep -->` inside the fence survives byte-exact
  And the `<!-- strip -->` outside the fence is gone

Scenario: a HARD-STOP gate does not strip   # R:strip_on_noncompleting
  Given a task whose TASK.md carries `<!-- … -->` comments
  When I run `add.py gate HARD-STOP <slug>`
  Then the comments remain (the task is not done)

Scenario: stripping is idempotent and degrade-safe   # M3
  Given a task already gated PASS (comments stripped)
  When the strip logic runs again on the stripped text
  Then the text is unchanged (no error, no double-clean)

Scenario: a reopened, re-gated task is not falsely tampered   # M5, R:strip_trips_tamper
  Given a task gated PASS once (its §3 instruction comment stripped), then reopened to verify
  When I run `add.py gate PASS <slug>` again
  Then the gate completes (no contract_tampered) and the task is done again

Scenario: engine parity holds   # M4, R:engine_pin_drift
  Given the build is complete
  Then every add.py copy is byte-identical and equals the re-pinned ENGINE_MD5
  And the phases lean pool is unchanged
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Strip live scaffold at done — frozen shape @ v1   (engine tidies a closed TASK.md; NO-EXEC)

add.py _strip_live_scaffold(text) -> str:
    segs = re.split(r"(```.*?```)", text, flags=re.DOTALL)   # alternating non-fence / fence
    for even-index (NON-fence) segments only:
        drop `<!--.*?-->` spans (DOTALL);
        rstrip trailing whitespace each removal leaves on a line;
        collapse 3+ consecutive newlines to 2 (one blank line).
    fence (odd-index) segments are passed through BYTE-EXACT. rejoin + return.
  -> idempotent (no comment left → returns input unchanged); content-safe.

add.py cmd_gate — in the `completing` branch, as the LAST step (after _stamp_gate_record +
_stamp_adr_record):
    try: t = TASK.md.read_text(); s = _strip_live_scaffold(t)
         if s != t: _atomic_write(TASK.md, s)
    except OSError: pass            # degrade-safe — the gate is already recorded in state
  -> only a completing gate reaches here; HARD-STOP never does. The strip mirrors the file only;
     state.json is already saved, so a write fault never loses the verdict.

add.py tamper guard (v2 — change request) — _tripwire_snapshot + _tripwire_divergence compute the
§3 fingerprint as _md5_text(_strip_live_scaffold(raw3)) — COMMENT-NORMALIZED, on BOTH sides:
  - snapshot (tests→build, comment present) and divergence (live, comment stripped) normalize to the
    SAME value (idempotent), so the at-done strip NEVER reads as contract_tampered;
  - a real fenced-shape edit still changes the fingerprint -> still HARD-STOP-class. The §3 instruction
    comment is template scaffolding, never frozen-contract content.

Invariants: add.py ×3 byte-identical == re-pinned engine_pin.ENGINE_MD5; phases lean pool untouched.
```

Least-sure flag surfaced at freeze: [contract/test] tamper-guard normalization (v2) — the §3 fingerprint is now hashed over the comment-stripped §3 on BOTH snapshot + divergence sides; the risk is that a real shape edit could be masked. Mitigated: `_strip_live_scaffold` removes ONLY `` comments + whitespace, never the fenced shape or Status line, so any contract-content edit still trips the guard (a scenario asserts reopen→re-gate is clean while the existing tamper tests still catch a §3 shape edit). Secondary [contract]: fenced-block safety — a `` inside a```fence``` survives the strip.

Status: FROZEN @ v2 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete (one test per Must + per Reject)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_pass_strips_instruction_comments: gate PASS / assert no `

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/tooling/test_strip_scaffold_at_done.py` `add-method/tooling/test_gate_record_writeback.py` `add-method/tooling/test_adr_harvest.py`
Strategy (ordered batches): 1. add `_strip_live_scaffold(text)` (re.split on```…``` fences; strip `` only in non-fence segments; trim trailing ws; collapse 3+ newlines). 2. call it last in cmd_gate's completing branch (after the §6/§7 stampers), atomic + degrade-safe. 3. (v2) normalize the §3 fingerprint in `_tripwire_snapshot` + `_tripwire_divergence` via `_strip_live_scaffold` so the strip is invisible to the tamper guard. 4. extend the 2 sibling tests' normalizers (gate-record no-op + adr-harvest byte-untouched) to ignore the now-stripped comments — orthogonal-behavior accommodation, NOT weakening. 5. propagate add.py ×3; re-pin engine_pin ×2; prepare_bundle. 6. full suite green.

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: as planned for batches 1–2; batch 3 evolved during the change request — a naive `_md5_text(_strip_live_scaffold(raw3))` left an off-by-one §3-boundary newline (snapshot vs post-strip extraction), so the normalization was hoisted into a shared `_contract_fingerprint(raw3)` that also `.strip()`s outer whitespace; both tripwire sides call it (no drift). Sibling normalizers (batch 4) reuse the engine's own `_strip_live_scaffold` for parity.
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2550/0 (background run, exit 0)
- [x] coverage did not decrease — +7 tests added (strip suite incl. the v2 reopen guard); none removed
- [x] no test or contract was altered during build — the 2 sibling normalizers extended are IN §5 scope (orthogonal-behavior accommodation), no assertion weakened; §3 frozen @ v2
- [x] the green was EARNED, not gamed — refute-read below; the reopen guard fails RED (exit 3) without the tripwire normalization and passes only with it
- [x] concurrency / timing of the risky operation is safe — strip is a single atomic `_atomic_write` AFTER state.json is saved; a write fault degrades (gate already recorded)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib `re`; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — engine NO-EXEC honored (no subprocess); state-first (strip mirrors the file only)
- [ ] a person reviewed and approved the change — method-trust change (tamper guard) ESCALATES to the human

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] After `gate PASS`, the task's TASK.md has no `` and keeps its headings/§1 — confirmed by `test_pass_strips_instruction_comments` + this task self-strips at its own gate (dogfood)
- [x] A `` inside a```fence``` survives while one outside is removed — confirmed by `test_fenced_block_left_untouched`
- [x] `gate HARD-STOP` leaves the comments (task not done) — confirmed by `test_hard_stop_does_not_strip`
- [x] `_strip_live_scaffold` is idempotent + trims trailing ws — confirmed by `test_idempotent_and_content_safe`
- [x] reopen→re-gate of a stripped task is CLEAN (no false contract_tampered) — confirmed by `test_reopen_regate_is_clean` (exit 0; RED exit 3 without the v2 fix)
- [x] every add.py copy == re-pinned ENGINE_MD5 (b8018975…); phases pool untouched; full suite green — confirmed by parity/pin tests + 2550/0 run summary

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_strip_live_scaffold` referenced from cmd_gate's completing branch AND `_contract_fingerprint`; `_contract_fingerprint` referenced from `_tripwire_snapshot` + `_tripwire_divergence` (both sides)
- [x] DEAD-CODE (code) — no orphaned symbol; the two helper regexes (`_HTML_COMMENT_RE`, `_BLANK_RUN_RE`, `_TRAILING_WS_RE`) are all consumed by `_strip_live_scaffold`
- [x] SEMANTIC (prose / non-code) — read in full: the empirical debug confirmed the §3-boundary off-by-one newline → `_contract_fingerprint` adds `.strip()` so snapshot==divergence converge byte-for-byte

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: tried to break the tamper-guard normalization 3 ways — (1) the reopen guard fails RED (exit 3) without the v2 fix and green with it, so it is not vacuous; (2) confirmed a REAL §3 fenced-shape edit still trips contract_tampered (the existing tamper tests test_reopen/test_min_pillar still pass, which depend on real edits being caught); (3) the 2 sibling normalizers were extended to the engine's OWN `_strip_live_scaffold` (parity), not loosened to ignore real diffs — `test_no_gate_record_block_is_noop` still asserts the write-back fabricated nothing.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — no secrets/injection; `re` only; the normalization narrows what the tamper guard ignores to template comments, never contract content (a real shape edit still HARD-STOPs).
2. Concurrency: CLEAR — single atomic write after state is persisted; no shared mutable state.
3. Architecture: CLEAR — NO-EXEC honored; one shared `_contract_fingerprint` used on both tripwire sides (no drift); strip mirrors the file only.
Verdict: PASS
Residue: none
Binding: advisory — method-trust (escalates to human regardless)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-30

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose strip in cmd_gate's completing branch, after the §6/§7 stampers; rejected strip in _sync_task_marker (rejected — it runs for every phase, not just done) · a separate `add.py tidy` command (rejected — manual, drifts; the audit wants it automatic at close)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: as planned for batches 1–2; batch 3 evolved during the change request — a naive `_md5_text(_strip_live_scaffold(raw3))` left an off-by-one §3-boundary newline (snapshot vs post-strip extraction), so the normalization was hoisted into a shared `_contract_fingerprint(raw3)` that also `.strip()`s outer whitespace; both tripwire sides call it (no drift). Sibling normalizers (batch 4) reuse the engine's own `_strip_live_scaffold` for parity.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

