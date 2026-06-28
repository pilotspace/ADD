# TASK: Reconcile roll-up: file-level heal of a partially-gutted tree + an 'N restored / M refreshed' summary

slug: reconcile-rollup · created: 2026-06-28 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `add-method/src/add_method/_installer.py:_clean_replace(src, dest, *, strip_tests=False) -> None` (1097) — wipes dest then `copytree(src→dest)` (orphan-sweeping). CHANGE: return file-level counts by diffing the dest's relative-file-path SET before-wipe vs after-copy (`restored` = a final file ABSENT before; `refreshed` = a final file PRESENT before). The wipe is why before/after must be captured around it.
- `add-method/src/add_method/_installer.py:_reconcile(target_path, bundled_root) -> dict` (1127) — per-tree loop (3 MANAGED trees), logs tree-level "restored (was missing)"/"refreshed". CHANGE: SUM `_clean_replace`'s file counts across trees, log a one-line "→ N restored · M refreshed" rollup, and return `{"restored": N, "refreshed": M, "trees": status}` (was: the pre-status dict).
- `add-method/src/add_method/_installer.py:update()` final message (1331-1333) — surface the rollup ("… skill · tooling · docs refreshed (N restored · M refreshed) …").
- callers of `_reconcile`: `install` (978) · `_update_global` per-project loop (1264) · `update` (1325) — all get the rollup LOGGED by `_reconcile`; only `update` folds it into the headline (per-project, single tree-set).
- `add-method/bin/cli.js:cleanReplaceTree(src, dest, stripTests)` (751) · `reconcile(args, target, srcRoot)` (781) · `cmdUpdate` final message (1145) — the npm twins; same file-level counts + rollup.
- `add-method/src/add_method/_installer.py:_managed_status` (1117) / `bin/cli.js:managedStatus` (767) — tree-level present/missing (UNCHANGED; the rollup is finer, file-level, so it catches a PRESENT-but-gutted tree the tree-level status marks "refreshed").

Context (working folder):
- `.add/milestones/installer-polish/MILESTONE.md` — task `reconcile-rollup` (depends-on: none): "manifest/file-count check that heals a partially-gutted present tree; a one-line 'N restored / M refreshed' reconcile summary". Exit criterion: "reconcile heals a partially-gutted tree and prints an 'N restored / M refreshed' summary". Harvested from the heal-reconcile SPEC delta. NOT a freeze-first contract (unlike global-update-harden).
- Tests (canonical `add-method/tooling/`): `test_update.py` (per-project update / heal-reconcile) · `test_install.py`. NEW `test_reconcile_rollup.py`.

Honors (patterns / conventions):
- **Design-for-failure / orphan-sweep** — `_clean_replace` already wipe+copies (a file removed upstream leaves no orphan); the rollup MEASURES that heal, it does not change the copy semantics. Counting is pure observation (no new failure mode).
- **cli.js ↔ pip parity** (identical counts + identical rollup wording) + **hermetic tests** (tmp dirs, injected env) + the per-tree log lines stay (the rollup is ADDED, not a replacement).
- **Managed-only** — counts cover ONLY the 3 MANAGED trees (skill·tooling·docs); user data is never touched or counted.

