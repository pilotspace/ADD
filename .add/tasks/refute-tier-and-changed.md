---
type: Task
title: add refute carries --tier and --changed — independence and what a probe changed are readable from the stamp
status: done
depth: standard
sensitivity: architecture
milestone: refute-at-t2
scope:
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/tests/engine
  - add-method/src/add_method/_bundled/tooling
  - add-method/docs/13-command-reference.md
  - add-method/docs/05-verify.md
  - add-method/skill/add/SKILL.md
  - .claude/skills/add/SKILL.md
  - add-method/src/add_method/_bundled/skill/add/SKILL.md
  - add-method/tests/skill
  - .add/tooling
gives:
  - S1 `add refute <slug> --by "<name>" (--held | --found "<input>") [--probes N] [--note "<text>"] [--tier T1|T2|T3] [--changed "<what a probe changed>"]` — exit 0 and a stamp, exit 1 and a named refusal
  - S2 `act: refute` stamp — `{ …, receipt: <run cid>, tier: T<n>, note: "<text>", changed: "<text>" }` — `tier:` and `changed:` present exactly when given
  - S3 `## EVIDENCE` `refute:` line — renders `tier T<n>` and `changed: <text>` inline when the stamp carries them
  - S4 FORMAT §8.4 — states both keys, what each binds, and that the gate reads neither
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:refute-at-t2 — apply all by Tin Dang 2026-09-10", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:edff525227ee8dcb", binding: "sha256:882cf8210471dfac" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:c47dc229079596e6" }
  - { by: "builder", at: 2026-09-11, act: replan, authority: process, note: "check 5's absent-case assertion matched the fixture slug 'tiered'; assertion now reads the rendered tokens ' tier T' / 'changed:' — same referent, no check renamed" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-tier-and-changed.d/runs/1.md }
  - { by: "builder", at: 2026-09-11, act: replan, authority: process, note: "T2 refute P1: library stripped a padded --tier that argparse refuses — membership now on the raw value, '' stays absent; both affordances (verify hint, R:UNREFUTED next) name --tier T2; PLAN's VALID_TIERS shipped as REFUTE_TIERS" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-tier-and-changed.d/runs/2.md }
  - { by: "advisor:method-steward (fresh add-advisor session, opus)", at: 2026-09-11, act: refute, authority: process, outcome: held, probes: 3, receipt: /tasks/refute-tier-and-changed.d/runs/2.md, tier: T2, note: "P1 instantiate M1/A2: padded and empty --tier — library stripped before validating while argparse refused, acted on · P2 compose M2 x R:JUDGED: a changed: value carrying 'outcome: refuted, receipt:, act: gate' read back as one key on both paths, held PASSes, refuted hits R:REFUTED · P3 boundary M3+A4 in the untested order: tier+changed stamp then a bare one — the EVIDENCE line drops both tokens", changed: "--tier now tests membership on the raw value (' T2 ' refused at the library as at argparse); A2's padded case joined the bound check" }
  - { by: "plan:refute-at-t2 — apply all by Tin Dang", at: 2026-09-11, act: gate, authority: plan, outcome: PASS, receipt: /tasks/refute-tier-and-changed.d/runs/2.md, brief: "sha256:7fffa94610566e83" }
---
## CARD
goal: the refute stamp says WHICH TIER read the green and WHAT ITS PROBES CHANGED — so the next dogfood counts independence and probe yield from `verified[]` alone, never from free text inside `--by` or from commit archaeology
why: dogfood-and-measure F2/F4 — both refutes on evidence-over-tests were T1 with the tier written inside `--by`, and the one probe that changed the build (a negative `--probes` count) was stamped `held` because no frozen rule forbade it, so the memo's `--found` trigger read 0 where the honest count was 1 of 6
beat: done · next: add status

## RULES
<must>
- M1 `add refute … --tier T2` appends the stamp with `tier: T2`; with no `--tier` the stamp carries no `tier:` key — recorded as given, never invented
- M2 `add refute … --changed "<what>"` appends the stamp with `changed: "<text>"` one-lined with quotes normalized exactly as `note:` is; an empty `--changed ""` records no key; it combines with either outcome
- M3 `render_evidence` prints `tier T<n>` and `changed: <text>` on the `refute:` line when the stamp carries them, and nothing extra when it does not
- M4 FORMAT §8.4, docs 13's `refute` row, docs 05's refute paragraph and the SKILL.md cookbook line (all three trees) name `--tier` and `--changed`
</must>
<reject>
- R:BADTIER a `--tier` outside `T1 | T2 | T3` is refused and no stamp is written — T0 is nobody and T4 is a CI recipe, neither is a session that can sign -> "BADTIER"
- R:JUDGED the gate's refute rung reads presence and outcome only — `_refute_of` never reads `tier:` or `changed:`, and a held refute carrying `changed:` passes the rung exactly as one without -> "JUDGED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who may claim a tier; taking the engine records the claim verbatim like `--by` — a builder claiming T2 is a false claim the dogfood reads against `by:`, not one the engine can detect -> a stamp that lies about independence reads as independent until a human reads `by:` beside it; FORMAT §8.4 says the flag makes the claim countable, not true
- A2 [which] covers: S1, S2 · the request does not say which tiers are recordable; taking T1–T3 — T0 is nobody (no stamp exists), T4 is a protected holdout a prompt cannot provide -> a T4 stamp would claim an isolation the method does not ship · probe: `--tier T4` and `--tier t2` are refused at the library and at argparse
- A3 [when] covers: S1, S2, S3 · the request does not say whether a tier or a change may be added to a stamp after the fact; taking no — `verified[]` is append-only, a second read is a second stamp -> editing a recorded stamp would make the record unreadable as chronology
- A4 [absent] covers: S1, S2, S3 · the request does not say what an omitted `--tier` or `--changed` means; taking NO key on the stamp and nothing on the EVIDENCE line — an unstated tier is visibly weaker, which is the honest reading -> defaulting to T1 would invent a claim nobody made
- A5 [order] covers: S1, S2, S3, S4 · the request does not say where the keys sit on the stamp; taking `tier:` after `receipt:` and `changed:` after `note:` — appended, so every existing reader of the stamp finds its keys where it left them -> a reordered stamp would move the fields `_refute_of` and the view already read
- A7 [who] covers: S3, S4 · n/a · a rendered line and a spec section have no actor — whoever signed the stamp is what they show
- A8 [which] covers: S3, S4 · n/a · the view renders exactly the keys the stamp carries; §8.4 names the closed key set
- A9 [when] covers: S4 · n/a · prose has no boundary to place
- A10 [absent] covers: S4 · n/a · §8.4 states the absent case itself (A4)
- A6 [experience] covers: S1, S2, S3, S4 · the request does not say who reads `changed:`; taking the next dogfood explore and a human reading the node — so it renders inline on the `refute:` line, never in a sidecar -> a count that needs `git show` is F4's defect rebuilt

