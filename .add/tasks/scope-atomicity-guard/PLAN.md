# PLAN: Advisory atomicity nudge at freeze for multi-Part scope

slug: scope-atomicity-guard · created: 2026-07-23 · stage: mvp
milestone: intake-atomicity
autonomy: auto
phase: build
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 0 · GROUND — the observed map (anchors opened live 2026-07-23)

- `add-method/tooling/add.py` · `cmd_freeze` (~962) — the §3 contract-freeze write command. After the atomic Status flip + `print("froze §3 …")` it calls advisory printers in a fail-open guard: `try: _scope_echo(root, slug) except Exception: pass`. This is the hook seam — a sibling advisory printer added here fires at the freeze the human already reads, never blocking it.
- `add-method/tooling/add.py` · `_scope_echo` (~870) — the pattern to mirror: pure read, prints `note:`/`scope:` lines, imposes nothing, never raises out (caller wraps fail-open).
- `add-method/tooling/add.py` · `_raw_phase_bodies(root, slug)` — returns section-int to body-text for §1–§7; the read primitive both echoers use to reach a task's section text.
- Precedent for measure-not-block advisory nudges: `persona-seed-nudge` / `persona-fit` (fires at new-milestone, advisory only, never a gate) and `_scope_echo`'s own `note:` lines. The house style is nudge, not gate.
- The three engine/template trees stay byte-identical: `add-method/tooling/add.py`, `add-method/.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py` (parity is asserted by the bundle-parity tests).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: at the §3 contract-freeze, surface a non-blocking advisory nudge when a task's frozen scope reads as more than one independent Part (a longtail/drain/sweep catch-all), steering it toward a milestone-of-tasks. Measure-not-block: the freeze always proceeds.
Framings weighed: advisory nudge (chosen — matches persona-seed-nudge and _scope_echo house style; a false positive costs one ignorable line, never a blocked freeze) · hard freeze-refusal (rejected — re-adds ceremony strategy-intake exists to remove; a false positive blocks a legitimate multi-facet task)
Must:
<must>
  - M1 detect multi-Part scope: a pure read of a task's §1/§3 returns the ordered list of independent Parts it enumerates; the nudge fires only when that list has two or more members.
  - M2 fire the nudge at freeze: on two-or-more Parts, cmd_freeze prints one advisory block naming the Part count, the Part labels, and the steer (new-milestone plus one task per Part).
  - M3 stay non-blocking and fail-open: the nudge is a pure read printed after the Status flip; it never changes the freeze exit status and a malformed/absent section silently prints nothing (mirrors the _scope_echo try/except seam).
  - M4 tree parity: the change is byte-identical across all three tooling trees (parity tests stay green).
</must>
Reject:
<reject>
  - single-Part or unenumerated scope (a normal atomic task) -> no nudge printed (silence is the pass)
  - a malformed / missing §1 and §3 -> no nudge, no raise -> "silent_absent" (never an error)
</reject>
After:
<after>
  - freezing a task whose scope enumerates two or more independent Parts prints the atomicity nudge AND still records FROZEN normally
  - freezing a normal single-Part task is byte-unchanged in behavior (nudge silent)
</after>
Boundary: the one external input shape is a task PLAN.md's §1/§3 body text — Part enumeration appears as either a numbered bold list, an explicit "(N parts)" / "N-part" marker, or a catch-all keyword (longtail, drain, sweep, catch-all, grab-bag) in the slug or title. Tests must speak all three plus the negative (a normal one-contract task).
<assumptions>
  ⚠ the detection heuristic (numbered-bold-parts, "(N parts)" marker, catch-all keyword) is the right signal — if wrong: it MISSES a junk-drawer that lists its parts as plain unnumbered Must bullets (false negative, the overload ships as admin-longtail did). Chosen because a false negative is recoverable (the honesty layer still catches fallout downstream) while a false positive on a real atomic task erodes trust in the nudge; the heuristic is deliberately biased toward precision over recall.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
  - Given a task PLAN.md whose §3 has a "(4 parts)" header plus four numbered bold parts, When it is frozen, Then the freeze succeeds AND an advisory nudge names four Parts and the steer.
  - Given a task whose slug contains "longtail", When frozen, Then the nudge fires on the catch-all-keyword signal even if the parts are not numbered.
  - Given a normal atomic task with one §3 contract shape and no part enumeration, When frozen, Then no nudge is printed and the freeze output is byte-unchanged from today.
  - Given a task with a malformed/empty §1 and §3, When frozen, Then no nudge and no exception (the freeze completes normally).
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — HARD, tamper-guarded)

