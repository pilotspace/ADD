# TASK: persist the canonical render to RETRO.md at milestone close

slug: retro-artifact · created: 2026-06-02 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- hooks the close ritual (cmd_milestone_done) in add.py — the engine; human reviews the diff at verify -->

> One-approval front (v7): the AI drafts Spec + Scenarios + Contract + Tests as ONE
> bundle; the human gives a single approval AT the frozen contract (§3, the seam).
> The render SHAPE is already frozen by report-render — this task only freezes WHERE
> and WHEN that canonical render is persisted, and the read-only-state invariant.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Closing a milestone (`add.py milestone-done <v>`) persists the milestone's canonical render
to `.add/milestones/<v>/RETRO.md` — the spec'd "Milestone exit report" artifact (appendix-f).
It reuses report-render's ONE renderer; it adds no new render logic and no new state field.

Must:
  - on a SUCCESSFUL close, write `.add/milestones/<v>/RETRO.md` containing exactly
    `render_report(root, state, <v>, width=72, ascii=False)` — the canonical PLAIN render
    (no ANSI, fixed width 72), byte-identical to a piped `report <v>`
  - the RETRO render reflects the milestone AS CLOSED — every member task done, so the
    verdict reads `DONE` (render is task-based, not dependent on the status write order)
  - persisting RETRO.md must NOT mutate `state.json` beyond the close ritual's pre-existing
    status write — the retro step itself is read-only on state (writes exactly one doc file)
  - re-running `milestone-done` on an already-closed milestone re-writes RETRO.md idempotently
    (same canonical content) — no crash, no duplicate
Reject:
  - the close itself already rejects `unknown_milestone` / `milestone_incomplete` (unfinished
    tasks) BEFORE any RETRO write — a milestone that cannot close produces no RETRO.md
  - if the RETRO.md write fails (e.g. unwritable dir / encoding error), the close ABORTS with
    `retro_write_failed` BEFORE committing `status=done` to state.json — fail-closed: no
    half-done milestone with a missing retro
After:
  - `.add/milestones/<v>/RETRO.md` exists and equals the canonical render; the milestone is
    `status=done` in state.json; the two are consistent. Scope: this guarantees every NEW close
    writes a retro; it does NOT backfill milestones closed before v9 (those stay retro-less —
    out of scope, same invariant-rot caution as the [SDD] delta this milestone surfaced)
Assumptions (confirm before building):
  - [x] write happens inside `cmd_milestone_done` (the single close path), not a new command —
        confirmed: close is the only "milestone exit" event in the engine
  - [x] RETRO.md is overwritten on re-close, not appended/versioned — confirmed: it is a
        regenerable projection of state, never hand-edited source
  - [x] ordering is render+write-RETRO THEN flip-status+save_state, so a write failure rolls
        back naturally (status never commits) — confirmed as the failure-design choice

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: close writes the canonical retro
  Given a milestone 'vX' whose every member task is done
  When I run `add.py milestone-done vX`
  Then `.add/milestones/vX/RETRO.md` exists
  And its content is byte-identical to render_report(root, state, "vX", width=72, ascii=False)
  And the file carries no ANSI escape sequences

Scenario: retro write does not mutate state beyond the close
  Given a closable milestone 'vX'
  When the retro is rendered and written
  Then the only state.json change from the whole close is the milestone's status/updated fields
  And the RETRO render step itself writes nothing to state.json

Scenario: idempotent re-close
  Given milestone 'vX' is already done with a RETRO.md
  When I run `add.py milestone-done vX` again
  Then RETRO.md is rewritten with the same canonical content
  And the command exits 0 (no crash, no duplicate file)

Scenario: a milestone that cannot close produces no retro
  Given milestone 'vX' has an unfinished task
  When I run `add.py milestone-done vX`
  Then it exits non-zero with "milestone_incomplete"
  And no RETRO.md is written and state.json is unchanged

