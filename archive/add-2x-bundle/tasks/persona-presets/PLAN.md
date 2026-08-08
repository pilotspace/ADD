# TASK: Per-phase teacher-grade persona presets on the roster

slug: persona-presets · created: 2026-07-14 · stage: mvp
milestone: six-phase-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: persona-presets — per-phase teacher-grade persona PRESETS on the lean roster (six-phase-loop 5/6, the user's interview decision: per-phase expertise via presets, NOT a per-step agent rebuild): each bundle agent's no-persona fallback upgrades from one thin generic line to a named expert stance PER OWNED PHASE, marked `Preset (<phase>):`
Must:
  - add-design.md carries `Preset (specify):` and `Preset (plan):` lines (a setup preset rides the specify one) — each names a concrete expert stance + its working rule in one line
  - add-build.md carries `Preset (tests):` and `Preset (build):` lines
  - add-verify.md carries a `Preset (verify):` line that spans the gate AND the post-gate Observe duties
  - the preset is the FALLBACK tier only: the project-persona selection stays first (the existing `flow:` routing prose is untouched above the presets); the preset never blocks and never lowers a gate
  - agents sync canonical -> _bundled byte-identical + .claude refresh
Reject:
  - a preset that overrides the project-persona routing (the `flow:` selection sentence removed or demoted) -> the routing-first pin goes red
  - banned idiom in preset prose (the wording-lint sweeps agents? if not: the fence's own census) -> lint red
Accept: Given a spawn with no project persona seeded or matched, When the bundle agent reads its persona section, Then it finds a named per-phase expert stance (not a bare "generic engineer") for every phase it owns.
Boundary: none — no external input (agent prose only; engine untouched)
Assumptions: ⚠ the wording-lint surface may not cover agents/ (its census is skill/add + appendix) so banned-idiom discipline is manual here — why: POOLS/census read skill trees only; if wrong (agents ARE swept): the fence names the exact line (cost: one round)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/agents/add-design.md · add-build.md · add-verify.md ("Become the persona" sections, fallback sentence -> preset lines) · _bundled/agents twins · .claude/agents copies
Context (working folder): engine untouched; test_bundle_disclosure + test_roster_shipped parity pins bind; the vendored teacher library (.add/personas-teacher/) is the STANCE SOURCE the presets distill, not a runtime read
Honors (patterns / conventions): teacher-not-runtime personas (persona-learning-loop) · presets advisory, never lowers a gate · banned-slang list (no "blast radius", no "least-sure" as a bare token)
Anchors the contract cites: add-design.md · add-build.md · add-verify.md persona sections
Ground SHA: e3e0164 — stamped by freeze

### Contract

```
Each "Become the persona" section's fallback sentence ("No persona seeded or
matched? Use a generic ...") is REPLACED by per-phase preset lines:
  add-design.md:
    Preset (specify): a domain analyst (15y) who asks rather than assumes —
      every Reject earns a named error code; setup rides this stance
    Preset (plan): a systems architect — contract-first, names the real
      anchors, sizes the change's reach before freezing scope
  add-build.md:
    Preset (tests): a test engineer — red for the RIGHT reason, one test per
      scenario, behavior not internals
    Preset (build): an implementation engineer — smallest honest diff, small
      reviewable batches, never touches a test
  add-verify.md:
    Preset (verify): an adversarial reviewer then reliability analyst —
      refutes the green before trusting it, then watches reality (§7)
Common tail on each block: presets are the no-persona FALLBACK tier —
  project personas route first; a preset never blocks and never lowers a gate.
NEW test_persona_presets.py pins: per-agent preset census (every owned phase)
  · routing-first sentence survives · no bare "generic <role>" fallback left
  · parity x2
```

`Least-sure flag surfaced at freeze:` [contract] the preset wording vs the wording-lint banned list — why: agent prose has tripped surface registries before (method-ergonomics lesson) and the banned list is only greppable, not enumerated here; if wrong: the fence names the exact banned token, reword (cost: one round)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/agents/` `add-method/src/add_method/_bundled/agents/` `.claude/agents/` `add-method/tooling/` `.add/tooling/` `add-method/.add/`
Strategy & known-problem fixes: red test_persona_presets -> replace the three fallback sentences with preset blocks -> sync x2 twins + .claude -> fence. Traps: add-verify's fallback sentence is LONG (severity-convention prose rides it — replace ONLY the trailing "No persona seeded or matched?" sentence) · parity pins re-check bytes.
Approach (domain strategy): distill the teacher library's stances into one-line presets; fallback tier only, routing untouched

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (all three persona sections read this session)
- [x] §1 every Must + every Reject present, each paired with its outcome
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (the banned-token wording risk)
Verified by: claude-fable-5 (orchestrator, inline) · at: 2026-07-14T02:50:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_each_agent_carries_a_preset_per_owned_phase · test_routing_first_sentence_survives · test_no_bare_generic_fallback_left · test_presets_synced_x2.
Tests live in: `add-method/tooling/test_persona_presets.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — the three fallback sentences swapped for preset blocks in place (add-verify's long severity-convention prose untouched above its trailing sentence, exactly as the strategy's trap note called); zero fence ripple.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): with no project persona seeded/matched, each bundle agent finds a named per-phase expert stance (design: specify+plan · build: tests+build · verify: verify spanning §7) instead of a bare generic line; the routing-first sentence and the never-blocks/never-lowers floor survive verbatim — confirmed by test_persona_presets 4/4 (3 red first) + the FULL fence 3545 tests OK / REAL_EXIT=0 (fence-pp-r1.log, zero ripple, zero weakened). Engine untouched.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

