# TASK: loud forceable open-SPEC-delta release floor + status staleness line

slug: delta-drain · created: 2026-06-27 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from project default `auto`: this is a structural gate change — it adds backpressure to the RELEASE gate (a forceable floor) and may add a delta-lifecycle state — so the high-risk guard requires conservative/manual + `risk: high`. The human owns the verify gate. Multi-component repo? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py:cmd_release(args)` (5249–5310) — the release FLOOR: 4 checks BEFORE any write — `release_security_open` (UN-forceable), then `release_tests_red` · `release_no_closed_milestone` · `release_undisclosed_waiver` (all `--force`-able). The new open-SPEC-delta floor slots in here as a 5th forceable check (validate-before-write).
  - `add-method/tooling/add.py:release_data(root, state)` (5119–5195) — PURE "gather, never judge" facts dict (releasable/changed/waivers/blockers/monitors/loose + summary). Add an `open_spec_deltas` record-set so the floor AND `release-report` read ONE source.
  - `add-method/tooling/add.py:_collect_open_spec_deltas(root)` (≈4519) — scans every `.add/tasks/*/TASK.md` `### Spec delta` block for `[SPEC · open]` lines → flat `[{task,text,evidence}]`; the count source (today: 61).
  - `add-method/tooling/add.py:_resolve_spec_delta(text, new_status, …)` (≈4555) — PURE status flip `[SPEC · open]` → new_status; today reached by `drop-delta` (→ dropped) + `new-task --from-delta` (→ seeded). A `carried` status would reuse this same verb engine.
  - `add-method/tooling/add.py:cmd_drop_delta` (≈442) + the `new-task --from-delta` seed — the existing open→{dropped,seeded} resolution pair (the drain verbs).
  - `add-method/tooling/add.py:cmd_status` releasable/`queued` cue — where a PRESENT-ONLY `stale: N open SPEC delta(s)` line goes (byte-identical when 0, mirroring the `queued:` cue).
Context (working folder): the 61 open SPEC deltas live in `.add/tasks/*/TASK.md` §7 `### Spec delta` blocks (+ archived tasks, whose deltas need manual `_resolve_spec_delta` transcription — `drop-delta` rejects archived). `add.py deltas` lists them.
Honors (patterns / conventions): validate-before-write (a reject leaves CHANGELOG/RELEASES/state byte-unchanged) · forceable-but-loud (only `release_security_open` is un-forceable) · judgment-free engine (the floor COUNTS open deltas, never reads their meaning) · honest reject naming (sibling `honest-reject-naming`) → name the new code `release_open_spec_deltas`, never a proxy · present-only status cues (byte-identical when zero).
Anchors the contract cites: `cmd_release` FLOOR · `release_open_spec_deltas` (new forceable reject) · `release_data.open_spec_deltas` (count source) · `_collect_open_spec_deltas` · `_resolve_spec_delta` · the `status` staleness line.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A loud, forceable open-SPEC-delta RELEASE floor + a non-lossy `carry` delta lifecycle (`open ⇄ carried`) with a retrieval surface + a `status` staleness line — backpressure so SPEC deltas resolve instead of silently accumulating (the 61 today).
Framings weighed: floor + carry-lifecycle + retrieval (chosen) · floor-only, drain by hand with seed/drop (rejected: reaching deltas=0 forces DROPPING real notes — lossy — or spawning 61 tasks; no honest "defer" state) · a HARD un-forceable floor (rejected: deltas are not security; a release must stay shippable under `--force`, loud)
Must:
<must>
  - `cmd_release` FLOOR: when the open-SPEC-delta count > 0 and not `--force`, REFUSE with `release_open_spec_deltas` (loud — names the count + how to drain); validate-before-write (CHANGELOG/RELEASES/state byte-unchanged). Forceable; `release_security_open` stays the ONLY un-forceable floor check. Placed AFTER `release_undisclosed_waiver`.
  - The count comes from `release_data(root, state)["open_spec_deltas"]` — a new PURE record-set (`{count, items}`) wrapping `_collect_open_spec_deltas`; ONE source for the floor + `release-report` (gather, never judge — counts `[SPEC · open]`, never reads meaning).
  - `add.py carry-delta <slug> [--match SUBSTR | --all] --reason "<text>"`: flip `[SPEC · open]` → `[SPEC · carried]` (via `_resolve_spec_delta`) + append a ` [carried: <reason>]` provenance stamp (mirrors seeded's ` [→ ptr]`); the delta SURVIVES on disk. `--all` = every open delta in the slug; `--match` = the unique open delta containing SUBSTR; bare = the first. Validate-before-write.
  - `--reason` is REQUIRED for carry (a deferral must say why — no silent carry): missing/empty → `carry_reason_required`.
  - A carried delta no longer counts as `open` (clears the floor AND the staleness line) but stays RETRIEVABLE: `add.py deltas --carried` (and `--all`) list carried deltas in their own section; bare `deltas` shows open only (byte-identical output).
  - `add.py reopen-delta <slug> [--match SUBSTR]`: flip `[SPEC · carried]` → `[SPEC · open]` (re-activate); refuse `no_carried_spec_delta` if none.
  - `add.py status`: the EXISTING PRESENT-ONLY `spec    : <N> open SPEC delta(s)` cue (the prefix the SHIPPED spec-delta-guards contract pins) REFRAMED to name staleness + the drain surface — `spec    : <N> open SPEC delta(s) — stale; drain via add.py deltas (carry-delta / new-task --from-delta / drop-delta)` when N>0; byte-identical when N==0 (mirrors the `queued:` cue). [v2: keep `spec :`, never break the shipped guarantee; carry the staleness word.]
  - `carried` joins the recognized delta-status enum (`_SPEC_DELTA_RE` / the parser) so a carried line round-trips and is never re-counted as open; the engine never auto-carries/auto-drops (judgment-free — it flips a tag it was TOLD to flip).
  - Drain scope: LIVE `.add/tasks/*` only (where `_collect_open_spec_deltas` scans + the 61 live); archived-task deltas are out of scope (known: `drop-delta` rejects archived).
</must>
Reject:
<reject>
  - open SPEC deltas > 0 at `add.py release`, no `--force` -> "release_open_spec_deltas"
  - `carry-delta` with no/empty `--reason` -> "carry_reason_required"
  - `carry-delta` on a slug with no open SPEC delta (or a `--match` miss) -> "no_open_spec_delta"
  - `carry-delta --match SUBSTR` matching >1 -> "ambiguous_spec_delta"
  - `reopen-delta` on a slug with no carried SPEC delta -> "no_carried_spec_delta"
</reject>
After:
<after>
  - `release` with N>0 open deltas + no `--force` leaves CHANGELOG/RELEASES/state byte-unchanged + prints `release_open_spec_deltas`; with `--force` it records (loud: footer notes forceable rejects bypassed); `release_security_open` still never bypassable.
  - after `carry-delta`: the line reads `[SPEC · carried]` + `[carried: <reason>]`; `deltas` drops it from open; `deltas --carried` lists it; the `status` staleness count drops.
  - after `reopen-delta`: the line reads `[SPEC · open]` again; it re-enters the open count + floor + staleness.
  - the 61 are cleared to 0 OPEN (a mix of carried / seeded / dropped); `add.py deltas` prints "no open spec deltas"; the carried set is retrievable via `--carried`.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Adding `carried` to the delta-status vocabulary must round-trip cleanly — lowest confidence because `_SPEC_DELTA_RE` (group 2 = status) + `_EVIDENCE_RE` (preserves the `(evidence: …)` tail) are SHARED across collect/seed/drop; if `carried` is not added to the recognized status set, a carried line fails to match (crash, or a silent leak back into the open count). MITIGATION: extend the status alternation + a round-trip test (open→carry→deltas--carried→reopen→open, evidence byte-preserved).
  - [x] the floor + drain target LIVE tasks only — CONFIRMED at ground: `_collect_open_spec_deltas` globs `root/tasks/*/TASK.md` (not archive); the 61 are all live.
  - [ ] per-slug `--all` (not a global `carry-all`) is the right granularity — med confidence; per-slug keeps `--reason` scoped + mirrors `drop-delta`'s shape; a global bulk can be a follow-up delta.
  - [ ] `release_open_spec_deltas` is the honest name (not a proxy) — high confidence; aligns with the sibling `honest-reject-naming`.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the release floor refuses an open-delta cut (forceable)
  Given a project with >=1 closed-unreleased milestone AND N>0 open SPEC deltas
  When add.py release 1.13.0   (no --force)
  Then it is refused with "release_open_spec_deltas" naming N
  And CHANGELOG.md, RELEASES.md and state.json are byte-unchanged

Scenario: --force cuts past the open-delta floor (loud)
  Given the same project with N>0 open SPEC deltas
  When add.py release 1.13.0 --force
  Then the release is recorded (CHANGELOG + RELEASES row written)
  And the footer notes forceable rejects were bypassed

Scenario: security stays un-forceable even with deltas resolved
  Given an open HARD-STOP gate AND 0 open SPEC deltas
  When add.py release 1.13.0 --force
  Then it is refused with "release_security_open"
  And nothing is written

Scenario: carry defers an open delta without losing it
  Given a task with an open SPEC delta carrying an (evidence: …) tail
  When add.py carry-delta <slug> --reason "post-1.13 backlog"
  Then the line becomes [SPEC · carried] with [carried: post-1.13 backlog]
  And add.py deltas no longer lists it AND add.py deltas --carried does
  And the (evidence: …) tail is byte-preserved

Scenario: carry without a reason is refused
  Given a task with an open SPEC delta
  When add.py carry-delta <slug>   (no --reason)
  Then it is refused with "carry_reason_required"
  And the delta line is unchanged (still [SPEC · open])

Scenario: carry on a task with no open delta is refused
  Given a task with no open SPEC delta
  When add.py carry-delta <slug> --reason "x"
  Then it is refused with "no_open_spec_delta"
  And nothing is written

Scenario: reopen re-activates a carried delta
  Given a task with a [SPEC · carried] delta
  When add.py reopen-delta <slug>
  Then the line becomes [SPEC · open] again
  And it re-enters the open count (deltas lists it; the floor counts it)

Scenario: status shows a staleness line only when deltas are open
  Given N>0 open SPEC deltas
  When add.py status
  Then a "spec    : N open SPEC delta(s) — stale; drain via add.py deltas …" line is present (the shipped `spec :` cue, reframed to name staleness)
  And when N==0 the status output is byte-identical to today (no such line)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI surface (engine, NO-EXEC — records / flips text tags only; never tags/publishes):

add.py release <version> [--force]
  FLOOR (cmd_release, before any write; placed AFTER release_undisclosed_waiver):
    if not --force and release_data[...]["open_spec_deltas"]["count"] > 0:
      -> _die("release_open_spec_deltas: <N> open SPEC delta(s) unresolved — carry/seed/drop
               them (see add.py deltas) or pass --force to cut anyway (they ride unresolved).")
    validate-before-write: CHANGELOG.md / RELEASES.md / state.json byte-unchanged on reject
    forceable; release_security_open remains the ONLY un-forceable floor check

release_data(root, state)["open_spec_deltas"] = { "count": <int>, "items": [{task, text}] }
    PURE gather; wraps _collect_open_spec_deltas (LIVE tasks); no judgment field

add.py carry-delta <slug> [--match SUBSTR | --all] --reason "<text>"
  -> [SPEC · open] -> [SPEC · carried]  + append " [carried: <reason>]"
     (via _resolve_spec_delta; entry text + "(evidence: …)" tail byte-preserved)
     --all = every open delta in <slug> · --match = the UNIQUE open delta containing SUBSTR · bare = first
  rejects: carry_reason_required (no/empty --reason) · no_open_spec_delta (none / --match miss)
           · ambiguous_spec_delta (--match matches >1)
  validate-before-write: a reject writes nothing

add.py reopen-delta <slug> [--match SUBSTR]
  -> [SPEC · carried] -> [SPEC · open]   (re-activate)
  rejects: no_carried_spec_delta

add.py deltas [--carried | --all] [--json]
  default : open lessons + open SPEC deltas               (UNCHANGED — byte-identical)
  --carried: ADD a "carried spec deltas (<N>):" section   (retrieval surface)
  --all    : open + carried · --json adds "carried" + "carried_total" keys

add.py status
  + PRESENT-ONLY line when open SPEC deltas > 0 — the EXISTING `spec :` cue (the prefix the
    SHIPPED spec-delta-guards contract pins) REFRAMED to name staleness + the drain surface
    (v2 amendment: keep `spec :`, do not break the shipped guarantee; carry the staleness word):
      "spec    : <N> open SPEC delta(s) — stale; drain via add.py deltas (carry-delta / new-task --from-delta / drop-delta)"
    byte-identical when N == 0 (mirrors the queued: cue)

Delta-status enum: open | seeded | dropped | CARRIED (new — added to _SPEC_DELTA_RE)
State schema: NONE — deltas live in TASK.md §7 text; no state.json change (byte-identical state)
```

Status: FROZEN @ v2 — approved by Tin Dang
Least-sure flag surfaced at freeze: [contract] the v1→v2 amendment reconciles the status cue's PREFIX — v1 froze `stale :` not knowing the status surface already carries a `spec :` cue that the SHIPPED spec-delta-guards contract pins (`spec : N open`); v2 keeps `spec :` (honoring that guarantee) and REFRAMES it to name staleness + the drain surface — the riskiest remaining point is still the SHARED `carried` vocabulary (`_SPEC_DELTA_RE` group-2 alternation + `_EVIDENCE_RE` tail-preservation): a missed alternation makes a carried line leak back into the open count — cost: a round-trip regression (open→carry→reopen, evidence byte-preserved) proven before any delta is carried.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/`   <!-- engine (cmd_release floor + carry-delta/reopen-delta verbs + cmd_deltas retrieval + cmd_status line + release_data + _SPEC_DELTA_RE enum) + its tests + 3-tree sync. Widened to DIRECTORY tokens once measured at build: the 3-tree propagation touched add.py + add_engine/constants.py + engine_pin.py in each tree, so each tooling/ dir is declared whole (subtree containment) — same reservation as freeze-gate-universal. The DATA drain (carry flips across .add/tasks/*/TASK.md) lands under .add/ which the scope walk excludes. Comment stays backtick-free so the parser reads exactly the three tokens above. -->
Strategy (ordered batches): 1. red tests (new `test_delta_drain.py`: floor block/force + security-still-blocks + carry/reopen round-trip + `deltas --carried` retrieval + status staleness line) · 2. `release_data.open_spec_deltas` + the `cmd_release` floor check · 3. `_SPEC_DELTA_RE` += `carried` + `carry-delta`/`reopen-delta` verbs (reuse `_resolve_spec_delta`) + argparse · 4. `cmd_deltas --carried/--all` + the `cmd_status` staleness line · 5. DRAIN the 61 (carry most → backlog, seed the actionable, drop the stale) · 6. propagate 3-tree + re-pin ENGINE_MD5
Safety rule (feature-specific): validate-before-write on EVERY verb (a reject writes nothing) · `carried` must round-trip (regex alternation + `(evidence: …)` preserved) before any of the 61 are carried · the floor is forceable, `release_security_open` stays un-forceable · `--reason` required (no silent carry).
Code lives in: `add-method/tooling/` (canonical) → propagated to `.add/tooling/` + `_bundled/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `unittest discover` = **2084 passed, 0 failed**; dogfood `check` 440/0, `audit` clean (92 tasks)
- [x] coverage did not decrease — +11 new tests (`test_delta_drain.py`) + 2 `test_min_pillar` LIFECYCLE entries for the 2 new verbs; no test removed or skipped
- [x] no test or contract was altered during build — the tripwire was re-baselined at the v2 re-cross (tests→build); §3 was frozen (v2) BEFORE tests; the test tightening happened in the TESTS phase, not build
- [x] the green was EARNED, not gamed — TWO independent adversarial refute-reads: #1 (agent ad833225b1c15eee4) verified all logic EARNED but caught a real `stale :` vs `spec :` contract-prefix divergence → NOT-EARNED → closed via the human-approved v1→v2 contract amendment + a tightened test that would fail a non-conforming impl; #2 (agent a1dbed680e3f569a8) re-verified → **BLOCKER-CLOSED**, no new nits
- [x] concurrency / timing of the risky operation is safe — validate-before-write on the floor (a reject leaves CHANGELOG/RELEASES/state byte-unchanged); carry/reopen are single-file `_atomic_write` flips; `--all` flips in-place (line count preserved, indices stay valid)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only, no new deps; `--reason` text is stored as data (never eval'd); the carried stamp is plain-text appended
- [x] layering & dependencies follow CONVENTIONS.md — reuses the pure `_resolve_spec_delta` / `_select_spec_delta` / `_atomic_write`; the shared delta regex stays in `add_engine/constants.py`; honest reject naming (`release_open_spec_deltas`, `carry_reason_required`, `no_carried_spec_delta`)
- [ ] a person reviewed and approved the change   <!-- PENDING: human verify gate (conservative · risk:high) ->

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py release` with N>0 open SPEC deltas (no `--force`) exits non-zero with `release_open_spec_deltas` naming N; CHANGELOG/RELEASES/state byte-unchanged — test_floor_refuses_open_delta_release GREEN
- [x] `add.py release --force` records past the floor; `release_security_open` still refuses even with `--force` — test_force_cuts_past_floor + test_security_still_unforceable_with_deltas_clear GREEN (security un-forceable confirmed by both refute-reads)
- [x] `add.py carry-delta t --reason "x"` flips `[SPEC · open]`→`[SPEC · carried]` + `[carried: x]`, evidence byte-preserved; `deltas` hides it, `deltas --carried` shows it — test_carry_defers_without_loss GREEN + the live carried-line sample (global-data/TASK.md) shows text + `(evidence: ev)` byte-preserved, stamp appended after
- [x] `carry-delta` rejects no-reason (`carry_reason_required`), no-open (`no_open_spec_delta`), `--match`>1 (`ambiguous_spec_delta`); `--all` carries every open — CarryReopenTest suite GREEN
- [x] `add.py reopen-delta t` flips `[SPEC · carried]`→`[SPEC · open]` (re-enters the count), breadcrumb stripped; refuses `no_carried_spec_delta` — test_reopen_reactivates GREEN
- [x] `add.py status` shows the present-only `spec    : N open SPEC delta(s) — stale; drain via add.py deltas …` cue when N>0 (the shipped `spec :` prefix, reframed), byte-identical when 0 — test_status_shows_staleness_only_when_open GREEN (regex pins the prefix + staleness + drain pointer; would fail a `stale :` impl); test_spec_delta_guards still GREEN
- [x] the project's OWN `add.py deltas` reaches 0 OPEN — 62 drained to carried (5 live via the verb + 57 archived via direct `_resolve_spec_delta` transcription, human-approved); `deltas` open = 0, `deltas --carried` = **62 retrievable**; the FLOOR is live-filtered so archived deltas stay visible but never block a cut (scratch-proven: project-wide 2, floor 1)
- [x] the 3 engine trees byte-identical + `ENGINE_MD5` re-pinned (7e05d07c) + `ENGINE_PKG_MD5` (e87f5652); full suite green — md5 compare across 3 trees + pin/parity tests + `unittest discover` 2084/0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol is referenced: `cmd_carry_delta`/`cmd_reopen_delta` wired to argparse subparsers (`carry-delta`/`reopen-delta`); `_collect_carried_spec_deltas` used by `cmd_deltas --carried`; `_open_spec_delta_indices` used by `carry-delta --all`; `release_data["open_spec_deltas"]` read by the `cmd_release` floor; `_SPEC_STATUS_TOKEN_RE` used by `_resolve_spec_delta`; both verbs exercised under the `test_min_pillar` read-spy LIFECYCLE
- [x] DEAD-CODE (code) — `_SPEC_OPEN_TOKEN_RE` was REPLACED (not orphaned) by `_SPEC_STATUS_TOKEN_RE` (grep: 0 remaining refs to the old name); no other unused symbol introduced
- [x] SEMANTIC (refute-read) — read in full by two independent adversarial subagents: #1 read all 225 changed add.py lines + the frozen contract + every test diff → EARNED on logic, caught the real `stale :`/`spec :` contract divergence; #2 confirmed the v2 amendment closed it with the contract, impl, and test in agreement and the test non-vacuous. Both reproduced the 2084/0 suite + the security-un-forceable + non-lossy proofs.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-27

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] the resolution verbs (carry-delta / drop-delta / reopen-delta) reach only LIVE tasks via `_resolve_task`, yet the project-wide `deltas` count includes archived-task deltas — so an operator must hand-transcribe archived ones; let the verbs operate on the on-disk `.add/tasks/<slug>/TASK.md` when slug ∉ state.tasks, closing the asymmetry (evidence: 57/62 deltas were archived; `carry-delta <archived-slug>` rejected as unknown task → direct `_resolve_spec_delta` transcription was required)
- [SPEC · open] reconcile the SPEC-delta reject vocabulary: carry emits `ambiguous_spec_delta` / `no_open_spec_delta` while `drop-delta` emits `ambiguous_spec_match` / `no_matching_spec_delta` for the same conditions — sibling `honest-reject-naming` should pick one (evidence: refute-read nit; cmd_carry_delta vs cmd_drop_delta reject codes diverge)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a frozen contract drafted on a GROUND miss must be reconciled by a v1→v2 change-request + re-freeze, never a silently-deviating build — the §3 froze a `stale :` status prefix without knowing the shipped spec-delta-guards contract pins a `spec :` cue; the build kept `spec :` but left the contract saying `stale :` (evidence: refute-read #1 NOT-EARNED → human-approved v2 amendment → refute-read #2 BLOCKER-CLOSED) [folded foundation-version 56]
- [TDD · folded] a status/format-cue test must pin the LINE (prefix + count + framing + pointer) via assertRegex, not `assertIn` a single keyword — a keyword-only assert under-specifies the contract and lets a non-conforming impl pass invisibly (evidence: `assertIn("stale")` passed a `spec :`-prefixed line the v1 contract said must be `stale :`) [folded foundation-version 56]
- [ADD · folded] `_collect_open_spec_deltas` scans every `.add/tasks/*` dir (live AND archived-but-lingering), so a count that reads as project-live can include shipped history — a release FLOOR should count only what its verbs can clear (gather-wide, gate-narrow) (evidence: 62 "open" deltas were 5 live + 57 archived; the floor is now live-filtered) [folded foundation-version 56]
