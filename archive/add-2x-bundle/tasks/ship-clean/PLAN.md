# TASK: prepublishOnly guard + add.py project (v3 ship-clean residuals)

slug: ship-clean · created: 2026-06-03 · stage: mvp
autonomy: conservative   <!-- bundles a publish-path change (npm publish is hard to reverse) -> high-risk guard forces conservative; human gates Verify. -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One-approval front (v7): the AI drafts Spec + Scenarios + Contract + Tests as ONE
> bundle; the human gives a single approval AT the frozen contract (the seam). Below
> is that draft. Nothing builds until you approve §3.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the two v3 ship-clean residuals (from the MILESTONE scope audit), bundled —
  (A) **prepublishOnly** — `add-method/package.json` gains a `prepublishOnly` hook that runs the
      manifest guard (`test_packaging`), so `npm publish` from a dirty/incomplete tree is blocked.
  (B) **`add.py project`** — a read-only subcommand that prints `.add/PROJECT.md` (the "read first"
      foundation) in one command.
Framings weighed:
  (A) prepublishOnly -> manifest guard (chosen, per milestone) · prepublishOnly -> full `npm test` (rejected:
      broadens frozen scope + redundant with the tag-time CI run) · a git pre-commit hook (rejected: wrong seam)
  (B) print contents (chosen) · open in $EDITOR (rejected: interactive-spawn complexity, ~0 AI-workflow value,
      against the project's minimalism) · print just the path (rejected: `status` already prints the path)

Must:
  (A) `add-method/package.json` has `scripts.prepublishOnly` whose command runs the manifest guard
      (`test_packaging`) via the project's unittest runner — so a tarball with dev junk or a missing
      runtime file reds the hook and `npm publish` aborts
  (A) the hook command is npm-free to execute (python + unittest only); the manifest guard's own
      npm-backed checks already self-skip when npm is absent (honest skip, never a false green)
  (B) `add.py project` prints the full text of `.add/PROJECT.md` to stdout and exits 0
  (B) it is strictly READ-ONLY — never writes state.json or any file
Reject:
  (A) `prepublishOnly` absent / misspelled / pointing at no real test -> the test for (A) goes RED
  (B) `.add/PROJECT.md` missing -> print a clear error to stderr naming the file and exit non-zero
      (fail-closed) -> "missing_foundation"
  (B) no `.add/` root at all -> `_require_root()` already dies with the standard message (reused, not re-implemented)
After:
  - a maintainer cannot `npm publish` a dirty/incomplete tree by mistake — the manifest guard runs at the publish seam
  - in one command a reader sees the foundation that every task builds on, without hunting for the path

Assumptions — least-sure first:
  ⚠ [test] the (A) proof is a WIRING linkage (the hook runs the guard that reds on a dirty tarball), NOT a
    live `npm publish` — least sure because we cannot publish in a test; if wrong (the hook is present but
    npm ignores it), a dirty publish could still slip. Mitigation: the test runs the actual hook command and
    asserts it executed ≥1 manifest test and exited 0, so it reds on broken/misspelled wiring — the strongest
    npm-free proof available.
  - [x] prepublishOnly (not the deprecated `prepublish`) is the publish-only hook — confirmed (runs on `npm publish`, not on install/pack)
  - [x] `package.json` is single-copy (add-method/) — confirmed: no `_bundled/` package.json, `prepare_bundle.py` never copies it; so (A) is NOT a three-tree change. (B) IS — `cmd_project` syncs all three add.py trees + bundle regen.
  - [x] `add.py init` creates `.add/PROJECT.md` (in SETUP_FILES) — confirmed; the (B) happy-path test can rely on it

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
# --- Concern A: prepublishOnly wired to the manifest guard ---
Scenario: the publish hook is present and wired to the manifest guard
  Given add-method/package.json
  When I read scripts.prepublishOnly
  Then it exists and its command runs test_packaging (the manifest guard)
  And deleting or misspelling it makes this check fail   # reject: hook absent/misspelled

Scenario: the publish hook actually runs the manifest guard
  Given the prepublishOnly command from package.json
  When I run it as a subprocess from the package root on the clean tree
  Then it executes at least one manifest-guard test and exits 0
  And nothing is published (it is a guard, not a publish)

# --- Concern B: add.py project prints the foundation ---
Scenario: project prints the foundation
  Given a freshly-initialised .add project (PROJECT.md exists)
  When I run `add.py project`
  Then stdout contains the PROJECT.md heading text and the exit code is 0
  And state.json is unchanged   # read-only

Scenario: project fails closed when the foundation is missing
  Given a .add project whose PROJECT.md has been removed
  When I run `add.py project`
  Then the exit code is non-zero and stderr names the missing foundation file   # missing_foundation
  And nothing is written to disk
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
(A) add-method/package.json  (single copy — NOT bundled, no tree parity)
    scripts.prepublishOnly = "python3 -m unittest discover -s tooling -p 'test_packaging.py'"
    - runs the manifest guard at the `npm publish` seam (fires on publish only, not install/pack)
    - npm-free to execute; test_packaging's npm-backed asserts self-skip when npm is absent
    - a dirty/incomplete tarball reds test_packaging -> non-zero exit -> publish aborts (fail-closed)

(B) add.py project        (new read-only subcommand; THREE-tree change + bundle regen)
    no args, no flags.
    root = _require_root()                      # reuses the standard no-.add/ death
    reads  .add/PROJECT.md ; writes NOTHING
    PROJECT.md exists   -> print its full text to stdout, exit 0
    PROJECT.md missing  -> _die("...") to stderr naming the file, non-zero exit   (code: missing_foundation)
    subparser: sub.add_parser("project", help="print .add/PROJECT.md (the read-first foundation)")
               .set_defaults(func=cmd_project)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- HUMAN-approved at the seam — AskUserQuestion "Approve — freeze & build", 2026-06-03; AI drafted, human froze. Both least-sure flags accepted as stated. Changing it now = change request back to SPECIFY. -->
Least-sure flag surfaced at freeze:
  ⚠ [test] (A) is proven by WIRING linkage, not a live `npm publish` — the hook is run as a subprocess and
    asserted to execute the guard + exit 0; it reds on broken/misspelled wiring, but it cannot prove npm
    itself honors the hook (cost if wrong: a dirty publish could slip). This is the strongest npm-free proof.
  ⚠ [contract] (B) prints CONTENTS (not path, not $EDITOR) — minimal by the project's value + "prints or opens"
    in the milestone; if a maintainer wanted a scriptable path, `status` already prints it.
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the least-sure flag surfaced. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: one test per scenario (4), behavioral (each reds for a REAL regression, not a file edit).
Plan (one test per scenario, asserting behavior not internals):
  - test_prepublish_hook_wired_to_manifest_guard: read package.json / assert scripts.prepublishOnly exists
    AND its command references the manifest guard (test_packaging) — reds if the hook is deleted/misspelled
  - test_prepublish_hook_runs_the_guard: subprocess-run the prepublishOnly command from add-method/ /
    assert it ran ≥1 test ("Ran [1-9]") AND exit 0 — reds if the command points at no real test (npm-free;
    inner npm checks self-skip)
  - test_project_prints_foundation: init temp project / run `project` / assert PROJECT.md heading in stdout +
    exit 0 + state.json unchanged
  - test_project_missing_foundation_fails_closed: init, delete PROJECT.md / run `project` / assert non-zero
    exit + stderr names the file + nothing written

Tests live in: `add-method/tooling/test_ship_clean.py` (the tooling-test home; imports add.py, runs in the
suite). MUST run red — prepublishOnly absent + no `project` command — before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): (A) edit ONLY the `scripts` block of add-method/package.json — touch no other
manifest field. (B) `cmd_project` is read-only (no save_state); keep all three add.py trees byte-identical and
regen the bundle. Do not touch any frozen contract or weaken a test.
Code lives in: `add-method/tooling/add.py` (+ `.add/tooling/add.py` + `_bundled/` regen) · `add-method/package.json`
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib + npm config only); ask if unclear.

