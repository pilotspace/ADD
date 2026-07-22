# Direction — the whole specification bundle (setup · rules · plan · red suite) to the ONE freeze

Every task COMPOSES §1–§3 + §5-scope in ONE silent draft — a single write, no "moving on to §N"
narration — then §4 runs red and ONE human approval crosses it into build:
`add.py freeze --by <name> --cross`. The only mandatory breaks in the draft are running the §4 red
suite (a tool action, not prose) and the freeze. This file is the reference depth for that span —
SKILL.md carries the loop; read the section you're stuck in, not the file.

## The reasoning discipline (the lens for the sections below)

**Fluent ≠ true.** A draft's polish tracks its token count, not its evidence; every check in this
file forces a fresh derivation from THIS task over a plausible template. It is Rule 2 (trust
evidence, not inspection) turned inward — on your own reasoning, not just the build. Distilled from
the fable-thinking protocol; each move maps to where the loop already applies it.

**Five moves, one arc per beat:**
- **FRAME** — restate the real question + the load-bearing facts. → §1 co-specify.
- **GROUND** — verify by observation, not memory; a recalled file/flag/symbol/lesson is `[PRIOR]`
  until re-confirmed against the live tree THIS session; a live read outranks memory. → §3 Grounding.
- **REASON** — hold more than one hypothesis; demand a mechanism ("because…"), not a correlation;
  simulate with concrete values before committing. → the persona plan · the advisor's propose-plan.
- **ATTACK** — switch to reviewer, run the cheap kill-test; its output is a concrete falsifying input
  (file · line · values), not a verdict. → advisor `refute` · verify earned-green (security = HARD-STOP).
- **DELIVER** — lead with the outcome, expose the weakness, recommend don't survey. → the gate report, lowest-confidence-first.

**Two pre-answer checks the fluent draft skips** (applied at the freeze — checklist below): the
**Floor** — restate the **Goal** in the human's world (not the wording), then sweep the
**Leftovers** (every supplied invariant / the BARE runtime encoded or waived) — and the
**constraint loop** for mechanically-checkable output shape (§3 tag census · §5 scope tokens · §4
`covers:` keys · REDS): expand → verify mechanically (grep/count, not a re-read) → repair → then freeze.

**Claim grammar** — tag each factual assertion by how you know it: `[OBSERVED]` (checked live this
session) · `[DERIVED]` (follows from an observation) · `[PRIOR]` (memory, may be stale) · `[ASSUMED]`
(unverified but required). A bare claim reads as OBSERVED — never leave a guess untagged; it is the
advisor's §6 Return discipline.

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
   milestone; on the human's reaction draft `MILESTONE.md` (Milestone scope drafting, below).
4. **Create the first task and draft its bundle §1–§4** (`new-task` is allowed pre-lock; the red
   suite must FAIL before build). Leave §3 `Status: DRAFT` — the lock is its approval; the engine
   refuses build until you `lock` (`setup_unlocked`).
5. **Write `.add/SETUP-REVIEW.md`** per `adopt.md`'s Setup review section: every drafted
   decision, **lowest-confidence-first**, tagged `guessed` | `evidence-grounded`.

**Run mode** — propose before the lock, confirm-to-keep, record in PROJECT.md Key Decisions:

| Autonomy | Human gates |
|----------|-------------|
| **sequential · auto** *(default)* | contract freeze **only** — Verify auto-PASSes on evidence |
| **sequential · manual/conservative** | contract freeze **and** every Verify — safest |

One task at a time; raise the gate via `add.py autonomy set conservative --project` (or
`init --run-mode conservative`). Need concurrency? Spawn a subagent per task to run in parallel, its
model picked by task complexity (mid ordinary · top complex) — floor stays **one human approval per contract**.

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
- [ ] First task created; §1–§4 drafted — the red suite (or §4 acceptance checks) runs RED before build opens; `.add/SETUP-REVIEW.md` written lowest-confidence-first.
- [ ] Human confirmed the baseline approval and `add.py lock --by` ran with their name.
</exit_gate>

---

## Milestone scope drafting — a classified request into a versioned MILESTONE.md

Intake CLASSIFIES (`intake.md`); this rubric fills the confirmed `MILESTONE.md` (the
template is the SHAPE).
`new-major`/`sub-milestone` → draft ONE MILESTONE.md · `split_required` → draft ALL N as one
batch pass · `task`/`change-request` → no milestone (route per intake).
**Confirm before create is the convention** — one drafting pass, nothing written until the human confirms; enforced only
by the opt-in gate: `new-milestone <slug> --await-confirm` seeds it unconfirmed and HOLDS
`new-task` (`milestone_unconfirmed`) until you show the filled draft and run
`milestone-confirm <slug>`.

## Position the goal FIRST — ground in assets, relate to the map

1. **Ground in current assets** — the four §3 Grounding fields at milestone scope: **Touches**
   (subsystems/files) · **Context** (docs · config · data) · **Honors** (`PROJECT.md`/
   `CONVENTIONS.md` invariants) · **Anchors** (contracts/symbols tasks cite) — each from real
   assets, never assumed. Record it as the milestone's `## Ground` — gathered ONCE; each task's
   specify PROJECTS its §1 from it. Touches >1 app root (BE+FE)? weigh `.add/components.toml` now.
