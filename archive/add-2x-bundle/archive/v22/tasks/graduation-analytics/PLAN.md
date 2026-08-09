# TASK: Read-only graduation-report: cluster MVP-loop evidence (gather, not judge)

slug: graduation-analytics · created: 2026-06-08 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: graduation-analytics — a read-only `add.py graduation-report` (+ `--json`) that harvests the whole MVP loop's accumulated evidence into FIVE labeled record-sets for the graduate.md interview. GATHER, never JUDGE.
Framings weighed: project-wide record-harvest reusing `_collect_open_deltas` + the v9 `report_data`/`--json` precedent (chosen) · aggregate `report_data` cross-milestone into one rollup · thin two-source seam deferring the three fuzzy sources (rejected — the 5 sources are a settled MILESTONE exit criterion, not a framing choice)
Must:
<must>
  - Add a READ-ONLY subcommand `graduation-report` with a text dashboard + `--json` mode; exit 0 ALWAYS. The exit code must NEVER encode readiness — this is a gather, not a gate (mirrors `cmd_deltas`, unlike `check`).
  - Emit FIVE labeled record-sets, each a RECORD the human verifies by looking — never a CONCLUSION the engine reasoned to (no readiness verdict, score, ranking, or theme anywhere in text or json):
      a. open deltas by competency — reuse `_collect_open_deltas(root)` (already project-wide; compacted milestones folded theirs by construction, so absence is correct).
      b. open RISK-ACCEPTED waivers — each {slug, owner, ticket, expires}, sorted by expiry soonest-first (the v3/Matrix-4 waiver shape).
      c. RETRO records — every `.add/milestones/*/RETRO.md` AND `.add/archive/*/RETRO.md`: path + carried-delta count. This is the durable backbone for the compacted milestones.
      d. verify residue — TWO sectioned views (chosen "both"): (i) gate verdicts = RISK-ACCEPTED + HARD-STOP gate records; (ii) §6 disclosed `⚠` residue lines parsed from in-state TASK.md §6. The two are clearly labeled so a RISK-ACCEPTED waiver is shown as one record's two facets, never double-counted as two risks.
      e. coverage-gaps PROXY, explicitly labeled as a proxy ("monitor not declared") — in-state tasks whose §7 "Watch" line is still the unfilled `<…>` placeholder template (a real record: this task left no monitor — never a judgment of coverage adequacy).
  - Render TWO tiers, both present: LIVE (the 14 in-state milestones — fine-grained from state + on-disk TASK.md) and CONSOLIDATED (the compacted milestones — represented by their RETRO record only). State the compacted boundary IN the report ("N milestones represented by RETRO record") — no silent cap.
  - Stay READ-ONLY: mutate no state, write no file, change no exit-code semantics. A missing/unreadable/malformed source is SKIPPED (that record omitted), never a crash (fail-closed, mirroring `_collect_open_deltas`'s OSError skip).
  - `--json` is the freeze-first FACTS SEAM the graduate.md interview consumes: ONE JSON object, each record-set a top-level key, a stable shape a harness can branch on without scraping text.
</must>
Reject:   <!-- read-only gather: each "reject" is a fail-closed state where the record is WITHHELD/skipped, the report still renders, and the exit code is unchanged — only the no-project case dies, exactly as today -->
<reject>
  - no `.add/` project root -> standard `_require_root` die (the one non-zero exit, unchanged from every command) :: "no_project"
  - an unreadable/malformed RETRO.md, TASK.md §6, or §7 Watch block -> that single record is skipped, the rest of the report still renders :: "source_unreadable" (fail-closed)
  - a compacted milestone's INDIVIDUAL waivers / §6 residue -> NOT deep-harvested from the moved `.add/archive/<slug>/` bundle; represented by its RETRO record only :: "archived_summarized" (a logged limitation, not an error)
  - ANY readiness verdict / score / theme, under any input -> refused; emitting one would be judging, which belongs to the cue (task 1) + the interview (task 3) :: "would_be_judging" (design invariant)
</reject>
After:
<after>
  - `add.py graduation-report` prints the five labeled record-sets across both tiers; `--json` returns the same as one stable object; state.json and every file are byte-identical before/after; exit 0; the engine names every source and judges nothing.
  - The graduate.md interview (task 3) can branch on `--json` without scraping text, and stage-goal-criteria's cue (task 1) now has the evidence harvest it invites — closing analytics → interview.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The §6 disclosed-`⚠`-residue parse (record-set d-ii) — lowest confidence because §6 residue is FREE PROSE with no enforced grammar (a `⚠` glyph + a human sentence), so a mechanical match across heterogeneous TASK.md files will mis-harvest (miss some, false-positive others); if wrong: the disclosed-residue section is noisy or thin — bounded cost, since it is additive interview context, not a gate (it degrades, never breaks). The contract MUST pin the exact line-match rule (what marks a §6 residue line).
  ⚠ The waiver ↔ gate-verdict double-count boundary (#2) — lowest confidence #2 because RISK-ACCEPTED appears in BOTH record-set b (waiver-by-expiry) and record-set d-i (gate verdicts); "both sectioned" means the two are FACETS of the same RISK-ACCEPTED record (expiry view vs residue-class view), not two findings; if the labeling is unclear the interview reads one waiver as two risks (inflated readiness picture). The contract must state the shared-record relationship explicitly.
  - [ ] coverage-gaps proxy signal = the §7 "Watch" line still equals the `<…>` angle-bracket placeholder template — confirm the exact detection string at contract (low stakes).
  - [ ] RETRO carried-delta count is read from the rendered "LEARNINGS (N carried)" line vs recomputed from the bundle — confirm at contract (low stakes).
  - [ ] `--json` top-level keys per record-set (e.g. `open_deltas · waivers · retros · residue_gates · residue_disclosed · coverage_gaps · summary`) — name/confirm at contract (low stakes).
  - [ ] scope is ALL milestones (live + archived), project-wide — NOT stage-filtered (stage is project-level, not tagged per milestone) — confirm out-of-scope concern (low stakes).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
# --- Must rules ---
Scenario: The report emits all five labeled record-sets          # M2
  Given a project with an open delta, an open RISK-ACCEPTED waiver, a RETRO.md,
    a TASK.md whose §6 discloses a "⚠" residue line, and a task whose §7 Watch is unfilled
  When I run `add.py graduation-report`
  Then the output contains five labeled sets: open deltas (by competency), waivers,
    RETRO records, verify residue (gate verdicts + disclosed §6 lines), coverage-gaps
  And no readiness verdict, score, ranking, or theme appears anywhere

Scenario: Exit code never encodes readiness                      # M1
  Given heavy accumulated evidence (many open deltas and waivers)
  When I run `add.py graduation-report`
  Then the exit code is 0
  And on a project with no evidence at all it still exits 0 (a gather, never a gate)

Scenario: --json is one object keyed by record-set              # M5
  Given the same gathered evidence
  When I run `add.py graduation-report --json`
  Then stdout is exactly one valid JSON object and nothing else
  And it has a top-level key per record-set (open_deltas · waivers · retros ·
    residue_gates · residue_disclosed · coverage_gaps · summary)

Scenario: Waivers are sorted by expiry, soonest first           # M2b
  Given two open RISK-ACCEPTED waivers expiring 2026-12-01 and 2026-07-01
  When I run `add.py graduation-report --json`
  Then the waivers set lists the 2026-07-01 waiver before the 2026-12-01 waiver

Scenario: One RISK-ACCEPTED is two facets, never two findings   # M2d (the #2 ⚠)
  Given one in-state task done via a signed RISK-ACCEPTED waiver
  When I run `add.py graduation-report --json`
  Then the task slug appears in BOTH waivers (expiry facet) and residue_gates (residue-class facet)
  And the summary counts it as one underlying waived record, not two

Scenario: Two tiers, with the compacted boundary stated         # M3
  Given live in-state milestones AND compacted milestones each with a RETRO.md
  When I run `add.py graduation-report`
  Then the live tier shows fine-grained records and the consolidated tier lists each
    compacted milestone's RETRO record
  And the report states how many milestones are represented by a RETRO record (no silent cap)

Scenario: Coverage-gaps lists undeclared monitors, labeled a proxy   # M2e
  Given an in-state task whose §7 Watch line is still the "<…>" placeholder
  And another in-state task with a filled-in Watch line
  When I run `add.py graduation-report`
  Then the coverage-gaps set lists the placeholder task as "monitor not declared"
  And it does not list the task whose Watch line is filled
  And the section is labeled a proxy, not a coverage-adequacy judgment

Scenario: Read-only — nothing mutates                           # M4
  Given any project state
  When I run `add.py graduation-report` and again with `--json`
  Then state.json and every TASK.md / RETRO.md / PROJECT.md are byte-identical before and after
  And no new file is written

# --- Reject / fail-closed states (each asserts what stays unchanged) ---
Scenario: No project root                                        # no_project
  Given no .add/ project exists in the working directory
  When I run `add.py graduation-report`
  Then it exits non-zero with "no_project"
  And no file is created and no state is written

Scenario: An unreadable source is skipped, the report still renders   # source_unreadable
  Given a directory sitting at a RETRO.md path (unreadable) among otherwise readable sources
  When I run `add.py graduation-report`
  Then the report renders every other record-set without crashing
  And the unreadable RETRO is omitted, never a partial or garbled record
  And state.json is byte-identical before and after

Scenario: A compacted milestone is summarized, not deep-harvested     # archived_summarized
  Given a compacted milestone in .add/archive/<slug>/ with waivers and §6 residue in the moved bundle
  When I run `add.py graduation-report`
  Then those archived individual waivers/residue do not appear in the live fine-grained sets
  And the milestone appears as its RETRO record in the consolidated tier
  And the .add/archive/<slug>/ bundle files are byte-identical (untouched)

Scenario: Never emits a readiness verdict                        # would_be_judging
  Given every milestone done and all evidence gathered
  When I run `add.py graduation-report` and `--json`
  Then no field or line states readiness, a score, a ranking, or a recommendation
  And state.json and the project stage are byte-identical (the report decides nothing)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE CONTRACT — new READ-ONLY subcommand. ADDITIVE: no existing command/exit-code
changes, no state mutation, no file writes. Names per GLOSSARY (graduation analytics ·
stage-graduation · waiver · delta · residue · RETRO).

CLI
  add.py graduation-report           -> text dashboard to stdout; exit 0 ALWAYS
  add.py graduation-report --json    -> ONE JSON object to stdout, nothing else; exit 0 ALWAYS
  add.py graduation-report --plain   -> ASCII/pipe-safe text tier (optional, mirrors cmd_report)
  No positional args. The ONLY non-zero exit is the standard _require_root die (no .add/ project).
  The exit code NEVER encodes readiness — a gather, not a gate (mirrors cmd_deltas, unlike check).

fn graduation_data(root, state) -> dict      # the single source of FACTS — PURE, NO writes (mirrors report_data)
  Both the --json payload and the text dashboard render from this one dict, so the human
  view and the machine view can never disagree.

--json shape (the FROZEN facts seam; each record-set a top-level key):
{
  "open_deltas":   { "total": int,
                     "by_competency": { "<COMP>": [ {"task","text","evidence"} ] } },  # reuse _collect_open_deltas (in-state)
  "waivers":       [ {"slug","owner","ticket","expires"} ],   # gate==RISK-ACCEPTED; sorted by expires ASC
                                                              # (soonest first); missing/unparseable expires sorts LAST
  "retros":        [ {"milestone","path","carried_deltas","tier"} ],  # tier ∈ {"live","consolidated"};
                                                              # path relative to .add/ ; live=.add/milestones/*, consolidated=.add/archive/*
  "residue_gates": [ {"slug","gate"} ],       # gate ∈ {"RISK-ACCEPTED","HARD-STOP"}; in-state; the residue-class FACET
                                              # (a RISK-ACCEPTED here is the SAME record as in waivers[] — NOT a new finding)
  "residue_disclosed": [ {"slug","line"} ],   # in-state §6 list items whose checkbox marker is "[⚠]" (the pinned rule); line trimmed
  "coverage_gaps": [ {"slug"} ],              # in-state tasks whose §7 "Watch" line still contains "<" (unfilled template); labeled proxy
  "summary": { "open_deltas":int, "waivers":int, "retros":int, "residue_gates":int,
               "residue_disclosed":int, "coverage_gaps":int,
               "milestones_live":int, "milestones_consolidated":int }   # the stated compacted boundary — no silent cap
}
NO readiness / score / ranking / recommendation key exists anywhere (would_be_judging is structurally impossible).

PINNED rules (resolve the §1 ⚠ assumptions):
  • §6 residue match (⚠#1): a "## 6 · VERIFY" list item whose marker is exactly "[⚠]" — i.e. line matches `- [⚠] …`.
    Precise, low-false-positive (a clean verify leaves [x]; disclosed residue marks [⚠], the stage-goal-criteria convention).
    Sparse harvest is CORRECT — most verifies were clean. NOT arbitrary prose.
  • waiver↔gate double-count (⚠#2): a RISK-ACCEPTED task appears in BOTH waivers[] (expiry facet) and residue_gates[]
    (residue-class facet) — FACETS OF ONE record keyed by slug. summary counts each list independently; the two are
    NEVER summed into a combined "risk count" (that would inflate one waiver into two findings).
  • coverage-gaps signal: the §7 line beginning "Watch" still contains the placeholder HEAD "<error rate"
    (the unfilled <…> template). NOT a bare "<" — a filled monitor using "<" as less-than ("latency < 200ms")
    must NOT be flagged. A human who fills the Watch replaces the whole template, so "<error rate" vanishes.
  • RETRO carried_deltas: parsed from the rendered "LEARNINGS (N carried)" line; absent line -> 0.
  • scope: ALL milestones — live (state["milestones"]) + consolidated (state["archived"]); never stage-filtered.

Reject responses (read-only; each WITHHOLDS a record, the report still renders, exit unchanged):
  no_project          -> _require_root die; stderr "no_project"; non-zero exit; no output object
  source_unreadable   -> the offending RETRO/TASK.md/§-block is SKIPPED (try/except OSError, like _collect_open_deltas);
                         that record omitted; all other sets render; exit 0
  archived_summarized -> compacted milestones contribute ONLY a retros[] entry (tier="consolidated"); their individual
                         waivers/§6 residue are NOT read from .add/archive/ bundles. CHECKED 2026-06-09: the 11
                         pre-archive-state.bak.json files carry 0 waivers + 0 non-PASS gates, so live-tier coverage is
                         COMPLETE today (nothing archived to miss). If a future archived milestone carries a waiver,
                         reading it from pre-archive-state.bak.json (structured JSON, not prose) is the additive evolution path.
  would_be_judging    -> structurally impossible: the schema has no verdict/score field; no code path emits one
```

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-09
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario (12) → one behavioral test asserting the contracted shape (not internals); every new symbol (`graduation_data`, `cmd_graduation_report`, helpers) exercised; the read-only invariant proven by md5.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  # --- Must ---
  - test_emits_five_record_sets (M2): seed an open delta + open RISK-ACCEPTED waiver + a RETRO.md + a §6 `- [⚠]` line + an unfilled §7 Watch / run `graduation-report` / assert the text carries all five labeled sets + no readiness/score/theme word
  - test_exit_zero_always (M1): heavy evidence → exit 0; AND a project with no evidence → still exit 0 (gather, not gate)
  - test_json_one_object_keyed (M5): `--json` → stdout parses as ONE object with keys {open_deltas, waivers, retros, residue_gates, residue_disclosed, coverage_gaps, summary} and nothing else on stdout
  - test_waivers_sorted_by_expiry (M2b): two RISK-ACCEPTED waivers expiring 2026-12-01 & 2026-07-01 / `--json` / assert waivers[0].expires == 2026-07-01 (soonest first)
  - test_risk_accepted_two_facets (M2d, ⚠#2): one task done via RISK-ACCEPTED waiver / `--json` / assert slug ∈ waivers AND ∈ residue_gates AND summary has no combined/summed risk count
  - test_two_tiers_boundary_stated (M3): a live + a consolidated (state["archived"]) milestone each w/ RETRO / assert consolidated retro listed w/ tier="consolidated" AND summary.milestones_consolidated ≥ 1 (boundary stated)
  - test_coverage_gaps_proxy (M2e): one task w/ placeholder `<error rate…>` Watch + one whose filled Watch uses "<" as less-than ("latency < 200ms") / assert coverage_gaps lists ONLY the placeholder task (the filled "<" is NOT a false-positive); section labeled a proxy
  - test_read_only (M4): md5 of state.json + a TASK.md + a RETRO.md + PROJECT.md unchanged after text AND `--json`; no new file created
  # --- Reject (each asserts what stays unchanged) ---
  - test_no_project (R1): run outside any .add/ → non-zero exit + stderr "no_project"; assert no file created
  - test_unreadable_source_skipped (R2): a directory sitting at a RETRO.md path / assert report renders the other sets, omits the bad one, exit 0, state.json md5 unchanged
  - test_archived_summarized (R3): a compacted milestone in .add/archive/<slug>/ w/ a waiver inside / assert that waiver is NOT in live waivers[]; the milestone IS a retros[] consolidated entry; archive bundle md5 unchanged
  - test_never_readiness_verdict (R4): full evidence / text AND `--json` / assert no readiness|score|ranking|recommendation field or word; state.json + stage md5 unchanged
</test_plan>

Tests live in: `add-method/tooling/test_graduation_report.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full engine suite 667 OK (incl. 12 new graduation-report tests); three-tree byte-identical; dogfooded live on this project (all 5 record-sets populated: 3 open deltas, 20 RETROs across both tiers, 1 disclosed-residue, 5 coverage-gaps, 0 waivers/gates)
- [x] coverage did not decrease — +12 tests; every new symbol (`_retro_carried`·`graduation_data`·`cmd_graduation_report`·the subparser) exercised; the pinned `- [⚠]` rule + `<error rate` proxy proven on REAL data
- [⚠] no test or contract altered during build — **CONTRACT untouched (FROZEN @ v1 honored). ONE test file touched (residue → human gate):** `test_min_pillar.py` LIFECYCLE gained `["graduation-report"]` + `["graduation-report","--json"]`. This is **SANCTIONED self-maintenance** — the test's own comment: *"A new subcommand fails here until it is added to LIFECYCLE"*; the assertion is UNCHANGED (every subcommand covered) and coverage is STRENGTHENED (graduation-report now runs under the read-spy, proving it reads no docs/). NOT a weakening. The ubiquitous-language test was NOT touched — I reworded my own "seam" prose to comply with the glossary.
- [x] concurrency / timing — N/A: feature is READ-ONLY (`graduation_data` reads state + files, mutates nothing; `test_read_only` proves state.json/TASK.md/RETRO/PROJECT md5 unchanged + no file written). No shared-state write → no race.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`, `json`, `datetime.date`); no secrets; read-only render has no injection surface; no new/invented package
- [x] layering & dependencies follow CONVENTIONS.md — `graduation_data` mirrors `report_data` (one pure facts source for text+json, never disagree); `_retro_carried` is a small pure parse; `cmd_graduation_report` mirrors `cmd_deltas`/`cmd_report`; reuses `_collect_open_deltas` (no duplicated harvest); three-tree byte-identity restored + `ENGINE_MD5` re-aimed → 80926fe1
- [x] verify-time correction (text renderer only, NOT the seam) — advisor caught the dashboard header conflating `milestones_live` (14) with the RETRO-record count (8 listed) → reworded to `RETRO records (N: L live · C consolidated) — milestones: M live · K represented by RETRO record`. Touches the `--plain`/text branch ONLY; the frozen `--json` interface is byte-identical (no key/value change); no test altered (text wording is not a contract obligation — the seam is `--json`, which is tested); contract FROZEN untouched. Suite re-run 667 OK; re-synced + re-pinned (md5 `c6fb3470`→`80926fe1`).
- [x] a person reviewed and approved the change — Tin Dang · 2026-06-09 · PASS (reviewed the disclosed LIFECYCLE residue + read-only/stdlib/no-security evidence + live dogfood)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_retro_carried`←`graduation_data`; `graduation_data`←`cmd_graduation_report` (text + --json branches); `cmd_graduation_report`←the `graduation-report` subparser (`set_defaults(func=...)`); `_collect_open_deltas` reused. Every new symbol has a call site (grep-confirmed) + proven live by the dogfood.
- [x] DEAD-CODE (code) — no new unused/orphaned symbol. `--plain` is an accepted CLI flag (output is plain by default) — a valid surface, not dead. The other new symbols all fire in the dogfood + tests.
- [ ] SEMANTIC (prose / non-code) — n/a (code change; the pinned-rule prose lives in the frozen §3 contract, not new untested prose)

### GATE RECORD
Outcome: PASS — human-led gate. 1 test file extended as sanctioned self-maintenance (`test_min_pillar.py` LIFECYCLE coverage; assertion unchanged, coverage strengthened, not a weakening); contract FROZEN untouched; read-only; stdlib-only; no security/concurrency residue. Full suite 667 OK; live dogfood proved all 5 record-sets.
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-09

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the two prose-heuristic record-sets — §6-disclosed-residue (`- [⚠]` match over free prose) and the coverage-gap proxy (the unfilled angle-bracket Watch-placeholder head) — watch their false-positive / false-negative rate as more TASK.md files accrue (a disclosed residue line that doesn't start `- [⚠]` is missed; a filled-but-templated Watch line could mis-flag). NB: an earlier draft of this very line reproduced the proxy's trigger token verbatim and self-flagged — a live false-positive of the exact class named here; the trigger is described, not quoted, to avoid it. AND watch the live/consolidated boundary: today the fine-grained sets (waivers, gate-verdicts, §6 residue) are LIVE-tier only and the archived tier is empirically empty of them (0 archived waivers/non-PASS gates) — the first archived RISK-ACCEPTED waiver or HARD-STOP gate is the trigger to extend the harvest to a RETRO-backed or `.bak`-backed source. (Filling this line is itself the fix for this task self-flagging as its own coverage-gap.)
Spec delta for the next loop: graduate.md (task 3) consumes the frozen `--json` 7-key object; if the interview needs a field not in those keys, that is a CONTRACT change-request back to this task — never a text scrape. The header now separates RETRO-record tiers (`N: L live · C consolidated`) from milestone counts (`M live · K represented`) — a renderer-clarity lesson worth carrying into any future cross-tier dashboard.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->

- [TDD · folded] **A gather-not-judge invariant guarded by a denylist is only as strong as the list — pin the invariant STRUCTURALLY, not lexically.** `test_never_readiness_verdict`'s FORBIDDEN set omits "theme"/"ready" (dropped deliberately), so the test is narrower than the §3 contract's "no verdict / score / ranking / theme" claim. Lesson: when an invariant is "the engine never concludes", assert the *absence of a conclusion field in the schema* (impossible to add a verdict), not the *absence of specific words in the output* (a denylist always lags the contract's vocabulary). (evidence: advisor caught the gap; the code genuinely judges nothing — the JSON schema has no verdict field — so it is a test-completeness gap, not a defect)
- [ADD · folded] **A multi-source report must declare ONE traversal basis per tier, or the sets silently diverge under archival.** `open_deltas` globs the filesystem (`_collect_open_deltas` over `tasks/*`) while `residue_disclosed` + `coverage_gaps` iterate `state["tasks"]`. They agree today ONLY because all 12 archived milestones are *compacted* (files moved out of `tasks/`); a future *light-archived* milestone (files stay, state entry dropped) would appear in `open_deltas` but vanish from the state-iterated sets. This is the same archive seam as stage-goal-criteria's DDD delta (done-tally over `state["milestones"]`). Lesson: pin each tier's source-of-truth (filesystem OR state) in the contract and prove the two bases agree, or document the divergence as a known limitation. (evidence: open_deltas globs tasks/* while residue_disclosed + coverage_gaps iterate state["tasks"]; the sets agree today only because all 12 archived milestones are compacted out of tasks/)
- [SDD · folded] **When a harvest's coverage is bounded by current DATA SHAPE (not by design), the contract must record the boundary AND the empirical check that made it safe — so a future shape that violates it re-opens the clause.** The `archived_summarized` reject clause bounds the fine-grained sets (waivers, gate-verdicts, §6 residue) to the live tier; it was frozen safe by a discriminating grep (0 archived waivers / non-PASS gates exist today), not by argument. Lesson: a data-shape-bounded contract clause should name its trigger (here: the first archived RISK-ACCEPTED/HARD-STOP) so the limitation surfaces as a change-request the day it stops being empty, instead of silently under-reporting. (evidence: pre-freeze advisor flagged the limitation as possibly silent; the grep made it empirically empty — 0 archived waivers / non-PASS gates)
