# TASK: §0 GROUND carries a Ground SHA + check warns on line-refs without one

slug: ground-anchor-sha · created: 2026-06-30 · stage: mvp
milestone: drift-guard
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

Touches (files · symbols · signatures):
  - `add-method/tooling/templates/TASK.md.tmpl` §0 GROUND (the `Related intent:` line is the last §0 field, just shipped by M1) — ADD a `Ground SHA:` field after it. (×3 template trees; FULL template only — the fast lane stays low-ceremony.)
  - `add-method/skill/add/phases/0-ground.md` (the GROUND phase guide; a phases-lean-pool member) — shift the convention to "cite symbols, optionally `@sha`; line numbers rot — record a Ground SHA so any line ref reads 'as of' that commit". Must NET-ZERO the pool (compact in place).
  - `add-method/tooling/add.py:cmd_check` (the per-task loop, l.2598-2631; the milestone-backlink-drift WARN at l.2611-2621 is the SIBLING pattern) — ADD a WARN: a §0 GROUND citing bare line numbers (`l.NNN`) with NO `Ground SHA:` line → drift is undetectable. warn-never-block (exit 0).
  - `add-method/tooling/add.py:_read_milestone_line` (l.187) — sibling header-reader; add a parallel `_read_ground_sha(text)` + a §0-scoped bare-line-ref detector.
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` — re-pinned ×2 (canonical + dogfood; engine_pin is NOT bundled).
  - `add-method/tooling/test_ground_anchor_sha.py` — NEW test (mirrors test_milestone_backlink harness).
Context (working folder): grounded against HEAD `67e3be3` (this task's own Ground SHA, recorded by hand since the field ships in THIS task's build). The per-task loop already reads each TASK.md once for the milestone backlink — reuse that read for the §0 line-ref scan (one read, two checks).
Honors (patterns / conventions): warn-never-block (a `check` finding is a nudge, exit 0 — like the backlink-drift WARN); engine NO-EXEC (the engine provides the field + the warn; the AI fills the SHA via its own git — add.py never shells out); degrade-safe (an unreadable TASK.md skips the scan); re-pin ×3 in lockstep.
Anchors the contract cites: TASK.md.tmpl §0 `Ground SHA:` field · `_read_ground_sha` + the §0 bare-line-ref detector · cmd_check per-task line-ref-without-sha WARN · engine_pin.ENGINE_MD5
Issues/Risks (→ feed §1):
  - **lean pool at zero headroom** — `0-ground.md` is a phases-lean-pool member and the pool is at EXACTLY target (32224/32224 B, headroom 0). The new convention prose MUST be offset by compaction WITHIN 0-ground.md (net-zero or net-negative) — no rebaseline (the M1 discipline: compact, don't grow the budget for borrowed surface).
  - **false-positive line-ref detection** — scope the scan to the §0 GROUND block only (between `## 0` and `## 1`) and key on the `l.\d+` idiom (the dominant convention), so a `./tests/` path or a timestamp elsewhere is never flagged. WARN, never block.
  - **fast-lane parity** — the fast template also has a §0; deliberately OMIT `Ground SHA:` there (low-ceremony lane). The test asserts the FULL template only — no fast-template parity requirement for this field.
