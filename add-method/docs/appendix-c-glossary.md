# Appendix C · Glossary

[← Appendix B Prompts](./appendix-b-prompts.md) · [Contents](./README.md) · Next: [Appendix D Worked example →](./appendix-d-worked-example.md)

---

## Terms

**AIDD (AI-Driven Development)** — a method of building software in which an AI agent writes most of the code and people direct and verify the work.

**Artifact** — a durable work product: the spec, the scenarios, the contract, the tests. The artifacts survive; the code is disposable.

**Lesson learned** (formerly "competency delta") — a single learning a loop produces, tagged by which of the five competencies (`DDD · SDD · UDD · TDD · ADD`) it improves, written in a task's OBSERVE phase as `- [<COMPETENCY> · <status>] <learning> (evidence: …)`. Emitted `open` by the AI; the human folds it into a versioned `PROJECT.md` (`folded`) or declines it (`rejected`). The mechanism by which the foundation self-improves instead of drifting. See the `add` skill's `deltas.md`.

**Contract** — the fixed external shape of a feature: interfaces, data structures, names, and error cases. Frozen before the build, it is the surface the AI builds against.

**Co-specification** — how a spec is made in ADD: the AI and the human **brainstorm the shape together** (diverge), the AI **drafts** it, and the human **validates with the AI's advice** (validate). The AI's decisive advice is the *lowest-confidence flag*. It replaces dictation-by-one-side — the human owns the decision, the AI owns surfacing what it does not yet know. See [03 Specify](./03-step-1-specify.md).

**Disposable code** — the view that code is one regenerable implementation of the artifacts, not a durable asset to be preserved.

**Evidence bundle** — the proof attached to a change (passing tests, clean security scan, no coverage loss) that justifies trusting it and may unlock more AI autonomy.

**Foundation version** — a monotonic integer marker in `PROJECT.md` that advances by one each time confirmed lessons learned are consolidated into the foundation. It makes the living documentation's evolution auditable: a rising version with fewer new deltas per milestone is the signal that a competency is converging rather than drifting. Bumped only by the retrospective consolidation (see the `add` skill's `fold.md`).

**Gate** — a checkpoint with an explicit pass/fail exit. Its outcome is `PASS`, `RISK-ACCEPTED`, or `HARD-STOP`.

**Ground (phase-0 preamble)** — the per-task phase *before* Specify in which the AI gathers the real current codebase the task touches — files, symbols, signatures, patterns, conventions — into a lean **grounding map**, surfacing the **anchors** the frozen contract will cite. It is AI-owned and adds no approval (the one approval stays at the contract freeze); it precedes the seven steps as step 0 so the contract, tests, and build are grounded in the code as it actually is, not in assumption. Lives in the `add` skill's `phases/0-ground.md`.

**Grounding map / anchors** — the §0 GROUND artifact: the real files, symbols, and conventions a task touches, plus the **anchors** — the symbols the frozen contract names. Task-specific delta only: it defers to `PROJECT.md` / `CONVENTIONS.md` for architecture and never re-runs the setup brownfield scan. `add.py status` / `check` surface whether the active task's contract is grounded (measure, never block — the contract-freeze checklist asks the human to confirm it).

**`HARD-STOP`** — a gate outcome meaning work cannot proceed; triggered by any failing test or security finding.

**Intake** — the step *before* a task: sizing a raw request into versioned scope by classifying it into one **request bucket**. The AI proposes `{bucket, rationale, command}`; the human confirms. Lives in the `add` skill's `intake.md` (the intake level, above the per-task flow).

**Lowest-confidence flag** (formerly "least-sure flag") — the AI's ranked declaration of the **1–2 things most likely to be wrong** in what it is asking a human to approve, each carrying *why* it is uncertain and *what it costs if wrong* (`⚠ [spec|scenario|contract|test] … — because …; if wrong: …`). It reshapes the old flat assumptions list into a ranked one, so a single approval aims the reviewer's attention at the real risk instead of a flat list of equal-looking ticks. Bundle-wide at the contract-freeze decision point; the §1 assumptions are its first input. If nothing is materially uncertain it still names the single biggest risk — never a blank "none". It makes a genuine review cheap and a lazy one visibly negligent, but cannot *force* the read. The "AI advises" half of **co-specification**.

