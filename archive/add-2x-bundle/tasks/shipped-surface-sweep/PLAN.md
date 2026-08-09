# PLAN: A declared shipped-surface set that CI sweeps for retired references

slug: shipped-surface-sweep · created: 2026-07-24 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the "sweep set" a retirement needs becomes EXECUTABLE — the set of shipped surfaces is derived from the packaging manifests themselves, and CI sweeps every one of them for references to book chapters that no longer exist.
Framings weighed: derive the surface set from package.json `files` + MANIFEST.in (chosen — a hand-written surface list is itself a thing that drifts, which is the very failure mode being fixed; the packaging manifests already ARE the definition of "shipped", so the sweep set cannot go stale without the package changing) · a per-milestone SWEEP-SET.md the close checks (rejected — process ceremony that relies on the same human diligence that already missed three surfaces; a doc cannot fail a build) · keep the check task-local (rejected — CI runs only `tooling/`, so it stops running the moment the task archives)
Must:
<must>
  - M1 every book-chapter reference in a shipped prose surface resolves to a chapter that exists in docs/
  - M2 the swept surface set is DERIVED from the packaging manifests, not hand-maintained in the test
  - M3 the guard lives where CI actually runs it (tooling/test_*.py, unittest-discoverable)
  - M4 a failure names the offending file and the dead reference, so it is actionable without investigation
</must>
Reject:
<reject>
  - a shipped prose surface citing a book chapter absent from docs/ -> "dead_chapter_ref"
  - a surface set that disagrees with what the packages actually ship -> "stale_surface_set"
</reject>
After:
<after>
  - the defect class that put a 404 in the published v2.3.0 tarballs cannot recur silently
  - adding a new shipped path to package.json or MANIFEST.in automatically brings it under the sweep
</after>
Boundary: chapter references appear in TWO shapes across shipped prose — published-site URLs (`pilotspace.github.io/ADD/nn-slug/`) and repo-relative doc paths (`docs/nn-slug.md`); both map to `add-method/docs/nn-slug.md` and both must be swept.
<assumptions>
  ⚠ THIS TASK FINDS NO NEW DEFECTS — a full sweep of 948 shipped files returned zero dead references before any code was written. Its entire value is durability: the equivalent check currently lives task-local and CI never runs it, so once `getting-started-descenarios` archives the class reopens. If that reasoning is wrong, this task is pure ceremony and should be dropped rather than shipped.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
NEW: add-method/tooling/test_shipped_surface_sweep.py   (the only file this task adds)

shipped_surfaces() — the executable sweep set, DERIVED not declared, THREE channels:
    add-method/package.json -> files[]        (npm tarball)
    add-method/MANIFEST.in  -> include/graft  (PyPI sdist)
    docs/ when mkdocs.yml exists              (GitHub Pages — pages.yml)
    drop negations (!…) and exclude rules; resolve each to real paths;
    keep prose (.md/.tmpl/.txt/.json/.js/.py/.yml/.css/.html)
  => the set cannot drift from what actually ships without a packaging manifest
     changing, which is the point.

  The docs-site channel was found while INSPECTING the derivation before the
  freeze: docs/ is in neither tarball manifest, so a tarball-only sweep would
  have missed every chapter-to-chapter link on the published site — the exact
  blind spot that produced this task. 666 files -> 693 with the channel added.

chapter_refs(text) — both shapes:
    https://pilotspace.github.io/ADD/<nn-slug>/     (published-site URL)
    docs/<nn-slug>.md                               (repo-relative path)
  => each maps to add-method/docs/<nn-slug>.md

ASSERT: every referenced <nn-slug> has a file in add-method/docs/.
  On failure the message names  <file> -> [<dead-slug>, …]

Runs under CI's existing `unittest discover -s tooling -p 'test_*.py'`
(ci.yml:53, publish.yml:85) — no workflow change needed.

