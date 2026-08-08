# MILESTONE: Delta Resolution Polish

goal: polish the delta-resolution machinery from the deltas the first milestone surfaced: a true multi-file commit primitive (all-or-nothing across N files), a --match selector to target a specific open SPEC delta, and a compact --force override for an unrelated open SPEC delta
rationale: sub-milestone follow-up of **delta-resolution** (classified at that milestone's close, 2026-06-17). The delta-resolution build surfaced three forward SPEC deltas, out of scope then but worth a focused polish pass: (1) fold-command's verify refute-read showed `_atomic_write_many` SHRANK but did not ELIMINATE the mid-rename residual window — a true all-or-nothing multi-file commit closes it; (2) `seed-and-drop` can't target a specific open SPEC delta when a task holds several — a `--match` selector disambiguates; (3) the project-wide compact guard has NO override — an urgent compaction blocked by an UNRELATED open SPEC delta needs a recorded `--force` escape hatch. Grouped as one polish milestone because all three live on the delta-resolution machinery surface and are each engine edits (3-copy + ENGINE_MD5).
stage: mvp · status: active · created: 2026-06-17

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A TRUE multi-file commit primitive — stage every temp → fsync → rename-all, with rollback-on-any-failure
     — replacing/strengthening `_atomic_write_many` so `fold`/`seed`/`release` are all-or-nothing across N files
     (no partial mid-rename residue). A `--match <substr>` selector on `new-task --from-delta` AND `drop-delta`
     so a specific open SPEC delta is targetable when a task holds several. A `compact --force` escape hatch so
     an urgent compaction is not blocked by an UNRELATED open SPEC delta — the guard still REPORTS, the override
     is EXPLICIT + RECORDED. All three are engine edits: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned
     per task (flags ride existing commands — no new subcommand, so no new `test_min_pillar` census entry).
Out: NO new delta TYPES or grammar (delta-resolution already shipped seed/drop + fold). NO change to WHICH files
     fold/seed/release write — only the ATOMICITY of writing them. `--force` does NOT bypass a security HARD-STOP
     or a RELATED delta — it overrides only an unrelated open-SPEC block, and never silently (recorded). `--match`
     only TARGETS a delta; the human still decides seed vs drop (no auto-resolution). NO concurrency/locking rework.

## Shared decisions & glossary deltas   (living — every task must honor these)
- all-or-nothing (multi-file) — a multi-file write either lands EVERY file or NONE; a partial mid-rename residue
  is exactly the failure mode being closed. Stage all temps, fsync, then rename-all; on any failure roll back the
  already-renamed files to their prior bytes. Add to GLOSSARY.
- --match is a disambiguator, not a filter — it selects EXACTLY ONE open delta by substring; 0 matches or >1 match
  is a REJECT (named error), never a silent pick of the first.
- --force is explicit + visible — the compact guard still prints what it WOULD block; `--force` records the
  override (auditable) and proceeds. A security finding is never force-able (inherited HARD-STOP rule).
- engine-edit discipline (inherited) — every task edits all THREE add.py copies byte-identically AND re-pins
  ENGINE_MD5 in the SAME commit; parity/pin tests stay green throughout.

## Shared / risky contracts (freeze these first)
- the multi-file commit primitive — its signature, the stage-all→fsync→rename-all ORDERING, the rollback semantics
  on a mid-write failure, and the error code(s); fold/seed/release all call it, so freeze its shape first -> owning task `multi-file-commit`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] multi-file-commit     depends-on: none   — the all-or-nothing multi-file write primitive (stage→fsync→rename-all + rollback); fold/seed/release adopt it. The risky shared contract — freeze first.
- [x] delta-match-selector  depends-on: none   — `--match <substr>` on `new-task --from-delta` + `drop-delta` to target one open SPEC delta among several; reject 0-match / ambiguous.
- [x] compact-force-override depends-on: none  — `compact --force` escape hatch for an urgent compaction blocked by an UNRELATED open SPEC delta; guard still reports, override recorded.

## Exit criteria (observable; map each to the task that delivers it)
- [x] `fold`/`seed`/`release` write N files all-or-nothing — an injected mid-write failure leaves the prior state intact (no partial residue), proven by a failure-injection test   (← multi-file-commit) (verify: `python3 -m unittest test_multi_file_commit`)
- [x] a specific open SPEC delta is targetable via `--match <substr>` on `new-task --from-delta` and `drop-delta`; a 0-match or ambiguous `--match` is rejected with a named error   (← delta-match-selector) (verify: `python3 -m unittest test_delta_match_selector`)
- [x] `compact --force` completes an urgent compaction despite an UNRELATED open SPEC delta, with the override recorded; without `--force` the guard still blocks   (← compact-force-override) (verify: `python3 -m unittest test_compact_force_override`)

## Close — ship review (filled at milestone-done)
Ship by domain (engine / delta-resolution machinery):
- multi-file-commit — `_atomic_write_many` hardened to stage→fsync→rename-aside→rename-all with all-or-nothing rollback; `fold`/`release`/`seed` route through it. Evidence: `test_multi_file_commit` 11/11 (PrimitiveTest + AdoptionTest + per-caller atomicity + EnginePin). Gate PASS (conservative, human-gated).
- delta-match-selector — `--match <substr>` on `new-task --from-delta` and `drop-delta`; first-open default preserved byte-identical; 0-match→`no_matching_spec_delta`, >1→`ambiguous_spec_match`. Evidence: `test_delta_match_selector` 9/9. Gate PASS (auto).
- compact-force-override — `compact --force` overrides the `open_spec_deltas_unresolved` block ONLY (never a structural guard), bypass warned + recorded as `force_bypassed_spec_deltas`. Evidence: `test_compact_force_override` 6/6. Gate PASS (auto).

Goal-met map: all 3 forward SPEC deltas from delta-resolution resolved → 3/3 exit criteria green, each citing a passing suite. Full suite 1543 passed / 0 failed; `add.py check` 377/0; `audit` clean. Engine 3-copy parity + ENGINE_MD5 (3f82050…) held throughout. Each task had an independent refute-read (verdicts SOUND, nits fixed in-build).
