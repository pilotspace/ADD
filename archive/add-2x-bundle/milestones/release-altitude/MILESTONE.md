# MILESTONE: Release altitude — cut a versioned, watched ship

goal: A project can cut a versioned, user-facing release that bundles one or more closed milestones — the AI drafts evidence-backed notes from folded deltas, the engine records the cut behind a security-hard-stop readiness floor, and the human owns the tag/publish — so shipping a version is a first-class 5th ADD altitude, not an ad-hoc ritual.
rationale: new-major — a new scope altitude (RELEASE) no active milestone's goal covers; sibling to graduation (`graduate.md`), orthogonal to stage. Closes the gap the human named: ADD formalizes building (tasks), keeping-going (`loop.md`), and rigor (`graduate.md`) but never the act of shipping a version — which this repo proves real by doing it by hand every release (the 1.5.0 recipe: CHANGELOG + 3 version sources + forward-pinned `test_release_X_Y_Z.py` + human-gated tag).
stage: mvp · status: active · created: 2026-06-16

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
- `release.md` on-demand guide: the 7-step RELEASE flow — cue → gather → draft notes → readiness floor → human confirms → cut → watch; referenced from `SKILL.md`. (drafted: `tmp/release.md`)
- `add.py release-report` (read-only): clusters the five record-sets — closed-since-last-release milestones · their folded deltas · RISK-ACCEPTED waivers riding in · open security HARD-STOP · §2 scenarios→monitors; `--json` branchable; emits the `→ releasable: N milestone(s)` status cue.
- `add.py release <version>` (guarded, record-only): prepends the CHANGELOG entry, appends a `RELEASES.md` ledger row (newest-first), attributes the bundled milestones; enforces the readiness floor. The engine records; it never tags, publishes, or deploys.
- `RELEASES.md` append-only ledger scaffold (date · version · milestones · waivers · evidence).
- Book ch.16 (`16-releasing.md`) + GLOSSARY entries + ×3-tree (canonical/bundled/dogfood) + repo-root parity. (outlined: `tmp/release-chapter-outline.md`)

