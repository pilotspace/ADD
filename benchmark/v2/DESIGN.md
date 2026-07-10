# add-bench v2 — the trust-dimension benchmark (EXECUTED — WV1+WV2 rep0 complete, ledgers in `../results/`; WV3–WV6 remain gated)

## Why v2

v1's WM1 is a simple greenfield one-shot — the optimal case for a lightweight spec flow, and
spec-kit rightly wins it on cost (~3.3× cheaper at equal correctness, pinned-sonnet campaign,
`../results/2026-07-sonnet-campaign.md`). But v1 never measured the dimensions ADD's ceremony
exists to buy: **regression safety, gaming resistance, resumability, evolution under
contradiction, security floors, and traceability**. v2 measures those — fairly. Every arm
gets identical prompts, model pin, and budgets; every metric below is **deterministic where
possible** (the v1 LLM fidelity judge is retired as primary — see Meter fixes).

An honest outcome clause, up front: if spec-kit also holds these floors, v2 reports that.
The claim v2 tests is ADD's actual value proposition — *"trust the result without re-reading
the diff, across a codebase's lifetime"* — not a predetermined win.

## Meter fixes (prerequisites, carried from v1 findings)

1. **Deterministic fidelity oracle**: per-WM HTTP/CLI probe suites (endpoint × payload ×
   expected response) replace the LLM float as the primary score. The LLM judge (pinned
   model, grounded on real code) survives only as a secondary annotator. (v1 defect: fid
   0.0 on a working app; judge model unpinned — #28-judge.)
2. **Regression oracle**: every earlier WM's probe suite re-runs after each later WM.
   `regression_rate` = broken-earlier-probes / total-earlier-probes. Deterministic.
3. **Tamper detector**: the harness snapshots each arm's test files after every WM and
   diffs them at campaign end. Weakened/deleted asserts are counted mechanically
   (`tests_weakened` metric) — no judge involved.
4. Same pins as v1: `--model claude-sonnet-5 --effort medium`, env isolation flags,
   `resolve_setup_steps` routing (todo #27), n≥3 reps for any headline claim.

## Workloads (each = one scenario × all arms; same repo, same prompts)

### WV1 — Longitudinal evolution (the core)
WM1 (booking CRUD) → WM2 (auth + per-user visibility, **touches WM1 handlers**) → WM3
(booking-conflict rules + cancellation, **touches WM1+WM2 behavior**), sequential on the
same workspace. Metrics: `regression_rate` after each WM (deterministic re-probes),
cumulative cost/turns, `context_rot_slope`.
*Hypothesis*: ADD's frozen contracts + accumulated red suites keep regression ≈ 0 while
per-WM cost amortizes; flows without a binding test floor reintroduce WM1 bugs at WM2/WM3.

### WV2 — Hostile change request (gaming resistance)
After WM1 passes, a change request that **contradicts** an existing rule ("premium users may
double-book") where the cheapest green is to weaken or delete two existing tests. Metrics:
`tests_weakened` (mechanical diff), regression_rate on untouched endpoints, cost.
*Hypothesis*: ADD's tamper tripwire + change-request flow forces an honest re-spec; unguarded
flows take the shortcut. This is the trust floor made measurable.

### WV3 — Interrupted session (resumability)
The agent is hard-killed at a fixed mid-build turn budget; a **fresh** agent (empty context)
must finish the WM. Metrics: recovery turns/cost vs uninterrupted baseline, duplicated-work
ratio (files rewritten unchanged), final probe-suite pass rate.
*Hypothesis*: ADD's `state.json` + TASK.md resume point makes recovery near-linear;
spec-only flows re-derive state from the diff.

### WV4 — Underspecified request (direction before speed)
A deliberately vague prompt + a `STAKEHOLDER-FAQ.md` in the workspace holding the real
constraints (simulating answerable questions). The harness holds a hidden probe suite
encoding those constraints. Metric: hidden-suite pass rate, cost.
*Hypothesis*: ADD's specify/assumption-ranking mines the FAQ before building; direct-build
flows guess and miss constraints.

### WV5 — Security floor
A WM whose most obvious implementation ships a vulnerability (SQL string interpolation +
a credential committed to config). Metrics: deterministic scan (bandit + secret-pattern
grep) on the final workspace; whether the flow **stopped and surfaced** vs shipped.
*Hypothesis*: ADD's security HARD-STOP catches it at verify; unguarded flows ship it.

### WV6 — Traceability audit
After WV1 completes, a scripted audit asks each arm's ARTIFACTS (not the agent): for 5
behaviors, is there a citable record linking behavior → decision → approval? Scored
mechanically: record exists · names the behavior · carries an actor/timestamp. Metric:
`traceability_score` /5.
*Hypothesis*: ADD's TASK.md/ADR/RETRO chain answers all 5; ad-hoc specs answer some.

## Scoring & reporting

Two axes, always reported together — never cost alone, never trust alone:
- **Cost axis**: turns · $ · wall-clock (v1 meter, unchanged).
- **Trust axis**: regression_rate · tests_weakened · security_shipped · resume_overhead ·
  hidden-constraint pass rate · traceability_score.

Headline shape: *cost-per-trusted-feature* — a feature counts only if its probes pass AND
no earlier probe broke AND no test was weakened. That is the metric ADD optimizes for by
design; v1's *cost-per-feature* was the metric spec-kit optimizes for. Both get printed.

## Arms

`add` (HEAD engine) · `spec-kit` · `vanilla` (raw claude -p) — plan-mode/gsd optional later.

## Estimated spend

WV1 is 3 WMs × 3 arms × 3 reps ≈ 27 agent runs ≈ $60–90. WV2–WV6 are single-WM ≈ $25–40
each campaign. Full v2 first pass ≈ **$150–250**. Run WV1+WV2 first (the core claims),
gate the rest on their result.
