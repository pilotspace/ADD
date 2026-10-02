# Prompt audit — the ADD 4.0 skill, for Claude Sonnet 5.5 at low effort (2026-10-02)

**Scope.** What ADD 4.0 puts in front of the model: `add-method/skill/add/SKILL.md` and its four
references (`format.md`, `evidence.md`, `explore.md`, `personas.md`), plus the `CLAUDE.md` block the
installer writes. The `.claude/skills/add/` and `_bundled/skill/add/` copies are byte-identical to
it. The benchmark harness counts too, because its prompts reach the measured model
(`benchmark/runner/core.py` wrappers, `runner/agent.py` argv). Not audited: `persona-author/`, the
vendored teacher corpus, and the operator's `~/.claude/`, which is outside the project and only
flagged below.

**Target.** `claude-sonnet-5-5` in Claude Code at `--effort low`. That is the configuration this
round benchmarks against raw Claude Code at `medium`.

## Summary

The skill is in good shape for Sonnet 5.5. There are no shouting markers, no "think step by step",
no scaffolds that an API feature replaced, and no prohibition lists without reasons. Its "never"
rules are the method's real constraints: the seal, not weakening checks, and HARD-STOP. Those stay.

The findings that matter:

1. **A path that doesn't resolve** (high). The skill sends the model to `personas-index/use-when.md`,
   but the installer puts that file at `.add/personas-index/use-when.md`. The file is 65 KB, so
   reading it whole also costs a lot.
2. **Numeric turn choreography** (medium). "Direction = three turns · Verify = two turns" is a fixed
   cadence written against Sonnet 5, which spread a beat over about 23 messages. On Sonnet 5.5 a
   Direction already takes 3–5 messages (round 6), and lower effort means fewer, more consolidated
   tool calls. The counts no longer buy anything. The substance around them does, so it stays and
   only the counts go.
3. **The bench measured a disciplined operator, not raw Claude Code** (flag). Every measured session
   loads `~/.claude/CLAUDE.md`, which says "interview me … until 95% confidence" and "use
   mcp__serena". Both conflict with a headless `-p` run, and both apply to every arm.

Counts: Group 1 (dated text) 1 · Group 2 (brittle config) 2 + 2 flags · Group 3 (tool descriptions)
not applicable · Group 4 (request config) 1 fixed + 1 flag.

## Findings

| # | Location | Evidence | Pattern | Why obsolete | Conf. | Action |
|---|---|---|---|---|---|---|
| 1 | `SKILL.md:184` | ``None in the project → `personas-index/use-when.md` `` | G2 volatile specifics | The installer writes `.add/personas-index/use-when.md` (`_installer.py:243`). The relative path doesn't resolve from the project root. | High | rewrite (hunk 2) |
| 2 | `references/personas.md:46` | `` `personas-index/use-when.md` in the teacher corpus `` | G2 volatile specifics | Same path as #1. | High | rewrite (hunk 3) |
| 3 | `SKILL.md:35-46` | "Direction = three turns … Verify = two turns." | G1f output choreography / G1c over-specification | Fixed counts tuned against Sonnet 5's 23-message Directions. Sonnet 5.5 packs a beat into 3–5 messages without them (r6), and low effort consolidates further. Round 5 showed the batching prose did not change Sonnet 5's behaviour either (wm1 ~23 messages). Keep the content (stubs, the one-command seal), drop the counts. | Medium | rewrite (hunk 1) |
| 4 | `SKILL.md:40` | "stubs that raise `NotImplementedError`" | G1c, wrong degree of freedom | Stubbing every module up front makes Build rewrite them. Round 6's lean edit "stub only what the checks import" cut Build from 2.75 to 1.3 min with no quality loss (n=3). | Medium | rewrite (in hunk 1) |
| 5 | `SKILL.md:182-185` | the lead is chosen "best fit on beat and `risks:`" with no way to find candidates | G2, add a mechanism | With no lookup named, the model either skips personas or reads the 65 KB index. A `covers-risks` grep is the cheap, exact lookup (r6 lean edit). | Medium | rewrite (hunk 2) |
| 6 | `runner/agent.py:51` | `"--effort", "medium"` hard-coded for every arm | G4 request config | This made the effort question unaskable and unrecorded. | High | **fixed** in `fae22f71` (per-arm `effort`, stamped into `artifacts.effort`) |
| 7 | `SKILL.md:58`, `CLAUDE.md` block | "When in doubt, size up." | G1a "if in doubt, default to X" | Matches the over-triggering idiom, but it is a ratified routing policy that the floor depends on. Keep-list 5. | Low | flag |
| 8 | `SKILL.md:109-111` | "the body itself (not JSON, `null`, a number, a list)" | G2 recency trap / patch accretion | Added after round 5's wm1 oracle, and HTTP-JSON-specific in a general skill. It did transfer on Sonnet 5 (4/6 → 0/6), but on Sonnet 5.5 every arm, vanilla included, scored 19/19 on edges. Re-test before cutting. | Low | flag |
| 9 | `~/.claude/CLAUDE.md` (operator, out of scope) | "interview me … until … 95% confidence", "Use the `mcp__serena` tools" | G2 conflicting instruction files | Loaded into every `claude -p` session. In a headless run it pushes toward halting to ask, which matches vanilla's amb1 halts in round 5 (2 of 7). It applies to all arms equally. | Medium | flag — user-level, so no edit; a clean `HOME` or `--setting-sources` for bench runs |
| 10 | `runner/core.py:82-111` | "read … FIRST", "NEVER end the run…", "SEALED" | G1a pressure language | Capitalised emphasis, but the wrapper's length and wording are pinned for fairness against `add-loop` (`test_arms_4v3.py`). Editing it would break comparability with rounds 4–6. | Low | flag |

