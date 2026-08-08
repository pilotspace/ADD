# Appendix C · Glossary

[← 18 Personas in practice](./18-personas.md) · [Contents](./README.md) · Next: [Appendix D Worked example →](./appendix-d-worked-example.md)

Every term the method uses, defined once. Where a term names something the **engine
enforces**, the definition says so — and where it names discipline the engine cannot
see, it says that too. The difference is the whole point of the method.

---

## The method

**ADD (AI-Driven Development)** — a method of building software in which an AI agent
writes most of the code and people own direction and verification. The engine records
what was decided and what was proven; it never writes the code and never runs the
method.

**NO-EXEC** — the engine's founding constraint: it never runs your suite, your build,
or an agent. You run things; the engine records what happened. Every guarantee in ADD
is therefore about *evidence on disk*, never about having watched the work.
See [01 Core principles](./01-principles.md).

**Notary** — what the engine is, as opposed to an orchestrator: it witnesses and
stamps facts (a freeze, a receipt, a verdict) and refuses to stamp ones that do not
hold up. It has no opinion about how you work.

**Disposable code** — the view that code is one regenerable implementation of the
direction, not a durable asset to be preserved.

**Living document** — a document expected to change as the loop learns. The five
living specs are the standing example; a frozen contract is the deliberate exception.

**Verification capacity** — the rate at which a team can confirm AI output is correct.
It is the real ceiling on safe speed, and adding more AI does not raise it.

## The loop

**Beat** — one of the three phases of a task: **Direction**, **Build**, **Verify**. A
node's current beat is *derived from its stamps*, not typed into a field: an explicit
reopen wins, else a run stamp means verify, else a freeze stamp means build, else
direction.

**Direction** — the first beat: authoring what must hold, what must never happen, the
contract, the scope, and the red checks — then freezing it. The human's beat.
See [03 Direction](./03-direction.md).

**Build** — the second beat, and the only one the AI leads: turn the red checks green
without editing a check, the frozen contract, or anything outside `scope:`.
See [04 Build](./04-build.md).

**Verify** — the third beat: record a receipt, examine the residue tests cannot cover,
and record exactly one verdict. See [05 Verify](./05-verify.md).

**Freeze** — the single human decision of a task, which stamps the direction and opens
Build (`add freeze <slug>`). Freezing *stamps*; it does not itself bind the checks —
that binding is enforced at the gate.

**Gate** — the checkpoint that records a task's one verdict (`add gate <slug> …`). A
`PASS` closes the node.

**`PASS`** — the verdict meaning the work is proven by a fresh, bound receipt.

**`RISK-ACCEPTED`** — the verdict meaning the work proceeds with a written reason
(`--reason`). Unavailable on a security-floored node.

**`HARD-STOP`** — the verdict meaning work cannot proceed. Where a security finding
goes.

## The bundle

**ABF-1** — the bundle format ADD 3.0 is built on: typed markdown nodes with YAML
frontmatter, plus a compiled graph. See [12 The `.add/` bundle](./12-bundle-format.md).

**Bundle (`.add/`)** — everything the method keeps on disk for one repository: the
nodes, the five living specs, the personas, the vendored engine under `.add/tooling/`,
and the compiled `graph.json`. One repo, one bundle.

**Node** — one typed markdown file that is the unit of everything: a Task, a
Milestone, a Spec, a Persona, a Run, or the Project. Its frontmatter carries the
machine-readable facts; its sections carry the human-readable ones.

**Lifecycle node** — a node that moves through the beats and can be gated: a **Task**
or a **Milestone**. Specs and Personas are living documents with no lifecycle.

**`graph.json`** — the compiled cache of every derivable fact, rebuilt from the node
frontmatter at any time and gitignored. Because it is rendered rather than
hand-maintained, it cannot go stale and has no concurrent writers — which is what
lets a wave fan out across worktrees with no coordinator.

**The five living specs** — `domain`, `system`, `experience`, `quality`, and `method`
in `.add/specs/`. The project-level foundation every task freezes against, and where
confirmed lessons land. See [14 The foundation](./14-foundation.md).

## Inside a task node

**`## CARD`** — the goal, why the task exists, and the current beat with its next verb.

