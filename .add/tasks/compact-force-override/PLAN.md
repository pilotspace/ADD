# TASK: Compact Force Override

slug: compact-force-override · created: 2026-06-17 · stage: mvp
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
  - `add-method/tooling/add.py:cmd_compact(args)` (~line 2923) — heavy-archive a milestone's files into
    `.add/archive/<slug>/`. The PROJECT-WIDE SPEC-delta guard at ~line 2966 (`open_spec_deltas_unresolved`)
    refuses the compaction if ANY open SPEC delta exists anywhere — even one UNRELATED to the milestone being
    compacted. This is the block --force overrides. Validate-before-move: the guard fires before the first rename.
  - `add-method/tooling/add.py:_collect_open_spec_deltas(root)` — the offenders the guard reports (task slugs with
    open SPEC deltas project-wide). Unchanged; --force reads the same list to REPORT what it bypasses.
  - the archived-entry dict (`entry` in cmd_compact; lives in `state["archived"]`) — gains an additive
    `force_bypassed_spec_deltas` stamp (the offending slugs) ONLY when --force actually bypasses, so the override
    is RECORDED + auditable. `entry["compacted"]` (the date stamp) is unchanged.
  - the `compact` subparser (~line 5746) — add `--force`.
Context (working folder): engine 3-copy mirrored + ENGINE_MD5 re-pin same commit. Tests beside canon. Mirrors the
  `cmd_release --force` precedent (force bypasses a FORCEABLE floor reject, prints that it did, records nothing
  silently). `--force` is a NEW FLAG on an existing command — NO test_min_pillar census change.
Honors (patterns / conventions): validate-before-move (a reject leaves tree+state byte-unchanged); --force is
  EXPLICIT + RECORDED, never silent; --force overrides ONLY the open-SPEC block, never the structural guards
  (milestone_not_archived / already_compacted / source_files_missing / open_deltas_unfolded / dest_exists) — those
  protect integrity and forcing past them would corrupt. Security un-forceability principle (n/a here: compact has
  no security guard, but the only-the-spec-block scoping honors it).
Anchors the contract cites: `cmd_compact`, the `open_spec_deltas_unresolved` guard, `force_bypassed_spec_deltas` stamp.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the project-wide compact guard has NO override — add a `compact --force` (or `--allow-open-spec`) escape hatch for when an UNRELATED open SPEC delta must not block an urgent compaction (from spec-delta-guards spec-delta)
Framings weighed: `--force` mirroring cmd_release (chosen) · `--allow-open-spec` narrow flag · interactive confirm prompt
  - chosen (`--force`) — reuse the established `cmd_release --force` shape: force bypasses ONLY the forceable open-SPEC block, prints what it bypassed, and records the override (auditable). Consistent vocabulary across the engine; one flag users already know.
  - `--allow-open-spec` — more self-documenting but a one-off flag name; REJECTED for consistency with --force elsewhere.
  - interactive confirm prompt — breaks the tool-agnostic / non-interactive contract; REJECTED.
Must:
<must>
  - `compact <slug> --force` BYPASSES the `open_spec_deltas_unresolved` block (the project-wide open-SPEC guard) and completes the compaction.
  - the override is RECORDED: the archived entry gains `force_bypassed_spec_deltas` = the bypassed offender slugs (auditable in state.json), written only when --force actually bypassed open deltas.
  - the override is VISIBLE: when --force bypasses, print a warning naming the bypassed offenders (the guard still REPORTS what it would have blocked) — never a silent skip.
  - `--force` overrides ONLY the open-SPEC block. The structural guards stay HARD even under --force: milestone_not_archived · unknown_milestone · already_compacted · archive_destination_exists · source_files_missing · open_deltas_unfolded (forcing past these would corrupt the archive).
  - `--force` ABSENT → behavior is byte-identical to today (the open-SPEC guard refuses); the refusal message now also mentions `--force` as the override.
  - validate-before-move preserved: a non-forceable reject still leaves tree + state byte-unchanged.
</must>
Reject:
<reject>
  - open SPEC delta(s) exist AND `--force` NOT passed -> "open_spec_deltas_unresolved" (existing; message now names --force)
  - any STRUCTURAL precondition fails (not archived / unknown / already compacted / dest exists / files missing / unfolded competency deltas) -> its existing error code, EVEN WITH --force (not overridable)
</reject>
After:
<after>
  - on a forced compaction past open SPEC deltas: the milestone is compacted into `.add/archive/<slug>/`, and `state["archived"][…]["force_bypassed_spec_deltas"]` records the bypassed slugs.
  - with no open SPEC deltas, `--force` is a harmless no-op (nothing recorded, identical output to an unforced clean compaction).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `--force` should override ONLY the open-SPEC block, not the other guards — lowest confidence because a user might expect `--force` to mean "force everything"; if wrong: they'd be surprised a structural guard still blocks. Cost: low and SAFE-biased — the structural guards protect archive integrity (a forced move past source_files_missing would lose data), so scoping --force narrowly is the correct, defensible default; the error message names the specific guard so the user understands why.
  - [ ] recording on the archived entry (`force_bypassed_spec_deltas`) is the right home (vs a print-only like release) — chosen because compact already stamps `compacted` on that entry, so the bypass is co-located + auditable; release prints-only because it has no per-cut state record.
  - [ ] `--force` with no open SPEC deltas records NOTHING (no empty stamp) — confirm, to keep the clean path byte-identical.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: open SPEC delta blocks compaction without --force
  Given a light-archived milestone M is ready to compact
  And some UNRELATED task has an open SPEC delta
  When I run compact M   (no --force)
  Then it exits non-zero with "open_spec_deltas_unresolved"
  And the message mentions --force
  And M's files are NOT moved (tree + state byte-unchanged)

