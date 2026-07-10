# TASK: Never-defer invariants: entry-contract-class constraints pin into the seed lines

slug: never-defer-invariants · created: 2026-07-07 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small guide/template task; trust floor held.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): add-method/skill/add/phases/0-setup.md §3.1 "Seed, don't draft" (task 3's deferral — deferred one step too far) · add-method/tooling/templates/PROJECT.md.tmpl Domain section (living-marked) · 3 skill trees + 3 template trees · test_lightweight_setup.py (extends)
Context (working folder): Appendix C — lean rerun wm1/wm3 fidelity 0.0: agent chose uvicorn, green in .venv, dead under the frozen bare `python -m app` entry contract; the 4-lens interview ALREADY asks "the one invariant that must NEVER break" but the seed step didn't make it load-bearing
Honors (patterns / conventions): lean pool fences (small addition; 0-setup has −290B headroom from task 3) · 3-tree parity · trust floor untouched
Anchors the contract cites: 0-setup.md §3.1 · PROJECT.md.tmpl Domain header
Ground SHA: 67a2ae1

---

## 1 · SPECIFY — the rules

Feature: never-deferrable invariants in the seed lines
Must:
  - 0-setup.md §3.1 gains the invariant pin: the Domain-lens invariant AND any externally-imposed run/entry contract (how the artifact is EXECUTED/CONSUMED — interpreter, port, packaging, protocol) are written into PROJECT.md's `invariants:` seed line at setup — NEVER deferred, and every task's §0 GROUND re-states them.
  - PROJECT.md.tmpl gains an `invariants:` line (with a "never deferred" comment) directly under the Domain header, exempt from the living marker.
Reject:
  - none engine-enforced — guide/template truth; doc-pinning guards fixed forward
Accept: Given a fresh init, When PROJECT.md is read, Then it carries the `invariants:` seed line marked never-deferred; And 0-setup.md instructs pinning run/entry contracts there at setup.
Assumptions: ⚠ a one-line pin is enough to change headless-agent behavior — tested by the wm1/wm3 rerun; if wrong: the next iteration escalates it into the workspace CLAUDE.md block (engine sync-guidelines), cost one more task.

---

## 3 · CONTRACT — freeze the shape

```
0-setup.md §3.1 += "Pin invariants first — never defer: the Domain-lens 'never breaks'
  invariant and any imposed run/entry contract (how the artifact is executed/consumed:
  interpreter · port · packaging · protocol) go into PROJECT.md `invariants:` NOW;
  every task §0 GROUND re-states them. Deferral applies to everything else."
PROJECT.md.tmpl (under ## Domain header, above the living marker):
  invariants:
  <!-- never deferred — pin the run/entry contract + the one domain invariant at setup;
       every task §0 re-states these -->
```

`Least-sure flag surfaced at freeze:` [test] behavior-change is only provable by the rerun (task-level tests can only pin the text); if the rerun still fails, the pin escalates to the CLAUDE.md sync block.
Status: FROZEN @ v1 — approved by Tin Dang ("yes" to running this iteration; shape rendered in the proposal)

---

## 4 · TESTS — failing-first (red)

Plan: extend test_lightweight_setup.py — test_invariants_seed_line_on_init (fresh init: `invariants:` + never-deferred comment under Domain) · test_setup_guide_pins_invariants ("Pin invariants first" + run/entry-contract wording + §0 re-statement rule) · parity tests already cover trees.
Tests live in: `add-method/tooling/test_lightweight_setup.py` · `add-method/skill/add/intake.md` · `.claude/skills/add/intake.md` · `add-method/src/add_method/_bundled/skill/add/intake.md` · `add-method/tooling/engine_pin.py` · `CLAUDE.md.bak` · `AGENTS.md.bak` · `.clinerules.bak` · `tmp/` · `benchmark/runs/` · red pre-build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add_engine/guidelines.py` · `.add/tooling/add_engine/guidelines.py` · `add-method/src/add_method/_bundled/tooling/add_engine/guidelines.py` · `CLAUDE.md` · `AGENTS.md` · `.clinerules` · `add-method/skill/add/phases/0-setup.md` · `.claude/skills/add/phases/0-setup.md` · `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md` · `add-method/tooling/templates/PROJECT.md.tmpl` · `.add/tooling/templates/PROJECT.md.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/PROJECT.md.tmpl` · `add-method/tooling/test_lightweight_setup.py`
Strategy & known-problem fixes: insert above the living marker so the marker's first-touch semantics stay untouched · pool headroom check.
Strategy actually used: <fill at verify>
Code lives in: guide/template text · Constraints: no engine change; no test weakened.

---

## 6 · VERIFY — evidence + gate

- [x] new tests green; fences green; trees in parity — full tooling suite 3202 tests, sole failure is the fresh-checkout CI mirror (tests HEAD; clears on this commit)
- [x] rerun evidence: wm3 (fresh workspace, escalated CLAUDE.md block) fidelity 0.00 → 0.95 (median 0.95;0.92;0.97), 1.06M tokens vs 4.03M baseline; wm1/wm2 carried from lean-r2 (0.95 / 0.92) — full lean loop 4.36M vs 20.5M (−79%), all within the ±0.05 band; regression 0.67 identical to baseline (known wm1-re-export workload artifact)

Build expectations (from §1 Accept + §3 CONTRACT): fresh init shows the invariants seed line; guide pins run/entry contracts at setup — confirmed by tests + the rerun records.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08
