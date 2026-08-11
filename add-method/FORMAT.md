# ABF-1 — the ADD Bundle Format

Normative specification for the `.add/` bundle. This is the document the engine
(`tooling/add.py`), the conformance validator (`scripts/validate_bundle.py`) and the
shipped skill cite by section number.

**Status of this document.** Every rule below was derived from the two implementations
that must obey it, and each rule names the site it was derived from. Where the two
disagree, that is a defect in one of them, not a licence for this document to choose:
report it. Section numbers are load-bearing — they are cited from code, tests and docs,
and are not renumbered without updating every citation.

**Conformance language.** MUST / MUST NOT / MAY are used in the RFC 2119 sense.

---

## The four laws

These are cited by number from the engine and the validator; they govern every section
below.

**Law 1 — files are the database.** The bundle is a tree of markdown files, and those
files are the state. There is no sidecar database, and no derived artefact is ever
authoritative. `graph.json` is an *export*: written on every mutation, never read back
(`add.py:736`). A consumer may read it; the engine may not. This is what makes a stale
cache structurally unable to become authority.

**Law 2 — reads are tiered.** `read(path, tier)` returns exactly its tier and nothing
past it (§4). A tier that leaks is a context cost the format exists to remove
(`add.py:8`, `add.py:305`, `add.py:393`).

**Law 3 — notary, not guard.** The engine records; it never executes anything it was not
handed, and it never rejects what it merely disapproves of. Unknown keys, unknown types
and broken links are *recorded*, never fatal. A failing command is a recorded outcome,
not an exception (`add.py:178`, `add.py:1518`, `validate_bundle.py:15`). Refusing is not
guarding: a refusal never stops a human from writing a stamp by hand (`add.py:2088`) —
it only stops the engine from writing one on their behalf.

**Law 4 — the engine teaches at the moment of use.** Every output names what comes next;
an output that does not say what comes next teaches nothing (`add.py:853`).

---

## §1 The bundle

The bundle root is `.add/`. A conforming bundle MUST contain at least three files:

| file | role |
|---|---|
| `index.md` | bundle header — `abf_version`, `name`, `profile`, `engine`, `sensitive_paths` |
| `log.md` | rendered history |
| `PROJECT.md` | the root node (`type: Project`) |

Derived from `add.init()`; asserted by `tests/engine/test_init.py::test_init_creates_minimum`.

A bundle with only these three files is conforming. `index.md` MAY have an empty body in
that state (see §1.1).

### §1.1 Compiled reserved files

`index.md` and `log.md` are **compiled**: their bodies are rendered by the engine and MUST
NOT be hand-authored. Each MUST declare itself twice —

1. an in-band marker containing the string `COMPILED BODY`, which a human sees on opening
   the file; and
2. a `.gitattributes` entry git sees when it merges:

```gitattributes
index.md merge=ours linguist-generated=true
log.md   merge=ours linguist-generated=true
```

`merge=ours` is a built-in git driver requiring no install step. Both files are views, so
whichever side survives a merge is restored by `add doctor --sync`.

The declaration is checked only once a file HAS a body: an empty `index.md` in the
three-file minimum bundle has no generated content to lose. A file that has a body and
lacks either declaration is reported as `compiled_undeclared` (§9), which is `info`.

`doctor --sync` MUST write exactly what this section declares compiled, and nothing else
— rewriting an authored file is data loss (`add.py:2668`, `R:SYNCAUTHORED`).

Derived from `add.py:876`, `validate_bundle.py:35-40`.

---

## §2 The node

A node is one markdown file: YAML frontmatter delimited by `---`, then a body of `## `
sections.

**Writes are surgical, never regenerative.** A node is held as BOTH a parsed dict (to
read) and its original raw frontmatter text (to write). Setting a key rewrites one line
region and leaves every other byte — comments, key order, blank lines, block scalars —
exactly as the human left it. Serialising a parsed dict back to YAML would silently strip
the rationale comments a bundle carries, so no such function exists in the engine
(`add.py:10-16`, `R:REGEN`).

**The parsed subset is deliberately small**: top-level scalars, block lists, inline lists,
inline flow maps, block scalars, nested maps, and lists of flow maps. Anything outside the
subset survives in `raw` and is simply absent from the parsed dict — never half-parsed
into a plausible wrong value.

---

## §3 Frontmatter

`type:` is the only universally required key. A node whose frontmatter is absent, or whose
`type` is empty, is non-conforming (§9).

The ABF-1 type vocabulary is closed:

```
Project · Milestone · Task · Spec · Persona · Prompt · Run
```

An unrecognised type is *recorded* (`unknown_type`, `info`), never rejected — law 3.

