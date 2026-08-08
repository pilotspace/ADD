# MILESTONE: Installer Smarts Polish

goal: Close the PTY-only-reachable interactive-coverage gaps the installer-smarts gates disclosed: a reusable PTY test helper that drives clack select/confirm so the agent-select step and the clack happy-path prompts are exercised in CI (today they are node-syntax-checked + logic-unit-tested only).
rationale: sub-milestone — the forward-seed bucket for installer-smarts (mirrors how delta-resolution-polish homes delta-resolution's seeds). Holds the one deduped PTY-helper task that installer-smarts' gates disclosed as PTY-only-reachable; the other 13 archived SPEC deltas stay open as documented backlog.
stage: mvp · status: active · created: 2026-06-18

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A reusable PTY test helper (committed, shared by both twins) that drives clack
     select/confirm with real keystrokes, plus the CI tests that use it to exercise the
     installer's interactive TUI paths — the agent-select step (D8) and the clack
     happy-path sequence (intro → target → scope → agent → intent).
Out: No change to installer BEHAVIOR (the twins are frozen — this is test-harness only);
     no new runtime dependency (test-only PTY); no engine (add.py) edits; the other 13
     archived SPEC deltas (Cursor/Copilot registry, global-data restore/prune, etc.) stay
     open backlog, not pulled into this milestone.

## Shared decisions & glossary deltas   (living — every task must honor these)
- PTY harness — a test-only helper that allocates a pseudo-terminal so clack enters raw mode
  and the test can send keystrokes; it exercises the EXISTING interactive flow, never changes it.
- backlog seed — this milestone homes a seeded forward delta; tasks here are picked up
  just-in-time, not all built at once.

## Shared / risky contracts (freeze these first)
- PTY-helper API (how a test drives select/confirm + asserts the rendered flow) -> owning task pty-clack-harness

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] pty-clack-harness   depends-on: none   — Reusable PTY test helper driving clack select/confirm; CI-covers the agent-select step + the clack happy-path prompts. (DONE · gate PASS)

## Exit criteria (observable; map each to the task that delivers it)
- [x] The clack agent-select step and the happy-path prompt sequence are exercised by a committed CI test (no longer PTY-manual-only)   (verify: python3 -m unittest discover add-method/tooling)   (← pty-clack-harness)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : NEW `tooling/pty_clack.py` (test-only stdlib-PTY harness: `drive_clack` + `PtyRun`/`PtyTimeout` + keystroke constants) and NEW `tooling/test_pty_clack.py` (6 tests). `add.py` / `state.json` / templates UNTOUCHED; no new runtime/dev dependency (package.json unchanged).
- skill   : untouched.
- book    : untouched.

### Cross-task evidence   (one row per task)
- pty-clack-harness : gate=PASS · tests=6 green (suite 1319→1325, +6) · residue=none — adversarial earned-green verdict EARNED-WITH-CONCERNS with all 3 concerns closed; the build/verify edits to the task's own new test were human-reviewed + re-baselined; installer twins frozen, no behavior change.

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] the single Exit criterion is satisfied by the pty-clack-harness evidence row: a committed CI test drives the REAL clack TUI through a pseudo-terminal — the agent-select step (D8, override via DOWN → codex AGENTS.md) AND the happy-path sequence (target→confirm→scope→agent→intent, all 5 prompts asserted rendered, brain drops), plus cancel-writes-nothing and the prompt/child timeout guards.
- goal: close the PTY-only-reachable clack-coverage gaps the installer-smarts gates disclosed — proven by `python3 -m unittest discover -s tooling` running the 6 PTY tests green (the agent-select + happy-path are no longer PTY-manual-only).

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] commit the two new files (`tooling/pty_clack.py` + `tooling/test_pty_clack.py`) + the TASK/MILESTONE records on a feature branch (test-harness only; no engine/version bump)
- [ ] open a PR from the Close ship-review above; the human reviews + merges (CI must run setup-node + npm ci so the real clack is present for the PTY tests — same node-deps gap that bit ci.yml/publish.yml before)
- [ ] this milestone is test-coverage only — fold into the NEXT release bundle (no standalone version cut); it rides whenever the next release is drawn (per release.md)
