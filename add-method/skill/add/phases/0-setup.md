# Phase 0 — Setup (autonomous draft → one human baseline approval)

Goal: point ADD at a repo and **you** draft the whole foundation — domain, first-milestone scope,
and the first task's contract — then hand the human exactly one decision: the **baseline approval**. Brownfield
is silent (the code answers the questions); greenfield keeps a short interview. Either way, the human's
only gate is `add.py lock`. This is the setup-level analog of a task's one-approval contract freeze.

## 1 · Zero-touch entry — you run init yourself

When there is no `.add/state.json`, do **not** tell the human to initialise — run it yourself. Infer the
project name and stage from the repo, and **arm the baseline-approval gate** with `--await-lock`:

```bash
python3 .add/tooling/add.py init --name "<inferred from repo/dir>" --stage <prototype|poc|mvp|production> --await-lock
```

- `--await-lock` is **required** here: it seeds an *unlocked* setup, which arms the gate so the engine
  refuses a second task / crossing into build / a `gate` until you `lock`. A plain `init` is
  grandfathered-locked — its gate never arms, and the closing `lock` would error `already_locked`.
- name + stage are **your judgment** (read them from the dir name, README, manifests); the engine stays
  mechanical. Pick the stage from the ambition you hear: throwaway → `prototype`, one risky slice → `poc`,
  narrow-but-real → `mvp`, full rigor → `production`.

`init` prints one of two things — **that is your branch**:
- a line starting `brownfield:` → there is existing code (go to **2a**);
- the greenfield closing (no `brownfield:`) → an empty repo (go to **2b**).

## 2a · Brownfield — map it silently

The code answers the questions a greenfield interview would ask, so **read it instead of asking**. Open
`adopt.md` and follow it: fill each living-doc file from the code, never clobber an existing one, and tag
every decision `evidence-grounded` (cite the file) or `guessed`. Ask the human **nothing** at this step.

## 2b · Greenfield — the 4-lens interview (kept): co-specify at foundation level

An empty repo has no code to read, so run the short interview. This is the **co-specify at foundation
level** move — the same diverge → converge → validate brainstorm a task's §1 uses (`phases/1-specify.md`),
lifted to the foundation. Ask the one load-bearing question per lens (diverge), draft the foundation
(converge), then rank where your confidence is lowest and show the top flag first (validate):

| Lens | The one question that unblocks the section |
|------|--------------------------------------------|
| Domain (DDD) | The 3–5 core nouns, and the one invariant that must NEVER break? |
| Spec (SDD) | The first milestone's outcome — and what's explicitly NOT in v1? |
| Users (UDD) | The primary user and the one job they hire this for? (or "no UI — surface is X") |
| Decisions | What's already decided that you'd regret re-litigating? (first Key Decision row) |

Ask only the live ones; skip what the request already answers. Rank your drafts lowest-confidence-first using the
one notation every scope level shares — `⚠ <assumption> — lowest confidence because <why>; if wrong: <cost>` — and
tag thin or inferred answers `guessed`.

## 2c · Domain deep-dive — per-drive, across multiple turns (deepens §2b)

§2b gets a foundation from one question per lens; this step DEEPENS it across **multiple
turns**, one deep-dive per **drive** — naming all four, including the one §2b's lens list omitted:

| Drive | Deepen |
|-------|--------|
| **DDD** (domain) | core nouns → model: the entities, the invariants, the bounded edges |
| **SDD** (spec) | the milestone outcome → the behaviors and the explicit non-goals |
| **UDD** (users) | the primary user → the jobs, the surface, the one flow that must feel right |
| **TDD** (trust) | what "done & trusted" means: the risks to prove, the evidence that closes them |

Capture each surfaced decision as an **ADR** (architecture decision record) into `PROJECT.md`
**Key Decisions** as it lands — the Decisions lens becomes explicit ADR capture (the *why*, not just the *what*).

**Under `autonomy: auto` with full context, auto-complete all four drives in one pass** — draft
each without stopping to interview, still lowest-confidence-first, surfacing the top **flag**. Ask
only the live drives; skip what the request already answered. This deepens **drafting**, never the
gate: auto-complete NEVER skips the human baseline approval — the `lock` (§4) stays the one decision.

## 3 · Draft to the lock (both paths)

1. **Fill the living documentation** (it outlives all code): `.add/PROJECT.md` (the foundation — Domain · Spec/active
   milestone · UI/UX · Key Decisions, one screen), `CONVENTIONS.md`, `GLOSSARY.md`, `MODEL_REGISTRY.md`,
   `dependencies.allowlist`, and — for a UI project — `DESIGN.md` (the design source of truth: identity ·
   principles · screens · the named-set foundation pointers + render recipe; delete it if there's no UI;
   the design-definition loop that fills it — domain → components → wireframe → a captured screen confirmed before build — is `design.md`), and — for an
   AI feature — `AI-SPEC.md` (the eval source of truth: success metric · adaptation rung · the `.add/ai/` named-set pointers; delete it if there's no AI feature;
   the eval-definition loop that fills it — spec → ladder → eval-set → freeze-the-contract — is `ai.md`).
   Brownfield: from the code. Greenfield: from the interview, gaps flagged `guessed`.
