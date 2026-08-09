# TASK: Per-facet ADR harvest + Watch cites the Optimization stance

slug: facet-adr-harvest · created: 2026-07-07 · stage: mvp · sensitivity: architecture
milestone: build-strategy-facets
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- add-method/tooling/add.py : `_stamp_adr_record` → inner `_strategy()` — harvests §5 "Strategy actually used" via `_capture_wrapped(label, body)`, placeholder rule = value startswith "<fill"; emits the fixed 4-line ADR block ([AI] specify · [human] freeze · [AI] build strategy used · gate); wrapped in try/except so harvest never blocks the gate; 3-file trio (canon · .add/tooling · _bundled) pinned by engine_pin.ENGINE_MD5 78baf42b
- add-method/tooling/engine_pin.py : ENGINE_MD5 + ENGINE_PKG_MD5 — both re-aim on any engine byte change
- add-method/tooling/templates/TASK.md.tmpl : §7 "Watch (reuse scenarios as monitors):" line — hint today names error rate/rejection rate/latency only; 4 twins in lockstep at 5899d7f7, size ceiling 11400 (test_taskmd_lean)
Context (working folder): test_strategy_facets.py (facet labels + contract-exact lines — the upstream frozen shape this consumes) · test_engine_repin_parity.py (trio/pin parity) · test_adr_harvest*.py (existing harvester guards incl. multiline-field capture) · test_taskmd_lean.py (11400 ceiling)
Honors (patterns / conventions): faithful-capture rule (only a leading placeholder token degrades; a real value containing "<" is kept — mirrored from `_strategy()`) · harvest-never-blocks-the-gate (whole stamp in try/except) · engine trio byte-copy + honest re-pin (diff vs main, not vs a history comment) · additive template change under the migrated 11400 ceiling
Seams consulted: none that apply (the scope-token-grammar seam was consulted at task 1; this task's scope is engine+template dirs)
Anchors the contract cites: `_stamp_adr_record` · `_strategy` (inner) · `_capture_wrapped` · `ENGINE_MD5` / `ENGINE_PKG_MD5` · the §5 facet labels frozen by task 1 (`Approach (domain strategy):` · `Data strategy:` · `Pattern:` · `Optimization stance:`) · `Watch (reuse scenarios as monitors):`
Issues/Risks (→ feed §1):
- backwards compatibility: every DONE task's TASK.md lacks facet lines — the harvester must collapse to today's exact single-line output when no facet is filled (no retro-churn on re-stamps)
- `_capture_wrapped("Pattern", …)` label collision risk: "Pattern:" must not accidentally match "Honors (patterns" or prose — verify `_capture_wrapped` anchors at line start
- placeholder detection differs by facet: template placeholders start with "<the "/"<WHAT " etc — the general rule "startswith('<')" (like `_framing`) fits, NOT the "<fill" rule
- engine change moves ENGINE_MD5/PKG — re-pin against a real md5 diff vs main (persona-learning-loop lesson), sync trio + bundle
Related intent: MILESTONE build-strategy-facets exit criterion 3 (diverged facet = own [AI] ADR line; "as planned" collapses to one) · GLOSSARY "Strategy facet" · consumes task 1's frozen facet-line shape
Ground SHA: 79a9dea (task 1 committed on feat/build-strategy-facets); `_capture_wrapped` verified line-start-anchored (`^Label:`), so a bare "Pattern" label cannot bleed from prose — the §0 collision risk above is resolved, kept for the record

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: per-facet ADR harvest at task done + §7 Watch cites the Optimization stance
Framings weighed: extend _stamp_adr_record to emit one [AI] build line per FILLED facet, keeping the strategy-used line (chosen) · merge facets INTO the single strategy-used line (loses per-facet ADR granularity, the milestone's point) · harvest at verify instead of done (changes the stamp lifecycle for no gain)
Must:
<must>
  - M1: each FILLED §5 facet (Approach (domain strategy) · Data strategy · Pattern · Optimization stance) emits its own ADR line "- [AI] build — <facet key>: <value>", ordered approach → data strategy → pattern → optimization stance, all placed directly BEFORE the existing strategy-used line
  - M2: an unfilled facet (absent line, or value starting with "<") emits nothing — silent, per facet
  - M3: collapse — a task with no filled facet renders EXACTLY today's ADR block (byte-identical lines, incl. "strategy used: as planned" defaulting); done tasks without facet lines re-stamp unchanged
  - M4: TASK.md.tmpl §7 Watch hint gains the stance cross-cite (contract-exact line), 4 twins in lockstep, 11400 size ceiling held
  - M5: ENGINE_MD5 + ENGINE_PKG_MD5 re-pinned against the real md5 diff; add.py trio byte-identical; repin-parity suite green
</must>
Reject:
<reject>
  - a facet value merely CONTAINING "<" mid-text degraded to unfilled -> "false_placeholder_drop"
  - any harvest exception reaching the gate (stamp must stay try/except-shielded) -> "gate_blocked"
  - a facet harvested from a section other than §5 (label collision outside bodies[5]) -> "cross_section_bleed"
</reject>
After:
<after>
  - a demo task with filled facets shows one [AI] line per facet in §7 Decisions at done; a facet-less legacy task re-stamps byte-identical
  - full guard suite green; pins honest
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ FILLED-is-diverged is the right harvest trigger (vs diffing plan-vs-actual) — lowest confidence because a facet may be filled at tests->build and followed exactly; if wrong the ADR gains true-but-planned lines, cost = mild ADR noise, no data loss (strategy-used still records divergence)
  - [x] the "<" prefix placeholder rule matches all four facet template hints — confirmed: all start "<the "/"<WHAT " per task 1's frozen lines
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: filled facets each earn an ADR line   # M1
  Given a done task whose §5 has all four facets filled with real values
  When the ADR block is stamped
  Then four "- [AI] build — <facet key>: <value>" lines render, ordered approach, data strategy, pattern, optimization stance
  And they sit directly before the strategy-used line

Scenario: an unfilled facet stays silent   # M2
  Given a §5 where only Approach is filled and the rest keep their placeholder hints
  When the ADR block is stamped
  Then exactly one facet line (approach) renders
  And no line renders for the placeholder facets

Scenario: legacy collapse   # M3
  Given a done task whose §5 predates the facet lines entirely
  When the ADR block is stamped
  Then the block is byte-identical to today's four-line output
  And "strategy used: as planned" still defaults when unfilled

Scenario: Watch cites the stance   # M4
  Given the canonical TASK.md.tmpl §7
  When the Watch line is read
  Then its hint names the §5 Optimization stance as a monitor source
  And the 4 twins share one md5 and the 11400 ceiling holds

Scenario: honest re-pin   # M5
  Given the engine change is complete
  When the add.py trio and engine_pin are hashed
  Then all three add.py copies match the NEW ENGINE_MD5
  And the repin-parity suite is green

Scenario: faithful capture   # R:false_placeholder_drop
  Given a filled facet whose value quotes a "<tag>" mid-text
  When the ADR block is stamped
  Then the facet line renders with the full value
  And only a LEADING "<" marks a facet unfilled

Scenario: harvest never blocks   # R:gate_blocked
  Given a §5 that makes the facet parser raise
  When the gate records its outcome
  Then the gate completes normally
  And the ADR placeholder is simply left standing

Scenario: no cross-section bleed   # R:cross_section_bleed
  Given a TASK.md whose §0 or §6 prose contains a line starting "Pattern:"
  When the ADR block is stamped
  Then only §5's facet lines are harvested
  And other sections contribute nothing
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_stamp_adr_record inner _strategy() extension (add.py), harvest source = bodies[5] ONLY:
  FACETS = (("Approach (domain strategy)", "approach"), ("Data strategy", "data strategy"),
            ("Pattern", "pattern"), ("Optimization stance", "optimization stance"))
  for label, key in FACETS:
      val = _capture_wrapped(label, bodies.get(5, ""))
      filled := val is not None and not val.startswith("<")     # LEADING "<" only = placeholder
      filled -> emit "- [AI] build — {key}: {val}"              # in FACETS order
  facet lines insert directly BEFORE "- [AI] build — strategy used: {strat}" (which stays, incl.
  its "as planned" default and its "<fill" placeholder rule, unchanged)
  zero filled facets -> the ADR block is byte-identical to today's 4-line output (collapse)
  the whole stamp remains inside _stamp_adr_record's existing try/except (never blocks the gate)

TASK.md.tmpl §7 — the Watch line becomes, exactly:
Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

Schema: add.py trio (canon · .add/tooling · _bundled; ENGINE_MD5 re-pins) · engine_pin.py (both pins) ·
TASK.md.tmpl 4 twins (size ceiling 11400 held) · guard suite add-method/tooling/test_facet_adr_harvest.py (new file)
```

Glossary deltas: none (uses task 1's "Strategy facet")
Status: FROZEN @ v1 — approved by Tin (2026-07-07)
Reported: yes — banner/ARC/SHAPE/FLAGS rendered before the freeze
Least-sure flag surfaced at freeze: [spec] filled-is-harvested as the trigger — a facet followed exactly as planned still earns its ADR line; if wrong the cost is mild ADR noise (true-but-planned lines), no data loss since strategy-used still records divergence

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: one test per scenario, unit-level against _stamp_adr_record on synthetic task dirs
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_filled_facets_each_earn_a_line: synth TASK.md, 4 real facet values / stamp / assert 4 keyed lines in FACETS order, before strategy-used · covers: M1
  - test_unfilled_facet_stays_silent: only Approach filled / stamp / assert exactly one facet line · covers: M2
  - test_legacy_collapse_byte_identical: facet-less §5 / stamp / assert block == today's 4 lines, "as planned" default intact · covers: M3
  - test_watch_line_cites_stance: read canon tmpl / assert contract-exact Watch line + 4-twin lockstep + ≤11400 B · covers: M4
  - test_engine_repin_honest: hash add.py trio / assert == NEW engine_pin.ENGINE_MD5 (red while pin still 78baf42b) · covers: M5
  - test_faithful_capture_mid_text_bracket: facet value quoting a tag mid-text / stamp / assert full value rendered · covers: R:false_placeholder_drop
  - test_harvest_never_blocks_gate: §5 body engineered to raise in parse / gate records / assert outcome recorded, placeholder standing · covers: R:gate_blocked
  - test_no_cross_section_bleed: "Pattern: x" line planted in §0 and §6 prose / stamp / assert zero facet lines · covers: R:cross_section_bleed
</test_plan>

Tests live in: `add-method/tooling/` test_facet_adr_harvest.py · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy (ordered batches): 1. red guard suite (tests phase) 2. extend _strategy() with the FACETS loop, contract-exact 3. edit the §7 Watch line in canon tmpl 4. byte-copy add.py + tmpl to their twins 5. re-pin ENGINE_MD5 + ENGINE_PKG_MD5 honestly (md5 diff vs main) 6. targeted sweep + full suite in background
Approach (domain strategy): extend the existing single-pass ADR stamp with a declarative FACETS tuple loop — the same _capture_wrapped + placeholder-prefix idiom the harvester already trusts, no new parsing machinery; fits because the harvester's domain is faithful line-capture, and reuse keeps the failure surface inside the one existing try/except
Data strategy: FACETS as an ordered tuple of (label, key) pairs; harvest reads bodies[5] only (the §-body dict the stamp already builds — agrees with the §3 Schema line's add.py-trio scope); output is ordered ADR lines, facet lines strictly before the strategy-used line
Pattern: faithful-capture + collapse-to-legacy (§0 Honors: only a LEADING placeholder degrades; harvest-never-blocks-the-gate try/except; additive behavior so done tasks re-stamp byte-identical)
Optimization stance: correctness-first, no budget — the stamp runs once per task at done, performance is immaterial; ⚠ least-trusted facet: Data strategy (the bodies[5]-only sourcing is asserted by R:cross_section_bleed, the risk I most want the tests to catch)

Persona (required): methodology-engine-dev
Spawn isolation (default): shared tree — orchestrator builds inline (sequential mode, single writer)
Known-problem fixes: label bleed from prose → harvest bodies[5] only + line-start-anchored _capture_wrapped · placeholder false-positive on values quoting tags → leading-"<" rule only · stale-pin dishonesty → re-pin from a fresh md5 of the BUILT add.py, diffed vs main, trio synced before pinning · tmpl growth → Watch line delta ≈ +60 B, ceiling 11400 has ~68 B headroom (11332 now) — verify before copy
Strategy actually used: as planned, with two deviations — the Watch line overshot the 11400 ceiling by 12 B (headroom estimate missed the em-dash bytes), reclaimed from the unpinned Spawn-isolation hint rather than touching the frozen line; and the full suite exposed two fresh-checkout/anchor ripples (gitignored-dogfood twin absent in a clean clone → skip-tolerance per ba09498; SEAMS.md pin re-drifted under this task's own +20 lines → re-pinned 4786), both healed via the tests->build re-cross convention
Safety rule (feature-specific): the harvest must never block or fail a gate — every new code path stays inside _stamp_adr_record's existing try/except shield; frozen §3 of ANY task is never parsed for facets (facets live in §5 only)
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full tooling suite 3141/3141 OK post-commit (incl. the fresh-checkout clone test and the seams anchor test)
- [x] coverage did not decrease — 9 new tests added, none removed; adjacent ADR/repin/lean suites green
- [x] no test or contract was altered during build — EXCEPT two disclosed heals re-anchored by re-crossing tests->build: fresh-checkout skip-tolerance in the two new twin-parity suites (gitignored dogfood twin absent on a clean clone, ba09498 precedent) and the SEAMS.md line pin 4766→4786 (this task's own upstream growth); frozen §3 untouched since v1
- [x] the green was EARNED — refute-read by add-verify agent (below): mutation probe on a scratch copy redded the placeholder-rule tests; the never-blocks-gate mock traced to the real shielded path
- [x] concurrency / timing safe — single-pass stamp at gate time, atomic write (_atomic_write), no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — zero packages; harvest renders only text already present in the task file
- [x] layering follows CONVENTIONS.md — harvest-not-author preserved (every line sourced from an existing §5 stamp); NO-EXEC; trio byte-copied; honest re-pin
- [ ] a person reviewed and approved the change — THIS gate (sensitivity: architecture -> human decision)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] THIS task's own §7 Decisions block will show one [AI] line per facet filled in §5 above — the mechanism is proven by test_filled_facets_each_earn_a_line on the same engine; final self-dogfood reading happens right after the gate stamps (confirmed post-gate, see §7)
- [x] a legacy done task re-stamps byte-identical — confirmed by test_legacy_collapse_byte_identical + the grandfather placeholder rule (a resolved block is a no-op; strategy-facet-block's block is already resolved so it can never be re-written)
- [x] the canon TASK.md.tmpl §7 Watch line names the Optimization stance, 4 twins one md5, 11379 B ≤ 11400 — confirmed by md5 sweep + byte count (mine and the refute-read's, independently)
- [x] git diff main..HEAD of add.py is ONLY the _facets addition (+20/-0); ENGINE_MD5 35e7f701 equals the fresh md5 of all three built copies — confirmed by direct md5 on the branch

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_facets` is called at the harvest gather (add.py:532) and consumed in the `lines` render (add.py:541); confirmed by the refute-read's trace + the green M1/M2 tests
- [x] DEAD-CODE (code) — no new unused symbol: `_FACETS`/`_facets` both referenced; nothing else added
- [x] SEMANTIC (prose / non-code) — read in full: the Watch line (contract-byte-exact) and the trimmed Spawn-isolation hint (meaning preserved: worktree default + stated-reason exception + seam name all retained)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 cites resolves: _stamp_adr_record/_strategy/_capture_wrapped/_facets in the current add.py; ENGINE_MD5/ENGINE_PKG_MD5 in engine_pin.py; the four facet labels in the template; the Watch line present
- [x] anchors that moved since Ground SHA, named: _declared_scope drifted 4766→4786 under this task's own +20 lines (SEAMS.md re-pinned, disclosed); ENGINE_MD5 78baf42b→35e7f701 (the deliberate re-pin)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: add-verify agent a69363da5d75f0a8d (persona tdd-verifier) · adversarially checked: mock reachability of the never-blocks-gate shield (traced to the real path) · mutation probe on a scratch copy (placeholder-rule removal redded 2 tests for the right reason; repo restored, git clean) · legacy re-stamp via real synthetic tasks · ENGINE_MD5 re-derived on all 3 copies · Watch line byte-exact + twins + ceiling · 38/38 guard+adjacent suites

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: add-verify agent a69363da5d75f0a8d
1. Security: CLEAR — harvest renders only text already in the task file; NO-EXEC; no new input surface
2. Concurrency: CLEAR — single-pass stamp, atomic write, no shared mutable state
3. Architecture: CLEAR — harvest-not-author invariant preserved; bodies[5]-only sourcing structural; trio parity + honest re-pin
Verdict: PASS
Residue: none
Binding: advisory — architecture

### GATE RECORD
Reported: yes — gate report (banner/ARC/SUMMARY/FLAGS/EVIDENCE) rendered to Tin before any outcome is recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose extend _stamp_adr_record to emit one [AI] build line per FILLED facet, keeping the strategy-used line; rejected merge facets INTO the single strategy-used line (loses per-facet ADR granularity, the milestone's point) · harvest at verify instead of done (changes the stamp lifecycle for no gain)
- [human] freeze — froze §3 @ v1 (approved by Tin (2026-07-07))
- [AI] build — approach: extend the existing single-pass ADR stamp with a declarative FACETS tuple loop — the same _capture_wrapped + placeholder-prefix idiom the harvester already trusts, no new parsing machinery; fits because the harvester's domain is faithful line-capture, and reuse keeps the failure surface inside the one existing try/except
- [AI] build — data strategy: FACETS as an ordered tuple of (label, key) pairs; harvest reads bodies[5] only (the §-body dict the stamp already builds — agrees with the §3 Schema line's add.py-trio scope); output is ordered ADR lines, facet lines strictly before the strategy-used line
- [AI] build — pattern: faithful-capture + collapse-to-legacy (§0 Honors: only a LEADING placeholder degrades; harvest-never-blocks-the-gate try/except; additive behavior so done tasks re-stamp byte-identical)
- [AI] build — optimization stance: correctness-first, no budget — the stamp runs once per task at done, performance is immaterial; ⚠ least-trusted facet: Data strategy (the bodies[5]-only sourcing is asserted by R:cross_section_bleed, the risk I most want the tests to catch)
- [AI] build — strategy used: as planned, with two deviations — the Watch line overshot the 11400 ceiling by 12 B (headroom estimate missed the em-dash bytes), reclaimed from the unpinned Spawn-isolation hint rather than touching the frozen line; and the full suite exposed two fresh-checkout/anchor ripples (gitignored-dogfood twin absent in a clean clone → skip-tolerance per ba09498; SEAMS.md pin re-drifted under this task's own +20 lines → re-pinned 4786), both healed via the tests->build re-cross convention
- [AI] verify — gate PASS (reviewed by Tin)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

