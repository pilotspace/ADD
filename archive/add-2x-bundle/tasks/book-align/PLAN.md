# TASK: Align book chapters 10/13/14 with autonomous-setup flow

slug: book-align · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: align the book's trust layer (chapters 10/13/14) with the autonomous-setup → lock-down flow that
v12 tasks 1–4 + installer-arm shipped — so the *why* the book teaches matches the *how* the skill drives.
Framings weighed: minimal-consistency-edits (chosen) · full-chapter-rewrite · new-setup-chapter
  - minimal-consistency-edits (chosen): touch only the passages that still tell the OLD human-led-setup story;
    keep each chapter's structure, voice, and surrounding content intact. The flow already lives in the skill
    (`0-setup.md`); the book gives the *why*, not the recipe.
  - full-chapter-rewrite (rejected): over-reach; most of ch.10/13/14 is stage/foundation theory unaffected by
    the setup-flow change — rewriting risks regressions for no gain.
  - new-setup-chapter (rejected): duplicates the skill's 0-setup.md and bloats the book; the existing chapters
    are the right homes.
Must:
  - **Ch 10 "One-time setup"** rewritten: setup is no longer a human chore. The AI runs `init --await-lock`,
    drafts the foundation (brownfield silent / greenfield 4-lens interview), the first-milestone scope, and the
    first task's candidate contract; the human's single act is the **lock-down** (`add.py lock`) — the
    setup-altitude analog of the contract freeze. The survivor files + "pipeline green before the first feature"
    substance is KEPT (they still exist; the AI fills them).
  - **Ch 13 "Adoption"** made consistent: the "Set the foundation" rollout step and the "Architect/Lead: stand
    up setup" role task describe the AI drafting the foundation and the human locking it down (not hand-standing
    it up). The 90-day rollout / profile / onboarding-from-the-build-end structure is UNCHANGED.
  - **Ch 14 "The foundation"** made consistent: the `add.py init` tooling bullet + one framing sentence note the
    foundation is now AI-drafted and frozen at the single human lock-down; never-overwrites-a-hand-edit stays true.
  - Each edited chapter stays byte-identical across canonical `add-method/docs/` and bundle `_bundled/docs/`
    (the `.add/docs/` install copy is gitignored; synced for local dogfood but not parity-tested).
Reject:
  - none material — PROSE consistency edits to the trust layer; cannot fail at runtime. Biggest risk = the book
    drifting from the skill's actual flow (describing a step the engine doesn't do). Mitigated: every claim is
    traced to a shipped, gated artifact (0-setup.md / add.py `lock` / installer-arm). Flagged ⚠ below.
After:
  - A reader of ch.10/13/14 sees the same autonomous-draft → one-human-lock-down flow the skill drives; no
    chapter still tells a reader to hand-stand-up the foundation before the first feature.
