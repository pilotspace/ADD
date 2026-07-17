# Direction — the whole specification bundle (setup · rules · plan · red suite) to the ONE freeze

Every task drafts §1–§4 top-to-bottom, then ONE human approval crosses it into build:
`add.py freeze --by <name> --cross`. This file is the reference depth for that span —
SKILL.md carries the loop; read the section you're stuck in, not the file.

---

## Setup — first session only (autonomous draft → one baseline lock)

## 1 · Zero-touch entry — you run init yourself

No `.add/state.json`? Run init yourself — never tell the human to. Infer name + stage from the
repo and **arm the baseline-approval gate** with `--await-lock`:

```bash
python3 .add/tooling/add.py init --name "<inferred from repo/dir>" --stage <prototype|poc|mvp|production> --await-lock
```

- `--await-lock` seeds an *unlocked* setup — the engine refuses build/`gate` until you `lock`; a plain `init` is grandfathered-locked (re-lock: `already_locked`).
- name + stage are **your judgment**: throwaway → `prototype`, risky slice → `poc`, narrow → `mvp`, full rigor → `production`.
- `init` prints your branch: `brownfield:` → existing code, map it SILENTLY (open `adopt.md`: fill each living documentation file from code, never clobber, tag `evidence-grounded` | `guessed`; ask the human nothing). No `brownfield:` → greenfield, run the 4-lens interview below.

## 2 · Greenfield — the 4-lens interview: co-specify at foundation level

Ask one load-bearing question per lens (only the live ones), draft, rank lowest-confidence-first:

| Lens | The one question that unblocks the section |
|------|--------------------------------------------|
| Domain (DDD) | The 3–5 core nouns, and the one invariant that must NEVER break? |
| Spec (SDD) | The first milestone's outcome — and what's explicitly NOT in v1? |
| Users (UDD) | The primary user and the one job they hire this for? (or "no UI — surface is X") |
| Decisions | What's already decided that you'd regret re-litigating? (first Key Decision row) |

Rank: `⚠ <assumption> — lowest confidence because <why>; if wrong: <cost>` — tag thin answers
`guessed`. Under `autonomy: auto`, deepen all four drives in one pass (deepens drafting, never the
gate); capture each surfaced decision as an ADR in `PROJECT.md` **Key Decisions**.

## 3 · Draft to the lock (both paths)

1. **Pin invariants first — never defer.** The "never breaks" invariant + any imposed
   run/entry contract (interpreter · port · packaging · protocol) land in PROJECT.md `invariants:`
   NOW; every task's §3 Grounding re-states the ones it touches.
2. **Seed, don't draft.** Fill ONLY the `goal:` line, the 4-lens seed answers, and the sections the
   FIRST milestone touches (UI project: seed `DESIGN.md` per `design.md`; delete if no UI). Every
   other section keeps its `<!-- living: fill on first touch -->` marker. One `generic` persona is
   enough at setup; author per-role personas from the local teacher library
   (`.add/personas-teacher/`) when a task first embodies the role.
3. **Propose, then size it.** Float a kickoff suggestion (goal · flow · scenarios) for the first
   milestone; on the human's reaction draft `MILESTONE.md` (read `scope.md`).
4. **Create the first task and draft its bundle §1–§4** (`new-task` is allowed pre-lock; the red
   suite must FAIL before build). Leave §3 `Status: DRAFT` — the lock is its approval; the engine
   refuses build until you `lock` (`setup_unlocked`).
5. **Write `.add/SETUP-REVIEW.md`** per `setup-review.md`: every drafted decision,
   **lowest-confidence-first**, tagged `guessed` | `evidence-grounded`.

**Run mode** — propose before the lock, confirm-to-keep, record in PROJECT.md Key Decisions:

| Run mode | Human gates | Concurrency |
|----------|-------------|-------------|
| **sequential · auto** *(default)* | contract freeze **only** — Verify auto-PASSes on evidence | one task at a time |
| **sequential · manual/conservative** | contract freeze **and** every Verify | one task; safest |

Raise the gate: `add.py autonomy set conservative --project` · parallel streams per milestone:
`add.py streams set parallel --project` + `add.py waves`. Floor: **one human approval per contract**.

## 4 · The one human gate — the baseline approval

Open the report with the ARC per `gate-udd.md`, then present `SETUP-REVIEW.md`
lowest-confidence-first. They confirm **once** — an explicit yes; ambient agreement is not a
confirmation. **Never self-stamp a timeout — hold, or re-ask.** On that recorded confirmation, you run:

```bash
python3 .add/tooling/add.py lock --by "<name>"
```

