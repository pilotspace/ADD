# ADD final enhancement plan v2

This refinement compares `tmp/ADD-final-enhancement-plan.md` with the supplied
`ADD-next-enhancement-research-plan.md`. The earlier plan remains the detailed rationale and target
experience. This document records the accepted deltas and the implementation order.

## Governing invariant

Every handoff that changes responsibility, authority, or trust preserves the exact subject, claim,
evidence class, and limit of what the evidence proves. The engine remains a local notary and graph
reader; it does not become an identity provider, CI runner, agent manager, or empirical evaluator.

## Adopted refinements

- Split proof into mechanism, provenance, and effectiveness. A green local fixture proves only the
  mechanism it exercises.
- Make receipt purpose explicit: bound evidence, regression floor, diagnostic support, and later
  externally attested holdout evidence have different authority.
- Treat moved work as a counted state whose destination must explicitly accept the stable source
  obligation. A source note alone cannot transfer responsibility.
- Compile a complete, digest-bound decision manifest and show a refreeze delta while keeping one
  human approval and every decision ID accessible.
- Require later independent eligibility before an escaped-defect prevention is promoted into a
  binding policy.
- Prove persona instruction truth before routing studies; assess usefulness through repeated
  neutral/correct/wrong-persona trials.
- Add source-to-built-artifact install and upgrade smoke evidence. External CI and registry
  attestations establish authenticity; ADD records their subjects and references.

## Deliberate limits

- No second approval, refusal log in authoritative state, persona authority, local `T4` label,
  universal end-to-end mandate, or productivity claim from fixtures.
- Current `defer` behavior is described precisely; this release does not create a new gate outcome
  or reinterpret unanswered input as acceptance.
- External model trials wait for a predeclared cost cap. Human comprehension trials wait for real
  participants. The harness and protocol may ship before those results exist.

## Compatibility constraints discovered in branch review

- Moved criteria need authored stable IDs. Generated ordinal references such as `#C5` drift when
  criteria are reordered, and the current checkbox parser silently ignores `[~]`.
- `carries:` belongs to node/obligation edges with an explicit local mapping; the existing
  `relations:` vocabulary is for Spec delta concepts and cannot represent Task Must ownership.
- Effective verdict ordering comes from append-only stamp order and reopen boundaries, not day-only
  dates. A later run or refute cannot hide an earlier unresolved HARD-STOP.
- Legacy receipts normalize to `bound` when purpose is absent and to `floor` when the existing
  regression marker is present. A local run cannot claim protected `holdout` origin.
- Later escape validation cannot rely on dates alone. It requires a resolvable independent receipt
  and durable Git/source containment; the filing task cannot validate itself.
- Persona commands execute only in tests/evaluation tooling. The notary and build path remain
  NO-EXEC.
- Publishing must consume the exact artifacts built, hashed, and smoke-tested by CI; rebuilding in
  independent registry jobs breaks the source-to-installed-artifact proof.

## Delivery milestones

### As-built checkpoint — 2026-09-16

The security scope-seal Tasks remain Direction/red because their computed human floor
requires a real, separate interview for each Task. Independent B1 status and B2 moved-EXIT
mechanisms were built and process-gated meanwhile: B1 binds a consequential verdict to
its own gate stamp; B2 keeps `[~]` in the original tally and accepts a reciprocal Milestone
destination only under a current EXIT-bound freeze. This sequencing preserves the human
boundary while using safe independent work. The historical `loop-that-closes` line still
has no accepted destination; it is 10/11, not a completed transfer. B3 inherited carries
and B4 repair/scope return remain red Direction contracts until A's seal and human authority
are supplied. The independent C2 local candidate gate is process-gated: receipt 2 binds
29 passing checks, a fresh GPT-5.6 T2 held after three repaired counterexamples, and a
separate 30-command local install/upgrade probe passed against actual 3.5.0 and 3.6.0
package files. This remains local working-tree evidence; the tagged workflow and registries
have not run. C1 receipt-purpose gate entitlements and decision-manifest freeze changes
now each have an authored security Direction and discriminating RED suite; both need their
own human authority review before Build.

Sample state flow now supported by B1/B2:

```text
resume → quick-lane-tripwire · verify · HARD-STOP · gate receipt runs/20.md
source EXIT: - [x] C1 met; - [~] C2 original (moves-to: /milestones/dest.md#EXIT:C1)
destination EXIT: - [ ] C1 duty (accepts: /milestones/src.md#EXIT:C2)
destination freeze: exact EXIT direction digest
close source → 1/2 met, moved C2; destination duty remains authored
missing acceptance / stale freeze / cycle → refusal by source C2, no rewrite
```

The C2 release flow now implemented for a future tag is:

```text
tagged checkout → source suite + version guard
  → build wheel + sdist + npm tarball once → record byte hashes
  → cache npm runtime dependencies → install candidate files by local path
  → launcher init/update + dropped engine status + installed payload comparison
  → old local files initialize two projects → candidate update --check/update
  → user state survives and version/engine advance → local candidate report
  → upload the same candidate files → each publisher downloads and rehashes
  → npm publishes the checked .tgz; PyPI publishes byte-identical wheel/sdist
any failed candidate stage → refusal report uploaded, both publishers blocked
```

The local probe confirms the installer and upgrade path. The workflow's tagged-tree
execution, registry delivery, and external attestation remain separate evidence to collect.

### A. seal-what-you-signed

