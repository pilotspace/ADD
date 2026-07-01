# Appendix C · Glossary

[← Appendix B Prompts](./appendix-b-prompts.md) · [Contents](./README.md) · Next: [Appendix D Worked example →](./appendix-d-worked-example.md)

---

## Terms

**AIDD (AI-Driven Development)** — a method of building software in which an AI agent writes most of the code and people direct and verify the work.

**Artifact** — a durable work product: the spec, the scenarios, the contract, the tests. The artifacts survive; the code is disposable.

**Lesson learned** (formerly "competency delta") — a single learning a loop produces, tagged by which of the five competencies (`DDD · SDD · UDD · TDD · ADD`) it improves, written in a task's OBSERVE phase as `- [<COMPETENCY> · <status>] <learning> (evidence: …)`. Emitted `open` by the AI; the human folds it into a versioned `PROJECT.md` (`folded`) or declines it (`rejected`). The mechanism by which the foundation self-improves instead of drifting. See the `add` skill's `deltas.md`.

**Contract** — the fixed external shape of a feature: interfaces, data structures, names, and error cases. Frozen before the build, it is the surface the AI builds against.

**Co-specification** — how a spec is made in ADD: the AI and the human **brainstorm the shape together** (diverge), the AI **drafts** it, and the human **validates with the AI's advice** (validate). The AI's decisive advice is the *lowest-confidence flag*. It replaces dictation-by-one-side — the human owns the decision, the AI owns surfacing what it does not yet know. See [03 Specify](./03-step-1-specify.md).

**Component** — a declared part of a multi-part codebase that owns a source `root` and its own `green-bar` (suite + checks), named in `.add/components.toml` under `[component.<name>]`. A task binds to one with a `component:` header line, which adds that root to its §5 Scope and holds it to that component's green bar at verify. At the gate the engine also **surfaces** the component's `verify` command (the literal suite to run, e.g. `pytest -q`) and records it — NO-EXEC, the operator runs it; the fast lane carries the same `component:` affordance. Declared, never inferred; a project with no components is byte-identical to a single-codebase project. See [17 Components](./17-components.md).

**persona** — a project-fit requirements lens the agent adopts, distilled from a *teacher* — the vendored local library at `.add/personas-teacher/` — to three machine-readable parts: an **Identity** (the stance), **Critical Rules** (the non-negotiable constraints), and measurable **Success Metrics** (the done-bar). Stored as a versioned `.add/personas/<slug>.md`; read off-build (the teacher is never a runtime dependency); advisory only — it never lowers a gate (a security finding still `HARD-STOP`s) and the engine stays NO-EXEC. See [18 Personas](./18-personas.md).

**persona loop** — how personas come to exist and improve: **seed** (proposed at setup from the foundation) → **grow** (observe emits a persona delta; the human consolidates confirmed deltas into the file) → **apply** (UDD framing, advisor/streams subagent selection, and the build overlay atop `SOUL.md`). Opt-in and additive; a project with no personas behaves exactly as before. See [18 Personas](./18-personas.md).

**Cross-component contract** — the frozen, machine-checkable interface between a producer component and its consumers, declared under `[contract.<id>]` (producer + consumers). A task names its role with a `produces: <id>` or `consumes: <id>` header. On the producer's freeze the engine writes an immutable snapshot at `.add/contracts/<id>.json`; a consumer pins its hash and is flagged `contract_consumer_stale` if the producer later re-freezes a changed shape. Inside one milestone a `consumes:` task is HELD from writing its §3 until the producer's snapshot exists — the intra-milestone BE→FE ordering. Freeze-recency: the consumer is also held `producer_contract_stale` if a *live* producer task has re-opened or drifted its §3 (the snapshot no longer matches a frozen producer); `add.py check` surfaces the softer `contract_producer_stale` and `contract_snapshot_hashless` (a snapshot with no hash to verify) as never-red warnings. See [17 Components](./17-components.md).

