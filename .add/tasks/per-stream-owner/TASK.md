# TASK: show each active stream's owner in the streams block + report

slug: per-stream-owner · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default auto: edits the byte-pinned engine across all 3 add.py copies + re-pins; a human owns the high-risk gate (run.md guard). -->
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — surface each active stream's owner:
  - `cmd_status` HUMAN `streams:` block (~1495, gated `len(_ams) >= 2`) — each stream line currently prints `task=… phase=…{tag}`; APPEND a present-only ` · owner: <name>` using the milestone record's `owner` via `_fmt_actor` (skip when the active milestone has no owner — additive-cue, byte-identical).
  - `cmd_status` `--json` milestones entries (~1343) — each `{slug,status,done,total}` gains `"owner": m.get("owner"), "assignee": m.get("assignee")` (present-only values; None when unset). Parity with the per-TASK owner/assignee M3 already added to the `tasks` entries. Top-level json keys UNCHANGED, so the frozen-surface guard (test_wave_status_hint `test_json_surface_frozen`, which asserts only the TOP-LEVEL key set) is untouched.
- `engine_pin.py:ENGINE_MD5` — re-pin after this engine edit (same commit). (No new subcommand → no `test_min_pillar` LIFECYCLE change.)

Context (working folder):
- M1 parallel-status-view built the `streams:` block (gated N≥2 active milestones, primary-first ▸/(primary), `task=… phase=…`). This task adds the owner — the carried delta it left open.
- M3 ownership-assignment put `owner`/`assignee` records (`{name,email,source}`) on MILESTONE records too (not just tasks), and ownership-surface already renders a milestone `owned by` line in `render_report` (lines ~3979-3981). So the REPORT half of the exit criterion is ALREADY DONE — this task adds only the `streams:` block (human) + the `status --json` milestone-entry parity.
- `_fmt_actor(actor)` (~3860) renders `{name,email,source}` as `name <email>` present-only ("" when absent). `_fmt_ownership` renders both roles; here a single `owner:` label on the stream line is clearer than both roles, so use `_fmt_actor(m.get("owner"))`.

Honors (patterns / conventions):
- additive-cue convention — owner appears ONLY when the active milestone has one; a no-owner stream line is byte-identical to today. The JSON entries always carry the keys (present-only value, None when unset), mirroring the per-task pattern.
- present-only render — reuse `_fmt_actor`; never a blank `owner: ` placeholder.
- descriptive, never enforced — read-only surface; no write, no decision reads it.
- engine-edit discipline — 3-tree byte-identity + same-commit ENGINE_MD5 re-pin. No new command → census unchanged.

