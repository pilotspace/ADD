# TASK: Propagate canonical skill/template to stale mirror trees (123258c fallout)

slug: mirror-resync · created: 2026-06-29 · stage: mvp
autonomy: auto   <!-- Multi-component repo? add a `component: <name>` line (declared in .add/components.toml) to bind this fast task to a component — its root joins §5 Scope and its green-bar/verify surface at the gate. Omit for single-component projects. -->
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `.claude/skills/add/phases/5-build.md` (stale mirror) ← `add-method/skill/add/phases/5-build.md` (canonical) · `.add/tooling/templates/TASK.md.tmpl` (stale mirror) ← `add-method/tooling/templates/TASK.md.tmpl` (canonical)
Context (working folder): drift from commit 123258c ("enrich §5 Strategy prompt") — canonical + _bundled updated, these two mirror trees not → 16 red parity guards (test_tree_parity · test_template_form_tags · test_high_risk_signal · test_path_confinement · test_skill_lean · …)
Honors (patterns / conventions): canonical `add-method/` is the single source of truth; mirrors must byte-match it — propagate with cp (the recurring 3-tree skill/template parity invariant). NO engine change → ENGINE_MD5 unchanged.
Anchors the contract cites: the two canonical↔mirror file pairs above.

---

## 1 · SPECIFY — the rules

Feature: Re-sync the two stale mirror files to canonical so the 3-tree skill/template parity guards pass.
Must:
  - `.claude/skills/add/phases/5-build.md` is byte-identical to its canonical source
  - `.add/tooling/templates/TASK.md.tmpl` is byte-identical to its canonical source
Reject:
  - propagating mirror→canonical (reverting 123258c's enrichment) -> "wrong_propagation_direction"
Accept: after the task, md5(each mirror) == md5(its canonical) AND the full parity suite is green.
Assumptions: ⚠ canonical is the correct truth (123258c enriched canonical; mirrors are stale; _bundled already matches canonical) — if wrong I'd revert a real change; if so, re-propagate the other way. Confidence high.

---

## 3 · CONTRACT — freeze the shape

```
mirror parity — byte-identical to canonical (direction: canonical add-method/ → mirror, never reverse):
  .claude/skills/add/phases/5-build.md   == add-method/skill/add/phases/5-build.md
  .add/tooling/templates/TASK.md.tmpl    == add-method/tooling/templates/TASK.md.tmpl
no engine/code change · ENGINE_MD5 unchanged · the existing parity suite (test_tree_parity etc.) goes green.
```

`Least-sure flag surfaced at freeze:` [spec] direction = canonical→mirror (123258c enriched canonical; mirrors stale; _bundled already matches canonical). If wrong: re-propagate the other way.
Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: test_mirror_parity — assert md5(.claude/skills/add/phases/5-build.md)==md5(canonical) AND md5(.add/tooling/templates/TASK.md.tmpl)==md5(canonical). Red now (they differ); green after propagation.
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `.claude/skills/` `.add/tooling/templates/`
Strategy & known-problem fixes: 1. write the red parity test in ./tests/ · 2. cp canonical→mirror for both files · 3. re-run the full suite (the 16 parity reds + my test go green). Trap: copy the RIGHT direction (canonical→mirror); never touch canonical or _bundled (already correct). `.claude` is excluded from the scope walk (scope-exclude-claude), so only `.add/tooling/templates/` registers in the snapshot.
Strategy actually used: as planned — wrote test_mirror_parity (red: both mirrors drifted), then `cp` canonical→mirror for the two files. Verified both md5-match canonical. The 14 byte-identical/parity guards (test_tree_parity, test_template_form_tags, test_high_risk_signal, test_path_confinement, test_*_triplet, grammar/scope/stale-guide mirrors) all flipped green. Discovered 123258c's fallout was BROADER than mirror parity: 2 non-parity reds remain, each outside this task's frozen §3 — `test_min_pillar` (persist-dag-plan's new `dag-plan` subcommand census) and `test_skill_lean` (the enriched 5-build.md is 57 B over the phases lean fence). Both surfaced for separate handling; no canonical/_bundled edits made here.
Code lives in: the two mirror files   ·   Constraints: change no test, no contract; no canonical/_bundled edits.

---

## 6 · VERIFY — evidence + gate

- [x] frozen-§3 tests pass (test_mirror_parity + the 14 parity guards) · no test or contract altered during build
- [x] green was EARNED — md5 equality is byte-exact; test was red-for-the-right-reason first
- [x] no exposed secrets, injection openings, or unexpected dependencies (cp-only; security = HARD-STOP) — none

Build expectations (from frozen §3): both mirror files md5-match canonical AND the parity suite (test_tree_parity, test_template_form_tags, test_high_risk_signal, test_path_confinement, the byte-identical triplets) is green — confirmed by `python3 -m unittest discover`. NOTE: 123258c's fallout proved broader than mirror parity; 2 NON-parity reds remain, each outside this frozen §3 and handed to its owner — `test_min_pillar` (persist-dag-plan) · `test_skill_lean` (a separate 57 B lean-fence breach).

### GATE RECORD
Outcome: PASS
Reviewed by: Claude (self-gated; loose fast task, mechanical canonical→mirror propagation authorized by Tin "fix it now as a loose task") · date: 2026-06-29
OBSERVE: [process] commit 123258c shipped with a red suite (14 parity + 1 lean-fence + drift) — a pre-merge `add.py check`/full-suite run would have caught it; mirror-resync clears the parity legs only.
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
