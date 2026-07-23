# PLAN: PLAN.md.tmpl §3 gains a drafted-blank 'Least-sure flag surfaced at freeze:' slot (4 twins)

slug: freeze-flag-slot · created: 2026-07-23 · stage: mvp
milestone: wm1-lean-to-twelve
autonomy: auto
phase: done
sensitivity: mechanical
gate_mode: ai-plan-verify
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: PLAN.md.tmpl §3 gains a drafted-blank `Least-sure flag surfaced at freeze:` slot so agents fill the REQUIRED freeze flag while drafting §3 instead of learning it from the `unflagged_freeze` refusal — the 2026-07-23 WM1 re-measure showed the FIRST freeze failing on exactly this in 3/3 reps (+1 wasted call each; I hit the same wall on trim-build-strategy-labels this session).
Framings weighed: drafted-blank template slot whose UNFILLED placeholder still refuses (chosen — the affordance teaches at draft time; the `_FLAG_PART_RE` gate keeps binding because `[spec|scenario|contract|test]` never matches the part regex) · weaken unflagged_freeze to a warning (rejected — inverts the flag-first-freeze floor) · put the hint only in the freeze error (rejected — that IS today's behavior, measured +1 call/rep)
Must:
<must>
  - PLAN.md.tmpl §3 carries a `Least-sure flag surfaced at freeze:` line with a bracketed part-menu placeholder + `<...>` hint, placed after the Persona line, before `### AI-verify record`
  - the UNFILLED placeholder does NOT satisfy the engine's flag gate — `_FLAG_PART_RE` must not match the literal `[spec|scenario|contract|test]`, so an undrafted freeze still refuses `unflagged_freeze`
  - a FILLED slot (e.g. `[contract] the shape of X — because Y`) passes the same gate unchanged — zero engine edit
  - all 4 PLAN.md.tmpl twins stay byte-identical
</must>
Reject:
<reject>
  - a placeholder that the part-regex accepts (silently passing an undrafted flag) -> "placeholder_satisfies_gate"
  - any add.py/add_engine edit (the gate logic is untouched; template-only) -> "engine_touched"
</reject>
After:
<after>
  - a fresh task's §3 shows the flag slot at draft time; a first freeze with the slot properly filled succeeds (no unflagged_freeze retry); the tooling suite is green
</after>
Boundary: none — one static template line across 4 twins; the only "input" is the placeholder literal vs `_FLAG_PART_RE`.
<assumptions>
  ⚠ that no test pins the §3 region between the Persona line and `### AI-verify record` as EXACT bytes — if wrong: a template pin breaks. Mitigated: test_template_atomic pins a census LIST (additive-safe) and #38's relabel just touched the adjacent lines green.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Surface: PLAN.md.tmpl §3 (×4 twins) — ONE new line between the Persona line and `### AI-verify record`:

    Least-sure flag surfaced at freeze: [spec|scenario|contract|test] <the ONE part you trust least + why — REQUIRED at the freeze (unflagged_freeze); §1's top ⚠ usually feeds it>

Gate interaction (unchanged engine): _FLAG_LABEL_RE finds the label; _FLAG_PART_RE
(`\[(?:spec|scenario|contract|test)(?:/…)*\]`) does NOT match the literal part-menu
`[spec|scenario|contract|test]` (pipes are not in the pattern), so an unfilled slot
still refuses unflagged_freeze; a filled `[contract] …` passes as today.
Invariant: 4 template twins byte-identical · ZERO add.py/add_engine edit · ENGINE_MD5 + ENGINE_PKG_MD5 both UNCHANGED
```

Target (measurable): tooling suite green incl. new test_freeze_flag_slot (placeholder-never-matches proven against the LIVE `_FLAG_PART_RE` import, not a copy); a fresh scaffolded task shows the slot in §3. Boots: N/A — static template line.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered before this froze

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT
Scope (may touch): `add-method/tooling` `add-method/src/add_method/_bundled/tooling` `add-method/.add/tooling` `.add/tooling`   <the 4 tooling twins — templates/PLAN.md.tmpl + the new conformance test under add-method/tooling>
Regression floor: the tooling suite — test_template_atomic · test_bundle_parity · test_packaging · test_ship_clean · test_build_strategy_labels — must stay green
Persona (optional): `.add/personas/methodology-engine-dev.md` (template + pin discipline; advisory)

Least-sure flag surfaced at freeze: [test] that `_FLAG_PART_RE` truly rejects the part-menu literal `[spec|scenario|contract|test]` in every code path (the freeze gate must NOT be satisfiable by an undrafted template) — proven by a red test importing the LIVE regex from add.py, not by eyeballing the pattern.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — `_FLAG_LABEL_RE`/`_FLAG_PART_RE` (add.py:5769-5771), the Persona/AI-verify §3 anchors in all 4 PLAN.md.tmpl twins, engine_pin.ENGINE_MD5 all present
- [x] §1 every Must + every Reject present, each Reject paired with an error code — 4 Musts; Rejects `placeholder_satisfies_gate` · `engine_touched`
- [x] §3 Contract shape is concrete — the exact slot line + the regex non-match rationale + the byte-identical/zero-engine invariants; no `<...>` placeholders remain
- [x] Lowest-confidence flag surfaced and substantive — [test] the part-menu literal must never satisfy the live gate, proven by importing `_FLAG_PART_RE` from add.py (not a copy)
Verified by: claude-opus-4-8 (add-worker, direction beat) · at: 2026-07-23T13:29:42Z

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_flag_slot_present_and_placed: canon PLAN.md.tmpl §3 carries the `Least-sure flag surfaced at freeze:` line AFTER the Persona line and BEFORE `### AI-verify record` · covers: M1
  - test_placeholder_never_satisfies_gate: the LIVE `_FLAG_PART_RE` (imported from add.py) does NOT match the template's part-menu literal, and DOES match a filled `[contract]` form · covers: M2, M3, R:placeholder_satisfies_gate
  - test_template_twins_byte_identical: the 4 PLAN.md.tmpl twins are md5-equal · covers: M4
  - test_engine_untouched: add.py's md5 equals engine_pin.ENGINE_MD5 (no engine edit rode in) · covers: R:engine_touched
</test_plan>
Tests live in: `add-method/tooling/test_freeze_flag_slot.py` — red before the slot exists, green after.

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — red test first (slot-present RED, gate-regex/twins/engine-pin guards green), ONE line inserted into canon PLAN.md.tmpl §3 between Persona and AI-verify, 3 twins cp'd byte-identically, suite green. Zero engine edit; ENGINE_MD5 untouched. DOGFOOD: this task's own first freeze passed with no unflagged_freeze retry because its §3 carried the new slot.
Code lives in: `add-method/tooling/templates/PLAN.md.tmpl` (+ 3 twins)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — test_freeze_flag_slot 4/4; neighbors (template_atomic · build_strategy_labels · decide_digest · bundle_parity · packaging · ship_clean) 65/0
- [x] coverage did not decrease — net +4 conformance tests
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; the red suite predates the freeze
- [x] the green was EARNED, not gamed — slot-present ran RED before the insert; the gate test imports the LIVE _FLAG_PART_RE from add.py (a copied regex could drift green)
- [x] concurrency / timing of the risky operation is safe — N/A: one static template line
- [x] no exposed secrets, injection openings, or unexpected dependencies — template prose only
- [x] layering & dependencies follow CONVENTIONS.md — 4-twin parity held; ENGINE_MD5 asserted unchanged by the suite itself
- [x] a person reviewed and approved the change — sensitivity: mechanical, gate_mode: ai-plan-verify (sanctioned headless path)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self (add-worker, verify beat) · adversarially checked: (1) tried to make the placeholder pass the gate — `_FLAG_PART_RE.search("[spec|scenario|contract|test]")` is None against the LIVE import, so an undrafted freeze still refuses; (2) confirmed filled forms `[contract] …` AND `[contract/test] …` still pass (no accidental tightening); (3) this task's own freeze ran the REAL path: first freeze succeeded flag-first — the measured +1-call retry is gone at the source.

### GATE RECORD
Reported: yes — the gate report (banner/ARC) rendered before this outcome recorded
Outcome: PASS
Reviewed by: Tin Dang (AI-plan-verify, mechanical) · date: 2026-07-23

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose drafted-blank template slot whose UNFILLED placeholder still refuses; rejected weaken unflagged_freeze to a warning (rejected — inverts the flag-first-freeze floor) · put the hint only in the freeze error (rejected — that IS today's behavior, measured +1 call/rep)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — red test first (slot-present RED, gate-regex/twins/engine-pin guards green), ONE line inserted into canon PLAN.md.tmpl §3 between Persona and AI-verify, 3 twins cp'd byte-identically, suite green. Zero engine edit; ENGINE_MD5 untouched. DOGFOOD: this task's own first freeze passed with no unflagged_freeze retry because its §3 carried the new slot.
- [AI] verify — gate PASS (reviewed by Tin Dang (AI-plan-verify, mechanical))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
