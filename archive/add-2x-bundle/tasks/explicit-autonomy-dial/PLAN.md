# TASK: Explicit 3-mode autonomy dial (manual/conservative/auto)

slug: explicit-autonomy-dial · created: 2026-06-10 · stage: mvp · risk: high
autonomy: conservative   <!-- this task rewrites the autonomy guard itself; Verify STOPS for the human. -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: make the autonomy level an EXPLICIT, human-set 3-mode dial — `manual | conservative | auto` —
recognized and enforced by the engine, with no silent default. Scope: make-explicit only — the dial keeps
governing the freeze+Verify gate axis; it does NOT expand to gate every phase transition.
Framings weighed: make-explicit + add `manual` as the strict rung (chosen) · scope-expansion to gate every phase seam (rejected — bigger, a separate task) · docs-only relabel (rejected — prose-only is the convention task 1 killed)
Must:
<must>
  - the engine recognizes EXACTLY three autonomy levels, ordered by strictness: manual < conservative < auto
  - `auto` keeps today's behaviour (Verify auto-PASSes on complete evidence); `conservative` keeps a human at
    the Verify gate; `manual` is the strict floor — the human owns the gate and the engine never auto-resolves
  - the high-risk completion guard accepts ANY lowered level (manual OR conservative), not just conservative,
    so a high-risk task set to `manual` is NOT wrongly refused; `risk: high` + `autonomy: auto` still REFUSES
  - the level is EXPLICIT (written, never silently inferred): `new-task` seeds a VISIBLE, overridable
    `autonomy: auto` default in the template, and status/guide surface the active level every session
  - a LIVE task whose `autonomy:` line is absent (a deleted line, or a task predating the seed) is SURFACED as
    `implicit_autonomy` (WARN, live tasks only — done/archived predecessors skipped, no flood; task 1's lesson)
  - GLOSSARY + the autonomy docs (appendix-c · 10-setup-and-stages · 11-governance) describe the 3-mode dial (prose ≡ enforcement)
</must>
Reject:
<reject>
  - a REAL autonomy token outside {manual, conservative, auto} -> "unknown_autonomy_level"
  - `risk: high` with `autonomy: auto` (or no lowered level) -> "unguarded_high_risk_auto" (existing — widened to accept manual)
  - a task carrying no explicit autonomy level -> "implicit_autonomy" (WARN, not a hard refuse — see ⚠)
</reject>
After:
<after>
  - every task declares its autonomy level explicitly; the human reads the active level each session; a
    high-risk scope may be lowered to manual OR conservative; auto never silently governs a high-risk scope
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec/contract] `manual` needs NO distinct engine teeth beyond being the strictest recognized rung — it
    satisfies the high-risk guard and never auto-resolves, i.e. behaviourally the conservative floor with the
    explicit "I drive this; the AI proposes only" name — lowest confidence because if you want manual to gate
    something conservative does not (refuse RISK-ACCEPTED waivers · confirm each phase), that is scope
    expansion and a separate, bigger task; if wrong: an under-built manual
  - [x] new-task seed mechanism — RESOLVED at freeze: seed a VISIBLE `autonomy: auto` default (the established
    v7 default made explicit/overridable; the human is aware new non-high-risk tasks then default to auto, and the
    high-risk guard still refuses risk:high+auto) — chosen over the warn-until-filled placeholder
  - [x] "explicit" enforces as WARN on a missing level (not a hard REFUSE) — RESOLVED: human chose WARN —
    additive, never retro-reds the existing 49-record board (task 1's verified-marker lesson); a high-risk
    implicit task is still hard-refused by the widened guard, so the soft path cannot smuggle high-risk auto
  - [x] the three levels read as an ordered ladder the high-risk guard treats as "not auto" — confirmed
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: manual is recognized as the strictest rung and satisfies the high-risk guard
  Given a task header "risk: high" with "autonomy: manual"
  When I gate PASS at verify
  Then it succeeds (manual is a lowered rung — not refused as unguarded)

Scenario: conservative still satisfies the high-risk guard (unchanged)
  Given "risk: high" with "autonomy: conservative"
  When I gate PASS at verify
  Then it succeeds

Scenario: high-risk + auto is still refused
  Given "risk: high" with "autonomy: auto"
  When I gate PASS at verify
  Then it REFUSES with "unguarded_high_risk_auto"

Scenario: an unknown level is rejected
  Given a header "autonomy: yolo"
  When I run check
  Then it reports "unknown_autonomy_level"

Scenario: a missing level warns but does not red (live tasks)
  Given a LIVE non-high-risk task with no "autonomy:" token
  When I run check
  Then it emits an "implicit_autonomy" WARNING
  And check still passes (the warning never reds)

Scenario: done predecessors are never warned (no flood)
  Given a DONE task with no "autonomy:" token
  When I run check
  Then no "implicit_autonomy" is emitted for it (the warn is live-tasks-only)

Scenario: a high-risk task with no level is still hard-refused
  Given "risk: high" with no "autonomy:" token
  When I gate PASS at verify
  Then it REFUSES "unguarded_high_risk_auto" (the soft warn never smuggles high-risk auto)

Scenario: new-task seeds a visible auto default
  Given I create a task with new-task
  When I open its TASK.md header
  Then it carries a visible "autonomy: auto" default
  And check emits NO "implicit_autonomy" for it (a valid level, not unset)

Scenario: status surfaces the active level
  Given an active task with "autonomy: conservative"
  When I run status
  Then the output shows the active autonomy level
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
autonomy levels — engine vocabulary (ordered strictness)
  _AUTONOMY_LEVELS = ("manual", "conservative", "auto")               # manual < conservative < auto
  _autonomy_level(hdr)   -> "manual"|"conservative"|"auto"  (a recognized rung)
                          |  None  (the `autonomy:` line is absent -> UNSET)
                          |  "?"   (a real token outside the set, e.g. "yolo" -> unknown)
  _autonomy_lowered(hdr) -> bool     # True iff level in {manual, conservative} (a high-risk-safe rung)

add.py gate   (high-risk completion guard — widened; same refuse code)
  refuse "unguarded_high_risk_auto"  when  risk: high  AND not _autonomy_lowered(hdr)
    was: requires `autonomy: conservative` literally  ->  now: any lowered rung (manual OR conservative)
  risk: high + auto (or no token) still REFUSES; manual + conservative both pass.

Verify resolver   (behaviour unchanged, recognition widened)
  auto-PASS fires ONLY under `auto`; manual + conservative keep the human at the gate (never auto-resolve).

add.py new-task   (template seed)
  the seeded header carries a VISIBLE, overridable default `autonomy: auto` (the established v7 default made
  explicit — written, the human sees and lowers it; no new-task warn-noise). implicit_autonomy fires only if
  the line is later deleted, or on a pre-existing live task that predates the seed.

add.py status / guide   (surface)
  print the active task's autonomy level each session (or "unset" when the line is absent).

add.py check / audit   (findings)
  unknown_autonomy_level   : _autonomy_level == "?" — a REAL out-of-set token        -> finding (red, exit 1)
  implicit_autonomy        : _autonomy_level is None on a LIVE task (phase before     -> WARNING (yellow; additive)
                             done/observe); the unfilled seed counts as unset. Done/archived predecessors are
                             SKIPPED — a fresh live-only predicate, NOT the audit open-front skip (which is inverted)
  unguarded_high_risk_auto : risk: high AND not _autonomy_lowered (auto / unset)      -> finding (red; widened)

Reject codes: unknown_autonomy_level · implicit_autonomy (WARN) · unguarded_high_risk_auto (widened)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-10
Least-sure flag surfaced at freeze: ⚠ [spec/contract] `manual` carries no distinct engine teeth beyond being the strictest recognized rung — if the human later wants manual to gate what conservative does not, that is scope-expansion (a separate, bigger task); the seed-default fork was resolved at the freeze (seed `auto` — the established v7 default made visible/overridable, human aware), so the residual risk is an under-built manual.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject (3 levels · widened high-risk guard · explicit seed/surface · warn-not-red)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_manual_satisfies_high_risk_guard / _conservative_satisfies / _auto_refused: gate PASS under risk: high
  - test_unknown_level_rejected: a bogus token -> "unknown_autonomy_level" (check red, exit 1)
  - test_missing_level_warns_not_red: a LIVE non-high-risk task, no token -> "implicit_autonomy" WARNING, check passes
  - test_done_predecessor_not_warned: a DONE task with no token -> no implicit_autonomy (live-only scope)
  - test_high_risk_missing_level_refused: risk: high + no token -> "unguarded_high_risk_auto" (soft path can't smuggle)
  - test_new_task_seeds_auto_default: a new-task TASK.md header carries a visible `autonomy: auto`, no implicit_autonomy
  - test_status_surfaces_level: status prints the active task's autonomy level
  - test_docs_state_3mode: GLOSSARY + autonomy docs name manual|conservative|auto (prose ≡ enforcement), synced ×3
</test_plan>

Tests live in: `add-method/tooling/test_explicit_autonomy_dial.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the guard widening is LOOSEN-ONLY (`conservative` -> `{manual, conservative}`)
— no existing high-risk task regresses; the autonomy read is PURE (header-only, comments stripped); the
implicit_autonomy lint is WARN-never-red and LIVE-only (done predecessors never flood).
Code lives in: `add-method/tooling/add.py` (+ synced byte-identical to `.add/tooling/` and `_bundled/`);
template `templates/TASK.md.tmpl`; the autonomy doc-surface the §1 Must names — GLOSSARY (survivor
`.add/GLOSSARY.md` + `templates/GLOSSARY.md.tmpl`) · `appendix-c-glossary.md` · `10-setup-and-stages.md` ·
`11-governance.md` · skill `run.md` (each synced across the three trees).
Constraints: do NOT change any test or the frozen contract; stdlib only; reuse the gate/audit/check/status seams.

Built: `_AUTONOMY_LEVELS` + `_autonomy_level()`/`_autonomy_lowered()` (replacing `_AUTONOMY_CONSERVATIVE_RE`);
gate + audit high-risk guard widened to any lowered rung; cmd_check `unknown_autonomy_level` (red) +
`implicit_autonomy` (live-only WARN); cmd_status surfaces the active level; new-task seeds `autonomy: auto`
(template + `_FALLBACK_TASK`). Full suite 717 green; 3-tree parity re-pinned (c0c9329c); docs synced ×3.
Deviation (logged): the level regex uses `\b` not `^`, so an inline slug-line token reads like the legacy
guard — caught by the high-risk-signal regression tests and fixed before green (no test weakened).
Verify-stage close (logged): the build first shipped only 2 of the 4 doc surfaces the frozen §1 Must names;
the advisor caught it at the gate, so GLOSSARY (survivor + template) · 11-governance · run.md were completed
to the 3-rung ladder (no bare "dial"; `formerly "autonomy dial"` bridges kept) and DocsAccordTest was extended
to machine-pin all 4 named surfaces — the frozen §4 plan ("GLOSSARY + autonomy docs … synced ×3") that the
first build under-delivered. RED→green; no engine byte changed (pin stable).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `Ran 717 … OK` (guard widen · check lint · status · seed · docs accord ×4-surface)
- [x] coverage did not decrease — new suite purely additive; the 4 high-risk-signal regressions were FIXED, not weakened
- [x] no test or contract was altered during build — frozen §3 honored; the widening matches the contracted shape
- [x] concurrency / timing of the risky operation is safe — single-process CLI; the autonomy read is pure (header-only)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — pure helpers + the existing gate/audit/check/status seams
- [x] a person reviewed and approved the change — Tin, at the verify gate, 2026-06-10

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_autonomy_level` referenced by `_autonomy_lowered` (gate+audit guard), cmd_check (lint),
      cmd_status (surface); `_autonomy_lowered` by cmd_gate + `_audit_findings`; `_AUTONOMY_LEVELS`/`_AUTONOMY_LINE_RE`
      by `_autonomy_level`. Live dogfood: status prints `autonomy: conservative`; risk:high+conservative passed the widened guard
- [x] DEAD-CODE (code) — `_AUTONOMY_CONSERVATIVE_RE` was REMOVED (both call sites moved to `_autonomy_lowered`); no orphaned symbol
- [x] SEMANTIC (prose / non-code) — read in full, NOT skimmed: the frozen §1 Must names FOUR doc surfaces
      (GLOSSARY · appendix-c · 10-setup · 11-governance); the first build shipped only 2. Closed at verify —
      `.add/GLOSSARY.md` + `GLOSSARY.md.tmpl` + `11-governance.md` + skill `run.md` now name the 3-rung ladder
      `manual < conservative < auto`, and run.md's two STALE guard lines ("lowered to conservative") were
      corrected to "conservative or manual" (prose was wrong vs the widened engine). No bare "dial" on the
      vocab surface (bridges exempt); DocsAccordTest extended to machine-pin all 4 surfaces + ×3 sync.
      Method-wide straggler sweep (advisor-prompted, since the vocab linter catches banned WORDS, not a stale
      2-mode DESCRIPTION): fixed the operative skill surface too — `streams.md` throttle table + worker STOP
      bullet (was gated `ONLY when autonomy=conservative`; `manual` must STOP too — a real behavioral gap) +
      high-risk rule, and `SKILL.md` ×2 — all synced ×3. Scope disclosed (NOT a defect): the book NARRATIVE
      chapters (01-principles · 02-the-flow · 08-step-6-verify · phase guides) teach `conservative` as the
      canonical lowering — accurate, not exhaustive, and outside the frozen Must's 4 named surfaces; the
      reference docs name `manual` as the strict-floor variant. So the prose≡enforcement claim holds for the
      engine-token reference + operative surfaces; the narrative's two-ended default↔lower framing is a
      pedagogical choice, optionally widened in a follow-up.
      Final sweep — add.py's own user-facing strings (help · hints · the `unguarded_high_risk_auto` message ·
      sync-guidelines) + every `*.tmpl`: ALL already name `manual` (3-mode), no lone `auto|conservative`
      pairing — the build wrote them 3-mode, so the engine byte is unchanged and the pin holds (no re-pin).

### GATE RECORD
Outcome: PASS — human-confirmed at the verify gate (build green; prose ≡ enforcement gap closed + machine-pinned across all 4 frozen-Must surfaces; the standing `manual`-scope flag accepted as a disclosed boundary)
Reviewed by: Tin (human, at verify gate) · date: 2026-06-10

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `unknown_autonomy_level` rate (typo'd tokens) · `implicit_autonomy`
warn rate (drift toward un-declared levels) · `unguarded_high_risk_auto` refusals (the guard earning its keep).
Spec delta for the next loop: if `manual` accrues real demand to gate what `conservative` does not (refuse
RISK-ACCEPTED waivers · confirm each phase), that is the next scope — a separate, bigger task, not a widening here.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a docs-accord test must pin EVERY surface the §1 Must names, or "prose ≡ enforcement" is only as wide as the pin — frozen §4 said "GLOSSARY + autonomy docs … synced ×3" but the implemented DocsAccordTest pinned 1 of 4, so 2 surfaces shipped stale-green and the gap was caught by human review at the gate, not by CI (evidence: DocsAccordTest extended 1→4 surfaces, RED on GLOSSARY + 11-governance before close)
- [ADD · folded] a word-ban linter does not catch a stale multi-valued DESCRIPTION — once a 3rd rung lands, "auto | conservative" enumerations read green to the slang fence; level-set prose widens by a structural/test pin or manual sweep, never by the vocab ban (evidence: streams.md + SKILL.md 2-mode stragglers passed the vocab linter, found only by the advisor-prompted method-wide grep)