**Federation (multi-repo)** — the transport that carries a frozen cross-component contract between separate repositories. A consumer repo declares `[federation.<id>]` with a `source` (and optional `pin`); `add.py federate pull <id>` validates the producer repo's published snapshot and lands a byte-for-byte copy locally, where it behaves exactly as in a monorepo. Fail-loud: an unknown id, unreadable source, a `source` that escapes the repo's allowlist (`federation_source_escapes` — the path is confined to a sibling of the repo root), invalid snapshot, or version mismatch HARD-STOPS and lands nothing. Each repo keeps its own git-native `state.json`; only the immutable snapshot crosses. See [17 Components](./17-components.md).

**Disposable code** — the view that code is one regenerable implementation of the artifacts, not a durable asset to be preserved.

**Evidence bundle** — the proof attached to a change (passing tests, clean security scan, no coverage loss) that justifies trusting it and may unlock more AI autonomy.

**Foundation version** — a monotonic integer marker in `PROJECT.md` that advances by one each time confirmed lessons learned are consolidated into the foundation. It makes the living documentation's evolution auditable: a rising version with fewer new deltas per milestone is the signal that a competency is converging rather than drifting. Bumped only by the retrospective consolidation (see the `add` skill's `fold.md`).

**Fast lane** — the collapsed, opt-in task path for small, low-risk work. `add.py new-task <slug> --fast` scaffolds a minimal `TASK.fast.md` (sections {0,1,3,4,5,6}; scenarios and observe dropped) and the specification bundle is approved in one freeze. It runs the SAME flow with fewer sections — it never drops the trust floor: a `--fast` task is held to a frozen contract, a red test before build, and a recorded verify gate under any milestone. Collapse, never skip; the human opts in (the engine never auto-classifies a task as small). See the `add` skill's `phases/fast-lane.md`.

**Gate** — a checkpoint with an explicit pass/fail exit. Its outcome is `PASS`, `RISK-ACCEPTED`, or `HARD-STOP`.

**Ground (phase-0 preamble)** — the per-task phase *before* Specify in which the AI gathers the real current codebase the task touches — files, symbols, signatures, patterns, conventions — into a lean **grounding map**, surfacing the **anchors** the frozen contract will cite. It is AI-owned and adds no approval (the one approval stays at the contract freeze); it precedes the seven steps as step 0 so the contract, tests, and build are grounded in the code as it actually is, not in assumption. Lives in the `add` skill's `phases/0-ground.md`.

**Grounding map / anchors** — the §0 GROUND artifact: the real files, symbols, and conventions a task touches, plus the **anchors** — the symbols the frozen contract names. Task-specific delta only: it defers to `PROJECT.md` / `CONVENTIONS.md` for architecture and never re-runs the setup brownfield scan. `add.py status` / `check` surface whether the active task's contract is grounded (measure, never block — the contract-freeze checklist asks the human to confirm it).

**`HARD-STOP`** — a gate outcome meaning work cannot proceed; triggered by any failing test or security finding.

**Intake** — the step *before* a task: sizing a raw request into versioned scope by classifying it into one **request bucket**. The AI proposes `{bucket, rationale, command}`; the human confirms. Lives in the `add` skill's `intake.md` (the intake level, above the per-task flow).

**Lowest-confidence flag** (formerly "least-sure flag") — the AI's ranked declaration of the **1–2 things most likely to be wrong** in what it is asking a human to approve, each carrying *why* it is uncertain and *what it costs if wrong* (`⚠ [spec|scenario|contract|test] … — because …; if wrong: …`). It reshapes the old flat assumptions list into a ranked one, so a single approval aims the reviewer's attention at the real risk instead of a flat list of equal-looking ticks. Bundle-wide at the contract-freeze decision point; the §1 assumptions are its first input. If nothing is materially uncertain it still names the single biggest risk — never a blank "none". It makes a genuine review cheap and a lazy one visibly negligent, but cannot *force* the read. The "AI advises" half of **co-specification**.

**Living document** — an artifact expected to change as the loop learns; never frozen forever (the one exception being a versioned contract, which changes only via a change request).

**Onboarding** (formerly "on-ramp") — the path a new user walks from install to their first milestone: install → `/add` → describe the goal → the agent runs intake (sizing the request into a milestone the human confirms) → the specification bundle → the self-driving run. The AI-first entry to the method; the human talks to the agent rather than hand-typing `add.py`.

