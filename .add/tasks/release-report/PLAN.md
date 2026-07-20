# TASK: add.py release-report (read-only) + the releasable cue + RELEASES.md ledger schema

slug: release-report · created: 2026-06-16 · stage: mvp
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - the 3 byte-identical ENGINE homes (md5 91e76c35): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py`. ADD: a `release-report` subparser + `cmd_release_report` + `release_data(root, state)` (PURE, no writes) + a `RELEASABLE_CUE` const + `_releasable(root, state)` helper + the cue print in `cmd_status`.
  - `add.py:graduation_data` (L3989) + `cmd_graduation_report` (L4070) — the EXACT template to mirror: PURE gather→dict→text/`--json`, **exit 0 ALWAYS** (only `no_project` non-zero), GATHER-not-JUDGE (no readiness/score field by construction), unreadable source SKIPPED never crash.
  - `add.py:GRADUATION_CUE` (L38) const + the `cmd_status` cue print (L1043–1048: `grad_ready → print(f"  → {GRADUATION_CUE}")`) — the additive cue model; add `RELEASABLE_CUE` + `_releasable` printed the SAME way (a new line only when ≥1; non-ready output byte-identical).
  - state model: `state["milestones"]` (live dict) · `state["archived"]` (list of compacted milestone slugs) · `state["tasks"]` (gate/waiver). Reusable gathers: `_collect_open_deltas(root)`, waivers (`gate==RISK-ACCEPTED` + `t["waiver"]` {owner·ticket·expires}), residue gates (`gate in RISK-ACCEPTED/HARD-STOP`), RETRO records (glob `milestones/*/RETRO.md` + `archive/*/RETRO.md`).
  - NEW `RELEASES.md` at the project root — the append-only ledger. release-report READS it (parses released milestone slugs from rows) → the attribution source: a milestone is released iff named in a row. **Missing/malformed file → fail-open: all closed milestones releasable.**
Context (working folder): MILESTONE.md shared decisions (RELEASES.md-membership attribution · gather-not-judge · the 5 record-sets · the order-after-fold). The `release.md` guide (task 1, DONE) SPECIFIES this command — release-report realizes the guide's `gather` step + the `→ releasable` cue. The guarded `add.py release` (writes RELEASES.md) is the sibling `release-command` task, NOT this one.
Honors (patterns / conventions): gather-not-judge (no readiness/score/ranking field) · exit 0 always except `no_project` · PURE function, NO writes (mirrors `graduation_data`/`report_data`) · 3-home engine byte-parity (the md5 `test_engine_untouched`-style guard + bundle-parity tests) · design-for-failure: missing/malformed RELEASES.md → fail-open (all closed releasable), unreadable source SKIPPED never crash.
Anchors the contract cites: `release_data` · `cmd_release_report` · `RELEASABLE_CUE` · `_releasable` · the `RELEASES.md` row schema (the attribution-read) · `graduation_data` (the mirrored template).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py release-report` — a read-only command that GATHERS the release inventory into labeled record-sets (text + `--json`), plus a `→ releasable: N` status cue, plus the `RELEASES.md` append-only ledger schema it reads for attribution. Mirrors `graduation-report`; PURE; exit 0 always.
Framings weighed: mirror `graduation_data`/`cmd_graduation_report` exactly (chosen — same gather-not-judge shape; one dict drives both the text and `--json` views) · a bespoke report shape (rejected — needless divergence) · fold the report into `status` (rejected — `status` shows only the cue; the report is the richer gather).
Must:
<must>
  - RELEASE_DATA (PURE): `release_data(root, state)` returns a dict of 5 record-sets + a summary, NO writes (mirrors `graduation_data`). The 5: (1) releasable milestones (closed, not in RELEASES.md) — slug · goal · RETRO carried-delta count; (2) the consolidated "what changed" for them (PROJECT §Key-Decisions rows + RETRO records); (3) open RISK-ACCEPTED waivers (soonest-expiry first); (4) open HARD-STOP residue (the blocker set, security called out); (5) §2 scenarios → monitor candidates (the coverage proxy).
  - REPORT CMD: `cmd_release_report` prints a text dashboard (default) or `--json` (the facts interface) from release_data. **Exit 0 ALWAYS**; the ONLY non-zero is `no_project`. Judges nothing.
  - THE CUE: a `RELEASABLE_CUE` const + `_releasable(root, state)` → the count of closed-but-unreleased milestones; `cmd_status` prints `→ releasable: N milestone(s) closed since last release` ONLY when N≥1 (additive — the non-releasable output is byte-identical to today).
  - ATTRIBUTION-READ: a milestone is "released" iff it appears in a `RELEASES.md` row's `milestones:` line; "closed" = a milestone whose milestone-done gate passed (live-done OR archived). releasable = closed − released.
  - LEDGER SCHEMA: define `RELEASES.md` (project root) as newest-first append-only per-release blocks — `## <version> — <date>` then `milestones:` (comma/space slugs) · `waivers:` · `evidence:` lines. release-report only READS it (parses the `milestones:` lines).
  - FAIL-OPEN: a missing / malformed / unreadable RELEASES.md → treat as zero released (all closed milestones releasable); never crash.
  - 3-HOME PARITY: the engine edit is byte-identical across the 3 `add.py` homes; the bundled wheel + dogfood `.add/tooling` stay md5-equal.
