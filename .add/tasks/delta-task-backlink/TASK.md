# TASK: Seeded task §0 backlinks its originating delta; check warns on dangling lineage

slug: delta-task-backlink · created: 2026-06-30 · stage: mvp
milestone: traceability-ids
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_new_task` (the `--from-delta` seed block — resolves the prior's open SPEC delta, sets `feature_override`, flips the source to `[SPEC · seeded] … [→ slug]`, records state `from_delta`) — ADD a §0 reverse backlink: when seeding, pre-fill the new task's §0 `Related intent:` with its originating delta + prior, mirroring the existing §1 Feature pre-fill.
  - `add-method/tooling/add.py:cmd_check` (the per-task WARN loop — already reads `_task_text` once for the milestone-backlink + ground-sha WARNs) — ADD a dangling-lineage WARN: a `[SPEC · seeded] … [→ <slug>]` whose pointer task is neither a live state task NOR an archived task dir.
  - `add-method/tooling/add.py` — NEW pure helper `_seeded_delta_pointers(text) -> list[str]`: the pointer slugs from `[SPEC · seeded]` lines (via `_SPEC_DELTA_RE` group(3) + a `[→ <slug>]` sub-match).
  - `add-method/tooling/add_engine/constants.py:_SPEC_DELTA_RE` — `r"\s*-\s*\[\s*(SPEC)\s*·\s*(open|seeded|dropped|carried)\s*\]\s*(.+)$"`; group(3) tail carries the `[→ slug]` seed stamp. NEW `_SEED_POINTER_RE = re.compile(r"\[→\s*([A-Za-z0-9_-]+)\s*\]")`.
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` — re-pinned ×2 (canonical + dogfood).
  - `add-method/tooling/test_delta_task_backlink.py` — NEW guard suite (seed pre-fills §0 backlink · check WARNs on a dangling pointer · archived/live pointer is silent).