**Living document** — an artifact expected to change as the loop learns; never frozen forever (the one exception being a versioned contract, which changes only via a change request).

**Onboarding** (formerly "on-ramp") — the path a new user walks from install to their first milestone: install → `/add` → describe the goal → the agent runs intake (sizing the request into a milestone the human confirms) → the specification bundle → the self-driving run. The AI-first entry to the method; the human talks to the agent rather than hand-typing `add.py`.

**Decision point** (formerly "seam") — a place where the flow stops for human judgment: the contract-freeze approval (the one approval), an escalated verify gate, intake confirmation, milestone close. The machine layer keeps the legacy name: the `--json` owner enum `seam`, the decide-digest key `seam`, and the `seam-audit` CI job.

**The decision arc** — the three engine-sourced lines a gate report opens with at every **decision point**: `goal:` the milestone goal the work serves · `done:` the achievement, the proven progress toward it (the gate reports render this line as `done`) · `plan:` what comes next. What `done` reports adapts per gate (verify: tests + evidence · milestone close: exit-criteria met · intake: the request sized) while the three-part shape stays constant. Rendered first, above the report's summary, so the human confirms with sight of the whole trajectory, not a local snapshot. Engine-sourced like all evidence — goal · done · plan are pulled from `add.py` output, never re-typed. Presentation only: it never adds a gate or changes a `PASS` / `RISK-ACCEPTED` / `HARD-STOP` / freeze outcome. The report it opens is the chat report a person reads at a decision point — distinct from the three Test/Quality/Risk reports a verify gate produces ([11 Governance](./11-governance.md)). See the `add` skill's `report-template.md`.

**Guided decision** — a **decision point** presented not as a bare next-step line but as one highlighted **recommended pick** plus its real, described alternatives (each with its one-line consequence), so the human chooses with the recommendation and what each option costs already in view. It refines the report's DECISION block — composing with **the decision arc**, never adding a gate — and fires at human gates only (never at an autonomous `[you drive]` step). The sibling of the decision arc: both are what the human sees when it is their turn. See the `add` skill's `report-template.md` for the convention itself.

**Recommended pick** — the one option a **guided decision** highlights with the `▶ … (recommended)` marker: exactly one, never zero and never two. The AI's confidence self-score informs the pick; the human overrides it freely. See **Guided decision**.

**Specification bundle** (formerly "the one-approval front") — §1–§4 of a task (spec · scenarios · contract · failing tests) drafted by the AI as one piece and approved by a person **once**, at the contract freeze. Rejecting any part returns the whole bundle to draft. The single approval it carries is the bundle approval.

**Retrospective consolidation** (formerly "the fold / fold ritual") — the milestone-close (or on-demand) step where a person gathers `open` lessons learned, confirms each, and the AI writes them append-only into the versioned foundation, bumping `foundation-version:`. The AI never self-approves a consolidation. The machine names keep their names: `fold.md`, the `folded` delta status, and `add.py deltas`.

