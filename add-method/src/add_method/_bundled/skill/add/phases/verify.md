# Verify — evidence + non-functional review (gate + the observe tail)

Goal: establish trust and record an outcome. Passing tests are necessary, not
sufficient. Fill **§6** in PLAN.md including the GATE RECORD.

> **Who resolves this gate depends on the `autonomy:` header.** Under `autonomy: auto` (the default)
> a run auto-PASSes on complete evidence with **no residue** (security · concurrency · architecture),
> recorded *auto-resolved* with the named run as owner;
> **security is always a HARD-STOP and is never auto-passed**. Under `conservative`, or whenever
> residue is found, this phase is **human-led** (auto-PASS conditions: `run.md`).

## The reasoning discipline — verify's slice of the arc (definitions: `phases/direction.md`)

**Fluent ≠ true** holds for verdicts: a verdict's confidence tracks how much evidence prose you
wrote, not what you checked — a checkbox ticked from memory is a guess wearing a PASS. The arc
at the gate:

- **GROUND** — every Part-one checkbox is a factual claim: tick it only `[OBSERVED]` — you ran
  the suite / read the evidence THIS session; a remembered pass is `[PRIOR]` — re-run it, never
  recall it. A safety-grep counts only once you confirmed it actually matched.
- **ATTACK** — verify IS the arc's attack beat: the earned-green refute-read (Part four) whose
  primary output is a concrete falsifying input, and the three lenses of Part two. Security
  stays HARD-STOP.
- **DELIVER** — the gate card leads with the outcome, exposes the residue yourself
  lowest-confidence-first, and tags its claims by evidence basis — never a bare "all green".
- **Floor Goal check** — before recording PASS, restate the goal in the human's world: a suite
  that satisfies the §4 words but misses what they actually wanted is the most expensive miss,
  and this gate is the last place to catch it.
- **Constraint loop on the §6 record** — the record blocks (3-lens verdict · Deep checks ·
  Refute-read verdict · `Reported:`) are mechanically checkable: sweep them as a census before
  the gate — an unfilled block is an unrecorded verdict, caught by you, not by the spot-audit.

## Part one — confirm the evidence

- [ ] All tests pass — or, for a non-coding task, every §4 acceptance check is green (the evidence it names is real).
- [ ] Coverage did not decrease.
- [ ] No test or contract was altered during build.
- [ ] The §3 Target (measurable) is hit — including any declared outcome tests can't show, confirmed by real evidence.
- [ ] §1 rules trace to a §4 test (`covers:` tag) — an untraced rule is a coverage gap (`add.py check` warns on it).
- [ ] every §3-cited symbol still resolves in the CURRENT tree.

If any is false, stop and return to Build.

## Part two — check what tests miss

- **Concurrency/timing** — correct when two run at once? (Tests run serially and miss races.)
- **Security** — exposed secrets, injection openings, unexpected dependencies. A security finding is always `HARD-STOP`, never a waiver. ANY note here escalates to the human — start it with `NOTE` or `⚠` so a reviewer can see it. A finding you never marked is **invisible** — escalated to no one. Under `auto`, a human **spot-audit** (reading the diff) is the only backstop for a *missed* security finding.
- **Architecture** — respects layering/dependency rules in CONVENTIONS.md?

Run the three lenses in order — a Security `HARD-STOP` ends the checklist (leave the rest blank). Record in §6 `### Advisor 3-lens verdict` (Verdict · Residue · Binding): `sensitivity: mechanical` → Binding `yes` (engine reads it for `advisor-gate-relax`), every other class → Binding `advisory`. An unfilled block is an unrecorded verdict, not a PASS.

## Part three — the deep check (do not skim)

Code: record every new symbol referenced (wiring) and no new dead/unused code introduced. Prose or non-code: record a semantic read — what you read in full and what it confirmed. The resolver judges which path; the engine never classifies.

Record in the §6 **Deep checks** block — an unfilled one is a **shallow verify**, not a PASS.

## Part four — was the green earned?

