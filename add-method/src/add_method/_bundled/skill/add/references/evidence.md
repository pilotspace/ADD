# Evidence — closing the loop from intent to production

Read this when a task has `risks:`, a changed `gives:`, an agentic or nondeterministic feature, a
release to tag, or an escaped defect. Ordinary work needs only SKILL.md.

The aim is **the least independent evidence that keeps intent intact across every handoff** —
not the most tests, agents or artifacts. Every handoff below has a durable claim and a way to
falsify it:

```
request → RULES → CHECKS → code → verified commit → tag → production → escape → next Direction
```

## Contents
1. Why same-author evidence is not enough
2. Rule origin and the falsifier
3. Pick the evidence by risk
4. Evidence the builder never saw
5. The regression floor
6. Consumers of a changed surface
7. Residue by risk
8. Agentic and nondeterministic features
9. Release — from verified commit to tag
10. Observe — after release
11. Escapes, successors and prevention
12. Method economics
13. The twelve invariants, and where each lives

## 1 · Why same-author evidence is not enough

"An expired invitation must never be usable." You write `M1 reject expired invites`, a check
`expiry < now → rejected`, code `expiry < now → reject`. All green. The domain meant `expiry <= now`.
The rule, the check and the code were written by one mind with one reading, so they agree with each
other and are still wrong. More tests by the same author do not fix this; a different reader, a
different kind of evidence, or a check the builder never saw does. That is what the rest of this
file buys, and only where `risks:` says it is worth buying.

## 2 · Rule origin and the falsifier

Each rule says where it came from: `(from: request)`, `(from: docs/auth.md §3)`, `(from: spec
D4)`, or `(from: derived: <why>)`. A derived rule carries a decision nobody made — it goes in the
report next to the ASSUMPTIONS and should not earn the same trust as a sourced one.

Each CHECKS line names its **falsifier**: the most plausible implementation that looks right and
breaks the rule. The check must fail against it.

```
- C2 covers: R:EXPIRED · acceptance · tests/test_invites.py::test_redeem_at_expiry_instant_refused · falsifier: `expiry < now` (lets the boundary instant through)
```

If you cannot name a falsifier, the check probably asserts what the code happens to do.

## 3 · Pick the evidence by risk

Ask "which independent kinds of evidence would all have to be fooled for this defect to escape?",
not "how many tests?". Modes:

| mode | what it is | defends against |
|---|---|---|
| E0 example | a readable Given/When/Then edge | wrong business meaning |
| E1 acceptance | the rule exercised through the public seam | broken behavior end to end |
| E2 property / metamorphic | a relation over many inputs or runs | cases nobody enumerated; nondeterminism |
| E3 contract | a consumer's expectation replayed on the provider | breaking another component |
| E4 analyzer | a type checker, linter, security or architecture rule | structural and policy violations |
| E5 mutation | mutate the code, expect a check to fail | hollow assertions |
| E6 probe after build | written by a second reader after the code exists (§4) | overfitting the visible checks |
| E7 regression | the relevant host suite | collateral damage |
| E8 runtime | a monitor or canary after release (§10) | what no test environment shows |

Every task has E1 and E7. Each rule touching a `risks:` item adds one mode that fails independently
of the first, by risk:

| risk | add |
|---|---|
| authorization, privilege | E6 bypass probe · E1 negative path for the anonymous and wrong-actor caller |
| data, migration | E2 round-trip (migrate → rollback → migrate) · E7 on real-shaped fixtures |
| compatibility, a `gives:` surface | E3 on each consumer (§6) |
| concurrency | E2 with interleavings · a stress probe |
| performance, resource | a measured ceiling check (time, memory, calls) |
| AI / agent behavior | E2 metamorphic relations (§8) |
| input handling, parsing | E2 generated inputs · E4 |

A high-risk rule backed by one mode only is allowed — but say so as an ASSUMPTION
(`A4 [which] R:EXPIRED relies on acceptance only → …`) so the reviewer sees the thin spot.

## 4 · Evidence the builder never saw

"Don't look at the hidden tests" is not a boundary. What works without infrastructure:

- **Probes written after the build.** At refute, the counter-lens (a fresh subagent for security ·
  data · architecture work) reads the task file first, then the diff, and writes 1–3 probes into
  `.add/tasks/<slug>.probes/` (or a scratch test file). The builder wrote the code before the
  probes existed, so it could not overfit them. Run them once; record each command and result under
  `probes:` in EVIDENCE. A probe that fails is a defect.
- **Holdout for long work.** For a milestone of many tasks, a second reader can write held-out
  scenarios that compose several rules, kept on a branch or directory the building session never
  reads, run at milestone exit. Visible-suite pass with holdout fail means the build fit the
  checks, not the intent.

Without subagents, do the probe step after a context break: reread only the task file, then write
probes before rereading the code.

## 5 · The regression floor

`regression:` in PLAN is one of:
- the full suite (the default),
- `affected: <command> — <why the rest cannot be touched>` for a large repo,
- `none — <why>` only when no other code exists.

Brownfield work that changes a `gives:` surface runs the full suite. A task-level green with a
broken host test is the classic escape.

## 6 · Consumers of a changed surface