Scenario: --force bypasses the open-SPEC block and records it
  Given a light-archived milestone M ready to compact
  And an unrelated task "other" has an open SPEC delta
  When I run compact M --force
  Then M is compacted into .add/archive/M/
  And state archived entry for M has force_bypassed_spec_deltas including "other"
  And a warning naming "other" was printed

Scenario: --force with no open SPEC deltas is a clean no-op
  Given a light-archived milestone M ready to compact
  And NO open SPEC delta exists anywhere
  When I run compact M --force
  Then M is compacted
  And the archived entry has NO force_bypassed_spec_deltas key

Scenario: --force does NOT override a structural guard
  Given a milestone slug that is still active (not archived)
  When I run compact <slug> --force
  Then it exits non-zero with "milestone_not_archived"
  And nothing is moved
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py compact <slug> [--force]
  ok   -> move the milestone's files into .add/archive/<slug>/ ; stamp entry["compacted"]=<date>
          --force ALSO bypasses the open-SPEC block: stamp entry["force_bypassed_spec_deltas"]=[slugs]
          (only when it actually bypassed open deltas) + print a warning naming them
  4xx  -> "open_spec_deltas_unresolved"  (open SPEC delta(s) exist and --force NOT passed; message names --force)
        | "milestone_not_archived" | "unknown_milestone" | "already_compacted"
        | "archive_destination_exists" | "source_files_missing" | "open_deltas_unfolded"
          ^ STRUCTURAL guards — NOT overridable by --force (forcing past them would corrupt the archive)

Scope of --force: overrides ONLY open_spec_deltas_unresolved. Validate-before-move preserved (a reject
leaves tree + state byte-unchanged). --force absent OR no open SPEC deltas -> byte-identical to today
(no force_bypassed_spec_deltas key written).

Schema: filesystem renames + state["archived"][i] gains additive key force_bypassed_spec_deltas
(list[str]) only on a real forced bypass. `--force` is a NEW FLAG on the existing compact subparser
(no new subcommand, no census change).
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization, 2026-06-22)
Least-sure flag surfaced at freeze: [spec] --force overrides ONLY the open-SPEC block, NOT the structural guards (not-archived / unknown / already-compacted / dest-exists / files-missing / unfolded) — why low: a user may read "--force" as "force everything"; cost: low + SAFE-biased — forcing past a structural guard (e.g. source_files_missing) would corrupt/lose the archive, so the narrow scope is the defensible default and each structural reject names its specific guard so the refusal is legible. Mirrors cmd_release --force (security/structural rejects un-forceable).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the --force bypass + record + report, the no-op clean path, and the un-forceable structural guard.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_open_spec_blocks_without_force: archive-ready M + unrelated open SPEC delta / compact M / exit!=0 "open_spec_deltas_unresolved" + msg mentions --force + .add/archive/M absent (unmoved)
  - test_force_bypasses_and_records: same + open delta in "other" / compact M --force / archive/M exists + state archived entry force_bypassed_spec_deltas contains "other" + warning names "other"
  - test_force_clean_noop: archive-ready M, NO open SPEC delta / compact M --force / compacted + entry has NO force_bypassed_spec_deltas key
  - test_force_does_not_override_structural: active (not-archived) milestone / compact <slug> --force / exit!=0 "milestone_not_archived" + nothing moved
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
Strategy (ordered batches): 1. in cmd_compact, gate the open-SPEC block on `forced`: bypass+warn+record when forced, else _die (message names --force). 2. add `--force` to the compact subparser. 3. mirror to 2 copies + re-pin.
Safety rule (feature-specific): --force overrides ONLY the open-SPEC block; structural guards stay hard; record the bypass on the archived entry (auditable), never silent.
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

- [x] all tests pass — `test_compact_force_override` 6/6; full suite 1543 passed, 0 failed
- [x] coverage did not decrease — +6 tests (1537→1543); a new branch (`--force`) is now exercised
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; the one post-crossing test edit (assertion STRENGTHENED, not weakened) was re-crossed tests→build→verify
- [x] the green was EARNED, not gamed — independent python-expert refute-read verdict SOUND, no blocking; its one nit (loose warning assert) was tightened to `assertRegex(out, r"--force bypassed open SPEC delta.*other")` + `assertIn("force_bypassed_spec_deltas", out)`
- [x] concurrency / timing — N/A: the bypass adds no IO; the move sequence + last-step additive state write are unchanged from the audited cmd_compact
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib argparse flag; no new imports; offender slugs only ever printed, never shell-interpolated
- [x] layering & dependencies follow CONVENTIONS.md — additive-cue: `--force` absent ⇒ byte-identical block + no state key; 3 engine trees byte-identical + engine_pin re-pinned (3f82050…) in the same commit
- [x] a person reviewed and approved the change — approved by Tin Dang (auto-mode standing authorization); refute-read SOUND, `add.py check` 377/0 + `audit` clean

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `--force` flag wired to the subparser (cmd_compact); `forced` gates the spec block; `force_bypassed_spec_deltas` written + asserted in tests; warning printed on stdout
- [x] DEAD-CODE (code) — no orphaned symbol: every added branch is reached by a test (block-without-force, bypass+record, clean-noop, structural-still-blocks, member-competency-still-blocks)
- [x] SEMANTIC — N/A (code change)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-23

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
