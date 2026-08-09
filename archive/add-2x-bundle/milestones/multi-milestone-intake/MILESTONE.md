# MILESTONE: Multi-milestone intake

goal: when intake decomposes a request into multiple milestones, the engine creates ALL of them — the first active, the rest QUEUED — and resume surfaces the queue, instead of creating only the first milestone.md
rationale: sub-milestone (a few tasks) extending INTAKE/roadmapping. Confirmed via interview: today intake creates only the FIRST milestone.md when a request decomposes into several; the multi-active STATE model already exists (active_milestones list), but there is no QUEUED milestone status and no batch-creation/resume surfacing. Behavior confirmed: create all N, first active + rest queued.
stage: mvp · status: active · created: 2026-06-26T08:26:18+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a `queued` milestone status (active · queued · done) so a milestone can exist non-active; a way to create milestones queued (`new-milestone --queued`) and promote a queued one to active; intake guidance (intake.md) for decomposing a multi-milestone request into a roadmap that creates all N (1 active + N−1 queued); status/resume surfacing of the queued backlog (active + what's next).
Out: changing the multi-active STATE model (active_milestones list already exists — reused, not reshaped); auto-activating all N (the chosen model is 1-active + queued, NOT multi-active-all); per-user ownership of queued milestones (team-collab concern, deferred); any auto-start of a queued milestone without human confirm.

## Shared decisions & glossary deltas   (living — every task must honor these)
- Milestone status enum becomes **active · queued · done** (was active · done). `queued` = created, not yet the focus, awaiting promotion. Named consistently in engine + GLOSSARY + status render.
- The roadmap creates **1 active + N−1 queued** — never auto-activates the whole set (that would be the rejected multi-active-all model).
- Promotion is human-gated: a queued milestone becomes active only on an explicit `activate`/promote, never silently.

## Shared / risky contracts (freeze these first)
- the `queued` milestone status + its state shape -> owning task `milestone-queued-state` (the other two build on it)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] milestone-queued-state   depends-on: none                   — add the `queued` milestone status (active·queued·done) + `new-milestone --queued` + promote-to-active; migration-safe
- [x] roadmap-intake-guide     depends-on: milestone-queued-state — intake.md: decompose a multi-milestone request into a roadmap that creates all N (1 active + N−1 queued), not just the first
- [x] queue-resume-surface     depends-on: milestone-queued-state — status/guide surface the queued backlog at resume (active milestone + what's queued next)

## Exit criteria (observable; map each to the task that delivers it)
- [x] a milestone can be created `queued` and promoted to active; status enum is active·queued·done   (← milestone-queued-state)
- [x] intake.md guides decomposing a multi-milestone request into all-N creation (1 active + N−1 queued)   (← roadmap-intake-guide)
- [x] `status` surfaces the queued backlog (active + next-up), so a multi-milestone session resumes cleanly   (← queue-resume-surface)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add.py` — `new-milestone --queued` (creates status=queued, non-focused) + `cmd_activate` promotes queued→active + `cmd_status` additive `queued :` resume cue (present-only, byte-identical when zero). Milestone status enum now active·queued·done. ENGINE_MD5 acda5c26→8a6440cf→e81bef8b across the 2 engine tasks; 3-tree mirror byte-identical.
- skill   : `intake.md` — new `## Roadmap — a request that is several milestones` section (decompose → propose → confirm → create 1 active + N−1 `--queued` → promote with `activate`; contrasted with split_required). 3-tree byte-identical; core lean pool rebaselined 18465→19675.
- book    : `appendix-c-glossary.md` (×4 trees) — new `Queued milestone` + `Roadmap` entries.

### Cross-task evidence   (one row per task)
- milestone-queued-state : gate=PASS · tests=2002/0 (+7) · residue=none (engine; default path byte-identical, md5-confirmed)
- roadmap-intake-guide   : gate=PASS · tests=2009/0 (+7) · residue=none (convention-only; ENGINE_MD5 unchanged; lean fence rebaselined)
- queue-resume-surface   : gate=PASS · tests=2013/0 (+4) · residue=none (present-only render; re-pin + task-2 constant updated in lockstep per human-approved freeze)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
  - EC1 (queued status + promote + enum) ← milestone-queued-state (tooling: --queued + cmd_activate + enum)
  - EC2 (intake guides all-N creation) ← roadmap-intake-guide (skill: intake.md `## Roadmap`)
  - EC3 (status surfaces the queued backlog) ← queue-resume-surface (tooling: cmd_status `queued :` cue; live-rendered "queued : 2 milestone(s) next — beta, gamma")
- goal: when intake decomposes a request into several milestones, the engine creates ALL of them (1 active + rest queued) and resume surfaces the queue — proven end-to-end: `new-milestone --queued` creates non-active, `activate` promotes, and `status` shows the backlog + promote-next hint. Full suite 2013/0.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from the branch carrying this milestone (3 tasks + engine re-pin + glossary); the human reviews + merges
- [ ] this milestone joins the next MINOR release cut (engine feature: queued milestones + roadmap intake) — `add.py release <version>` records it (CHANGELOG + RELEASES.md attribution)
- [ ] tag / publish (npm + PyPI) — human-run, per release.md (the published engine then carries the queued-milestone feature)