Context (working folder): `.add/tasks/*/TASK.md` §7 SPEC-delta lines (the seeded stamp lives here) · state.json `tasks.<slug>.from_delta` (lineage key) · `.add/archive/**/tasks/<slug>/` (a completed seeded task moves here — must NOT read as dangling) · TASK.md.tmpl §0 `Related intent:` placeholder (×3 template trees, FULL only — fast lane has no §0 Related-intent line).
Honors (patterns / conventions): engine NO-EXEC (no git/subprocess) · warn-never-block (a `check` finding is exit-0 nudge) · validate-then-write + `_atomic_write_many` (seed already writes new+flip as one commit) · degrade-safe (unreadable TASK.md → skip) · pure transforms (`_seeded_delta_pointers` is IO-free, mirrors `_select_spec_delta`).
Anchors the contract cites: cmd_new_task `--from-delta` seed block · cmd_check per-task WARN loop · `_seeded_delta_pointers` · `_SPEC_DELTA_RE` / `_SEED_POINTER_RE` · `.add/archive` lookup
Issues/Risks (→ feed §1):
  - **archived-pointer false positive** — when a seeded task completes and its milestone is archived, its dir moves to `.add/archive/`; the seeded `[→ slug]` line still lives in the (possibly still-live) prior task. "Dangling" MUST mean: pointer not in state AND not under `.add/archive/**/tasks/<slug>/`. Else every healthy completion would WARN.
  - **§0 override safety** — the seed-time `Related intent:` pre-fill must only fire on `--from-delta` and only replace the template PLACEHOLDER (a fresh task's §0 is still the placeholder), never a hand-written line. Mirror the §1 Feature `re.sub(count=1)`.
  - **fast-lane** — `TASK.fast.md` has no §0 Related-intent line; the §0 backlink pre-fill applies to the FULL template only (skip silently when the line is absent).
Related intent: traceability-ids M4 (sub-milestone of the artifact-trust roadmap) · PR40 (api-proxy) audit — "a SPEC delta turned into a task has only a one-way pointer; promote recurring links so lineage is bidirectional" · GLOSSARY "SPEC delta" / "seed" · completes the M2 artifact-graph backlink family (task↔milestone, milestone↔release → now delta↔task).
Ground SHA: 3e56342

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the delta→task lineage is BIDIRECTIONAL — a `--from-delta` seed pre-fills the new task's §0 with a backlink to its originating delta, and `add.py check` WARNs when a `[SPEC · seeded]` delta points at a task that no longer exists (dangling lineage)
Framings weighed: pre-fill §0 `Related intent:` on seed + a check WARN for dangling pointers (chosen — symmetric with the existing forward `[→ slug]`, reuses the per-task read, NO-EXEC, warn-only) · a new `[← prior]` machine field in §7 (rejected — a second stamp to maintain; §0 prose is where intent already lives) · a hard gate that blocks new-task when the source delta is missing (rejected — violates warn-never-block)
Must:
<must>
  - M1: a `--from-delta <prior>` seed pre-fills the new task's §0 `Related intent:` with a backlink naming the originating delta text + prior task (mirrors the existing §1 Feature pre-fill; same atomic write).
  - M2: the §0 pre-fill only REPLACES the template placeholder (`<…>`) and only on `--from-delta`; a non-seeded new-task, or a `Related intent:` already authored, is left untouched. The fast template (no §0 Related-intent line) is skipped silently.
  - M3: `add.py check` WARNs (nudge, exit 0) for each `[SPEC · seeded] … [→ <slug>]` whose `<slug>` is neither a live state task (`state.tasks`) NOR an archived task (`_archived_task_slugs(state)`) — a dangling lineage.
  - M4: a seeded pointer that DOES resolve (live task OR archived dir) is silent; an unreadable TASK.md is skipped (degrade-safe); the WARN never turns red (`check` exit unchanged by it).
  - M5: invariants — every `add.py` copy byte-identical == the RE-PINNED `engine_pin.ENGINE_MD5`; the phases lean pool is UNTOUCHED; full suite green.
</must>
Reject:
<reject>
  - a non-seeded new-task, or one whose §0 `Related intent:` is already authored, has its §0 overwritten -> "backlink_clobbers_authored"
  - a seeded pointer that resolves to a live or archived task is flagged dangling -> "false_dangling_warn"
  - the dangling-lineage finding turns `check` red (exit 1) instead of a warn -> "lineage_warn_blocks"
  - the build edits add.py without re-pinning ENGINE_MD5 across all copies -> "engine_pin_drift"
</reject>
After:
<after>
  - After a `--from-delta` seed, the new task's §0 `Related intent:` names its originating delta; `add.py check` warns on any seeded delta whose pointer task is gone (and is silent for resolvable/archived ones); add.py re-pinned ×3; phases pool unchanged; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Archived-pointer resolution — lowest confidence: that "not dangling" is `slug in state.tasks OR slug in _archived_task_slugs(state)`. Confirmed `_archived_task_slugs` reads `state.archived[].task_slugs` (the same resolver `cmd_ready` trusts; "archived ⇒ was PASS-done" invariant) — no FS glob. If wrong (a removal path that doesn't record `task_slugs`): a healthy completed-then-archived seed would WARN — noise that trains users to ignore the signal. Mitigate: a scenario seeds → archives the pointer task → asserts SILENCE.
  - [ ] The §0 pre-fill placeholder match is safe — confirmed: a fresh full TASK.md §0 carries the literal `Related intent: <…>` placeholder; `re.sub(count=1)` on the placeholder line only, gated by `from_delta`, cannot touch a non-seeded or hand-edited task.
  - [ ] `[→ slug]` is the only pointer grammar — confirmed: `_resolve_spec_delta` appends exactly ` [→ <pointer>]`; `_SEED_POINTER_RE` reads it back.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a --from-delta seed pre-fills the §0 backlink   # M1
  Given a prior task with an open `[SPEC · open]` delta
  When I run `add.py new-task child --from-delta prior`
  Then child's §0 `Related intent:` names the originating delta + prior task
  And the prior's delta is flipped to `[SPEC · seeded] … [→ child]`

Scenario: a plain new-task leaves §0 untouched   # M2, R:backlink_clobbers_authored
  Given no --from-delta
  When I run `add.py new-task plain`
  Then plain's §0 `Related intent:` is still the template placeholder (not overwritten)

Scenario: check WARNs on a dangling seeded pointer   # M3
  Given a live task whose §7 has `[SPEC · seeded] x (evidence: y) [→ ghost]` and no task `ghost` exists
  When I run `add.py check`
  Then a dangling-lineage WARN names task and `ghost`
  And `check` still exits 0   # warn-never-block

Scenario: a resolvable or archived pointer is silent   # M4, R:false_dangling_warn
  Given a seeded delta `[→ done-child]` whose task was completed and archived under `.add/archive/`
  When I run `add.py check`
  Then no dangling-lineage WARN is printed for `done-child`
  And `check` exits 0

