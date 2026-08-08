# TASK: Rewrite phase-0 + SKILL routing; zero-touch entry + chain v7 front to first contract

slug: autonomous-setup-guide · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- high-risk: method/trust-layer scope; `auto` refused (unguarded_high_risk_auto). Front seam released by the human for the v12 tail — I self-freeze §3 and STOP at verify. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: rewrite `phases/0-setup.md` + update `SKILL.md` routing so setup is AUTONOMOUS: when there is no
`.add/state.json`, the AI runs `init --await-lock` ITSELF (zero-touch entry), branches on the brownfield
signal (→ adopt.md silent map / → greenfield 4-lens interview), drafts the foundation + first-milestone scope
+ the first task's candidate §1–§3, writes `.add/SETUP-REVIEW.md` (per setup-review.md), and ends at the ONE
human gate — `add.py lock`. The lock IS the first task's contract approval (the v7 one-approval-front and the
lock-down collapse into the same signature). Pure PROSE: it wires tasks 1–3's shipped pieces into one flow.

Framings weighed: prose-guide-rewrite (chosen) · engine-driven-wizard · new-onboarding-command
  - chosen: rewrite the two guides (0-setup.md + SKILL.md routing); the engine pieces already exist
    (init brownfield-detect + `--await-lock` from tasks 1–2, `lock` + build-boundary gate from task 1,
    setup-review.md + adopt.md from tasks 2–3). Task 4 only describes the flow that drives them.
  - engine-driven-wizard (rejected): an `add.py setup` command that walks the steps — injects flow judgment
    into the engine; ADD keeps `add.py` judgment-free (the human signature is the gate, task 1's invariant).
  - new-onboarding-command (rejected): a separate entry command — duplicates `init`; the milestone says
    `init` is the entry and is AI-invokable.

Must:
  - `0-setup.md` prescribes ZERO-TOUCH ENTRY: when there is no `.add/state.json`, the AI runs init itself —
    `python3 .add/tooling/add.py init --name "<inferred>" --stage <prototype|poc|mvp|production> --await-lock`.
    `--await-lock` is REQUIRED (arms the lock-down gate; a plain init is grandfathered-locked — the adopt.md
    lesson). Name + stage are AI JUDGMENT (inferred from the repo/dir); the engine stays mechanical.
  - `0-setup.md` BRANCHES on init's output: a `brownfield:` signal → route to `adopt.md` (silent map, ZERO
    questions); no signal (greenfield) → run the 4-lens interview (KEPT), then draft.
  - `0-setup.md` draws the DRAFT-TO-LOCK sequence both paths share: fill survivors → size first milestone
    (scope.md) → `new-task <slug>` (allowed pre-lock) → draft the first task's §1–§3 candidate front →
    write `.add/SETUP-REVIEW.md` (per setup-review.md, least-sure-first, tagged) → present → human `lock`.
  - `0-setup.md` states the COLLAPSE explicitly: for the first task the lock IS the contract approval — do
    NOT seek a separate contract-freeze sign-off (that would double-gate the human). §3 stays DRAFT pre-lock;
    after the human locks, the AI stamps §3 `FROZEN @ v1` (lock-authorized) and crosses into build.
  - `0-setup.md` honors task 1's build-boundary gate: the AI MAY advance specify→…→tests pre-lock but the
    engine REFUSES crossing into build until `lock` (`setup_unlocked`). The guide sequences front → lock → build.
  - `SKILL.md` routing updated: the "No `.add/` yet" bullet sends the AI to run `init --await-lock` itself then
    enter autonomous setup; the flow-table `setup` row's "who leads" becomes "AI drafts → human locks".
  - `0-setup.md` + `SKILL.md` are byte-identical across canonical + dogfood + bundle skill trees.

Reject:
  - none material — PROSE wiring of shipped engine pieces; cannot fail at runtime. Biggest risk = the guide
    prescribing a command the engine refuses (the adopt.md defect class). Mitigated: the zero-touch `init`
    command was verified to run without `--name` (infers it); `--await-lock` + build-boundary sequence checked
    against task 1's frozen gates. Flagged ⚠ below.

After:
  - Pointing ADD at a repo with no `.add/` makes the AI init + draft autonomously to a single `lock`; brownfield
    is silent, greenfield keeps the interview; the first task's §3 is FROZEN at the lock; the two guides ship
    byte-identical in all three trees.

