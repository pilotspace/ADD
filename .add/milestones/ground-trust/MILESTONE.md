# MILESTONE: Ground-trust

goal: GROUND surfaces the issues/risks it finds in the real code (feeding SPECIFY) and links each task's related intent to the foundation (PROJECT.md · GLOSSARY.md · conversation), so specs build on problems found, not assumed.
rationale: new-major roadmap (artifact-trust line), milestone 1 of 5. A new theme no active milestone covers — making TASK artifacts ground-aware. Confirmed via intake interview 2026-06-30 (Core M1+M2+M3+M4+M5 selected; minimal-backlink graph).
stage: mvp · status: active · created: 2026-06-30T11:47:47+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  Two new §0 GROUND sub-fields (terse, task-delta, lean-consistent with Touches/Context/Honors/Anchors):
     (1) **Issues/Risks (→ feed §1)** — concrete problems/traps/untestable risks the AI finds in the REAL
         code while grounding, which §1 SPECIFY then builds on (so the spec answers problems found, not
         assumed). (2) **Related intent** — links the task to foundation intent: `.add/PROJECT.md` §,
         `GLOSSARY.md` term(s), and the conversation source. Ground guide (`phases/0-ground.md`) gathers
         both; §1 specify guide consumes the issues; exit gate updated. Template + guide propagated across
         their 3 byte-identical trees; tests guard presence/parity.
Out: rule IDs / coverage lint (→ traceability-ids), cross-artifact metadata (→ artifact-graph),
     line-number/ground_sha drift fix (→ drift-guard), SEAMS.md (→ seams). No NEW human gate in ground
     (it stays AI-owned, §0 preamble). Lean budget: absorb new guide/template bytes by compaction first.

## Shared decisions & glossary deltas   (living — every task must honor these)
- Both new fields are §0 sub-fields, **task-delta only, never a re-scan** — same lean discipline as the
  existing four GROUND fields. A `<…>` placeholder = WEAK grounding (same rule as today).
- "conversation" target is undecided (`.add/conversation.md` does not exist) — resolved in
  `ground-related-intent`'s contract (candidate: SOUL.md / live session pointer, NOT a heavy new artifact).

## Shared / risky contracts (freeze these first)
- the §0 GROUND template shape (TASK.md.tmpl) -> first frozen by `ground-issues`; `ground-related-intent`
  extends the SAME shape (change-aware, serialized — both touch §0 + the ground guide).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] ground-issues          depends-on: none           — §0 "Issues/Risks (→ feed §1)" field + ground guide gathers it + §1 specify guide consumes it + template/guide 3-tree parity + test
- [ ] ground-related-intent  depends-on: ground-issues  — §0 "Related intent" field (PROJECT.md · GLOSSARY · conversation) + ground guide + exit gate + resolve the conversation target + 3-tree parity + test

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A grounding records the concrete issues/risks found in the real code, and §1 SPECIFY can cite them   (← ground-issues)
- [ ] A grounding links the task to its foundation intent (PROJECT.md § · GLOSSARY term · conversation)    (← ground-related-intent)
- [ ] §0 template parity holds across its 3 trees and the ground guide across its 3 skill trees; full suite green   (← both)

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