When the diff changes anything named in `gives:` (a signature, a return shape, a status code, an
event, a file format):

1. `git grep -n '<symbol or route>'` outside `scope:` — every hit is a consumer.
2. Run each consumer's tests; where a consumer has an explicit contract (a schema, a pact, a
   fixture), replay it.
3. Record `consumers: <paths> → <command> → <result>` in EVIDENCE.
4. A broken consumer blocks PASS. Either fix the provider, widen `scope:` by refreeze and update the
   consumer, or HARD-STOP if the break is security-relevant.

A surface that is renamed or removed is a changed surface.

## 7 · Residue by risk

Always read the diff for **security**, **concurrency** and **architecture**. Add, by `risks:`:

- data / migration — reversible? what happens to rows written between deploy and rollback?
- performance / resource — ceilings on time, memory, calls, payload; N+1 access
- reliability / integration — retries, idempotency, timeouts, a dependency that is slow or down
- privacy — personal data in logs, errors, caches; retention
- UI / experience — keyboard reach, screen-reader labels, error text a user can act on
- observability — can a failure of this rule be seen after release?
- operations — how to roll back, who is paged

## 8 · Agentic and nondeterministic features

Exact output is a weak oracle when many answers are acceptable. Check relations instead:
- changing only the display language does not change an authorization decision;
- appending an irrelevant document does not change which sources are cited;
- removing a tool makes the agent fail closed, never fabricate the tool's output;
- reordering independent inputs preserves the final state.

For an agent that acts, acceptance = outcome + permitted path + side-effect boundary:

| dimension | example check |
|---|---|
| tool authorization | never calls a forbidden tool |
| side effects | writes, sends, deletes only when authorized |
| end state | external state matches the intended end state |
| grounding | every cited source was actually retrieved |
| termination | stops on success or failure, never loops |
| budget | stays within its token, call and time ceiling |
| recovery | a failed tool yields an honest error, not invented success |

## 9 · Release — from verified commit to tag

ADD never holds deployment credentials; it binds to what the pipeline produced.

- Tag only a commit where every task since the previous tag ends in a `verify(` commit with PASS or
  RISK-ACCEPTED, and no code landed after its verify without its own task:
  `git log --oneline <last-tag>..HEAD` — every change should trace to a task and its verify.
- When the pipeline gives you a build identity (CI run URL, artifact or image digest, lockfile
  digest), write it into the milestone's EXIT evidence or the release notes next to the tag. Then a
  production observation can be traced to the verified source and the frozen intent that produced it.

## 10 · Observe — after release

A task with `risks:` that ships names what to watch, in PLAN:

```
observes: R:EXPIRED → invite_redeem_total{result="expired"} and memberships_from_expired == 0 · 30m after rollout · roll back
observes: none — internal refactor, no runtime surface
```

Classify what you then see:
- **expected** — the signal supports the frozen rule;
- **rule violation** — the rule was right and the code or release failed → an escape (§11);
- **spec silence** — behavior mattered but no rule covered it → a new Direction, with the silence
  recorded as a `domain` delta.

## 11 · Escapes, successors and prevention

A closed task is history: what was believed and verified then. Never edit it. An escaped defect
opens a successor:

```
fixes: invite-expiry@8be0d44
```

with, in its CARD or LOG: the evidence (issue, incident, failing input), the reproducing check,
**why the old checks missed it** (no boundary falsifier, a mode missing, a consumer not run), and a
prevention bound to something that runs — a check, a monitor, a lint, a `Decision that binds`.
It drains only when one of these holds:
- the prevention is bound and green;
- the proposed prevention is rejected with evidence;
- a named owner accepts the residual risk until a stated date.

## 12 · Method economics

Every control here costs turns. Track what catches: when a probe, a second reader, a consumer run
or a persona finds a real defect, the `lens:` and `probes:` lines in EVIDENCE say so. Periodically
`grep -h '^lens:\|^probes:' .add/tasks/*.md` — a control with zero yield over many tasks is a
`method` delta proposing to drop it or re-aim it. A trust method can bloat too.

## 13 · The twelve invariants, and where each lives

| invariant | where ADD holds it |
|---|---|
| C1 intent lineage — every rule traces to a source or is marked derived | RULES `(from: …)`, `derived:` |
| C2 forward coverage — each Must/Reject has a discriminating check | CHECKS, one per rule |
| C3 verifier potency — a check fails a plausible wrong build | `falsifier:` + red-first |
| C4 independent evidence — high risk does not rest only on builder-visible checks | second reader, counter-lens probes (§4) |
| C5 regression — old behavior preserved | `regression:` (§5) |
| C6 artifact identity — a tag maps to verified commits | tag rule (§9) |
| C7 runtime mapping — critical behavior has a signal, or a reason it has none | `observes:` (§10) |
| C8 escape prevention — each escape binds a prevention or an owned risk | successor rule (§11) |
| C9 dependency impact — a changed surface checks its consumers | Verify step 3 (§6) |
| C10 historical immutability — closed history is linked, never rewritten | `fixes:`, rule 5 |
| C11 tripwire — Quick becomes a Task when risk appears | Quick lane, "is a Task now" |
| C12 economics — each control earns its cost | yield review (§12) |
