# PLAN: Fold PROJECT.md standing bullets into the 5-DD living specs

slug: foundation-split · created: 2026-07-22 · stage: mvp
kind: docs
milestone: thin-engine-loop
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: foundation-split — fold the live PROJECT.md's accumulated §Domain/§Spec/§Users
standing bullets into the five 5-DD living specs (`.add/specs/`), slim PROJECT.md back to
its engine-bound core (header · invariants · pointers · Key Decisions ledger), and leave
one rolled settled line per folded section (the compact-foundation idiom: summarize +
`see git`, never delete). Content-only — zero engine change; this dogfoods the migration
ritual external 2.0 upgraders will follow.
Framings weighed: convention-guided manual fold (chosen — folding is per-bullet judgment,
the method says fold approval is human-owned; matches compact-foundation.md) · an
`add.py migrate --fold-foundation` verb (rejected: auto-migrating prose is judgment the
engine can't own; verb-census + pin ripple for a one-shot move).
Must:
<must>
  - M1 every engine-read PROJECT.md line survives byte-identical: `streams: sequential` · the `autonomy: auto` decl line · the `goal:` line (the `_project_autonomy` / status / `autonomy set --project` seams); the `slug:`-prefixed header line survives with ONLY its `updated:` date and `foundation-version:` field changing
  - M2 PROJECT.md keeps the standing-invariants block INSIDE the `## Domain` section (so the `_foundation_skeleton` orient map — which keeps only `## Domain`/`## Spec` — still surfaces it), naming the `reopen` back-edge (test_reopen_transition pins the live file) and keeping the invariants currently under "Invariants that must always hold"
  - M3 each folded section (§Domain surplus · §Spec · §Users) collapses to ONE rolled settled line naming its destination spec file + a `see git` pointer — no bullet is deleted without either migrating to a spec or being covered by the rolled line
  - M4 the five specs' `## Now` + `## Decisions that bind` placeholders are replaced with the migrated standing picture, sourced ONLY from existing PROJECT.md content (no invented claims); open forward-gaps (e.g. the UDD a–d gaps) stay live, never silently settled; each spec keeps its `## Deltas (newest first)` heading + prepend comment intact (the `cmd_delta_append` anchor)
  - M4b the build emits a fold LEDGER (`.add/tasks/foundation-split/fold-ledger.md`: one line per source bullet → destination spec | rolled) — the honest no-bullet-lost evidence; the §6 refute-read samples FRESH bullets from it, never only the pre-named A7 three
  - M5 Key Decisions: the pure fold-ceremony rows collapse into one settled row; substantive ship rows + the existing settled row stay; ONE new row records this fold; the header stamps `foundation-version: 66`
  - M6 zero engine/test change — the working-tree diff touches ONLY `.add/PROJECT.md`, `.add/specs/*.md`, and this task dir
</must>
Reject:
<reject>
  - a standing bullet findable in neither PROJECT.md nor any spec after the fold -> "content_lost"
  - an engine-read header line moved, reworded, or dropped -> "engine_seam_moved"
  - the retired "Two UX follow-ups for v21" note reappearing in the live foundation -> "stale_note_regrown"
</reject>
After:
<after>
  - PROJECT.md ≤ 120 lines (from 322) and remains the read-first map: header · invariants · three pointer sections · ledger
  - `add.py status` output for goal/autonomy/streams is byte-identical to pre-fold
  - the specs are the single home of the standing 5-DD picture; the next `delta-append` fold consumes specs/, with no second destination
</after>
Boundary: none — no external input; the fold is a curated text move between two tracked file sets
<assumptions>
  ⚠ classification of each §Spec ship-bullet as "settled history" (roll) vs "standing rule" (migrate) is the judgment most likely to mis-file one rule — if wrong: a live rule is only reachable via `see git`; cost is a recovery read, never data loss (rolled lines keep the trail)
  ⚠ disclosed: the §5 scope gate is BLIND under `.add/` (`_scope_walk` prunes it via _SCOPE_EXCLUDE_DIRS) — the declared tokens are grammatically valid but vacuous; A6's diff-confinement check is the real write-set guard for this task
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
FOLD .add/PROJECT.md -> .add/specs/{domain,system,experience,quality,method}.md
  PROJECT.md KEEPS: streams · autonomy decl · goal (all byte-identical) · the `slug:`
    header line (only `updated:` + `foundation-version:` fields change) · the
    standing-invariants block INSIDE ## Domain (names the reopen back-edge) ·
    Key Decisions ledger (compacted per M5)
  PROJECT.md each folded section -> ONE rolled line:
    "standing picture folded into `.add/specs/<file>` @ fv66 — see git"
  specs/*.md: "## Now" + "## Decisions that bind" placeholders -> migrated standing
    picture; routing: DDD bullets -> domain.md · SDD -> system.md (test-strategy
    lessons -> quality.md) · UDD -> experience.md · loop/gate/residue rules -> method.md
  Never: delete without a rolled pointer · invent a claim not already in PROJECT.md ·
    touch add.py / any test / any file outside `.add/PROJECT.md` + `.add/specs/` + this task dir
Schema: two tracked markdown file sets; no state.json shape change; no engine read path changes
Anchors: `_project_autonomy` · `_project_benchmark_mode` · cmd_status goal line ·
  cmd_autonomy `--project` writer · test_reopen_transition LIVE_PROJECT pin ·
  test_ux_stale_followups StaleNotesTest · templates/PROJECT.md.tmpl (untouched)
```

Target (measurable): PROJECT.md 322 -> ≤120 lines with all engine-read lines byte-identical (checked by diff); 5/5 specs carry a non-placeholder `## Now` + `## Decisions that bind`; 3-bullet spot-trace (one per folded section) resolves to its destination spec; `add.py check` 0-failed and the two live-file test modules green; the full tooling suite stays the CI floor.
Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [contract] the settled-vs-standing classification of
each §Spec ship-bullet (roll vs migrate) is the judgment most likely to mis-file one rule
— if wrong, the rule stays reachable via the rolled `see git` pointer; a recovery read,
never data loss (accepted: leanness beats re-pasting history).
Reported: yes — contract + fold mapping + advisor findings rendered to the human before this freeze

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `.add/PROJECT.md` `.add/specs/` `tmp/` `./`
Regression floor: `add.py check` 0-failed + targeted live-file tests (`test_reopen_transition` · `test_ux_stale_followups` · `test_foundation`) green; full tooling suite via CI/background
Persona (required): `.add/personas/method-product-owner.md` (foundation curation — what binds vs what is history is a product-owner judgment)

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - A1_specs_not_placeholder: none of the 5 specs still carries the seed placeholder text ("<the standing" / "-lens decisions") in Now/Decisions — RED today (all five are placeholders) · covers: M4
  - A2_engine_lines_byte_identical: `git diff .add/PROJECT.md` leaves the streams/autonomy/goal lines untouched AND `add.py status --all` prints the identical goal + autonomy (plain status omits the goal line — cite --all) — guard, checked at verify · covers: M1, R:engine_seam_moved
  - A3_sections_rolled: PROJECT.md ≤120 lines; each folded section carries exactly one rolled line naming its destination spec + "see git"; the bare `add.py status --foundation ""` orient map still contains the invariants + reopen lines — RED today (322 lines, no rolled lines) · covers: M3, M2
  - A4_pinned_strings_hold: "reopen" present · "Two UX follow-ups for v21" absent · `python3 -m unittest test_reopen_transition test_ux_stale_followups test_foundation` green · covers: M2, R:stale_note_regrown
  - A5_ledger_compacted: ceremony fold-rows collapsed to one settled row · one new fv66 row · header stamps foundation-version: 66 — RED today (65, ~30 ceremony rows) · covers: M5
  - A6_diff_confined: `git diff --name-only` (tracked modifications since the pre-task baseline) ⊆ {.add/PROJECT.md, .add/specs/*.md, .add/tasks/foundation-split/*, .add/state.json}; NEW untracked paths vs the baseline recorded in this task dir: none outside the task dir — engine + tests md5-unchanged (`git status --porcelain` alone can never pass: pre-existing untracked benchmark/ dirs) · covers: M6
  - A7_spot_trace: 3 pre-named bullets (owner-vs-actor DDD · TUI house rule UDD · §6-checkbox-drift SDD) PLUS ≥3 FRESH bullets sampled from the fold ledger by the §6 refute-read — each findable in its destination spec — RED today (specs empty) · covers: M4, M4b, R:content_lost
</test_plan>

Tests live in: evidence · acceptance checks — red before the fold exists, green after (flexible-TDD §4).

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, plus one refute-driven repair — the cross-agent
refute-read (NOT-EARNED, F1: all 15 substantive ship rows rolled despite frozen M5's
"stay"; F2: settled-row tally 33 vs actual; F3: three rolled OPEN tails unannotated)
drove a restore of the 15 rows byte-identical from git, a corrected 30-row settled
tally, and supersession notes on ledger #26/#30/#32/#34. Order of work: specs first
(5 files, placeholders → Now/Decisions), then PROJECT.md rewrite, then the 62-line
fold ledger, then acceptance checks A1–A7.
Code lives in: `.add/PROJECT.md` + `.add/specs/` + this task dir (content-only; no `./src/`)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — A1–A7 all green post-repair; regression floor: full tooling suite 1959 passed / 0 failed (twice: pre- and post-repair) · `add.py check` 414 passed / 0 failed · targeted live-file modules 22 tests OK
- [x] coverage did not decrease — content-only task; the two live-file guards (reopen pin · stale-note absence) still exercise the new file
- [x] no test or contract was altered during build — the M5 deviation was repaired toward the frozen text (rows restored), never by editing §3
- [x] the green was EARNED, not gamed — cross-agent refute-read: first pass NOT-EARNED (F1 M5 deviation · F2 tally miscount · F3 unannotated OPEN tails); all repaired; 13 fresh ledger samples verified substance-intact vs `git show HEAD`
- [x] concurrency / timing — n/a: two tracked markdown file sets, atomic single-writer edits, no engine state shape change
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no new deps; engine byte-untouched (suite + diff confirm)
- [x] layering & dependencies follow CONVENTIONS.md — compact-foundation idiom (summarize + `see git`, never delete); specs keep their `## Deltas` anchors; single-source pointers, no restated content
- [x] a person reviewed and approved the change — contract frozen by Tin Dang; fold rendered + approved before freeze; gate recorded in-session

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: add-advisor (cross-agent, two-pass, tdd-verifier persona) · adversarially checked:
13 fresh ledger samples vs pre-fold git source (none pre-named) · ledger coverage census
(§Domain 8 · §Spec 27 · §Users 23 · ledger 4 — no unlisted bullet) · M1 byte-diff on
engine lines · M2 invariants placement + reopen pin · M4 Deltas anchors + both pre-existing
open deltas · M6 diff confinement · semantic no-invented-claims spot-check (3) — first pass
NOT-EARNED (F1/F2/F3), repaired: 15 ship rows restored byte-identical, tally 30, ledger annotated

### GATE RECORD
Reported: yes — evidence + refute verdict rendered before this outcome recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-resolved (autonomy: auto; evidence + recorded EARNED verdict; kind: docs, no security/concurrency/architecture residue) · date: 2026-07-22

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose convention-guided manual fold; rejected an `add.py migrate --fold-foundation` verb (rejected: auto-migrating prose is judgment the engine can't own; verb-census + pin ripple for a one-shot move).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, plus one refute-driven repair — the cross-agent refute-read (NOT-EARNED, F1: all 15 substantive ship rows rolled despite frozen M5's "stay"; F2: settled-row tally 33 vs actual; F3: three rolled OPEN tails unannotated) drove a restore of the 15 rows byte-identical from git, a corrected 30-row settled tally, and supersession notes on ledger #26/#30/#32/#34. Order of work: specs first (5 files, placeholders → Now/Decisions), then PROJECT.md rewrite, then the 62-line fold ledger, then acceptance checks A1–A7.
- [AI] verify — gate PASS (reviewed by auto-resolved (autonomy: auto; evidence + recorded EARNED verdict; kind: docs, no security/concurrency/architecture residue))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