Complete the already ratified scope seal, explicit signer/lifecycle refusals, commit-tree routing,
doctor diagnostics, full regression, packaging parity, and fresh T2 re-gate. This blocks reliance
on human-frozen scope elsewhere.

### B. state-that-tells-truth

Render the latest consequential verdict beside the derived beat. Parse moved criteria explicitly,
give them stable authored IDs, keep them in the denominator, require a resolvable and accepted
destination, reject dangling and cyclic transfers, and retain original closure facts. Add
`carries:` as a separate obligation edge with an explicit destination mapping and inherited
authority. Distinguish implementation repair from a contract change without allowing Build-only
work to alter sealed surfaces.

### C. evidence-has-a-purpose

Stamp receipt purpose. Gate only on the purpose it expects. Let Explore cite support receipts
without switching to executable-gate semantics. Define externally attested holdout and release
provenance as subject-consistency records, then add build-once artifact install/upgrade smoke checks.
Missing-purpose legacy receipts remain compatible as `bound`; the legacy regression field maps to
`floor`.

### D. approval-is-a-decision-set

Derive a stable manifest containing decision IDs, kinds, text digests, sources, examples, required
authority, and proposed readings. Freeze binds its digest. Refreeze shows added, changed, removed,
stale, and unchanged decisions. No answer is inferred from omission, Git identity, persona output,
or an empty response.

The refined contract stores an immutable schema-versioned snapshot beside each node and keeps
answers out of it. `_open_decisions` remains the question compiler; the snapshot includes the
whole declared candidate, including sourced Musts and non-question declarations. `stale` remains
the current whole-interview result and is not inferred from a per-row unchanged diff. Legacy
freeze stamps have unknown coverage and gain a full baseline only on a future refreeze. This
track depends on A's scope seal and stable authored Milestone EXIT IDs.

The Direction contract and ten RED checks now exist. They cover exact canonical bytes and
content-addressed storage; complete Task S/M/R/A/E and Milestone C identities; separation of
the complete candidate from the current question subset; immutable added/changed/removed/
unchanged refreeze deltas; a separate whole-interview stale set; legacy unknown coverage versus
corrupt claimed artifacts; and per-node security interviews. Build remains held on A's scope
seal, stable authored EXIT IDs, and this Task's own human interview/freeze.

### E. learning-earns-binding

Keep evidence, cause, prevention, and human fold/reject. For escaped defects, require a resolvable
later independent validation before `fold --bind`; the filing task cannot validate itself. A
same-day calendar value is insufficient ordering evidence.

The Direction contract and six RED checks now exist. The narrow change affects escape
`fold --bind` only: an explicit distinct later Task must carry a committed descendant, fresh
bound receipt and PASS gate over the exact sealed prevention file/blob. A durable filing commit
anchors order, and one ineligible item refuses the whole match atomically. Build waits for A's
scope seal and C1's receipt-purpose authority; ordinary fold, `--reject`, and non-escape binding
retain their existing behavior.

### F. personas-prove-value

Validate schema, real commands, references, authority language, and source provenance. Build a
versioned routing set with acceptable-persona sets and no-fit cases. Run repeated neutral, routed,
and wrong-plausible-persona trials only under a fixed model/tool/budget protocol.

The implementation slice is a separate benchmark package with a strict prospective protocol,
versioned corpus, acceptable-persona sets, explicit no-fit cases, balanced seeded allocation,
fake-agent runner, oracle-first grading, and task-level reporting. Fixture tests may prove
allocation, isolation, provenance pins, caps and report honesty. They cannot prove persona value.
The first live pilot remains four tasks × three conditions × two fresh repetitions (24 trials),
and stays disabled until aggregate and per-cell spend caps are explicitly supplied.

The fixture harness is now implemented and plan-gated. It accepts canonical digest-bound,
detached protocol and corpus values; issues an exact balanced allocation with full protocol and
seed-independent campaign manifests; and requires every attempted cell to declare all reported
provenance before a fresh subprocess starts in a fresh content-and-mode-hashed workspace. The
child receives only the selected treatment and prompt digests—never acceptable/wrong/no-fit or
condition labels, oracle/rubric material, or outcomes. A prospective reservation ledger preserves
stopped cells, graders must provide every counter plus held-out or final-workspace evidence for a
pass, and summaries retain the complete task-level denominator while refusing effectiveness or
governance language. Fixture records have process-local integrity attestations and deliberately
fail closed after process restart; C2 therefore needs a separate durable live-run attestation and
adapter rather than promoting fixture records. Receipt 6 reports all 14 frozen checks, receipt 7
passes the declared floor, a fresh 97-check T2 review holds, and the full benchmark is 474 green.

### G. prove-the-loop

Keep the evaluation schema and harness outside the notary. Record exact repository, ADD, task,
prompt, persona, model-family, independence, environment, outcome, repair, cost, and provenance
fields. Add a sibling trial schema rather than extending the existing frozen RunRecord v3.
Separate deterministic mechanism fixtures, model trials, and human governance trials.

## Proof rule

Each completed mechanism updates `ADD-enhancement-proof.md` (and its local `tmp/` working copy)
with concrete checks and receipts.
Rows remain pending where authenticity or effectiveness has not been observed. Release readiness
requires full regression, twin/pin parity, built-artifact smoke, migration notes, and accurate
version/release ledgers; research need not produce a positive result before a coherent mechanism
release is ready.