A green suite proves tests pass — not that the build EARNED them. Three judgment cheats pass the unchanged suite: src overfit to the test fixtures (special-cased to literal inputs), vacuous asserts (green against an empty implementation), and real logic stubbed away — all invisible to the mechanical tamper tripwire. Score them with an adversarial refute-read: an independent reviewer — the engine never spawns one — prompted to argue the green was NOT earned. Its PRIMARY output is a concrete falsifying input — the fixture value, interleaving, or caller that makes the green wrong (file · line · values), not a verdict; a "looks fine" with no attempted repro is not a refute, and if a real attempt finds none it concedes the green holds and says so. A confirmed earned-green failure is HARD-STOP-class: never auto-passed, never RISK-ACCEPTED — a first cheat enters the bounded self-heal loop (run.md). Under `auto`, **record the verdict** in §6's `### Refute-read verdict` block — an unrecorded verdict leaves the auto-PASS untraceable (the human spot-audit is the backstop).

## Record exactly one outcome (no silent pass)

Render this gate from the card: banner → ARC → SUMMARY → FLAGS → EVIDENCE → APPROVE → NEXT
(`gate-udd.md` = the full template + examples, read at most once per session), and reconcile FLAGS
with `add.py report --decide`'s open-item count. Right-size the render to the risk: `sensitivity: mechanical`
tasks use the compact form — banner → SUMMARY → EVIDENCE → APPROVE; `security` / `data` /
`architecture` always get the full card. Audience by mode: under `conservative` the card renders to the human before the gate; under `autonomy: auto` (no reachable human) you WRITE it to the §6/trace record as the accountable artifact and proceed — you render, you don't wait. **Human-led: render before `gate` and record `Reported: yes` in §6, never self-stamp.**

| Outcome | When |
|---------|------|
| `PASS` | all checks met |
| `RISK-ACCEPTED` | a **non-security** gap, with signed owner + ticket + expiry |
| `HARD-STOP` | any failing test or acceptance check, or any security finding |

## Exit gate / Next

<exit_gate>
- [ ] Evidence confirmed, non-functional risks checked, outcome recorded — a person approved, or
  (under `autonomy: auto`, no residue) the run auto-resolved as accountable owner.
</exit_gate>

> **Persona** — refute-read under the fit `flow: verify` persona / Code-Reviewer lens (advisory; security still HARD-STOPs).
> **Advisor · Confidence** — the earned-green refute-read is the canonical adversarial spawn (the
> advisor spawn, below); score it with the confidence self-score (`phases/direction.md`) before recording the gate.

```bash
python3 .add/tooling/add.py gate PASS          # marks the task done
# or: add.py gate RISK-ACCEPTED   |   add.py gate HARD-STOP (return to Build)
```

## Observe (post-gate, §7) — feed the next loop

Verify owns the loop's tail since the six-phase merge. After the gate, fill §7:

1. **Release behind a scope-of-impact limit** — a flag and/or gradual rollout.
2. **Reuse scenarios as monitors** — the §4 scenarios/tests that defined "correct" define
   what you alert on: overall error rate, each rejection's rate, latency of the risky op.
3. **Draft the next spec delta** — every defect, surprise, or new need becomes a change
   that re-enters the flow at Specify (a new task). Emit lessons tagged by the
   competency they improve (`deltas.md`); file each into its living spec (`delta-append`).
4. **Propose a voice delta** — where your voice diverged from the human's, propose a
   confirmable voice delta tuning `SOUL.md`, emitted `open` (grammar + routing: `deltas.md` —
   the human is the only writer). Never auto-roll-back — recommend; a human owns production.

> **Decisions (ADR)** — the gate already harvested §7's ADR block into the milestone record.
> **Persona** — tag `· persona:<slug> · critical-rule|success-metric|anti-pattern|ability`;
> a HOW-an-agent-behaves lesson belongs in that persona file, not the shared pile.

Loop — the artifacts are living docs the next cycle refines. Map: the self-improving map
(`phases/build.md`) · book: `docs/08-step-6-verify.md` · `docs/09-the-loop.md`.