Assumptions — least-sure first:
  ⚠ [spec] How much of the book to touch. Least sure because the setup-flow change *ripples* — it could be
    argued to touch ch.12 (roles) or the appendices too; if wrong (under-reach): a reader hits a stale
    human-led-setup passage elsewhere. Mitigation: the milestone names exactly 10/13/14 as in-scope; I grep the
    whole book for residual old-setup language and DISCLOSE any hit outside 10/13/14 rather than silently
    expanding scope (the human decides whether it's this task or a follow-up).
  - [ ] the book is conceptual/tool-agnostic — keep the edits at the *why* altitude (don't paste skill command
    syntax into the book); name `add.py lock` only where the book already names `add.py` commands (ch.14).

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: ch.10 setup section describes autonomous-draft → lock-down
  Given a reader opens 10-setup-and-stages.md "setup" section
  Then it says the AI drafts the foundation (brownfield silent / greenfield interview) + first scope + first
    contract, and the human's single act is the lock-down (add.py lock)
  And the survivor files + "pipeline green before the first feature" substance is retained

Scenario: ch.13 adoption is consistent with autonomous setup
  Given a reader reads the 90-day rollout step + the Architect/Lead first-week row
  Then both describe the AI drafting the foundation and the human locking it down
  And the rollout/profile/onboarding-from-the-build-end structure is unchanged

Scenario: ch.14 foundation tooling line is consistent
  Given a reader reads ch.14 "In the tooling" + the framing
  Then it notes the foundation is AI-drafted and frozen at the single human lock-down
  And "add.py init never overwrites a hand-edited survivor" stays true

Scenario: edited chapters ship byte-identical (parity)
  Given the three chapters are edited in canonical add-method/docs/
  Then each is byte-identical to its _bundled/docs/ copy
  (asserted by test_bundle_parity::test_docs_tree_byte_identical — editing canonical alone turns it RED via
   md5 divergence; syncing canonical→bundle turns it GREEN)

Scenario: no old-setup language survives outside the named chapters
  Given the whole book
  When grepped for old human-led-setup phrasing
  Then hits exist only in 10/13/14 (verified at §1: zero hits elsewhere) — no silent scope creep
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

Prose-edit contract (not HTTP) — the exact passages that change and what stays untouched:

```
EDIT (canonical add-method/docs/, then sync → _bundled/docs/):
  10-setup-and-stages.md  "## One-time setup" block (lines ~9–28)
     → reframe to "Setup: the AI drafts, you lock down". KEEP: survivor-file table content (the files still
       exist), the "pipeline green before the first feature" exit idea. ADD: AI runs init --await-lock, drafts
       foundation (brownfield silent / greenfield 4-lens) + first scope + first contract, human's one act = lock-down.
  13-adoption.md  line 13 ("Days 1–15 — Set the foundation") + line 56 (Architect/Lead row)
     → AI drafts foundation, human locks down. UNCHANGED: everything else in the chapter.
  14-foundation.md  "## In the tooling" `add.py init` bullet (line ~116) + one framing sentence
     → note AI-drafted + frozen-at-lock-down; KEEP never-overwrites-hand-edit.

DO NOT TOUCH: ch.10 stages/depth-matrix/parallel-streams; ch.13 rollout/profiles/onboarding/portability;
  ch.14 three-concerns/one-file/feeds-the-engine/hierarchy. No other chapter (grep-confirmed clean).

PARITY INVARIANT: each edited file byte-identical canonical ↔ _bundled/docs/ (test_bundle_parity).
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- self-frozen 2026-06-04 per the v12-tail cadence ("pause only at each VERIFY gate"); lead-flag below -->
<!-- Bundle least-sure flag — [spec/scope]: how much of the book to touch. Resolved empirically at §1 — a
     whole-book grep for old-setup language returned ZERO hits outside 10/13/14, so the milestone's named scope
     is exactly right. If a reader later finds stale setup language elsewhere, that's a follow-up (disclose, don't
     silently expand). Cost: low — additive consistency edit. Decision: edit exactly 10/13/14, keep the why-altitude. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: parity (byte-identical docs trees) + human read. This is the book (the *why* / trust layer):
asserting prose CONTENT in a unit test is the over-testing the method warns against. The mechanical guard is
parity; the substantive guard is the human reading the diff at the verify gate.

Plan:
  - (existing) `test_bundle_parity.py::test_docs_tree_byte_identical` — editing the 3 canonical chapters turns it
    RED via md5 DIVERGENCE (the files already exist in both trees, so it's divergence, not orphan); syncing
    canonical → `_bundled/docs/` turns it GREEN. This is the red→green cycle for the edits.
  - (manual, recorded at §1) whole-book grep for old-setup language → zero hits outside 10/13/14 (scope guard).
No new test file.

Tests live in: (existing) `add-method/tooling/test_bundle_parity.py` · MUST be RED (md5 divergence on the edited
canonical chapters) before the sync, GREEN after.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): PROSE; no code, no engine change, no new imports. Edits restricted to the
§3-contracted passages; the surrounding chapter content (stages, depth matrix, parallel streams; rollout,
profiles, onboarding, portability; three-concerns, one-file, feeds-the-engine, hierarchy) is UNTOUCHED.
Code lives in: `add-method/docs/{10-setup-and-stages,13-adoption,14-foundation}.md`
  → synced to `src/add_method/_bundled/docs/...` (parity-tested) + `.add/docs/...` (gitignored, local dogfood).
What changed:
  - ch.10: "## One-time setup" → "## Setup: the AI drafts, you lock down" — AI runs init + drafts foundation
    (brownfield silent / greenfield 4-lens) + first scope + first contract; human's one act = lock-down; survivor
    table KEPT (added PROJECT.md row); exit-check reworked around the lock + pipeline-green.
  - ch.13: "Days 1–15 — Lock the foundation" (AI drafts, human locks) + Architect/Lead row (review + lock down,
    first contract freezes with it). Rest of chapter unchanged.
  - ch.14: "One file, not three" gained one framing sentence (AI drafts all four sections → human lock-down
    freezes it); "In the tooling" `add.py init` bullet notes draft → lock-down; never-overwrites-hand-edit KEPT.
Constraints honored: no code; no engine/test change (`add.py` md5 unchanged); canonical ↔ _bundled/docs
byte-identical for all 3; stayed at the why-altitude (named `add.py lock` only in ch.14, which already names add.py).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `Ran 322 tests … OK`; `test_bundle_parity::test_docs_tree_byte_identical`
      green after the canonical→bundle sync (md5-divergence→sync RED→GREEN completed).
- [x] coverage did not decrease — prose/trust-layer; parity re-verifies all 3 edited chapters byte-identical
      across canonical + bundle (+ dogfood synced). No code, so no unit coverage to move.
- [x] no test or contract was altered during build — §3 frozen; NO test touched; NO engine change
      (`add.py` md5 unchanged at `7174a4cf…`).
- [x] concurrency / timing safe — n/a (static markdown; no code, no state writes).
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no imports/eval/secrets.
- [x] layering & dependencies follow CONVENTIONS.md — 3-way md5 parity (10: `668f3d9b…`, 13: `2be3f8d4…`,
      14: `a0c40b15…`, identical canonical/bundle/dogfood); edits stay at the why-altitude; every claim traces to
      a shipped+gated artifact (0-setup.md / `add.py lock` / installer-arm). Scope guard: whole-book grep for
      old-setup language returned ZERO hits outside 10/13/14 (recorded §1) — no silent scope creep.
- [ ] a person reviewed and approved the change — **PENDING (this gate)**; the human reads the chapter diffs.

### Evidence
- **RED→GREEN**: editing the 3 canonical chapters turned `test_docs_tree_byte_identical` RED (md5 divergence) →
  GREEN after syncing canonical → `_bundled/docs/`. Full suite `Ran 322 tests … OK`.
- **Minimal-edit fidelity**: only the §3-contracted passages changed; stages/depth-matrix/parallel-streams (ch.10),
  rollout/profiles/onboarding (ch.13), three-concerns/one-file/hierarchy (ch.14) untouched.
- **Consistency with the skill**: the book now teaches the same autonomous-draft → one-human-lock-down flow that
  `0-setup.md` drives and `installer-arm` makes reachable — the *why* matches the *how*.
- **Milestone closure**: this is v12's final exit criterion (book ch.10/13/14 consistent). On PASS, v12 is complete.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-04

<!-- Evidence: full suite Ran 322 tests OK · ch.10/13/14 byte-identical canonical↔bundle↔dogfood
     (10=668f3d9b, 13=2be3f8d4, 14=a0c40b15) · streams.md 3-tree md5 5ac01db8 · add.py unchanged
     (7174a4cf — book-only task) · scope-guard grep clean outside 10/13/14. Disclosed gap closed
     before gate: advisor-flagged stale cross-ref docs/10-setup-and-stages.md:53 → :91 fixed across
     all 3 skill trees (the ch.10 setup rewrite shifted the cited "seams are serial" line down). No
     dead #one-time-setup anchor. This is v12's final exit criterion — PASS closes the milestone. -->

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
