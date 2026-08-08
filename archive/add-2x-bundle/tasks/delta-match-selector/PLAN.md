# TASK: Delta Match Selector

slug: delta-match-selector · created: 2026-06-17 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
  - `add-method/tooling/add.py:_resolve_spec_delta(text, new_status, pointer=None) -> str|None` (~line 4704) —
    PURE flip of the FIRST `[SPEC · open]` line to new_status (+ optional `[→ pointer]`). The selection point:
    today it always takes the first open. Will gain an optional pre-selected line index so a --match-chosen
    delta can be flipped instead of the first (match absent → byte-identical first-open behavior).
  - `add-method/tooling/add.py:_first_open_spec_text(text) -> str|None` (~line 4725) — the first open delta's
    display text (evidence-stripped), pre-fills a seeded task's §1 Feature. Used in the no-match path unchanged.
  - `add-method/tooling/add.py:cmd_new_task` from-delta seed block (~lines 774-782) — resolves prior's open SPEC
    delta (feature pre-fill + flip to seeded). Gains the --match selection path.
  - `add-method/tooling/add.py:cmd_drop_delta(args)` (~line 834) — flips a task's first open SPEC delta to dropped.
    Gains the --match selection path.
  - the `new-task` subparser (~line 5644, where `--from-delta` is defined) + the `drop-delta` subparser — add `--match`.
  - `_SPEC_DELTA_RE` / `_SPEC_OPEN_TOKEN_RE` (~line 4701) — the open-delta line grammar the selector reuses.
Context (working folder): engine 3-copy mirrored + ENGINE_MD5 re-pin in the same commit. Tests beside canon.
  `--match` is a NEW FLAG on EXISTING commands (new-task / drop-delta) — NOT a new subcommand, so NO test_min_pillar
  LIFECYCLE census entry is needed (census tracks subcommands, not flags).
Honors (patterns / conventions): additive-cue convention (—match absent → byte-identical first-open behavior);
  validate-before-write (a 0-match / ambiguous reject writes nothing); the pure-transform pattern of `_resolve_spec_delta`.
Anchors the contract cites: `_resolve_spec_delta` (gains line_index), a NEW `_select_spec_delta` selector, `cmd_new_task`/`cmd_drop_delta`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: add a `--match <substr>` selector to `new-task --from-delta` and `drop-delta` so a specific open SPEC delta can be targeted when a task holds several (from seed-and-drop spec-delta)
Framings weighed: case-insensitive substring on the delta header-line text (chosen) · case-sensitive exact-text · regex
  - chosen — `--match <substr>` selects the unique OPEN SPEC delta whose header-line text contains <substr> (case-insensitive). Forgiving, no escaping, and the explicit no-match/ambiguous rejects let the user refine. Reuses the existing per-line `_SPEC_DELTA_RE` selection.
  - case-sensitive exact — surprising (users half-remember wording/case); REJECTED.
  - regex — powerful but an injection/escaping footgun for a disambiguation aid; REJECTED (out of scope).
Must:
<must>
  - `--match <substr>` is accepted by BOTH `new-task --from-delta` and `drop-delta`. It selects, among the relevant task's OPEN SPEC deltas, the UNIQUE one whose header-line text contains <substr> (case-insensitive), then resolves THAT one — seed flips it `[SPEC · seeded] [→ <new>]`, drop flips it `[SPEC · dropped]` — exactly as the first-open path does.
  - on SEED, the §1 Feature pre-fill uses the MATCHED delta's text (not the first open).
  - `--match` ABSENT → behavior is byte-identical to today (resolve the FIRST open SPEC delta).
  - validate-before-write: a 0-match or ambiguous `--match` refuses and writes nothing (no task created, no delta flipped).
  - selection matches the delta's TEXT, not its `(evidence: …)` tail.
