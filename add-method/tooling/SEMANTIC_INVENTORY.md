# SEMANTIC_INVENTORY — v17 prompt-clarity   (FROZEN @ v1 · 2026-06-06)

The single source for the v17 semantic-preservation gate. `semantic_inventory.py` reads its
units FROM this file (no hardcoded duplicate) and diffs them against the agent-facing surface
(skill/add 18 files + docs/appendix-b-prompts.md). It is the MEANING-side twin of `wording_lint.py`
(which is lexical): a rewrite changes PHRASING, never the RULE — this gate proves no semantic unit
was dropped, renamed, relocated, or quietly excepted.

**NECESSARY, not SUFFICIENT.** The gate proves preservation is necessary-true: nothing dropped /
renamed / relocated (S1), every safety invariant's anchors still co-occur in a tight list-item
window (S2), no listed exception introduced (S3). It does NOT prove meaning is fully intact: an
INVERSION around surviving anchors (an added "unless…" / negation / scope-narrowing that keeps every
anchor word) is model-judgment and is CEDED — see `## cede_list`. Honoring that boundary is why a
verbatim-text diff (`verbatim_diff`) and a model-judged "same meaning?" check (`model_judged_gate`)
are refused by design: each mis-gates a good reword. Three deterministic checks, all GREEN at freeze:

  S1  every frozen token still present IN ITS FILE          (a dropped / renamed / relocated unit)
  S2  every invariant's anchors still co-occur in its window (a dropped conjunct / a removed "always")
  S3  no invariant's negative-anchor sits in its window      (an added exception — opportunistic catch)

Window: S1 = per-file. S2/S3 = ANCHOR-LOCAL — a markdown list-item is its own unit, else the
blank-line paragraph. Tighter than a paragraph by necessity: run.md's auto-gate bullets are
contiguous, and bullet 3 legitimately lists `RISK-ACCEPTED` next to the security rule in bullet 2 —
a paragraph window would false-positive at freeze. The list-item window keeps them apart.

## token_layer

Per-file stable identifiers that must survive a rewrite UNCHANGED (S1 asserts each present in its
file). gate_outcomes are a fixed vocab; named_codes are backticked snake_case reject/error codes
(rule-extractable via `--extract`, so the list is reproducible, never hand-typed-and-forgotten).

- SKILL.md: PASS, RISK-ACCEPTED, HARD-STOP, auto-resolved
- run.md: PASS, RISK-ACCEPTED, HARD-STOP, auto-resolved, unguarded_high_risk_auto
- streams.md: PASS, RISK-ACCEPTED, HARD-STOP, ESCALATE, auto-resolved, unguarded_high_risk_auto, active_task
- gate-udd.md: PASS
- phases/6-verify.md: PASS, RISK-ACCEPTED, HARD-STOP, auto-resolved, unescalated_security_note
- adopt.md: already_locked
- phases/0-setup.md: already_locked, setup_unlocked
- deltas.md: no_evidence, not_found, unknown_competency, unknown_status
- fold.md: no_open_deltas, unconfirmed_fold, unroutable_delta
- intake.md: ask_human, frozen_scope, split_required
- scope.md: dangling_criterion, no_milestone, not_classified, split_required

## invariants

Each safety proposition the token layer can't guard, as `<id> @ <file> | anchors: … | neg: …`.
anchors[0] is the PRIMARY (locates the window); the rest must co-occur within it (S2). Each neg is
forbidden inside that window (S3). Seeded from task-1's FROZEN negative_keep_list + the gate
outcomes; all 7 verified green at freeze (window line-counts noted).

- security-always-hardstop @ run.md | anchors: security, HARD-STOP, always | neg: unless, except, waive, RISK-ACCEPTED
- never-auto-pass-security @ run.md | anchors: auto-pass, security, never | neg: unless, except
- never-weaken-test @ SKILL.md | anchors: weaken, never, test | neg: unless, except
- never-self-fold @ fold.md | anchors: self-approve, never | neg:
- never-prompt-field @ phases/1-specify.md | anchors: Never: | neg:
- auto-pass-conjunction @ run.md | anchors: Auto-PASS, test, coverage, weaken, contract | neg:
- unguarded-high-risk @ run.md | anchors: risk: high, conservative, refus | neg:

## coverage

Every negative on task-1's frozen negative_keep_list (WORDING_RUBRIC.md) maps to ≥1 invariant
(`<distinctive-substring-of-the-negative> -> <invariant-id>`). The freeze-time `invariant_uncovered`
check asserts each frozen negative contains some key here whose invariant exists — so a safety
negative can never ship un-anchored.

- Never: -> never-prompt-field
- weaken a test -> never-weaken-test
- security finding is always -> security-always-hardstop
- never auto-pass -> never-auto-pass-security
- self-approve -> never-self-fold

## cede_list

NAMED, never hidden — the gate does NOT prove these; human review + the INDICATIVE behavioral eval
do. Listing them is required: an inventory that claims preservation without naming its cede is the
`overclaim_sufficient` reject.

- inversion around surviving anchors — an added exception / negation / scope-narrowing that keeps every anchor word
- positivity / scope judgment — whether a negative was rightly positivized, whether a scope qualifier is correct
- meaning beyond the anchors — any drift the anchor/neg-anchor sets do not pin
