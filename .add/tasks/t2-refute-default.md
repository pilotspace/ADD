---
type: Task
title: at floor ≥ plan the verify beat spawns a fresh refuter — T2 is the default, T1 a prelude
status: done
depth: standard
sensitivity: architecture
milestone: refute-at-t2
scope:
  - add-method/skill/add/SKILL.md
  - .claude/skills/add/SKILL.md
  - add-method/src/add_method/_bundled/skill/add/SKILL.md
  - add-method/skill/add/phases/verify.md
  - .claude/skills/add/phases/verify.md
  - add-method/src/add_method/_bundled/skill/add/phases/verify.md
  - add-method/agents/add-worker.md
  - .claude/agents/add-worker.md
  - add-method/src/add_method/_bundled/agents/add-worker.md
  - add-method/agents/add-advisor.md
  - .claude/agents/add-advisor.md
  - add-method/src/add_method/_bundled/agents/add-advisor.md
  - add-method/docs/05-verify.md
  - add-method/tests/skill
gives:
  - S1 verify.md §2 "Who refutes" — at floor ≥ plan the DEFAULT is a spawned fresh session (`add-advisor` refute mode, briefed from the frozen node before the diff), recorded `--tier T2`; the builder's own read is T1, a prelude that never satisfies the rung
  - S2 SKILL.md loop step 3 VERIFY — one clause naming the T2 spawn before the gate at floor ≥ plan
  - S3 add-worker.md §4 verify bullet — spawn `add-advisor` refute (T2) at floor ≥ plan, record its line with `--tier T2`; your own read is T1
  - S4 add-advisor.md refute mode — the Return line the worker records carries `--tier T2`
  - S5 docs 05 tier table — the T2 row says default and spawned; the T1 row says prelude
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:refute-at-t2 — apply all by Tin Dang 2026-09-10", at: 2026-09-11, act: freeze, authority: plan, direction: "sha256:3282e23f45c28a6e", binding: "sha256:22249aa61fd2594e" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:93e8de76f46258e4" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/t2-refute-default.d/runs/1.md }
  - { by: "builder", at: 2026-09-11, act: replan, authority: process, note: "R:SILENTTRIPWIRE guard: the HEAD-vs-worktree check in the static test now declares itself a TRIPWIRE (docstring only; no check renamed)" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/t2-refute-default.d/runs/2.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/t2-refute-default.d/runs/3.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/t2-refute-default.d/runs/4.md }
  - { by: "advisor:method-steward (fresh add-advisor session, opus)", at: 2026-09-11, act: refute, authority: process, outcome: held, probes: 3, receipt: /tasks/t2-refute-default.d/runs/4.md, tier: T2, note: "P1 verify.md:48-49 refute-read template omitted --tier so the copy-paste path recorded an uncountable stamp — change-request, acted on · P2 add-worker:93/SKILL:105 state floor >= plan without the quick/explore carve-out, but A2+A6 license the one-clause form and S1/FORMAT 8.4 carry the exact arming · P3 SKILL.md 13254->13256 bytes at 175/175 lines — R:BUDGET's line clause passed on a byte growth; the byte ceiling holds with 2 bytes headroom", changed: "verify.md's refute-read template now carries --tier T2 — the copy-paste path no longer records an uncountable stamp" }
  - { by: "plan:refute-at-t2 — apply all by Tin Dang", at: 2026-09-11, act: gate, authority: plan, outcome: PASS, receipt: /tasks/t2-refute-default.d/runs/4.md, brief: "sha256:89fdc185a020d207" }
---
## CARD
goal: the independent read is the DEFAULT the method states, not an option the ladder lists — every guide, agent and book page an agent reads at Verify says: at floor ≥ plan, spawn a fresh session to refute, record `--tier T2`; your own read is a prelude
why: dogfood-and-measure F2 — with the ladder stated as options, both refutes on the milestone that shipped it were T1; the tier the rung "asks for" was prose nobody was bound to. The engine now records the tier (refute-tier-and-changed); this task makes the prose choose, so the next dogfood's T2 count measures the method rather than a session's mood
beat: done · next: add status

