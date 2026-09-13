---
type: Task
title: A human-floor PASS refuses a self-refute
status: done
depth: standard
sensitivity: security
milestone: loop-that-closes
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine
  - add-method/tooling/engine_pin.py
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
  - add-method/FORMAT.md
gives:
  - S1 the gate refusal `R:SELFREFUTE` — at computed floor `human`, `gate PASS` refuses while the latest refute citing the gated receipt claims `tier: T1` or no tier
  - S2 the plan-floor notice on the gate's success line naming the same state, promoted or dropped on the count
  - S3 `_refute_of` returns (outcome, tier) — presence, outcome and the tier CLAIM, never a judgment of it
generated: { by: add/3.6.0, at: 2026-09-11 }
verified:
  - { by: "human:Tin Dang", at: 2026-09-13, act: interview, authority: human, interview: "sha256:c2f79c6aa39741e0", receipt: /tasks/refute-tier-floor.d/interviews/1.md, answers: "A1=confirm|A2=confirm|A3=confirm|A4=confirm|A5=confirm|A6=confirm|E1=confirm|E2=confirm|E3=confirm|E4=confirm|E5=confirm|E6=confirm|R:SELFREFUTE=confirm|R:TIERJUDGED=confirm|R:NOTICEASREFUSAL=confirm|M1=confirm|M2=confirm|M3=confirm|M4=confirm|M5=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-13, act: interview, authority: human, interview: "sha256:9fa3f2ff97035a13", receipt: /tasks/refute-tier-floor.d/interviews/2.md, answers: "A1=confirm|A2=confirm|A3=confirm|A4=confirm|A5=confirm|A6=confirm|A7=confirm|A8=confirm|A9=confirm|A10=confirm|A11=confirm|E1=confirm|E2=confirm|E3=confirm|E4=confirm|E5=confirm|E6=confirm|R:SELFREFUTE=confirm|R:TIERJUDGED=confirm|R:NOTICEASREFUSAL=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-13, act: freeze, authority: human, direction: "sha256:e10bafc6cd1bfe25", binding: "sha256:69e14c1306e71f45", gives: "sha256:8a656234b6a2c0e1" }
  - { by: "cli", at: 2026-09-13, act: brief, authority: process, brief: "sha256:d9589e56e9823b80" }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/1.md }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/2.md }
  - { by: "advisor:engine-notary", at: 2026-09-13, act: refute, authority: process, outcome: held, probes: 10, receipt: /tasks/refute-tier-floor.d/runs/1.md, tier: T2, changed: "no build change; the read found M1's authority_for clause bound by no check — every check drove the floor through sensitivity: alone, so a mutant swapping the COMPUTED floor for the DECLARED one survives the full suite" }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/3.md }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/4.md }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/5.md }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, floor: regression, outcome: FAIL, receipt: /tasks/refute-tier-floor.d/runs/6.md }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/7.md }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/8.md }
  - { by: "advisor:engine-notary", at: 2026-09-13, act: refute, authority: process, outcome: refuted, probes: 16, receipt: /tasks/refute-tier-floor.d/runs/7.md, tier: T2, note: "a sensitivity: data task (plan floor) + `add refute <slug> --by me --tier T1 --held` + `add gate <slug> PASS` emits 'notice: ... claims `T1` - a green read by its own builder IS A PRELUDE, NEVER THE RUNG'S ANSWER; a human floor refuses this (R:SELFREFUTE)', but frozen M2 quotes that notice VERBATIM without the inserted clause. The allowlist fix threaded its `why` clause into a string M2 states literally (M1 never quotes its refusal, so that half was free), and test_plan_floor_notices_never_refuses binds only the substrings notice:/T1/R:SELFREFUTE, so the drift is invisible - restore M2's literal for the T1/no-tier branch, or refreeze M2. Second, still unbound: the by/tier decorrelation landed only on the HUMAN fixture, so a mutant suppressing the PLAN-floor notice by reading by: passes all 18 checks - repro: data task, --by fresh:verifier --tier T1, gate PASS must still notice; mirror both decorrelated cases into test_plan_floor_notices_never_refuses. Verified dead: the gate-judges-by mutant, the FORMAT 8.4 deletion, the variable-key AST evasion, the denylist revert and the T2-dropped allowlist all fail by the right check; the 13-value illegible sweep leaks nothing (quoted 'T2' parses to T2 and correctly passes); all 14 behavioural probes unchanged." }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/9.md }
  - { by: "process:run", at: 2026-09-13, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/10.md }
  - { by: "advisor:engine-notary", at: 2026-09-13, act: refute, authority: process, outcome: held, probes: 14, receipt: /tasks/refute-tier-floor.d/runs/9.md, tier: T2, changed: "no build change; all three fixes verified against receipt 9. M2's notice literal is emitted EXACTLY for both values its placeholder covers (T1 and no tier), and the new clause survives only on the illegible branch M2 does not cover - silence, not contradiction. Six mutants all die by the right check against a control of 18 passed: re-threading the why-clause through M2's T1 branch, suppressing the plan notice by reading by:, and noticing whenever by: looks like the builder with the tier ignored are each killed by a DIFFERENT assertion inside test_plan_floor_notices_never_refuses, so all three of its cases bind independently; the denylist revert is killed by test_an_unreadable_tier_floors_up; SIGNING_TIERS widened to include T1 kills 5 checks and narrowed to drop T3 kills 7, so the derivation is bound in both directions. A 17-value human-floor sweep leaks nothing, M1's refusal still names the claim and the fresh-session command for both T1 and no tier, R:REFUTED still answers first, and all 14 behavioural probes from the first read are unchanged. One residual margin, not a break: the literal is asserted with `in`, so text APPENDED after (R:SELFREFUTE) is not caught - a mutant doing that passes 11 of 11; the build does not do it, and line equality on the notice line would close it." }
  - { by: "advisor:gate-security-reviewer", at: 2026-09-13, act: refute, authority: process, outcome: held, probes: 9, receipt: /tasks/refute-tier-floor.d/runs/9.md, tier: T2, changed: "security lens re-review: CLEAR TO GATE. The allowlist closes the fail-open class (25-value matrix; the two laundering values I found, tier: 'T1 ' and [T1], now refuse), introduces nothing new (live add.py diffed against an INDEPENDENT pristine pre-fix baseline held since the first sitting — the check M60/M62 demand — plus four twins byte-identical and ENGINE_MD5 matching), and closes the AST residue BEYOND spec: both the variable-key and the helper-call evasions now fail, which the structural guard alone never could." }
  - { by: "human:Tin Dang", at: 2026-09-13, act: gate, authority: human, outcome: PASS, receipt: /tasks/refute-tier-floor.d/runs/9.md, brief: "sha256:ae340909a9e0ec51" }