Out:
- No tag/publish/deploy inside `add.py` — the engine records; the human ships (tool-agnostic); design-for-failure (timeouts/retries/rollback) lives in the human's pipeline, not the method tool.
- `--force` never overrides `release_security_open` — the security HARD-STOP is the one un-forceable reject.
- No new gated phase — release ships as an on-demand guide; the frozen 9-phase ladder is untouched (like `graduate.md`/`design.md`).
- No coupling to graduation — release and stage stay orthogonal; this milestone does not change `stage`/`graduate.md`.
- Un-release / yank flow deferred — a yanked version is a NEW ledger row; reverting attribution is OUT.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Engine records; human ships** — `add.py release` writes CHANGELOG + ledger + attribution; it never tags/publishes/deploys (consistent with the `capability-as-prose-recommendation-engine-tool-agnostic` convention and "the engine never renders/spawns").
- **Security HARD-STOP at the cut** — `release_security_open` refuses with NO `--force` override — the only un-forceable reject (mirrors verify's non-negotiable: a security finding is never auto-passed).
- **Notes draw from folded deltas** — release runs AFTER `fold.md`; the lifecycle order is `milestone-done → fold → compact → archive → (repeat ≥1×) → release → watch`. The changelog surfaces consolidated learnings, not raw open lessons.
- **Append-only ledger (newest-first)** — `RELEASES.md` rows are never rewritten (like §Key Decisions); a yank/supersede is a new row. The ledger IS the attribution source: a milestone is "released" iff it appears in a RELEASES.md row — so the cue never reads (compacted) milestone files.
- **Release bundles ≥1 milestone, orthogonal to stage** — not 1:1 with `milestone-done`; you cut releases at every stage (prototype preview · mvp beta · prod GA).
- **Glossary deltas** — `release` (a versioned user-facing cut bundling ≥1 closed milestone) · `release altitude` (the 5th scope level) · `readiness floor` (the engine-enforced pre-cut gate) · `RELEASES.md ledger` (the append-only release trail) · `hotfix release` (a narrowed PATCH re-entering via change-request).

## Shared / risky contracts (freeze these first)
- **the release flow contract** (the 7 steps + the cue + the order-after-fold + the tool-agnostic stance) -> owning task `release-guide`
- **the RELEASES.md ledger schema + attribution-read** (the row shape + how `status`/`release-report` knows a milestone is unreleased) -> owning task `release-report`
- **the readiness-floor contract** (the 4 reject codes + the un-forceable security stop) -> owning task `release-command`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] release-guide      depends-on: none            — author `release.md`: the 7-step RELEASE flow, the cue, the floor, invariants, depth-by-stage, the dogfooded 1.5.0 worked example; wire a "Beyond the bundle" reference from `SKILL.md`. Freezes the release-flow contract.   ✓ PASS 2026-06-16 (release-guide suite 11/11 + engine suite 1152 green; release.md ×3 md5-identical + SKILL cross-ref; both wording fences clean)
- [x] release-report     depends-on: release-guide   — `add.py release-report` read-only: the five record-sets + `--json` + the `→ releasable: N` status cue. Freezes the RELEASES.md ledger schema + attribution-read.   ✓ PASS 2026-06-16 (release-report suite 8/8 + engine suite 1152 green; cmd_release_report + release_data + _releasable + RELEASABLE_CUE/RELEASES_FILE ×3 md5-identical, engine_pin re-aimed d0d9b1ed; dogfood `→ releasable: 38` proven; attribution = RELEASES.md membership, fail-open)
- [x] release-command    depends-on: release-report   — `add.py release <version>` guarded record-only: CHANGELOG prepend + RELEASES.md append-only row + milestone attribution + the 4 reject codes (security un-forceable). Freezes the readiness-floor contract.   ✓ PASS 2026-06-16 (risk:high, conservative gate; release-command suite 12/12 + engine suite 1152 green; cmd_release + _build_in_flight + _prepend_block + the 2 renderers ×3 md5-identical, engine_pin re-aimed 9c479010; FULL-lifecycle dogfood validated all handoffs — close→cue→release→clear→archive→cue→release→refuse→security-un-forceable)
- [x] release-docs-align depends-on: release-command   — propagate to book (ch.16 `16-releasing.md`) + GLOSSARY (5 entries) + ×3 trees byte-identical + parity tests.   ✓ PASS 2026-06-16 (conservative gate; release-docs-align accord suite 6/6 + full engine suite 1158 green; 16-releasing.md ×3 trees md5-identical + .add/docs synced; 5 glossary entries + Scope-level enumeration extended; README index ×3 + repo-root ToC; both wording fences clean; NO engine change)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `release.md` walks the 7-step RELEASE flow (cue → gather → draft → floor → confirm → cut → watch) and is referenced from `SKILL.md`   (← release-guide)   (verify: test asserts release.md names the 7 ordered steps AND grep finds a release.md reference in `SKILL.md` across the 3 trees)   ✓ 2026-06-16 — release-guide suite 11/11; release.md ×3 md5-identical + the "Beyond the bundle" SKILL.md cross-ref present in all trees
- [x] `add.py release-report` clusters the five record-sets and `status` prints `→ releasable: N milestone(s)` when an archived milestone is unreleased, then goes silent after a recorded release   (← release-report)   (verify: test_release_report asserts the five labeled sets in `--json` AND a dogfood scenario where status shows the cue then clears post-release)   ✓ 2026-06-16 — test_release_report 8/8 (test_release_data_five_sets + test_cue_fires_and_clears + test_attribution_read); cue clears on a RELEASES.md fixture row (the real writer is release-command/task 3)
- [x] `add.py release <version>` records a cut (CHANGELOG entry + append-only RELEASES.md row + milestone attribution) and refuses on the floor — `release --force` still refuses `release_security_open`   (← release-command)   (verify: test_release asserts a green cut writes all three artifacts AND each reject code fires AND `--force` cannot override the security stop)   ✓ 2026-06-16 — test_release_command 12/12 (green cut writes CHANGELOG+RELEASES+attribution · all 4 reject codes · --force can't override release_security_open · 2nd-write rollback) + full-lifecycle dogfood
- [x] Book ch.16 describes the release scope level, the ×3 trees are byte-identical + parity tests pass, and release · release scope level · readiness floor · RELEASES.md ledger · hotfix release have glossary entries   (← release-docs-align)   (verify: test_book_parity + test_release_docs_accord green AND grep finds all 5 glossary terms)   ✓ 2026-06-16 — test_release_docs_accord 6/6 + test_book_parity + test_bundle_parity green; 5 glossary headwords present + Scope-level enumerates the release level