Scenario: a failed retro write aborts the close (fail-closed)
  Given a closable milestone 'vX' whose RETRO.md cannot be written
  When I run `add.py milestone-done vX`
  Then the command fails (non-zero)
  And the milestone's status in state.json is NOT flipped to done
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI:  add.py milestone-done <v>        (EXISTING command — this task extends its body)
        exit 0  -> milestone marked done AND .add/milestones/<v>/RETRO.md written
        exit !0 -> unknown_milestone | milestone_incomplete | retro_write_failed
                   (in every reject: no status flip; on retro_write_failed: no usable RETRO.md)

New seam (one helper, reuses the frozen renderer):
  _write_retro(root, state, slug) -> Path          # renders canonical + writes the doc
    - content = render_report(root, state, slug, width=72, ascii=False)   # the v9 frozen shape
    - writes content to <root>/.add/milestones/<slug>/RETRO.md via
      Path.write_text(content, encoding="utf-8")   # EXPLICIT utf-8: canonical is ascii=False
                                                     # (Unicode ═ ● ◉ ○ ─); never the locale default
    - returns the RETRO.md Path
    - PURE on state: reads state + MILESTONE.md/TASK.md/tests (via render_report); the ONLY
      thing it writes is that one file — it never calls save_state / mutates `state`

Close ritual order in cmd_milestone_done (failure-design = render-doc BEFORE state commit):
  1. validate: unknown_milestone -> die; gather members; blockers -> milestone_incomplete -> die
  2. try: retro_path = _write_retro(root, state, slug)    # if this raises, we have NOT yet
     except OSError: _die("retro_write_failed")           #   flipped status -> natural rollback
  3. state[milestones][slug].status = "done"; updated = _now(); save_state(root, state)
  4. print summary + f"wrote {retro_path.relative_to(root)}"

Files/State touched:
  WRITE  .add/milestones/<v>/RETRO.md        (generated doc — like a milestone doc; never source)
  WRITE  .add/state.json                      (status/updated only — pre-existing close behavior;
                                               retro adds NO new field and NO new mutation)
  READ   state.json · MILESTONE.md · each member TASK.md · tasks/<slug>/tests/   (via render_report)

