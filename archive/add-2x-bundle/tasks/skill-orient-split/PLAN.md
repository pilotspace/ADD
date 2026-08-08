# TASK: Split SKILL.md: lean orient core + on-demand beyond.md routing guide

slug: skill-orient-split · created: 2026-07-13 · stage: mvp
milestone: call-floor
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: skill orient split — SKILL.md (12819B, read EVERY task) carries ~4.6KB of on-demand routing prose ("Beyond the bundle" verbose bullets) that most tasks never take; it moves to a new on-demand guide `beyond.md`, SKILL.md keeps a compact one-line-per-trigger index (fast-lane read path drops ~3.8KB toward the <=30KB criterion)
Must:
  - SKILL.md <= 9500 bytes; the "Beyond the bundle" section survives as a compact index naming ALL 17 pinned on-demand pointers (test_skill_lean.ON_DEMAND_POINTERS) plus `beyond.md`
  - `beyond.md` (canonical skill/add/, synced x3) carries the full moved routing prose: run/streams/advisor/confidence spawn lane · fast lane · UDD design loop · milestone loop · graduate · release · components pillar · persona loop · sensitivity classes
  - pinned structure holds: phase-guide table rows · banner-cue pipeline sentence · question-summary line · SOUL.md within 1200 chars of "Always start here" · "## Depth by stage" + "## The method rationale" sections stay (test_graduate_guard, test_xml_convention)
  - core pool absorbs `beyond.md` in its guides list; the NET new surface (index + file header) rebaselines core by surface/0.88 per the documented "rebaseline for human-approved new surface" method, comment citing this frozen contract; wording-lint file-count pin 31 -> 32 (declared doc-truth ripples)
Reject:
  - any on-demand pointer name dropped from SKILL.md -> test_skill_lean.test_core_pointers_present red (pin, unchanged)
  - `beyond.md` missing from any of the 3 trees -> parity suites red (rglob, unchanged)
Accept: Given the split ships, When the skill orients a task, Then it reads a <=9500B SKILL.md whose Beyond index routes each trigger to its guide, and the full routing prose loads only on demand from beyond.md — all existing structural pins green.
Boundary: none — no external input (a docs/test restructure; the byte ceilings are the format surface)
Assumptions: ⚠ an unseen suite pins a moved SENTENCE (not header) to SKILL.md — why: ~20 suites grep SKILL.md and I audited by phrase-class, not exhaustively; if wrong: the fence names it, the pin updates-or-the-sentence-stays (cost: one re-run)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/skill/add/SKILL.md (split) · add-method/skill/add/beyond.md (new) · add-method/tooling/test_skill_lean.py:POOLS core guides + rebaseline comment · add-method/tooling/test_wording_lint.py:31-count pin · twin trees add-method/src/add_method/_bundled/skill/add/ + .claude/skills/add/
Context (working folder): no engine change — ENGINE_MD5 untouched; SEAMS pin untouched
Honors (patterns / conventions): rebaseline-for-human-approved-surface method (POOLS comments precedent) · sync guides x3 never tests · pinned phrases reworded AROUND, never dropped
Anchors the contract cites: ON_DEMAND_POINTERS · POOLS · surface_files
Ground SHA: d8e1718 — stamped by freeze

### Contract

```
SKILL.md: "## Beyond the bundle — load on demand" ->
    one intro line pointing at `beyond.md` + a compact index, one line per trigger,
    each backticking its guide (all 17 ON_DEMAND_POINTERS present); total file <= 9500B
beyond.md: frontmatter-free guide; the moved verbose bullets verbatim-modulo-lead-in
    (frozen-scope prose like "Collapse, never skip" keeps its wording)
test_skill_lean.POOLS core: guides ["SKILL.md", "intake.md", "beyond.md"];
    baseline 20666 + ceil(net_surface/0.88), comment cites task skill-orient-split FROZEN @ v1
test_wording_lint count: 31 -> 32 ("+beyond.md @ skill-orient-split")
new test_skill_orient_split.py: size ceiling · index completeness · beyond.md content markers
```

`Least-sure flag surfaced at freeze:` [test] the 9500B ceiling — why: chosen from the current 12819B minus the measured moved span, not from a rendered rebuild; if wrong the split still ships but the ceiling pins loose/tight: re-measure once at build and amend the ceiling IN the tests phase (sanctioned step-back), never post-gate
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/skill/` `add-method/tooling/` `add-method/src/add_method/_bundled/skill/` `add-method/../.claude/skills/add/`
Strategy & known-problem fixes: red tests -> write beyond.md + rewrite SKILL.md section -> pools/count pin updates -> sync x3 -> fence. Traps: 17 pointers backticked in SKILL.md (index covers) · "Depth by stage"/"method rationale" headers stay · banner sentence byte-exact · SOUL within 1200 of "Always start here" (index sits AFTER that region) · net-surface math measured, not estimated.
Approach (domain strategy): progressive disclosure — orient stays, routing prose loads on demand

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (ON_DEMAND_POINTERS/POOLS/surface_files + both structural pins read this session)
- [x] §1 every Must + every Reject present, each paired with its outcome
- [x] §3 Contract shape is concrete
- [x] Lowest-confidence flag surfaced and substantive (the 9500B ceiling derivation)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T17:40:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_skill_under_size_ceiling · test_beyond_exists_with_moved_markers · test_index_names_every_pointer_plus_beyond · test_moved_prose_left_skill (no duplicate verbose bullets).
Tests live in: `add-method/tooling/test_skill_orient_split.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (one sanctioned tests-phase step-back to exempt the pinned "persona loop" from my own no-duplication assert)
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): SKILL.md <= 9500B (landed 9498) with the Beyond section as a compact index keeping all 17 pinned pointers + beyond.md; beyond.md carries the full routing prose, synced x3 — confirmed by test_skill_orient_split.py (5 tests) RED 5/5 then green, plus the pin battery (131 tests: pools/wording/graduate/xml/banner/question/arc/soul/parity/persona/docs-align/per-step-hooks/phase-bundles) and full fence 3508/3508 OK exit 0 (r2 log). Fence r1 surfaced 2 more phrase/count pins (agent-call-preferred + default execution mode; wording surface 31->32) — both restored/updated as declared doc-truth ripples. Core pool rebaselined 20666->20906 for +211B net new surface per the documented method, comment cites this frozen contract. No engine change: ENGINE_MD5 untouched.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

