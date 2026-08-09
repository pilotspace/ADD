# MILESTONE: Auto by default — the one-approval flow

goal: Make auto the default autonomy and compress the human-led front to a single
approval at the contract-freeze seam — keeping the seam human and security a HARD-STOP.
stage: mvp · status: active · created: 2026-06-01

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> **What v7 reverses, and what it keeps.** v6 made the build->verify far side a
> dynamic run with `conservative` as the dial default. v7 is a **deliberate,
> human-directed reversal** of that default: `auto` becomes the default, and the
> human-led FRONT compresses from three approvals to **one batched approval at the
> contract-freeze seam**. This overrides the v6/foundation-version-2 stance
> ("conservative is default", reject code `auto_by_default`) — recorded honestly,
> not hidden. The two load-bearing safeties from v6 are PRESERVED: the contract
> freeze stays human (so "never self-gate a human-led gate" still holds), and
> security is always a HARD-STOP.

## Scope
In:  (1) **dial default flip** — `run.md` §autonomy dial: `conservative` -> `auto`
     as the default; the per-scope dial (principle 5) is kept, only its starting
     point moves; a new guard requires **high-risk / method-defining scope to lower
     to `conservative`** (reject code `unguarded_high_risk_auto`), retiring
     `auto_by_default`. (2) **one-approval front** — the human-led front compresses:
     the AI analyzes the user's input and drafts Spec + Scenarios + Contract + Tests
     as ONE bundle; the human gives a **single approval at the frozen contract** (the
     seam); build->verify then runs auto and auto-gates on evidence. (3) **principle
     5 reframe** — "start `auto`, lower on risk" replaces "start `conservative`, earn
     `auto`"; the per-scope substance is unchanged. (4) **governance default** —
     the autonomy-ladder/profile default row moves to auto-with-evidence behind the
     one-approval seam.
Out: any change that lets the AI **freeze its own contract** — the seam stays human
     (one approval, but a human one); any **auto-pass of the residue** — security
     (HARD-STOP, always), concurrency, architecture still escalate; any **autonomous
     fold** (v5 holds: run emits `open`, the human folds); any new always-loaded doc
     (Minimal pillar holds — `run.md` stays on-demand); any re-cut of the 7-phase
     sequence; any engine judgment in `add.py` (the dial stays a rubric).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **`auto` is the default; `conservative` is the deliberate lowering.** This reverses
  v6. Principle 5 ("trust earned per scope") is intact — what moves is the default
  starting point, not the per-scope nature of the dial.
- **The seam stays human — one approval, not zero.** The AI drafts the whole front
  bundle, but the human approves the FROZEN contract. The AI never freezes the
  interface it then builds against. This is what keeps "never self-gate a human-led
  gate" (foundation-version 2) true under an auto default.
- **High-risk scope must lower to `conservative`.** The v6 dogfood blind-spot —
  `auto` on the riskiest possible scope (the method itself) — is now a named guard,
  not a hope. `auto` on a high-risk/method-defining scope is `unguarded_high_risk_auto`.
- **Security is always a HARD-STOP.** Unchanged, absolute, never swept into "auto".
- **Engine is truth; the dial is a rubric (v4-1).** `add.py` may record an outcome;
  it must not decide autonomy. The default lives in `run.md` + the book, not a flag.
- New glossary term: **One-approval front** (the batched Spec+Scenarios+Contract+Tests
  draft approved once at the seam).

## Shared / risky contracts (freeze these first)
- the **autonomy default + high-risk guard** — what the default level is, and the
  exact condition under which `auto` is refused and `conservative` is forced. Riskiest
  because it reverses a folded learning; freeze first -> auto-default-dial

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] auto-default-dial   depends-on: none               — `run.md` §autonomy dial default conservative->auto; retire `auto_by_default`; add `unguarded_high_risk_auto` high-risk guard; principle 5 reframe + governance default row  [PASS 2026-06-02]
- [x] one-approval-front  depends-on: auto-default-dial   — `run.md` front/seam section: AI drafts Spec+Scenarios+Contract+Tests as one bundle; human gives ONE approval at the frozen contract; then auto runs  [PASS 2026-06-02]

## Exit criteria (observable; map each to the task that delivers it)
- [x] `run.md` states `auto` is the default and per-scope dial is preserved          (← auto-default-dial)
- [x] high-risk/method-defining scope is guarded — `auto` refused, must lower          (← auto-default-dial)
- [x] book principle 5 reads "start auto, lower on risk"; security HARD-STOP intact    (← auto-default-dial)
- [x] `run.md` documents the one-approval front (AI drafts the bundle, human approves the seam once)  (← one-approval-front)

## Deferred issues (tracked, not folded — open competency deltas + carry-forward)
- carry-forward from v6 (still open): the run does not actually fan out (#8); no
  automated fold-nudge (#13); **no high-risk auto-gate friction signal (#16)** — now
  MORE load-bearing under an auto default, since the guard is prose, not enforcement.
- new (v7): enforcement is prose, not engine — nothing tests that a high-risk scope
  actually lowers, or that the one-approval seam is honored (the recurring v6 TDD gap:
  words-exist != method-works). Candidate for a CI enforcer separate from the agent.
- new (v7): "human just approves the bundle" — does compressing Scenarios+Contract
  into a single approval cost edge-case coverage the human would have caught across
  three separate gates? Watch in OBSERVE.