Related intent: PROJECT.md drift-guard rationale ("a closed TASK.md stays true to the code") · GLOSSARY "ground" · originating PR40 (api-proxy) audit — "line numbers rot; symbols don't … add ground_sha capturing the commit §0 was written against"; milestone drift-guard M3, sibling to artifact-graph's header-backlink pattern.
Ground SHA: 67e3be3

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: §0 GROUND carries a `Ground SHA:` anchor; `add.py check` warns when a §0 cites bare line numbers without one
Framings weighed: engine seeds the field + warns, AI fills the SHA (chosen — honors NO-EXEC, mirrors M1 Related-intent) · engine shells out to `git rev-parse` (rejected — breaks NO-EXEC) · doc-only convention shift, no field/warn (rejected — drift stays undetectable)
Must:
<must>
  - M1: `TASK.md.tmpl` §0 GROUND gains a literal `Ground SHA:` field (after `Related intent:`) — the FULL template only (fast lane omits it). (×3 template trees, byte-identical)
  - M2: `0-ground.md` shifts the convention to "cite symbols, optionally `@sha`; line numbers rot — record a Ground SHA so any line ref is 'as of' that commit" — and the phases lean pool stays WITHIN budget (compact in place, no rebaseline).
  - M3: `add.py check` WARNs (nudge, exit 0) when a task's §0 GROUND block cites bare line numbers (`l.NNN`) but carries no `Ground SHA:` line — naming the slug + how to fix. A §0 with a Ground SHA, or with no line refs, is silent.
  - M4: invariants — every `add.py` copy byte-identical == the RE-PINNED `engine_pin.ENGINE_MD5`; TASK.md.tmpl ×3 byte-identical; full suite green.
</must>
Reject:
<reject>
  - the line-ref scan flags a line number OUTSIDE the §0 GROUND block (e.g. a `./tests/` path, a §4 coverage figure) -> "line_ref_false_positive"
  - the missing-SHA finding is a BLOCKING check (exit 1) instead of a WARN -> "drift_warn_blocks"
  - the build edits add.py without re-pinning ENGINE_MD5 across all copies -> "engine_pin_drift"
  - the build grows the phases lean pool past target (rebaseline instead of compact) -> "lean_pool_rebaselined"
</reject>
After:
<after>
  - A new task's §0 carries `Ground SHA:`; `add.py check` warns (exit 0) on a §0 that cites `l.NNN` without a Ground SHA, and is silent once the SHA is present; add.py re-pinned ×3; template ×3 byte-identical; phases pool within budget; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Net-zero compaction of `0-ground.md` — lowest confidence: that I can add the symbols-over-line-numbers + Ground-SHA guidance AND compact ≥ the same bytes elsewhere in 0-ground.md so the pool (at 32224/32224, headroom 0) stays ≤ target. If wrong: a forced rebaseline (the M1 anti-pattern) or a blocked gate. Mitigate: tighten existing 0-ground prose first, measure, only then add.
  - [ ] The `l.\d+` idiom is the dominant bare-line-ref convention in §0 (so keying on it catches real drift with near-zero false positives) — confirmed by the live §0 blocks (`l.6286`, `l.2611-2621`); a raw `path:NNN` form is rarer and can be added later if needed.
  - [ ] Reusing the per-task loop's existing TASK.md read (for the milestone backlink) for the §0 scan needs no second file read — confirmed: the text is already in hand at l.2614-2615.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a new task's §0 carries a Ground SHA field   # M1
  Given a fresh project
  When I run `add.py new-task t1`
  Then t1's TASK.md §0 GROUND has a `Ground SHA:` field

Scenario: check warns on a §0 line-ref without a Ground SHA   # M3
  Given a task whose §0 GROUND cites `l.6286` and has no `Ground SHA:` line
  When I run `add.py check`
  Then a WARNING names the task and the missing Ground SHA
  And the exit code is 0   # warn-never-block

Scenario: a Ground SHA silences the line-ref warning   # M3
  Given a task whose §0 GROUND cites `l.6286` AND carries `Ground SHA: abc1234`
  When I run `add.py check`
  Then no Ground-SHA warning is raised for that task
  And the exit code is 0

Scenario: a line number outside §0 is never flagged   # R:line_ref_false_positive
  Given a task with no line refs in §0 but `./tests/` paths + a §4 figure elsewhere
  When I run `add.py check`
  Then no Ground-SHA warning is raised for that task