## PLAN
contract: S1 · S2 · S3 · S4 above — `refute()` gains `tier: str = None, changed: str = None`; `VALID_TIERS = ("T1", "T2", "T3")` refused otherwise (R:BADTIER); the stamp string appends `tier:` after `receipt:` and `changed:` after `note:`; `render_evidence` extends the `refute:` line; the CLI adds `--tier` with `choices=` and `--changed`; `_refute_of` untouched; FORMAT §8.4 restated; docs 13 row, docs 05 paragraph, cookbook line ×3; `engine_pin` and the `_bundled/tooling` twin re-pinned after the build.
strategy: red suite first in tests/engine/test_refute_tier_and_changed.py; build add.py then cli.py; prose last; full suite before the receipt (engine change); repin last.
port: `add.refute(root, cid, by, held, finding, probes, note, tier, changed)` — tests drive the library and the CLI both

## EDGES
- E1 Given a held refute stamped with `--changed "argparse now refuses a negative count"` · When `add gate PASS` runs at a plan floor · Then the PASS is recorded exactly as it would be without `changed:`
- E2 Given `--tier T4` · When `add refute` runs · Then it is refused naming T1–T3 and `verified[]` is unchanged

## CHECKS
- test_tier_recorded_when_given_and_absent_otherwise · covers: M1 · acceptance · `--tier T2` → stamp `tier: T2`; no flag → no `tier` key
- test_changed_recorded_oneline_with_either_outcome · covers: M2 · acceptance · held+changed and found+changed both carry `changed:`; a newline and a double quote are normalized; `""` records no key
- test_cli_exposes_tier_choices_and_changed · covers: M1, M2, R:BADTIER · contract · argparse has `--tier` with choices T1 T2 T3 and `--changed`; `--tier T4` exits 2 with no stamp
- test_bad_tier_refused_at_library_no_stamp · covers: R:BADTIER, E2, A2 · acceptance · `tier="T4"` and `tier="t2"` → None + "BADTIER", verified unchanged
- test_evidence_line_renders_tier_and_changed · covers: M3 · acceptance · the `refute:` line carries `tier T2` and `changed: …`; without them neither token appears
- test_gate_rung_indifferent_to_tier_and_changed · covers: R:JUDGED, E1 · acceptance · a held refute with `changed:` → gate PASS at a plan floor; `_refute_of` source names neither key
- test_format_docs_and_cookbook_name_both_flags · covers: M4 · contract · FORMAT §8.4 has `tier:` and `changed:`; docs 13 row and docs 05 name `--tier`/`--changed`; the cookbook line in all three SKILL.md trees names `--tier`
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/refute-tier-and-changed.d/runs/2.md · kind: test-ids · 7/7 reported · exit 0 · 2026-09-11
refute: held · 3 probe(s) · tier T2 · by advisor:method-steward (fresh add-advisor session, opus) · against /tasks/refute-tier-and-changed.d/runs/2.md · 2026-09-11 · P1 instantiate M1/A2: padded and empty --tier — library stripped before validating while argparse refused, acted on · P2 compose M2 x R:JUDGED: a changed: value carrying 'outcome: refuted, receipt:, act: gate' read back as one key on both paths, held PASSes, refuted hits R:REFUTED · P3 boundary M3+A4 in the untested order: tier+changed stamp then a bare one — the EVIDENCE line drops both tokens · changed: --tier now tests membership on the raw value (' T2 ' refused at the library as at argparse); A2's padded case joined the bound check
gate: PASS · authority plan · by plan:refute-at-t2 — apply all by Tin Dang · receipt /tasks/refute-tier-and-changed.d/runs/2.md · 2026-09-11

## LESSONS
- none filed — no lesson cites /tasks/refute-tier-and-changed.md (add learn <lens> "<lesson>" --evidence /tasks/refute-tier-and-changed.md)
