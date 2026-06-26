# TASK: Prefer descriptive milestone slugs + full-ISO created stamp

slug: milestone-naming · created: 2026-06-26 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/add.py:cmd_new_milestone` — creates the milestone dir + MILESTONE.md + state record. Slug is validated alnum-only at L2425 (`_die("bad_slug")`); the MILESTONE.md `created:` is stamped via `date.today().isoformat()` (date-only) at L2436 while the state record uses full `_now()` at L2444.
Context (working folder): the 3-tree engine mirror (`.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py`) + the `ENGINE_MD5` literal in `add-method/tooling/engine_pin.py`; `templates/MILESTONE.md.tmpl:5` renders `created: {{date}}`.
Honors (patterns / conventions): engine stays NO-EXEC; non-fatal advisories print as `note:` (the established convention — `add.py:429`, no `warn:` prefix exists); two-pin model + byte-identical 3-tree; `engine_pin.py` never ships to `.add/tooling/`.
Anchors the contract cites: `cmd_new_milestone`, `_now()`, `date.today()`, the bare-version slug pattern.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: prefer-descriptive-milestone-slug + full-ISO created stamp
Framings weighed: warn-not-block (chosen) · hard-reject bare versions · docs-only nudge
Must:
<must>
  - when the slug matches a bare-version pattern (`^v?\d+([._-]\d+)*$`, case-insensitive — e.g. v2, v1-1, 1.2), print a `note:` suggesting a short descriptive name, AND still create the milestone (non-blocking)
  - a descriptive slug (not matching that pattern) creates with NO such note
  - the MILESTONE.md `created:` carries the full `_now()` UTC ISO timestamp (not date-only), and equals the state record's `created` instant (one `_now()` call feeds both)
</must>
Reject:
<reject>
  - slug not alnum after stripping -/_  -> "bad_slug"   (PRE-EXISTING — unchanged; the warn never blocks)
</reject>
After:
<after>
  - the milestone dir + MILESTONE.md + state record exist; a version-y slug additionally emitted one `note:` line; the MILESTONE.md `created:` is a full ISO datetime identical to `state.milestones[slug].created`
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the bare-version regex `^v?\d+([._-]\d+)*$` is the right shape — lowest confidence because a legit name could in theory be all-digits (e.g. "2024"); if wrong: a spurious advisory note, zero functional cost (never blocks). 
  - [x] `note:` (not `warn:`) is the correct prefix — confirmed: it is the engine's only advisory convention; the approved mock's "warn:" was illustrative.
  - [x] one shared `_now()` for template+record — confirmed: makes the two stamps provably equal.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: bare-version slug nudges but still creates
  Given a fresh project root
  When new-milestone is called with slug "v9"
  Then stdout contains a note: line naming "bare version" + "descriptive"
  And the milestone 'v9' is still created (exit 0)

Scenario: descriptive slug creates silently
  Given a fresh project root
  When new-milestone is called with slug "payment-retries"
  Then stdout contains NO bare-version note
  And the milestone 'payment-retries' is created (exit 0)

Scenario: created stamp is a full ISO timestamp equal to the state record
  Given a fresh project root
  When new-milestone is called with slug "billing"
  Then the MILESTONE.md created: value is a full ISO datetime (has 'T' + UTC offset)
  And it equals state.milestones["billing"].created

Scenario: a non-alnum slug is still rejected (unchanged)
  Given a fresh project root
  When new-milestone is called with slug "bad slug!"
  Then it exits with error "bad_slug"
  And no milestone dir is created
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py new-milestone <slug> [--title T] [--stage S] [--await-confirm]
  slug =~ ^v?\d+([._-]\d+)*$  (re.I)  -> stdout includes exactly one line:
       note: slug '<slug>' looks like a bare version — prefer a short descriptive
             name (e.g. 'payment-retries'). Creating anyway.
     ...and the milestone is still created (exit 0)
  slug descriptive                    -> no bare-version note; created (exit 0)
  slug non-alnum (strip -/_)          -> _die("bad_slug")        [PRE-EXISTING, unchanged]

  MILESTONE.md line 5 renders:
       stage: <stage> · status: active · created: <ISO>
     where <ISO> == _now() (full UTC, e.g. 2026-06-26T03:27:43+00:00)
     AND  <ISO> == state.milestones[<slug>].created   (one _now() call feeds both)
Schema: state.json milestones[<slug>].created/updated already full ISO (unchanged);
        only the MILESTONE.md render switches date-only -> full ISO.
```