Scenario: engine + template parity holds   # M4, R:engine_pin_drift, R:lean_pool_rebaselined
  Given the build is complete
  Then every add.py copy is byte-identical and equals the re-pinned ENGINE_MD5
  And the 3 TASK.md.tmpl copies are byte-identical with a `Ground SHA:` field
  And the phases lean pool is within budget (≤ target)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Ground SHA anchor — frozen shape @ v1   (engine seeds the field + warns; the AI fills the SHA)

TASK.md.tmpl §0 GROUND gains, after the `Related intent:` line:
    Ground SHA: <git rev-parse --short HEAD at ground time — line refs are "as of" this commit>
  (a placeholder, like the other §0 fields; the AI fills it. FULL template only — fast lane omits it.)

add.py _read_ground_sha(text) -> str|None    — mirror of _read_milestone_line:
    return the `Ground SHA:` header value (after a `## 0` heading), stripped; None if absent or a
    placeholder (`<…>`).
add.py a §0-scoped bare-line-ref probe — _ground_cites_line_ref(text) -> bool:
    slice the §0 GROUND block (`## 0` … next `## `), True iff it contains the `l.\d+` idiom.

add.py cmd_check (per-task loop, reusing the TASK.md text already read for the milestone backlink):
    if _ground_cites_line_ref(text) and _read_ground_sha(text) is None:
        warnings.append((f"task '{slug}'", "§0 cites line numbers (l.NNN) with no `Ground SHA:` —
                         record `git rev-parse --short HEAD` so drift is detectable"))
  -> WARN only (exit 0); a missing/placeholder SHA on a §0 with NO line refs is silent; an
     unreadable TASK.md is skipped (degrade-safe).

Invariants: add.py ×3 byte-identical == re-pinned engine_pin.ENGINE_MD5; TASK.md.tmpl ×3 byte-identical;
phases lean pool ≤ target (compact 0-ground.md in place, never rebaseline).
```

Least-sure flag surfaced at freeze: [spec/contract] net-zero compaction of `0-ground.md` — the phases lean pool is at exactly target (32224/32224, headroom 0), so the new symbols-over-line-numbers + Ground-SHA guidance must be offset byte-for-byte by compaction within 0-ground.md; if it can't absorb the addition I return to SPECIFY rather than rebaseline. Secondary [test]: the `l.\d+` probe is §0-scoped so paths/figures elsewhere never false-positive.

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

Coverage target: behavior-complete (one test per Must + per Reject)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_new_task_has_ground_sha_field: new-task / assert §0 has `Ground SHA:`
  - test_check_warns_on_line_ref_without_sha: §0 cites l.6286, no SHA / check / assert WARN names t1 + exit 0
  - test_ground_sha_silences_warning: §0 cites l.6286 + SHA present / check / assert no warn + exit 0
  - test_line_ref_outside_ground_not_flagged: l.NNN only outside §0 / check / assert no warn
  - test_template_has_ground_sha_and_parity / test_engine_byte_identical_to_pin / test_phases_pool_within_budget (baseline still 40280)
</test_plan>

Tests live in: `add-method/tooling/test_ground_anchor_sha.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/tooling/templates/TASK.md.tmpl` `.add/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/skill/add/phases/0-ground.md` `.claude/skills/add/phases/0-ground.md` `add-method/src/add_method/_bundled/skill/add/phases/0-ground.md` `add-method/tooling/test_ground_anchor_sha.py`
Strategy (ordered batches): 1. TASK.md.tmpl: add literal `Ground SHA: <…>` after `Related intent:` (FULL template only). 2. 0-ground.md: shift convention to symbols-over-line-numbers + Ground SHA, COMPACT in place to net-zero the lean pool (measure before/after). 3. add.py: `_read_ground_sha` + `_ground_cites_line_ref` helpers; cmd_check per-task WARN reusing the existing TASK.md read. 4. propagate add.py + template to twins; re-pin engine_pin ×2; prepare_bundle. 5. full suite green + pool ≤ target.

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2543/0 (2536 + 7 new)
- [x] coverage did not decrease — new behavior fully guarded incl. the §0-scoped false-positive case
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; sibling guard tests (ground-context/issues/related-intent/wiring/tree-parity) NOT weakened — the dropped tokens (`textbase`, "grounding is complete when") were RESTORED in the doc, not removed from the tests
- [x] the green was EARNED, not gamed — refute-read below; dogfood proof: live `check` warns 4 older tasks, ground-anchor-sha's own SHA drops it out
- [x] concurrency / timing — none; pure read + string-scan in cmd_check, reusing the existing per-task TASK.md read (one read)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib re; reads confined under the project root
- [x] layering & dependencies follow CONVENTIONS.md — `_read_ground_sha`/`_ground_cites_line_ref` mirror `_read_milestone_line`; warn-never-block; engine NO-EXEC (no git subprocess)
- [ ] a person reviewed and approved the change — ENGINE + method-doc change → ESCALATED to Tin (human-gated)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] A new task's §0 carries a `Ground SHA:` field — confirmed: new-task test green; this task's own §0 now carries `Ground SHA: 67e3be3`
- [x] `add.py check` WARNs (exit 0) on a §0 citing `l.NNN` without a Ground SHA, silent once present / when the ref is outside §0 — confirmed: 3 check tests green + live dogfood (4 warned, ground-anchor-sha silent)
- [x] phases lean pool ≤ target with baseline STILL 40280 — confirmed: pool 32203 ≤ 32224 (0-ground.md 4280→4259 B, compacted in place; NO rebaseline)
- [x] every add.py copy == re-pinned ENGINE_MD5 (6dc41985); TASK.md.tmpl ×3 + 0-ground.md ×3 byte-identical — confirmed: parity/pin tests green
- [x] full suite green — confirmed: 2543/0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — `_ground_cites_line_ref` + `_read_ground_sha` are both called in the cmd_check per-task loop; `_ground_section` is called by both; the template field is rendered by new-task. All test-exercised + live-dogfooded.
- [x] DEAD-CODE — no orphan; `_GROUND_SHA_RE`/`_LINE_REF_RE` both used; helpers have a live caller.
- [x] SEMANTIC — read the full 0-ground.md diff: the Ground-SHA field + symbols-over-line-numbers convention were ADDED; prose compacted to net-zero; the four category keywords + "grounding is complete when" rubric remain intact (sibling guards green).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (a) Is the §0 scoping real or does the probe scan the whole file? REAL — `_ground_section` slices `## 0`…next `## `; the false-positive test puts `l.999` AFTER §0 and stays silent. (b) Does a placeholder SHA count as present? No — `_read_ground_sha` returns None for `<…>`, so a fresh template task with the placeholder is still (correctly) eligible to warn once it cites lines. (c) Did I weaken any sibling guard to get green? No — I RESTORED the doc tokens they pin (textbase, the rubric phrase); the only test edits are the NEW suite. (d) Lean pool gamed via rebaseline? No — baseline asserted STILL 40280; the pool shrank by real compaction. (e) Dogfood: live check warns 4 real older tasks and exempts this one — the feature does what it claims.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — read-only string scan; no secrets, no injection; the engine still NO-EXEC (no git subprocess — the SHA is AI-filled).
2. Concurrency: CLEAR — no new write path; reuses the existing single TASK.md read.
3. Architecture: CLEAR — helpers mirror the milestone-backlink pattern; warn-never-block preserved; lean discipline (compact, not rebaseline) honored.
Verdict: PASS
Residue: none.
Binding: advisory — method/trust (engine + method-doc change → human-gated; NOT mechanical)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (human-gated; engine + method-doc change; clean build, net-zero compaction, no residue) · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose engine seeds the field + warns, AI fills the SHA; rejected engine shells out to `git rev-parse` (rejected — breaks NO-EXEC) · doc-only convention shift, no field/warn (rejected — drift stays undetectable)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang (human-gated; engine + method-doc change; clean build, net-zero compaction, no residue))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