NOT changed: no template, no engine module, no pin. Additive test only.
```

Grounding anchors (verified in-context): package.json `files` (14 entries incl. README/GETTING-STARTED/CHANGELOG/SECURITY) · MANIFEST.in (graft `src/add_method/_bundled` + 5 includes) · add-method/docs/ holds 27 chapters · ci.yml:53 and publish.yml:85 both run `unittest discover -s tooling` · a full pre-build sweep of 948 shipped files found ZERO dead references.

HONEST FRAMING: this task fixes nothing today. The dead link it guards against was already fixed in `getting-started-descenarios`; that task's check is task-local and CI never runs it. This makes the guard durable and derives its scope from packaging so future surfaces are covered automatically.

Target (measurable): shipped files swept >= 600 (693 at freeze, across 3 channels) · dead references 0, asserted rather than assumed · surface set derived from 3 packaging sources, 0 hand-listed paths · guard green under CI's own `unittest discover` · the detector proven to name a dead slug AND to stay silent on a live one (no crying wolf) · the full tooling suite stays green.

Floor note: the target originally read ">= 900 (948 at drafting)", taken from an ad-hoc pre-task sweep that counted differently-scoped files. Inspecting the real derivation before the freeze gave 693; the floor is set to 600 with churn headroom. Corrected while still DRAFT — pre-freeze drafting, not a frozen-contract edit.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/test_shipped_surface_sweep.py` `./tests/`
Regression floor: the full `tooling/` suite via CI's `unittest discover` (2285 tests at last run) must stay green — this task is additive, so any red is caused by it.
Persona (optional): `.add/personas/methodology-engine-dev.md` — deterministic, fail-loud, derives its inputs rather than restating them.

Strategy (preferred, not hard): build the derivation first and PRINT what it resolves to, so the swept set is inspected rather than trusted; then assert zero dead references; then mutation-prove the guard by injecting a dead reference into a real shipped file and confirming it is named in the failure.

Least-sure flag surfaced at freeze: [test] whether deriving the surface set from packaging manifests is genuinely more robust than a short hand-written list, or just more machinery. The derivation has to parse two formats (a JSON allowlist with `!` negations, and MANIFEST.in's graft/include/global-exclude grammar) — that parser is itself code that can be wrong, and if it silently resolves to FEWER files than really ship, the guard passes while covering less than it claims. Mitigated by M-target asserting a FLOOR on files swept (>= 900) so silent under-coverage fails loudly rather than passing quietly; that floor is the single most important line in this task.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_every_shipped_chapter_ref_resolves: no shipped prose file references a chapter absent from docs/ · covers: M1, R:dead_chapter_ref
  - test_surface_set_derives_from_packaging: the swept set comes from package.json + MANIFEST.in, and sweeping fewer than the floor fails · covers: M2, R:stale_surface_set
  - test_known_shipped_files_are_covered: the surfaces that actually shipped the v2.3.0 404 (GETTING-STARTED.md, README.md, skill/, templates/) are each in the swept set · covers: M2
  - test_failure_message_names_file_and_ref: an injected dead reference produces a message naming the file and the slug · covers: M4
</test_plan>

Kind: engine (regression guard). NO check here can be red-first in the normal sense — a full sweep found zero dead references BEFORE any code was written, which is the honest state of the repo after the three preceding tasks. Red-first duty is therefore discharged by MUTATION, actually executed, not asserted: a dead chapter reference is injected into a real shipped file, the guard must go red and name it, and the file is restored. test_failure_message_names_file_and_ref bakes that mutation into the suite itself using a temp file, so the guard's own failure path stays permanently exercised instead of being a one-off manual step.

M3 (the guard runs in CI) is verified by CONSTRUCTION + evidence, not by a self-referential test: the file matches `tooling/test_*.py`, and §6 records an actual `unittest discover` run collecting it.

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, and the "print what it resolves to before trusting it" step paid for itself twice. First it showed 666 files against a drafted floor of 900 — the floor was wrong, taken from a differently-scoped ad-hoc count. Second, inspecting the per-root breakdown showed `docs/` was absent entirely: the book is in NEITHER tarball manifest, because it ships via GitHub Pages. A tarball-only sweep would have passed while never looking at a single book chapter — the same blind spot that created this task. The docs-site channel was added (666 -> 693) and the floor corrected to 600, both while still DRAFT.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — FULL suite via CI's runner: **2289 tests, OK, exit 0** (213s), up from 2285 by this task's 4
- [x] coverage did not decrease — additive only; no file outside the new test was touched
- [x] no test or contract was altered during build — the guard and the contract were both settled before the freeze; nothing edited after it
- [x] the green was EARNED, not gamed — this guard is green from birth, so green alone proves nothing; it was MUTATION-PROVEN by injecting a dead reference into the real add-method/README.md, confirming the failure names `README.md -> 04-step-2-scenarios`, then restoring (git diff clean). The detector is also asserted to stay SILENT on a live chapter, so it cannot pass by crying wolf.
- [x] concurrency / timing — n/a, a read-only filesystem sweep
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (json/re/pathlib/unittest); reads files, writes none
- [x] layering & dependencies — `tooling/test_*.py`, matching CI's discover pattern; no workflow change needed
- [x] a person reviewed and approved the change — Tin Dang approved the freeze

TARGET — met:
  · files swept 693 >= floor 600 ✓ across 3 channels ✓
  · dead references 0, ASSERTED over all 693 (not assumed) ✓
  · hand-listed paths: 0 — the set derives from package.json, MANIFEST.in and mkdocs.yml ✓
  · green under CI's own `unittest discover` ✓ · detector names a dead slug AND ignores a live one ✓
  · full tooling suite green ✓ (2289 OK)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) the central risk was a guard that sweeps almost nothing and passes forever — probed by printing the resolved set and its per-root breakdown BEFORE freezing, which is exactly what exposed the missing docs/ channel and the wrong floor; the MIN_SWEPT_FILES floor is now the assertion that keeps that risk closed; (2) a green-from-birth guard proves nothing, so its failure path was exercised against a real shipped file, not a fixture; (3) the "crying wolf" inverse was checked too — a live chapter reference must produce no finding, else the guard would be trivially satisfiable; (4) additivity confirmed by the full suite rising exactly 2285 -> 2289 with zero failures, so nothing existing was perturbed.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose derive the surface set from package.json `files` + MANIFEST.in; rejected a per-milestone SWEEP-SET.md the close checks (rejected — process ceremony that relies on the same human diligence that already missed three surfaces; a doc cannot fail a build) · keep the check task-local (rejected — CI runs only `tooling/`, so it stops running the moment the task archives)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, and the "print what it resolves to before trusting it" step paid for itself twice. First it showed 666 files against a drafted floor of 900 — the floor was wrong, taken from a differently-scoped ad-hoc count. Second, inspecting the per-root breakdown showed `docs/` was absent entirely: the book is in NEITHER tarball manifest, because it ships via GitHub Pages. A tarball-only sweep would have passed while never looking at a single book chapter — the same blind spot that created this task. The docs-site channel was added (666 -> 693) and the floor corrected to 600, both while still DRAFT.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · seeded] the sweep-set delta from `fold-residue-engine-guide` is DELIVERED as executable code rather than a process document — the surface set derives from package.json, MANIFEST.in and mkdocs.yml, so a retirement's blast radius is computed, not remembered (evidence: 693 files swept in CI, 0 hand-listed paths)
