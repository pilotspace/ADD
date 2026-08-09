# PLAN: Relabel §3 Build-strategy: Scope is HARD scope-lock, Strategy/Approach SOFT; Regression+Persona optional

slug: trim-build-strategy-labels · created: 2026-07-23 · stage: mvp
milestone: build-strategy-trim
autonomy: auto
phase: done
sensitivity: mechanical
gate_mode: ai-plan-verify
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Relabel the §3 Build-strategy block so `Scope (may touch)` reads as the HARD, tamper-guarded scope-lock while Strategy · Approach · Regression floor · Persona read as SOFT/optional — a pure label change across the 4 PLAN.md.tmpl twins + the engine's `_PLAN_FIELDS` recognizer, with backward-compat so already-frozen tasks (authored `Persona (required):`) still surface.
Framings weighed: relabel-in-place, machine-read prefixes preserved (chosen — the `Scope (may touch):`/`Regression floor:` prefixes are keyed by scope-lock + the inherited-floors census; renaming them would ripple ~coupled tests; only the human-facing framing and the `Persona (required→optional)` word change) · rename-the-prefixes (rejected — churns test_template_atomic + the scope-lock parser for zero user gain)
Must:
<must>
  - PLAN.md.tmpl §3 Build-strategy header states `Scope (may touch)` is the HARD scope-lock and the remaining fields are SOFT/optional
  - The Persona field label reads `Persona (optional):` (was `Persona (required):`) in all 4 template twins
  - The `Scope (may touch):` and `Regression floor:` machine-read prefixes survive verbatim (scope-lock + inherited-floors census still resolve)
  - Engine `_PLAN_FIELDS` recognizes `Persona (optional)`; a legacy task authored `Persona (required):` still surfaces its Persona at the freeze digest (backward-compat fallback in `_build_plan`)
  - All 4 PLAN.md.tmpl twins remain byte-identical
</must>
Reject:
<reject>
  - a relabel that drops or renames the `Scope (may touch):` prefix -> "scope_lock_prefix_lost"
  - template twins diverging (not byte-identical) -> "twin_drift"
</reject>
After:
<after>
  - new tasks scaffold with `Persona (optional):` and a Scope-is-HARD header; the freeze digest surfaces Persona for BOTH new (optional) and legacy (required) tasks; the full tooling suite is green
</after>
Boundary: none — no external input; the surfaces are 4 static template files + one engine tuple (`_PLAN_FIELDS`) + its parser (`_build_plan`).
<assumptions>
  ⚠ that no OTHER live engine/test surface keys on the literal `Persona (required)` beyond `_PLAN_FIELDS` and test_decide_digest — if wrong: a hidden consumer silently drops the Persona line. Mitigated: a full-repo grep found only these two live sources; every other hit is a frozen historical `.add/tasks/*/PLAN.md` (never re-parsed).
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Surface: §3 Build-strategy block of PLAN.md.tmpl (×4 twins) + `_PLAN_FIELDS` / `_build_plan` in add.py
  §3 header       -> "### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)"
  Scope prefix    -> "Scope (may touch):"   (PRESERVED verbatim — machine-read scope-lock; hint reworded to say HARD)
  Regression pfx  -> "Regression floor:"    (PRESERVED verbatim — inherited-floors census; hint reworded to say optional)
  Persona label   -> "Persona (optional):"  (WAS "Persona (required):")
  Engine tuple    -> _PLAN_FIELDS holds "Persona (optional)"; _build_plan falls back to legacy "Persona (required):" so frozen tasks still surface
  Trailing note   -> "Contract + Scope (may touch) = HARD (tamper-guarded); Strategy · Regression floor · Persona = SOFT/optional"
Invariant: 4 template twins byte-identical · ENGINE_MD5 repinned (add.py changed) · ENGINE_PKG_MD5 UNCHANGED (add_engine/ untouched)
```

Target (measurable): full tooling suite green (test_decide_digest · test_template_atomic · new test_build_strategy_labels · test_bundle_parity · test_packaging · test_ship_clean); `grep -rn "Persona (required)"` over live sources (templates + tooling *.py) returns 0 hits (only frozen `.add/tasks/*/PLAN.md` history remains). Boots: N/A — static files + one tuple.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered before this froze

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT
Scope (may touch): `add-method/tooling` `add-method/src/add_method/_bundled/tooling` `add-method/.add/tooling` `.add/tooling`   <the file write-set: the 4 tooling twins — add.py · templates/PLAN.md.tmpl · test_decide_digest.py · engine_pin.py, plus the new conformance test>
Regression floor: the tooling suite — test_decide_digest · test_template_atomic · test_bundle_parity · test_packaging · test_ship_clean — must stay green
Persona (optional): `.add/personas/methodology-engine-dev.md` (deterministic engine + template relabel with pin discipline; advisory, never lowers a gate)

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — `_PLAN_FIELDS`/`_build_plan` (add.py:5814), the 4 PLAN.md.tmpl §3 Build-strategy blocks, test_decide_digest.py, engine_pin.py all present and cited by symbol
- [x] §1 every Must + every Reject present, each Reject paired with an error code — 5 Musts; Rejects `scope_lock_prefix_lost` · `twin_drift`
- [x] §3 Contract shape is concrete (no template placeholder text remains) — the Surface block names exact literal labels + the byte-identical/pin invariants, no `<...>`
- [x] Lowest-confidence flag surfaced and substantive — ⚠ "no OTHER live surface keys on `Persona (required)`" resolved by full-repo grep (only `_PLAN_FIELDS` + test_decide_digest live; rest is frozen task history)
Verified by: claude-opus-4-8 (add-worker, direction beat) · at: 2026-07-23T09:36:36Z

Least-sure flag surfaced at freeze: [spec] that no OTHER live surface keys on the literal `Persona (required)` beyond `_PLAN_FIELDS` and test_decide_digest — if wrong, a hidden consumer silently drops the Persona line at some freeze. Mitigated: a full-repo grep over `*.py`/`*.tmpl` found only these two live sources; every other hit is a frozen historical `.add/tasks/*/PLAN.md` (never re-parsed), and `_build_plan` keeps a legacy `Persona (required):` fallback so even those still surface.

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_persona_label_is_optional: canon PLAN.md.tmpl §3 contains `Persona (optional):` and NOT `Persona (required):` · covers: M2
  - test_scope_and_regression_prefixes_preserved: canon PLAN.md.tmpl still contains `Scope (may touch):` and `Regression floor:` verbatim · covers: M3, R:scope_lock_prefix_lost
  - test_header_marks_scope_hard: the §3 `### Build-strategy` header line names `Scope (may touch)` as HARD scope-lock · covers: M1
  - test_template_twins_byte_identical: the 4 PLAN.md.tmpl twins are md5-equal · covers: M5, R:twin_drift
  - test_engine_recognizes_optional: `_PLAN_FIELDS` in add.py contains `"Persona (optional)"` · covers: M4
  - test_legacy_persona_still_surfaces: `_build_plan` on a raw3 authored with `Persona (required): generic` returns a Persona row (backward-compat fallback) · covers: M4
