# 16 · Releasing

[← 15 Foundations and lineage](./15-foundations-and-lineage.md) · [Contents](./README.md) · Next: [17 Components — monorepo and multi-repo →](./17-components.md)

---

The loop chapters take one change from direction to a verdict, and a milestone until its goal is met. None of them *ship*. This chapter names that act: bundling closed milestones into a versioned release whose notes are backed by evidence, whose risks are disclosed, and whose behavior is then watched.

## Milestone ≠ release

A milestone is *goal met and consolidated*: every EXIT box ticked with evidence, its lessons folded into the specs. A release is *shipped and watched*. One version may carry several milestones — forcing one release per milestone is the anti-pattern.

## A release is work too

Preparing a release is a task like any other — `kind: release` — and it runs the same loop. Its rules are what the release must hold; its checks are whatever can fail:

```markdown
## RULES
- M1 every version declaration agrees with the new version (from: RELEASING.md)
- M2 the changelog has a section for the new version naming every bundled milestone (from: request)
- R:OPEN_HARDSTOP no bundled milestone has a task still at HARD-STOP (from: 09-governance)
- R:UNDISCLOSED every RISK-ACCEPTED verdict in a bundled task is named in the notes (from: 09-governance)

## CHECKS
- C1 covers: M1 · script · tests/test_version_parity.py
- C2 covers: M2, R:UNDISCLOSED · rubric · the notes read against each bundled task's ## EVIDENCE
- C3 covers: R:OPEN_HARDSTOP · script · grep for "verdict: HARD-STOP" in the bundled task files
```

The residue lens for release work is **the rollback path**: how is this version withdrawn if it misbehaves, and has that path been tried?

## The notes come from the record, never from memory

The evidence is already written down. Each bundled milestone's EXIT lines, each task's verdict, and the deltas folded into the specs are the source of the changelog. Group the changes under Added / Changed / Fixed in the user's language, not the commit's. Propose the version — a breaking change is a MAJOR, a new capability a MINOR, a fix-only cut a PATCH — and say which in the report.

## The floor does not move

**A security `HARD-STOP` is never shipped.** A milestone carrying one is not done, so it cannot be in a release. And every `RISK-ACCEPTED` that rides into a release is **named in the notes**: an accepted risk the user cannot read about is a hidden risk.

## The agent prepares; a person ships

The agent can prepare everything — the version bumps, the notes, the checks, the verdict. The outward act — the tag that triggers publishing, the deploy — is taken by a person, in a pipeline that owns the credentials, the retries and the rollback. Release behind something that limits the cost of a mistake: a feature flag, a gradual rollout, or both.

## Watch, and the hotfix path

A release is where the most reliable information finally appears. The checks that were pass/fail cases at build time become monitors. A regression found in the wild re-enters as a new task — a fix, scoped tight, cut as a PATCH. There is no separate emergency mode; there is the ordinary loop at a smaller scope.

## The arc

1. **Close** — every bundled milestone has every EXIT box ticked with evidence.
2. **Prepare** — a `kind: release` task: bumps, notes from the record, checks, verdict.
3. **Floor** — no open security `HARD-STOP`; every `RISK-ACCEPTED` disclosed.
4. **Ship** — a person tags and deploys behind a rollback-tested pipeline.
5. **Watch** — checks become monitors; a wild regression becomes a new task.

This repository releases itself this way; its recipe is [RELEASING.md](https://github.com/pilotspace/ADD/blob/main/RELEASING.md).