Invariant: every NEW close is done ⇒ RETRO.md present and == canonical render. A close that
fails to write the doc fails the whole command (status stays active), so no NEW done-without-retro
state is reachable. (Milestones closed before v9 keep no retro — backfill is out of scope.)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (2026-06-02 — approved at the seam; reuses report-render's frozen render
shape, adds only WHERE/WHEN it persists + the read-only-state + fail-closed invariants. Advisor
pins folded in: explicit utf-8, retro_write_failed reject, scoped no-backfill invariant.)
<!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 90% (of the new close-writes-retro path)
Plan (one test per scenario; drive `add.py milestone-done` via `main()` on a tempdir .add):
  - test_close_writes_canonical_retro: fixture milestone, all tasks done / run milestone-done /
    assert RETRO.md exists AND == render_report(root, state, slug, width=72, ascii=False) AND
    contains no "\x1b[" escape
  - test_retro_write_is_state_pure: snapshot state.json bytes / call `_write_retro` directly /
    assert state.json bytes UNCHANGED and RETRO.md == canonical (isolates the retro step from
    the close's own status write)
  - test_close_state_diff_is_status_only: capture state before/after milestone-done / assert the
    ONLY changed keys under the milestone are status (-> "done") and updated
  - test_idempotent_reclose: close once, close again / assert RETRO.md still == canonical, exit 0
  - test_incomplete_blocks_retro: milestone with one task at phase=build / run milestone-done /
    assert exit !=0 ("milestone_incomplete") AND no RETRO.md AND state.json unchanged
  - test_failed_write_aborts_close: monkeypatch `_write_retro` to raise OSError (portable; root
    can't bypass; tests the ordering directly) / run milestone-done / assert exit !=0 with
    "retro_write_failed" AND milestone status still NOT "done" in state.json (fail-closed rollback)

Tests live in: `add-method/tooling/test_retro.py` (mirrors test_report.py; the dual tree keeps
suites in the tooling dir) · MUST run red (missing `_write_retro` / unhooked close) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): render+write RETRO.md BEFORE the status-flip commit — the doc
  write is the only failure-prone step, so it runs first; on OSError the close aborts
  (`retro_write_failed`) and status never flips (natural rollback). The retro step never writes
  state.json. Partial-write risk (process dies mid-write) self-heals: status didn't commit, so
  re-close overwrites the doc cleanly.
Code lives in: `add-method/tooling/add.py` (`_write_retro` helper + the `cmd_milestone_done` hook),
  synced byte-identical to `.add/tooling/add.py`.
Constraints: do NOT change any test or the contract; stdlib only (matches add.py); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 6 `test_retro` + full suite **208 passed** (incl. report-render's v4
      human-review layout change, which retro inherits via the shared renderer); red-first
      confirmed: the 4 new-behavior tests failed for the right reason (no `_write_retro`, close
      didn't write RETRO) before build; 2 invariant-guards (state-diff-only, incomplete-blocks)
      were green pre-build and stayed green (they pin invariants the change must not break)
- [x] coverage did not decrease — one test per scenario incl. both rejects (incomplete /
      retro_write_failed) and the fail-closed rollback; canonical-equality + no-ANSI asserted
- [x] no test or contract was altered during build — contract FROZEN @ v1 honored exactly:
      `_write_retro(root, state, slug)`, explicit `encoding="utf-8"`, render-before-commit order,
      `_die("retro_write_failed")` on OSError. No test weakened.
- [x] concurrency / timing of the risky operation is safe — single local file write; ordered
      BEFORE the state commit so a failure rolls back (status stays active). DISCLOSE (considered
      tradeoff): RETRO.md uses plain `write_text`, not `_atomic_write` (tmp+rename) as save_state
      does — a crash mid-write could leave a partial doc, but since status hasn't committed,
      re-close regenerates it cleanly (self-healing); kept to honor the frozen contract verbatim.
- [x] no exposed secrets, injection openings, or unexpected dependencies — **stdlib only**;
      writes one file under `.add/milestones/<slug>/` (no path from user input — slug is a
      validated state key); reads only via the already-vetted pure renderer; no eval/shell/network
- [x] layering & dependencies follow CONVENTIONS.md — `_write_retro` sits beside `render_report`
      (reuses it at canonical args, adds no render logic); hook is 4 lines in `cmd_milestone_done`;
      dual tree (`.add` ⇄ `add-method`) re-synced byte-identical; RETRO.md is a generated DOC,
      never engine state (state.json untouched by the retro step — `test_retro_write_is_state_pure`)
- [ ] a person reviewed and approved the change   ← YOUR gate (human-only step)

### GATE RECORD
Outcome: PASS   (recorded via `add.py gate PASS retro-artifact`, 2026-06-02; diff reviewed)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-02

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a `retro_write_failed` exit in normal use (the milestones
  dir should always be writable at close — a failure means a deeper FS/permission problem); a
  closed milestone WITHOUT a RETRO.md (the done⇒retro invariant broke — should be impossible for
  a new close).
Spec delta for the next loop: the close ritual is now the proof point that "report writes nothing,
  the CLOSE writes the doc" — clean separation held. If a future surface needs the same
  render-then-persist, reuse `_write_retro`'s shape (pure render + single utf-8 write, ordered
  before any state commit).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

- [TDD · folded] A "fail-closed / abort-before-mutate" guarantee is directly testable by
  monkeypatching the IO step to raise and asserting the downstream state commit did NOT happen.
  Evidence: test_failed_write_aborts_close patches `_write_retro`→OSError and asserts status never
  flips to done. Fold: make this the house pattern for any ordered "do-risky-IO THEN commit-state"
  path — the rollback is proven by the test, not just by reading the ordering.
- [ADD · folded] A directed PRESENTATION change mid-flight (report-render v4, while retro-artifact
  was at verify) cost only a shape-sketch + test-assertion update — no re-freeze, no SPECIFY
  round-trip. Evidence: the v4 layout landed by updating §3's shape sketch + 4 assertions +
  2 new guards, 208 green, while the frozen DATA seam was untouched. Fold: this empirically
  confirms report-render's [ADD] "presentation isn't a freezable contract" delta — bind the
  data seam, let the layer iterate. Worth promoting both to PROJECT.md as one method rule.