advised_by: gate-security-reviewer
---
## CARD
goal: `gate PASS` at computed floor `human` refuses while the latest refute citing the gated receipt claims `tier: T1` or no tier (R:SELFREFUTE); at `plan` the same state is a notice on the gate's success line, promoted or dropped on the count; the tier stays a claim the engine holds and never judges
why: `_refute_of` reads presence and outcome only, so a payment task's builder can refute its own green and pass a human floor today — the tier ladder verify.md states (T1 a prelude, never the rung's answer) is prose the gate never reads (L3)
beat: done · next: add status

## RULES
<must>
- M1 at computed floor `human` (`authority_for`), `gate PASS` on a rung-bound task refuses R:SELFREFUTE when the latest `act: refute` stamp citing the gated receipt carries `tier: T1` or no `tier:` key, naming the claim it read (`T1` or `no tier`) and the fix — a fresh session's `add refute <slug> --by "<name>" --tier T2 --held|--found`; a latest refute claiming `T2` or `T3` passes the rung; the rung reads the LATEST citing stamp, so a T1 prelude followed by a T2 read passes and a T2 read followed by a T1 re-read refuses (from: interview)
- M2 at computed floor `plan`, the same state is a NOTICE appended to the gate's success line — `notice: the refute of this receipt claims <T1|no tier> — a green read by its own builder; a human floor refuses this (R:SELFREFUTE)` — never a refusal (R:NOTICEASREFUSAL); at `process`, `quick` depth or the explore lane nothing is read (from: interview)
- M3 the tier is a CLAIM: `_refute_of` returns `(outcome, tier)` read from the stamp's `outcome:` and `tier:` keys and nothing else — never `by:`, `probes:`, the note, or who signed the gate; the engine holds the claim and `by:` beside it says whether it is true (R:TIERJUDGED) (from: interview)
- M4 evidence-class: `RISK-ACCEPTED` and `HARD-STOP` are never refused by R:SELFREFUTE, and R:UNREFUTED / R:REFUTED fire before it (a missing or refuted read is the earlier answer) (from: interview)
- M5 verify.md's tier ladder says a T1 read is refused at a human floor (R:SELFREFUTE) and noticed at plan; FORMAT §8.4 says the gate reads `tier:` at floor human; the skill surface stays line-neutral vs HEAD and the three trees identical (from: interview)
</must>
<reject>
- R:SELFREFUTE a human-floor PASS whose latest refute claims T1 or no tier -> "SELFREFUTE"
- R:TIERJUDGED the engine deciding whether a tier claim is true — comparing `by:` to the builder, counting probes, reading the note -> "TIERJUDGED"
- R:NOTICEASREFUSAL the plan floor refusing on the tier — the promotion is a count's decision, not this task's -> "NOTICEASREFUSAL"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · the request does not say who may claim T2; taking anyone — the engine records `--tier` as a claim beside `--by`, exactly as `--authority` is recorded against the floor; a false claim is a lie in the record with a name on it, which is the notary's whole stance -> cost if wrong: a builder claims T2 on its own read and passes; `by:` names it, and the close review counts it
- A2 [which] covers: S1 S2 · the request does not say which refute stamp is read; taking the LATEST stamp citing the gated receipt, as `_refute_of` already does for outcome — one reader, one answer -> cost if wrong: a T2 read followed by the builder's own T1 re-read refuses until a fresh session reads again, which is the honest order · probe: T2 then T1 refuses; T1 then T2 passes
- A3 [when] covers: S1 S2 · the request does not say whether a pre-3.7 stamp (no `tier:` key) is T1; taking "no tier" as refused at human — a claim nobody made is not independence, and FORMAT §8.4 already says tier is never defaulted -> cost if wrong: a human-floor task gated after 3.7 on a tier-less 3.6 refute must be re-read by a fresh session, once
- A4 [absent] covers: S2 · the request does not say what the notice says when the plan floor has no refute at all; taking nothing — R:UNREFUTED already refused before the notice could run -> cost if wrong: none
- A5 [order] covers: S1 S2 · the request does not say where the rung sits; taking it inside the refute rung, after R:UNREFUTED and R:REFUTED and before the floor and stale-needs rungs, so a green nobody read is named before a green the builder read -> cost if wrong: a CI diff churns
- A6 [experience] covers: S1 S2 S3 · the request does not say who reads the refusal; the reader is the builder who just refuted their own green at 2am; hard for them is a refusal that says "independence" and not what to do — taking the refusal to name the claim it read and the exact fresh-session command, and the notice to say which floor would refuse it -> cost if wrong: the builder re-runs its own refute with `--tier T2` typed in, which A1 records with their name on it
- A7 [which] covers: S3 · the request does not say which stamp keys `_refute_of` may read; taking `outcome:` and `tier:` and nothing else — never `by:`, `probes:`, the note or who signed the gate — because any of those would make the engine judge a claim it cannot verify (R:TIERJUDGED) -> cost if wrong: a builder who types `--tier T2` on its own read passes; `by:` names them and the close review counts it
- A8 [when] covers: S3 · the request does not say when the tier is read; taking the gate, on the LATEST refute citing the gated receipt, at the moment PASS is recorded — never at `refute` time, which would refuse a T1 prelude the ladder explicitly allows -> cost if wrong: a T1 prelude followed by a T2 read passes, which is the order verify.md prescribes
- A9 [absent] covers: S1 · the request does not say what a refute with no `tier:` key means at a human floor; taking it as REFUSED — a claim nobody made is not independence, and FORMAT §8.4 already says the tier is never defaulted (interviewed 2026-09-13) -> cost if wrong: a human-floor task gated on a tier-less 3.6 refute is re-read once by a fresh session
- A10 [absent] covers: S3 · the request does not say what `_refute_of` returns when no refute cites the receipt at all; taking `(None, None)` so R:UNREFUTED answers first and R:SELFREFUTE never fires on a green nobody read -> cost if wrong: none; the earlier rung names the earlier gap
- A11 [order] covers: S3 · the request does not say where the tier read sits among the gate's rungs; taking it INSIDE the refute rung, after R:UNREFUTED and R:REFUTED and before the floor and stale-needs rungs, so a green nobody read is named before a green the builder read -> cost if wrong: a CI diff churns

