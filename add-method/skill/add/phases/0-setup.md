# Phase 0 — Setup (autonomous draft → one human baseline approval)

Goal: point ADD at a repo and **you** draft the whole foundation — domain, first-milestone scope, and the first task's contract — then hand the human one decision: the **baseline approval**. Brownfield is silent; greenfield keeps a short interview. Either way, the human's only gate is `add.py lock`.

## 1 · Zero-touch entry — you run init yourself

When there is no `.add/state.json`, do **not** tell the human to initialise — run it yourself. Infer the
project name and stage from the repo, and **arm the baseline-approval gate** with `--await-lock`:

```bash
python3 .add/tooling/add.py init --name "<inferred from repo/dir>" --stage <prototype|poc|mvp|production> --await-lock
```

- `--await-lock` seeds an *unlocked* setup — the engine refuses crossing into build or calling `gate` until you `lock`. A plain `init` is grandfathered-locked; its closing `lock` would error `already_locked`.
- name + stage are **your judgment** (read from the dir name, README, manifests): throwaway → `prototype`, risky slice → `poc`, narrow-but-real → `mvp`, full rigor → `production`.

`init` prints one of two things — **that is your branch**:
- `brownfield:` → existing code (go to **2a**);
- no `brownfield:` → empty repo (go to **2b**).

## 2a · Brownfield — map it silently

The code answers the questions a greenfield interview would ask — **read it instead of asking**. Open `adopt.md` and follow it: fill each living-doc file from the code, never clobber an existing one, tag every decision `evidence-grounded` or `guessed`. Ask the human **nothing** at this step.

## 2b · Greenfield — the 4-lens interview (kept): co-specify at foundation level

An empty repo has no code to read, so run the short interview. This is the **co-specify at foundation
level** move — diverge → converge → validate, as a task's §1 uses (`phases/1-specify.md`), lifted to the foundation. Ask the one load-bearing question per lens, draft, then rank lowest-confidence-first and show the top flag:

| Lens | The one question that unblocks the section |
|------|--------------------------------------------|
| Domain (DDD) | The 3–5 core nouns, and the one invariant that must NEVER break? |
| Spec (SDD) | The first milestone's outcome — and what's explicitly NOT in v1? |
| Users (UDD) | The primary user and the one job they hire this for? (or "no UI — surface is X") |
| Decisions | What's already decided that you'd regret re-litigating? (first Key Decision row) |

Ask only the live ones. Rank: `⚠ <assumption> — lowest confidence because <why>; if wrong: <cost>` — tag thin answers `guessed`.

## 2c · Domain deep-dive — per-drive, across multiple turns (deepens §2b)

| Drive | Deepen |
|-------|--------|
| **DDD** (domain) | core nouns → model: entities, invariants, bounded edges |
| **SDD** (spec) | milestone outcome → behaviors and explicit non-goals |
| **UDD** (users) | primary user → jobs, surface, the one flow that must feel right |
| **TDD** (trust) | what "done & trusted" means: risks to prove, evidence that closes them |

Capture each surfaced decision as an **ADR** into `PROJECT.md` **Key Decisions** as it lands.

**Under `autonomy: auto` with full context, auto-complete all four drives in one pass** — lowest-confidence-first, surfacing the top flag. This deepens **drafting**, never the gate: auto-complete NEVER skips the human baseline approval — the `lock` stays the one decision.

## 3 · Draft to the lock (both paths)

1. **Fill the living documentation**: `.add/PROJECT.md` (Domain · Spec/active milestone · UI/UX · Key Decisions), `CONVENTIONS.md`, `GLOSSARY.md`, `MODEL_REGISTRY.md`, `dependencies.allowlist`, and — for a UI project — `DESIGN.md` (delete if no UI; design loop: `design.md`). Brownfield: from code. Greenfield: from interview, gaps flagged `guessed`.
2. **Propose, then size it.** Float a **kickoff suggestion** for the first milestone: a **goal** (one outcome sentence), a **flow** (task order), and **scenarios** (concrete examples of what ships). Not the frozen `MILESTONE.md`. On their reaction, draft `MILESTONE.md` (read `scope.md`).
3. **Create the first task and draft its candidate specification bundle.** `new-task` is allowed pre-lock:
   ```bash
   python3 .add/tooling/add.py new-task <slug> --title "<first feature>"
   ```
   Draft the full bundle **§1–§4** — incl. the **§4 red suite** (`phases/4-tests.md`); the lock approves it whole. **Leave §3 `Status: DRAFT`** — the lock is its approval. You MAY `advance` pre-lock, but the engine **refuses crossing into build** until you `lock` (`setup_unlocked`). Sequence: **bundle (§1–§4, tests RED) → lock → build** — the red suite must FAIL **before build** (never start Build until §1–§4 exist and tests are red).
4. **Write `.add/SETUP-REVIEW.md`** per `setup-review.md`: every drafted decision, **lowest-confidence-first**, tagged `guessed` | `evidence-grounded`.

## Run mode — how the build will be driven (propose parallel + auto; confirm to keep)

Before the lock, surface the **run mode** — **autonomy** (`add.py autonomy`, run.md) and **streams** (`add.py waves` + `streams.md`):

| Run mode | Human gates | Concurrency |
|----------|-------------|-------------|
| **sequential · manual/conservative** | contract freeze **and** every Verify | one task at a time; safest, slowest |
| **parallel · auto** *(proposed default)* | contract freeze **only** — Verify auto-PASSes on complete evidence | `add.py waves` schedules independent tasks; builds overlap behind frozen contracts |

**Propose `parallel + auto`, ask the human to confirm-to-keep** (or downgrade: `add.py autonomy set conservative --project`). Record the chosen mode in **`PROJECT.md` Key Decisions**.

The irreducible floor: **one human approval per contract** fires no matter the mode.

## 4 · The one human gate — the baseline approval

Open the report with the ARC per `report-template.md`, render the DECISION as a guided choice, then present `SETUP-REVIEW.md` lowest-confidence-first. They confirm **once** — an explicit yes to the baseline approval itself; ambient mid-stream agreement is not a confirmation. On that recorded confirmation, you run the lock:

```bash
python3 .add/tooling/add.py lock --by "<name>"
```

Typing it themselves stays the **escape hatch** — the decision is always the human's; you just execute it. `lock` records the lock layers in one atomic write and opens the build.

## 5 · After the lock

- The lock **is** the first task's contract approval — do **not** ask for a separate contract-freeze sign-off.
- Stamp the first task's §3 `Status: FROZEN @ v1`, then read `phases/5-build.md`.

## Exit gate

<exit_gate>
- [ ] `.add/state.json` exists; setup was seeded unlocked (`--await-lock`) then locked.
- [ ] Living docs filled (brownfield: from code, tagged evidence-grounded; greenfield: from the interview).
- [ ] First task created; **§1–§4 drafted — the red suite (per `phases/4-tests.md`) runs RED before build opens**; `.add/SETUP-REVIEW.md` written lowest-confidence-first.
- [ ] Human confirmed the baseline approval and `add.py lock --by` ran with their name; first task §3 `FROZEN @ v1`; build open.
</exit_gate>

## Next

After the lock, read `phases/5-build.md` (build is open). Book: `docs/10-setup-and-stages.md`.