**`## RULES`** — what must hold and what must never happen: `<must>` entries (`M1`,
`M2`, …) and `<reject>` entries (`R:NAME`), each an independently checkable claim.

**`## PLAN`** — the contract this task publishes, its build strategy, its `scope:`,
and its assumptions, ordered lowest-confidence first.

**`## EDGES`** — enumerated edge cases (`E1`, `E2`, …): boundary and failure conditions
that must be covered like rules. Inert until authored, so a fresh task gates unchanged.

**`## CHECKS`** — the red suite: one check per rule and per edge, each naming what it
`covers:`.

**`## EVIDENCE`** — the recorded receipt and the recorded verdict.

**`## LESSONS`** — what the task taught, on its way to `add learn`.

**Must / Reject** — the two rule kinds. A Must is behavior that has to hold (`M1`); a
Reject is behavior that must never happen, carrying its own error name
(`R:OVERDRAW … -> "insufficient_funds"`).

**Edge case** — a boundary or failure condition written down as `E1`, `E2`, … Edge
cases are first-class **covers referents**: an authored edge with no check bound to it
blocks the gate exactly as an uncovered rule does.

**`covers:`** — the binding between a check and the rule or edge it proves. It is the
single grammar that makes "every rule is tested" mechanical rather than aspirational.

**Referent** — anything a check may `covers:` — a Must, a Reject, or an Edge.

**`scope:`** — the files or directories a task may touch, declared on the node. It is
also the **freshness set**: the paths the gate hashes a receipt against.

**`gives:`** — the contract shape a task publishes. Hand-authored into frontmatter,
and immutable once the task freezes.

**`needs:`** — a citation of another node's frozen `gives:`. It cannot resolve until
the producer has frozen, which is how a consumer is held behind its producer.

**`depends_on:`** — an edge to a node this one depends on, written in block-list form.
The DAG `add wave` reads.

**Contract** — the fixed external shape a task publishes: interfaces, data structures,
names, and error cases. In ABF-1 it is not a separate file type — it is the `gives:`,
frozen at the freeze stamp.

**Change request** — the path for altering already-frozen scope: return the affected
node to Direction and refreeze, so dependents citing the old shape are flagged stale.
Never fork the truth into a parallel node.

## Evidence

**Receipt** — the recorded result of a run (`add run <slug> -- <cmd>`): what command
ran, its exit code, and which checks were observed. The engine records it; it does not
produce it.

**Fresh** — a receipt is fresh when every file in the task's `scope:` is byte-identical
to what it was at the run. Edit a scoped file afterwards and the gate refuses.

**Bound** — a receipt is bound when every check the rules `covers:` appears in it as
passed. Unbound evidence is not evidence of the thing you are signing for.

**Red-first** — the rule that every check must fail before any implementation exists.

**Lying red** — a check that fails for the wrong reason — an import error, a broken
fixture, a `should_panic` that would pass on anything. It looks like a baseline and
proves nothing.

**Residue** — the three things automated checks cannot cover, examined by hand at
every verify: **security**, **concurrency and timing**, and **architecture
conformance**. See [05 Verify](./05-verify.md).

**Deep check** — reviewer discipline no engine can perform for you: tracing that every
new symbol is **wired** in from a production entry point, that no **dead code** was
introduced, and — for prose — that a **semantic read** actually happened.

## Authority and routing

**`sensitivity:`** — what a task touches, and therefore the floor on who must sign:
`mechanical → process`, `data → plan`, `architecture → plan`, `security → human`. It
cannot be talked down.

**Authority floor** — the computed lowest lane a task may run in: the higher of its
declared `sensitivity:` and any match against `sensitive_paths:`. You may always run
more ceremony than the floor demands, never less.

**`sensitive_paths:`** — glob patterns in `.add/index.md` naming paths that floor to a
human regardless of what a task declares about itself. A task scoped to a matching
path is security-floored even with no `sensitivity:` line.

**Security floor** — the two refusals that make "security is a HARD-STOP" structural
rather than advisory: a security-floored node cannot record `RISK-ACCEPTED`
(`R:SECURITYFOLD`), and its `PASS` requires a named lens (`R:NOCOVERAGE`).

