---
type: Milestone
title: The loop closes — every handoff leaves an object the next beat reads
status: direction
generated: { by: add/3.6.0, at: 2026-09-11 }
verified:
  - { by: "Tin Dang", at: 2026-09-11, act: freeze, authority: plan, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
  - { by: "process:check", at: 2026-09-13, act: check, authority: process, via: process, boxes: "EXIT:1,2,3,4,5,6,7,8,10" }
  - { by: "process:check", at: 2026-09-13, act: check, authority: process, via: process, boxes: "EXIT:11" }
advised_by: method-steward
---
## CARD
goal: Every handoff in the closed-loop continuum (rules → checks → build → verified source → released tree → observation → prevention → successor) leaves an object the engine reads, and no shipped sentence promises a behaviour the engine lacks
why: 3.6 closed the drain (R:UNDRAINED). A rung-by-rung read of the engine against the closed-loop research (design page, 2026-09-11) found seven open seams, all mechanical, and three of them already CLAIMED in shipped prose: "dependents that need: it are flagged stale" (four files, no reader, a §3.5 FORMAT never wrote), "the regression floor" (one direction.md bullet, no slot, no reader), and a refute rung that a builder's own T1 read satisfies at a human floor. A receipt records blobs but no commit, so nothing can say which tree a tag shipped; an escaped defect drains as a sentence; a task in a closed milestone is reopened by hand. Each is a handoff where evidence is lost while the loop still reads valid.
next: add freeze receipt-anchored-to-head

## SCOPE
In:  Ten tasks and two explores, sequential (the engine is one file and its twins forbid parallel writes), in
     this order: receipt-anchored-to-head → regression-floor → consumers-go-stale → release-stamp →
     escape-with-prevention → successor-not-reopen → refute-tier-floor → must-carries-source →
     quick-lane-tripwire → observes-slot; residue-by-kind rides DIRECT (router column + verify.md);
     explores holdout-that-holds and method-health answer the two questions this milestone will not build on a guess.
     Every new refusal arms at the refute rung's arming (standard|deep × computed floor plan|human) or higher.
     One new verb (`add release`), one new FORMAT section (§3.5), zero new node types.
Out: No fourth beat, no second human approval, no deployment credential or outward act in the engine, no
     Release node type (a release is a stamp on the Milestone), no universal verifier (quick · process · explore
     never pay), no promotion of the two-mode notice to a refusal (the dogfood count decides), no trajectory
     check mode (the domains milestone owns the recipes), no T4 mechanism before its explore answers.

## GROUND
touches: add-method/tooling/add.py (run:3728 · scope_digest:3624 · fresh:3669 · freeze:2222 · gate:6112 ·
  _refute_of:3201 · reopen:2478 · learn:4050 · fold:4271 · doctor:6613 · interview:5055 · new:2097) and its
  bundled twin · add-method/tooling/cli.py + twin · add-method/tooling/engine_pin.py · add-method/FORMAT.md
  (§3.5 new, §8.1, §8.4) · the three skill trees (phases/direction.md · verify.md · build.md · intake.md ·
  loop.md · deltas.md) · add-method/docs/05, 06, 16, appendix-c, appendix-d · add-method/tests/engine ·
  add-method/tests/skill
risks:
  - SKILL.md sits at its 176-line / 13,258-byte pin: every skill sentence a task adds is funded by compressing one, or lands in a phase file the router loads on demand.
  - An engine task ripples into the twins, engine_pin.py and the verb registries; the full suite runs before each engine receipt (method.md bind) — a targeted receipt alone is how 3.2 shipped a red host.
  - Two tasks are security-floored (refute-tier-floor · quick-lane-tripwire): their freeze is interviewed and human, never plan-authority under the standing go-ahead.
  - A new key on a receipt must stay out of the T0 scan cost argument (FORMAT §4): scalars only; anything per-file joins the deferred payload.

## EXIT
- [x] a receipt written inside git carries head: and committed:, and one written outside git carries neither and says why   (← receipt-anchored-to-head)
- [x] a rung-bound task cannot freeze without a regression: line, and cannot PASS while a declared full|affected floor has no fresh exit-0 floor receipt   (← regression-floor)
- [x] a refreeze that moves a gives: surfaces every consumer as needs_stale in doctor and todo, that consumer's gate refuses PASS until it re-crosses, FORMAT §3.5 exists, and every "flagged stale" sentence is driven by a check   (← consumers-go-stale)
- [x] add release refuses a tag whose tree lacks a gated receipt's blob, records artifact and build as handed, and status --all / show render the stamp   (← release-stamp)
- [x] an escape cannot be filed without why-missed and prevention, and cannot fold while its prevention does not resolve; loop.md names the three observation outcomes   (← escape-with-prevention)
- [x] reopen refuses a task in a done or archived milestone and names --supersedes; new --supersedes writes the edge and show walks it   (← successor-not-reopen)
- [x] a human-floor PASS refuses a self-refute, and a plan-floor gate notices one   (← refute-tier-floor)
- [x] at a human floor every unsourced Must is put to the human at interview; elsewhere freeze notices them by id   (← must-carries-source)
- [ ] a quick: learn citing a commit that touched a sensitive path or an open task's scope is refused by name   (← quick-lane-tripwire)
- [x] observes: lines render in brief and show and a human-floor task with none is noticed at freeze; the router carries residue by kind   (← observes-slot · direct: residue-by-kind)
- [x] both explores gate on cited FINDINGS, and the close review carries the counts (floor receipts · consumers flagged · self-refutes refused · quick refusals) that decide which notices are promoted   (← holdout-that-holds · method-health)

## CLOSE
evidence: one row per task — status · gate verdict · gate authority · who signed · refutes that FOUND

- consumers-go-stale        done     PASS           plan     plan:loop-that-closes    9 found
- escape-with-prevention    done     PASS           process  plan:loop-that-closes    25 found
- holdout-that-holds        done     RISK-ACCEPTED  process  plan:loop-that-closes    0 found
- method-health             done     RISK-ACCEPTED  process  plan:loop-that-closes    1 found
- must-carries-source       done     PASS           plan     plan:loop-that-closes    5 found
- observes-slot             done     PASS           process  plan:loop-that-closes    0 found
- quick-lane-tripwire       direction —              —        —                        8 found
- receipt-anchored-to-head  done     PASS           process  plan:loop-that-closes    0 found
- refute-tier-floor         done     PASS           human    human:Tin Dang           1 found
- regression-floor          done     PASS           plan     plan:loop-that-closes    1 found
- release-stamp             done     PASS           plan     plan:loop-that-closes    3 found
- successor-not-reopen      done     PASS           process  plan:loop-that-closes    0 found

counts the promotion rule reads (method-health F1/F3, judged at that node's gate):
- floor receipts ........ 90 receipts carry `floor: regression`, 10 of them `exit: 1` — a red floor
                          receipt followed by a green one before the gate IS the floor catching the
                          host. DERIVABLE, 0 bytes.
- consumers flagged ..... 0, and 0 BY CONSTRUCTION, not by health: every `needs:`-bearing task froze
                          before the pin shipped, so no freeze stamp carries a `needs:` digest. This
                          number must NOT be read as evidence the rung is unused.
- self-refutes refused .. UNKNOWN. Not derivable: a refusal writes nothing (law 3), and the human-floor
                          refusal leaves no trace. The plan-floor NOTICE is derivable and stands at 1
                          of 5 gated rung-bound tasks (must-carries-source, whose gate cites a T1).
- quick refusals ........ UNKNOWN. Not derivable, and the denominator is empty too: `learn` writes only
                          on acceptance, and this milestone accepted 0 `quick:` lessons.

promotion verdict: the frozen rule (FORMAT §6.2, "the count is what decides") names no threshold and no
direction, so as written it is not decidable by any count — 0-of-6 compliance argues equally for promote
(prose binds nothing) and drop (nobody pays for it). method-health F3 recommends deciding on
COMPLIANCE-AT-CLOSE, which costs 0 bytes and anyone can recompute, and recording the refusal-count half
as unknown until a record exists. Compliance measured now: two-mode 0 of 6 rung-bound tasks; 
must-carries-source 0 of 4 plan-floor (2 of 2 human-floor, but the interview forces it there, so that
pair measures the interview and not the notice); observes-slot 2 of 2 human-floor, 0 of 8 elsewhere
where the notice does not arm. NO notice is promoted to a refusal in 3.7 — the milestone's own SCOPE
Out line said the count would decide, and the count says it cannot yet.

