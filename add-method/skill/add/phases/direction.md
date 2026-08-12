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

## The four sections (all in the node body)

- **`## RULES`** — `Must` (what it must do) · `Reject` (what it must refuse, each a `R:CODE`) · `After`
  (post-conditions). What you were **told**, and only that.
- **`## ASSUMPTIONS`** — `A<n> [<dim>] covers: <S ids> · <what the spec does NOT say — and the
  reading you took> -> <cost if wrong>`. **Sweep every `gives:` surface on every dimension** —
  `who · which · when · absent · order · experience` — or retire one with `[<dim>] n/a · <why>`. `freeze`
  REFUSES while a slot is template, `gives:` is unauthored, or a `(dimension, surface)` pair is
  unswept — and it names the pairs. `add todo` counts them down while you author, so freeze confirms
  work already done instead of ambushing you with the whole matrix.

  **Work the matrix, don't free-associate.** Author `gives:` FIRST — the `S<n>` surfaces this node
  publishes — since that is the axis the sweep runs along and freeze refuses while it is template.
  **Enumerate ALL the surfaces**: every route × verb, function, or section the request touches is
  one — including the read paths it mentions in passing. One surface per `S<n>` id — freeze
  REFUSES an entry naming several HTTP methods, several distinct `name()` callables, or several
  backticked documents, because five endpoints under one id shrinks the
  matrix to one set of questions about the loudest of them. The sweep can only force questions about
  surfaces you listed; in five live runs the never-questioned silences all lived on the quiet
  `GET` path while every run wrote assumptions about the loud `POST` path, because free-association
  follows the spec's own emphasis (a spec that discussed status constantly and named caller
  identity once).
  Then take each surface and ask all six: *who* may do this and
  whose data is it · *which* rows/cases are in and which are filtered out · *when* — is the boundary
  inclusive · what if the value is *absent* · what *order* / what breaks a tie · whose *experience*
  is this — who RECEIVES the output and what would make it hard for them. That last one is the only
  dimension not about correctness, and the only one `who` does not already answer: `who` is
  authorization, `experience` is audience. Name the recipient AND the difficulty; either half alone
  is answerable without looking.
  When a taken reading is checkable against the running code, say so on the line:
  `· probe: <what shipped behavior must show>` makes that `A<n>` a `covers:` referent — cite it
  from a CHECKS line and the gate holds the PASS until that check reports passing. Probe the
  readings whose cost-if-wrong is the highest; an unprobed line stays a priced guess on the record.

  **One line, one silence.** Each `A<n>` names ONE open question. A line that resolves the
  contradiction *and* carries the ordering, boundary and visibility questions in the same breath
  is not auditable — a reviewer can only agree or disagree with it wholesale, and each silence it
  bundles loses its own answer, its own cost-if-wrong, and its own place to be challenged. The
  scaffold is one line per dimension; keep that shape as you author.

  **Discharge the dearest guesses — the micro-spike.** A line whose cost-if-wrong is high MAY be
  discharged before freeze by a bounded micro-explore: a few targeted tool calls inline (read the
  code path, probe the API, check the doc) — never a task. Key the effort on cost-if-wrong —
  highest first, checkability second; evidence where guessing is expensive, guessing where evidence
  is not worth its cost. Record it on the line: the taken reading becomes
  `· found: the answer (evidence: a file+line, doc, URL, or command output)` — found without its
  evidence ref is not a discharge, just a louder guess. The line itself stays in ASSUMPTIONS,
  never deleted — the record that the silence existed and was answered; found-lines stay freely
  editable like any assumption. This is optional per line — an undischarged silence stays a
  legitimate priced guess. When the question outgrows a few calls it is no micro-spike any more:
  route it to the Explore lane through intake (`intake.md`), never a shadow research task.

  Write one here whenever you catch yourself about to state something the request never said. The
  failure this exists to stop is silent and looks like competence: an unstated requirement gets
  written as a Must in the same authoritative voice as a stated one, a check is bound to it, the
  check passes, and the gate goes green on a decision nobody ever made. RULES has no slot for
  "nobody told me" and EDGES only bounds rules you already wrote, so without this section the
  guess has nowhere to be visible.

  An assumption is a declared **unknown**, not a rule: it needs no check (`A<n>` is not bindable by
  `covers:`) and editing one does not break the freeze seal.
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

The graph, `brief`, downstream re-scoping AND the assumption sweep all read a node's `gives:` (the
surfaces it publishes) and `needs:` (the frozen fragments it consumes) from **frontmatter**. `new`
scaffolds `gives:` and `freeze` refuses while it is still template — it went unauthored in 3 of 3
live runs when nothing asked for it. Give each surface an `S<n>` id; that id is what an ASSUMPTIONS
line names in its `covers:`:

```yaml
gives:
  - S1 auth.verify(token) -> Claims | None       # a surface this node publishes
  - S2 GET /sessions — the caller's own sessions
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
