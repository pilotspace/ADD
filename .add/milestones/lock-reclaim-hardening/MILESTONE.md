# MILESTONE: Harden the global-update stale-reclaim lock so the publish gate is flake-free

goal: The concurrency suite (test_concurrent_stale_reclaim_*) passes deterministically under publish-job load — either the residual TOCTOU/double-hold in _update_lock's stale-reclaim path is fixed, or the test is proven to assert only what the CI filesystem can guarantee (without weakening the peak<=1 mutual-exclusion contract). Unblocks the v2.4.0 npm/PyPI publish.
rationale: <why this scope — the confirmed intake classification (bucket + reason)>
stage: mvp · status: active · created: 2026-07-24T11:03:03+00:00
relations: <cross-MILESTONE edges — `depends-on:` / `extends:` / `relates-to:` header lines, comma-sep slugs; omit if none; `add.py check` validates>

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/PLAN.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  <what this milestone delivers>
Out: <explicitly deferred — the anti-scope-creep list>

> UI/UX in scope? Name it precisely, not "make it nice" — IA · interaction pattern ·
> visual hierarchy · tokens · component states · WCAG AA · breakpoints · user journey.
> Skip generic AI-design defaults; name ONE deliberate signature element. A UI feature
> also triggers DESIGN.md via the `add` skill's design.md.

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): <the code every task in this milestone lands in — gathered once, task-delta>
Anchors: <the shared symbols tasks may cite — the floor each task's contract builds on>
Honors (conventions): <PROJECT.md · CONVENTIONS.md · SEAMS.md rules every task honors>
Issues/Risks (shared): <traps in the shared code that feed each task's §1 expectations>

> Gathered ONCE per milestone (`scope.md`); each task's specify PROJECTS its §1 from
> here + the specific request — light, never re-grounded per task.

## Shared decisions & glossary deltas   (living — every task must honor these)
- <cross-cutting rule, named from GLOSSARY.md>

## Shared / risky contracts (freeze these first)
- <contract name> -> owning task <slug>

## Tasks (breadth-first decomposition; detail lives in each PLAN.md)
- [x] lock-reclaim-hardening   depends-on: none   — stale-reclaim re-verifies staleness, not just inode identity

## Exit criteria (observable; map each to the task that delivers it)
- [x] A publish run completes without a second holder ever acquiring the lock — the
      concurrency suite (test_concurrent_stale_reclaim_*) stays green on Linux CI under
      publish-job load, and v2.4.0 actually reaches npm and PyPI.        (← lock-reclaim-hardening)

      EVIDENCE (recorded 2026-07-25):
      - root cause FIXED, not suppressed: fd9d5d5f re-verifies staleness rather than inode
        identity at 4 sites across BOTH lock twins (_installer.py and bin/cli.js). The
        peak<=1 mutual-exclusion contract was never weakened.
      - the thing this criterion said it would unblock SHIPPED: npm @pilotspace/add 2.4.0
        and PyPI pilotspace-add 2.4.0 are both live.
      - Linux CI (`ci` workflow, py3.10 + py3.12) green on main and on both feature
        branches through 2026-07-25.
      - 79 reclaim tests green locally (lock_reclaim_hardening 6 · js_reclaim_lock_heartbeat
        6 · project_scope_lock 31 · global_update_harden 36).

      LIMIT ON THIS CLAIM — read before trusting it: "deterministically" rests on repeated
      Linux CI green, NOT on a proof. The original defect was FLAKY (peak=2 observed twice
      on py3.10) and is filesystem-dependent: ext4/tmpfs reuse freed inodes, APFS does not,
      so every local macOS run is near-worthless as evidence for THIS bug. A future flake
      here is a REOPEN of this criterion, not a surprise regression from nowhere.

      NOTE ON PROVENANCE: this MILESTONE.md was never drafted — the exit criteria section
      held the raw template placeholder, so the earlier "0/1 met" was counting a placeholder
      rather than a real unmet criterion. The criterion above was written at close from the
      milestone goal, and is marked met on the evidence listed, not by lowering a bar.

## Strategy   (AI-drafted WITH the human — the optimized task plan; SOFT/advisory like a task's Build-strategy; drafted-blank for a micro/--tiny milestone)
> The persona-led strategy over THIS milestone's tasks — sequencing, freeze-first contracts,
> parallel waves, the first unblocking slice, tradeoffs named. SOFT: the preferred plan; the
> loop may deviate and records what it did. Drafted-blank is valid (risk-proportional).
- Approach (sequencing): <risk-first | dependency-first | first-slice-unblocks — and WHY>
- Freeze-first: <the shared/risky contract to freeze before the rest>
- Waves (parallel): <task slugs that can run concurrently behind frozen contracts — or "sequential">
- Tradeoffs weighed: <alternative decompositions considered + why this one>

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Cross-task review the AI fills — the evidence behind the EXISTING milestone-done gate, NOT a new approval.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> AI-written steps for THIS milestone (hints, not engine commands); MERGE is one small step; the human runs the cut.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run)>
