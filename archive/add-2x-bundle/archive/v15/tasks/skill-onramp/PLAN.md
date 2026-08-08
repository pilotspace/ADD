# TASK: Protocol-walk proof: /add drives fresh install to gated task, zero typed commands

slug: skill-onramp · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a protocol-walk test executes the /add journey literally — fresh
  install → init → lock → first task → gate PASS — issuing every add.py call
  ITSELF from the installed tree, with the commands sourced from the skill's
  own prose; plus the one prose gap that still tells the HUMAN to type a
  command is closed: the lock is executed by the AGENT on the human's
  recorded chat confirmation (v15 exit criterion 3)
Gaps from the v15 research, adjudicated here:
  - CLOSED (this task): gap 1 — 0-setup.md §4 says "They sign once:
    `python3 … lock --by`", instructing the human to TYPE; the human's
    decision stays the seam, but the agent should run the command on their
    recorded word (typing it stays the escape hatch). Gap 6 — no
    protocol-walk test exists for the full journey (test_v8_onramp's own
    HONEST SCOPE note: words-exist ≠ method-works).
  - DEFERRED (recorded for observe; engine is feature-frozen this milestone
    per MILESTONE Out, and add.py's md5 is pinned by four shipped suites):
    gaps 2–4 — engine-PRINTED hints (brownfield closing line, status
    new-task escape hatch, unlocked-status lock hint) still address the
    terminal reader; rewording them is an engine edit → a deliberate
    change-request-sized follow-up. Gap 5 — a machine-readable protocol for
    "the human confirmed in chat" is a method-design question, not prose.
Framings weighed: prose-fix + protocol-walk (chosen: closes the only
  zero-command gap reachable without touching the frozen engine, and pins
  the whole journey behaviorally) · close ALL six gaps (rejected: gaps 2–4
  re-open the engine this milestone froze and would re-aim four shipped md5
  pins — a follow-up milestone decision) · walk-test only (rejected: the
  walk would pin a journey whose own guide still tells the human to type)
Must:
  - test_skill_onramp.py walks the journey end-to-end from a tmp install
    (canonical skill tree + tooling copied as the installers lay them down):
    status (no project, fails) → init parsed FROM 0-setup.md §1's fence
    (placeholders substituted) → status shows the unlocked window → lock
    parsed FROM 0-setup.md §4's fence (--by substituted) → new-task →
    advance ×5 → gate PASS → state reads done/PASS. Every command issued by
    the walker; ZERO pre-seeded state.
  - The walk runs the INSTALLED add.py (tmp/.add/tooling/add.py), not the
    repo's — proving the shipped surface drives the loop.
  - 0-setup.md §4 reworded: the human confirms the lock-down in
    conversation; YOU (the agent) run `add.py lock --by "<name>"` with
    their name on that recorded confirmation; typing the command themselves
    stays the escape hatch. Lock semantics, layers, judgment-free note —
    unchanged.
  - 0-setup.md ships ×3 (canonical · dogfood · _bundled) byte-identical;
    the cospecify anchors in it stay (four lenses · co-specify-at-foundation
    · flag grammar · phases/1-specify.md pointer).
  - ENGINE untouched: add.py byte-identical ×3 (md5 ccb0aa1589c09d3238d7e7fbca1e0240).
Reject:
  - the walk pre-seeds state.json or skips the lock -> the test is vacuous;
    walk asserts the pre-lock refusal window exists (status names the lock)
  - prose tells the human to TYPE as the primary path -> test_lock_step red
  - engine edits -> md5 pins red (four shipped suites + this one)
Assumptions — least-sure first:
  ⚠ [test] the parsed-from-prose init fence substitutes cleanly — least sure
    because §1's fence carries TWO placeholders (`<inferred from repo/dir>`
    and `<prototype|poc|mvp|production>`) whose exact spelling the regex
    must survive; if wrong: the walk errors at arrange (not a false green)
    and the regex is fixed against the real fence text — cost: one
    test-harness iteration, no contract change
  ⚠ [spec] rewording §4 keeps the v12 lock SEMANTICS readable — least sure
    because §4 is the lock-down's only guide; if the reword muddies who
    DECIDES (always the human), the seam itself erodes; mitigation: the
    sentence structure keeps "the human confirms" before "you run", and the
    escape hatch keeps their hands on the wheel — reviewed at this freeze
  - [x] no test pins §4's current wording ("They sign once") — grepped;
    only engine lock BEHAVIOR is pinned (test_setup_lock, brownfield_scan)
  - [x] advance ×5 reaches verify from specify — golden-spine precedent

