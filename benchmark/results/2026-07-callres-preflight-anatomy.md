# call-residuals — pre-measure anatomy of the real WM1 runs — 2026-07-14

Purpose: before spending on the paid WM1 re-measure, anatomize the **actual**
`sixphase-r{1,2,3}/wm1` transcripts (the only call-instrumented real ADD runs)
to find *all* reducible call/turn/cost waste — not just the four levers the
six-phase report named. Method: parse `transcript.jsonl`, split every `add.py`
invocation into `--help` flag-discovery probes vs real calls, and reconstruct
the ordered command timeline with the agent's stated intent to root-cause each
re-read.

## Headline: two of the four milestone tasks target levers that never fired

| six-phase claim | reality in the 3 transcripts | task built | effect on calls |
|---|---|---|---|
| "double init ×2/rep" | **true double-init = 0** (real `init` ran exactly once each rep; the "×2" was `init --help` + real `init`, miscounted) | init-idempotent-nudge | **~0** (target never fires) |
| "the --help habit (typo)" | **invalid-choice / unknown-command = 0** (agent never mistyped a command) | help-habit-kill | **~0** (target never fires) |

Both fixes are defensively correct and harmless, but they cannot move the call
count because their failure modes do not occur in the runs.

## The real call split (per rep)

| | r1 | r2 | r3 | mean |
|---|---|---|---|---|
| `--help` flag-discovery probes | 6 | 4 | 5 | **5.0** |
| real calls | 13 | 18 | 16 | 15.7 |
| **total (the "20.7" headline)** | 19 | 22 | 21 | **20.7** |

The probes are deliberate flag discovery *before first use* of a correctly-typed
command: `add.py --help`, `init --help`, `new-task --help`, `freeze --help`,
`advance --help`, `lock --help`, `re-cross --help`. **No current task touches
this** — help-habit-kill only intercepts the typo/unknown-command case.

## Ranked reducible waste (by real-run impact)

| # | Lever | per rep | current task? | fix layer |
|---|---|---|---|---|
| **A** | **Startup root-walk confusion** — fresh workspace nested under an ancestor `.add/`; first `status` resolves the *parent* project; agent greps `find_root`/`STATE_FILE`/`_root` to understand why before `init` | **7–13 cmds** | ❌ none | **HARNESS** (isolate workspace from ancestor `.add/`) + optional status warn |
| **B** | **`--help` flag-discovery** before first use | **5.0 calls** | ❌ none | `status`/`advance` emit the *paste-ready next command with flags* |
| **C** | **Engine-mechanics spelunking** — grep/read of `_declared_scope`/`scope_violation`/`_in_scope`/`_SKIPPABLE_PHASES` to decode scope + skip behavior | 5–11 cmds | partial (scope-first-draft) | self-explaining `scope_violation` + skip messages |
| **D** | **status re-reads** — initial (caused by A) + final-ceremony reducible; middle two legit | ~2 reducible | status-orientation-diet ✓ | A fixes initial; drop final-ceremony |
| **E** | **guide re-reads** | 1–2 | ❌ | fold the guide hint into `advance` output |
| **F** | **advance multi-call** — `advance --fill` + `advance --help` + `advance` = 3 calls for 1 crossing (r2) | ~1 | subset of B | B covers it |

## The measurement is partly contaminating the metric (First-Principles)

Lever **A is 100% harness-induced**: the runner places the workspace at
`benchmark/runs/<arm>/wm<N>/workspace` — *inside* AIDD-Book, which has a `.add/`
at its root. `add.py`'s root-walk therefore finds the ancestor project. A real
greenfield user runs in a standalone dir and never triggers it. So the measured
**20.7 calls / 131 turns / $3.17 are inflated by the harness nesting** (mostly
turns/cost; ~1–2 add.py calls). Paying to re-measure without fixing this would
partly measure the apparatus, not the method.

- **Harness fix (highest leverage, zero method change):** run the workspace
  outside any ancestor `.add/` tree (tmpdir, or a root boundary so the walk stops
  at the workspace). Removes A entirely, makes every future re-measure honest,
  and cuts turns/cost/context-rot.
- **Method fix (complementary):** `status` warns when it resolved an *ancestor*
  project ("no `.add/` here; using project at <path> — run `init` to scope
  here"). Helps real nested cases (monorepos, subdir projects) but is secondary
  to the harness fix for benchmark honesty.

## What actually moves ≤12 calls

Irreducible 1-task lifecycle floor ≈ `init` + `new-task` + ~5 `advance` +
`freeze` + `gate` ≈ **~10 real calls**. On top of that:

- **B (kill `--help` flag discovery): −4 calls** → the single biggest call lever, currently unaddressed.
- **D (status-diet, final-ceremony): −1**
- **E (guide-fold): −1**
- **C/scope-first-draft (re-cross): −1**

Projected: 20.7 → ~12.7 with **B + D + E + scope all working**. ≤12 is reachable
but tight, and **B is required** — the merged milestone (B absent, A/help-typo
phantom) would land ~15–16.

## Recommendation

1. **Fix the harness first** (isolate the workspace) → honest baseline, cheaper reruns.
2. **Add lever B** (paste-ready next-command-with-flags) — the one call lever that makes ≤12 achievable.
3. Optionally fold E (guide) and self-explain C (scope_violation) — cheap, message-layer.
4. *Then* run the paid 3-rep re-measure against a milestone that can actually hit the bar, in a harness that measures the method rather than the nesting.

Evidence: `benchmark/runs/sixphase-r{1,2,3}/wm1/transcript.jsonl` (335/… lines
each); anatomy reproducible from the parse in this session.