Anchors the contract cites: `_clean_replace` (new file-count return) · `_reconcile` (rollup return + "N restored · M refreshed" log) · `update` (headline surface) · `bin/cli.js:cleanReplaceTree`/`reconcile`/`cmdUpdate` twins · `_managed_status` (tree-level, unchanged).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: reconcile-rollup — make a reconcile REPORT a file-level "N restored · M refreshed" roll-up so a partially-gutted managed tree's heal is visible (today only WHOLE-tree missing/present is shown).
Framings weighed: file-level count via before/after relative-path SET diff around the existing wipe+copy (chosen) · per-tree-only (status quo — misses a present-but-gutted tree) · content-hash diff to split "changed" from "rewritten" (rejected: clean-replace rewrites all; no manifest needed, over-scoped)
Must:
<must>
  - `_clean_replace(src, dest, *, strip_tests)` returns file-level counts: snapshot dest's set of relative FILE paths before the wipe; after the copy(+strip), `restored` = a final file whose rel-path was ABSENT in the before-set, `refreshed` = a final file whose rel-path WAS in the before-set. Counts FILES (leaves), not dirs. Copy semantics are UNCHANGED (still wipe+copytree, orphan-sweeping).
  - `_reconcile(target, bundled)` SUMS the per-tree counts across the 3 MANAGED trees, logs ONE rollup line "→ N restored · M refreshed", and returns `{"restored": N, "refreshed": M, "trees": <pre-status>}`. The existing per-tree log lines stay.
  - `update()` folds the rollup into its final headline: "… skill · tooling · docs refreshed (N restored · M refreshed) · your project state untouched."
  - A PARTIALLY-GUTTED present tree (tree exists, some files deleted) is healed (already true) AND its restored files are COUNTED — so the rollup shows restored>0 even when `_managed_status` calls the tree "present/refreshed".
  - A fully-missing tree counts ALL its files as restored; a fully-present untouched tree counts all as refreshed, restored=0.
  - `bin/cli.js` twins (`cleanReplaceTree` → counts, `reconcile` → rollup log+return, `cmdUpdate` → headline) compute the rollup the SAME way and emit the SAME `(N restored · M refreshed)` parenthetical (same `·` U+00B7). Parity of the COUNTS holds wherever the reconciled tree-set matches — i.e. the default path. The pre-existing Node-only `--no-skill` skip (Node `reconcile` drops `skill/add`; Python `update` always copies it) and the pre-existing surrounding-headline phrasing ("docs refreshed" vs "managed layer reconciled") are NOT in scope for this additive-observation task (closing them would change copy behavior) — both filed as §7 deltas.
  - Counting touches ONLY managed trees; user data is never read or counted.