Scenario: the dangling WARN never blocks   # R:lineage_warn_blocks
  Given a dangling seeded pointer and NO red findings elsewhere
  When I run `add.py check`
  Then the exit code is 0 (a warn, never red)

Scenario: engine parity holds   # M5, R:engine_pin_drift
  Given the build edited add.py
  When I check every add.py copy
  Then all are byte-identical and == the re-pinned engine_pin.ENGINE_MD5
  And the phases lean pool is unchanged
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
delta↔task backlink — frozen shape @ v1   (engine completes the seed lineage; NO-EXEC, warn-only)

add.py cmd_new_task — in the `--from-delta` seed block, alongside the existing §1 Feature pre-fill:
    when from_delta AND a `[SPEC · open]` was selected, replace the §0 Related-intent PLACEHOLDER:
      re.sub(r"(?m)^Related intent:\s*<.*>\s*$",
             f"Related intent: seeded from {prior} spec-delta — \"{delta_text}\" [← {prior}]",
             rendered, count=1)
  -> fires ONLY on --from-delta; matches the `<…>` placeholder ONLY (a hand-written line or the
     fast template's absent line is left untouched). Part of the SAME _atomic_write_many seed commit.

add.py _seeded_delta_pointers(text) -> list[str]   (PURE, IO-free):
    for each line matching _SPEC_DELTA_RE with group(2) == "seeded":
        m = _SEED_POINTER_RE.search(group(3));  if m: collect m.group(1)
  -> the pointer slugs a task's §7 seeded deltas point at. constants._SEED_POINTER_RE = r"\[→\s*([A-Za-z0-9_-]+)\s*\]".

add.py cmd_check — in the per-task WARN loop, reusing `_task_text` (one read):
    live = set(tasks);  arch = _archived_task_slugs(state)
    for ptr in _seeded_delta_pointers(_task_text or ""):
        if ptr not in live and ptr not in arch:
            warnings.append((f"task '{slug}'", f"seeded SPEC delta points at '{ptr}' which no longer "
                             f"exists (dangling lineage) — re-point or drop the delta"))
  -> WARN only (feeds `warnings`, never `checks`/`failed`); degrade-safe (unreadable -> _task_text None -> skip).

Invariants: add.py ×3 byte-identical == re-pinned engine_pin.ENGINE_MD5; phases lean pool untouched.
```

Least-sure flag surfaced at freeze: [contract] archived-pointer resolution — the dangling test is `ptr not in state.tasks AND ptr not in _archived_task_slugs(state)`. Risk: a task-removal path that doesn't record `task_slugs` would make a healthy completed-then-archived seed WARN (noise). Mitigated: `_archived_task_slugs` is the SAME resolver `cmd_ready` trusts (archived ⇒ PASS-done), and a scenario seeds→archives→asserts silence. Secondary [contract]: the §0 pre-fill `re.sub` matches the `<…>` placeholder ONLY, gated by `from_delta`, so it can never clobber an authored Related-intent line.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete (one test per Must + per Reject)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_seed_prefills_section0_backlink: new-task --from-delta / §0 Related intent names the delta + prior; source flipped [→ child]
  - test_plain_newtask_leaves_section0: new-task (no --from-delta) / §0 Related intent still the `<…>` placeholder
  - test_check_warns_on_dangling_pointer: a live task with `[SPEC · seeded] … [→ ghost]`, no `ghost` / check prints dangling WARN, exit 0
  - test_archived_pointer_is_silent: seed → archive the pointer task / check prints no dangling WARN for it, exit 0
  - test_dangling_warn_never_blocks: dangling pointer, no red findings / check exit 0
  - test_seeded_delta_pointers_pure: `_seeded_delta_pointers` parses seeded `[→ x]`, ignores open/dropped
  - test_engine_byte_identical_to_pin / test_phases_pool_untouched
</test_plan>

Tests live in: `add-method/tooling/test_delta_task_backlink.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/add_engine/constants.py` `.add/tooling/add_engine/constants.py` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/tooling/test_delta_task_backlink.py`
Strategy (ordered batches): 1. add `_SEED_POINTER_RE` to constants.py + export. 2. add pure `_seeded_delta_pointers(text)` to add.py. 3. cmd_new_task: §0 Related-intent pre-fill on --from-delta (re.sub placeholder, count=1, in the rendered template before write). 4. cmd_check: dangling-lineage WARN reusing `_task_text` + `_archived_task_slugs`. 5. propagate add.py ×3 + constants.py ×3; re-pin engine_pin ×2; prepare_bundle. 6. full suite green.

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: as planned. One additional re-pin surfaced: editing `add_engine/constants.py` changed the PACKAGE digest, so `ENGINE_PKG_MD5` (the second pin in engine_pin.py, computed by `engine_manifest.package_digest`) needed re-aiming ×2 too — 19 `*_pkg_digest_3tree` failures pointed straight at it (51671e2b → d66bd8da).
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2559/0 (exit 0)
- [x] coverage did not decrease — +8 tests added (delta-task-backlink suite); none removed
- [x] no test or contract was altered during build — only the new test file + engine code; §3 frozen @ v1 untouched
- [x] the green was EARNED, not gamed — refute-read below; behavior tests went 8 RED → green only after the real seed pre-fill + WARN landed
- [x] concurrency / timing of the risky operation is safe — seed pre-fill rides the existing `_atomic_write_many` seed commit; the WARN is read-only
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib `re`; one new shared regex
- [x] layering & dependencies follow CONVENTIONS.md — NO-EXEC honored (no git); warn-never-block; the new regex lives in `add_engine/constants.py` with the other shared delta regexes
- [ ] a person reviewed and approved the change — engine change ESCALATES to the human

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `new-task child --from-delta prior` writes child's §0 `Related intent: seeded from prior spec-delta — "…" [← prior]` — confirmed by test_seed_prefills_section0_backlink + reading the file
- [x] a plain `new-task` keeps the §0 `<…>` placeholder (no clobber) — confirmed by test_plain_newtask_leaves_section0
- [x] `add.py check` prints a dangling-lineage WARN naming the missing pointer, exit 0; silent for a live OR archived pointer — confirmed by the 3 CheckWarnsDangling tests
- [x] every add.py copy == re-pinned ENGINE_MD5 (e23cd35e); add_engine package == re-pinned ENGINE_PKG_MD5 (d66bd8da); phases pool untouched; full suite green — confirmed by parity/pin tests + 2559/0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_SEED_POINTER_RE` consumed by `_seeded_delta_pointers`; `_seeded_delta_pointers` called from cmd_check's per-task loop; the §0 pre-fill `re.sub` runs in cmd_new_task's `from_delta` branch
- [x] DEAD-CODE (code) — no orphaned symbol; the new regex + helper are both referenced
- [x] SEMANTIC (prose / non-code) — read in full: the dangling test reuses `_archived_task_slugs` (the same resolver `cmd_ready` trusts), so a completed-then-archived seed stays silent — verified by test_archived_pointer_is_silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (1) the 8 behavior tests were RED before the build (seed pre-fill absent → §0 placeholder; WARN absent → no "ghost"); (2) the archived-silence path is exercised by a real injected `state.archived[].task_slugs` record, not a stub — flipping it back to a live/missing slug changes the verdict; (3) confirmed the §0 `re.sub` matches the `<…>` placeholder ONLY (test_plain_newtask asserts a non-seeded task keeps its placeholder), so it cannot clobber an authored line; (4) the 19 PKG-digest failures were a REAL drift signal (constants.py changed the package) — fixed by re-pinning, not by relaxing the parity tests.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — `re` only; no secrets/injection; the WARN is read-only and never blocks.
2. Concurrency: CLEAR — the seed pre-fill rides the existing single atomic seed commit; the check is a pure read.
3. Architecture: CLEAR — NO-EXEC honored; the lineage resolution reuses `_archived_task_slugs` (one source of truth, the same `cmd_ready` trusts); the regex sits with its sibling delta regexes in constants.py.
Verdict: PASS
Residue: none
Binding: advisory — method-trust (escalates to human regardless)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose pre-fill §0 `Related intent:` on seed + a check WARN for dangling pointers; rejected a new `[← prior]` machine field in §7 (rejected — a second stamp to maintain; §0 prose is where intent already lives) · a hard gate that blocks new-task when the source delta is missing (rejected — violates warn-never-block)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned. One additional re-pin surfaced: editing `add_engine/constants.py` changed the PACKAGE digest, so `ENGINE_PKG_MD5` (the second pin in engine_pin.py, computed by `engine_manifest.package_digest`) needed re-aiming ×2 too — 19 `*_pkg_digest_3tree` failures pointed straight at it (51671e2b → d66bd8da).
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