## PLAN
contract: `_refute_of(stamps, receipt_cid) -> (outcome, tier)` · gate's refute rung gains the tier read at floor human (refuse) and plan (notice) · `_next_verb` unchanged · verify.md sentence · FORMAT §8.4 sentence
strategy: the computed floor is `authority_for(graph, cid)` as the freeze reads it; the notice rides the existing gate success `note` the way freshness does; four twins, both pins, three skill trees line-neutral
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/skill/add add-method/src/add_method/_bundled/skill/add .claude/skills/add add-method/tests/skill add-method/FORMAT.md
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change on the gate (method.md bind)
- O1 covers: M1, M2 · signal count of gate PASS refused R:SELFREFUTE per week · window 7d · threshold > 0 sustained 2 weeks · action alert
port: `add.gate` on the rung fixture at security (human) and data (plan) floors — `SENSITIVITY_FLOOR` maps security alone to human

## EDGES
- E1 Given a security-sensitivity task (floor human), gated receipt, latest refute `--tier T1 --held` · When `gate PASS` · Then R:SELFREFUTE naming `T1` and `--tier T2`; given the refute carries no tier · Then R:SELFREFUTE naming `no tier`
- E2 Given the same task, refute `--tier T2 --held` (and again `T3`) · When `gate PASS` · Then recorded
- E3 Given T1 then T2 · Then PASS; given T2 then T1 · Then R:SELFREFUTE (the latest citing stamp)
- E4 Given a data task (floor plan) with a T1 refute · When `gate PASS` · Then recorded, and the success note carries `notice:` naming `T1` and `R:SELFREFUTE`; with T2 · Then no notice
- E5 Given the human-floor task with a T1 refute · When `gate RISK-ACCEPTED --reason …` · Then recorded; given no refute at all · Then R:UNREFUTED, not R:SELFREFUTE
- E6 Given a quick-depth security task with a T1 refute · When `gate PASS` · Then recorded with no notice

