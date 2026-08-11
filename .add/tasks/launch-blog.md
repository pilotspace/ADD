---
type: Task
title: the v3.0.0 launch post — written now, published at the final tag
status: done
milestone: v3-final-collateral
depth: doc
scope:
  - blog/introducing-add-30.md
  - add-method/tests/book/test_launch_blog.py
gives:
  - S1 `blog/introducing-add-30.md` — the launch post for normal users, held for the final tag
  - S2 `tests/book/test_launch_blog.py` — the claims oracle pinning the post's numbers to the committed records
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "human:tindang", at: 2026-08-11, act: freeze, authority: process, direction: "sha256:feda9a1dc2b4e456" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:f096e60f2b4c22a3" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/launch-blog.d/runs/1.md }
  - { by: "human:tindang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/launch-blog.d/runs/1.md, brief: "sha256:f096e60f2b4c22a3" }
---
## CARD
goal: a launch post a normal user can act on — what ADD is, what 3.0 changes, the honest numbers, a ten-minute start — with every measured claim pinned to a committed record
why: announcement is held for the final tag by decision; writing it now inside the loop means the claims are test-bound before anyone can quote them, and the cheat post stays frozen as the beta-era evidence trail it links to
beat: done · next: add status
## RULES
<must>
- M1 every measured number in the post traces to a committed record — the homogeneous campaign (safe rate, n, cost) to CAMPAIGN-amb1-beta2.md, artifact sizes to the ledger's figures
- M2 the post links the cheat post as its evidence trail and repeats the release claim verbatim: auditability, not correctness
- M3 both install commands (npx and pip) appear exactly as shipped, and no verb or feature is named that the CLI does not wire
</must>
<reject>
- R:QUOTEDRIFT a stat in the post that disagrees with the committed record it came from -> "QUOTEDRIFT"
</reject>
## ASSUMPTIONS
- A1 [who] covers: S1,S2 · the request does not say who the reader is; taking "a developer who has never seen ADD — no 2.5 knowledge assumed; the cheat post carries the adversarial depth" -> cost if wrong: the post re-explains what its audience already knows
- A2 [which] covers: S1,S2 · the request does not say which numbers are in; taking "the homogeneous beta.2 campaign only (5/7 every rep, n=3, $3.00 mean) — pooled five-engine numbers stay in the cheat post with their caveat" -> cost if wrong: a quotable stat carries a silent heterogeneity caveat · probe: the campaign stats in the post match CAMPAIGN-amb1-beta2.md
- A3 [when] covers: S1,S2 · the request does not say the publication moment; taking "written and committed now, published at the final tag — the file carries no date in its name and a hold note in its meta comment" -> cost if wrong: an early leak reads as an announcement
- A4 [absent] covers: S1,S2 · the request does not say what version the post names; taking "v3.0.0 with the final-tag caveat in the hold note — the claims are all beta.2-true and survive the tag unchanged" -> cost if wrong: a stale version string at publication
- A5 [order] covers: S1,S2 · the request does not say the narrative order; taking "problem -> what ADD is -> what 3.0 enforces -> honest numbers -> what it does not claim -> ten-minute start" -> cost if wrong: cosmetic only
## PLAN
contract: one markdown post plus one pytest module reading both the post and the committed campaign record
scope: blog/introducing-add-30.md · add-method/tests/book/test_launch_blog.py
## EDGES
- E1 the campaign record is regenerated with different numbers — the oracle reads the RECORD, so the post reds instead of drifting
## CHECKS
- test_campaign_stats_match_the_committed_record · covers: M1,A2,R:QUOTEDRIFT,E1 · safe rate, n and cost in the post equal CAMPAIGN-amb1-beta2.md
- test_post_links_the_evidence_trail · covers: M2 · the cheat post is linked and the auditability claim is verbatim
- test_install_commands_are_the_shipped_ones · covers: M3 · npx @pilotspace/add init and pip install pilotspace-add both present
- test_post_names_no_unwired_verb · covers: M3 · every `add <verb>` in the post is in cli.build_parser()
red-first: every check MUST fail first.
## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>
## LESSONS
- <lesson> -> add learn <lens>
