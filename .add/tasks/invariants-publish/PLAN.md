# PLAN: A task cannot publish an invariant that no test proves

slug: invariants-publish · created: 2026-07-27 · stage: mvp
milestone: direction-velocity
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a task's §3 can PUBLISH invariants, each citing the test that proves it, and the freeze refuses a published invariant that no test backs.
Framings weighed: an optional §3 block whose entries must each cite a resolvable test file, enforced at the existing freeze seam (chosen — the freeze is already the one place a contract's shape is validated, and `validate-then-write` means a refusal costs nothing; making the block OPT-IN keeps every task on disk freezing exactly as it does today, and opting in is precisely what binds you) · a project-level invariant registry (rejected — PROJECT.md `invariants:` already exists for project-wide rules; the gap is a TASK publishing something its dependents inherit, and a second global store would have no owner) · prose guidance with no refusal (rejected — an invariant nobody can fail is a comment, and this project has already paid for that once with `turn_ceiling`: declared in every arm, asserted equal by a test, read by nothing)
Must:
<must>
  - a §3 `Invariants (published):` entry must cite a proving test, or the freeze refuses and names WHICH invariant is unproven
  - a citation whose test FILE does not resolve under the project root is refused too — a citation to nothing is not a proof
  - a fully-cited block freezes exactly as any other contract does
  - a §3 with NO Invariants block is grandfathered: absence never becomes a new refusal, and the scaffold's own template line must freeze as-is
  - the template offers the block on all four twins, so a task can discover the feature without reading the engine
</must>
<reject>
  - a published invariant with no `(proof: ...)` citation, or one citing a file that does not resolve -> "invariant_without_proof"
</reject>
After:
<after>
  - a node can state something its dependents must not break, and be answerable for it
  - `invariant-inherit` has something real to walk: a published, proven invariant on an ancestor node
  - no task already on disk changes behaviour
</after>
Boundary: the block is markdown inside §3 — a `Invariants (published):` line followed by `  - <text>` bullets, each optionally carrying `` (proof: `path::test_name`) ``; the path is resolved as a FILE under the project root. Any other shape is simply not an invariant entry.
<assumptions>
  ⚠ requiring the test FILE to resolve, rather than the test FUNCTION to exist, is the right strictness — if wrong (someone cites the right file and the wrong test name): the citation still points a reader at the correct file and the §4 `covers:` machinery already resolves function-level claims; cost = a stricter check later, which is additive and breaks nothing that passes today.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract

```
PLAN.md §3 (OPTIONAL block, grandfathered by absence):

  Invariants (published):
    - <invariant text> (proof: `<path>::<test_name>`)

add.py :: _published_invariants(raw3: str) -> list[tuple[str, str | None]]
  PURE. Each entry -> (text, cited_path | None). No block -> []

cmd_freeze, inserted AFTER unflagged_freeze, BEFORE boundary_unfilled
  (validate-then-write: nothing is written on this path)
  entry with cited_path None                     -> _die invariant_without_proof
  entry whose cited_path does not resolve to a FILE under root.parent
                                                 -> _die invariant_without_proof
  the refusal NAMES the offending invariant text

templates/PLAN.md.tmpl  (4 TWINS)
  + a commented, OPTIONAL `Invariants (published):` line in §3
```
Ground: `add-method/tooling/add.py::cmd_freeze` — "validate-then-write: every refusal fires before any write", with the floor order `already_frozen` -> `contract_not_drafted` -> `unflagged_freeze` -> `boundary_unfilled` -> `scope_unresolved` -> `sensitivity_invalid`; the new floor slots after `unflagged_freeze` so the cheapest structural refusals still fire first. `_phase_spans(text).get(3, "")` is how cmd_freeze already reads §3 (`raw3`). `boundary_unfilled` is the precedent for an OPTIONAL §-line whose ABSENCE is grandfathered and whose PRESENCE is validated (`if bnd is not None`) — this block copies that shape exactly. `_declared_scope` is the precedent for backticked-token parsing inside §3. Template twins, all four currently md5 `4c1f6fc9bbf793066aa2086140db4da7`: `add-method/tooling/templates/PLAN.md.tmpl` · `.add/tooling/templates/PLAN.md.tmpl` · `add-method/.add/tooling/templates/PLAN.md.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/PLAN.md.tmpl`. `.add/PROJECT.md` carries project-wide `invariants:` that bind every task — this is the TASK-level counterpart, deliberately not a second global store.

Target (measurable): the new suite is RED before the change and GREEN after; a §3 with no Invariants block freezes with byte-identical behaviour to today (the grandfather test); a refused freeze leaves PLAN.md byte-identical; all four template twins stay md5-identical; `add-method/tooling/` (2882 currently green across both floors) stays green, with `test_min_pillar`'s lifecycle freeze and every existing freeze-floor test passing UNCHANGED.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `.add/tooling/` `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Regression floor: `add-method/tooling/` — the whole method suite, in particular every existing freeze-floor test (`test_scope_first_freeze.py`, `test_ai_plan_verify_gate.py`, `test_min_pillar.py`) which must pass UNCHANGED, plus `test_tree_parity.py` for the template twins and the `engine_pin` re-aim.
Persona (optional): `.add/personas/tdd-verifier.md` — the refusal is the deliverable.

Least-sure flag surfaced at freeze: [spec] whether anyone will actually publish an invariant. This ships a floor that only bites people who opt in, and the honest risk is not that it is too strict but that it is never used — in which case it is dead weight in the freeze path and in the template. The mitigation is downstream, not here: `invariant-inherit` gives a published invariant a consumer (`new-task --depends-on` prints what it inherits), and if that pair still goes unused after a real milestone, the right move is to delete both rather than to keep a feature alive by documenting it harder.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_invariant_without_a_proof_refuses_the_freeze: an uncited entry refuses · covers: M1, R:invariant_without_proof  [GATED]
  - test_invariant_citing_a_missing_test_refuses: a citation to a nonexistent file refuses · covers: M2, R:invariant_without_proof  [GATED]
  - test_refusal_names_the_offending_invariant: the message names WHICH one · covers: M1  [GATED]
  - test_the_freeze_writes_nothing_on_refusal: PLAN.md byte-identical after the refusal · covers: M1  [GATED]
  - test_a_proven_invariant_freezes: a cited, resolvable entry stamps FROZEN · covers: M3  [GATED]
  - test_no_invariants_block_is_grandfathered: absence freezes exactly as today · covers: M4  [GATED]
  - test_every_template_twin_carries_the_block: 4 twins, byte-identical · covers: M5  [GATED]
  - test_several_invariants_all_proven: a multi-entry block freezes · covers: M3  [edge]
  - test_one_bad_apple_among_proven_ones_still_refuses: one uncited entry among proven ones refuses · covers: M1  [edge]
  - test_the_template_block_is_commented_out_or_optional: a bare new task must still freeze · covers: M4  [edge]
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated.

Build-guidance (prose, not gated): resolve the cited path against the project root with the same fail-closed posture as `_declared_scope` — an outside-root path grants no proof. Keep `_published_invariants` PURE so it can be unit-tested without a project on disk.

Tests live in: `add-method/tooling/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned. The floor copies `boundary_unfilled`'s grandfathering shape exactly (absent line = no refusal, present line = validated) and slots after `unflagged_freeze` so the cheaper structural refusals still fire first. The template's line deliberately carries a `<optional — …>` placeholder so it does NOT match the parser's bare `Invariants (published):` header — that is what lets a freshly scaffolded task freeze untouched. THIS task's own direction bundle was authored by `add.py draft --from … --run-red --freeze --cross`, the verb its predecessor shipped: one call ran the suite, observed it RED, wrote §1+§3+§4, froze, and crossed to build.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite)
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) `test_no_invariants_block_is_grandfathered` is the positive control that stops the floor passing by refusing everything — it caught a real fixture defect, where the fixture left the template contract in place and `contract_not_drafted` fired before the floor under test, so four tests were passing for the wrong reason; (2) `test_one_bad_apple_among_proven_ones_still_refuses` proves the check is per-entry, not a block-level any/all; (3) `test_invariant_citing_a_missing_test_refuses` separates "cited" from "proven" — a citation to nothing is the same failure wearing a citation; (4) `test_the_freeze_writes_nothing_on_refusal` observes PLAN.md byte-identical, so validate-then-write is measured rather than assumed; (5) `test_the_template_block_is_commented_out_or_optional` guards the grandfather claim at the scaffold, where a bare new task would otherwise be unable to freeze. Path resolution is fail-closed with `is_relative_to`, mirroring `_declared_scope`. NOT claimed: that the cited test FUNCTION exists — only the file resolves; §1's assumption states this and why the stricter check is additive.

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-27

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose an optional §3 block whose entries must each cite a resolvable test file, enforced at the existing freeze seam; rejected a project-level invariant registry (rejected — PROJECT.md `invariants:` already exists for project-wide rules; the gap is a TASK publishing something its dependents inherit, and a second global store would have no owner) · prose guidance with no refusal (rejected — an invariant nobody can fail is a comment, and this project has already paid for that once with `turn_ceiling`: declared in every arm, asserted equal by a test, read by nothing)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned. The floor copies `boundary_unfilled`'s grandfathering shape exactly (absent line = no refusal, present line = validated) and slots after `unflagged_freeze` so the cheaper structural refusals still fire first. The template's line deliberately carries a `<optional — …>` placeholder so it does NOT match the parser's bare `Invariants (published):` header — that is what lets a freshly scaffolded task freeze untouched. THIS task's own direction bundle was authored by `add.py draft --from … --run-red --freeze --cross`, the verb its predecessor shipped: one call ran the suite, observed it RED, wrote §1+§3+§4, froze, and crossed to build.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
