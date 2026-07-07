# TASK: worker-contract persona block names flow preference

slug: streams-persona-flow · created: 2026-07-07 · stage: mvp
milestone: delta-drain
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): skill/add/streams.md worker-contract `<persona>` block, lines ~175–189 (3 skill trees: add-method/skill · .claude/skills · _bundled/skill)
Context (working folder): advisor.md (the pin-locked byte-identical `<strategy>` twin — line 37 already teaches flow-first selection) · test_skill_dedup.py + test_loop_surfacing_nudges.py (the BINDING 41300 orchestration floor, current bytes 41258 = 42 B headroom)
Honors (patterns / conventions): streams.md `<strategy>` block byte-identical vs advisor.md is a pin-locked floor (test_streams / test_xml_convention) · lean-over-budget-bump: absorb new surface by in-file compression, no rebaseline · v16 XML closed tag vocab (no new tags)
Anchors the contract cites: the `<persona>` block · the `<strategy>` twin-pin · the 41300 dedup floor
Ground SHA: a1cfd6a

---

## 1 · SPECIFY — the rules

Feature: the streams.md worker-contract `<persona>` block could also name flow: preference — deferred to keep the pin-locked `<strategy>` floor untouched (from persona-flow-routing spec-delta)
Must:
  - the worker-contract `<persona>` block carries a flow-preference sentence (frozen in §3): select by frontmatter flow first, matched to the worker's step (build worker -> flow: build · verify refute-read -> flow: verify), then use-when
  - the `<strategy>` block stays BYTE-IDENTICAL between streams.md and advisor.md (no character inside it moves)
  - the orchestration dedup floor holds: pool bytes <= 41300 — the added sentence is paid for by in-file compression elsewhere in streams.md
  - 3 skill trees lockstep (md5-identical streams.md)
Reject:
  - (prose-only task — no runtime rejects; a would-be `<strategy>` edit is the tripwire the twin-pin test rejects)
Accept: Given the worker contract, When a build or verify worker is spawned from streams.md, Then its `<persona>` block instructs flow-first selection naming build and verify, and the `<strategy>` block md5 equals advisor.md's.
Assumptions: ⚠ 42 B headroom + in-file compression is enough (no rebaseline needed) — if wrong: compress harder or escalate to a contract-signed rebaseline (human decision), moderate cost

---

## 3 · CONTRACT — freeze the shape

```
new sentence INSIDE <persona>, directly after the "Load `.add/personas/…`" load instruction:
  "Select by frontmatter flow first, matched to this worker's step (build worker -> flow: build ·
   verify refute-read -> flow: verify), then use-when; read ONE body."
invariants: <strategy> block byte-identical streams.md == advisor.md · orchestration pool <= 41300 B
            · 3 skill trees md5-lockstep · no new XML tag
```

`Least-sure flag surfaced at freeze:` [contract] the sentence's exact wording vs the pool math — it may need trimming during build to fit 41300; wording (not meaning) may re-flow; if wrong: cheap re-freeze of one sentence
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first (red)

Plan: test_streams_persona_flow.py — flow sentence inside `<persona>` naming build+verify (Accept) · `<strategy>` md5 streams == advisor · pool <= 41300 · 3-tree lockstep · sentence sits INSIDE the persona block (between its open/close tags).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/skill/` `.claude/skills/` `add-method/src/add_method/_bundled/skill/` `add-method/tooling/`
Strategy & known-problem fixes: (1) red test first (2) measure the sentence's exact byte cost (3) compress non-pinned streams.md prose by >= that cost minus 42 B headroom — NEVER inside `<strategy>` (4) insert the sentence, sync 3 trees (5) run dedup+lean suites before claiming green
Approach (domain strategy): additive one-sentence contract prose · byte-ledger compression inside the same file · pin-floor untouchable (twin md5) · token-cost-first (41300 hard floor)
Strategy actually used: as planned + the sentence re-flowed for byte cost (the freeze's anticipated trim: 'flow first'->'flow', 'build worker'->'build'; meaning intact) and the whole-tree lean fence (145974) forced 26 B extra reclaim beyond the 41300 pool floor
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [ ] all tests pass · coverage held · no test or contract altered during build
- [ ] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [ ] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): worker <persona> block teaches flow-first selection naming flow: build + flow: verify; <strategy> md5 streams==advisor; pool<=41300; 3 trees lockstep — confirmed by test_streams_persona_flow (5 green) + 83-test guard run

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07