- [SPEC · open] the sweep covers BOOK-CHAPTER references only; the same class exists for other cross-references in shipped prose (skill guide filenames, persona slugs, `add.py` verb names in docs). Each would need its own resolver, and only the chapter one has actually bitten so far — deliberately not pre-built (evidence: the 3 residuals this session were 1 chapter link, 1 flag, 1 phase name; the latter two are now covered by test_template_flag_vocabulary)
- [SPEC · open] `docs/` ships on a THIRD channel (GitHub Pages) that neither packaging manifest describes — any future "what do we ship" reasoning must count it, or it will be invisible again (evidence: a tarball-only derivation resolved 666 files and looked at zero book chapters)

### Competency deltas
- [TDD · open] a guard that is green from birth proves nothing until its failure path is exercised — mutation against a REAL shipped file, plus the inverse check that a valid reference produces no finding, is what converts "the test passes" into "the test would catch this" (evidence: injected ref produced `README.md -> 04-step-2-scenarios`; restored clean)
- [SDD · open] PRINT a derived set before trusting it — inspecting the resolution caught both a wrong floor (900 vs a real 693) and an entire missing channel (docs/), either of which would have shipped a guard that passed while covering the wrong things (evidence: per-root breakdown showed docs=0 before the fix)
- [ADD · open] derive a sweep set from the artifacts that DEFINE the thing, never restate it — a hand-written surface list would itself be a drift-prone copy, i.e. the very defect being guarded; packaging manifests are the definition of "shipped" and cannot go stale without the package changing (evidence: adding a path to package.json now brings it under the sweep with no test edit)
- [ADD · open] state plainly when a task finds nothing — this one fixed no live defect and its §1 assumption says so, including the condition under which it should have been DROPPED as ceremony rather than shipped; a durability task that oversells itself is how ceremony accumulates (evidence: pre-build sweep returned zero dead references)