Anchors the contract cites: the `cmd_status` `streams:` block owner line (present-only `_fmt_actor(m.get("owner"))`) · the `status --json` milestones-entry `owner`/`assignee` keys · reuse of `_fmt_actor` · the existing M3 milestone `owner`/`assignee` record fields.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: each active stream in the `status` `streams:` block names its milestone's owner (present-only), and the `status --json` milestone entries carry `owner`/`assignee` — completing the carried M1 delta (the report already shows the milestone owner via M3).
Framings weighed: a single `owner:` label on the stream line via `_fmt_actor(m.get("owner"))` (chosen — the stream view is a compact one-liner; the lead/owner is the one identity that matters at a glance) · both roles via `_fmt_ownership` on the stream line (rejected — too wide for the compact stream row; the full owner+assignee pair already lives in the report's `owned by` line) · a whole new `streams`/`teams` command (rejected — the block already exists; this is the carried delta, not a new surface).
Must:
<must>
  - in `cmd_status`'s human `streams:` block (rendered when ≥2 milestones are active), each stream line appends a present-only ` · owner: <name>` derived from that milestone record's `owner` via `_fmt_actor`; a stream whose milestone has no owner (or a blank-name owner) renders byte-identically to today (no `owner:` fragment).
  - in `cmd_status --json`, each milestones-list entry gains `owner` and `assignee` (the milestone record's values, or None when unset) — additive, alongside the existing `slug/status/done/total`; the TOP-LEVEL json key set is unchanged.
  - read-only: `status` writes nothing; the rest of the `streams:` block (order, ▸/(primary) marks, task/phase) and every other status line are unchanged. All 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned same commit. No new subcommand (census unchanged).
</must>
Reject:
<reject>
  - no rejectable input — `status` reads state and renders. A milestone with no owner is a valid case (renders without the owner fragment), not an error. (No `_die` path.)
</reject>
After:
<after>
  - with ≥2 active milestones, `add.py status` shows each stream's owner when set; `status --json` milestone entries carry owner/assignee; a no-owner stream/milestone is byte-identical to before; state.json unchanged; the prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Showing only the `owner` (not assignee) on the human stream line is the right compactness trade — lowest confidence because a team might lead a stream by ASSIGNEE rather than owner, so the most relevant person could be hidden on the one-liner. Chose owner as the single "who leads this stream" signal; the full owner+assignee pair is one `report` away (and now in `status --json`). If wrong: add assignee to the stream line too (one `_fmt_ownership`-style change, no contract-surface break).
  - [ ] putting owner/assignee on the `status --json` milestone entries (not just the human block) is right — confirmed: JSON parity lets a wrapper read stream ownership; it mirrors the per-task pattern M3 set and doesn't touch the frozen top-level surface.
  - [ ] the report needs no change — confirmed: M3's ownership-surface already renders the milestone `owned by` line; re-implementing it here would duplicate.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: an owned stream shows its owner in the streams block
  Given two active milestones, one with owner "Ada <ada@x.io>"
  When `add.py status`
  Then that stream's line carries "owner: Ada" and state.json is unchanged

Scenario: a stream with no owner renders byte-identically
  Given two active milestones, neither with an owner
  When `add.py status`
  Then no stream line carries an "owner:" fragment (the block matches the pre-owner format)

Scenario: status --json milestone entries carry owner/assignee
  Given two active milestones, one with owner "Ada <ada@x.io>"
  When `add.py status --json`
  Then that milestone's entry has owner.name == "Ada" and an "assignee" key (None when unset)
  And the TOP-LEVEL json key set is unchanged (frozen-surface guard holds)

Scenario: single-milestone status is unaffected
  Given exactly one active milestone (no streams block renders)
  When `add.py status`
  Then output is byte-identical to before this change (additive-cue: N<=1 untouched)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
cmd_status — HUMAN `streams:` block (rendered iff len(active_milestones) >= 2):
  per stream line, after the existing "  {mk} {m:<20} task={tk} phase={ph}{tag}":
    _own = _fmt_actor((milestones.get(_m) or {}).get("owner"))
    if _own:  append "  · owner: " + _own
  (present-only — no owner / blank-name owner -> line byte-identical to today)

cmd_status --json — each milestones-list entry:
  {"slug", "status", "done", "total",
   "owner":   m.get("owner"),       # {name,email,source} or None
   "assignee": m.get("assignee")}   # {name,email,source} or None
  TOP-LEVEL json keys unchanged (frozen-surface guard reads only obj.keys()).

Schema: READ-ONLY — no state write, no schema change, no new state key. Reuses `_fmt_actor`
  + the M3 milestone `owner`/`assignee` record fields. No new command (census unchanged).
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization) · 2026-06-22

Least-sure flag surfaced at freeze:
- [spec] showing only `owner` (not assignee) on the compact human stream line — the point most likely wrong. A team that leads a stream by ASSIGNEE would see the less-relevant identity on the one-liner. Chose owner as the single "who leads this stream" signal; the full pair is in the report's `owned by` line and now in `status --json`. Cost if wrong: add assignee to the stream line too — a one-fragment change at the same seam, no contract re-freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 4 scenarios + the engine-pin parity guard.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_owned_stream_shows_owner: 2 active ms, m1 owner Ada; `status` → the m1 stream line carries "owner: Ada"; state bytes unchanged
  - test_no_owner_stream_byte_identical: 2 active ms, no owners; `status` streams block has NO "owner:" fragment on any stream line
  - test_json_milestone_owner_assignee: 2 active ms, m1 owner Ada; `status --json` → m1 entry owner.name=="Ada" + "assignee" key present (None); top-level key set unchanged
  - test_single_milestone_unaffected: 1 active ms; `status` renders no streams block + no owner fragment (N<=1 additive-cue)
  - test_three_trees_byte_identical_and_pinned: md5(3 copies)==1 and ==ENGINE_MD5
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
Tests in: `add-method/tooling/test_per_stream_owner.py`
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_per_stream_owner.py`
Strategy (ordered batches): 1. append the present-only `owner:` fragment to the `streams:` block + add owner/assignee to the `status --json` milestone entries in the canonical add.py. 2. mirror to the other 2 copies (`cp`) + re-pin ENGINE_MD5. 3. run the red suite green.
Safety rule (feature-specific): READ-ONLY — `cmd_status` writes nothing; the owner fragment is present-only (no blank placeholder); the JSON change is additive (top-level keys untouched).
Code lives in: `add-method/tooling/add.py` (+ 2 mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — already imported); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_per_stream_owner` 6/6 green; full tooling suite 1510 green (was 1509)
- [x] coverage did not decrease — net +6 tests (4 scenarios + pin guard + blank-name edge); +1 added post-review, none removed
- [x] no test or contract was altered during build — §3 frozen unchanged; the post-review edits were a test ADDITION (blank-name edge) + a rename to an honest name + a stronger assert; re-crossed tests→build to re-anchor
- [x] the green was EARNED, not gamed — independent python-expert refute-read: MERGE-WITH-NITS, no HARD-STOP, no stub/overfit, frozen JSON top-level surface confirmed intact. Its Finding 1 (a blank-name owner emitting a fragment — a real fidelity gap vs the frozen contract) was FIXED with the `_fmt_ownership`-style name-guard + locked by a test; Finding 2 (overstated test name) renamed + strengthened
- [x] concurrency / timing — n/a: `status` is a single read-render; no write, no race
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (already imported); no new input surface
- [x] layering & dependencies follow CONVENTIONS.md — reuses `_fmt_actor` (the present-only render seam) + the M3 milestone owner/assignee fields; mirrors the per-task owner/assignee pattern M3 set in `status --json`
- [x] a person reviewed and approved the change — auto-mode standing authorization (risk:high → conservative), independent subagent review on record

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] an owned stream shows its lead in the `streams:` block — confirmed by a live scratch-project run: "alpha … · owner: Ada <ada@x.io>" while "beta … (primary)" carries no fragment
- [x] a no-owner / blank-name stream renders byte-identically — confirmed by test_no_owner_stream_has_no_owner_fragment + test_blank_name_owner_renders_no_fragment (no `owner:`, no empty `· ` separator, no leaked email)
- [x] `status --json` milestone entries carry owner/assignee, top-level surface frozen — confirmed by test_json_milestone_owner_assignee (m1 owner.name=="Ada", assignee None) + the in-test top-level key-set guard
- [x] N<=1 active milestones is untouched — confirmed by test_single_milestone_unaffected (no `streams :` line at all) + the live project (1 active milestone → no streams block, no regression)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the streams-block owner fragment and the JSON owner/assignee keys are both on the live `cmd_status` render path; reuse `_fmt_actor` (already wired); exercised by all 6 tests
- [x] DEAD-CODE (code) — no new symbol added (no helper, no command); only inline render code in `cmd_status`; nothing orphaned
- [x] SEMANTIC — n/a (code task; WIRING applies)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do streams actually carry owners (are milestones being assigned)? · is `owner`-only enough, or do users want the assignee on the stream line too (the freeze flag)?

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] add the assignee to the human stream line (not just owner) if teams lead streams by assignee (evidence: §3 freeze flag — owner chosen as the single compact signal; the assignee is now in `status --json` but not the human one-liner) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] a test named `*_byte_identical` must actually assert byte-identity (or absence of EVERY new fragment, incl. empty separators), not just absence of the one new keyword — else a different spurious fragment passes under a name that claims more than it checks (evidence: refute-read Finding 2 — `test_no_owner_stream_byte_identical` only checked `not in "owner:"`; renamed + strengthened to also reject the `· ` separator) [folded foundation-version 45]
- [ADD · folded] a present-only render that reuses a formatter (`_fmt_actor`) must replicate that formatter's OWN emptiness guard at the call site — `_fmt_actor` returns a truthy ` <email>` for a blank-NAME record, so a naked `if _fmt_actor(x)` check emits a fragment the contract forbids; guard on `.get("name")` like `_fmt_ownership` does (evidence: refute-read Finding 1 — blank-name owner leaked an `owner:  <email>` fragment until the name-guard was added) [folded foundation-version 45]