**Decisions (ADR)** — the engine-harvested record in a task's §7 OBSERVE: one actor-tagged line per key decision, gathered at the gate from the stamps already in the task — §1 framing `[AI]` (the choice + the rejected alternatives), §3 freeze `[human]`, §5 strategy-actually-used `[AI]`, §6 gate `[human|AI]`. *Harvested, never authored* — the engine invents no decision content, only mirrors what the task recorded — and scoped to the §7 OBSERVE placeholder alone. The durable who-decided-what trail that separates human direction from AI building; `add.py audit` flags a done task whose block never harvested (`adr_record_missing`).

**Decision point** (formerly "seam") — a place where the flow stops for human judgment: the contract-freeze approval (the one approval), an escalated verify gate, intake confirmation, milestone close. The machine layer keeps the legacy name: the `--json` owner enum `seam`, the decide-digest key `seam`, and the `seam-audit` CI job.

**The decision arc** — the three engine-sourced lines a gate report opens with at every **decision point**: `goal:` the milestone goal the work serves · `done:` the achievement, the proven progress toward it (the gate reports render this line as `done`) · `plan:` what comes next. What `done` reports adapts per gate (verify: tests + evidence · milestone close: exit-criteria met · intake: the request sized) while the three-part shape stays constant. Rendered first, above the report's summary, so the human confirms with sight of the whole trajectory, not a local snapshot. Engine-sourced like all evidence — goal · done · plan are pulled from `add.py` output, never re-typed. Presentation only: it never adds a gate or changes a `PASS` / `RISK-ACCEPTED` / `HARD-STOP` / freeze outcome. The report it opens is the chat report a person reads at a decision point — distinct from the three Test/Quality/Risk reports a verify gate produces ([11 Governance](./11-governance.md)). See the `add` skill's `report-template.md`.

**Guided decision** — a **decision point** presented not as a bare next-step line but as one highlighted **recommended pick** plus its real, described alternatives (each with its one-line consequence), so the human chooses with the recommendation and what each option costs already in view. It refines the report's APPROVE block — composing with **the decision arc**, never adding a gate — and fires at human gates only (never at an autonomous `[you drive]` step). The sibling of the decision arc: both are what the human sees when it is their turn. See the `add` skill's `report-template.md` for the convention itself.

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

**Queued milestone** — a milestone created non-active: its status is `queued` (the milestone status enum is **active · queued · done**). It is recorded with its `MILESTONE.md` on disk but does not hold the active focus; `add.py new-milestone --queued <slug>` creates it, and `add.py activate <slug>` promotes it queued→active one at a time. A queued milestone is not `done`, so it does not satisfy the graduation gate.

**Roadmap** — the multi-milestone intake artifact: when a request decomposes into N>1 milestones of the same line, the AI proposes the ordered roadmap and, on human confirm, creates all N — the first active, the rest **queued** — then promotes each with `activate` as it is started. Distinct from `split_required` (which spans different buckets). Lives in the `add` skill's `intake.md`.

**Scope level** (formerly "altitude") — the granularity a decision lives at, as one ordered ladder of five: **setup/foundation** · **intake** (request → versioned scope) · **the milestone loop** (the task is its inner unit) · **stage graduation** (changes rigor, not version; see **Stage graduation**) · **release** (≥1 closed milestone → a versioned, watched cut; see **Release scope level**). One ⚠-assumption notation is shared across every scope level.

**Autonomy level** (formerly "autonomy dial") — the explicit per-task setting (`autonomy: manual | conservative | auto`, an ordered ladder manual < conservative < auto) choosing who resolves Verify: `auto` auto-PASSes on complete evidence, `conservative` keeps a human at the gate, `manual` is the strict floor (the human owns the gate; nothing auto-resolves). A high-risk scope refuses an unguarded `auto` — it must be lowered to `manual` or `conservative`. New tasks seed a visible, overridable `autonomy: auto`; a live task with no level warns (`implicit_autonomy`), a token outside the set is rejected (`unknown_autonomy_level`).