</must>
Reject:
<reject>
  - (no new user-facing rejection — this is additive observation over an existing, already-guarded copy path; a copy/IO failure keeps the EXISTING behavior: `_reconcile`'s caller already maps an OSError to the existing "cannot write …" fail. The rollup is computed only on a successful copy.)
</reject>
After:
<after>
  - every reconcile (install · update · update --global per project) logs a "→ N restored · M refreshed" rollup; `update`'s headline carries the `(N restored · M refreshed)` parenthetical; the numbers equal the count of managed FILES absent-before (restored) vs present-before (refreshed); pip and npm produce identical counts on the default path (where they reconcile the same tree-set) and surface the same parenthetical wording.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "refreshed" = a managed file that was PRESENT before the wipe (regardless of whether its bytes changed) — lowest confidence because a user reading "M refreshed" might expect M = files whose CONTENT changed, not "files re-written"; if wrong: the number reads higher than a content-diff would (every present file is "refreshed" since clean-replace rewrites all). Mitigation: the milestone asks for a heal/file-count summary, not a content-diff; "refreshed = re-materialized" matches the wipe+copy reality and needs no manifest. Surfaced at the freeze.
  - [ ] counting FILES (recursive leaves), not directories — a gutted subdir's files each count; matches "manifest/file-count".
  - [ ] the skill tree copied to a separate claude dir (when applicable) is out of THIS rollup (the rollup covers the in-`.add/` MANAGED trees `_reconcile` walks); low cost.
  - [ ] `_reconcile`'s changed return type (rollup dict, was pre-status dict) has no other reader that depends on the old shape — verify at build by grepping call-sites (install/_update_global ignore the return; update will read it). CONFIRMED at build: only `update` reads it.
  - [x] pip↔npm parity is scoped to the DEFAULT path + the parenthetical wording — RESOLVED @ v2 (a refute-read caught the v1 INV over-claiming): the surrounding-headline phrasing already diverged at HEAD and the Node `reconcile` `--no-skill` skip is pre-existing; both are out of this additive task's scope and filed as §7 deltas. The rollup faithfully counts each twin's actual reconcile.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a partially-gutted present tree is healed and its restored files counted   # Must 1 + Must 4
  Given an installed project whose tooling/ tree is present but a subdir of it was deleted (gutted)
  When I run `update`
  Then the deleted files are restored on disk AND the rollup counts them as restored (restored > 0)
  And the tree-level line still says "refreshed" for tooling (present), while the rollup reflects the file-level heal

Scenario: a fully-missing tree counts all its files as restored   # Must 5
  Given an installed project whose docs/ tree was entirely removed
  When I run `update`
  Then every docs/ file is restored and the rollup's restored count includes all of them
  And refreshed counts the files of the still-present trees

Scenario: a fully-intact project refreshes everything, restores nothing   # Must 5
  Given an installed project with all 3 managed trees fully present
  When I run `update --force`
  Then the rollup reports restored = 0 and refreshed = the total managed file count
  And no managed file is missing afterward

Scenario: update's headline carries the rollup   # Must 3
  Given an installed project with one gutted tree
  When I run `update`
  Then the final "ADD updated …" line includes "(N restored · M refreshed)" with the real counts

Scenario: _clean_replace returns the file-level counts   # Must 1 (unit)
  Given a dest tree missing 2 files that exist in src, and 3 files present in both
  When I call _clean_replace(src, dest)
  Then it returns restored = 2 and refreshed = 3
  And dest now contains every src file (heal) with no orphan left behind

Scenario: orphan-sweep is unchanged and not miscounted   # Must 1 (copy semantics unchanged)
  Given a dest tree holding an extra file that does NOT exist in src
  When I call _clean_replace(src, dest)
  Then the orphan file is gone (swept) and is counted as neither restored nor refreshed
  And the returned counts cover only files present in the final tree

Scenario: parity — cli.js prints the same rollup   # Must 6
  Given the npm cli.js update path on a project with a gutted tree
  When I run `node cli.js update`
  Then cli.js prints a "→ N restored · M refreshed" rollup and a headline with "(N restored · M refreshed)" matching the pip counts
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
reconcile roll-up  [CLI: `pilotspace-add update` · `node bin/cli.js update` · also install / update --global]

  _clean_replace(src, dest, *, strip_tests=False) -> dict        # was -> None
    before = { rel path of every FILE under dest }   (∅ if dest absent)   # captured BEFORE the wipe
    … wipe(dest) + copytree(src→dest) + (strip_tests ? drop test_*.py + __pycache__) …  # UNCHANGED
    after  = { rel path of every FILE under dest }                        # the FINAL tree (post-strip)
    return { "restored": |after \ before|, "refreshed": |after ∩ before| }
    # restored = final file absent before · refreshed = final file present before · orphans (before\after) uncounted

  _reconcile(target_path, bundled_root) -> dict                  # was -> the pre-status dict
    status = _managed_status(target_path)                        # tree-level present/missing (unchanged)
    for sub in MANAGED:  r = _clean_replace(...);  restored += r["restored"];  refreshed += r["refreshed"]
                         # existing per-tree "restored (was missing)" / "refreshed" log lines stay
    _log(f"  → {restored} restored · {refreshed} refreshed")     # the NEW one-line rollup
    return { "restored": restored, "refreshed": refreshed, "trees": status }

  update(...) -> int
    roll = _reconcile(target_path, bundled_root)
    _log("ADD updated {cur} -> {new} · skill · tooling · docs refreshed "
         "({roll['restored']} restored · {roll['refreshed']} refreshed) · your project state untouched.")

Schema / files touched (NO new persisted state — counts are computed in-memory, logged, returned):
  bin/cli.js: cleanReplaceTree -> {restored, refreshed} · reconcile -> rollup log + return · cmdUpdate headline.
  The 3 MANAGED trees only (skill/add · tooling · docs); user data never read/counted.

INV: copy semantics UNCHANGED — restored+refreshed counts never alter what is copied/swept; a gutted tree is
     still fully healed; the rollup is pure observation.
INV (v2): both twins compute the rollup the SAME way and emit the SAME `(N restored · M refreshed)` parenthetical
     (same `·` U+00B7); the COUNTS are equal wherever the two reconcile the same tree-set (the default path). The
     pre-existing Node-only `--no-skill` skip and the pre-existing surrounding-headline phrasing are out of scope
     (closing either changes copy/headline behavior) — filed as §7 deltas. v1 said "identical counts + wording"
     unconditionally; a refute-read showed that over-claimed (both divergences pre-date this task) → re-frozen @ v2.
```

Least-sure flag surfaced at freeze: [contract] the v2 parity INV is now SCOPED (default-path counts + identical parenthetical), not the v1 unconditional "identical counts + wording" — because a refute-read proved the surrounding headline phrasing ("docs refreshed" vs "managed layer reconciled") already diverged at HEAD and Node's `reconcile` `--no-skill` skip is pre-existing, so the rollup can only faithfully count each twin's actual reconcile. Cost if wrong: a reader expects byte-identical headlines across twins; they aren't (and weren't before this task). Low — the counts + parenthetical ARE identical on the path everyone uses; the two divergences are filed as §7 follow-ups. (Prior v1 flag retained: [spec] "refreshed" = present-before-the-wipe, not content-changed — so M reads higher than a content-diff; the restored count is the heal signal that matters.)

Status: FROZEN @ v2 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/bin/cli.js`
Strategy (ordered batches): 1. `_clean_replace` → snapshot before-set (rglob files, rel paths) around the wipe, return {restored, refreshed} from the after-set diff. 2. `_reconcile` → sum across trees, log "→ N restored · M refreshed", return the rollup dict. 3. `update()` → fold the rollup into the headline. 4. mirror in cli.js (cleanReplaceTree counts → reconcile rollup → cmdUpdate headline).
Known-problem fixes: count over the FINAL (post-strip) tree so stripped test_*.py aren't miscounted; capture the before-set BEFORE the rmtree (or it's always empty); a caller that ignored `_reconcile`'s old return (install/_update_global) must not break on the new dict shape — grep call-sites; rel paths must be relative to the tree root (use `Path.relative_to(dest)`), identical convention in JS (`path.relative(dest, f)`).
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): the rollup is PURE OBSERVATION — it must never change which files are copied or swept (counts are derived after the copy, never gate it).
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] reconciling a project whose tooling subdir was deleted restores those files AND the rollup line shows restored>0 — `test_partial_gut_healed_and_counted`: guts `add_engine`, reconciles, asserts `core.py` exists + `restored==2` + "2 restored" in the log
- [x] a fully-intact project re-run reports restored=0 and refreshed = the total managed file count — `test_intact_reconcile_all_refreshed`: 2nd reconcile → restored=0, refreshed=6 (=TOTAL_MANAGED)
- [x] `_clean_replace` returns restored=2/refreshed=3 for a dest missing 2 of 5 src files — `test_returns_restored_and_refreshed` passes
- [x] an orphan (dest file not in src) is swept and counted as NEITHER restored nor refreshed — `test_orphan_swept_not_counted`: orphan gone, restored+refreshed==2 (only final-tree files)
- [x] update's headline reads "(N restored · M refreshed)" with the real numbers — `test_headline_carries_rollup` asserts the regex on the "ADD updated …" line
- [x] both twins compute the rollup identically — `test_pip_restored_equals_files_deleted` + `test_npm_restored_equals_files_deleted`: restored == files-deleted for EACH twin (the v2 INV's provable parity); node prints the same `· U+00B7` parenthetical

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — new symbols referenced: `_tree_files` ← `_clean_replace`; `_clean_replace` return ← `_reconcile` (sums); `_reconcile` return `roll` ← `update` headline. JS: `treeFiles` ← `cleanReplaceTree` ← `reconcile` (sums) ← `cmdUpdate` `roll`. Grepped all call-sites (install/_update_global ignore the return; only update reads it).
- [x] DEAD-CODE (code) — no orphaned symbol: `_tree_files`/`treeFiles` each have exactly one caller; the rollup dict's `trees` key carries the prior pre-status (no field dropped). Confirmed by the independent FIX-CONFIRM reviewer (Check 5).
- [x] SEMANTIC — the v2 INV honesty was the crux: an independent reviewer git-proved BOTH the Node `--no-skill` skip and the headline-phrase divergence pre-date this task (HEAD already had them), so the rollup faithfully counts each twin's actual reconcile; the scoped v2 parity claim (default-path counts + identical U+00B7 parenthetical) is TRUE in both twins' code.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED (after a v2 contract correction — NOT a code change)
By: agent aece70dbd5b483103 (refute) + agent adf0b8a26d10e1234 (FIX-CONFIRM) + self · adversarially checked: count correctness (before-set captured pre-wipe; final-tree/post-strip counted) · Python rglob vs Node walk leaf parity · orphan-sweep not miscounted · broken-symlink no new abort path · `_reconcile` return-shape has no old-shape reader · the partial-gut→restored>0 key claim. The refute found the v1 INV over-claimed "identical counts+wording" → Tin approved re-freeze @ v2 with a scoped, provable parity INV + the `restored==files-deleted` cross-twin test + 2 §7 deltas; the FIX-CONFIRM reviewer git-proved both divergences pre-date the task and the v2 INV is honest + the test non-vacuous.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate on complete evidence; autonomy: auto, non-security additive observation) · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the rollup line `→ N restored · M refreshed` on every reconcile — a non-zero `restored` on a routine `update` means a managed tree was being silently gutted between updates (the heal signal); a mismatch vs the prior tree-set size flags drift.

