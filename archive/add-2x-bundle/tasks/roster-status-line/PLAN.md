# TASK: engine-rendered persona roster line in status/check

slug: roster-status-line · created: 2026-07-07 · stage: mvp
milestone: delta-drain
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): add-method/tooling/add.py status renderer (~line 2110, the persona-hint slot) + check persona walk (~line 3153) + a new pure roster helper · add.py trio twins · engine_pin.py:ENGINE_MD5 (re-pin)
Context (working folder): .add/personas/*.md frontmatter (name · vibe · flow) · add_engine/io_state.py:_real_persona_slugs + _personas_unseeded (the existing fail-soft listing this builds on — imported, not changed)
Honors (patterns / conventions): presentation-only, existence-gated — a persona-less project's output is byte-identical (fast-lane-marker precedent) · fail-soft reads (unreadable file never raises) · advisory, never a gate
Anchors the contract cites: _real_persona_slugs · the status persona-hint slot · the check personas walk
Ground SHA: a1cfd6a

---

## 1 · SPECIFY — the rules

Feature: if agents keep whole-roster reads despite the frontmatter-first instruction, add an engine-rendered persona roster line (slug · flow · vibe) to status/check — the recorded escalation (from persona-load-performance spec-delta)
Must:
  - with >=1 REAL persona, `add.py status` renders a `personas:` header + one line per persona: `  - <slug> [<flow|?>] — <vibe, truncated to 70 chars>` (sorted by slug; frontmatter-only read so agents stop whole-roster reads)
  - `add.py check` renders ONE roster INFO line: `roster: <slug>[<flow>] · <slug>[<flow>] · …` (vibe elided — check is a linter)
  - zero real personas -> status/check output byte-identical to today (existence-gated)
  - fail-soft: a persona file with unreadable/absent frontmatter renders `<slug> [?] —` and never raises
Reject:
  - (read-only rendering — no runtime rejects; malformed frontmatter degrades to `?`, it never errors)
Accept: Given tdd-verifier declares `flow: verify, advisor`, When `add.py status` runs, Then the roster shows `- tdd-verifier [verify, advisor] — Trust evidence…` (truncated vibe).
Assumptions: ⚠ per-persona lines in status (not one packed line) is the right verbosity for a 6-persona roster — if wrong: presentation-only re-shape, cheap

---

## 3 · CONTRACT — freeze the shape

```
status (only when >=1 real persona):
  personas:
    - <slug> [<flow-value-list | ?>] — <vibe first 70 chars, ellipsis when cut>
check  (only when >=1 real persona), one INFO row:
  ("personas", "roster: <slug>[<flow|?>] · <slug>[<flow|?>] · …")     # sorted by slug
guarantees: zero personas -> byte-identical output · pure frontmatter read, fail-soft `?` on any
            parse miss · advisory (never a WARN, never a gate)
```

`Least-sure flag surfaced at freeze:` [spec] the 70-char vibe truncation + placement under the status persona slot — presentation judgement; if wrong: cosmetic re-shape, cheap
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first (red)

Plan: test_roster_status_line.py — status roster line for a seeded persona incl. flow+vibe (Accept) · check INFO roster row · zero-persona byte-identity (status diff before/after seeding dir removal) · fail-soft `?` on frontmatter-less file · truncation at 70 · trio + ENGINE_MD5 honesty.
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy & known-problem fixes: (1) red test first (2) pure helper in add.py (frontmatter regex mirroring _persona_quality_warnings' fence parse; do NOT touch add_engine — keep PKG pin still) (3) wire status then check, both existence-gated (4) trap: status byte-identity for persona-less projects is pinned by MANY sibling tests — run the status/check suites before claiming green (5) sync trio, re-pin ENGINE_MD5
Approach (domain strategy): frontmatter-only single-pass read · existence-gated additive rendering (fast-lane-marker precedent) · fail-soft degrade to `?` · readability-first, no perf budget (6-file scan)
Strategy actually used: as planned + one disclosed out-of-scope side-fix: .add/SEAMS.md scope-token-grammar anchor re-pinned 4786->4798 (the helper's +25 lines moved add.py line numbers — the known SEAMS drift ripple)
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [ ] all tests pass · coverage held · no test or contract altered during build
- [ ] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [ ] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): status renders `- <slug> [<flow>] — <vibe<=70>` per real persona and check one packed roster INFO; persona-less projects byte-identical — confirmed by test_roster_status_line (7 green) + seams/mirror/nudge guard run

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07