Build checklist:
  - [ ] add `cmd_project` + its subparser to canonical add-method/tooling/add.py
  - [ ] sync to .add/tooling/add.py (byte-identical)
  - [ ] regen bundle: python3 add-method/scripts/prepare_bundle.py
  - [ ] add scripts.prepublishOnly to add-method/package.json
  - [ ] full suite green incl. test_tree_parity / test_bundle_parity / test_cospecify_scaffold

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 260 green (4 new in test_ship_clean + project registered in test_min_pillar)
- [x] coverage did not decrease — +4 behavioral guards; test_min_pillar LIFECYCLE strengthened (project added)
- [x] no test or contract was altered during build — §3 FROZEN untouched; the only test edit is a registration
      (project → LIFECYCLE), a strengthening, not a weakening
- [x] concurrency / timing — n/a (cmd_project is a local file read; prepublishOnly is npm config; no shared state)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib + npm config only; read-only
- [x] layering & dependencies follow CONVENTIONS.md — cmd_project mirrors cmd_deltas/cmd_status; three add.py
      trees byte-identical (md5 fb14391…), bundle regenerated; package.json single-copy (no parity)
- [x] a person reviewed and approved the change  — conservative dial: ESCALATED to human; human recorded PASS at this gate

Evidence (run-gathered; the run STOPS here — auto-PASS disabled by the conservative dial):
- DEMO (A): `npm run prepublishOnly` → "Ran 4 tests … OK", exit 0 — the hook executes the manifest guard live
- DEMO (B): `add.py project` on the real repo → prints PROJECT.md, exit 0
- DEMO (B-reject): missing PROJECT.md inside a valid .add → exit 1, empty stdout,
  stderr "add: error: missing foundation: .add/PROJECT.md (...)" — fail-closed, names the file