### CHANGE REQUEST → contract v2 (approved by Tin, 2026-06-05)
Trigger: the 3-lens adversarial verify found the SAME human-types-the-lock
gap in two companion guides the v15 research never swept (3× MAJOR), plus
an ambient-consent ambiguity in the new §4 sentence itself (2× MAJOR —
"recorded confirmation" undefined; §1 autonomous "you run" tone-bleed).
Scope added (per the close-gap-before-gate convention):
  - setup-review.md ×3: "they sign once:" → confirm-in-conversation +
    you-run; template `Sign:` row → "confirm in chat → the agent runs
    `add.py lock --by "<name>"` (typing it yourself works too)"
  - adopt.md ×3: brownfield gate "and signs:" → confirms-in-conversation +
    you-run (pinned `init --await-lock` entry untouched)
  - 0-setup.md §4 ×3 tightened: confirmation = an EXPLICIT YES to the
    lock-down itself; ambient mid-stream agreement is not a confirmation
  - 0-setup.md exit gate ×3: "Human signed `add.py lock`" → "Human
    confirmed the lock-down and `add.py lock --by` ran with their name"
Still deferred (unchanged): gaps 2–5 — the MACHINE-READABLE chat-confirm
protocol remains a method-design follow-up; v2 only closes the prose reading.
Test amendments (strengthening, disclosed, red-first): companion-guides
agent-run pins + ship-×3 parity; `_fence_command` verifies real fence
membership; §4 prose assertions run on the section BODY (heading excluded);
`explicit yes` pinned in test_lock_step_is_agent_run.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the installed tree drives the whole journey hands-free
  Given a tmp dir holding only what the installers lay down
  When the walker issues status, init (parsed from 0-setup §1), status,
       lock (parsed from 0-setup §4), new-task, advance ×5, gate PASS
  Then every step exits as the prose promises and the final state is
       done/PASS
  And no human-typed command was simulated — the walker IS the agent

Scenario: the pre-lock window is real, not narrated
  Given the walk after init --await-lock and before lock
  When status runs
  Then its output names the lock as the single next step

Scenario: the lock is agent-run on the human's word
  Given 0-setup.md §4
  When its prose is read
  Then it tells the AGENT to run lock --by with the human's name on their
       recorded chat confirmation
  And typing the command themselves remains the named escape hatch
  And the human-decides seam is untouched (they confirm; you execute)

Scenario: every shipped lock fence is agent-run (v2)
  Given setup-review.md and adopt.md — the two other guides carrying the
        lock fence
  When their prose is read
  Then neither tells the human to sign/type as the primary path; both say
       the human confirms and YOU run; the Sign: template row says
       confirm-in-chat; and §4's confirmation is an EXPLICIT YES (ambient
       agreement mid-stream is not a confirmation)

Scenario: the guide ships everywhere it is loaded
  Given the three 0-setup.md copies (and ×3 for both companion guides, v2)
  Then canonical, dogfood, and _bundled are byte-identical
  And the cospecify anchors in the file survive the reword

Scenario: nothing else moves
  Then add.py is byte-identical ×3 and no other skill file changes
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add-method/skill/add/phases/0-setup.md   §4 reword ONLY: human confirms in
                                         conversation -> the AGENT runs
                                         `add.py lock --by "<name>"` on that
                                         recorded word; self-typing = escape
                                         hatch; lock semantics/judgment-free
                                         note unchanged; synced ×3
.claude/skills/add/phases/0-setup.md     dogfood twin (byte-identical)
add-method/src/add_method/_bundled/skill/add/phases/0-setup.md  bundled twin
v2 (change request, Tin 2026-06-05 — verify-lens findings closed pre-gate):
add-method/skill/add/setup-review.md     "Where it ends" + `Sign:` template
                                         row → confirm-in-chat + agent-runs;
                                         synced ×3
add-method/skill/add/adopt.md            brownfield gate "and signs:" →
                                         confirms + you-run; synced ×3
0-setup.md §4                            + explicit-yes tightening (ambient
                                         agreement ≠ confirmation)
0-setup.md exit gate                     "Human signed" → "Human confirmed
                                         … and `lock --by` ran with their name"