Typing it themselves stays the escape hatch. The lock IS the first task's contract approval —
stamp its §3 `Status: FROZEN @ v1`, build is open.

<exit_gate>
- [ ] `.add/state.json` exists; setup seeded unlocked (`--await-lock`) then locked.
- [ ] Seed lines filled; untouched sections carry the living marker (brownfield: evidence-grounded from code).
- [ ] First task created; §1–§4 drafted — the red suite runs RED before build opens; `.add/SETUP-REVIEW.md` written lowest-confidence-first.
- [ ] Human confirmed the baseline approval and `add.py lock --by` ran with their name.
</exit_gate>

---

## Rules (§1) + scenarios (§2) — co-specification

State what the feature MUST do and what it must REJECT, with zero ambiguity left for the AI to
resolve by guessing. Co-specify in three moves: **Diverge** (surface the 2–3 genuine framings +
open questions; let the user react), **Converge** (draft §1 by PROJECTING from the milestone
`## Ground` + the request), **Validate** (present the ranked uncertainty first). If you cannot
write the spec, you don't yet understand the feature — stop and ask. **Identity is direction, not
default (UDD)**: brand/palette/typeface are human-owned — surface, never assume; a UI screen runs
the design-definition loop (`design.md`).

<output_format>
- **Framings weighed** — one-line trace: `X (chosen) · Y · Z`.
- **Must** — each required behavior. **Reject** — each refused input/situation with a **named error
  code** (`amount <= 0 -> "amount_invalid"`). **After** — the state true once it succeeds.
- **Boundary** — one format-variant per external input shape the tests must speak (or an explicit "none").
- **Assumptions — lowest-confidence first** — ranked most-likely-wrong → least; the top 1–2 carry
  `⚠ <assumption> — lowest confidence because <why>; if wrong: <cost>`.
</output_format>

§2 makes every rule checkable — one scenario per Must and per Reject:

```gherkin
Scenario: <short name>
  Given <starting situation>
  When <action>
  Then <observable result>
  And <what must remain unchanged>   # REQUIRED for every rejection
```

Then sweep the edge cases — boundary · duplicate · partial failure · concurrency · malformed input —
one per applicable case, or rule it out on purpose. Every Then is specific and observable, never
"then it works". Your §1 ranking feeds the bundle-level flag the human reads at the freeze.

<exit_gate>
- [ ] Framings weighed noted; every required behavior stated; every rejection has a named error code.
- [ ] Assumptions ordered lowest-confidence first; the 1–2 `⚠` flags carry why + cost — or an honest
      "none material" that still names the single biggest risk (never a blank "none").
- [ ] §2: one scenario per Must and per Reject; every rejection asserts what stays unchanged; edge
      cases covered or ruled out on purpose.
</exit_gate>

---

## Plan (§3) — ground · freeze the shape · build-strategy

Turn the rules + scenarios into ONE change plan and FREEZE it. Below the freeze code is disposable;
above it the Contract does not move.

### Grounding — the real code the contract will cite (gather BEFORE you freeze)
Project from the milestone `## Ground`, then deepen only where THIS task lands. Never invent a
file/symbol you have not opened.
- **Touches** — real files · symbols · signatures, as `path:symbol — what it is / how keyed` (cite the
  symbol, not a bare line number — `l.NNN` rots; symbols survive). Use code-navigation tools, not memory.
- **Context (working folder)** — non-code artifacts touched: docs/textbase · TODOs · config · data fixtures. Task-delta.
- **Honors** — patterns/conventions from `PROJECT.md`/`CONVENTIONS.md` · seams consulted (`SEAMS.md`). Task-delta.
- **Anchors the contract cites** — the specific symbols §3's Contract will name; it may cite ONLY these.
- **Issues/Risks** — concrete traps/untestable risks found in the real code (feeds §1).
- **Related intent** — the WHY: `PROJECT.md §` · `GLOSSARY` term(s) · originating request/milestone rationale.
- **Ground SHA** — the commit grounded against, stamped by freeze.

Sweep BROAD cheaply (skim an index/map; a subagent sweep for unfamiliar ground), then DEEPEN on
what THIS task needs. **Grounding is complete when** every field
is filled from real assets (a `<…>` placeholder = weak). *Greenfield / first task:* grounding IS the
foundation docs — an honest "new module, no code; honors CONVENTIONS.md §X" is complete.

### Contract — freeze the external shape (HARD, tamper-guarded)
Interfaces with inputs/outputs; shapes + persistent schema (note transactional needs). Names drawn
from `GLOSSARY.md`; a response for **every** Reject code from §1; cites only Grounding anchors.
Declare the measurable **Target** — the success bar the verify evidence must hit (numbers, not
adjectives; judged at the gate with `--target-hit`). Generate a mock + contract tests so
dependent work can start.

