# PLAN: Fold Step-2 Scenarios chapter into Step-4 across the book (+ mermaid + add-flow.png)

slug: book-de-scenarios · created: 2026-07-23 · stage: mvp
milestone: scenarios-into-tests
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Reconcile the AIDD book with the engine's retired §2 — fold the standalone "Step 2 — Scenarios" chapter into "Step 4 — Tests & Scenarios", repoint the nav chain + all inbound links, and update the step enumeration (prose · Mermaid · tables · matrix) so the book teaches the SAME non-contiguous step set the template now renders. Applied to BOTH git-tracked book trees (canon `add-method/docs/` + repo-root chapter mirror).
Framings weighed: retire-in-place mirroring the engine (chosen — delete the Step-2 chapter, keep other chapter FILE numbers, fold teaching into Step-4; matches the template's own §1→§3→§4 non-contiguous scheme) · full chapter renumber 05→04… (rejected — renames every chapter file + every cross-ref for zero teaching gain)
Must:
<must>
  - M1 The "Step 2 — Scenarios" chapter (`04-step-2-scenarios.md`) no longer exists in either book tree; its teaching content (Given/When/Then form · edge-case sweep · rule-ID tagging) is folded into the Step-4 chapter, retitled "Step 4 — Tests & Scenarios".
  - M2 No book file links to the deleted `04-step-2-scenarios.md` (every inbound reference repointed to Step-4 or removed).
  - M3 Every internal book link resolves — no dangling file link or anchor after the fold (the nav prev/next chain re-links 03 -> 05 -> 06 with no gap).
  - M4 The step ENUMERATION reflects the fold: the flow prose, the `02-the-flow.md` Mermaid, and the step tables (`02-the-flow` · `10-setup-and-stages` · `11-governance` · `12-roles` · `appendix-f`) no longer present "Scenarios" as a standalone NUMBERED step. "Scenarios" as an ACTIVITY/concept may remain where it denotes the practice (glossary, "contributes to", curriculum).
  - M5 §-section references to a "§2 scenario" / "§2/§4" (`08-step-6-verify` · `16-releasing` · `03-step-1-specify`) point to §4.
  - M6 The `add-flow.png` raster is REMOVED from both trees and its embed line dropped; the flow diagram is the native```mermaid block in `02-the-flow.md` (updated to the new step set — both GitHub + MkDocs-material render it). Decided at freeze: drop raster, rely on Mermaid.
  - M7 The two book trees stay byte-identical per chapter (`test_tree_parity` docs invariant green).
</must>
Reject:
<reject>
  - a book edit that leaves a DANGLING internal reference — a link to a file or anchor that no longer resolves -> "broken_book_link"
</reject>
After:
<after>
  - The book teaches the same step model the engine renders; a link-resolve sweep passes; `test_tree_parity` docs check is green; the milestone `scenarios-into-tests` goal (book matches engine) is met.
</after>
Boundary: two reference kinds the checks MUST distinguish — (a) a STRUCTURAL ref (a "Step 2" numbered step · a "§2 section" · a `04-step-2-scenarios.md` link) which MUST change · vs (b) "Scenarios" as an ACTIVITY/concept, which MAY stay.
<assumptions>
  ⚠ Riskiest: that the native ```mermaid renders in BOTH book targets (GitHub + the MkDocs site) so the stale `add-flow.png` raster can be dropped rather than re-rendered. If a target needs the raster, the PNG must be regenerated out-of-session (image-docs flow) — cost: a follow-up, or a stale diagram ships. Surfaced as the freeze decision (M6).
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Book step model AFTER (mirrors the engine — NON-contiguous):
  Step 1 Specify · Step 3 Plan · Step 4 TESTS & SCENARIOS · Step 5 Build · Step 6 Verify · Step 7 Observe
  — NO standalone "Step 2 — Scenarios" chapter or numbered step —
Chapters: `04-step-2-scenarios.md` DELETED (both trees); `06-step-4-tests.md` RETITLED "Step 4 — Tests & Scenarios"
  + absorbs the scenario teaching; nav re-linked 03 <-> 05 <-> 06. Other chapter FILE numbers UNCHANGED.
Link integrity: zero refs to `04-step-2-scenarios.md`; every internal `](./NN-….md)` + anchor resolves.
Scenario-as-ACTIVITY: PRESERVED where it denotes the practice (glossary term, role "contributes to", adoption curriculum).
add-flow.png: REMOVED (both trees) + its embed line dropped; the native ```mermaid in 02-the-flow.md IS the flow diagram (updated to the new step set).
Twin parity: canon `add-method/docs/` == repo-root chapter mirror, per chapter (test_tree_parity docs invariant).
```

Target (measurable): `grep -rn "04-step-2-scenarios" <both docs trees>` == 0 · no "Step 2 — Scenarios" chapter/step or "§2 scenario" section-ref remains · a link-resolve sweep finds 0 dangling internal links · `test_tree_parity` green. (Renders/reads confirmed by the link sweep + a manual read of the folded Step-4 chapter.)
Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze:
  ⚠ [contract] PNG decision LOCKED (drop raster → native ```mermaid). Residual risk: the MkDocs-material site config must have the mermaid superfences enabled, else the site loses the diagram. Cost if wrong: the published site shows a code block, not a diagram. Verify the mkdocs config renders mermaid before removing the raster (build-time check).
Reported: yes — the freeze report (SHAPE/SUMMARY/FLAGS) rendered before this froze

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/docs/` `add-method/../02-the-flow.md` `add-method/../03-step-1-specify.md` `add-method/../04-step-2-scenarios.md` `add-method/../05-step-3-plan.md` `add-method/../06-step-4-tests.md` `add-method/../08-step-6-verify.md` `add-method/../09-the-loop.md` `add-method/../10-setup-and-stages.md` `add-method/../12-roles.md` `add-method/../14-foundation.md` `add-method/../16-releasing.md` `add-method/../appendix-d-worked-example.md` `add-method/../appendix-e-checklists.md` `add-method/../appendix-f-requirements-matrix.md` `add-method/../add-flow.png` `add-method/../mkdocs.yml`

Regression floor: `add-method/tooling/test_tree_parity.py` (docs-mirror + book-chapter parity) must stay green; a link-resolve sweep over both trees = 0 dangling.
Persona (required): `.add/personas/book-technical-writer.md`

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - check_no_scenarios_chapter: `04-step-2-scenarios.md` absent in BOTH trees; `06-step-4-tests.md` H1 == "Step 4 — Tests & Scenarios" and carries the folded scenario teaching (Given/When/Then + edge sweep + tagging) · covers: M1
  - check_no_inbound_links: `grep -rn "04-step-2-scenarios" add-method/docs/ <repo-root chapters>` == 0 · covers: M2
  - check_links_resolve: every internal `](./NN-….md)` (+ `#anchor`) across both trees resolves to an existing file/heading — 0 dangling · covers: M3, R:broken_book_link
  - check_step_enum_folded: no "Step 2 — Scenarios" / "2 Scenarios" step row in the `02-the-flow` Mermaid + the 5 step tables; flow prose reads the new set · covers: M4
  - check_section_refs: no "§2 scenario" / "§2/§4" section-ref in `08-step-6-verify` · `16-releasing` · `03-step-1-specify` (activity mentions ok) · covers: M5
  - check_png_removed: `add-flow.png` absent in both trees, no `](./add-flow.png)` embed remains, and the `02-the-flow.md` ```mermaid reflects the new step set · covers: M6
  - check_tree_parity: `add-method/tooling/test_tree_parity.py` docs invariant green (canon == repo-root mirror per chapter) · covers: M7
</test_plan>

Rigor: the 7 acceptance checks above are the PRIMARY gated floor (verifiable pass/fail evidence, red before the fold, green after). Minor polish (exact prose wording of the folded Step-4 sections, activity-mention phrasing) is build-guidance — not gated.

Tests live in: evidence · the checks run RED before the fold (chapter present, links point at it) and GREEN after.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned + one config addition. Retire-in-place across BOTH book trees: deleted the Step-2 chapter (`04-step-2-scenarios.md`) + `add-flow.png` (canon & repo-root); folded the scenario teaching (Given/When/Then · edge sweep · rule-ID tagging) into `06-step-4-tests.md`, retitled "Step 4 — Tests & Scenarios"; re-linked the 03↔05↔06 nav; reconciled the flow narrative (seven→six steps, non-contiguous 1·3·4·5·6·7) + rewrote the `02-the-flow.md` Mermaid (dropped the S2 node, S1→S3) + the two flow tables; folded the `10`/`appendix-e`/`appendix-d`/`appendix-f` step tables and the `12-roles` RACI (merged Scenarios→"Tests & Scenarios" column); repointed the §2 section-refs in `08`/`16`/`03` to §4; kept "Scenarios" as an ACTIVITY where the frozen Boundary permits (the `11-governance` skip-cost + profile-rigor tables, the `12-roles` "Contributes to" prose, the `2_scenarios` playbook). ADDED (M6-required, not in the original plan): enabled `pymdownx.superfences` mermaid in `mkdocs.yml` so the Material site renders the native diagram once the raster is dropped, and dropped the stale Step-2 nav entry. Synced the repo-root mirror byte-identical by copying canon.
Code lives in: `./src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite)
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self (solo, per §5) · adversarially checked: (1) tried to find a surviving STRUCTURAL ref — grep across BOTH trees for `04-step-2-scenarios` · `add-flow.png` · `Step 2` · `§2` all return 0; (2) ran a link-resolve sweep (custom checker: every `](./NN-.md)` + `#anchor` in both trees) → 0 dangling — the `broken_book_link` Reject cannot fire; (3) confirmed the 7 acceptance checks are genuine grep/parity evidence, not fixture-overfit; (4) `test_tree_parity` 6/6 green + FULL tooling suite 2236 OK (no doc-coupled test regressed); (5) probed the residual — the folded `06` H1 == "Step 4 — Tests & Scenarios" in both trees and carries the Given/When/Then + edge-sweep + tagging teaching. RESIDUAL (disclosed, not a code gap): the MkDocs-material mermaid render could NOT be build-verified in-session (no `mkdocs`/`pymdownx`/`material` installed here); the config added is the canonical Material superfences-mermaid setup — a pre-publish `mkdocs build` on CI/Pages must confirm it. The bare-"Scenarios" activity mentions left in `11-governance`/`12-roles` are classified per the frozen §1 Boundary (structural = numbered "Step 2"/"§2"/file-link only; activity MAY stay).

### GATE RECORD
Reported: yes — the gate report (banner/ARC + SHAPE/SUMMARY/FLAGS/EVIDENCE) rendered before this outcome recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-23

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose retire-in-place mirroring the engine; rejected full chapter renumber 05→04… (rejected — renames every chapter file + every cross-ref for zero teaching gain)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned + one config addition. Retire-in-place across BOTH book trees: deleted the Step-2 chapter (`04-step-2-scenarios.md`) + `add-flow.png` (canon & repo-root); folded the scenario teaching (Given/When/Then · edge sweep · rule-ID tagging) into `06-step-4-tests.md`, retitled "Step 4 — Tests & Scenarios"; re-linked the 03↔05↔06 nav; reconciled the flow narrative (seven→six steps, non-contiguous 1·3·4·5·6·7) + rewrote the `02-the-flow.md` Mermaid (dropped the S2 node, S1→S3) + the two flow tables; folded the `10`/`appendix-e`/`appendix-d`/`appendix-f` step tables and the `12-roles` RACI (merged Scenarios→"Tests & Scenarios" column); repointed the §2 section-refs in `08`/`16`/`03` to §4; kept "Scenarios" as an ACTIVITY where the frozen Boundary permits (the `11-governance` skip-cost + profile-rigor tables, the `12-roles` "Contributes to" prose, the `2_scenarios` playbook). ADDED (M6-required, not in the original plan): enabled `pymdownx.superfences` mermaid in `mkdocs.yml` so the Material site renders the native diagram once the raster is dropped, and dropped the stale Step-2 nav entry. Synced the repo-root mirror byte-identical by copying canon.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
