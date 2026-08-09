# Beat 1 · Direction — fix the direction before any code

Direction produces one frozen node: **rules, a contract, and red checks**, approved once. It is the
steering; Build is the engine. You do not start the engine until the wheel is set.

Compose the **whole bundle in ONE silent draft** — no per-section narration. Then present it for the
one approval, lowest-confidence-first.

**How you author it.** `add new Task <slug>` scaffolds the node file at `.add/tasks/<slug>.md` with
a `## CARD` (`goal:` · a one-line `why:` · `beat:`) and empty `## RULES / PLAN / CHECKS` sections.
There is **no author verb** — you fill those sections by editing that file directly (the engine
records; it never writes the method for you). Then run the checks red, then `add freeze`.

The CARD's `why:` is one line — the decision-rationale a plausible `goal:` can hide (*why this node
exists*, not what it does). **Optional on a task, required on a milestone**: `add milestone-done`
refuses to close while a milestone's `why:` is still an unfilled placeholder — rationale is not a
silent skip. Keep it to one line; a full section would just re-weigh the bundle.

## Ground first (AI-owned, adds no approval)

Before drafting, gather the real code the task touches — actual files, symbols, signatures,
conventions — into a lean grounding map, and surface the **anchors** the contract will cite. In a
milestone, ground is gathered ONCE on the milestone (`## GROUND`); tasks **project** from it and never
re-ground the repo. Aim the bundle at reality, not assumption.

## The three sections (all in the node body)

- **`## RULES`** — `Must` (what it must do) · `Reject` (what it must refuse, each a `R:CODE`) · `After`
  (post-conditions), plus the **one riskiest assumption** and what it costs if wrong. Co-specify the
  assumption; do not bury it.
- **`## PLAN`** — the **contract shape** (this becomes the frozen `gives:` — the interface neighbors
  depend on) · the build **strategy** · the `scope:` tokens (the paths this node may touch; also the
  freshness set) · the regression floor.
- **`## CHECKS`** — the **red suite**: one check per `Must` and per `Reject`, each carrying a `covers:`
  key naming the rule it proves. A `Must`/`Reject` encoded in **no** check means RULES is not
  understood — **stop and say so**. Minor behaviors are build guidance, not gated checks.

`covers:` grammar (FORMAT §6.1): at `quick` depth a referent is `goal` or `G<n>` (nth `gives:`); at
`standard|deep` it is `M<n>` (a Must) or `R:<CODE>` (a Reject).

## Run red — for the right reason

Author the checks and run them: they MUST fail, and fail because the behavior is absent, not because a
name is misspelled or an import is missing. A green check before any build is a check that proves
nothing. (At `quick` depth one call cannot produce a prior-red receipt; it records `red_first: unproven`
rather than claiming evidence it lacks.)

## Get the working prompt from the graph

`add brief <slug>` compiles the beat's XML prompt — the node's own body, T1 cards of its `depends_on`,
the frozen `#gives` fragments it `needs:`, and the five specs' *Decisions that bind*. Its refs resolve
**at brief time**, so editing a spec re-scopes every future prompt with no prompt edit. Never copy spec
prose into a node — that is what makes scope changes expensive.

## Author the contract edges yourself

The graph, `brief`, and downstream re-scoping read a node's `gives:` (the contract shape it publishes)
and `needs:` (the frozen fragments it consumes) from **frontmatter** — and nothing records them for you.
Before you freeze, hand-author them into the node's frontmatter, e.g.:

```yaml
gives: "auth.verify(token) -> Claims | None"      # the shape this node publishes
needs: [/tasks/session-store.md#gives]            # a frozen fragment it builds on
```

## The one approval — freeze

`add freeze` **stamps direction closed** — the single human approval that opens Build. It does *not*
bind coverage and does *not* write `gives:` (author that above). The `covers:`→rule binding — every
`M<n>` and `R:<CODE>` covered by a passing check — is enforced later, at **`add gate`**, against a real
receipt. Freeze is the approval; the gate is the proof.

```bash
add freeze <slug> --by "<name>" --authority human
```

Authority floor by sensitivity (unstrikeable): mechanical→process · data→plan · architecture→plan ·
**security→human, never derived, never batched**. A sensitive `scope:` path raises the floor to human
regardless. The freeze is the single human decision of the whole task; present it via `gate.md`.

## When Direction reveals a gap

If drafting the checks exposes a missing rule, that is the method working — fold it into RULES and
re-derive forward. Backward correction is always allowed; forward-skipping (building before checks are
red) is forbidden. → then `phases/build.md`.
