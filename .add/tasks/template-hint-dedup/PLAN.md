# TASK: template hints demand distinct content: kill §5/§6/exit-criteria restatement

slug: template-hint-dedup · created: 2026-07-14 · stage: mvp
milestone: call-residuals
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: template hints demand DISTINCT content — three fast-lane §5/§6 placeholder hints + the milestone Exit-criteria hint are tightened so the agent writes each field's OWN content instead of restating text already frozen upstream (§1 Accept, §3 Strategy, the task's plan line). Kills the measured restatement class the recent TASK.md files showed (this session's own tasks wrote §5 Approach as a Strategy-stance echo and §6 Build-expectations as an Accept paraphrase). NON-weakening: every gate (build-expectations-gate, goal_auto_ready) keeps firing — only the guidance value changes.
Must:
  - fast `TASK.fast.md.tmpl` §5 `Approach (domain strategy):` hint asks for a ≤6-word domain-technique TAG and says it is NOT a restatement of the Strategy above
  - fast §5 `Strategy actually used:` hint asks for "as planned" or ONLY the divergences from §3 Strategy (don't re-narrate it)
  - fast §6 `Build expectations` hint asks for the CONCRETE observable (printed line / exit code / file byte you can SEE) and says NOT a paraphrase of §1 Accept — the `### Build expectations` gate still fires on an unfilled `<…>` placeholder (unchanged)
  - `MILESTONE.md.tmpl` `## Exit criteria` hint asks for the SEEN outcome only, NOT the task's plan line (the `(← <slug>)` mapping stays)
  - LABELS + the `(from §1 Accept + §3 CONTRACT)` / `(← <slug>)` structure byte-unchanged; canonical == bundle for both templates
Reject:
  - none — documentation-string change only; no code path, parser, or gate altered (milestone OUT-of-scope). The build-expectations gate + goal_auto_ready gate must stay green unchanged
Accept: Given the fast TASK template and the MILESTONE template, When an agent reads §5/§6 and the Exit-criteria hint, Then each hint demands the field's distinct/concrete content (technique tag · divergences-only · a SEEN observable not an Accept paraphrase · the observed outcome not the plan line), so no field restates frozen upstream text
Boundary: none — static template text asserted by string-presence; no external input shape
Assumptions: ⚠ tightening the HINT (not adding a gate) is enough to change agent behavior — evidence: the deduped Touches/Scope hint from the prior task already scaffolded correctly into THIS task; if wrong (agents still restate): no harm, the gates are untouched and it stays pure guidance

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): the 4 placeholder-hint lines — `TASK.fast.md.tmpl:Approach`/`:Strategy-actually-used`/`:Build-expectations` + `MILESTONE.md.tmpl:Exit-criteria`; no engine symbol edited (pure template text)
Context (working folder): `add-method/tooling/templates/` (canonical). The full write-set — fast TASK template + milestone template, both bundle twins, the two gitignored dogfood twins, the new test — is the §5 Scope below
Honors (patterns / conventions): the [[template-touches-scope-dedup]] recipe just applied — reword only the `<…>` VALUE, keep LABELS byte-frozen; test_bundle_parity holds canonical==bundle; the full `TASK.md.tmpl` §6 `### Build expectations` block already says "evidence you can SEE, not test names" (unchanged — the redundancy is fast-lane-only)
Anchors the contract cites: the 4 hint VALUES (edited) · the build-expectations gate (add.py:1446, unchanged) · goal_auto_ready (unchanged) · test_bundle_parity
Ground SHA: cfe7f5a — stamped by freeze

### Contract

```
TASK.fast.md.tmpl §5 `Approach (domain strategy):`  → hint VALUE demands a ≤6-word technique TAG, "NOT a restatement of the Strategy above"
TASK.fast.md.tmpl §5 `Strategy actually used:`      → hint VALUE demands "as planned" or ONLY divergences ("don't re-narrate")
TASK.fast.md.tmpl §6 `Build expectations (…):`      → hint VALUE demands a CONCRETE SEEN observable, "NOT a paraphrase of §1 Accept"
MILESTONE.md.tmpl `## Exit criteria` `- [ ]` line   → hint VALUE demands the SEEN outcome only, "NOT the task's plan line"; the `(← <slug>)` mapping stays
INVARIANTS (unchanged):
  → LABELS + the `(from §1 Accept + §3 CONTRACT)` and `(← <slug>)` structure byte-identical
  → no engine/gate change: build-expectations gate (add.py:1446) still fires on unfilled `<…>`; goal_auto_ready unchanged
  → canonical == bundle for BOTH templates (test_bundle_parity green)
```

`Least-sure flag surfaced at freeze:` [contract] the exact hint wording — pure guidance text, cosmetic; the only hard edge is keeping the `<…>` wrapper (so the build-expectations gate still detects the shipped placeholder as unfilled) + the labels byte-identical.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/templates/TASK.fast.md.tmpl` `add-method/tooling/templates/MILESTONE.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/MILESTONE.md.tmpl` `add-method/tooling/test_template_hint_dedup.py` `add-method/tooling/test_strategy_facets.py`
Strategy & known-problem fixes: (1) RED first: new test_template_hint_dedup asserts the 4 hint VALUES carry their distinct-content phrase ("NOT a restatement" · "divergences"/"don't re-narrate" · "NOT a paraphrase"/"SEE" · "NOT the task's plan line") across both tracked template trees — RED now. (2) reword the 4 `<…>` values, keeping LABELS + `<…>` wrapper + `(← <slug>)`/`(from …)` structure (trap: the build-expectations gate detects `<…>` placeholders — keep the wrapper or the shipped template reads as "filled" and the gate stops firing). (3) sync ×4 twins per template (2 tracked + 2 gitignored). No add.py edit → NO ENGINE_MD5/SEAMS change.
Approach (domain strategy): doc-layer hint-tighten, gate-preserving

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned for the 4 rewords; ONE unplanned ripple caught by the full fence — `test_strategy_facets.py:FAST_FACET_LINE` pinned the exact OLD Approach placeholder (a value-pin my §3 Grounding missed). Migrated that constant to the new Approach text (still one collapsed line, same §5 position — the facets fast-collapse invariant holds; a pin migration, NOT a weakening), widened §5 Scope to cover it, re-crossed. Reworded the 4 `<…>` hint values, kept labels + `<…>` wrapper + `(from…)`/`(← slug)`, synced ×4 twins per template. No engine edit.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (full fence)
- [x] green was EARNED — the 4 hint-content asserts RED first, gate-placeholder + parity green throughout; GREEN only after the reword
- [x] input dialect held — the test speaks the real template placeholder dialect (label + `<…>` value)
- [x] no exposed secrets, injection openings, or unexpected dependencies (pure template text; security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): grep of `templates/TASK.fast.md.tmpl` prints "NOT a restatement" on the Approach line, "diverged"+"don't re-narrate" on Strategy-actually-used, "NOT a paraphrase"+"SEE" on Build-expectations; `templates/MILESTONE.md.tmpl` prints "NOT the task's plan line" on the exit-criteria line; each still wraps a `<…>` placeholder and canonical==bundle — confirmed by test_template_hint_dedup (6 asserts) + test_build_expectations_gate + test_bundle_parity green in the full fence.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

