# TASK: Align onboarding surfaces to the shipped v7 one-approval flow

slug: onboarding-align · created: 2026-06-02 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- bundles method/trust-layer doc edits (book/README) = high-risk scope -> v7 guard forces conservative; human reviews the diff at verify -->

> One-approval front (v7): the AI drafts Spec + Scenarios + Contract + Tests as ONE
> bundle; the human gives a single approval AT the frozen contract (the seam). Below
> is that draft. Nothing builds until you approve §3.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Now that v7 has shipped (auto-default-dial + one-approval-front both PASS, milestone
v7 done), the onboarding surfaces must tell ONE coherent truth — the one-approval
flow — and the empty-project entry point must point a brand-new user at it.

Must:
  - every shipping onboarding surface (`add-method/GETTING-STARTED.md` and
    `add-method/README.md` — root `README.md` is the book's front matter, out of scope)
    describes the SINGLE shipped flow: intake → one-approval front → self-driving run;
    security always HARD-STOP
  - `GETTING-STARTED.md` LEADS with the AI-first conversation path; the by-hand
    7-phase walk is DEMOTED to a clearly-labeled "under the hood / escape hatch"
    appendix (kept, not deleted — it is legitimate)
  - `add.py status` on a project with ZERO tasks prints a first-run next-move panel
    that names the AI-first move (`/add` + say what you want) AND the CLI escape
    hatch (`new-task`) — not a bare one-liner
After:
  - no onboarding surface narrates "v6 vs v7 / shipped default" version history
  - the dominant, and the only, flow a reader sees is the one-approval front
  - a new user running `status` first gets an actionable "your first move", not silence
Reject:
  - an onboarding surface still carries a v6/v7 "shipped default" caveat -> "version_caveat_in_onboarding"
  - `GETTING-STARTED.md` leads with the by-hand walk (AI-first not first) -> "manual_walk_leads"
  - `status` on a 0-task project prints only the bare "(none yet)" line -> "silent_empty_state"
Assumptions (confirm before building):
  - [x] v7 is shipped (both tasks PASS, milestone v7 done) — the gate the caveats waited on is closed
  - [x] human chose "one task, bundle docs + first-run panel" at intake (AskUserQuestion)
  - [x] the by-hand 7-phase walkthrough is KEPT as an escape-hatch appendix, not removed

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: onboarding tells one flow, no version history
  Given the shipped onboarding surfaces (GETTING-STARTED.md, both README.md)
  When a new reader reads them
  Then each names the one-approval front as THE flow
  And none contains a "shipped default (v6)" / "as designed in v7" caveat   # version_caveat_in_onboarding

Scenario: GETTING-STARTED leads AI-first
  Given GETTING-STARTED.md
  When a reader scans top to bottom
  Then the AI-first conversation path appears BEFORE the by-hand 7-phase walk
  And the by-hand walk is under a heading marked "under the hood" / "escape hatch"   # manual_walk_leads

Scenario: a new user's first status is actionable
  Given a freshly-initialised project with zero tasks
  When they run `add.py status`
  Then the output contains a first-run next-move panel naming `/add` and `new-task`
  And an existing project's status (with tasks) is unchanged   # silent_empty_state + regression
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT (prose, conservative) — the two shipping onboarding surfaces:
  - add-method/GETTING-STARTED.md  — AI-first leads; manual walk -> labeled appendix; zero version caveats
  - add-method/README.md           — "Use it" section names one flow; zero version caveats
  (OUT of scope: root README.md = the BOOK's front matter, carries no caveat + no onboarding flow)
ARTIFACT (code, auto):
  - add-method/tooling/add.py :: cmd_status  — the `if not tasks:` branch prints a first-run panel
  - .add/tooling/add.py                       — md5-identical to the package copy (engine parity)

FROZEN:
  - onboarding surfaces describe ONE flow (intake -> one-approval front -> self-driving run);
    security HARD-STOP intact; NO v6/v7 "shipped default" version narration
  - GETTING-STARTED: AI-first section ordered before the by-hand walk; by-hand walk under an
    "under the hood / escape hatch" heading
  - empty-project `status` first-run panel names BOTH `/add` (AI-first) and `new-task` (escape hatch);
    populated `status` output is byte-unchanged
  - the dial/seam guards from v7 are unchanged; this task does NOT touch run.md or the 7-phase flow

GUARD: tests/test_onboarding_align.py
  - asserts each surface contains one-approval-front language and NO caveat substring
  - asserts GETTING-STARTED section ordering (AI-first index < by-hand index) + appendix heading present
  - asserts empty-project status stdout contains the panel; populated status regression-safe
  - asserts add.py dual-tree md5 parity

reject codes: version_caveat_in_onboarding · manual_walk_leads · silent_empty_state
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (HUMAN-approved at the seam — AskUserQuestion "Approve & freeze — build", 2026-06-02; AI drafted, human froze)

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: structural (string + ordering + md5 assertions), matching the project's
existing doc-test convention (test_v8_docs.py / test_v8_onramp.py).

Plan (one test per scenario; assert behavior/content, not internals):
  - test_no_version_caveat_in_onboarding: read the two surfaces (GETTING-STARTED + pkg README);
    assert each is free of the caveat substrings ("as designed in v7", "Today's **shipped**",
    "three-gate front") AND each contains "one-approval front"
  - test_getting_started_leads_ai_first: assert the AI-first/conversation heading index <
    the by-hand-walk heading index; assert an "under the hood"/"escape hatch" appendix heading exists
  - test_status_first_run_panel: init a temp 0-task project; run cmd_status; assert stdout has the
    first-run panel naming "/add" and "new-task"
  - test_status_populated_unchanged: with >=1 task, assert the task-listing output is unchanged
    (regression guard so the panel only fires on the empty state)
  - test_addpy_dual_tree_md5: assert add-method/tooling/add.py == .add/tooling/add.py

Tests live in: `./tests/` · MUST run red (caveats still present, panel not built) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): edit prose + the single `if not tasks:` status branch ONLY;
do not touch run.md, the 7-phase flow, the dial, or any frozen contract. Keep both add.py
trees md5-identical. The by-hand walkthrough is MOVED to an appendix, never deleted.
Code lives in: `./src/` (panel) · prose edits in the named files
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

BUILT (3 changes, all green — full suite 178 OK):
  - add-method/GETTING-STARTED.md — removed the v6/v7 caveat blockquote; demoted the 7-phase
    walk under a new heading "## Under the hood — the seven phases by hand (escape hatch)"
  - add-method/README.md — removed the v6/v7 caveat blockquote ("one-approval front" already named)
  - add.py cmd_status `if not tasks:` branch — first-run panel naming `/add` + `new-task`;
    synced canonical -> dogfood via cp (md5 ca2d7bd… identical)

DEVIATIONS (recorded, none weaken the contract):
  1. test location: guard lives at add-method/tooling/test_onboarding_align.py (the project's
     tooling-test home where every sibling test_*.py runs + imports add.py), not the template's
     ./tests/ path. Clarification of the GUARD location, not a scope change.
  2. CHANGE-REQUEST (human-approved, AskUserQuestion 2026-06-02): v7 shipping falsified a sibling
     guard — test_v8_docs.test_docs_label_designed_vs_shipped required the now-removed caveat.
     Re-aimed it -> test_docs_post_ship_honesty (asserts the shipped one-approval front is named +
     NO stale version narration). Honesty guard kept, pointed at the post-ship truth — not weakened.
  3. strengthened test_getting_started_leads_ai_first to require an actual heading line (stricter).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 178 OK (5 new in test_onboarding_align + re-aimed test_v8_docs green)
- [x] coverage did not decrease — +5 guards; the v8 honesty guard re-aimed (kept), not dropped
- [x] no FROZEN contract altered during build; tests changed only as the human-approved change-request
      (re-aim test_v8_docs) + a strengthening (ai-first heading) — never a weakening to pass the build
- [x] concurrency / timing — n/a (no shared state; prose + a pure print branch)
- [x] no exposed secrets, injection openings, or unexpected dependencies (stdlib-only; prose)
- [x] layering & dependencies follow CONVENTIONS.md; both add.py trees md5-identical (engine parity)
- [x] a person reviewed and approved the change (conservative scope: human reviewed the diff at this gate)

Blind-spot / residue (conservative scope): one method/trust-layer edit (re-aiming a sibling guard)
— ESCALATED and human-approved (AskUserQuestion 2026-06-02) before it was made. No security finding.

### GATE RECORD
Outcome: PASS — human-reviewed (conservative-scope diff review completed at verify)
Reviewed by: Tin Dang (human, diff review — AskUserQuestion) · date: 2026-06-02

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: whether new adopters still hit the by-hand walk first (telemetry: which path they follow);
whether the first-run panel actually reduces "what do I do now?" confusion.
Spec delta for the next loop: the deferred first-class enforcer for the v7 high-risk guard /
one-approval seam (carried from v7) is still open — onboarding now claims the flow the enforcer
does not yet guarantee.

### Competency deltas
- [SDD · folded] onboarding docs OUTRAN their verify gate — the v6/v7/onboarding contradiction
  existed because docs claimed a flow before its tasks were PASS. Rule: a surface may not describe a
  flow whose gate is not yet recorded. [folded → PROJECT.md §Spec/§Key Decisions + CONVENTIONS.md, foundation-version 4]
- [ADD · folded] shipping a milestone can falsify a SIBLING task's frozen guard — v7 shipping broke
  test_v8_docs (it asserted the now-removed caveat). Stale-guard sweep at milestone close.
  [folded → CONVENTIONS.md, foundation-version 4]
- [UDD · folded] the empty-project `status` was a silent dead-end for a brand-new user; the first-run
  panel fixes the worst-lost moment. [folded → PROJECT.md §Users, foundation-version 4]
  (measurement of whether it reduces confusion remains an OBSERVE item, not a foundation delta.)
- [TDD · folded] the onboarding guards are structural string/ordering matches — they prove the WORDS,
  not that a human onboards faster (evidence: test_onboarding_align asserts string presence + section
  order, never a timed onboarding). The recurring v6/v7/v8 words-exist≠method-works gap persists here.
  (left open by human choice at the 2026-06-02 fold — same recurring gap already deferred in v7.)
