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

Before drafting, gather the real code the task touches — files, symbols, signatures, conventions — into
a lean grounding map and surface the **anchors** the contract will cite. In a milestone, ground is gathered
ONCE (`## GROUND`); tasks **project** from it. Take the **lens** with it: the `.add/personas/` entry whose
`flow:` names design and whose `task-kinds:` covers the node's `kind:`; no fit → `.add/personas-index/use-when.md`; none → proceed. Record it: `add advise <slug> --persona <p>`.

## The five sections (all in the node body)

- **`## RULES`** — `Must` (`M<n>`, what it must do) · `Reject` (`R:<CODE>`, what it must refuse).
  What you were **told**, and only that.
- **`## ASSUMPTIONS`** — `A<n> [<dim>] covers: <S ids> · <what the spec does NOT say — and the
  reading you took> -> <cost if wrong>`. **Sweep every `gives:` surface on every dimension** —
  `who · which · when · absent · order · experience` — or retire one with `[<dim>] n/a · <why>`. `freeze`
  REFUSES while a slot is template, `gives:` is unauthored, or a `(dimension, surface)` pair is
  unswept — and it names the pairs. `add todo` counts them down while you author, so freeze confirms
  work already done instead of ambushing you with the whole matrix.

  **Work the matrix, don't free-associate.** Author `gives:` FIRST — the `S<n>` surfaces this node
  publishes — since that is the axis the sweep runs along. **Enumerate ALL the surfaces**: every route ×
  verb, function, or section the request touches is one, the quiet read paths included; freeze
  REFUSES an entry naming several (five endpoints under one id shrinks the matrix to the loudest).
  In five live runs every never-questioned silence lived on the quiet `GET` path, because
  free-association follows the spec's own emphasis. Then ask each surface all six: *who* may do this
  and whose data is it · *which* rows/cases are in · *when* — is the boundary inclusive · what if the
  value is *absent* · what *order* / what breaks a tie · whose *experience* is this — who RECEIVES the
  output and what would make it hard for them (`who` is authorization, `experience` is audience;
  name the recipient AND the difficulty). A reading checkable against running code says so on the
  line: `· probe: <what shipped behavior must show>` makes that `A<n>` a `covers:` referent the gate
  holds the PASS to. Probe the readings whose cost-if-wrong is highest.
  **One line, one silence.** Each `A<n>` names ONE open question. A line that resolves the
  contradiction *and* carries the ordering, boundary and visibility questions in the same breath
  is not auditable — a reviewer can only agree or disagree with it wholesale, and each silence it
  bundles loses its own answer, its own cost-if-wrong, and its own place to be challenged. The
  scaffold is one line per dimension; keep that shape as you author.

  **Discharge the dearest guesses — the micro-spike.** A high-cost line MAY be discharged before
  freeze by a bounded micro-explore — a few targeted tool calls inline (read the code path, probe
  the API, check the doc), never a task — optional; highest cost-if-wrong first, then checkability. Record
  it on the line: `· found: the answer (evidence: a file+line, doc, URL, or command output)` —
  found without its evidence ref is not a discharge, just a louder guess. The line stays in
  ASSUMPTIONS, never deleted, and stays editable; an undischarged silence is a legitimate
  priced guess. A question that outgrows a few calls goes to the Explore lane via intake (`intake.md`).

  Write one whenever you catch yourself about to state something the request never said. The
  failure this stops looks like competence: an unstated requirement written as a Must in the same
  voice as a stated one, a check bound to it, the gate green on a decision nobody made. RULES has no
  slot for "nobody told me"; without this section the guess has nowhere to be visible.
  An assumption is a declared **unknown**, not a rule: a plain `A<n>` needs no check, and editing
  one does not break the freeze seal. Declare it `· probe: <what shipped behavior must show>` and
  it becomes bindable by `covers:` like any other referent — that is opt-in, never automatic.
- **`## PLAN`** — the **contract shape** (this becomes the frozen `gives:` — the interface neighbors
  depend on) · the build **strategy** · the `scope:` tokens (the paths this node may touch; also the
  freshness set) · the regression floor · optionally `port: <the seam acceptance checks exercise>` —
  unbound, unswept; it exists so an acceptance check is fast by construction, not a browser test.
- **`## EDGES`** — `E<n>` — the readable **example**: `E<n> Given <state> · When <action> · Then
  <observable result>`, so a non-technical owner can read it and say *that is what we mean* (RULES are
  the rules, filled EDGES the examples, ASSUMPTIONS the questions — Example Mapping's three columns;
  more than ~8 filled edges is two nodes). Optional, and NOT free:
  a line you FILL becomes a gate-bound referent exactly like a Must, so `gate PASS` refuses until
  some check names it. The scaffold's untouched `<placeholder>` owes nothing — writing an edge is
  what binds it. Retire one by deleting the line, never by answering it `n/a`.
