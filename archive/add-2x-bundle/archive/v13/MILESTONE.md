# MILESTONE: Decision-seam reports — decisive facts first, engine-sourced

goal: A reviewer at any decision seam (contract approval · verify gate · milestone-done) gets the decisive facts first from one rendered, engine-sourced report — instead of digging through chat prose or a 250-line phase dump.
stage: mvp · status: active · created: 2026-06-04

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a `report --decide` view that detects the task's seam FROM STATE and renders
     a short digest — NEEDS YOUR JUDGMENT (extracted ⚠ / [~] / [ ] markers,
     verbatim), ENGINE FACTS (phase · gate · deps · tests), UNLOCKS, and the
     decide command line; a DECIDE NEXT footer on the milestone rollup; a TESTS
     column fallback to the §4 `Tests live in:` declaration; fence-preserving
     wrap in the phase drill-down.
Out: NO auto-gating — the digest renders, it never records a gate; no engine
     ranking/judging of markers (document order only; extraction ≠ judgment);
     no change to the AI's chat obligations (the digest is the artifact BEHIND
     the chat presentation, not a replacement); text + `--json` only, no
     web/HTML; no marker-grammar lint in `check` (deferred — see the ⚠ flag at
     the decide-digest freeze).

## Shared decisions & glossary deltas   (living — every task must honor these)
- `decision seam` — a point where a human records a judgment: setup lock-down ·
  contract approval (v7 one-approval) · verify gate · milestone-done. Derived
  ONLY from state.json (phase + gate + milestone status), never from prose.
- `decision marker` — prose conventions the reports surface verbatim:
  `⚠` (least-sure assumption) · `- [~]` (disclosed deviation) · `- [ ]`
  (unconfirmed item). The engine EXTRACTS them; it never interprets, scores,
  or filters them — add.py stays judgment-free, the human signature is the gate.
- v9 read-only discipline carried: every report path stays PURE, no writes.
- All CLI/JSON changes are ADDITIVE (existing `report` output shapes unchanged).

## Shared / risky contracts (freeze these first)
- `report --decide` CLI contract (flag · seam detection rule · digest section
  order · `--json` shape · exit codes) -> owning task decide-digest
- decision-marker extraction grammar (which line prefixes, from which §bodies)
  -> owning task decide-digest

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] decide-digest            depends-on: none — `report --decide` seam digest + rollup DECIDE NEXT footer
- [x] tests-declared-fallback  depends-on: none — TESTS column falls back to counting tests at the §4 `Tests live in:` path, footnoted `†declared`
- [x] fence-safe-wrap          depends-on: none — `_detail_body` leaves fenced ``` blocks unwrapped so contract/gherkin blocks round-trip on copy-paste

## Exit criteria (observable; map each to the task that delivers it)
- [x] `report <ms> <task> --decide` renders: the seam (from state), NEEDS YOUR
      JUDGMENT with every ⚠/[~]/[ ] marker verbatim, ENGINE FACTS, UNLOCKS, and
      the decide command — at the contract seam it renders the §1–§4 front
      (ranked flags first) instead of the gate digest        (← decide-digest)
- [x] The milestone rollup ends with DECIDE NEXT naming the next human decision
      (fold+archive when DONE · the seam-blocked task when ACTIVE)   (← decide-digest)
- [x] When `tasks/<slug>/tests/` is empty but §4 declares `Tests live in:`, the
      TESTS column shows the count found at the declared path with a `†`
      footnote — never a bare misleading 0        (← tests-declared-fallback)
- [x] A fenced block in any §body renders byte-identical inside the drill-down
      (no mid-token wrap); copy-paste of the §3 contract round-trips   (← fence-safe-wrap)