`Least-sure flag surfaced at freeze:` [spec] the bare-version regex shape (all-digit names like "2024" would also nudge) — chosen scope per your decision; if wrong, a harmless extra note, never a block. Both design forks (warn-not-block · upgrade created:) were decided by you at intake.
Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 4 scenarios (new behavior fully covered)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_version_slug_nudges: new-milestone "v9" in a temp root → stdout has "note:" + "bare version"; dir 'v9' exists
  - test_descriptive_slug_silent: new-milestone "payment-retries" → stdout has NO "bare version"; dir exists
  - test_created_is_full_iso_and_matches_state: new-milestone "billing" → MILESTONE.md created: has 'T'+offset AND == state.milestones['billing'].created
  - test_bad_slug_still_rejected: new-milestone "bad slug!" → SystemExit (bad_slug); no dir created
</test_plan>

Tests live in: `add-method/tooling/test_milestone_naming.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py`
Strategy (ordered batches): 1. edit canonical `add.py:cmd_new_milestone` — compute `now=_now()` once, add the bare-version `note:`, pass `date=now`. 2. mirror canonical add.py → `.add/tooling/` + `_bundled/tooling/` (byte-identical). 3. re-aim `ENGINE_MD5` literal in engine_pin.py to md5(new add.py).
Safety rule (feature-specific): the warn is print-only — never raises, never changes the create path; `engine_pin.py` stays out of `.add/tooling/`.
Code lives in: `add-method/tooling/` (mirrored ×3)
Constraints: do NOT change any test or the contract; stdlib only (re/datetime already imported); MILESTONE.md.tmpl untouched (keeps `{{date}}`).

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (full tooling suite 1972/0, incl. test_milestone_naming 4/4 + parity/pin tests)
- [x] coverage did not decrease (added 4 tests for new behavior; nothing removed)
- [x] no test or contract was altered during build (only §5-declared engine files touched)
- [x] the green was EARNED — the test drives the real CLI via add.main(); the created stamp is read from the rendered file AND cross-checked equal to state.json (no vacuous assert); RED→GREEN confirmed
- [x] concurrency / timing safe — the change is a print + a single shared `_now()`; the existing atomic write is unchanged
- [x] no exposed secrets, injection openings, or unexpected dependencies (stdlib re/datetime only)
- [x] layering & dependencies follow CONVENTIONS.md (engine stays NO-EXEC; `note:` advisory convention; 2-pin + 3-tree mirror preserved)
- [x] reviewed + approved (Tin Dang — design forks decided at intake; auto-mode self-gate on complete evidence)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py new-milestone v9` prints a `note:` naming "bare version" + still creates v9 — confirmed by test_version_slug_nudges + live: `note: slug 'v3' looks like a bare version …` + dir created
- [x] `add.py new-milestone payment-retries` prints NO bare-version note — confirmed by test_descriptive_slug_silent + live (no note line)
- [x] a new MILESTONE.md `created:` line shows a full ISO datetime (`T`+offset) equal to the state record — confirmed live: `created: 2026-06-26T03:47:28+00:00`, == state.json
- [x] 3-tree md5 parity holds + `ENGINE_MD5` re-aimed; full suite green — md5 `acda5c26…` identical ×3; ENGINE_MD5 re-aimed; 1972/0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the `note:` print + shared `now` are inside cmd_new_milestone's live path; `re`/`_now` already imported and referenced
- [x] DEAD-CODE (code) — no new symbol; the inline regex + `now` local are both consumed; no orphan
- [x] SEMANTIC — n/a (code change; covered by WIRING/DEAD-CODE)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