</must>
Reject:
<reject>
  - `--match <s>` matches NO open SPEC delta in the task -> "no_matching_spec_delta"
  - `--match <s>` matches MORE THAN ONE open SPEC delta -> "ambiguous_spec_match"  (names the count; the user narrows)
  - the task has NO open SPEC delta at all (with or without --match) -> "no_open_spec_delta"  (existing; unchanged)
  - `--match` passed to `new-task` WITHOUT `--from-delta` -> "match_requires_from_delta"  (match targets the PRIOR's delta; meaningless alone — reject, never silently ignore)
</reject>
After:
<after>
  - exactly the targeted open SPEC delta is flipped (seeded/dropped); every other delta in the task is byte-unchanged.
  - on seed, the new task exists with its §1 Feature reflecting the MATCHED delta; on any reject, no file changed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ matching is case-INSENSITIVE substring on the delta's HEADER-LINE text — lowest confidence because a user could expect a multi-line entry's continuation text to be searchable, or case-sensitivity; if wrong: a continuation-only term wouldn't match. Cost: minor — the no_matching reject is explicit, so the user sees it and refines; SPEC deltas are near-always single-line.
  - [ ] the existing first-open path stays EXACTLY as-is when --match is absent (additive-cue) — confirm via the unchanged seed-and-drop tests staying green.
  - [ ] `--match` on new-task without `--from-delta` is a reject (match_requires_from_delta), not a silent ignore — confirm.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: drop --match targets a specific open delta
  Given task T has open SPEC deltas "alpha thing" and "beta thing"
  When I run drop-delta T --match beta
  Then "beta thing" becomes [SPEC · dropped]
  And "alpha thing" stays [SPEC · open]

Scenario: seed --match targets a specific open delta and pre-fills from it
  Given task PRIOR has open SPEC deltas "rate limit" and "retry budget"
  When I run new-task follow --from-delta PRIOR --match "retry budget"
  Then PRIOR's "retry budget" becomes [SPEC · seeded] [→ follow]
  And PRIOR's "rate limit" stays [SPEC · open]
  And follow's §1 Feature reflects "retry budget"

Scenario: match is case-insensitive
  Given task T has an open SPEC delta "Rate Limit retries"
  When I run drop-delta T --match "rate limit"
  Then that delta becomes [SPEC · dropped]

Scenario: no --match keeps the first-open behavior (byte-identical)
  Given task T has open SPEC deltas "alpha" then "beta"
  When I run drop-delta T   (no --match)
  Then "alpha" (the first) becomes [SPEC · dropped]
  And "beta" stays [SPEC · open]

Scenario: --match with no matching open delta is rejected
  Given task T has open SPEC delta "alpha"
  When I run drop-delta T --match zzz
  Then it exits non-zero with "no_matching_spec_delta"
  And T's TASK.md is byte-unchanged

Scenario: --match matching multiple open deltas is rejected
  Given task T has open SPEC deltas "alpha one" and "alpha two"
  When I run drop-delta T --match alpha
  Then it exits non-zero with "ambiguous_spec_match"
  And T's TASK.md is byte-unchanged

Scenario: --match on new-task without --from-delta is rejected
  Given any project
  When I run new-task foo --match bar   (no --from-delta)
  Then it exits non-zero with "match_requires_from_delta"
  And no task foo is created
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py drop-delta <slug> [--match <substr>]
add.py new-task <slug> --from-delta <prior> [--match <substr>]
  ok   -> resolve the UNIQUE open SPEC delta selected by --match (or the FIRST open when --match absent):
          drop -> [SPEC · dropped] ; seed -> [SPEC · seeded] [→ <slug>] + §1 Feature pre-fill from the matched delta
  4xx  -> "no_matching_spec_delta"   (--match matched zero open deltas)
        | "ambiguous_spec_match"     (--match matched >1; message names the count)
        | "no_open_spec_delta"       (no open SPEC delta at all — existing, unchanged)
        | "match_requires_from_delta"(--match on new-task without --from-delta)

New pure selector:
  _select_spec_delta(text, match=None) -> (status, line_index, display_text)
     status ∈ {"ok","no_open","no_match","ambiguous"}; match=None -> first open;
     match=<s> -> unique open whose header text contains <s> (case-insensitive, evidence excluded)
  _resolve_spec_delta(text, new_status, pointer=None, line_index=None)  # line_index None -> first open (back-compat)

Schema: filesystem only — flips ONE `[SPEC · open]` line in a TASK.md (validate-before-write; reject = no write).
  `--match` is a NEW FLAG on existing new-task / drop-delta subparsers (no new subcommand, no census change).
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization, 2026-06-22)
Least-sure flag surfaced at freeze: [spec] matching is case-INSENSITIVE substring on the delta's HEADER-LINE text only — why low: a user might expect a multi-line entry's continuation to be searchable or case-sensitive matching; cost: a continuation-only term won't match, but the explicit `no_matching_spec_delta` reject makes that visible so the user refines (SPEC deltas are near-always single-line). Additive: --match absent is byte-identical to today's first-open behavior, so the risk is confined to the new flag.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject of --match; first-open back-compat preserved.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_drop_match_targets_specific: 2 open deltas / drop-delta T --match beta / beta dropped, alpha still open
  - test_seed_match_targets_and_prefills: 2 open in PRIOR / new-task follow --from-delta PRIOR --match "retry budget" / that one seeded [→ follow], other open, follow §1 Feature reflects it
  - test_match_case_insensitive: "Rate Limit retries" / drop-delta T --match "rate limit" / dropped
  - test_no_match_first_open_byte_identical: 2 open / drop-delta T (no --match) / first dropped, second open (regression: existing seed_and_drop stays green)
  - test_no_matching_rejects: drop-delta T --match zzz / exit!=0 + "no_matching_spec_delta" + TASK.md byte-unchanged
  - test_ambiguous_rejects: 2 open both containing "alpha" / drop-delta T --match alpha / exit!=0 + "ambiguous_spec_match" + byte-unchanged
  - test_match_requires_from_delta: new-task foo --match bar (no --from-delta) / exit!=0 + "match_requires_from_delta" + no task foo
  - test_three_trees_byte_identical_and_pinned: pin parity