## The advisor spawn — delegate one piece, never the loop

Spawn a *single* subagent for one well-scoped piece of your plan (many-task pipelines: the
stream-orchestrator persona); the engine never spawns — your call per step. Spawn when the piece
is separable and worth the round-trip: a broad sweep, an independent adversarial review (the
refute-read — fresh context, never author-graded), a batch, a context-offload; not for narrow
cheap work — in doubt, do it in-context. **Prefer the named roster**: `add-worker` for an execution
piece (the spawn names the mode: direction · build · verify · persona) and `add-advisor` for an
advisory one (propose-plan · refute · advise-midflight) — over an ad-hoc spawn; each carries its
roster contract and loads the beat guide + best-fit persona itself. Tier: **mid** ordinary, **top**
complex/cross-cutting (the roster contract in `agents/*.md` maps tiers to
models); a stronger model never buys back a gate. **Refute-read persona** — a **Code-Reviewer**;
findings carry severity: 🔴 blocker · 🟡 concern · 💭 note. A persona is advisory: it never
lowers a gate (a security finding still HARD-STOPs).

The plan-following prompt (the worker-contract tags — canonical here):

```xml
<objective>
Execute THIS piece of the orchestrator's plan: {{PIECE}}. You own only this piece — not the
surrounding decisions. Return a verdict; do not record state.
</objective>

<persona>
SELECT the persona by frontmatter — flow: match first, then domain; read ONE body —
and load `.add/personas/{{PERSONA_SLUG}}.md` —
Identity→your stance · Critical Rules→constraints · Success Metrics→done-bar.
No match → a {{DOMAIN}} engineer, correctness over speed; never blocks.
Work step by step: load the context files + the persona; do the work in small steps honoring
the orchestrator's plan; self-score on the confidence six dimensions — any < 0.9 → refine
before returning.
</persona>

<strategy>
The task's §5 plan — the Strategy (ordered batches) order and the Known-problem fixes — is
your PREFERRED starting path, not a hard rule. Improve on it when a better strategy emerges
as you build; on done, report the strategy you ACTUALLY used so the orchestrator can update
§5 for the audit trail.
</strategy>

<context_files>
the plan / task files the piece needs (read-only unless the piece says otherwise)
</context_files>

<return>
End with a structured verdict the orchestrator parses and RECORDS:
{ piece, persona, result, evidence, confidence: {per-dimension 0–1}, open_questions }.
`persona` names the slug you adopted (or `generic`). Do NOT run add.py or write any shared
state — you propose, the orchestrator records.
</return>
```

**Delegate, don't abdicate**: the subagent PROPOSES, the orchestrator RECORDS — a worker never
runs add.py or writes shared state; delegation never lowers a gate — a SECURITY finding still
HARD-STOPs and high-risk scope still escalates, whoever did the work; a low returned self-score
means refine or re-spawn, never a pass.

## Sensitivity — the risk-class vocabulary

A `sensitivity:` header line declares the risk-CLASS (*what kind*, distinct from `risk:` = *how
much*); the engine validates + surfaces it (freeze/status/check), never classifies. Base four:
**security** (authn/authz, secrets, crypto, attack surface — HARD-STOP, human in EVERY tier) ·
**data** (persistence, migrations, privacy, loss — Datetime, money, or timezone arithmetic also ⇒
`data`, value formats are the risk surface, bench wm2's naive-timestamp green) · **architecture**
(module boundaries, contracts, cross-cutting structure) · **mechanical** (rote, low-impact — the
only class a recorded advisor verdict can gate for auto-completion, `advisor-gate-relax`). EXTEND
per project in `GLOSSARY.md`'s `## Sensitivity classes` (`- <token>: <definition>`); freeze accepts
base ∪ domain else `sensitivity_invalid`. Declared never inferred · base four never replaced · a
comment is never a declaration · a new KIND of risk → propose a class, human confirms (map domain →
base behavior in the definition, e.g. "pii … escalates to human review" = human-floor).