- **`## CHECKS`** — the **red suite**: at least one check per binding referent (`M` · `R` · filled
  `E` · probed `A`), each carrying a `covers:` key naming what it proves, and each written to FAIL
  on the most plausible wrong implementation — that is what a check is for, never a quota. One check
  may cover several referents when it discriminates each; at a plan or human floor a Must carries
  two checks of different mode (§ router). A `Must`/`Reject` encoded in **no** check means RULES is
  not understood — **stop and say so**. Minor behaviors are build guidance, not gated checks.
  For code the **default frozen check is an acceptance check**: business-readable, run through the
  port with deterministic adapters behind it, and it covers at least one filled edge — the example and
  the check stay bound through `covers:`. A unit check is frozen only when it is the cheapest
  discriminating evidence for a rule, never because a rule exists. Open the free text after the
  second `·` with a mode word — `acceptance · property · contract · static · unit · e2e · manual` —
  the engine never parses it; the router (§ PLAN) says which modes a change kind earns.

`covers:` grammar (FORMAT §6.1): at `quick` depth a referent is `goal` or `G<n>` (nth `gives:`); at
`standard|deep` it is `M<n>` (a Must), `R:<CODE>` (a Reject), `E<n>` (a filled edge) or `A<n>` (an
assumption you declared `· probe:`-able). Those six forms are the whole vocabulary the gate
resolves; a `covers:` naming anything else binds nothing.

## The evidence router — modes by change kind × computed floor

| change kind | default frozen evidence | added at floor ≥ plan | not frozen |
|---|---|---|---|
| mechanical · refactor | existing regression + static/architecture check | diff-scope check | new acceptance checks |
| small business rule | 1–3 acceptance examples | a property, if an invariant is nameable | a unit suite |
| algorithm · pricing · ranking | acceptance examples | properties + mutation on changed code | hand-picked edge lists |
| API · event boundary (a consumed `gives:`) | acceptance + consumer contract | one integration smoke | a broad e2e suite |
| data migration | data invariants as properties | rehearsal + rollback proof | unit-only evidence |
| UI workflow | acceptance per screen state | 1–2 browser e2e + a11y | every scenario in a browser |
| concurrency | acceptance | invariant under stress / schedule probes | example-only suite |
| auth · payment · security (floor human) | acceptance + negative examples | properties + probes + a fresh-session refute | builder-visible checks alone |

Preferred, not enforced — the floor still computes from sensitivity; record a divergence on the PLAN line. Property, contract and mutation checks are checkers that emit JUnit: recipes in `domains.md` §1.

## Run red — for the right reason

Author the checks and run them: they MUST fail, and fail because the behavior is absent, not because a
name is misspelled or an import is missing. A green check before any build is a check that proves
nothing. (At `quick` depth one call cannot produce a prior-red receipt; it records `red_first: unproven`
rather than claiming evidence it lacks.) Red proves the runner and fixture detect an ABSENT behavior; it
never proves the reading of the rule is right — when one session wrote rule, check and code, all three
can share a misunderstanding. The oracle is proven at `add interview` and the freeze, or at Verify by a
session that did not build.

## Get the working prompt from the graph

`add brief <slug>` compiles the beat's XML prompt — the node's body, T1 cards of its `depends_on`, the
frozen `#gives` fragments it `needs:`, the five specs' *Decisions that bind*. Refs resolve **at brief
time**, so a spec edit re-scopes every future prompt. Never copy spec prose into a node.

## Author the contract edges yourself

The graph, `brief`, re-scoping AND the sweep read `gives:` (surfaces published) and `needs:` (frozen
fragments consumed) from **frontmatter**; `freeze` refuses a template `gives:` — it went unauthored in
3 of 3 live runs when nothing asked. Each surface gets an `S<n>` id, the one ASSUMPTIONS `covers:`:

```yaml
gives:
  - S1 auth.verify(token) -> Claims | None       # a surface this node publishes
  - S2 GET /sessions — the caller's own sessions
needs: [/tasks/session-store.md#gives]            # a frozen fragment it builds on
```

## The one approval — freeze

`add freeze` **stamps direction closed** — the single human approval that opens Build. It does *not* bind
coverage and does *not* write `gives:` (author that above); the `covers:`→rule binding is enforced later, at
**`add gate`**, against a real receipt. Freeze is the approval; the gate is the proof.

```bash
add interview <slug>                                  # read the open decisions
add interview <slug> --answer A1=confirm --answer R:LEAK=confirm --by "<name>"
add freeze <slug> --by "<name>" --authority human
```

Authority floor by sensitivity (unstrikeable): mechanical→process · data→plan · architecture→plan ·
**security→human, never derived, never batched**. A sensitive `scope:` path raises the floor to human
regardless. The freeze is the single human decision of the whole task; present it via `gate.md`.

**At a human floor the approval is interviewed first.** `add interview <slug>` compiles every non-`n/a`
assumption, every Reject and every filled edge into a numbered question carrying the reading you took
and the cost if wrong; `freeze` refuses until each is `confirm`, `correct` or `defer` (R:UNINTERVIEWED).
Every other refusal checks the DOCUMENT — this one checks the CONVERSATION.

Put the questions to the human for real, one decision at a time, in their own words.
**Never record an answer you were not given** (R:SELFANSWER). `correct` does not complete an interview: it is
cleared by editing the item, which moves the digest and re-opens the pass; `defer` does — a human may accept a risk knowingly.
Reword an interviewed assumption or edge and the interview goes stale; edit a Must and it does not.

## When Direction reveals a gap

If drafting the checks exposes a missing rule, that is the method working — fold it into RULES and re-derive
forward. Backward correction is always allowed; forward-skipping (building before red) is forbidden. → `phases/build.md`.