## CHECKS
- test_human_floor_refuses_a_t1_or_tierless_refute · covers: M1, R:SELFREFUTE, A3, E1 · acceptance · both refusals name the claim and the fresh-session fix
- test_human_floor_passes_t2_and_t3 · covers: M1, E2 · acceptance · both recorded
- test_latest_citing_stamp_decides · covers: M1, A2, E3 · acceptance · T1→T2 passes, T2→T1 refuses
- test_plan_floor_notices_never_refuses · covers: M2, R:NOTICEASREFUSAL, E4 · acceptance · recorded with the notice; T2 draws none
- test_rung_is_evidence_class_and_ordered · covers: M4, A5, E5 · acceptance · RISK-ACCEPTED lands; no refute is R:UNREFUTED first
- test_exempt_rungs_read_nothing · covers: M2, E6 · acceptance · quick depth at security floor gates PASS with no notice
- test_refute_of_returns_the_claim_and_judges_nothing · covers: M3, R:TIERJUDGED · acceptance · `(outcome, tier)` from the keys; `by:` and `probes:` change nothing
- test_verify_md_and_format_state_it · covers: M5 · static · verify.md names R:SELFREFUTE at human and the notice at plan; FORMAT §8.4 names the gate's read; trees identical; line-neutral
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/refute-tier-floor.d/runs/9.md · kind: test-ids · 11/11 reported · exit 0 · 2026-09-13
refute: held · 9 probe(s) · tier T2 · by advisor:gate-security-reviewer · against /tasks/refute-tier-floor.d/runs/9.md · 2026-09-13 · changed: security lens re-review: CLEAR TO GATE. The allowlist closes the fail-open class (25-value matrix; the two laundering values I found, tier: 'T1 ' and [T1], now refuse), introduces nothing new (live add.py diffed against an INDEPENDENT pristine pre-fix baseline held since the first sitting — the check M60/M62 demand — plus four twins byte-identical and ENGINE_MD5 matching), and closes the AST residue BEYOND spec: both the variable-key and the helper-call evasions now fail, which the structural guard alone never could.
gate: PASS · authority human · by human:Tin Dang · receipt /tasks/refute-tier-floor.d/runs/9.md · 2026-09-13

