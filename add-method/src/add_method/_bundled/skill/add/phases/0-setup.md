# Phase 0 — Setup (autonomous draft → one human baseline approval)

Goal: point ADD at a repo and **you** draft the whole foundation — domain, first-milestone scope, first task's contract — then hand the human one decision: the **baseline approval**. Brownfield silent; greenfield keeps a short interview; either way the only gate is `add.py lock`.

## 1 · Zero-touch entry — you run init yourself

No `.add/state.json`? Don't tell the human to initialise — run it yourself. Infer name + stage
from the repo and **arm the baseline-approval gate** with `--await-lock`:

```bash
python3 .add/tooling/add.py init --name "<inferred from repo/dir>" --stage <prototype|poc|mvp|production> --await-lock
```

- `--await-lock` seeds an *unlocked* setup — the engine refuses build or `gate` until you `lock`. A plain `init` is grandfathered-locked (`already_locked` on a later `lock`).
- name + stage are **your judgment**: throwaway → `prototype`, risky slice → `poc`, narrow → `mvp`, full rigor → `production`.

`init` prints one of two things — **that is your branch**:
- `brownfield:` → existing code (go to **2a**);
- no `brownfield:` → empty repo (go to **2b**).

## 2a · Brownfield — map it silently

The code answers what a greenfield interview would ask — **read it instead of asking**. Open `adopt.md`: fill each living-doc from code, never clobber, tag every decision `evidence-grounded` or `guessed`. Ask the human **nothing** here.

## 2b · Greenfield — the 4-lens interview (kept): co-specify at foundation level

An empty repo has no code, so run the short interview — the **co-specify at foundation level** move
(diverge → converge → validate, as §1 does in `phases/1-specify.md`), lifted to the foundation. Ask one load-bearing question per lens, draft, rank lowest-confidence-first, show the top flag:

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

Capture each surfaced decision as an **ADR** in `PROJECT.md` **Key Decisions** as it lands.

**Under `autonomy: auto`, auto-complete all four drives in one pass** — lowest-confidence-first. This deepens **drafting**, never the gate — `lock` stays the one decision.

## 3 · Draft to the lock (both paths)

1. **Fill the living documentation**: `.add/PROJECT.md` (Domain · Spec · UI/UX · Key Decisions), `CONVENTIONS.md`, `GLOSSARY.md`, `MODEL_REGISTRY.md`, `dependencies.allowlist`, and — for a UI project — `DESIGN.md` (delete if no UI; `design.md`). Brownfield: from code. Greenfield: from interview, gaps flagged `guessed`.
   - **Seed personas** (`.add/personas/`): `init` scaffolds `_template.md` (the schema). **Author one per role** from PROJECT.md + the vendored teacher library `.add/personas-teacher/` (read off-build; engine never fetches) — citing the teacher in `source:` and carrying its top `## Playbook` are the two optional parts, not the authoring. Covered by the **baseline approval**; `add.py check` validates; never clobber.
2. **Propose, then size it.** Float a **kickoff suggestion** for the first milestone: a **goal** (one sentence), a **flow** (task order), **scenarios** (examples of what ships). Not the frozen `MILESTONE.md`. On their reaction, draft `MILESTONE.md` (read `scope.md`).
3. **Create the first task and draft its candidate specification bundle.** `new-task` is allowed pre-lock:
   ```bash
   python3 .add/tooling/add.py new-task <slug> --title "<first feature>"
   ```
   Draft the full bundle **§1–§4** incl. the **§4 red suite** (`phases/4-tests.md`); the lock approves it whole. **Leave §3 `Status: DRAFT`** — the lock is its approval. You MAY `advance` pre-lock, but the engine **refuses build** until you `lock` (`setup_unlocked`). Sequence: **bundle (§1–§4, tests RED) → lock → build** — the red suite must FAIL before build.
4. **Write `.add/SETUP-REVIEW.md`** per `setup-review.md`: every drafted decision, **lowest-confidence-first**, tagged `guessed` | `evidence-grounded`.

## Run mode — how the build will be driven (propose parallel + auto; confirm to keep)

Before the lock, surface the **run mode** — autonomy + streams (`run.md` · `streams.md`):

| Run mode | Human gates | Concurrency |
|----------|-------------|-------------|
| **sequential · manual/conservative** | contract freeze **and** every Verify | one task; safest |
| **parallel · auto** *(default)* | contract freeze **only** — Verify auto-PASSes on evidence | `add.py waves` overlaps independent builds behind frozen contracts |

**Propose `parallel + auto`; confirm-to-keep** (or downgrade: `add.py autonomy set conservative --project` + `add.py streams set sequential --project`). Record in **`PROJECT.md` Key Decisions**.

Floor: **one human approval per contract**.

## 4 · The one human gate — the baseline approval

Open the report with the ARC per `report-template.md`, render SHAPE then APPROVE as a guided choice, then present `SETUP-REVIEW.md` lowest-confidence-first. They confirm **once** — an explicit yes; ambient agreement is not a confirmation. **Never self-stamp a timeout — hold, or re-ask.** On that recorded confirmation, you run the lock:

```bash
python3 .add/tooling/add.py lock --by "<name>"
```

Typing it themselves stays the **escape hatch** — the decision is the human's; you execute. `lock` writes the lock layers atomically and opens the build.

## 5 · After the lock

- The lock **is** the first task's contract approval — no separate contract-freeze sign-off.
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