DEFERRED (named, not contracted): engine-printed hints (gaps 2-4) + the
machine-readable chat-confirm protocol (gap 5) — engine is feature-frozen.
ENGINE UNTOUCHED: add.py byte-identical ×3 (md5 ccb0aa1589c09d3238d7e7fbca1e0240).
GUARD: add-method/tooling/test_skill_onramp.py — the protocol walk
(behavioral, installed-tree) · agent-run lock prose (§4 body + companion
guides) · escape hatch kept · explicit-yes pin · fence-membership check ·
3-tree parity (0-setup + companions) · engine pin.
```

Status: FROZEN @ v2 — approved by Tin, 2026-06-05 (v1: one-approval front, ⚠ flags
reviewed — fence-substitution already empirically retired by the green walk; §4
reword reviewed as the proposed diff, "they confirm" before "you run" + named
escape hatch. v2: change request closing the adversarial-verify findings before
the gate — see the §1 CHANGE REQUEST block).
<!-- Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must has a test; deferred gaps are observe deltas,
not tests.
Plan (one test per scenario, asserting behavior not internals):
  - test_protocol_walk_zero_typed_commands: the full journey from a tmp
    install, commands parsed from 0-setup.md fences, run against the
    INSTALLED add.py; asserts each step + final done/PASS (green-by-design
    behavioral pin — the v12 machinery exists; the JOURNEY was never pinned)
  - test_prelock_window_names_the_lock: mid-walk status output names lock
    (green-by-design pin of the v12-1 one-next-step behavior)
  - test_lock_step_is_agent_run: 0-setup.md §4 instructs the AGENT to run
    the lock on the human's recorded confirmation (RED: §4 says "They sign
    once" — the human types)
  - test_lock_escape_hatch_kept: §4 still names self-typing as the escape
    hatch (RED: no escape-hatch framing exists today)
  - test_three_tree_parity: 0-setup.md md5 ×3 + cospecify anchors survive
    (green-by-design guard)
  - test_engine_untouched: add.py md5 ccb0aa1589c09d3238d7e7fbca1e0240 ×3
    (green-by-design pin)

Tests live in: `add-method/tooling/test_skill_onramp.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the §4 reword NEVER moves the decision off
the human — "they confirm, you execute"; the lock-down's judgment-free note
and layer semantics are byte-kept; sync ×3 before the suite runs.
Code lives in: `add-method/skill/add/phases/0-setup.md` · `.claude/skills/add/phases/0-setup.md` · `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — onramp suite 9/9; full suite 457/457 (448 + 9 new);
  engine check 194/0 (4 pre-existing milestone-attach warnings); audit clean
- [x] coverage did not decrease — suite grew +9; the protocol walk pins a
  journey no prior test covered (test_v8_onramp's honest-scope gap closed)
- [x] no test or contract was altered during build — tests amended ONLY at
  the human-approved v2 change-request seam, strengthening + red-first
  (3 RED for the declared v2 reasons before the reword); the frozen v1
  contract was changed only via that approved CR
- [x] concurrency / timing of the risky operation is safe — walk runs in an
  isolated tempdir per test, subprocess timeout 120s, no shared state; no
  engine change (lock's atomic write untouched, md5 pinned ×3)
- [x] no exposed secrets, injection openings, or unexpected dependencies —
  stdlib-only test; shlex.split runs fence text sourced from the repo's own
  guide (not user input); prose-only ship change. SEAM NOTE for this gate:
  the reword moves WHO TYPES the lock to the agent — the human's explicit
  yes remains the recorded decision (v2 tightening: ambient agreement ≠
  confirmation); the machine-readable confirm protocol stays a NAMED
  deferral (gap 5)
- [x] layering & dependencies follow CONVENTIONS.md — guides ship ×3
  byte-identical (parity-pinned incl. both companions, new); engine
  feature-frozen honored
- [ ] a person reviewed and approved the change — THIS gate (Tin)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-05
Evidence: protocol walk (test_protocol_walk_zero_typed_commands) drives a fresh
install → init → lock → first task → gate PASS issuing every add.py call itself
against the INSTALLED tree (v15 exit criterion 3 met, not a proxy); §4 + the two
companion guides (setup-review.md, adopt.md) reworded ×3 so the AGENT runs the
lock on the human's explicit confirmation; suite 457/457, engine check 194/0
(4 pre-existing milestone-attach warnings), audit clean; book swept dry (zero
.add/docs/ "human types the lock" instructions).
Knowingly accepted at this PASS (Tin): the lock is now AGENT-executed; consent is
PROSE-guarded ("explicit yes to the lock-down; ambient agreement is not consent")
— the machine-readable chat-confirm protocol (gap 5) stays a NAMED deferral, not
silent. No security finding (prose-only ship change; stdlib-only test).

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the protocol walk is the standing monitor —
if a future engine/guide change breaks the fresh-install→gate journey, it goes red.
Spec delta for the next loop: a machine-readable "the human confirmed in chat"
protocol (gap 5) would turn the prose consent-guard into an enforced one — the next
milestone's candidate, now that the engine can reopen.

### Competency deltas
- [ADD · folded] a cross-cutting reword must enumerate EVERY file carrying the
  pattern before freezing, not just the one named in the gap. The v1 contract
  scoped only 0-setup.md §4; the structural suite (incl. the green protocol walk)
  was satisfied while the SAME human-types-the-lock instruction sat in two
  unswept guides (setup-review.md, adopt.md). The adversarial cross-surface lens,
  not the test suite, caught it → CR v2 (evidence: 3× MAJOR from verify-skill-onramp).
- [SDD · folded] a behavioral journey test (protocol walk) and a prose-coherence
  test are different guarantees; the walk proved the MACHINERY works at v1 while
  the GUIDE still told the human to type — words-exist ≠ method-works cuts both
  ways (evidence: test_v8_onramp's own honest-scope note, now closed by this walk).
- [ADD · folded] moving WHO-EXECUTES a gated action (human→agent) leaves the DECISION
  with the human only if the trigger is defined tightly; "recorded confirmation"
  needed "an explicit yes to the lock-down itself" to keep an eager agent from
  reading ambient agreement as consent (evidence: seam-integrity lens, 2× MAJOR).
- [ADD · folded] the docs/book is a shipped surface too — sweep it in the same grep
  as the skill tree (it was dry here only because the advisor flagged the gap in
  coverage before the gate; the lens prompt had soft-pedaled .add/docs/ to NOTE).