### Decisions (ADR)
- [AI] specify — chose file-level count via before/after relative-path SET diff around the existing wipe+copy; rejected per-tree-only (status quo — misses a present-but-gutted tree) · content-hash diff to split "changed" from "rewritten" (rejected: clean-replace rewrites all; no manifest needed, over-scoped)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-gate on complete evidence; autonomy: auto, non-security additive observation))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
  - [SPEC · open] reconcile the pre-existing `--no-skill` copy divergence — Node `reconcile` drops `skill/add` under `--no-skill` but Python `update`/`_reconcile` always copies it; pick one behavior so a `--no-skill` reconcile is twin-identical in BOTH copy and count (evidence: refute-read on reconcile-rollup found pip vs npm rollup counts differ under `--no-skill`, a divergence that pre-dates this task)
  - [SPEC · open] unify the `update` headline phrasing across twins ("skill · tooling · docs refreshed" vs "managed layer reconciled") so the v2 INV's wording-parity can be unconditional, not parenthetical-only (evidence: FIX-CONFIRM reviewer git-proved the surrounding phrases already diverged at HEAD)
  - [SPEC · open] consider a `--quiet`/aggregate rollup for `update --global` (today each project logs its own `→ N restored · M refreshed`; a 50-project run is noisy) (evidence: `_update_global`/`cmdUpdateGlobal` call `_reconcile`/`reconcile` per project, each now emitting a rollup line)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [ADD · open] freeze OBSERVABLE behavior, not an over-broad INV — a verify refute-read caught the v1 contract claiming "identical counts + wording" when two divergences pre-dated the task; the honest fix was re-freeze @ v2 to the provable scope + file the rest as deltas, NOT change code or weaken a test (evidence: reconcile-rollup re-frozen v1→v2, code byte-identical across the re-freeze)
  - [TDD · open] a parity test that asserts "output CONTAINS a count" is vacuous for proving cross-twin equality — the `restored == files-deleted` invariant asserted on EACH twin proves identical computation without coupling to differing bundle contents (evidence: the v1 `test_npm_update_prints_rollup` regex-passed despite the twins being able to diverge; replaced by `test_*_restored_equals_files_deleted`)