2. **Propose, then size it.** You just read the codebase (brownfield) or interviewed (greenfield) — so
   don't silently draft. First float a **kickoff suggestion** for the first milestone the human reacts to:
   a **goal** (one outcome sentence), a **flow** (the breadth-first task order that gets there), and
   **scenarios** (concrete examples of what the user can DO once it ships). Keep it a lightweight react-to
   sketch — a few bullets, NOT the frozen `MILESTONE.md` or per-task §2 suites. This is show-before-ask:
   the human reacts (confirm / adjust / redirect); you do not auto-create. On their reaction, draft its
   `MILESTONE.md` (read `scope.md`) — goal · scope · exit criteria · breadth-first tasks.
3. **Create the first task and draft its candidate specification bundle.** `new-task` is allowed pre-lock:
   ```bash
   python3 .add/tooling/add.py new-task <slug> --title "<first feature>"
   ```
   Draft §1 (specify) · §2 (scenarios) · §3 (contract). **Leave §3 `Status: DRAFT`** — the lock is its
   approval (see §5). You MAY `advance` through specify → scenarios → contract → tests pre-lock, but the
   engine **refuses crossing into build** until you `lock` (`setup_unlocked`). Sequence: bundle → lock → build.
4. **Write `.add/SETUP-REVIEW.md`** per `setup-review.md`: every decision you drafted (foundation, scope,
   first contract), **lowest-confidence-first**, each tagged `guessed` | `evidence-grounded`.

## Run mode — how the build will be driven (propose parallel + auto; confirm to keep)

Before the lock, surface ONE more choice so the human is aware of how ADD will drive the build:
the **run mode**. Two settings compose it — the **autonomy** level (`add.py autonomy`, run.md: who owns
the verify gate) and **streams** (`add.py waves` + `streams.md`: whether independent tasks pipeline).
Show this table so the human sees the flow behavior of each, then PROPOSE the default:

| Run mode | Human gates that fire | Concurrency / flow behavior |
|----------|-----------------------|-----------------------------|
| **sequential · manual/conservative** | the contract freeze **and** every Verify, one task at a time | one task start-to-finish before the next; safest, slowest; the reviewer waits on each build |
| **parallel · auto** *(proposed default)* | the contract freeze **only** — Verify auto-PASSes on complete evidence (security/residue still escalate) | `add.py waves` schedules independent tasks into waves; builds overlap behind their frozen contracts while you review one bundle; the reviewer is never blocked on a build |

**Propose `parallel + auto` as the default, and ask the human to confirm-to-keep** (or downgrade in
one step — `add.py autonomy set conservative --project`, or just run tasks one at a time). This is a
confirm, never a silent flip. Record the chosen mode in **`PROJECT.md` Key Decisions** (e.g. "run mode:
parallel + auto (opt-out), confirmed by <name>") so every later session inherits it.

What the default does **not** change: the irreducible floor still holds — **one human approval per
contract** fires no matter the mode. `auto` + `parallel` change the *order and throttle* of the build
(which tasks run when, and who gates Verify), never *whether* the contract decision point fires. A
high-risk task still refuses `auto` and forces a lowered rung (run.md guard).

## 4 · The one human gate — the baseline approval

Open the report with the ARC (goal · done · plan) per `report-template.md`, render the baseline-lock DECISION as a guided choice (the recommended pick + described alternatives), then present
`SETUP-REVIEW.md` lowest-confidence-first (the `guessed` rows are what the human must actually check). They
confirm **once** — an explicit yes to the baseline approval itself, in conversation; ambient agreement mid-stream is
not a confirmation. On that recorded confirmation, you run the lock with their name:

```bash
python3 .add/tooling/add.py lock --by "<name>"
```

Typing the command themselves stays the **escape hatch** — the decision is always the human's; you just
execute it. `lock` records the lock layers (foundation · scope · contract) in one atomic write and opens the
build. It is judgment-free — it does **not** parse `SETUP-REVIEW.md`; the human *reading* it is the review.

## 5 · After the lock

- The lock **is** the first task's contract approval — the v7 specification-bundle approval and the baseline approval collapse
  into this single signature. Do **not** ask for a separate contract-freeze sign-off (that double-gates).
- Stamp the first task's §3 `Status: FROZEN @ v1` (lock-authorized), then read `phases/5-build.md` — build is
  now open. Everything before this signature, you drafted.

## Exit gate

<exit_gate>
- [ ] `.add/state.json` exists; setup was seeded unlocked (`--await-lock`) then locked.
- [ ] Living docs filled (brownfield: from code, tagged evidence-grounded; greenfield: from the interview).
- [ ] First task created; §1–§3 drafted; `.add/SETUP-REVIEW.md` written lowest-confidence-first.
- [ ] Human confirmed the baseline approval and `add.py lock --by` ran with their name; first task §3 `FROZEN @ v1`; build open.
</exit_gate>

## Next

After the lock, read `phases/5-build.md` (build is open). · Book: `docs/10-setup-and-stages.md`
*(note: book chapters 10 / 13 / 14 still describe the older human-led setup until `book-align` lands).*