- Residue: none security / concurrency / architecture (read-only print + publish-config). The ⚠ [test] limit
  stands: (A) proves the WIRING (hook runs the guard that reds on a dirty tarball), not a live `npm publish`.

### GATE RECORD
Outcome: PASS   (conservative dial: ESCALATED to human; human recorded this gate after evidence + diff review)
Evidence: full suite 260 green (ship-clean 4/4); DEMO (A) prepublishOnly runs the manifest guard live
          ("Ran 4 tests … OK", exit 0); DEMO (B) `add.py project` prints PROJECT.md (exit 0); DEMO (B-reject)
          missing foundation → exit 1, stderr names the file. Three add.py trees byte-identical (md5 fb14391…).
          Accepted limitation (surfaced + approved at freeze): (A) is wiring-linkage proof, not a live `npm publish`.
Reviewed by: Tin Dang (human, AskUserQuestion gate decision) · date: 2026-06-03

<!-- conservative dial: the run STOPS here for a human (publish-path change). A security finding is ALWAYS HARD-STOP. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether a dirty publish ever slips past prepublishOnly; whether `project` is reached for over re-reading the path from `status`
Spec delta for the next loop: proving a publish-TIME guard without publishing is inherently partial — the
wiring-linkage test reds on broken wiring but cannot prove npm honors the hook; a stronger still-publish-free
probe (`npm pack` + tarball-content assertion) is the next rung if this ever bites.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a publish-time hook can be proven WITHOUT publishing — run the hook command as a subprocess
  and assert it executed the guard and exited 0; it reds on broken/misspelled wiring but cannot prove npm
  honors the hook (evidence: test_prepublish_hook_runs_the_guard; ship-clean §6 ⚠ wiring-vs-live limit).
- [ADD · folded] a planned-but-unscaffolded milestone (v3, 0 TASK.md) is best closed by a SCOPE AUDIT against
  shipped code — 3 of 5 original tasks were already superseded/delivered/obsolete; only 2 residuals were real
  (evidence: v3 MILESTONE.md scope-audit table, 2026-06-03).