**Owner (of a phase)** — who drives a phase, exposed by `add.py … --json` as `human`, `seam`, or `ai` (machine enum values that keep their names; in prose the `seam` value's concept is now the decision point, formerly "seam"). It tells an autonomous harness where it may run (`ai`) and where it must checkpoint to a person (`human`/`seam`), following the who-does-what table (Verify is always `human`).

**Profile** — the intensity at which the method is run: Express, Standard, or Regulated.

**Request bucket** — one of the four intake classifications — `new-major`, `sub-milestone`, `task`, or `change-request` — chosen by the tie-break order (the frozen-scope test runs before the size test). A request too vague to size is rejected `ask_human`; one that touches frozen scope, `frozen_scope`; one spanning buckets, `split_required`.

**`RISK-ACCEPTED`** — a gate outcome meaning work proceeds with a signed waiver (owner, ticket, expiry); allowed for non-security gaps only.

**Scenario** — a single rule expressed as Given/When/Then; readable by people and checkable by machines; the bridge between spec and tests.

**Scope drafting (scope-loop)** — the second half of **intake**: once a request is classified `new-major`/`sub-milestone`, turning it into a confirmed, well-formed `MILESTONE.md` (goal · scope · exit criteria · breadth-first tasks) through discussion. Every exit criterion maps to a declared task slug; the AI proposes the draft, the human confirms before anything is created. Lives in the `add` skill's `scope.md`.

**Spec (`SPEC.md`)** — the plain-language statement of what a feature must do, must reject, and assumes.

**Cross-cutting concern** (formerly "spine / continuous concern") — a concern that runs through every step rather than being one step: security, testing, observability, cost.

**Stage** — one pass through the flow at a chosen depth: Prototype, Proof of Concept, MVP, or Production-Ready.

**Stage graduation** — the orchestration loop that proposes the move to the next **stage** as a human-confirmed roadmap, never a bare flip; the 4th scope level after setup · intake · milestone-loop. The cue is every milestone `done` with the **stage-goal-criteria** all `[x]`; the flow is gather **graduation analytics** → interview *what production means here* → draft ≥1 production milestone → human confirms → `add.py stage production` as the final step. The →production flip is guarded: it refuses with `stage_no_roadmap` (a tally, not a readiness judgment) until ≥1 production milestone exists; `--force` overrides. Lives in the `add` skill's `graduate.md`.

**Graduation analytics** — the five record-sets `add.py graduation-report` clusters from the whole MVP loop for the graduation interview: open deltas by competency · open RISK-ACCEPTED waivers by expiry · RETRO records · verify residue · observe-loop coverage gaps. It gathers, never judges — there is no readiness verdict, only the records the human reasons from (gather-not-judge).

**Stage-goal-criteria** — the human-authored `[x]` checklist in `PROJECT.md` that defines "MVP covered" for this project; when every milestone is `done` and these are all checked, `add.py status` prints the graduation cue. Authored by the human (judgment), never inferred by the engine.

**Baseline approval** (formerly "the lock-down") — the single human gate ending autonomous setup: an explicit yes that freezes the foundation, first scope, and first contract together; runs as `add.py lock --by <name>`.

**Scope level** (formerly "altitude") — the granularity a decision lives at: intake level (request → versioned scope) · milestone level · setup/foundation level · task level · release level (≥1 closed milestone → a versioned, watched cut; see **Release scope level**). (A cross-stage decision lives one level out, at the **stage-graduation** loop — which `graduate.md` also numbers as a scope level; see **Stage graduation**.) One ⚠-assumption notation is shared across every scope level.

**Autonomy level** (formerly "autonomy dial") — the explicit per-task setting (`autonomy: manual | conservative | auto`, an ordered ladder manual < conservative < auto) choosing who resolves Verify: `auto` auto-PASSes on complete evidence, `conservative` keeps a human at the gate, `manual` is the strict floor (the human owns the gate; nothing auto-resolves). A high-risk scope refuses an unguarded `auto` — it must be lowered to `manual` or `conservative`. New tasks seed a visible, overridable `autonomy: auto`; a live task with no level warns (`implicit_autonomy`), a token outside the set is rejected (`unknown_autonomy_level`).

**Release** — a versioned, user-facing cut that bundles one or more closed milestones into something real users can run; its notes are evidence-backed, its risk is disclosed, and its behaviour is then watched. Recorded with `add.py release <version>`, which writes the changelog block and the ledger row but never tags, publishes, or deploys — the outward act stays human-owned. See [16 · Releasing](./16-releasing.md).

**Release scope level** — the fifth scope level: releasing as its own granularity, orthogonal to the stage. A release bundles ≥1 closed milestone (never forced one-per-milestone) and may be cut at any stage — prototype preview, mvp beta, production GA. Distinct from milestone-close (feature-complete + consolidated) and from stage graduation (which changes rigor, not version). See **Scope level** and [16 · Releasing](./16-releasing.md).

**Readiness floor** — the engine-enforced pre-cut gate `add.py release` applies before it records anything: a green suite, zero open security `HARD-STOP`, a closed-and-unreleased milestone to bundle, and every riding `RISK-ACCEPTED` waiver disclosed in the notes. Its four rejects are `release_security_open` (un-forceable) · `release_tests_red` · `release_no_closed_milestone` · `release_undisclosed_waiver`; `--force` may override every reject except the security stop.

**RELEASES.md ledger** — the append-only, newest-first trail of release rows at the project root (date · version · milestones · waivers shipped · evidence). Like the §Key Decisions log it is never rewritten; a superseded or yanked version is recorded as a new row. The ledger is the attribution source — a milestone is "released" because a row says so — which is why the `→ releasable` cue never has to read a milestone file.

**Hotfix release** — a narrowed PATCH cut that re-enters at Specify as a change request when a regression is found in a released version. It runs the same seven-step release flow scoped to the fix; releasing has no separate emergency mode, only the ordinary flow at a tighter scope.

**Auto-ready goal** — a milestone goal whose every exit criterion **cites a verifier** (`(verify: <test|command|metric>)`), so the engine can self-verify the result against the goal without human judgment. It is the prerequisite by which **autonomy is earned by goal-clarity**: the **autonomy level** governs *who* resolves Verify, but a clarified, machine-checkable goal is what makes a self-verifying run meaningful. `add.py check` raises a `goal_not_auto_ready` **WARN** (never red) for the active milestone until it has an auto-ready goal (≥1 exit criterion and every one cited), and `status` surfaces it (`goal-ready: auto-ready ✓` / cited-of-total); a zero-criteria goal reads not-auto-ready and is milestone-shaping's nudge, not this warning's. The lint forces a citation *slot* per criterion — it raises the floor but **cannot prove the citation is real** (a human can write `(verify: it works)`): citation-theater is the accepted irreducible floor, and the freeze gate and autonomy behavior are unchanged by it.

**Automated quality gate** (formerly "evidence auto-gate") — the Verify resolver under `autonomy: auto`: a run may auto-PASS on complete evidence, recorded as *auto-resolved*; a security finding always escalates (`HARD-STOP`).

**Change scope** (formerly "touch-boundary") — the hard boundary of a locked run: what it may edit (code, tests-to-green, evidence) and must not (the frozen contract, locked scope, any test weakening). The `<touch_boundary>` XML prompt tag keeps its name.

**Non-functional review** (formerly "blind-spot checks") — the deliberate verify-time check of the risks tests rarely catch: concurrency, security, architecture. Security findings always escalate.

**Failing-first suite** (formerly "red safety net") — the per-feature test suite written before any code and confirmed red for the right reason (a missing implementation, not a broken test); the TDD red phase at ADD step 4.

**Method rationale** (formerly "trust layer") — the *why* behind every rule: the AIDD book in `.add/docs/`, read on demand via each phase guide's chapter pointer, never auto-loaded.

**Working state** (formerly "state surface" — one of the two record surfaces) — everything an agent loads every session: the `add` skill (router `SKILL.md` + the active phase) and the lean operational docs — `PROJECT.md`, the active `MILESTONE.md` and `TASK.md`, and `state.json`. Kept small to avoid context rot. Contrast **audit trail**.

**Stop signal** — the boolean an autonomous harness reads from `add.py … --json` (`stop = owner != "ai"`): true means pause for a person before proceeding. The irreducible stops are the contract freeze and the Verify gate. See **Owner (of a phase)**.

**Audit trail** (formerly "story surface") — the book (`docs/*`): the whole method, read once by a person to trust ADD, then referenced by a pointer and **never auto-loaded** into agent context. Contrast **working state**.

**Living documentation** (formerly "survivor layer") — the set of durable artifacts (conventions, glossary, frozen contracts) that outlives any particular code.

**Trust ladder / autonomy ladder** — the graduated levels of AI autonomy, earned with evidence and verification capacity.

**Verification capacity / review throughput** — the rate at which a team can confirm AI output is correct; the real ceiling on safe speed.

**Foundation compaction** — the retrospective shrink: collapse a foundation spec's stable, shipped, zero-residue tail into one rolled-up settled line; the AI proposes and the human confirms; summarize and point, never delete; a SEPARATE step from the retrospective consolidation; distinct from the engine `add.py compact` (which archives finished-milestone files). See **Rolled-up settled line**, **Per-spec shape**.

**Rolled-up settled line** — the single line a compaction leaves in place of a collapsed run of records: lossy on prose, lossless on traceability (it carries a `see git` pointer).

**Per-spec shape** — each foundation spec's own tailored rolled-line format (PROJECT §Spec bullets · §Key-Decisions rows · CONVENTIONS learnings · GLOSSARY definition · MODEL_REGISTRY rows), all sharing one eligibility rule: shipped + zero open residues.

**Newest-first append-only** — every append-only foundation sequence prepends the newest record at the top; the rolled-up settled line anchors at the bottom (the oldest end), so compaction collapses upward.

**Wireframe** — the Stage-A low-fidelity, *structural* map of one screen: its regions and the component **slots** inside them, derived from `prototypes/<name>.json` *before* any color, type, or spacing — it answers "what goes where", not "what it looks like". Beat 3 of the UDD **design-definition loop**; the low-fi half of the two-stage fidelity that ends in a confirmed capture. See the `add` skill's `udd-wireframe.md` (Stage A).

**Design mock** — the Stage-B high-fidelity, **self-contained** HTML render of a screen: the `catalog.json` components as a reusable token-bound kit, bound to `tokens.json` and populated with mock data, openable offline and screenshot-able. The human-facing *visible* evidence the human confirms (the frozen `prototypes/<name>.json` tree is its machine-checkable twin). Beat 4's hi-fi artifact; the recipe lives in the `add` skill's `udd-wireframe.md` (Stage B).

**Capture** — the real rendered image (PNG/SVG) of a design mock: the **design-confirm evidence** artifact. Captures live at `.add/design/captures/<name>.<ext>` (one per prototype) and are attached or mentioned in the feature's `TASK.md`; `@json-render/image` (Satori → PNG/SVG, no browser) is the named default capture engine, otherwise the self-contained mock is screenshot headless. The engine never renders — it only MEASURES presence: `add.py check` raises a never-red `missing_capture` WARN for a prototype with no capture.

**Design-confirm** — the human touchpoint closing the UDD **design-definition loop** (`review-domain → research-components → wireframe → render-capture-confirm`, beat 4 of the `add` skill's `design.md`): approving the captured screen image **before build**, show-before-ask, so the implementation matches the layout the human has already seen instead of discovering it.

**EDD (eval-driven development)** — the AI vertical of ADD: the discipline of fixing what *good* means as a **frozen eval contract before build**, the AI analog of the red suite. An open-ended generative component has no green/red unit test — correctness is a statistical property over a held-out set — so EDD measures it. Loaded on demand for a `kind: ai` task via the `add` skill's `ai.md`; silent for a non-AI project. See [[Eval contract]].

**Eval contract** — the frozen bundle that defines and gates an AI feature: `eval-set.jsonl` (the held-out cases) · `rubric.json` (the four scored buckets) · `eval-spec.json` (primary metric · threshold · baseline-to-beat · the pinned judge) · `io-contract.json` (the boundary schema + guardrails) · `fallback.md` (the per-failure-mode safe states). The human approves it **once**, before any build; `add.py check` lints it and the `eval-set`/`eval-spec`/`rubric` ride ADD's tamper tripwire so a later weakening trips `build_tampered`. The EDD analog of the frozen §3 contract + red suite.

**Eval-set** — `eval-set.jsonl`, the frozen, held-out set of real cases an AI feature is measured against (≥1 row; ten or more preferred). It is the bar the build clears, never material to tune on. A populated `.add/ai/` set with no eval-set is `missing_eval_set` — no held-out set, no build.

**Held-out test split** — the `split: "test"` rows of the eval-set: **sacred**, informing no prompt, no retrieval tuning, no preprocessing, and no model selection. The train / val / test partitions must be disjoint; a row in two splits (`split_overlap`), a `group_key` straddling train and test (`group_leakage`), or a duplicated input across them (`duplicate_leakage`) is a leakage **HARD-STOP**. See [[Leakage]].

**Leakage** — any path by which the held-out test split informs the build, inflating the measured score above true generalization. The engine lints the statically detectable forms within `eval-set.jsonl` — `split_overlap`, `group_leakage`, `duplicate_leakage`, plus `selection_on_test` from `eval-spec.json` — as HARD-STOPs. Preprocessing leakage and finetune-set contamination, which the engine cannot see, are runner-enforced disciplines. See [[Held-out test split]].

**Rubric (four buckets)** — `rubric.json`, scoring an AI feature across **capability**, **generation faithfulness**, **instruction following**, and **cost & latency**, each bucket with a numeric pass threshold plus an `overall_threshold`. A missing bucket is `rubric_missing_bucket`; an un-numeric threshold is `rubric_missing_threshold`; accuracy as the sole metric is the `metric_mismatch` WARN (a majority-class predictor would already score high).

**Judge independence** — the rule that an LLM-judge must be **pinned** (model + version + temperature 0 + seed), **bias-mitigated** (order randomized over ≥2 samples), and **not the model-under-test**. An unpinned judge is `judge_unpinned`; an un-mitigated one `judge_bias_unmitigated`; a judge equal to the model-under-test `judge_self_preference`. Declared in `eval-spec.json`.

**AI-SPEC.md** — the human-owned binding entry doc for an AI feature (the `DESIGN.md` analog): the **success metric tied to business impact**, the four rubric buckets, the safety floor, and the chosen rung on the **prompt → RAG → finetune** ladder (cheaper rungs shown exhausted, not skipped). Scaffolded at setup; the eval-definition loop that fills it is `ai.md`.

**Eval-gated verify** — for a `kind: ai` task, `add.py gate PASS` requires a recorded eval run whose score clears the frozen threshold **AND** beats the baseline **AND** carries its lineage, scored against the frozen eval-set — not a green unit suite. The refusals are `ai_eval_unrecorded`, `below_threshold`, `no_baseline_gain`, `lineage_unrecorded`, `eval_run_stale`, and `safety_hard_stop` (a guardrail finding is always a HARD-STOP). The engine **measures** the recorded score; it never runs the eval.

**Io-contract** — `io-contract.json`, the boundary contract for an AI feature: the response schema validated at the edge, the guardrail set (prompt injection incl. indirect · PII · jailbreak · toxicity), and idempotency / retry. An unbound output is `io_contract_unbound`; a strict-mode reject path missing is `io_contract_strict_reject`. The probabilistic-IO analog of the frozen §3 shape.

**Fallback (safe state)** — `fallback.md`, a declared safe state for every failure mode of a probabilistic component — timeout, error, low-confidence, schema-invalid, guardrail trip, empty retrieval, tool failure — so the system degrades, never *crashes* or *hangs*. A missing mode is `fallback_missing`; no timeout + bounded retry is `fallback_no_timeout`; a guardrail with no wired safe state is `guardrail_without_fallback`.

**Online eval / drift** — the observe-phase beat for a shipped AI feature: `monitor.json` declares the production signals and a drift baseline, so degradation against the frozen eval is caught in the wild. A shipped `kind: ai` task with no monitor is the never-red `missing_monitor` WARN; a monitor with no baseline is `monitor_no_drift_baseline`. The AI analog of the observe loop's capture WARN.

---

## Optional mapping to formal phase names

This book uses plain step names. Teams connecting it to a larger formal standard may use these equivalents. The mapping is optional; the plain flow is complete on its own.

| Plain step (this book) | Formal phase name |
|------------------------|-------------------|
| Project setup | Foundation |
| Ground (preamble) | Codebase Discovery (the §0 grounding map) |
| Specify | Domain Discovery + Spec Definition |
| (design portion) | UX-Driven Design |
| Scenarios | Behavior specification (Given/When/Then) |
| Contract | Contract Freeze |
| Tests | Test-Driven Verification |
| Build | AI-Driven Development (the engine) |
| Verify | the review gate within the build |
| Observe (loop) | Operate and Learn |

The formal standard also names the *foundation* and *design* work as full phases in their own right; this book merges them into project setup and the Specify step (and the Prototype stage) to keep the flow to six memorable steps.