2. **Relate to the map** — `add.py search <keyword>` first, then read every live + archived goal
   (`.add/milestones/*` · `.add/archive/*`); name the relationship — *extends* X · *depends-on* Y ·
   *overlaps* Z — in the `rationale` line.
3. **Already delivered** by an existing milestone → reject `duplicate_goal`; route as `task` or
   `change-request`.

**Draft the sections well**: goal = ONE outcome sentence (no "and" — that is two milestones) ·
rationale = bucket + WHY + the relationship (never in state.json) · Scope In/Out = an explicit
deferral list (an empty Out means scope is not thought through) · shared decisions/contracts
name the owning task · tasks breadth-first (`slug · depends-on · one line`, each one-file-sized) ·
exit criteria observable, EVERY criterion maps to a declared task slug · `Close — ship review` +
`Release steps` stay drafted-blank (filled at `milestone-done`/release). Brainstorm via the
three-move co-specify (below) at milestone scope; rank assumptions lowest-confidence first (top
1–2 get the ⚠ flag); present per `gate-udd.md` as a guided choice — fix any unmet box first.
Rejects: `not_classified` · `dangling_criterion` · `no_milestone` · `duplicate_goal`.

---

## Rules (§1) + scenarios (§2) — co-specification

State what the feature MUST do and MUST REJECT — zero ambiguity left to guessing. Co-specify in three moves: **Diverge** (surface the 2–3 genuine framings +
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

Every Must and Reject must be checkable — canonically as a §4 test (its `covers:` tag); §2 gherkin is
an OPTIONAL readable projection, added only when a human needs prose cases at the freeze, never as ceremony:

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
- [ ] Every Must and Reject is encoded — a §4 test (canonical) or an optional §2 gherkin scenario;
      every rejection asserts what stays unchanged; edge cases covered or ruled out on purpose.
</exit_gate>

---

## Plan (§3) — ground · freeze the shape · build-strategy

Turn the rules + scenarios into ONE change plan and FREEZE it. Below the freeze code is disposable;
above it the Contract does not move.

### Grounding — reason it in-context (don't write an essay — `PLAN.md.tmpl`: persist the interface, not prose)
Project from the milestone `## Ground`, then deepen only where THIS task lands. Never invent a
file/symbol you have not opened; cite the **symbol**, not a bare line number (`l.NNN` rots; symbols
survive), via code-navigation tools, not memory. A recalled fact — a file, a flag, a symbol, or a
prior lesson (even one carried in from memory) — is **PRIOR until re-confirmed** against the live
tree THIS session; a live read outranks memory, and a safety-grep counts only once you have
confirmed it actually matched (a `for x in $VAR` that ran vacuous proves nothing). **Persist only what the contract needs**: the
**Anchors** it may cite (the specific symbols §3 names — it may cite ONLY these) and, optionally, a
**Ground SHA** (the commit grounded against — the engine stamps it when the line is present).
Everything else — what it **Touches**, the **Honors**/seams consulted, the **Issues/Risks**, the
**Related intent** (the WHY) — you REASON now and let the frozen Contract encode; don't transcribe it
into the file. Sweep BROAD cheaply (skim an index/map; a subagent sweep for unfamiliar ground), then
DEEPEN on what THIS task needs. *Greenfield / first task:* grounding IS the foundation docs — an
honest "new module, no code; honors CONVENTIONS.md §X" is complete.

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
(HARD) + the Build-strategy Scope; then `Status: FROZEN @ v1 — approved by <name>`. Lane modes are
retired — ONE atomic template serves every task; if the header still carries an optional `route:`
line the freeze records it (audit-only — `route_unrecorded` is measured, never a refusal).

<exit_gate>
- [ ] **Grounding** — reasoned in-context; the Contract's **Anchors** resolve in the code; an optional **Ground SHA** recorded (the essay bullets are not persisted — the interface is).
- [ ] **Contract** — versioned, `FROZEN`; contract tests pass against the mock; every name matches the glossary; every §1 rejection has a contracted response.
- [ ] **Build-strategy** — Scope declared; batches + persona + spawn isolation named; a measurable Target set.
- [ ] The Contract cites only Grounding anchors; the ⚠ lowest-confidence flag is surfaced.
</exit_gate>

## The freeze review checklist

The human's one minute, aimed. **Fluent ≠ true** — a bundle's polish tracks its token count, not its
evidence, so these checks force a fresh read of THIS task over a plausible template. Run the **Floor**
first, then walk the rest before saying yes:

- **Floor (before you read the shape)** — the pre-answer check the fluent draft skips. (1) Restate the
  **Goal**: the end-state the human actually wants, in their world, not the ticket's wording — a bundle
  that satisfies the words but misses the goal is the most expensive miss. (2) Check the **Leftovers**:
  every supplied constraint — each PROJECT.md `invariant:`, the BARE declared runtime, every ⚠ the
  interview surfaced — is either encoded in §1–§4 or explicitly waived. An unused constraint is a trap,
  not noise: the artifact must hold under the BARE runtime, so a leftover invariant is a defect already
  waiting at verify.
- **⚠ flags first** — read the lowest-confidence flags; accept each knowing its cost if wrong. The engine refuses an unflagged freeze before build (`unflagged_freeze`).
- **Intent** — does §1 say what you actually want built?
- **Cases** — does every Must and Reject have an observable §2 scenario?
- **Shape** — glossary names, error codes, additive vs breaking: is THIS the shape to freeze?
- **Shape self-verify (the constraint loop)** — for the mechanically-checkable output-shape rules — the
  frozen §3 tag census (the closed XML vocabulary), the §5 Scope path tokens, each §4 `covers:` key, any
  REDS / dangling refs — don't eyeball them: expand the rule, self-verify the draft **mechanically**
  (grep/count in reasoning space, not a re-read), repair, THEN freeze. This is where the freeze-parser
  self-breaks get caught before the engine does — a bare `<word>` colliding with the tag census, a
  `./src/` scope token tripping `scope_violation`.
- **Grounded** — does the Contract cite anchors that exist in the Grounding map? `status`/`check` surface this.
- **Risk** — high-risk or method-defining? Require `risk: high · autonomy: conservative` in the PLAN.md header.
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
coverage target.

**Non-coding task?** For `kind: docs · release · infra` (or a wholly non-coding project) the
check need not be a script: §4 is a failing-first **acceptance check** — verifiable pass/fail
evidence (renders · every internal link resolves · `§X covers A/B/C` · a command exits 0), red
before the artifact exists and green after. Declare `Tests live in: evidence`. Red→green still
binds; only the must-be-executable-code requirement is lifted (the human may declare acceptance
mode on any task). Coding kinds keep the executable red suite above.

## Declaring where tests live

§4's `Tests live in:` line is machine-read — declare paths as backticked tokens on that line: with
no local `tests/`, `add.py report` counts test functions at the declared paths (FIRST such line only).
REPLACE the template's `./tests/` placeholder in place — never append a SECOND `Tests live in:` line:
the report reads the FIRST, so a stale default left above your real path silently wins.
`./…` → this task dir · a token with `/` → the project root · a bare name → a
sibling of the previous token's dir. A directory counts its `*.py` files
(non-recursive); a `.py` file counts itself. Resolved files dedupe; declared counts
marked `†`. Paths are confined: outside the project root counts 0 — `..` traversal,
absolute paths, and symlink escapes are never read.

**Clause map + edges.** Fill each `<test_plan>` bullet's `covers:` tail — frozen with the
bundle; `add.py locate path::test_x` walks a failure → owning node → that frozen §3 clause.
Declare edges at creation (`--depends-on`, later `relate`; milestone-confirm compiles `## Tasks`
rows into inherited edges) — `locate <slug>` names who re-verifies when a settled contract
moves. Ground §3 on each parent edge's frozen §3 — the PLAN.md itself, never a summary or
built code.

<exit_gate>
- [ ] One test (or acceptance check, for a non-coding kind) per scenario, red for the right reason, asserting observable behavior; coverage target recorded.
</exit_gate>

> **Persona / Advisor / Confidence** — load the domain-fit `.add/personas/<slug>.md` (its Critical
> Rules shape §1, its Success Metrics shape the red suite; advisory, never lowers a gate). If none
> fits, spawn the add agent in persona mode to seed one (PROJECT.md + `.add/personas-teacher/`),
> then load it — seed per DOMAIN, REUSE across tasks, never one per task. Canonical spawns:
> researcher (unfamiliar domain) · risky-shape second opinion · test-author for a wide suite (the
> advisor spawn — `phases/verify.md`); self-score the bundle below — the lowest dimension aims ⚠.

## The confidence self-score

Before presenting ANY drafted artifact (spec · contract · bundle · subagent verdict), self-score
it 0–1 on six dimensions: **Completeness** (every rule/scenario/rejection covered?) · **Clarity**
(understood without you in the room?) · **Practicality** (implementable against the real code?) ·
**Optimization** (correctness/simplicity/cost balanced — no gold-plating, no corner cut?) ·
**Edge cases** (failure modes, concurrency, empty/oversized inputs named?) · **Self-evaluation**
(does it carry its own refine step?). Rank the six worst→best (a model ranks far more reliably than
it calibrates an absolute), then NAME the one concrete deficiency in your weakest dimension — a
missing scenario, an unhandled input, not a number — and fix THAT before presenting; re-rank after.
The lowest dimension is what you surface ⚠-first at the freeze; persistently low on risky scope →
*recommend* lowering autonomy (the level stays the human's call). The self-score is a **weak signal**:
the load-bearing correctness check is the adversarial refute-read (`phases/verify.md`) — the
plausible-but-wrong a self-score waves through is exactly what the refute exists to catch.
The hard rule: **advisory, never a gate** — it never auto-passes a verify, never substitutes for evidence or the
human decision, and a self-asserted score is never recorded as something the human "agreed to".

Book: `docs/03-step-1-specify.md` · `docs/05-step-3-plan.md` · `docs/06-step-4-tests.md` · `docs/10-setup-and-stages.md`.