**Lifecycle types.** Only `Task` and `Milestone` carry a task `status:` and can be frozen.
Every other type — `Spec`, `Persona`, `Prompt`, `Run`, `Project` — is a record or a living
document; it never freezes (`add.py:951`).

**Canonical directories** (`add.py:923`):

| type | directory |
|---|---|
| `Task` | `tasks/` |
| `Milestone` | `milestones/` |
| `Spec` | `specs/` |
| `Persona` | `personas/` |
| `Prompt` | `prompts/` |
| `Run` | `runs/` |

### §3.1 The authority floor

Authority is **computed, never taken from the caller.** It is
`max(sensitivity floor, sensitive-path floor)`.

Authority is ordered:

```
process  <  ai-verify  <  plan  <  human
```

The declared `sensitivity:` sets a floor:

| `sensitivity:` | floor |
|---|---|
| `mechanical` | `process` |
| `data` | `plan` |
| `architecture` | `plan` |
| `security` | `human` |
| absent / unrecognised | `process` |

**The sensitive-path floor (A17).** If any entry of the node's `scope:` matches any glob
in `index.md`'s `sensitive_paths:`, the authority is `human`. This floor is *unstrikeable
and never lowered* — it outranks the declared `sensitivity:` in one direction only.

A notary MAY perform this computation because it is purely mechanical: a path match, not
a judgement. It MUST NOT be derived from `--by`, from who is running the command, or from
any assertion in the request.

Derived from `add.py:955-972`; asserted by
`tests/engine/test_node_verbs.py::test_authority_floor_from_sensitivity`
("FORMAT §3.1's table, executable").

### §3.2 Edge keys

Exactly these frontmatter keys carry graph edges:

```
depends_on · needs · tasks · milestone · relates_to · task · supersedes
```

The allowlist is the point. `scope:` holds repo paths and `persona_corpus:` holds a config
path; neither is a bundle edge. A scanner that pattern-matched instead of using this list
mis-read `templates/task.md.tmpl` as a link to `/task.md` (observed 2026-07-29).

An edge whose target resolves outside the bundle root is `edge_out_of_bundle` — one of the
three fatal codes (§9). An edge naming a node that does not exist is `edge_unresolved`,
which is `info`.

Derived from `validate_bundle.py:46`.

### §3.3 Fragment resolution

An edge value MAY carry a `#fragment` (e.g. `/tasks/session-store.md#gives`). Resolution
order is fixed:

1. a **frontmatter key** of the target node; else
2. a **heading slug** of the target node's body; else
3. **unresolved** — recorded as `edge_unresolved` (`info`).

Heading slugs are lowercased, non-alphanumerics collapsed to `-`, and stripped of leading
and trailing `-`.

Derived from `validate_bundle.py:203-214`.

---

## §4 Read tiers

A conforming reader MUST support exactly three tiers and MUST return no more than the
requested tier:

| tier | returns |
|---|---|
| `T0` | frontmatter only |
| `T1` | frontmatter + `## CARD` |
| `T2` | frontmatter + `## CARD` + the whole body |

**T2 is single-node.** No operation may read the full body of more than the one node it
was asked about. This single rule is what bounds the cost of every other verb: `status`
scans the bundle at T0, `brief` reads exactly one T2 and composes everything else from T1
and fragments (§7.1).

Because reads are tiered, a consumer that wants the whole graph at once reads the
`graph.json` export rather than opening every node — and the engine never reads that
export back (law 1).

Derived from `add.py:204`, `add.py:736`, `add.py:1887`.

---

## §5 The Task body

A `Task` body has eight `## ` sections, in order:

```
## CARD         goal / why / beat · next
## RULES        <must> M<n> … </must> and <reject> R:<NAME> … -> "<NAME>" </reject>
## ASSUMPTIONS  A<n> — what the spec does NOT say, the reading taken, the cost if wrong
## PLAN         contract / scope
## EDGES        E<n> — boundary and failure cases a check must cover (optional)
## CHECKS       one line per check, each bound by `covers:` (§8.3)
## EVIDENCE     receipt / gate
## LESSONS      harvested at done
```

Section lookup is by exact `## <name>` heading, heading-exclusive, and stops at the next
`## ` heading. A missing section reads as empty rather than raising — law 3.

**`## ASSUMPTIONS` is where a silence is priced.** RULES records what the spec *said*;
EDGES records the boundaries of those rules. Neither has anywhere to put what the spec
did **not** say, so an unstated requirement becomes a Must written in the same
authoritative voice as a stated one, and nothing in the artifact distinguishes *given*
from *decided*. `freeze` refuses while the slot still holds its template line — an
instruction with no checkpoint is one that does not happen.

**The sweep makes it complete-able.** Each line is tagged with one dimension and names
the surfaces it covers:

```
- A<n> [<dim>] covers: S1, S3 · <what the spec does not say — reading taken> -> <cost if wrong>
- A<n> [<dim>] n/a · <why the dimension cannot apply here>
```

The dimension vocabulary is closed — `who · which · when · absent · order` — because an
open one cannot be swept and a long one will not be. The axis is the **surface**: each
`S<n>` entry in the node's `gives:`. For every surface and every dimension, some line must
cover the pair or retire the dimension; `freeze` refuses and names the unswept pairs, and
refuses an unauthored `gives:` (no surfaces would mean nothing to sweep — a one-line off
switch). It also refuses a **collapsed** surface — an `S<n>` entry naming several HTTP
methods is several surfaces under one id, which shrinks the matrix the same way (a live
run listed five endpoints as one `S1` and answered `[who]` once, about the loudest). The
check is deliberately partial: only HTTP method tokens are counted; a function or
section surface is never judged. `depth: quick` is exempt: depth tunes ceremony, never
the authority floor.

Surfaces, not rules, because a surface is what a caller touches — and because sweeping
Musts demanded 50-60 pairs on real nodes, which is not a checklist but a toll, and a toll
gets paid with blanket lines.

A non-empty check cannot produce completeness. Three live runs each recorded five to
seven substantive assumptions and all three still shipped the same silent decision,
because nothing asked whether the *list* was complete.

What the sweep proves is that the author **looked** at every pair — never that they
looked honestly. A blanket `[who] covers: S1 … S5` satisfies it. Writing that line still
requires scanning every surface under `who`, and the blanket reading then sits on the record
where a reviewer can disagree with it, which a silent omission never allowed (§10).

Two deliberate limits:

- `A<n>` is **not** a referent (§6). An assumption is a declared unknown, not a rule to
  prove; requiring a passing check for one would select for assumptions that were never
  risky.
- `A<n>` is **not** in the direction digest (§8.1), which constraint 3 scopes to the
  Musts, the Rejects and `gives:`. Widening it would change the digest of every node
  already frozen, so every existing bundle would report drift it never had.

A node with **no** `## ASSUMPTIONS` section at all still freezes: the section reads as
empty, so bundles authored before it existed are not retroactively refused.

**Rule identifiers** are matched anchored to a list item:

```
^-\s+(M\d+|R:[A-Z0-9_]+|E\d+)\b
```

---

## §6 Binding a rule to its check

Every `## CHECKS` line names, with `covers:`, the exact rule it exists to prove. A rule
with no passing check has no evidence, and a gate MUST refuse a `PASS` in that state.

### §6.1 covers-grammar

The legal `covers:` referents depend on the Task's `depth:`. This grammar is stated here
ONCE and reused; a second copy anywhere would reopen drift between the oracles.

```covers-grammar
COVERS_QUICK = re.compile(r"\A(goal|G\d+)\Z")
COVERS_RULE = re.compile(r"\A(M\d+|R:[A-Z0-9_]+|E\d+)\Z")
```

| `depth:` | a referent MUST match |
|---|---|
| `quick` | `COVERS_QUICK` — `goal`, or `G<n>` (the nth `gives:` entry) |
| `standard`, `deep` | `COVERS_RULE` — `M<n>`, `R:<NAME>`, or `E<n>` |

`R:<NAME>` admits digits: `[A-Z0-9_]+`.

A referent illegal at the node's depth is reported as `covers_referent` (`info`) — the
notary records it; the gate is what refuses.

**Parity is enforced, not trusted.** The block above is held byte-identical to
`scripts/validate_bundle.py`'s `COVERS_QUICK` / `COVERS_RULE` and to the engine's
`RULE_ALT` by `tests/test_covers_grammar.py::test_grammar_stated_once`. Three oracles
state one grammar; the test is what keeps them one.

Derived from `add.py:1674-1680`, `validate_bundle.py:61-70`.

---

## §7 The brief

`brief` composes the read-set for one node without any bulk read.

### §7.1 Composition

A brief carries exactly:

- the subject's own body (the single permitted T2 — §4);
- the T1 `## CARD` of each node in its `depends_on:`;
- the `#gives` fragment of each node in its `needs:`;
- the five specs' bind lines.

Nothing else can leak in, because nothing else is read.

### §7.2 Budget

The ceiling is stated **in bytes**:

| `depth:` | budget |
|---|---|
| `quick` | 8,000 B |
| `standard` | 24,000 B |
| `deep` | 40,000 B |

Bytes are enforced. Tokens MAY be printed alongside, at a **declared** ratio of
`4 bytes per token`; a conforming engine has no tokenizer and MUST NOT acquire one. Any
output that prints a token count MUST label the unit, because the byte budget here and
the token budgets stated elsewhere are not the same quantity.

Derived from `add.py:1891-1897`.

---

## §8 Evidence