</must>
Reject:
<reject>
  - `release_data` or `cmd_release_report` performs a WRITE / mutation -> "report-not-pure"
  - the report emits a readiness verdict / score / ranking -> "judging-not-gathering"
  - a non-`no_project` path exits non-zero (the gather must be exit 0) -> "gather-exits-nonzero"
  - a missing / malformed RELEASES.md crashes instead of fail-open -> "ledger-read-fragile"
  - the 3 `add.py` homes diverge -> "engine-drift"
</reject>
After:
<after>
  - `add.py release-report` prints the 5 record-sets (text + `--json`) and exits 0; `status` shows `→ releasable: N` when ≥1 closed-unreleased milestone exists and is silent otherwise; RELEASES.md is READ (never written) for attribution; missing RELEASES.md → all closed releasable; the 3 engine homes are byte-identical.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "closed" = milestone whose milestone-done gate passed (live-done OR archived), NOT strictly "done AND archived" — lowest confidence because `release.md` prose says "done AND archived"; I generalize because a milestone-done milestone is closed whether or not it has been compacted, and this project has many done-but-unarchived milestones. If wrong: the cue under/over-counts. Mitigation: archived ⊂ done; define closed = done-gate-passed and note it in the report legend.
  - [ ] the RELEASES.md block schema (`## ver — date` + `milestones:`/`waivers:`/`evidence:`) over a markdown table — treated settled (a `milestones:` line is trivially + robustly parseable; the table is the changelog/book's job, not the attribution source).
  - [ ] the "consolidated what-changed" record-set draws from §Key-Decisions rows + RETRO records — treated settled (those ARE the consolidated deltas after `fold.md`).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: release_data gathers the five record-sets
  Given a project with ≥1 closed milestone
  When `add.py release-report --json` runs
  Then the JSON has releasable, changed, waivers, blockers, monitors, and a summary of counts
  And no readiness verdict / score / ranking field is present

Scenario: the report is read-only
  Given a project
  When release_data(root, state) is called
  Then it returns a dict and writes nothing
  And state.json and every file on disk are byte-unchanged

Scenario: the gather always exits zero
  Given a project (any state)
  When `add.py release-report` runs
  Then it exits 0
  And only a missing project (no_project) exits non-zero

Scenario: the cue fires for a closed-unreleased milestone and clears once attributed
  Given ≥1 milestone is closed and absent from RELEASES.md
  When `add.py status` runs
  Then it prints `→ releasable: N milestone(s) closed since last release`
  And after a RELEASES.md row names that milestone the cue count drops (silent at 0; non-releasable output byte-identical)

Scenario: attribution reads RELEASES.md membership
  Given a RELEASES.md row whose `milestones:` line names a closed milestone
  When release_data computes releasable
  Then that milestone is excluded from releasable
  And a milestone on no row stays releasable

Scenario: a missing or malformed ledger fails open
  Given no RELEASES.md (or a malformed one)
  When release-report / the cue runs
  Then all closed milestones are treated as releasable and nothing crashes
  And the run still exits 0

Scenario: the three engine homes stay byte-identical
  Given the add.py edit
  When it lands
  Then add-method/tooling, .add/tooling, and the bundled wheel are md5-identical
  And a diverged home is rejected with "engine-drift"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
RELEASE-REPORT CONTRACT — read-only gather + the releasable cue + the RELEASES.md ledger schema

command: add.py release-report [--json]
  stdout: text dashboard (default) | JSON facts (--json)
  exit:   0 ALWAYS · non-zero ONLY for no_project   (gather, never a gate)
  writes: NONE (PURE)

release_data(root, state) -> dict {
  releasable: [ {slug, goal, carried_deltas} ]                  # closed (done-gate-passed) − released
  changed:    [ {milestone, key_decisions:[…], retro: path|null} ]   # consolidated "what changed"
  waivers:    [ {slug, owner, ticket, expires} ]                # open RISK-ACCEPTED, soonest expiry first
  blockers:   [ {slug, gate} ]                                  # open HARD-STOP residue (security called out)
  monitors:   [ {slug, scenarios|proxy} ]                       # §2 scenarios → live-monitor candidates
  summary:    { releasable, changed, waivers, blockers, monitors }   # counts only — NO verdict field
}

cue: RELEASABLE_CUE + _releasable(root, state) -> int
  cmd_status prints "  → releasable: N milestone(s) closed since last release"  ONLY when N≥1
  (additive; non-releasable status output byte-identical to today)

attribution: a milestone is "released" iff its slug appears on a RELEASES.md `milestones:` line.
  closed = milestone-done gate passed (live-done OR archived).   releasable = closed − released.

RELEASES.md schema (project root; release-report READS, the sibling release-command WRITES) —
newest-first, append-only, per-release blocks:
  ## <version> — <YYYY-MM-DD>
  milestones: <slug>[, <slug>…]
  waivers: <none | slug…>
  evidence: <free text>

fail-open: missing / malformed / unreadable RELEASES.md → 0 released (all closed releasable); never crash.
3-home parity: the add.py edit is byte-identical across the 3 engine homes.

reject: report-not-pure · judging-not-gathering · gather-exits-nonzero · ledger-read-fragile · engine-drift
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-16
Least-sure flag surfaced at freeze: [spec] the "closed" predicate — done-gate-passed (live-done OR archived) vs the `release.md` prose's literal "done AND archived". Chose the broader done-gate (archived ⊂ done) so done-but-not-yet-compacted milestones still count. If wrong: the `→ releasable` cue over/under-counts — a `_releasable` predicate tweak, no schema change.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: each Must + each Reject has a test; assert behavior (record-sets, purity, exit code, cue, attribution, fail-open, parity) via the public CLI / release_data, not internals.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_release_data_five_sets: `--json` has releasable · changed · waivers · blockers · monitors · summary
  - test_release_data_pure: state dict + on-disk files byte-unchanged after release_data() [guards report-not-pure]
  - test_exit_zero_always: a normal release-report exits 0; only no_project exits non-zero [guards gather-exits-nonzero]
  - test_cue_fires_and_clears: status prints `→ releasable: N` with a closed-unreleased milestone; drops/silent once a RELEASES.md row names it (N=0 silent; non-releasable output byte-identical)
  - test_attribution_read: a milestone on a RELEASES.md `milestones:` line is excluded from releasable; one on no row stays releasable
  - test_fail_open_ledger: missing RELEASES.md → all closed releasable, no crash, exit 0; a malformed file → same [guards ledger-read-fragile]
  - test_not_judging: no readiness/score/verdict/ranking key anywhere in `--json` [guards judging-not-gathering]
  - test_engine_3home_parity: md5 of the 3 add.py homes equal [guards engine-drift]
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_min_pillar.py` `./tests/`   — the release-report command + cue + _releasable + release_data in the 3 byte-identical engine homes, the ENGINE_MD5 pin recomputed (legit engine change, like a version bump — `test_release_1_5_0` asserts 3-home parity vs this pin), the subcommand-census ratification (`test_min_pillar.py` LIFECYCLE += release-report — the self-maintaining guard EVERY new-subcommand task must touch, exactly the pre-noted discovery below), and this task's guard tests. NO RELEASES.md (the sibling release-command writes it; tests use temp fixtures). DISCOVER at build: any CLI-surface/help-list guard that counts subcommands → register additively (the compact-guide lesson).
Strategy (ordered batches): 1. write `./tests/` red · 2. implement `release_data` + `cmd_release_report` + `RELEASABLE_CUE` + `_releasable` + the `release-report` subparser + the status cue print in ONE home `add-method/tooling/add.py` · 3. copy that add.py byte-identical to the other 2 homes (md5) · 4. recompute + update `engine_pin.ENGINE_MD5` · 5. run green (this suite + full engine suite).
Safety rule (feature-specific): release_data is PURE (no writes); RELEASES.md reads are wrapped fail-open (missing/malformed → 0 released, never raise); the 3 add.py homes written from ONE source (write-once-copy) so parity is structural.
Code lives in: the 3 add.py engine homes + engine_pin.py
Constraints: do NOT change any test or the frozen contract; gather stays exit-0 + write-free; allow-list only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — release-report suite 8/8 + full add-method engine suite 1152/1152 green
- [x] coverage did not decrease — +8 new task tests; engine suite count steady at 1152 (no test lost); +2 LIFECYCLE census entries
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the red suite is byte-unchanged since it went red (tripwire re-snapshot clean); the only existing-test edit is ADDITIVE (test_min_pillar LIFECYCLE += release-report — the self-maintaining census, never weakened)
- [x] the green was EARNED, not gamed — adversarial self-refute: each of the 8 tests exercises REAL behavior (cue fire→clear via status, attribution include/exclude via a real RELEASES.md, fail-open on a malformed ledger, state-bytes purity, gather-not-judge token ban, 3-home md5 parity) — none vacuous, overfit to a fixture, or stubbed; the dogfood run (38 releasable, cue fired, report rendered) corroborates on real data
- [x] concurrency / timing of the risky operation is safe — release_data + the cue are READ-ONLY (no save_state, no locks); a concurrent writer only yields a snapshot-consistent stale read, the floor every read command already lives with
- [x] no exposed secrets, injection openings, or unexpected dependencies — read-only; NO new imports (re/json/date/Path already present); no shell/eval/network; parses text, never executes it
- [x] layering & dependencies follow CONVENTIONS.md — mirrors graduation_data/cmd_graduation_report verbatim (the gather-not-judge pattern); the cue is additive to cmd_status (a line only when releasable); 3 engine homes written from ONE source (structural parity) + engine_pin re-aimed; capability-as-prose / engine-records-never-acts honored (no tag/publish/deploy)
- [x] a person reviewed and approved the change — Tin Dang approved PASS at the conservative gate (2026-06-16)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — release_data ← cmd_release_report ← the `release-report` subparser (set_defaults); _releasable ← BOTH the cmd_status cue AND release_data; _released_milestones/_closed_milestones/_releases_path/_key_decisions_for ← release_data; RELEASABLE_CUE/RELEASES_FILE referenced. Confirmed by 8 tests + the live dogfood run.
- [x] DEAD-CODE (code) — no orphaned symbol: every new helper/constant has a caller (verified by grep + the suite); no leftover scaffold.
- [x] SEMANTIC (non-code) — disclosed change (close-gap-before-gate): §5 Scope was amended at verify to declare `add-method/tooling/test_min_pillar.py` (the subcommand-census every new-command task must ratify — pre-noted in §5's "DISCOVER at build" line), then tests→build was re-crossed so the scope anchor re-snapshots cleanly with the amended §5 (the documented legit re-cross; `check` now 0 scope findings). Design choice surfaced for review: the RELEASES.md read FAILS OPEN (missing/malformed → all closed milestones read releasable) — the safe direction (over-surface work, never silently hide an unreleased milestone).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-16

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the cue fires-then-clears on attribution; the RELEASES.md read stays fail-open on a malformed ledger; release_data never writes.
Spec delta for the next loop: "closed" was generalized to done-gate-passed (live-done OR archived), not the guide's literal "done AND archived" — the §1 lowest-confidence flag; release-command must adopt the SAME predicate so the cue and the writer agree.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the §5 scope gate reads `declared` from the state.json ANCHOR frozen at tests→build, NOT live §5 — a legitimate mid-build scope expansion must amend §5 AND re-cross tests→build to re-snapshot, not just edit the prose (evidence: `check` stayed red on test_min_pillar.py after the live §5 edit, cleared only after `phase tests` → `advance` re-snapshot)
- [ADD · folded] a new subcommand redds test_min_pillar.test_every_subcommand_is_covered (the self-maintaining census) — register it additively in LIFECYCLE, exactly as §5's "DISCOVER at build" line pre-warned (evidence: the full engine suite went 1 failure → 0 after `LIFECYCLE += release-report`)
- [TDD · folded] mirroring the graduation_data harness (temp project + add.main capture + direct state seeding) produced 8 honest RED-first tests with zero throwaway scaffolding (evidence: the 5 behavioral tests were RED for the right reason — argparse exit 2 / no cue — then GREEN unchanged after build)
- [SDD · folded] attribution-via-RELEASES.md-membership (vs a per-milestone `released_in:` marker) keeps the cue read-only over compacted milestones (evidence: dogfood `status → releasable: 38` read only state.json + RELEASES.md, never opened a milestone file)
