# TASK: Engine guards the merge-time fork-base echo on merge-back

slug: engine-merge-base-enforcement · created: 2026-06-11 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from the auto default (human-confirmed 2026-06-11): trust-layer / method-defining scope — the high-risk guard (run.md) demands a human verify gate; the engine refuses an unguarded completion (`unguarded_high_risk_auto`). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): VERIFIED 2026-06-11 — the engine has NO wave verb today; its only wave surface is the existence-only `status` resume hint (add.py:858–865, globs `.add/milestones/*/WAVE.md`). `cmd_check` (checks list of (ok,label,reason) tuples → red FAILs; `warnings` list → measure-not-block WARNs, precedent `goal_not_auto_ready` at add.py:1140, rendered `WARN <name> <reason>` at :1178). The ledger artifact: `.add/milestones/<m>/WAVE.md` per the streams.md template (header `wave/opened/status: live|merging` · `base: <sha>` · `### Roster` table with fork-base cell = column 3 · `### Merge order`). The verb census: `test_min_pillar.py` LIFECYCLE (line 56) executes every argv under a read-spy; `test_every_subcommand_is_covered` asserts parser-verbs == covered BOTH ways (closed census); `_NONZERO_OK` tolerates refusal verbs (precedent: heal). ENGINE change → pin bump ×3 + re-sync (`engine_pin.ENGINE_MD5`); prose change → streams.md ×3 mirrors (`add-method/skill/add/` · `_bundled/skill/add/` · `.claude/skills/add/`).
Context (working folder): the deferred half of `wave-protocol-runtime` (PASS 2026-06-11). That task shipped the prose-discipline; its frozen lowest-confidence flag named this enforcement as explicitly DEFERRED. v19 wave delta #7 (merge-time fork-base) is the source; CONVENTIONS:90 + streams.md:74–80/119–126 already STATE the rule — this task makes the engine EXECUTE it. Enforcement form A+B human-chosen at co-specify (status-aware `check` + new `wave-verify` verb).
Honors (patterns / conventions): CLAUDE.md "MUST design for failure" (fail-closed parse); the wave-ledger evidence-cell convention (pasted output, never a tick); the release-gate pin-bump ×3 idiom; census-guard-whole-and-closed (new verb → LIFECYCLE row); words-exist≠method-works (the exact recursion this closes); design-for-failure-shifts-never-skips (this task's own §7 sibling delta from wave-protocol-runtime). CHANGE-REQUEST 2026-06-11: heal_exhausted HARD-STOP → human routed re-freeze; bundle reopened at specify — the ONLY honest door for both the v2 clause and suite-hardening (the frozen suite could not absorb the refute-discovered vectors).
Anchors the contract cites: `cmd_check` (checks/warnings seams, add.py:1140/1178) · the `status` wave hint glob (add.py:862) · `.add/milestones/<m>/WAVE.md` grammar (streams.md:103–117) · `unverified_fork_base` · `test_min_pillar.py` LIFECYCLE/`_NONZERO_OK` · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the engine EXECUTES the wave-ledger fork-base rule streams.md only states: every roster row's pasted `rev-parse HEAD` echo must equal the wave `base:`. Two surfaces (A+B, human-chosen at co-specify 2026-06-11): (A) `add.py check` validates every existing WAVE.md, status-aware, as the standing monitor; (B) a NEW read-only `wave-verify` verb is the explicit merge-time gate the orchestrator runs before the first merge-back. Closes the enforcement-deferral recorded at wave-protocol-runtime's freeze (v19 wave delta #7) — the rule is prose-only today (words-exist ≠ method-works).
Framings weighed: status-aware check + explicit wave-verify verb (chosen — A+B: standing monitor AND merge ritual) · check-only (rejected by human — fires only when check happens to run) · gate-hook (rejected — wrong locus: gates run worker-side in worktrees; WAVE.md is orchestrator-owned and workers never read it)
Must:
<must>
  - check: for every `.add/milestones/*/WAVE.md` — a FILLED fork-base cell whose sha does not match `base:` is RED `unverified_fork_base` at ANY status; at `status: merging` an unfilled/placeholder row is ALSO RED `unverified_fork_base` (merge-time strictness); at `status: live` an unfilled row is only WARN `fork_base_pending` (measure-not-block, mirrors goal_not_auto_ready — workers may not have step-0-synced yet)
  - check: an unparseable ledger (no base sha · no `status: live|merging` · no roster row) is RED `wave_ledger_malformed`, naming WHAT failed to parse (fail-closed, never a silent skip)
  - wave-verify [milestone]: read-only and judgment-free — strict at any status: exit 0 ONLY when every roster row's echo matches `base:`, printing a per-row report; NEVER mutates the ledger, the status field, or state.json
  - wave-verify resolves its target: explicit milestone argument, else the single existing WAVE.md
  - sha match := exact equality, or prefix-match where both tokens are ≥7 hex chars (git short-sha tolerant)
  - echo-column resolution (v2, change-request 2026-06-11): the roster header row must contain EXACTLY ONE column whose label matches the fork-base token — zero matching columns is malformed (already enforced); MORE than one (e.g. a decoy `fork-base-prev` beside the real `fork-base (pasted)`) is RED `wave_ledger_malformed` naming the colliding labels — ambiguity refusal, never first-wins on a hand-written artifact
  - the six refute-discovered drift vectors stay closed as pinned regressions: drift-note cell (multi-token echo) · body-prose status rescue · later-wave:-line status rescue · shifted column · headerless roster · empty base: line
  - status resolution (v3, change-request 2026-06-11): the status value is the exact token after `status:` on the wave header line, terminated ONLY by whitespace, the `·` separator, or end-of-line; it must EQUAL `live` or `merging` — the unfilled template placeholder (`live|merging`) and suffix drift (`live-ish`, `merging-soon`) are RED `wave_ledger_malformed` naming the bad token (regex `\b` is never a terminator on hand-written input)
  - the pass-5 vectors stay closed as pinned regressions: placeholder-status + matching echo · placeholder-status + pending row (the standing-monitor harm case) · suffix-drift status
  - status field anchoring (v4, change-request 2026-06-11): the `status:` label must itself START a field — preceded by start-of-line, whitespace, or the `·` separator; an embedded substring (`substatus: live`) is NOT a status field, so a header whose only status-like text is embedded has NO status field → RED `wave_ledger_malformed` (the existing no-status path; pass-6 observation N12 closed)
  - a project with no WAVE.md: check emits NO new line (regression-silent); the 850-test baseline stays green
</must>
Reject:
<reject>
  - wave-verify finds no WAVE.md (bare, or the named milestone has none) -> "wave_not_found"
  - wave-verify bare with more than one WAVE.md -> "wave_ambiguous" (names them; pick one)
  - any mismatched echo, or a missing echo at merge-time -> "unverified_fork_base" (check RED / wave-verify exit 1)
  - unparseable ledger -> "wave_ledger_malformed" (check RED / wave-verify exit 1; fail-closed)
  - more than one fork-base-matching roster header column -> "wave_ledger_malformed" naming the colliding labels (ambiguity refusal — v2)
  - status token not exactly `live`/`merging` (the unfilled placeholder `live|merging`, suffixed `live-ish`/`merging-soon`) -> "wave_ledger_malformed" naming the bad token (strict terminator — v3)
  - a wave header whose only status-like text is an EMBEDDED label (`substatus: live`, no real status field) -> "wave_ledger_malformed" (no status field — left anchor, v4)
</reject>
After:
<after>
  - the merge-time fork-base rule is engine-executed on both surfaces; streams.md (×3 mirrors) names `add.py wave-verify` as the merge-time gate before merge-back; `wave-verify` is census-classified (LIFECYCLE + `_NONZERO_OK`); engine pin re-aimed, ×3 trees byte-identical
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ (v3) the strict terminator set {whitespace, `·`, end-of-line} flips the failure direction — an orchestrator who writes a VALID intended status followed by an unlisted separator (`status: live,` or `status: live.`) now gets a false RED `wave_ledger_malformed`; if wrong: alert fatigue, the v1 lowest-confidence worry. Cost judged right: on the trust layer a false red that trains template conformance beats a false green that waves an unfilled ledger through; the template puts status last on the header line so EOL covers the canonical write.
  ⚠ (v2) a SINGLE wrong-but-matching header label (a decoy `fork-base-prev` ALONE, real column absent) is still accepted as the echo column — substring tolerance is deliberate (real labels carry prose: `fork-base (pasted)`), and ambiguity refusal only closes the >1 case; if wrong: a ledger that renamed the real column away while keeping one decoy could aim the check at the wrong cells. Cost judged acceptable at mvp: that drift requires rewriting the template header, and the fail-closed malformed paths still catch the structural variants. Change-request surface if stricter matching is wanted.
  ⚠ the WAVE.md grammar the engine parses (the `base:` line · the `status:` field · roster column 3) matches what orchestrators actually WRITE — lowest confidence because the ledger has exactly ONE dogfood instance so far and hand-written markdown drifts; if wrong: false `wave_ledger_malformed` reds train orchestrators to ignore the standing monitor — alert fatigue ON the trust layer. Mitigation: parse exactly the streams.md template grammar; fail-closed messages name the unparseable piece. [v2 note: VINDICATED by four refute passes — hand-written drift produced 6 contract-violating vectors; the v2 clause + pinned fixtures are the structural answer.]
  - [ ] WARN-not-red at `status: live` is the right friction — a live wave legitimately has pending rows before step-0 echoes land; red there would cry wolf.
  - [ ] prefix-match ≥7 hex is collision-safe for fork-base equality (git's own short-sha standard).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: check goes red on a filled-but-mismatched echo (any status)
  Given a board with milestone "mvp" and a WAVE.md at status live whose roster row echo != base
  When add.main runs check
  Then check exits non-zero and prints FAIL unverified_fork_base
  And state.json and WAVE.md are unchanged

Scenario: check goes red on a pending row at merge time
  Given a WAVE.md at status merging with one roster row still holding the paste-placeholder
  When add.main runs check
  Then check exits non-zero and prints FAIL unverified_fork_base

Scenario: check only WARNs on a pending row while live
  Given a WAVE.md at status live with one placeholder row and no other defect
  When add.main runs check
  Then check prints WARN fork_base_pending and the wave adds NO red finding

Scenario: check fails closed on an unparseable ledger
  Given a WAVE.md whose base: line carries no sha (template placeholder left in)
  When add.main runs check
  Then check exits non-zero and prints FAIL wave_ledger_malformed naming the missing piece

Scenario: no ledger, no noise (regression)
  Given a board with no WAVE.md anywhere
  When add.main runs check
  Then no wave_* line appears and the exit code matches today's behavior

Scenario: wave-verify passes a fully-echoed roster
  Given a WAVE.md (any status) where every roster echo matches base
  When add.main runs wave-verify
  Then exit 0 with a per-row report
  And the ledger file is byte-identical after the call (read-only)

Scenario: wave-verify refuses a mismatch or a pending row
  Given a WAVE.md with a mismatched or placeholder echo
  When add.main runs wave-verify
  Then exit non-zero with unverified_fork_base
  And WAVE.md is unchanged   # required for every rejection

Scenario: wave-verify names its target or refuses
  Given no WAVE.md -> wave_not_found; two WAVE.md files and a bare call -> wave_ambiguous
  When add.main runs wave-verify [bare]
  Then the named refusal fires and nothing is mutated

Scenario: short-sha tolerance
  Given base holds a 40-hex sha and a roster echo holds its 12-hex prefix
  When check and wave-verify run
  Then both treat the row as matching

Scenario: the verb is census-classified and the engine re-anchors
  Given the build is complete
  When test_min_pillar's closed census and the pin guards run
  Then wave-verify is in LIFECYCLE (read-spy exercised, nonzero tolerated) and md5(add.py) == re-aimed ENGINE_MD5 across the x3 copies

Scenario: ambiguity refusal on a decoy fork-base column (v2)
  Given a WAVE.md whose roster header carries BOTH a decoy "fork-base-prev" column and the real "fork-base (pasted)" column, and the real echo does not match base
  When add.main runs check and wave-verify
  Then both fail with wave_ledger_malformed naming the colliding labels — never a silent first-wins pass
  And WAVE.md is unchanged

Scenario: the refute-discovered drift vectors stay closed (v2 regression pins)
  Given six ledgers, one per healed vector — a drift-note echo cell (mismatch + base-prefix token), a status-less header with rescuing body prose, a status-less header with a later wave:-prefixed body line, a roster with an extra leading column, a headerless roster, an empty base: line
  When check and wave-verify run on each
  Then each is refused per the contract (FAIL/exit 1 with its named code) — no vector regresses to a silent pass

Scenario: the unfilled status placeholder is malformed (v3)
  Given a WAVE.md whose header still carries the literal template text "status: live|merging", base filled with a real sha, and EITHER every echo matching OR a pending placeholder row
  When add.main runs check and wave-verify
  Then BOTH fail with wave_ledger_malformed naming the bad status token — an unfilled status is never parsed as live, and the standing monitor never downgrades it to a WARN
  And WAVE.md is unchanged

Scenario: status suffix drift is malformed (v3)
  Given a WAVE.md whose header reads "status: live-ish" (and a sibling with "status: merging-soon"), echoes matching base
  When check and wave-verify run
  Then both fail with wave_ledger_malformed — `live`/`merging` must be the exact token, terminated by whitespace, the · separator, or end-of-line

Scenario: an embedded status-like label is not a status field (v4)
  Given a WAVE.md whose header reads "wave: 1 · opened: 2026-06-11 · substatus: live" with NO real status field, base filled, every echo matching
  When add.main runs check and wave-verify
  Then both fail with wave_ledger_malformed — `substatus:` never anchors the status parse; a header without a real status field has no status
  And WAVE.md is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py check                       (standing monitor — wave-ledger section, fail-closed, read-only)
  for every .add/milestones/*/WAVE.md:
    FILLED echo != base (any status)            -> FAIL "unverified_fork_base"
    pending/placeholder row @ status: merging   -> FAIL "unverified_fork_base"
    pending/placeholder row @ status: live      -> WARN "fork_base_pending"   (never red)
    no base sha | no status live|merging | no roster row
                                                -> FAIL "wave_ledger_malformed: <missing piece>"
    >1 fork-base-matching header column (v2)    -> FAIL "wave_ledger_malformed: ambiguous fork-base columns <labels>"
    no WAVE.md anywhere                         -> no new output (regression-silent)

add.py wave-verify [milestone]     (merge-time gate — read-only, judgment-free, strict at any status)
  exit 0 -> every roster echo matches base; per-row report printed
  exit 1 -> "unverified_fork_base: <rows>" | "wave_ledger_malformed: <why>"
          | "wave_not_found" | "wave_ambiguous: <m1, m2 — name one>"
  NEVER mutates WAVE.md, the status field, or state.json.

sha match := exact, OR prefix-match with both tokens >=7 hex chars (git short-sha tolerant).
echo column := the EXACTLY-ONE roster header column whose label matches the fork-base token (v2);
        zero matching columns OR more than one -> "wave_ledger_malformed" (ambiguity refusal —
        never first-wins on a hand-written artifact). The six refute-discovered drift vectors
        are pinned suite fixtures (regressions, never silent passes).
status := the exact token after `status:` on the wave header line, terminated ONLY by
        whitespace, the `·` separator, or end-of-line; it must EQUAL `live` or `merging` (v3).
        The unfilled template placeholder (`live|merging`) or any suffixed variant
        (`live-ish`, `merging-soon`) -> FAIL "wave_ledger_malformed: <bad token>" on BOTH
        surfaces, at any echo state — never parsed as its valid prefix, never a WARN.
        The three pass-5 vectors are pinned suite fixtures.
        The `status:` label must itself START a field — preceded by start-of-line,
        whitespace, or `·` (v4): an embedded `substatus: live` is NOT a status field, and a
        header with no real status field -> FAIL "wave_ledger_malformed" (no status).
        The pass-6 vector is a pinned suite fixture.
Schema: NO state.json change; reads WAVE.md only. ENGINE change -> engine_pin.ENGINE_MD5 re-aimed,
        x3 trees byte-identical. Census: wave-verify added to test_min_pillar LIFECYCLE +
        _NONZERO_OK (refusal verb in the no-wave board, precedent: heal). Prose: streams.md
        (x3 mirrors) names `add.py wave-verify` as the merge-time gate before merge-back.
```

Status: FROZEN @ v4 — approved by Tin Dang (2026-06-11, in-chat freeze approval; the close-gap-before-gate micro change-request on pass-6 N12; targeted pass-7 scope approved at the same freeze). v4 delta: the status-label left-anchor rule + the substatus fixture pinned.
Least-sure flag surfaced at freeze: ⚠ [contract] the v4 anchor set {start-of-line, whitespace, `·`} mirrors the v3 terminator set, so a punctuation-wrapped but INTENDED status (`(status: live)`) is now a false RED — same deliberately-chosen failure direction as v3: on the trust layer a false red that trains template conformance beats a false green. ⚠ [test] targeted scope: pass 7 re-executes the known vectors + the status-anchor family only, NOT a fresh 19-probe hunt — proportionate to a one-line delta whose pass 6 already swept the surrounding surface; if that proportionality is wrong, a full pass is the change-request surface.
Prior freeze flags (v3/v2, resolved into history): the terminator + ambiguity clauses shipped; pass 6 re-executed all 13 known-vector points and confirmed every one refused with its named code (VERDICT: EARNED, findings empty).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: all 15 scenarios pinned (10 @ v1 + 2 @ v2 + 2 @ v3 + 1 @ v4); suite-level coverage not decreased. v1 red driver: the verb did not exist. v2 red driver: the decoy-column ambiguity fixture (5 healed-vector pins declared GREEN at write — honest pins). v3 red drivers: both fixtures RED against the shipped `\b` matcher. v4 red driver: the substatus-header fixture is RED against the shipped left-unanchored regex (greens both surfaces today, pass-6 N12).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_check_red_on_mismatched_echo: arrange board + WAVE.md live, echo != base / act check / assert exit!=0 + "unverified_fork_base" + ledger unchanged
  - test_check_red_on_pending_at_merging: WAVE.md merging, placeholder row / check / exit!=0 + "unverified_fork_base"
  - test_check_warns_on_pending_at_live: WAVE.md live, placeholder row / check / "WARN  fork_base_pending" printed, NO wave FAIL line
  - test_check_fail_closed_malformed: WAVE.md with placeholder base / check / exit!=0 + "wave_ledger_malformed"
  - test_check_silent_without_ledger: no WAVE.md / check / no "wave_" token in output; exit matches a clean board
  - test_wave_verify_passes_full_roster: all echoes == base / wave-verify / exit 0 + per-row report + file bytes identical
  - test_wave_verify_refuses_mismatch: mismatched + placeholder variants / wave-verify / exit 1 + "unverified_fork_base" + file unchanged
  - test_wave_verify_target_resolution: none -> "wave_not_found"; two ledgers bare -> "wave_ambiguous"; explicit milestone arg resolves
  - test_short_sha_prefix_matches: base 40-hex, echo 12-hex prefix / check + wave-verify / both treat as match
  - test_census_and_pin: wave-verify present in test_min_pillar LIFECYCLE (closed census both ways) + md5(add.py) == ENGINE_MD5 across the x3 copies
  - test_ambiguity_refusal_decoy_column (v2 — RED driver): header carries decoy `fork-base-prev` AND real `fork-base (pasted)`; real echo != base / check + wave-verify / both exit!=0 + "wave_ledger_malformed" naming the ambiguity + ledger unchanged
  - test_drift_vectors_stay_closed (v2 — green pins): the 5 healed vectors as fixtures (drift-note cell · body-prose status rescue · later-wave:-line rescue · shifted column · headerless roster · empty base line), each asserting its NAMED refusal code on both surfaces
  - test_status_placeholder_is_malformed (v3 — RED driver): header carries the literal template text `status: live|merging` ×(matching echo · pending row) / check + wave-verify / both exit!=0 + "wave_ledger_malformed" + NO fork_base_pending WARN downgrade + ledger unchanged
  - test_status_suffix_drift_is_malformed (v3 — RED driver): `status: live-ish` and `status: merging-soon` with matching echoes / check + wave-verify / both exit!=0 + "wave_ledger_malformed"
  - test_status_label_left_anchored (v4 — RED driver): header `wave: 1 · opened: 2026-06-11 · substatus: live` with NO real status field + matching echo / check + wave-verify / both exit!=0 + "wave_ledger_malformed" + ledger unchanged
</test_plan>

Tests live in: `add-method/tooling/test_merge_base_enforcement.py` · MUST run red (missing implementation) before Build. Declared census edit (tests-phase, pre-freeze): `test_min_pillar.py` gains the `["wave-verify"]` LIFECYCLE row + `_NONZERO_OK` membership — red pre-build via the closed census (LIFECYCLE names a verb the parser does not expose).
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the check SHIFTS, never SKIPS — an unparseable ledger is NEVER a silent pass (`wave_ledger_malformed`, fail-closed), and `wave-verify` NEVER mutates anything (read-only gate). A false-negative here un-guards the trust layer; a silent skip is worse than a false red.
Code lives in: the engine trees — `add-method/tooling/add.py` (canonical) synced byte-identical ×3 + `engine_pin.py` re-aim; prose in `add-method/skill/add/streams.md` mirrored ×3 (`_bundled` + `.claude/skills/add`).
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — no new deps); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 860/860 on py3.10 AND py3.14 after every heal cycle
- [x] coverage did not decrease — 850 → 860 (+10, one per §2 scenario); census edit strengthens (closed both ways)
- [x] no test or contract was altered during build — three heal cycles fixed SRC ONLY; the red suite + §3 untouched since the tests→build snapshot
- [x] the green was EARNED-scored by FOUR independent adversarial refute passes — pass 1: NOT-EARNED (FG-1 any()-over-sha-tokens · FG-2 unanchored status) → heal 1; pass 2: FG-1/FG-2 CONFIRMED FIXED, new FG-3 (later wave:-line rescues status) → heal 2; pass 3: FG-3 CONFIRMED CLOSED, new P1/P2b/Pex (column-shift · headerless-roster silent skip · base-regex crosses newline) → heal 3; pass 4: heals 1–3 + clean paths CONFIRMED, new N1/N10 (substring+first-wins decoy column steals the echo) → heal cap EXHAUSTED → engine HARD-STOP (heal_exhausted), escalated to the human
- [x] concurrency / timing — read-only parse, no shared state, no mutation on any path (refusal paths byte-compare verified)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib re/pathlib only; error strings echo ledger fragments the user already owns
- [x] layering & dependencies follow CONVENTIONS.md — helpers beside cmd_check; ubiquitous-language lint green; ×3 engine + ×3 streams.md parity held
- [ ] a person reviewed and approved the change — THE OPEN ITEM: `autonomy: conservative` — this gate is the human's; the engine recorded HARD-STOP at the cap and the human now chooses change-request vs abandon

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_wave_ledgers`/`_parse_wave_ledger`/`_sha_match` called from cmd_check wave section + cmd_wave_verify; `cmd_wave_verify` wired via the wave-verify subparser (census-classified); streams.md ×3 names the gate
- [x] DEAD-CODE (code) — no orphan symbol; every helper has ≥2 call sites or a subparser binding
- SEMANTIC — n/a: code task (WIRING/DEAD-CODE path filled)

### GATE RECORD
Recorded (v1, superseded by the human-routed change-request): HARD-STOP — engine-recorded at the bounded self-heal cap (heal_exhausted after 3 honest re-build attempts + a 4th confirmed finding N1/N10; a gamed green is never auto-passed)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: the bounded self-heal loop (engine, mechanical cap); human disposition by Tin Dang 2026-06-11 — CHANGE-REQUEST → re-freeze (bundle reopened at specify via `add.py phase specify`; v2 adds the ambiguity-refusal clause + pins the 6 discovered vectors). This v1 gate record stays as history; the v2 run records its own gate below it at re-verify.

### v2 run (re-freeze 2026-06-11, change-request after heal_exhausted)
- [x] all tests pass — 862/862 on py3.10 AND py3.14 (the +2 v2 tests: ambiguity-refusal red driver + 6-vector pins)
- [x] red-for-the-right-reason confirmed pre-build — the decoy fixture failed on BOTH surfaces (exit 0 against the shipped first-wins matcher); the 5 heal pins were green as declared at the freeze
- [x] coverage did not decrease — 860 → 862; every §2 scenario (12) pinned
- [x] no test or contract was altered during build — fresh tripwire snapshot at the v2 tests→build advance; `add.py check` build_tampered WARN cleared (258 passed, 0 failed)
- [x] engine pin re-aimed (`e12ee9deec0f5562939381cdceac3903`) — ×3 trees byte-identical; ubiquitous-language lint green inside the suite
- [x] refute pass 5 executed (NOT-EARNED) — ALL 7 known vectors re-executed and CONFIRMED closed (heals 1–3 + the v2 ambiguity refusal hold; the ambiguity message names the colliding labels); 24 new probes across 16 input families, 23 conform; ONE new root-cause family found: FG-STATUS-BOUNDARY — `\b` in the status regex fires at non-word chars, so the EXACT unfilled streams.md template placeholder `status: live|merging` (+ matching echo) exits 0 on BOTH surfaces, and (harm) the same placeholder + a PENDING row leaves the standing monitor green (WARN only); orchestrator-confirmed in an independent sandbox reproduction
- [ ] the green is EARNED — NO: FG-STATUS-BOUNDARY is a confirmed contract violation (`no status live|merging -> wave_ledger_malformed`); reported via `add.py heal` → heal cap already exhausted → engine HARD-STOP (5th history entry)
- [ ] a person reviewed and approved the change — `autonomy: conservative`: this gate is the human's

### GATE RECORD (v2)
Recorded (v2, superseded by the human-routed change-request): HARD-STOP — engine-recorded (heal_exhausted — the bounded cap was spent on heals 1–3; the 5th-pass confirmed finding FG-STATUS-BOUNDARY escalates straight to the human, by design)
Reviewed by: refute pass 5 (adversarial audit) + the engine cap; human disposition by Tin Dang 2026-06-11 — CHANGE-REQUEST → re-freeze v3 (strict status terminator via exact token equality; pin the 3 pass-5 fixtures; contracted residues left as accepted tolerances). This v2 gate record stays as history; the v3 run records its own gate below it at re-verify.

### v3 run (re-freeze 2026-06-11, second change-request)
- [x] all tests pass — 864/864 on py3.10 AND py3.14 (the +2 v3 tests: placeholder-status ×2 echo states · suffix-drift)
- [x] red-for-the-right-reason confirmed pre-build — exactly the 4 v3 subtests failed against the shipped `\b` matcher (placeholder+match exit 0 ×2 surfaces · placeholder+pending WARN-downgrade · live-ish/merging-soon exit 0); all 12 prior tests green
- [x] coverage did not decrease — 862 → 864; every §2 scenario (14) pinned
- [x] no test or contract was altered during build — fresh tripwire snapshot at the v3 tests→build advance; `add.py check` 258 passed, 0 failed, build_tampered WARN cleared
- [x] engine pin re-aimed (`32c602e49e18ef16e1dc0f6e3bb3fb08`) — ×3 trees byte-identical; the fix is categorical (token extraction + exact equality — the regex-`\b` class removed, not patched)
- [x] the green is EARNED — refute pass 6 VERDICT: EARNED, findings EMPTY. All 13 known-vector execution points (10 canonical + 3 heal-3 variants) refused with their exact named codes on BOTH surfaces; 19 new probes — every refusal contract-conformant, every green a named contracted tolerance; the K09 harm case confirmed (placeholder-status + pending row → malformed, NO fork_base_pending downgrade); exact-token equality held across all boundary probes (`Live`/`LIVE`/`liveX`/empty/NBSP/full-width-colon all malformed). ONE observation, NOT a finding: N12 `substatus: live` greens (the status regex is left-unanchored — same textual family as healed FG-2/FG-3 but NOT contracted; no real ledger writes it) — disclosed at the gate, disposition the human's
- [ ] a person reviewed and approved the change — `autonomy: conservative`: this gate is the human's

### GATE RECORD (v3)
Recorded (v3, resolved into the v4 run): refute pass 6 EARNED; human disposition by Tin Dang 2026-06-11 on the disclosed N12 observation: CLOSE-GAP-BEFORE-GATE — micro change-request → re-freeze v4 (left-anchor the status field label; one fixture; targeted pass 7), THEN the gate is recorded. This v3 record stays as history; the v4 run records the final gate below it.
Reviewed by: <the v4 run carries the final review>

### v4 run (re-freeze 2026-06-11, close-gap-before-gate micro change-request)
- [x] all tests pass — 865/865 on py3.10 AND py3.14 (the +1 v4 test: substatus left-anchor)
- [x] red-for-the-right-reason confirmed pre-build — exactly the 2 v4 subtests failed (the substatus header greened both surfaces against the shipped left-unanchored regex); all 14 prior tests green
- [x] coverage did not decrease — 864 → 865; every §2 scenario (15) pinned
- [x] no test or contract was altered during build — fresh tripwire snapshot at the v4 tests→build advance; `add.py check` 258 passed, 0 failed
- [x] engine pin re-aimed (`b441421c938f8306773cd81a1859c1be`) — ×3 trees byte-identical; the fix is the one-line anchor `(?:^|[\s·])status:`
- [x] the green is EARNED — targeted refute pass 7 VERDICT: EARNED, findings EMPTY (25/25 execution points). All 11 known vectors refused with their exact named codes on BOTH surfaces; both green controls (clean template · short-sha) passed; 10 status-anchor probes all contract-derived — the v4 substatus vector refuses on both surfaces, a real `status:` field beside a `substatus:` decoy anchors correctly (SA-4/SA-5), a body-line `status:` still never rescues a status-less header (SA-8), and the contracted false-red `(status: live)` behaves exactly as the freeze flag declared; ledger bytes unchanged on every refusal; repo untouched by the audit
- [x] a person reviewed and approved the change — Tin Dang took the conservative gate in-chat 2026-06-11 (PASS recorded with the two riding-along flags disclosed: accepted tolerances into dogfooding · targeted pass-7 scope)

### GATE RECORD (v4 — final)
Outcome: PASS
Reviewed by: Tin Dang (human gate, `autonomy: conservative`) — on the evidence of refute passes 6 + 7 (both EARNED, findings empty), 11/11 pinned vectors re-confirmed, 865/865 ×2 interpreters, tripwire clean · date: 2026-06-11

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): all 10 refute-discovered drift vectors are now pinned suite fixtures — 6 @ v2 (drift-note cell · status-rescue ×2 · column-shift · headerless roster · empty base line) + decoy column @ v2 + the 3 status-boundary vectors @ v3 (placeholder+match · placeholder+pending · suffix drift). The remaining accepted tolerances to watch in dogfooding: lone decoy label · non-hex-case shas → pending · 6-hex echo prefix → pending · false-red on unlisted separators after a valid status token.
Spec delta for the next loop: (v2, SHIPPED) the AMBIGUITY-REFUSAL rule — exactly one roster header column may match the fork-base label. (v3, SHIPPED) the STRICT STATUS TERMINATOR rule — status is the exact token after `status:`, terminated only by whitespace/`·`/end-of-line, equal to `live` or `merging`; token boundaries on hand-written input are terminator-explicit, never regex-`\b`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] a red suite for a PARSER of hand-written artifacts must include grammar-DRIFT fixtures, not only template-conformant ones — the 10-test suite stayed green across 6 contract-violating false-greens found only by adversarial probing (evidence: refute passes 1–4 on engine-merge-base-enforcement)
- [ADD · folded] the bounded self-heal cap held under real fire — 3 honest src-only redos, then a 4th confirmed finding forced heal_exhausted HARD-STOP to the human, exactly as designed; refute-read → heal → re-refute is a working convergence loop (evidence: this task's heal history + gate record)
- [SDD · folded] a fail-closed contract over hand-written input needs an ambiguity-refusal clause (exactly-one-match), or substring/first-wins matching re-opens the fail-open door the contract closed (evidence: N1/N10, 4th refute pass)
- [SDD · folded] regex `\b` is not a token terminator on hand-written input — the unfilled template placeholder `live|merging` parses as its valid prefix `live`, greening an unfilled ledger on both surfaces; keyword grammars over free text must name explicit terminators (whitespace/separator/end-of-line) or use exact token equality (evidence: refute pass 5 FG-STATUS-BOUNDARY on engine-merge-base-enforcement)
- [ADD · folded] close-gap-before-gate converges — a disclosed non-finding observation routed as a micro change-request (one contract sentence · one red fixture · one-line fix · targeted re-refute) closed in a single short cycle and let the gate record a clean PASS instead of a PASS-with-asterisk (evidence: pass-6 N12 → v4 re-freeze → pass-7 EARNED on engine-merge-base-enforcement)