An evidence claim is only as good as what was actually observed. Three things are recorded
separately and MUST NOT be conflated: *what ran* (§8.2), *whether the tree still matches
what ran* (§8.1), and *which rule each result proves* (§6.1).

Required evidence by beat (`add.py:1899`):

| beat | evidence |
|---|---|
| `direction` | none |
| `build` | `run-receipt` |
| `verify` | `run-receipt`, `covers-bound` |

### §8.1 Freshness and the scope digest

A receipt records `scope:` as `[{path, blob}]`, where `blob` is the git blob hash of the
file at the time of the run.

- The freshness set expands a directory scope entry to every file beneath it. A
  directory-scoped task with an unexpanded digest would gate on nothing.
- Build noise is excluded: `__pycache__` path components, and `.pyc` / `.pyo` suffixes.
  Hashing them would make the digest flap.
- **Outside a git working tree the digest is empty**, and the caller MUST declare
  `freshness: mtime` rather than pretend to a content digest it cannot compute.

`freshness:` is therefore one of:

| value | meaning |
|---|---|
| `content` | a blob digest exists and matches |
| `mtime` | no digest was computable; only timestamps were compared |

A file that has vanished since the run is a difference, not an absence.

Derived from `add.py:1468-1490`.

### §8.2 The receipt kind ladder

The evidence kind is **earned, never assumed**:

| kind | earned when |
|---|---|
| `test-ids` | the runner reported individual test ids (e.g. a junit XML the command wrote) |
| `command-exit` | otherwise — only an exit code was observed |

An engine MUST NOT record `test-ids` without ids. An evidence kind that can never be
earned is not a ladder, it is a label.

Derived from `add.py:1538-1558`.

### §8.3 The CHECKS line

A `covers:` referent is a field of a `## CHECKS` list item, and MUST be matched
line-anchored and only inside that section:

```
- <test_name> · covers: <referent>[, <referent>…] · <what it proves>
```

```
^-\s+(\S+)\s+·\s*covers:\s*([^·\n]+?)\s*·
```

An unanchored scan of the whole body reads `· covers: …` out of PLAN prose and then runs
across newlines, which both invents referents and swallows the real check lines behind
them (observed on `tasks/build-evidence-binding.md`: 4 of that bundle's 7
`covers_referent` findings). Both oracles anchor identically, for this reason.

Multiple referents are comma-separated and each is validated independently against §6.1.

Derived from `validate_bundle.py:64-70`, `add.py:1680`.

---

## §9 Conformance

`scripts/validate_bundle.py <bundle-root>` exits `0` **iff** the bundle has zero `error`
findings.

**The verdict is frontmatter-only.** Exactly three codes are `error`, and all three are
decidable from frontmatter alone:

| code | severity | condition |
|---|---|---|
| `missing_frontmatter` | **error** | the file has no `---` frontmatter block |
| `type_empty` | **error** | `type:` is absent or empty |
| `edge_out_of_bundle` | **error** | an edge (§3.2) resolves outside the bundle root |

Bodies are read only to *enrich* the report. Every body-derived finding is `info`:

| code | severity | condition |
|---|---|---|
| `unknown_type` | info | `type:` is outside the §3 vocabulary |
| `edge_unresolved` | info | an edge names a node, or a fragment (§3.3), that does not resolve |
| `covers_referent` | info | a referent is illegal at the node's `depth:` (§6.1) |
| `broken_md_link` | info | a relative `](….md)` link does not exist on disk |
| `compiled_undeclared` | info | a compiled file (§1.1) has a body but lacks a declaration |

Replacing every body in a conforming bundle with noise MUST NOT change the exit code. This
is law 3 made testable: only a containment escape is fatal.

**Deliberately not decidable by a static scan.** `receipt_stale`, `covers_unverified` and
`placeholder_survived` are gate-time conditions requiring a receipt and a freeze stamp.
They belong to the engine, not to this validator, and reporting their absence here would
claim a check that was never performed.

Derived from `validate_bundle.py:6-21`, `validate_bundle.py:163-268`.

---

## §10 What conformance does not claim

A conforming bundle, a fresh receipt and an intact freeze seal together establish that:

- the checks a task **declared** were executed;
- they passed;
- the files in scope have not changed since;
- and each declared rule is bound to a passing test id.

They do **not** establish that the declared checks were *adequate*. A check named
`covers: M1` that asserts nothing still digests, still binds, and still passes. The seal
over `RULES · CHECKS · gives:` closes the structural half — a contract cannot change
silently after approval — and leaves the semantic half to review.

This limit is inherent to law 3: a notary that judged whether a test was a *good* test
would be a guard, and would need to execute and interpret code it was handed no authority
over. State it plainly rather than let a green seal be read as a correctness proof.