Assumptions — least-sure first:
  ⚠ [spec] RESUME GAP (disclosed, OUT of scope): after `init --await-lock` (pre-lock), `add.py status` prints
    "you're set up — run /add", NOT "review SETUP-REVIEW.md, then lock". A session resuming mid-setup would not
    know to lock. Least sure whether to fix now: fixing = a `cmd_status` change behind task 1's FROZEN+PASSED
    engine (a change-request to task 1). Chose to DISCLOSE as a follow-up, not expand task 4. Cost if deferred:
    a single interrupted onboarding could miss the lock; cost if fixed here: re-opens the frozen engine.
  - [ ] book inconsistency is EXPECTED until task 5: `0-setup.md` points at `docs/10-setup-and-stages.md`, which
    still describes the old human-led flow until `book-align` (task 5, deps on this). Not a defect at this gate.
  - [ ] the AI marks §3 `FROZEN @ v1` post-lock (no engine field flips it) — confirmed against task 1 (grep
    `contract_locked` → none); the freeze is artifact-observable + the setup `contract` lock layer.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: 0-setup.md + SKILL.md ship byte-identical in every skill tree
  Given the repo
  Then each file is identical across canonical, dogfood (.claude/skills/add), and bundle (_bundled/skill/add)
  (asserted by test_tree_parity + test_bundle_parity — editing canonical alone turns them RED via md5
   DIVERGENCE, not orphan, since both files already exist in all trees; syncing turns them GREEN.)

Scenario: zero-touch entry prescribes a command that actually runs (human-read + verified)
  Given a repo with no .add/state.json
  Then 0-setup.md tells the AI to run `init --name "<inferred>" --stage <picked> --await-lock` itself
  And that command was verified to succeed (init runs without an explicit --name; --await-lock arms the gate)

Scenario: the brownfield/greenfield branch routes correctly (human-read, prose)
  Given init printed a `brownfield:` signal
  Then 0-setup.md routes to adopt.md (silent, zero questions)
  Given no signal (greenfield)
  Then 0-setup.md runs the 4-lens interview, then drafts

Scenario: the collapse does not double-gate the human (cross-task consistency, human-read)
  Given the first task's §1–§3 are drafted and SETUP-REVIEW.md is presented
  Then 0-setup.md says the single `add.py lock` IS the contract approval (no separate freeze sign-off)
  And §3 stays DRAFT pre-lock, becomes FROZEN @ v1 after the human locks

