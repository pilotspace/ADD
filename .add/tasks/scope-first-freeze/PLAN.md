# PLAN: Freeze refuses a zero-cover Scope (scope_unresolved); root-relative src/ default + task-dir teach note

slug: scope-first-freeze · created: 2026-07-23 · stage: mvp
milestone: wm1-lean-to-twelve
autonomy: auto
phase: done
sensitivity: mechanical
gate_mode: ai-plan-verify
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the scope-grammar death spiral dies at the freeze — (a) a DECLARED §3 Scope whose every token drops (unbackticked/outside-root garbage) REFUSES the freeze (`scope_unresolved`, validate-then-write, nothing persisted) instead of freezing a guaranteed later scope_violation; (b) the template Scope default flips `./src/`→`src/` (root-relative — the shape agents copy) with a grammar cue in the hint; (c) a MISSING token resolving under `.add/tasks/` gets a teach note in the freeze echo; (d) the placeholder-still-default warning — DEAD since #38 reworded its detection hint — is repaired. Evidence: 2026-07-23 WM1 re-measure, 3/3 reps lost 2–3 calls to this class (rep0 garbage; rep1/2 `./app/` task-dir cover vs root `app/` writes).
Framings weighed: fail-closed at the FREEZE seam (chosen — the Scope line lives INSIDE frozen §3, so any post-freeze fix costs a re-cross; rep0 paid exactly that ×2) · refuse at the tests→build cross (rejected — §3 is already frozen there; fixing scope would mean tampering a frozen contract) · warn-only louder (rejected — that is today's behavior; the echo already warned and 3/3 agents froze past it)
Must:
<must>
  - a freeze whose §3 declares a Scope line resolving to the EMPTY allowlist (`_declared_scope` == []) is REFUSED with error `scope_unresolved` naming the grammar (backticked tokens · `name/` = project root · `./…` = this task's dir); nothing is written (validate-then-write)
  - UNDECLARED (no Scope line, `_declared_scope` is None) stays grandfathered — freeze proceeds silently, exactly as today
  - a resolvable declaration (tokens [ok] or [MISSING]) freezes exactly as today — greenfield MISSING is never refused
  - the freeze echo appends a teach note to any [MISSING] token resolving under `.add/tasks/`: it names the `./…`=task-dir rule and the root-relative alternative
  - PLAN.md.tmpl's Scope default reads `src/` (root-relative) with the grammar cue in the hint, across all 4 twins
  - the untouched-default warning fires again: detection keys on the CURRENT hint text (`<HARD — fill before the freeze`), message updated for the `src/` default
  - `_build_plan`'s placeholder skip recognizes the new bare `src/` default alongside the legacy `./src/`
</must>
Reject:
<reject>
  - refusing an UNDECLARED task -> "grandfather_broken"
  - refusing a resolvable-but-MISSING (greenfield) declaration -> "greenfield_refused"
  - any state.json/sidecar/PLAN.md write on the scope_unresolved path -> "refusal_wrote_state"
</reject>
After:
<after>
  - a garbage Scope declaration fails fast at the freeze with a copy-ready grammar reminder; fresh scaffolds teach the root-relative token shape; the measured scope_violation→re-cross cycle (+2–3 calls/rep) has no remaining trigger in the happy path; suite green; ENGINE_MD5 repinned
</after>
Boundary: none — inputs are the §3 Scope line text (grammar unchanged, only the []-result now refuses) and static template text.
<assumptions>
  ⚠ that NO existing test or archived-task flow freezes with a []-resolving Scope declaration — if wrong: that test breaks and needs its expectation updated to the refusal. Mitigated: grepped the suite — fixtures use `pkg/nope/` (MISSING, resolvable) or UNDECLARED; the only []-asserting test is a parser UNIT test (test_scope_gate_enforce.test_parser_outside_root_dropped, no freeze involved).
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Surface: cmd_freeze validation block (add.py ~1180, after unflagged_freeze/boundary_unfilled) + _scope_echo + the untouched-default warning in _build_entry (~1968) + _build_plan skip (~5832) + PLAN.md.tmpl (×4 twins)

freeze validation (NEW, validate-then-write):
  declared = _declared_scope(root, slug)
  declared == []  ->  _die("scope_unresolved: <slug> declares a §3 Scope but every token dropped …
                       backtick each token: `name/` = project root · `./…` = THIS task's dir …")
  None / non-empty ->  proceed exactly as today

_scope_echo (teach note): a [MISSING] rel starting ".add/tasks/" additionally prints
  "note: <rel> resolves under THIS TASK's dir (`./…` grammar) — a project file wants a root-relative token (e.g. `app/`)"

_build_entry warning repair: detection "<fill before the §3 freeze" -> "<HARD — fill before the freeze"; message names the `src/` default
_build_plan skip: startswith("./src/") OR the bare untouched "src/" default
PLAN.md.tmpl line: Scope (may touch): `src/`   <HARD — … tokens: `name/` = project root · `./…` = THIS task's dir …>; §5 Code lives in: `src/`
test_edge_truth replace-literal updated to the new template line.
Invariant: 4 template twins + 4 add.py twins byte-identical · ENGINE_MD5 repinned · ENGINE_PKG_MD5 unchanged (no add_engine/ edit)
```

Target (measurable): new test_scope_first_freeze green (live subprocess: garbage freeze exits non-zero naming scope_unresolved with NO sidecar/anchor written · greenfield MISSING freeze exits 0 · UNDECLARED exits 0 · teach note printed · default-warning fires) + full tooling suite green. Boots: N/A.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered before this froze

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT
Scope (may touch): `add-method/tooling` `add-method/src/add_method/_bundled/tooling` `add-method/.add/tooling` `.add/tooling`   <the 4 tooling twins — add.py · templates/PLAN.md.tmpl · engine_pin.py · test_edge_truth.py · the new conformance test>
Regression floor: the tooling suite — test_scope_echo_draft · test_scope_gate_enforce · test_edge_truth · test_decide_digest · test_template_atomic · test_freeze_flag_slot · bundle/packaging/ship — must stay green
Persona (optional): `.add/personas/methodology-engine-dev.md` (fail-closed engine gate work; advisory)

Least-sure flag surfaced at freeze: [contract] whether refusing `declared == []` at the freeze seam catches EVERY garbage form the bench produced without over-refusing — outside-root-only declarations also resolve [] and become refusals (correct: they grant no cover), but any yet-unseen fixture that legitimately freezes with zero cover would now break; mitigated by the suite-wide grep (only a parser unit test asserts []) and by running the FULL suite before the gate.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — cmd_freeze validation block · _scope_echo · _build_entry default-warn · _build_plan skip · PLAN.md.tmpl Scope line, all cited by symbol and present
- [x] §1 every Must + every Reject present, each Reject paired with an error code — 7 Musts; Rejects grandfather_broken · greenfield_refused · refusal_wrote_state
- [x] §3 Contract shape is concrete — exact refusal semantics, detection strings, template line; no placeholders
- [x] Lowest-confidence flag surfaced and substantive — [contract] over-refusal risk on []-resolving declarations, mitigated by suite grep + full-suite run
Verified by: claude-opus-4-8 (add-worker, direction beat) · at: 2026-07-23T13:38:53Z

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_garbage_scope_refused: live board; §3 Scope line with UNBACKTICKED tokens → freeze exits non-zero, names `scope_unresolved` + the grammar; NO scope-snapshot.json, NO state anchor, §3 NOT frozen · covers: M1, R:refusal_wrote_state
  - test_outside_root_refused: Scope of only `` `../outside/` `` → same refusal (outside-root drops = zero cover) · covers: M1
  - test_undeclared_grandfathered: no Scope line → freeze exits 0, "scope: UNDECLARED (grandfathered)" · covers: M2, R:grandfather_broken
  - test_greenfield_missing_freezes: Scope `` `pkg/nope/` `` → freeze exits 0 with [MISSING] echo (never refused) · covers: M3, R:greenfield_refused
  - test_taskdir_missing_teach_note: Scope `` `./nope/` `` (task-dir, missing) → freeze exits 0 AND the echo carries the task-dir teach note · covers: M4
  - test_template_default_root_relative: canon PLAN.md.tmpl Scope line token is `src/` (no `./` prefix), hint carries the grammar cue; 4 twins md5-equal · covers: M5
  - test_untouched_default_warns: a task frozen with the template Scope line UNTOUCHED gets the still-the-default warning (detection repaired) · covers: M6
  - test_build_plan_skips_new_default: _build_plan skips a bare `src/` untouched default (and still skips legacy `./src/`) · covers: M7
</test_plan>
Tests live in: `add-method/tooling/test_scope_first_freeze.py` — red before the engine/template change, green after.

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned + one self-caught bug — the first template hint used BACKTICKED grammar examples (`name/` · `./…`) which the scope parser read as PHANTOM tokens (the known §5-note-backtick hazard); caught by the new default-warn test's output, fixed by de-backticking the hint and asserting no phantom tokens. Red suite (6/8 red) → engine edits (scope_unresolved refusal at freeze validation · _scope_echo task-dir teach note · default-warn detection repaired for BOTH hint eras · _build_plan skips bare src/) → template default `./src/`→`src/` + grammar hint → test_edge_truth literal updated → ENGINE_MD5 repinned 868bd79b→68109d80 → 4-way twin sync → 122 targeted green + full suite 2270 (1 census collision fixed via the split-token idiom, assertion strength identical).
Code lives in: `add-method/tooling/` (+ 3 tooling twins)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — test_scope_first_freeze 8/8; scope/edge/digest/template/parity neighbors 122/0; full suite 2270 with the one census collision resolved (split-token, assertion identical); add.py check 370/0
- [x] coverage did not decrease — net +8 conformance tests
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; the red suite predates the freeze; the census fix touched a DONE task's guard via the sanctioned split-token idiom with identical strength (disclosed)
- [x] the green was EARNED, not gamed — 6/8 ran RED first; refusal tests drive the REAL cmd_freeze via add.main on a live board and assert NOTHING persisted (no sidecar, §3 unfrozen); the phantom-token bug was caught BY the suite, not around it
- [x] concurrency / timing of the risky operation is safe — validate-then-write: the refusal fires before any PLAN.md/state/sidecar write
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — 4-way twin sync held; ENGINE_MD5 repinned; ENGINE_PKG_MD5 untouched (no add_engine/ edit)
- [x] a person reviewed and approved the change — sensitivity: mechanical, gate_mode: ai-plan-verify (sanctioned headless path)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self (add-worker, verify beat) · adversarially checked: (1) tried to refuse a LEGITIMATE freeze — UNDECLARED and greenfield-[MISSING] boards both freeze exit-0 (grandfather + greenfield tests); (2) tried to sneak state past the refusal — asserted NO scope-snapshot.json and §3 NOT FROZEN on the refusal path; (3) hunted phantom cover — found + fixed the hint-backtick token leak and pinned it (assertNotIn "scope: name/"); (4) both this task's AND freeze-flag-slot's own freezes ran first-try clean on the new engine — live dogfood of the whole lean-pass.

### GATE RECORD
Reported: yes — the gate report (banner/ARC) rendered before this outcome recorded
Outcome: PASS
Reviewed by: Tin Dang (AI-plan-verify, mechanical) · date: 2026-07-23

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose fail-closed at the FREEZE seam; rejected refuse at the tests→build cross (rejected — §3 is already frozen there; fixing scope would mean tampering a frozen contract) · warn-only louder (rejected — that is today's behavior; the echo already warned and 3/3 agents froze past it)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned + one self-caught bug — the first template hint used BACKTICKED grammar examples (`name/` · `./…`) which the scope parser read as PHANTOM tokens (the known §5-note-backtick hazard); caught by the new default-warn test's output, fixed by de-backticking the hint and asserting no phantom tokens. Red suite (6/8 red) → engine edits (scope_unresolved refusal at freeze validation · _scope_echo task-dir teach note · default-warn detection repaired for BOTH hint eras · _build_plan skips bare src/) → template default `./src/`→`src/` + grammar hint → test_edge_truth literal updated → ENGINE_MD5 repinned 868bd79b→68109d80 → 4-way twin sync → 122 targeted green + full suite 2270 (1 census collision fixed via the split-token idiom, assertion strength identical).
- [AI] verify — gate PASS (reviewed by Tin Dang (AI-plan-verify, mechanical))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