## RULES
<must>
- M1 verify.md's tier paragraph states T2 as the default at floor ≥ plan in the imperative — spawn, brief from the frozen node before the diff, record `--tier T2` — and states T1 as an optional prelude, byte-identical across the three skill trees
- M2 SKILL.md's VERIFY step names the T2 spawn before the gate at floor ≥ plan, in all three trees, inside the existing line and byte budgets (funded by compression)
- M3 add-worker.md's verify bullet says spawn `add-advisor` in refute mode at floor ≥ plan and record its returned line with `--tier T2`, your own read being T1 — identical across its three trees
- M4 add-advisor.md's refute mode ends its Return with a line carrying `--tier T2`, identical across its three trees
- M5 docs 05's tier table: the T2 row reads "default" and "spawn", the T1 row reads "prelude"
</must>
<reject>
- R:T1RUNG no shipped tree says a T1 read satisfies the rung at floor ≥ plan — the word "prelude" or "optional" sits on every T1 statement, and no T1 statement names `floor ≥ plan` -> "T1RUNG"
- R:LADDERMOVED the T0 and T4 statements are unchanged in wording — T0 nobody at quick depth · process floor, T4 a protected holdout, a CI recipe, "a prompt is not isolation" -> "LADDERMOVED"
- R:BUDGET no budget literal in `skill_budget.py` moves; the surface line count is ≤ HEAD's -> "BUDGET"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3, S4, S5 · the request does not say who spawns; taking the session driving Verify (the skill orchestrator or an `add-worker` verify beat) spawns `add-advisor` — a subagent cannot reach the human, but it can spawn a peer -> a rule addressed to nobody is the F2 outcome again
- A2 [which] covers: S1, S2, S3, S4, S5 · the request does not say which floors; taking exactly the rung's arming (floor plan|human × standard|deep × not explore) — the same set the engine refuses R:UNREFUTED on, so the default and the refusal agree -> a default wider than the rung is ceremony on the mechanical lane; narrower leaves the rung asking for what the prose never told the agent to do
- A3 [when] covers: S1, S3 · the request does not say when the spawn happens; taking after the builder's own green and BEFORE the gate, the advisor briefed from the frozen node before it sees the diff -> a refuter that reads the diff first inherits the builder's frame, the shared-misunderstanding failure the tier exists to break
- A4 [absent] covers: S1, S2, S3, S4, S5 · the request does not say what happens with no advisor available; taking the ladder's existing answer — T3 a human at the gate — and never T1 -> silently downgrading to T1 is exactly the record F2 read
- A5 [order] covers: S1, S5 · n/a · the ladder order T0–T4 is unchanged (R:LADDERMOVED)
- A6 [experience] covers: S1, S2, S3, S4, S5 · the request does not say how much text; taking one imperative clause per site — the ladder already exists, this task changes its mood from a list to a default -> a paragraph per site re-inflates the surface the budgets hold
- A7 [when] covers: S2, S4, S5 · n/a · prose; the ladder's timing lives in S1/S3
- A8 [order] covers: S2, S3, S4 · n/a · one clause each, appended in place

## PLAN
contract: S1–S5 above — verify.md §2's "Who refutes" paragraph rewritten in the imperative (T2 default · T1 prelude), SKILL.md step 3 gains "at floor ≥ plan spawn `add-advisor` (refute, T2) before the gate" funded by compressing the same step, add-worker.md §4 verify bullet rewritten, add-advisor.md's Return line gains `--tier T2`, docs 05 T1/T2 rows re-worded; three trees each synced by copy; `PROSE_PINS["SKILL.md"]` re-aimed with the reason on its line.
strategy: red suite first in tests/skill/test_t2_refute_default.py; prose in the canonical tree, then copy to twins; run tests/skill (budgets, parity, tier ladder); no engine change, no full suite needed.
port: the three canonical files — the tests read the trees, never the transcript

## EDGES
- E1 Given an `add-worker` verify beat on a plan-floor task whose builder already ran its own refute (T1) · When it reads §4 · Then the text still tells it to spawn the T2 refute before the gate — the T1 read did not discharge the rung

## CHECKS
- test_verify_guide_makes_t2_the_default · covers: M1, R:T1RUNG, E1, A2 · contract · verify.md ×3 identical; the tier paragraph says spawn · brief · `--tier T2` · default at floor ≥ plan; T1 carries prelude/optional and no `floor ≥ plan`
- test_skill_loop_names_the_t2_spawn · covers: M2 · contract · SKILL.md ×3 identical; the VERIFY step names `add-advisor`, refute and T2 before `add gate`
- test_worker_verify_spawns_and_records_t2 · covers: M3, E1 · contract · add-worker.md ×3 identical; the verify bullet names spawn, refute, `--tier T2`, and T1 as its own read
- test_advisor_return_line_carries_tier · covers: M4 · contract · add-advisor.md ×3 identical; the refute mode's recorded line contains `--tier T2`
- test_book_tier_table_says_default_and_prelude · covers: M5 · contract · docs 05's T2 row has default and spawn; T1 row has prelude
- test_ladder_ends_unmoved_and_budgets_hold · covers: R:LADDERMOVED, R:BUDGET · static · verify.md still carries the T0 and T4 statements verbatim; `skill_budget.py` literals equal HEAD's; surface lines ≤ HEAD's
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/t2-refute-default.d/runs/4.md · kind: test-ids · 6/6 reported · exit 0 · 2026-09-11
refute: held · 3 probe(s) · tier T2 · by advisor:method-steward (fresh add-advisor session, opus) · against /tasks/t2-refute-default.d/runs/4.md · 2026-09-11 · P1 verify.md:48-49 refute-read template omitted --tier so the copy-paste path recorded an uncountable stamp — change-request, acted on · P2 add-worker:93/SKILL:105 state floor >= plan without the quick/explore carve-out, but A2+A6 license the one-clause form and S1/FORMAT 8.4 carry the exact arming · P3 SKILL.md 13254->13256 bytes at 175/175 lines — R:BUDGET's line clause passed on a byte growth; the byte ceiling holds with 2 bytes headroom · changed: verify.md's refute-read template now carries --tier T2 — the copy-paste path no longer records an uncountable stamp
gate: PASS · authority plan · by plan:refute-at-t2 — apply all by Tin Dang · receipt /tasks/t2-refute-default.d/runs/4.md · 2026-09-11

## LESSONS
- none filed — no lesson cites /tasks/t2-refute-default.md (add learn <lens> "<lesson>" --evidence /tasks/t2-refute-default.md)