Scenario: the guide never prescribes crossing into build before lock (cross-task, honors task 1's gate)
  Given setup is unlocked (pre-lock)
  Then 0-setup.md sequences front → SETUP-REVIEW → lock → build
  And it notes the engine REFUSES build/advance-into-build until lock (`setup_unlocked`)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable (parity by test, the flow by human read + the verified command). -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# two PROSE guides (gated by parity + human read, NO new unit test; TDD binds only where there is code.
#   Red→green IS the parity guard: edit canonical -> md5 DIVERGENCE -> test_tree_parity/_bundle_parity RED -> sync 3 trees -> GREEN.)

phases/0-setup.md  — REWRITTEN to the autonomous flow:
  1. Zero-touch entry (no .add/state.json) — AI runs:
       add.py init --name "<inferred>" --stage <prototype|poc|mvp|production> --await-lock
     (--await-lock REQUIRED: arms the lock-down gate; name/stage are AI judgment)
  2. Branch on init output: `brownfield:` -> adopt.md (silent) | greenfield -> 4-lens interview (KEPT)
  3. Draft-to-lock (both): fill survivors -> scope first milestone -> new-task <slug> (allowed pre-lock)
     -> draft first task §1–§3 (candidate; §3 stays DRAFT) -> write .add/SETUP-REVIEW.md (per setup-review.md)
  4. ONE human gate: present SETUP-REVIEW.md least-sure-first -> human `add.py lock --by "<name>"`
  5. Post-lock: AI stamps first task §3 `FROZEN @ v1` (lock-authorized) -> build opens (gate lifts)
  COLLAPSE: the lock IS the first task's contract approval — no separate contract-freeze sign-off.
  BUILD-BOUNDARY (task 1): advance specify→tests allowed pre-lock; build refused until lock (`setup_unlocked`).

SKILL.md  — routing updated:
  - "No `.add/` yet" bullet -> AI runs `init --await-lock` itself, then enters autonomous setup (0-setup.md)
  - flow-table `setup` row "who leads": `human` -> `AI drafts → human locks`

Synced (BOTH files): .claude/skills/add/ + src/add_method/_bundled/skill/add/  (byte-identical, all 3 trees)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- self-frozen 2026-06-04: the human released the front seam for the v12 tail; the least-sure flag (the disclosed status resume gap) is carried to the verify gate. -->
<!-- Least-sure flag for the gate: the status resume gap (post-init/pre-lock, `status` doesn't point at lock) —
     disclosed as an out-of-scope follow-up, NOT fixed here (would re-open task 1's frozen+passed engine). -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + least-sure flag surfaced. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: prose guides — NO new unit test (TDD binds where there is code). The red→green safety net is
the EXISTING parity pair: `test_tree_parity` + `test_bundle_parity`. Because `0-setup.md` and `SKILL.md` ALREADY
exist in all three trees, editing canonical alone turns the pair RED via md5 DIVERGENCE (not an orphan); syncing
BOTH files to the dogfood + bundle trees turns them GREEN. That divergence→sync is the documented red→green.
No new test file (asserting prose content would be the over-testing the method warns against).

Tests live in: (existing) `add-method/tooling/test_tree_parity.py` + `test_bundle_parity.py` · MUST be RED
(md5 divergence on the edited canonical files) before the sync, GREEN after.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason (divergence); target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): PROSE; no code, no new imports, no engine change. The guide must prescribe only
commands verified to run (zero-touch `init --await-lock` checked) and must not describe any `lock`/gate behavior
beyond task 1's frozen contract. Both files (0-setup.md + SKILL.md) sync to all THREE trees — md5 divergence on
SKILL.md's `_bundled/` copy is an easy miss; verify all three.
Code lives in: `add-method/skill/add/phases/0-setup.md` + `add-method/skill/add/SKILL.md`
  → synced to `.claude/skills/add/...` + `src/add_method/_bundled/skill/add/...` (both files, all 3 trees).
Constraints: no code; do NOT touch the engine or any test; keep all three trees byte-identical for BOTH files.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `Ran 322 tests … OK` (318 + installer-arm's 4); `test_tree_parity` +
      `test_bundle_parity` confirm 0-setup.md + SKILL.md byte-identical across all three trees
      (md5-divergence→sync red→green completed, twice: the guide rewrite, then the SKILL.md keying fix below).
- [x] coverage did not decrease — prose; the parity pair re-verifies both edited files in all trees;
      `test_cospecify_lift` re-verifies 0-setup.md's foundation-interview invariants (4 lenses, anchor, flag grammar).
- [x] no test or contract was altered during build — §3 frozen; NO test modified or weakened; NO engine change
      (add.py md5 unchanged at `7174a4cf…`). CROSS-TASK COLLISION (disclosed): the rewrite first DROPPED three
      v5 `cospecify-lift` invariants 0-setup.md must keep (the `co-specify at foundation altitude` anchor, the
      `phases/1-specify.md` reference, the verbatim `⚠ … least sure because … if wrong:` flag grammar) → 3 RED in
      `test_cospecify_lift`. Fixed by RESTORING all three into the greenfield 4-lens section — the guard is correct;
      I honored it (did NOT touch the test). Re-synced; green.
- [x] concurrency / timing safe — n/a (no code; static markdown guides; no state writes).
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no imports, no eval, no secrets.
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree md5 parity (0-setup.md `a11e2b6a…`, SKILL.md
      `b88cbe91…` after the keying fix); the zero-touch `init --await-lock` command was VERIFIED to run
      (no --name needed; exit 0); cross-task: routes to adopt.md + setup-review.md (no duplication), honors
      task 1's build-boundary gate + `--await-lock`, the collapse is consistent with task 3's SETUP-REVIEW rows.
- [x] **REACHABILITY (was a disclosed gap, now CLOSED)** — at this task's first verify pass the flow was
      *unreachable*: both installers pre-ran plain `add.py init`, grandfather-locking the gate before `/add`.
      The human grew v12 with a 6th task **installer-arm** (PASS 2026-06-04): installers now drop files only, so a
      fresh install leaves no `.add/state.json` → `/add` → `status` (`no .add/ project found`) → AI runs
      `init --await-lock` → 0-setup.md §1's entry fires. **KEYING FIX (this task):** SKILL.md routing bullet
      `No .add/ yet` → `No .add/state.json yet` (a fresh install leaves `.add/tooling/` + `.add/docs/`, so the
      precise trigger is the missing state.json). Synced 3-tree (RED→GREEN parity), suite 322 OK.
- [x] a person reviewed and approved the change — Tin, at the verify gate (2026-06-04).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · 2026-06-04
Note: keystone guide (0-setup.md autonomous draft→lock + SKILL routing + keying fix) fully specified AND
reachable (the install-path gap was closed by the human-approved 6th task installer-arm, PASS). 322 OK; both
guides 3-tree byte-identical (0-setup.md a11e2b6a, SKILL.md b88cbe91); zero engine change. Two disclosures
carried forward: the `no .add/ project found` status hint names plain init (§7 follow-up, frozen engine), and
book ch. 10/13/14 still describe the old flow until book-align (task 5).

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): on real onboardings, does the AI reach `lock` without a human prompt
between init and lock? do greenfield runs keep the interview? does any session resume mid-setup and miss lock
(the disclosed status gap firing)?
Spec delta for the next loop: with installer-arm landed, the fresh-install CLI entry now runs `status` → gets
`error: no .add/ project found. Run add.py init first.` — the hint names PLAIN `init`, which grandfather-locks.
For the AI this is harmless (SKILL.md/0-setup.md prescribe `--await-lock`), but a human-CLI user following the
literal hint would skip the lock-down. Candidate 1-line engine refinement (same family as the deltas below):
the no-project error should suggest `init --await-lock`. Disclosed at this gate; behind task 1's frozen engine.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] `add.py status` doesn't surface the unlocked-setup → lock step (evidence: check 3, post-init
  status prints "run /add", not "review SETUP-REVIEW.md then lock"); follow-up: a small `cmd_status` hint when
  `setup.locked is False`. Behind task 1's frozen engine — schedule as a v12 fast-follow or next-milestone task.
