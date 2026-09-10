---
type: Task
title: dogfood evidence-over-tests on real work and decide whether a bench is warranted
status: done
kind: explore
milestone: evidence-over-tests
scope:
  - .add
gives:
  - S1 `## FINDINGS` — the three numbers the design memo asked for, read from this bundle's own nodes and stamps, and the bench decision they force
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:af62485faf7327f9", binding: "sha256:e3b0c44298fc1c14" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:726887cabd3f0057" }
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: gate, authority: process, outcome: PASS, kind: sources, closed: "4/4" }
advised_by: method-steward
---
## CARD
goal: measure evidence-over-tests on the real work that shipped it — bound checks per referent, refutes and what their probes surfaced, human minutes at the freeze — and decide from the numbers whether a four-arm bench is warranted
why: the design memo refused to bench before dogfooding; two prior benches produced headline findings that were instrument artifacts. The numbers have to come from nodes and stamps, never from memory of the session
beat: done · next: add status

## RULES
<must>
- M1 how many bound checks did the loop-lane tasks freeze per binding referent (Musts · Rejects · filled edges · probed assumptions), and how many Musts at a plan floor carried two checks of different mode — read from the task nodes
- M2 how many refute stamps were recorded, at which tier, how many `outcome: refuted`, and what the probes surfaced — read from the stamps and the commits they changed
- M3 what the freezes cost in human decisions — read from the authority on each freeze stamp
- M4 is a bench warranted — decided by the trigger the memo set (found-refutes across the milestone, human minutes at freeze), and if the trigger's shape is wrong, say what the right shape is
</must>
<reject>
- R:INVENTED a number that is not read from a node, a stamp, a test id or a commit is not a finding -> "INVENTED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who reads the findings; taking the human who ratified the memo, at the next milestone's intake -> a finding aimed at nobody changes nothing
- A2 [which] covers: S1 · the request does not say which tasks count; taking the milestone's own three loop-lane nodes and its four direct commits — the only work that ran under the new rules -> n=3 is a smoke test, not a sample; the findings say so
- A3 [when] covers: S1 · n/a · the window is the milestone
- A4 [absent] covers: S1 · the request does not say what a refute at tier T1 (same session) proves; taking that it proves presence only — independence (T2) was never exercised here and is reported as unmeasured -> a held refute by the builder read as evidence of independence would be the assessment's own confirmation-bias loop
- A5 [order] covers: S1 · n/a · the numbers do not depend on order
- A6 [experience] covers: S1 · the request does not say how long the brief may be; taking one screen, numbers first, decision last -> a finding buried under narrative is the report-summary-first failure this bundle already carries

## PLAN
contract: S1 — four findings F1–F4, each with an evidence ref into this bundle or the git log, and one decision line
budget: ~20 tool calls

## CHECKS
- F1 names checks-per-referent for refute-verb and refute-gate-rung and the count of two-mode Musts · covers: M1 · sufficient when every number cites a node path
- F2 names the refute stamps, their tier, their outcomes, and what each probe changed · covers: M2 · sufficient when every probe cites a stamp or a commit
- F3 names the authority on every freeze stamp in the milestone · covers: M3 · sufficient when read from `verified[]`
- F4 states the bench decision and the trigger it was read against · covers: M4, R:INVENTED · sufficient when it names the trigger's defect if any
judged at the gate against ## FINDINGS, not by pytest.

## FINDINGS
- F1 (answers M1) · refute-verb froze 9 checks over 11 binding referents (M1–M4 · R:NORECEIPT R:NOFINDING R:UNSEALED R:NOVERDICT · E1 E2 · probed A2) — 0.82 checks per referent, four checks covering two referents each; refute-gate-rung froze 9 over 11 (M1–M6 · R:NOTINTEGRITY R:NOJUDGE · E1 E2 · probed A2) — 0.82. Musts at the plan floor carrying two checks of different mode: 0 of 10 — every Must has one mode, `acceptance` (8) or `contract`/`static` (2). The rule C1 states was not followed by the session that wrote it, one task later · (evidence: .add/tasks/refute-verb.md#checks · .add/tasks/refute-gate-rung.md#checks)
- F2 (answers M2) · 2 refute stamps, both tier T1 (the building session, `by: "builder:claude (same session, tier T1)"`), both `outcome: held`, 6 probes total, 0 `refuted`. The probes were not decorative: refute-verb P2 (`--probes -1` stamped verbatim) changed the build — argparse now refuses a negative count (commit 52f5f89e) — and was recorded as `held` because no FROZEN rule forbade it; refute-gate-rung P1/P3 confirmed the citation rule and latest-wins (A2 probe). Independence (tier T2, a fresh session) was not exercised in this milestone · (evidence: .add/tasks/refute-verb.md `verified[]` act: refute · .add/tasks/refute-gate-rung.md `verified[]` act: refute · git show 52f5f89e -- add-method/tooling/cli.py)
- F3 (answers M3) · every freeze in the milestone carries `authority: plan`, `by: "plan:evidence-over-tests…"` — milestone (1), refute-verb (freeze + refreeze after scope widening), refute-gate-rung (1): 0 interviewed decisions, 0 human minutes at any freeze. The one human decision was the memo's ratification ("go", 2026-09-10), before any node existed. Before/after is not measurable from this bundle: the previous milestone's freezes were interviewed at a human floor (checks-that-hold-in-ci: C1–C4) and carry no duration · (evidence: .add/milestones/evidence-over-tests.md `verified[]` · .add/tasks/refute-verb.md `verified[]` · .add/milestones/checks-that-hold-in-ci.md `verified[]`)
- F4 (answers M4) · Read literally, the memo's trigger fires: found-refutes across the milestone = 0 ("zero found refutes on a whole milestone means the probes are decorative"). Read against F2 it is wrong-shaped: a probe that changed the build or the spec was recorded `held` because the rung reads outcome against FROZEN rules, so `--found` undercounts what probes do. The right trigger counts probes that changed something (here 1 of 6) and requires at least one T2 refute before any bench is designed — every refute here was the builder reading its own green, the weakest tier, and the design's central claim (independence catches the shared misunderstanding) is UNMEASURED. Decision: no bench yet. The next real milestone runs its refutes at T2 (a fresh `add-advisor` session per task) and reports probes-that-changed-something; a bench is designed only if that number is 0 across the milestone · (evidence: this node F2 · https://claude.ai/code/artifact/facb60e5-a047-4db3-8edc-90312dc251c7 §10)

## EVIDENCE
receipt: none recorded
gate: PASS · authority process · by plan:evidence-over-tests · 2026-09-10

## LESSONS
- [method · M51 · folded] A refute recorded by the builder (tier T1) proves presence, never independence; the memo's bench trigger counted --found and undercounted probes that changed the build under a held outcome — count probes that changed something, and require one T2 refute before designing a bench (evidence: .add/tasks/dogfood-and-measure.md)