**Depth dial** — `quick · standard · deep`: how much ceremony a single task carries.
Depth tunes **ceremony, never authority** — a `quick` depth can never lower a
`security` floor.

**Lane** — the cheapest route that fits a request, chosen before any node exists:
**Quick** (below the scope floor — no node, just the diff and a lesson), **Task** (one
atomic node), or **Project / milestone** (a theme or a slice). The AI proposes; the
human vetoes. Anything touching security, data, or architecture always sizes up to at
least a Task. See [07 Setup and the three lanes](./07-setup-and-lanes.md).

## Personas

**Persona** — a requirements lens the agent adopts, stored as a versioned node in
`.add/personas/` and distilled to machine-readable parts: an **Identity** (the
stance), **Critical Rules** (the non-negotiables), and **Success Metrics** (the
done-bar), plus a `use-when:` line that says when to route to it. Advisory in
judgment, but its *presence* is enforced: a security `PASS` needs one.

**Personas teacher** — the vendored corpus at `.add/personas-teacher/`, the library a
project persona is distilled *from*. Read off-build; never a runtime dependency.

**Lens** — a persona as applied to a piece of work. "A named lens" is the thing
`R:NOCOVERAGE` requires: someone on record as having reviewed it.

**`persona:`** — the lens stamped on a node by a wave, when a stream is assigned one.

**`advised_by:`** — the lens recorded on a node routed sequentially with
`add advise <slug> --persona <p>`, and the provenance `add join` carries back from a
lensed stream onto the delivered node.

**`use-when:`** — the routing line on a Persona node saying what kind of work it is
for. Rendered into the personas index, so a lens is discoverable rather than
folklore.

## Parallel work

**Wave** — a parallel execution plan derived from the task DAG (`add wave
<milestone>`): topological levels, so producers land before their consumers. It
refuses a cycle, an intra-level dependency, or overlapping scope rather than
scheduling a conflict.

**Stream** — one task within a wave, running in its own git worktree, behind its own
frozen contract and under its own persona lens.

**Join** — folding finished stream bundles back (`add join <bundles…>`): PASS-only,
byte-for-byte on nodes, union-merging spec deltas, flagging divergence rather than
silently keeping one side. Rollback is dropping a worktree.

**Worktree** — the isolated checkout a stream runs in. Isolation is what makes
parallel builds safe; `graph.json` being a rebuildable cache is what makes it cheap.

## The loop closing

**Lesson** — one thing a loop learned, filed with `add learn <lens> "<lesson>"
--evidence <ref>` against one of the five lenses (`ddd · sdd · udd · tdd · add`). A
lesson without evidence is refused.

**Delta** — a recorded, not-yet-consolidated change to a living spec. `add deltas`
lists them.

**Fold** — the consolidation step (`add fold`) where confirmed lessons are written
into the living specs. The AI never self-approves a fold.

**Reopen** — returning a closed task to the loop (`add reopen <slug>`) rather than
opening a near-duplicate beside it.

**Exit criteria** — the checkboxes on a Milestone's `## EXIT` that define what "done"
means for it. `add milestone-done` refuses to close a milestone while any box is
unchecked — the goal-loop that keeps a milestone open until it is actually met.

**Milestone archive** — `add milestone-archive`, which moves a closed milestone and
its tasks out of the working set without deleting the record.

## Reading the bundle

**`add status`** — the resume point: what exists, what beat each lifecycle node is on,
and the single next verb. Never re-read the repo to find out where you are.

**`add todo`** — the open worklist, grouped by beat, each task with its next verb.

**`add locate <path>`** — the scope reverse lookup: which node's `scope:` owns this
path.

**`add brief <slug>`** — the assembled context for working a node: the binding
decisions from the living specs plus the node itself.

**`add doctor`** — the read-only health report. It reports and never writes; `add
doctor --sync` is the separate verb that re-vendors a stale engine.

**Finding** — one item `add doctor` reports, at `info` or `warn`. A finding is a
nudge, not a refusal — the gate is where refusals live.

**Refusal** — the engine declining to record something that would not hold up, named
by a code (`R:GREENLIE`, `R:SECURITYFOLD`, `R:NOCOVERAGE`, `R:OVERLAP`, …). A refusal
writes nothing and tells you the verb that would fix it.