### Build-strategy — the intended approach (SOFT: preferred; the builder self-improves, records actual at verify)
**Scope (may touch)** — backticked path tokens; the freeze locks this. **Strategy** — ordered
batches. **Approach / Data strategy / Pattern / Optimization stance** — the domain plan + the
trust-least facet. **Persona** · **Spawn isolation** · **Known-problem fixes** (`SEAMS.md` traps).

### The freeze — the one approval
Present the bundle **lowest-confidence first**. Render from the card: banner → ARC → SHAPE →
SUMMARY → FLAGS → DECIDED → EVIDENCE → APPROVE → NEXT (`gate-udd.md` = template + examples, read at
most once per session) — **render before `FROZEN`, then record `Reported: yes`; never on a
timeout** (`run.md`). The freeze always renders the full card. The approval freezes the Contract
(HARD) + the Build-strategy Scope; then `Status: FROZEN @ v1 — approved by <name>`. The freeze also
ratifies the header `route:` line — the persona's lane proposal — recording it to state
(`route_unrecorded` is audit-measured, never a refusal).

<exit_gate>
- [ ] **Grounding** — Touches · Context · Honors · Anchors named from the code; Issues/Risks · Related intent · Ground SHA recorded (or an honest none).
- [ ] **Contract** — versioned, `FROZEN`; contract tests pass against the mock; every name matches the glossary; every §1 rejection has a contracted response.
- [ ] **Build-strategy** — Scope declared; batches + persona + spawn isolation named; a measurable Target set.
- [ ] The Contract cites only Grounding anchors; the ⚠ lowest-confidence flag is surfaced.
</exit_gate>

## The freeze review checklist

The human's one minute, aimed. Walk these seven before saying yes:

- **⚠ flags first** — read the lowest-confidence flags; accept each knowing its cost if wrong. The engine refuses an unflagged freeze before build (`unflagged_freeze`).
- **Intent** — does §1 say what you actually want built?
- **Cases** — does every Must and Reject have an observable §2 scenario?
- **Shape** — glossary names, error codes, additive vs breaking: is THIS the shape to freeze?
- **Grounded** — does the Contract cite anchors that exist in the Grounding map? `status`/`check` surface this.
- **Risk** — high-risk or method-defining? Require `risk: high · autonomy: conservative` in the TASK.md header.
- **Tests** — will §4 go red for the right reason, asserting behavior rather than internals?

Reject any line → the bundle goes back to draft; the freeze stays the only gate.

---

## Tests (§4) — failing-first suite

Run the suite now, with no implementation — **red for the right reason** (missing implementation,
not a broken harness). A test green before code exists is testing nothing. **A test is any
machine-checkable assertion**, not only xUnit code — a metric threshold (ML/data), a reconciliation
query, a plan-diff (infra), a rendered-screen diff (UI). Produce: one executable test per §2
scenario asserting **behavior, not internals** · contract-conformance tests (shapes + error
responses) · side-effect assertions on rejection paths (`assert balance unchanged`) · a recorded
coverage target · §6 **Build expectations** filled now, BEFORE build.

## Declaring where tests live

§4's `Tests live in:` line is machine-read — declare paths as backticked tokens on that line: with
no local `tests/`, `add.py report` counts test functions at the declared paths (FIRST such line only).
`./…` → this task dir · a token with `/` → the project root · a bare name → a
sibling of the previous token's dir. A directory counts its `*.py` files
(non-recursive); a `.py` file counts itself. Resolved files dedupe; declared counts
marked `†`. Paths are confined: outside the project root counts 0 — `..` traversal,
absolute paths, and symlink escapes are never read.

<exit_gate>
- [ ] One test per scenario, red for the right reason, asserting observable behavior; coverage target recorded.
</exit_gate>

> **Persona / Advisor / Confidence** — load the fit `.add/personas/<slug>.md` (its Critical Rules
> shape §1, its Success Metrics shape the red suite; advisory, never lowers a gate). Canonical
> spawns: a researcher for an unfamiliar domain, a broad ground sweep, a second opinion on a risky
> shape, a test-author for a wide suite (`advisor.md`); self-score the bundle — the lowest dimension
> aims your ⚠ flag (`confidence.md`).

Book: `docs/03-step-1-specify.md` · `docs/05-step-3-plan.md` · `docs/06-step-4-tests.md` · `docs/10-setup-and-stages.md`.
