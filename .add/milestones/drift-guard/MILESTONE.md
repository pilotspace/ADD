# MILESTONE: Drift-guard

goal: Kill §0 reference rot: cite symbols not line numbers, stamp ground_sha, refresh at close, strip dead live-phase scaffolding at done — so a closed TASK.md stays true to the code.
rationale: sub-milestone of the artifact-trust roadmap (M3) — the PR40 audit's top recurring defect: §0 line-number references rot during BUILD while symbols survive, and closed TASK.md files keep their live-phase `<!-- -->` scaffolding as dead weight. Make a closed task stay true to the code.
stage: mvp · status: active · created: 2026-06-30T11:47:47+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  Two threads, both honoring engine NO-EXEC (add.py never shells out — the engine SEEDS a field + VALIDATES/WARNs; the AI FILLS it at ground time, exactly like M1's Related-intent).
  1. **ground-anchor-sha** — §0 GROUND template gains a `Ground SHA:` field; the AI records `git rev-parse --short HEAD` at ground time so every cited location is "as of this SHA" (drift becomes detectable, not silent). The 0-ground guide shifts the convention to "cite SYMBOLS, optionally `@sha` — not bare line numbers". `add.py check` WARNs (nudge, exit 0) when a §0 cites bare line numbers (`l.NNN`/`:NNN`) but carries no Ground SHA — drift would otherwise be invisible.
  2. **strip-scaffold-at-done** — when a task reaches `phase: done`, the engine strips the live-phase `<!-- … -->` instruction comments from its TASK.md (scaffolding for the live phase; dead weight once closed). Lean + true closed artifact. Degrade-safe + atomic; only HTML comments removed, never authored content.
Out: auto-REFRESHING line numbers at close (needs serena/git → NO-EXEC forbids; the Ground SHA marks staleness instead, the AI refreshes manually if wanted) · rule IDs / `# covers:` / delta↔task links (→ M4 traceability-ids) · SEAMS.md (→ M5 seams).

## Shared decisions & glossary deltas   (living — every task must honor these)
- Engine stays NO-EXEC: it provides the field + the warn; the AI/human fills the SHA (no `git` subprocess in add.py).
- A `check` finding here is a WARN (nudge, exit 0), never a blocking gate — mirrors the artifact-graph backlink-drift WARN.
- Every add.py edit re-pins ENGINE_MD5 ×3; templates parity ×3; the phases lean pool stays within budget.

## Shared / risky contracts (freeze these first)
- §0 GROUND `Ground SHA:` field + the `check` line-number-without-sha WARN -> owning task ground-anchor-sha
- the done-time comment-strip transform (which comments, when, atomic) -> owning task strip-scaffold-at-done

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] ground-anchor-sha       depends-on: none              — §0 gains `Ground SHA:`; 0-ground guide → cite symbols not line numbers; `check` WARNs on line-refs without a SHA
- [ ] strip-scaffold-at-done  depends-on: none              — at `phase: done` the engine strips the live-phase `<!-- -->` instruction comments from TASK.md (atomic, content-safe)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A new task's §0 GROUND carries a `Ground SHA:` field, and `add.py check` warns when a §0 cites bare line numbers without one   (← ground-anchor-sha)
- [ ] A task that reaches `phase: done` has its live-phase `<!-- -->` instruction comments stripped from TASK.md, with all authored content intact   (← strip-scaffold-at-done)
- [ ] every add.py copy stays byte-identical == the re-pinned engine_pin.ENGINE_MD5; templates parity holds; full suite green   (← both)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

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
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
