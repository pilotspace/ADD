# ceremony-to-effort WM1 re-measure — 2026-07-13

3 reps · `add` arm · pinned meter (`claude-sonnet-5 --effort medium`) · engine =
feat/ceremony-to-effort (`ec1a675`, all 7 milestone tasks) installed editable by the
arm's own setup. Archived: `benchmark/runs/ceremony-r{1,2,3}`. Method: same
transcript anatomy as the 2026-07-13 audit (assistant-message turns; `add.py
<subcommand>` invocations in Bash tool_use).

## Per rep

| rep | turns | add.py calls | --help | repeated-identical cmds | cost | fidelity | regressions |
|-----|------:|-------------:|-------:|------------------------:|------:|---------:|------------:|
| r1  | 119   | 25           | 1      | 2                       | $3.27 | 0.97     | 0 |
| r2  | 140   | 15           | 0      | 1                       | $3.69 | 0.98     | 0 |
| r3  | 144   | 16           | 1      | 2                       | $3.57 | 0.98     | 0 |
| **mean** | **134** | **18.7** | **0.7** | **1.7** | **$3.51** | **0.98** | **0** |

## Same metric over the archived honest ADD rounds (identical counting script)

| round | turns | add.py calls | cost |
|-------|------:|-------------:|------:|
| baseline-round3 | 197 | 27 | $6.26 |
| enforced-r1 / seeded-r1 | 245 | 33 | $7.41 |
| hint-r1 | 321 | 25 | $11.25 |
| **ceremony (mean)** | **134** | **18.7** | **$3.51** |

(lean-r1/2/3 excluded: 1 add.py call each — those agents bypassed the engine
entirely, which is why add-lean-loop was held open. Archived spec-kit on the same
meter: 133 turns / $4.00 / fid ≤ these reps — workload-version comparability
unverified, noted not claimed.)

## Verdict vs the milestone exit bar

- calls ≤ 12 → **UNMET** (mean 18.7, best rep 15) — but −31% vs baseline-round3's 27
- zero --help → **near** (0.7 mean vs 2–6 before)
- zero duplicate-identical retries → **near** (1.7 mean, ~8–13% of calls vs 12–21%)
- turns/cost ≤ 77.7t/$2.97 → **UNMET on this meter** (134t/$3.51) — the 77.7/$2.97
  bar came from the risk-proportional round whose raw record is not in
  `benchmark/runs/`; on rounds that ARE archived, ceremony is the cheapest honest
  ADD ever measured (−32% turns, −44% cost vs baseline-round3), fid 0.97–0.98, 0
  regressions
- oracle fidelity held → **MET** · scope_violation → r1/r3 each self-healed one
  (`re-cross` visible), r2 clean

## Residual waste anatomy (the next levers, from these transcripts)

1. **double init ×every rep** — the arm's setup already ran `pilotspace-add init`;
   the agent re-runs `add.py init` (+1–2 calls/rep). Harness/flow interaction:
   status should say "project exists — do NOT init".
2. **milestone bait, r1** — 3× `new-milestone` despite the wrapper explicitly
   prescribing the oneshot lane; message-layer instruction lost (r1 is the
   25-call outlier).
3. **re-cross repairs** (r1, r2 ×2 each) — scope declarations still get repaired
   post-freeze; the scope echo shows the resolution but can't force a re-draft.
4. **status re-reads ×3/rep** — orientation re-anchoring; candidate for a
   `--brief` habit or recipe reinforcement.