</test_plan>
Tests live in: `add-method/tooling/test_build_strategy_labels.py` (the tooling suite dir) — a static-surface conformance suite (drift-stable pins of the achieved labels), red before the relabel, green after.

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — relabel-in-place with the machine-read prefixes preserved. Edited canon `add.py` (`_PLAN_FIELDS` Persona required→optional + `_build_plan` legacy fallback) and canon `templates/PLAN.md.tmpl` (§3 header names Scope HARD · Scope/Regression hints reworded · Persona label optional · trailing note); propagated both to the 3 tooling twins byte-identically; updated `test_decide_digest.py` (4 label occurrences); wrote the `test_build_strategy_labels.py` conformance suite; repinned `ENGINE_MD5` = 868bd79b… (add.py changed) across 4 engine_pin.py twins; `ENGINE_PKG_MD5` untouched (no add_engine/ edit).
Code lives in: `add-method/tooling/` (+ 3 tooling twins)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite): full tooling suite **2253 passed, 0 failed** (218.8s); `add.py check` 366/0; conformance suite test_build_strategy_labels 6/6
- [x] coverage did not decrease — a net +6 conformance tests; no test removed
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; test_decide_digest updated in DIRECTION (before freeze) as the red-suite alignment, not during build
- [x] the green was EARNED, not gamed — the 3 label/engine assertions ran RED before the relabel, GREEN after; the backward-compat test drives `_build_plan` on a real legacy-shaped raw3 (not a stubbed return)
- [x] concurrency / timing of the risky operation is safe — N/A: static file edits + one pure tuple/parser; no IO, no concurrency
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib-only; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — 4-way tooling twin sync held (all 4 add.py/template/engine_pin byte-identical); ENGINE_MD5 repinned, ENGINE_PKG_MD5 correctly untouched (add_engine/ not edited)
- [x] a person reviewed and approved the change — sensitivity: mechanical, gate_mode: ai-plan-verify; AI-self-verified per the sanctioned headless path (no security/data/architecture surface)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self (add-worker, verify beat) · adversarially checked: (1) tried to break the backward-compat claim — confirmed `_build_plan` still surfaces a legacy `Persona (required):` line via the fallback branch, so no frozen historical task loses its Persona; (2) confirmed the machine-read `Scope (may touch):`/`Regression floor:` prefixes survive verbatim (test_template_atomic census still green) so scope-lock + inherited-floors are intact; (3) full-repo grep proved 0 live `Persona (required)` consumers remain outside frozen `.add/tasks/` history.

### GATE RECORD
Reported: yes — the gate report (banner/ARC) rendered before this outcome recorded
Outcome: PASS
Reviewed by: Tin Dang (AI-plan-verify, mechanical) · date: 2026-07-23

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose relabel-in-place, machine-read prefixes preserved; rejected rename-the-prefixes (rejected — churns test_template_atomic + the scope-lock parser for zero user gain)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — relabel-in-place with the machine-read prefixes preserved. Edited canon `add.py` (`_PLAN_FIELDS` Persona required→optional + `_build_plan` legacy fallback) and canon `templates/PLAN.md.tmpl` (§3 header names Scope HARD · Scope/Regression hints reworded · Persona label optional · trailing note); propagated both to the 3 tooling twins byte-identically; updated `test_decide_digest.py` (4 label occurrences); wrote the `test_build_strategy_labels.py` conformance suite; repinned `ENGINE_MD5` = 868bd79b… (add.py changed) across 4 engine_pin.py twins; `ENGINE_PKG_MD5` untouched (no add_engine/ edit).
- [AI] verify — gate PASS (reviewed by Tin Dang (AI-plan-verify, mechanical))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