Kept on purpose (keep list): the `<constraints>` recap (item 10, deliberate recap), the "never"
rules on seals and checks (items 3 and 5), the trigger-tuned `description:` (item 6, eval-tuned
12/12 · 8/8), the twelve-invariants table and the evidence-mode tables (reference data, loaded on
demand), and explore's numeric BUDGET (a real constraint, not output shaping).

## Proposed diff

Each hunk applies to all three skill trees (`add-method/skill/add/`, `.claude/skills/add/`,
`add-method/src/add_method/_bundled/skill/add/`). The benchmarked form is
`benchmark/arms/variants/add-4-audited/SKILL.md`.

```diff
--- a/add-method/skill/add/SKILL.md   (hunk 1 — findings 3, 4)
+++ b/add-method/skill/add/SKILL.md
-## Turns — the real cost
-
-Every turn re-reads the whole context: cost grows with turns, not words. Keep every step; cut round-trips:
-- **Direction = three turns.** (1) One command reads what the task touches and finds how the tests run,
-  installing what is missing in that same command. (2) The task file, its tests, and stubs that raise
-  `NotImplementedError` (the first run fails on behavior, not imports), all as parallel writes in one
-  message. (3) one command runs the checks and seals: `<check> ; git add .add/tasks/<slug>.md <tests>
-  && git commit -qm "freeze(<slug>): <goal>"`. Green, or red on an import error: fix it, `refreeze`.
-- **Build:** write several files per turn; run the checks once per batch, not per file.
-- **Verify = two turns.** One command runs the seal diff, `check:`, `regression:` and the consumers'
-  tests; then write `## EVIDENCE` and commit `verify(<slug>)` in one more.
-- **Subagents:** at most one per beat, in the foreground — never pause the session to wait for one.
+## Batch the work
+
+Each round-trip re-reads the whole context, so put independent reads and writes in one message:
+- **Direction:** one command reads what the task touches and finds how the tests run, installing what
+  is missing. Then the task file and its tests — stub only what the checks import (usually one module),
+  raising `NotImplementedError` so the first run fails on behavior, not imports — as parallel writes.
+  Then one command runs the checks and seals: `<check> ; git add .add/tasks/<slug>.md <tests>
+  && git commit -qm "freeze(<slug>): <goal>"`. Green, or red on an import error: fix it, `refreeze`.
+- **Build:** write several files per message; run the checks once per batch, not per file.
+- **Verify:** one command runs the seal diff, `check:`, `regression:` and the consumers' tests; then
+  write `## EVIDENCE` and commit `verify(<slug>)`.
+- **Subagents:** at most one per beat, in the foreground.
```

```diff
--- a/add-method/skill/add/SKILL.md   (hunk 2 — findings 1, 5)
+++ b/add-method/skill/add/SKILL.md
-one more only for a risk the lead leaves bare. None in the project → `personas-index/use-when.md`;
-none fits → proceed. The second reader and the refuter load the lead's `counter-lens:`. A persona
+one more only for a risk the lead leaves bare. Find candidates with
+`grep -H '^covers-risks' .add/personas/*.md`; none there → grep `.add/personas-index/use-when.md`
+for the risk (never read it whole); none fits → proceed. The second reader and the refuter load the lead's `counter-lens:`. A persona
```

```diff
--- a/add-method/skill/add/references/personas.md   (hunk 3 — finding 2)
+++ b/add-method/skill/add/references/personas.md
-2. **Candidates** — `.add/personas/` first (project scars beat generic knowledge); nothing there →
-   `personas-index/use-when.md` in the teacher corpus, read the matching source as a lens; nothing
+2. **Candidates** — `.add/personas/` first (project scars beat generic knowledge); nothing there →
+   `.add/personas-index/use-when.md` in the teacher corpus, read the matching source as a lens; nothing
```

```diff
--- a/add-method/tests/test_skill_only.py   (hunk 4 — the test pins hunk 1's old wording)
+++ b/add-method/tests/test_skill_only.py
-    turns = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split("## Turns", 1)[1]
+    turns = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split("## Batch the work", 1)[1]
                      .split("\n## ", 1)[0].split())
-    for phrase in ("finds how the tests run", "installing what is missing in that same command",
-                   "as parallel writes in one message"):
+    for phrase in ("finds how the tests run", "installing what", "stub only what the checks import",
+                   "as parallel writes"):
```

Removal check: `test_direction_is_a_batched_plan` (`add-method/tests/test_skill_only.py:104`) is the
only other place that pins the old Turns wording, and hunk 4 updates it. Grep the skill trees,
the installer, and `add-method/tests` again before applying the diff.

The measured effect of these hunks is in `PILOT-4v3-2026-10-02-r7.md`.
