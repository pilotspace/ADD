# Release — cut a versioned ship, never an unwatched flip

A project releases when ≥1 **closed milestones** are bundled into a versioned cut whose notes are evidence-backed, risk is disclosed, and behaviour is then watched. This is the **5th scope level** — distinct from milestone (feature-complete), graduation (rigor shift), and stage (mvp→prod).

- **milestone** = feature-complete and consolidated; **release** = shipped + watched.
- **graduation** changes *rigor*; a **release** ships a *version*. Orthogonal axes.

You **gather and propose**; the **human confirms and ships**; the engine records the cut and enforces a floor — it **never tags, publishes, or deploys**.

## The cue

When ≥1 milestone is `done` AND archived AND not yet attributed to a release, `add.py status` prints:

```
  → releasable: N milestone(s) closed since last release
```

That line is a tally over unreleased-but-archived milestones — never a readiness judgment.

## The flow

One arc, seven steps: **cue → gather → draft notes → readiness floor → human confirms → cut → watch.**

1. **Gather** — run `add.py release-report` (`--json` to branch on it). It clusters the cut's evidence: closed milestones since last release · consolidated deltas · open RISK-ACCEPTED waivers · open security HARD-STOP (blocker) · §2 scenarios to take live as monitors. Gathers, never judges.
2. **Draft notes** — write a [Keep a Changelog](https://keepachangelog.com/) entry from the consolidated deltas + each milestone's goal. Group Added / Changed / Fixed. Propose the **semver bump** (breaking→MAJOR, feature→MINOR, fix-only→PATCH) for human confirmation.
3. **Readiness floor** — the engine enforces: suite green, zero open security HARD-STOP, every RISK-ACCEPTED waiver signed and disclosed in the notes.
4. **Human confirms** — present via `report-template.md`, opening with the ARC (goal · done · plan). Render as a guided choice (per `report-template.md`). Never pre-stamp; show-before-ask.
5. **Cut** — only now run `add.py release <version> --notes <file>`. The engine records: CHANGELOG entry, append-only `RELEASES.md` row (newest-first: date · version · milestones · waivers · evidence), milestone attribution.
6. **Ship** — the **human** runs the tag / publish / deploy (`git tag`, `npm publish`, deploy pipeline). Engine never performs it.
7. **Watch** — §2 scenarios become live monitors. A regression re-enters at Specify as a **change request** → PATCH hotfix release.

## The floor

`add.py release <version>` is **guarded** — refuses (non-zero exit, state byte-unchanged) on:

<reject_codes>
- `release_security_open` — open security HARD-STOP exists. Never shipped. `--force` does NOT override this.
- `release_tests_red` — suite not green.
- `release_no_closed_milestone` — nothing new since last release.
- `release_undisclosed_waiver` — a RISK-ACCEPTED waiver rides into the release but is absent from the notes.
</reject_codes>

`--force` preserves human authority for grandfathered / edge cases (e.g. brownfield first cut) — never overrides `release_security_open`.

## Invariants

- **Engine records; human ships.** `add.py release` writes CHANGELOG + ledger + attribution; never tags, publishes, or deploys.
- **Security is a HARD-STOP at the cut**, not just at verify. No `--force`, no waiver, no exception.
- **Notes draw from consolidated deltas** — release after `fold.md` has run. Lifecycle order: `milestone-done → fold → compact → archive → (repeat ≥1×) → release → watch`.
- **Ledger is append-only (newest-first)** — a release row is never rewritten; a yanked version gets a new row.
- **A release bundles, it does not equal.** One version may attribute several milestones.

## Depth by stage

- **prototype/poc** — one-line preview note + tag; no deploy ceremony.
- **mvp** — full notes + tag + guarded publish; watch headline scenarios.
- **production** — full rigor: notes + tag + deploy behind rollback-tested pipeline + live monitors + error-budget watch. Hotfix path (step 7) is first-class.

## Worked example

The `udd-design-loop` milestone closed (4/4), consolidated into `foundation-version 33`; the human drafted `## [1.5.0]` from those deltas, bumped version sources in lockstep, and `test_release_1_5_0.py` asserted readiness. The `git tag` stayed human-gated; live-registry confirmation gathered *after* the tag as verify evidence, never a unit test.