</test_plan>

Tests live in: `tooling`   <!-- engine tests live beside canon at add-method/tooling/test_*.py -->
MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py`
Strategy (ordered batches): 1. add `_select_spec_delta` selector + `line_index` param to `_resolve_spec_delta` (back-compat). 2. wire the --match path into cmd_drop_delta + cmd_new_task (match absent → unchanged). 3. add `--match` to both subparsers. 4. mirror to 2 copies + re-pin.
Safety rule (feature-specific): validate-before-write — a no_match / ambiguous / match_requires_from_delta reject must write NOTHING.
Code lives in: `./src/`
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

- [x] all tests pass — 9/9 in test_delta_match_selector; full suite 1537 green
- [x] coverage did not decrease — +9 tests: every Must + every Reject + back-compat + evidence-exclusion (incl. malformed)
- [x] no test or contract was altered to pass — §3 frozen untouched; post-cross edit ADDED a hardening test (no assertion weakened); re-crossed to re-anchor the §4 snapshot
- [x] the green was EARNED — independent python-expert refute-read: VERDICT SOUND, no BLOCKING. Confirmed line_index↔flip consistency, open-only + evidence-excluded match, write-free rejects, byte-identical back-compat. Its one fidelity nit (a malformed unclosed `(evidence:` leaked into the matchable text) FIXED in-build (cut at first `(evidence:`) + a regression test; its multi-line-continuation nit is the disclosed header-line behavior (frozen §1 flag), accepted
- [x] concurrency / timing — n/a; pure in-memory selection + single-file write per command, no shared state
- [x] no exposed secrets, injection openings — `--match` is a plain case-insensitive substring (NOT regex), no eval/escaping surface; stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — engine 3-copy byte-identical (efb7eac0) + ENGINE_MD5 re-pinned same change; --match is a flag (no census change, per §0)
- [x] a person reviewed and approved the change — auto autonomy: self-gated under the 2026-06-22 standing authorization, with an independent subagent refute-read substituting for human inspection

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_select_spec_delta` called by cmd_new_task (seed) + cmd_drop_delta; `--match` on both subparsers; `line_index` flows select→resolve (verified by the refute-read + tests)
- [x] DEAD-CODE (code) — REMOVED the now-orphaned `_first_open_spec_text` (its sole caller adopted `_select_spec_delta`'s display_text); `_spec_delta_entries` still used (3 refs); no new orphan
- [x] SEMANTIC — n/a (code); §1/§3 read in full and matched against the implementation

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization; independent python-expert refute-read SOUND) · date: 2026-06-22

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