**Release** — a versioned, user-facing cut that bundles one or more closed milestones into something real users can run; its notes are evidence-backed, its risk is disclosed, and its behaviour is then watched. Recorded with `add.py release <version>`, which writes the changelog block and the ledger row but never tags, publishes, or deploys — the outward act stays human-owned. See [16 · Releasing](./16-releasing.md).

**Release scope level** — the fifth scope level: releasing as its own granularity, orthogonal to the stage. A release bundles ≥1 closed milestone (never forced one-per-milestone) and may be cut at any stage — prototype preview, mvp beta, production GA. Distinct from milestone-close (feature-complete + consolidated) and from stage graduation (which changes rigor, not version). See **Scope level** and [16 · Releasing](./16-releasing.md).

**Ship review** — the whole-milestone, cross-task evidence the AI fills at milestone close in the `## Close — ship review` section: ship-by-domain (what changed per bounded context), cross-task evidence (one row per task: gate · tests · residue), and a goal-met map (each exit criterion tied to its evidence). A person reads it *before* checking the exit-criteria boxes — evidence, not a new gate. The ritual lives in the `add` skill's `loop.md`. See [09 · The Loop](./09-the-loop.md).

**Release steps** — the AI-defined, per-milestone ordered hints to ship a closed milestone, of which `merge` is one small step (a pull request, an exported hand-off document, a tag or a publish are others). Defined at close and **fed** into the release scope (see **Release**), never a second flow.

**Readiness floor** — the engine-enforced pre-cut gate `add.py release` applies before it records anything: a green suite, zero open security `HARD-STOP`, a closed-and-unreleased milestone to bundle, and every riding `RISK-ACCEPTED` waiver disclosed in the notes. Its four rejects are `release_security_open` (un-forceable) · `release_build_in_flight` · `release_no_closed_milestone` · `release_undisclosed_waiver`; `--force` may override every reject except the security stop.

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

**Design intake** — beat 0 of the UDD **design-definition loop**: the agent interviews the human on four design **axes** *before* reading the domain, so the look is directed not guessed. **Fidelity** (lo-fi wireframe · hi-fi mockup · production — how far the design renders), **Concept** (idea · mood · direction), **Layout** (structure · grid · hierarchy), and **Visual design** (color · type · spacing · imagery — surfaced for the human, never auto-picked). Recorded as project defaults in `DESIGN.md`'s `## Design intake` and per-screen overrides in the prototype note. Fidelity is recorded intent, not an engine gate.

**Wireframe** — the Stage-A low-fidelity, *structural* map of one screen: its regions and the component **slots** inside them, derived from `prototypes/<name>.json` *before* any color, type, or spacing — it answers "what goes where", not "what it looks like". Beat 3 of the UDD **design-definition loop**; the low-fi half of the two-stage fidelity that ends in a confirmed capture. See the `udd-wireframe.md` template (`tooling/templates/`, Stage A).

**Design mock** — the Stage-B high-fidelity, **self-contained** HTML render of a screen: the `catalog.json` components as a reusable token-bound kit, bound to `tokens.json` and populated with mock data, openable offline and screenshot-able. The human-facing *visible* evidence the human confirms (the frozen `prototypes/<name>.json` tree is its machine-checkable twin). Beat 4's hi-fi artifact; the recipe lives in the `udd-wireframe.md` template (`tooling/templates/`, Stage B).

**Capture** — the real rendered image (PNG/SVG) of a design mock: the **design-confirm evidence** artifact. Captures live at `.add/design/captures/<name>.<ext>` (one per prototype) and are attached or mentioned in the feature's `TASK.md`; `@json-render/image` (Satori → PNG/SVG, no browser) is the named default capture engine, otherwise the self-contained mock is screenshot headless. The engine never renders — it only MEASURES presence: `add.py check` raises a never-red `missing_capture` WARN for a prototype with no capture.

**Design-confirm** — the human touchpoint closing the UDD **design-definition loop** (`design-intake → review-domain → research-components → wireframe → render-capture-confirm`, the final beat of the `add` skill's `design.md`): approving the captured screen image **before build**, show-before-ask, so the implementation matches the layout the human has already seen instead of discovering it.

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
