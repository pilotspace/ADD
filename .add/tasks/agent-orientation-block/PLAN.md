# TASK: Rewrite the sync-guidelines orientation block to the AI-first flow

slug: agent-orientation-block · created: 2026-06-02 · stage: mvp · v8 · depends-on: none
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- method/trust-layer edit (the agent's first instruction) = high-risk scope -> conservative (v7 guard, self-applied). Hold at verify for human diff review. -->

> v8 · *DD driver: ADD. Owns `_guideline_block()` in add.py (both trees) — the CLAUDE.md/AGENTS.md
> orientation block `sync-guidelines` writes. Re-aims it from the manual phase-walk to the AI-first flow.

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

The orientation block (`_guideline_block()` → CLAUDE.md/AGENTS.md) is the agent's FIRST instruction
after install. Today it teaches the *manual* flow ("keep the `phase:` marker in sync via
`add.py phase`/`advance`, record the gate with `add.py gate`") — the least AI-first version of the
method. Re-aim it at the AI-first flow without bloating it (it stays a stable minimal pointer; see
add.py:198–201 — auto-loaded context measurably hurts).

Must:
  - keep orient-first: step 1 = `add.py status`, step 2 = read `.add/PROJECT.md` foundation
  - name the AI-first flow: the **`add` skill drives** — INTAKE sizes a request into a milestone,
    then each task runs the **one-approval front** (Spec+Scenarios+Contract+Tests bundle, ONE
    approval at the frozen contract) → a self-driving build→verify run
  - frame `add.py` as the **agent's hands**, not the human's prescribed interface
  - stay a **stable minimal pointer** — point at the skill + book (`.add/docs/`); do not duplicate
    the flow or grow into an always-loaded narrative
  - keep both add.py trees byte-identical (mirror parity)
Reject:
  - block prescribes the human hand-walking phases (`phase`/`advance`/`gate` as their job) -> "manual_only_framing"
  - block bloats past a pointer (enumerates the whole flow instead of aiming at the skill)        -> "bloated_pointer"
After:
  - `_guideline_block()` teaches orient → skill-driven intake → milestone → one-approval run; `add.py`
    framed as the agent's tool; book still pointed to; both trees identical.
Assumptions (confirm before building):
  - [x] the block stays a minimal pointer (honor add.py:198–201), re-aimed not expanded — design-confirmed
  - [x] `add.py` CLI is kept as the agent's hands + human escape hatch (v8 Scope Out) — milestone-confirmed

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the block names the AI-first flow
  Given the block _guideline_block() generates
  Then it names intake, milestone, and the one-approval front, and points at the `add` skill

Scenario: manual-only framing is gone
  Given the block
  Then it does NOT prescribe the human hand-walking phases via `phase`/`advance`/`gate`

Scenario: it stays a stable pointer (not bloated)
  Given the block
  Then it still points at `.add/docs/` (the book) and stays short — a pointer, not a flow narrative

Scenario: both trees stay identical
  Given add-method/tooling/add.py and .add/tooling/add.py
  Then they are byte-identical (mirror parity preserved)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT: _guideline_block() in add.py (both trees, byte-identical) — the CLAUDE.md/AGENTS.md
          orientation block written by `sync-guidelines` / `init`.
FROZEN:   the block (a) keeps orient-first (status, then PROJECT.md), (b) names the AI-first flow —
          the `add` skill drives: intake → milestone → one-approval front → self-driving run,
          (c) frames add.py as the agent's hands not the human's interface, (d) stays a minimal
          pointer to the skill + book (.add/docs/), (e) keeps both add.py trees byte-identical.
GUARD:    test_v8_onramp.py — names-ai-first-flow · drops-manual-only-framing · stays-a-pointer · addpy-parity
reject codes: manual_only_framing, bloated_pointer
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (HUMAN-approved at the seam — AskUserQuestion "Approve & freeze", 2026-06-02)

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Structural (same pattern as test_v7_auto_default.py — assert the rubric's words exist; words-exist
!= method-works, the runtime property is unreachable by a string check). Lives in
`add-method/tooling/test_v8_onramp.py`; imports `_guideline_block()` from the canonical add.py.

Plan (one test per scenario):
  - test_block_names_ai_first_flow:    block names intake + milestone + "one approval" + the `add` skill
  - test_block_drops_manual_only_framing: block lacks the `phase`/`advance` hand-walk prescription   [RED now]
  - test_block_stays_a_pointer:        block still points at `.add/docs/`; line count within a pointer bound
  - test_addpy_parity:                 md5(add-method/tooling/add.py) == md5(.add/tooling/add.py)

RED now for the right reason: the two behavioral tests fail because the current block has no
intake/milestone/one-approval language and still carries the manual phase-walk. Parity + pointer
start green — they are invariants the build must not break.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the block is the agent's FIRST instruction after install — it must
stay a stable minimal pointer (add.py:198–201), and the edit MUST land byte-identical in both
`add.py` trees (a drifted block = two different methods).
Artifact: `_guideline_block()` in `add-method/tooling/add.py` + mirrored `.add/tooling/add.py`.
Constraints: did NOT touch test_v8_onramp.py or the frozen contract; no new dependency (stdlib only).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_v8_onramp` 4/4; full tooling suite **158 OK**; `add.py check` **112/0**
- [x] coverage did not decrease — added 4 structural tests; none removed/weakened
- [x] no test or contract was altered during build — contract FROZEN @ v1; test_v8 unchanged since red
- [x] concurrency / timing — N/A (pure string template; no IO, no shared state)
- [x] no exposed secrets / injection / unexpected dependencies — stdlib-only, no inputs
- [x] layering & dependencies follow CONVENTIONS.md — edit confined to `_guideline_block()`; both trees identical
- [x] a person reviewed and approved the change — human approved at verify (AskUserQuestion 2026-06-02)

Blind-spot (completeness-critic): the guard proves the block's WORDS are AI-first; it does NOT prove
an agent actually runs intake→milestone→one-approval (words-exist != method-works — same honest gap
as v6/v7). Carries forward as an OBSERVE watch, not a blocker.
Backward-correction resolved: the v8 honesty-rule (designed-vs-shipped) conflicted with the
minimal-pointer constraint for this artifact. Human chose "accept block + amend rule" — MILESTONE.md
now exempts the terse pointer and adds a release-ordering constraint (v8 ships with/after v7).

### GATE RECORD
Outcome: PASS   <!-- human-approved at verify; honesty-rule conflict resolved by milestone amendment -->
Reviewed by: Tin Dang (human, at verify gate) · date: 2026-06-02

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does a freshly-installed agent actually run intake→milestone
→one-approval, or fall back to ad-hoc coding? (the words-exist≠method-works gap).
Spec delta for the next loop: the rendered block claims a flow the agent must honor — pair with the
deferred CI/runtime enforcer (v7 carry-forward) so the seam is checked, not just described.

### Competency deltas
- [ADD · folded] No CLI verb re-points `active_task` among parallel tasks — `new-task` sets it, but
  switching to an existing sibling needs `phase <p> <slug>` by explicit slug, and `status` then
  reports a stale active task. Evidence: had to drive this whole task by slug while `active_task`
  stayed `milestone-onboarding-docs`. Candidate: `add.py activate <slug>` (engine bookkeeping, not judgment).
  [folded foundation-version 8 → PROJECT.md §Spec OPEN "add.py activate <slug>" (deferred feature)]
- [ADD · folded] The orientation block now describes the one-approval/auto flow that is v7-*designed*
  but not shipped (v7 at verify). Evidence: this build labels designed-vs-shipped in prose only —
  the block itself can't. Watch whether new users hit the gap; the honesty rule lives in the docs tasks.
  [folded foundation-version 8 → reinforces CONVENTIONS.md "Docs must not outrun their gate"]
