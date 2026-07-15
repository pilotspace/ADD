# MILESTONE: Engine output diet — cut add.py's re-read cache weight

goal: Reduce the engine_output share of an ADD run's cache-read (WM1 baseline 38.4% / 5.48M residency-weight) by trimming the highest-residency add.py command outputs (--help, default status, new-task/init orientation) without losing the resume point, next-call hint, or guide pointer the AI needs, re-measured by the token_anatomy harness.
rationale: sub-milestone — the token-anatomy harness proved engine_output (re-read add.py command output) is 38.4% of an ADD run's WM1 cache-read, dwarfing method-doc residency (6.3%); this milestone trims the three highest-residency outputs. Data-driven follow-on to the measure-first anatomy work.
stage: mvp · status: active · created: 2026-07-15T06:57:13+00:00
release: pending
relates-to: call-residuals, orientation-honesty

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  trim the OUTPUT BYTES of the three highest-residency `add.py` commands so they carry less resident cache-read weight — (1) `--help` (120 lines/8.3k, 17% of engine weight from ONE early call), (2) bare `status` default (75 lines/5.4k, 29.8%; a `--brief` flag already exists — make the LEAN view the default, fat roster/backlog behind `--all`), (3) `new-task`/`init` orientation echo (recipe + roster dumps, ~15%). Every trim PRESERVES the load-bearing lines (resume point · `next:` hint · phase-guide pointer). Re-measure with `token_anatomy` + a deterministic static byte-size proxy.
Out: reducing the NUMBER of calls (call-residuals/orientation-honesty own that — this is bytes-per-call, orthogonal) · verify-gate / freeze / report output (not top-residency) · a real fresh headless benchmark re-run (expensive; the static byte proxy is the gate, harness re-run is optional confirmation) · trimming PROJECT.md/method-doc residency (only 6.3% — not worth the risk).

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): `add-method/tooling/add.py` — the argparse top-level help/epilog (help-diet), `cmd_new_task` + `cmd_init` created/recipe echoes (orient-diet). SEPARATELY `add-method/skill/add/SKILL.md` + `phases/*` + `agents/*` — the bare-`status` call sites switch to `status --brief` (status-brief-adoption, doc-only). Split: the add.py edits repin ENGINE_PKG_MD5 + SEAMS.md; the skill-doc edits do NOT.
Anchors: the argparse parser/epilog, `cmd_new_task`, `cmd_init`, `--brief` (already exists), the SKILL orient section.
Honors (conventions): `SEAMS.md` pins add.py line numbers (repin on shift) · `status` must still name PROJECT.md + SOUL.md (skill orient contract) · report-template banner discipline · every command still ends with a `next:` hint (the load-bearing guidance line).
Issues/Risks (shared): trimming an output line that a TEST or the SKILL/guide flow parses (many status-census tests pin phrases) → grep the pinned-phrase census before cutting; a diet that drops the resume point / `next:` / guide pointer is a GOAL violation, not a win.

> Gather this ONCE per milestone (the drafting step in `scope.md`). Each task's `specify`
> PROJECTS its §1 expectations from here + the specific request — light, not re-grounded per task.

## Shared decisions & glossary deltas   (living — every task must honor these)
- LOAD-BEARING FLOOR: the AI must still receive the resume point (active task · phase), the `next:` hint, the phase-guide pointer, AND the orient instruction to read PROJECT.md + SOUL.md — a diet that drops guidance is a defect. NOTE: `status --brief` omits the PROJECT.md/SOUL.md names by design; the SKILL orient PROSE already carries "read PROJECT.md + SOUL.md", so switching the skill to `--brief` preserves the floor (guidance moves from thrice-re-emitted command output into the once-cached skill — a real saving).
- MEASURE: the gate is a DETERMINISTIC static byte/line-count drop of each command's output (residency-weight ∝ output size at equal call-position); a `token_anatomy` re-run on a fresh run is optional confirmation, never the blocking gate (avoids paid re-runs).
- ENGINE repin SPLIT: help-diet + orient-diet EDIT `add.py` → re-pin ENGINE_PKG_MD5 + update SEAMS.md line refs. status-brief-adoption is a SKILL-DOC edit (switches which command the guides call; engine untouched) → NO engine repin (call-residuals lesson: doc/template edits don't repin).

## Shared / risky contracts (freeze these first)
- `add.py --help` top-level output shape (what stays vs moves behind per-command `-h`) -> owning task `help-diet` — the largest single trim; keep every subcommand discoverable.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] help-diet              depends-on: none            — trim `add.py --help` top-level output to essentials + a "per-command: add.py <cmd> -h" pointer; no command lost from discoverability (17% of engine weight, one early call). EDITS add.py → repin.
- [ ] status-brief-adoption  depends-on: none            — switch SKILL.md + phase guides + agents from bare `status` to `status --brief` at the orient + mid-loop call sites; RETAIN the "read PROJECT.md + SOUL.md" instruction in the skill prose. DOC-only, engine default untouched, no repin (29.8%).
- [ ] orient-diet            depends-on: none            — trim `new-task` created-echo + `init` banner/recipe dumps to the load-bearing next-step lines (~15%). EDITS add.py → repin.

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `add.py --help` output drops from 120 lines to ≤ ~45, still lists every subcommand (or a discoverable pointer), tested by a line-count + subcommand-presence assertion   (← help-diet)
- [ ] SKILL.md + phase guides + agents call `status --brief` (not bare `status`) at orient/mid-loop sites; the "read PROJECT.md + SOUL.md" orient instruction is retained in prose; bare-status ENGINE output is unchanged (existing status-census tests stay green)   (← status-brief-adoption)
- [ ] `add.py new-task` / `init` echo trimmed to their load-bearing next-step lines (measurable char drop), guidance preserved   (← orient-diet)
- [ ] combined static output size of the targeted surfaces drops ≥40% vs baseline; full `add-method` test suite green; ENGINE_PKG_MD5 + SEAMS.md repinned for the two add.py-editing tasks   (← all three)

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
