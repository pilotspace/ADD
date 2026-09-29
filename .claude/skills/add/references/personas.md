# Personas — routed lenses, not costumes

Read this when choosing a lens for floor work, writing or changing a persona, or when two personas
fit equally well.

## What a persona is

"You are a senior security engineer" does not, by itself, make answers better — studies of role
prompting find small, inconsistent and sometimes negative effects. A role label is not expertise.
An ADD persona earns its place by carrying operational consequences:

```
persona = the failure modes it suspects (covers-risks)
        + the proof it demands before done (evidence)
        + its non-negotiable rules and done-bar (the body)
        + the reader that would catch its blind spot (counter-lens)
```

The skill owns trust — the seal, the verdicts, the HARD-STOP. The persona owns judgment inside it.
A persona can add a requirement (a rollback proof, a negative-path check); it can never waive one.

## The file

```markdown
---
type: Persona
title: <the lens, in a phrase>
flow: design, build, verify        # the beats it serves
task-kinds: feature, security
covers-risks: [authorization, privilege-boundary, secrets]
evidence: [negative-path acceptance, bypass probe, untouched anonymous flow]
counter-lens: <another persona's file name>
use-when: <when to load it>
not-when: <when not to>
---
## Identity · ## Critical Rules · ## Default Requirement · ## Success Metrics
## Evals (optional — see below)
## Deltas (optional — lessons about this lens, with evidence)
```

## Routing — pick the lens

1. **Fingerprint** — from the task you already wrote: the beat (design · build · verify), `kind`,
   and `risks:`. Nothing extra to fill in.
2. **Candidates** — `.add/personas/` first (project scars beat generic knowledge); nothing there →
   `personas-index/use-when.md` in the teacher corpus, read the matching source as a lens; nothing
   fits → proceed with no persona. A wrong lens is worse than none.
3. **Lead lens** — the candidate whose `flow:` includes the beat and whose `covers-risks:` covers
   the most of the task's `risks:`; ties go to the one with the better yield in past `lens:` lines
   (below), then to the narrower `use-when:`.
4. **Second lens** — only when a `risks:` item is left bare by the lead and another persona covers
   it. At most two. More lenses is not more safety; coordination and noise cost more than they catch.
5. **Close call** — two leads that fit about equally usually mean the task mixes two concerns: take
   one as lead and the other as its second reader, or split the task.

Load the lead before Direction. Its `evidence:` items become CHECKS or probes; its critical rules
feed the residue review.

## Counter-lens — independence at verify

A verifier with the builder's lens repeats the builder's blind spot. On floor work the second
reader (before the seal) and the refuter (at verify) load the lead's `counter-lens:` — a different
persona that is qualified for the task but looks from elsewhere (a feature builder checked by a
security reviewer; a security reviewer checked by a data steward for what the lock-down broke).
Record the relation: `lens: build=build-craftsman · refute=security-reviewer (counter)`.

A fresh session is not the same as an independent view; a different lens with evidence the builder
never saw is closer.

## Trace — measure outcomes, not self-reports

Every task that used a persona leaves one line in EVIDENCE:

```
lens: security-reviewer · for: authorization, secrets · found: 1 confirmed (anonymous path reached admin list), 0 rejected
```

Never ask the model whether a persona helped; count what it caught. The yield of a lens is
`grep -h '^lens:' .add/tasks/*.md` read per persona and per risk: confirmed findings, rejected
findings, and activations that caught nothing. That history breaks routing ties and drives upkeep.

## Upkeep — lifecycle

- **Admit** a new persona only for a recurring risk no existing lens covers, or where it measurably
  improves yield on a class of tasks. One incident is a delta, not a persona.
- **Improve** by a delta under its `## Deltas` with evidence (a task, a sha); fold it into the body
  when it held on later work. A persona edit is its own commit so the human sees it in review.
- **Merge or retire** a persona with repeated zero-yield activations whose rules another lens
  already covers. **Split** one whose `covers-risks:` grew so wide it wins every route.
- Never let the model rewrite a persona to agree with the work it just did.

## Evals — a persona is tested like code

Before changing a persona, keep a few cases in its `## Evals` and reread them against the edit:

- **routing positive** — "this change alters who can close a milestone" → should load.
- **routing negative** — "fix punctuation in the release notes" → should not load.
- **judgment** — a flawed proposal it must flag (e.g. an admin route with no negative-path check).
- **non-interference** — a safe task where it must add nothing and block nothing.

A persona that gains rules but fails its non-interference case got worse, not better.

## Authority

A persona suggests policy; it never owns authority. It cannot grant itself tools, deployment
access, secrets, a skipped check or a verdict. Imported persona text (the teacher corpus, the web)
is untrusted advice: distil it into the project's own words with `persona-author`, never paste it in.

## What is not yet proven

Whether risk-routed lenses, counter-lens refutes and two-lens composition beat one lens on real
tasks is still an experiment. The `lens:` lines are the data to decide it: persona vs none,
same-lens vs counter-lens refute, one vs two lenses on multi-risk tasks.