## LESSONS
- [method · M64 · open] a fix made to close a finding is itself unreviewed until someone reads it. On refute-tier-floor three consecutive reads each found a defect introduced by the fix that closed the previous one: the allowlist fix drifted M2's quoted notice; the decorrelation fix landed only on the human fixture and left the plan floor readable by `by:`; the typo fix split `recorded as handed` across a newline and turned another task's guard red. None was a behaviour bug and none was caught by the checks written alongside the fix. The cheap counter is to re-run the PREVIOUS finding's mutant plus the new one after every fix, and to ask what the fix's own blast radius is — not just whether the reported defect is gone. (evidence: /tasks/refute-tier-floor.d/runs/ — refutes on runs 1, 7 and 9)
- [method · M63 · open] the literal a frozen Must QUOTES is part of the contract, and an `in` assertion does not bind it. M2 of refute-tier-floor states the plan-floor notice verbatim; a later fix threaded a new clause through that string and `test_plan_floor_notices_never_refuses` — asserting only the substrings notice:/T1/R:SELFREFUTE — stayed green, so the build drifted off a frozen Must invisibly. Where a Must quotes a string, assert the string. And know which half is free: M1 never quotes its refusal, so the refusal may say more; M2 does, so the notice may not. Residual, named by the read that found it: even the literal is asserted with `in`, so text APPENDED after it is still not caught — line equality would close that. (evidence: /tasks/refute-tier-floor.d/runs/7.md — T2 refute, FOUND; runs/9.md — HELD, 14 probes, six mutants each killed by a different assertion)
- [method · M59 · open] an unreadable `tier:` on a refute stamp fails OPEN at a human floor: the gate refuses only exact `T1` or an absent key, so a hand-edited `T4`, `t2`, `T0`, `0`, `[T2]` or `null` all pass as independent. Twelve hundred lines up in the same file `sensitivity_floor` states the opposite law — an unreadable declaration is one the engine cannot honour, so it floors UP (R:SILENT_FLOOR). One fact, two readers, opposite directions. Reachable only by hand-edit (`refute` validates against REFUTE_TIERS and is the sole writer of act: refute), and A1/A7 already accept the tier as an unverified claim — so this is honesty-of-record, not privilege escalation. Closing it widens M1, which names T1-and-absent only, so it needs a human refreeze: raise it at the milestone seam. (evidence: /tasks/refute-tier-floor.d/runs/1.md — T2 refute, HELD, 10 probes)