```
_scope_parts(root, slug) -> list of Part labels
  pure read of §1/§3 body via _raw_phase_bodies; returns ordered Part labels.
  Part signals (union):
    numbered-bold   a line "N. **label**"
    marker          "(N parts)" / "N-part"  with N >= 2
    catch-all kw    slug or title matches longtail|drain|sweep|catch-all|grab-bag
  returns [] when fewer than 2 parts detected (the silent-pass case).

_atomicity_nudge(root, slug) -> None
  parts = _scope_parts(root, slug)
  if len(parts) < 2: return            # silence = pass
  print "note: §3 scope reads as {n} independent Parts ({labels}) — one file = one task."
  print "      consider: add.py new-milestone <slug> + one task per Part."

cmd_freeze  (hook, additive):  after the existing _scope_echo fail-open guard, add
  try: _atomicity_nudge(root, slug)
  except Exception: pass               # never blocks a freeze
```
Schema: no state.json / disk writes — pure read plus stdout. Three tooling trees updated byte-identical.

Target (measurable): a two-or-more-Part / catch-all task freeze prints the nudge (asserted on captured stdout); a single-Part task freeze prints zero nudge lines AND its non-nudge freeze output is byte-identical to pre-change; the full test_freeze_ suite plus bundle-parity tests stay green; freeze exit status unchanged in every case.
Least-sure flag surfaced at freeze: [contract] the detection heuristic (numbered-bold-parts ∪ "(N parts)" marker ∪ catch-all keyword) is biased to precision over recall — it will MISS a junk-drawer whose parts are plain unnumbered Must bullets (false negative). Accepted because a false negative is recoverable (the honesty layer still catches downstream fallout, as admin-longtail proved) while a false positive on a real atomic task erodes trust in the nudge; if recall matters more, that reopens this contract.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/add.py` `add-method/.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `./tests/`
Regression floor: the `test_freeze_` suite plus the bundle-parity test (three-tree byte-identity) — run green before the gate.
Persona (required): `.add/personas/methodology-engine-dev.md` (deterministic, fail-loud engine work; advisory, never lowers a gate)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_nudge_fires_on_numbered_multipart: freeze a fixture PLAN with a "(4 parts)" §3 plus numbered bold parts -> stdout contains the nudge naming four Parts · covers: M1,M2
  - test_nudge_fires_on_catchall_slug: freeze a fixture whose slug matches longtail -> nudge fires · covers: M1,M2
  - test_no_nudge_on_atomic_task: freeze a single-contract fixture -> zero nudge lines in stdout · covers: R:single-part
  - test_freeze_output_identical_when_silent: non-nudge freeze stdout matches the pre-change baseline for an atomic task · covers: M3
  - test_nudge_failopen_on_malformed: freeze a fixture with empty §1/§3 -> no nudge, no raise, freeze completes · covers: M3,R:silent_absent
  - test_three_trees_byte_identical: the added functions are byte-identical across the three tooling trees · covers: M4
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: fill at VERIFY
Code lives in: `add-method/tooling/add.py` plus the two mirror trees
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope; keep the §3 Regression floor green; the nudge is pure-read plus fail-open — it must never alter the freeze write path or exit status.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all §4 tests pass — including the test_freeze_ plus parity regression floor
- [ ] coverage did not decrease
- [ ] no test or contract altered during build
- [ ] the green was EARNED — the identical-when-silent test proves no behavior drift on normal tasks
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] a person reviewed and approved the change

### GATE RECORD
Reported: no
Outcome: PASS | RISK-ACCEPTED | HARD-STOP
Reviewed by: name · date: date

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
harvested at done

### Spec delta
One line per forward change, tagged SPEC open/seeded/dropped plus evidence.

### Competency deltas
One lesson per line: DDD/SDD/UDD/TDD/ADD open — the learning (evidence).
