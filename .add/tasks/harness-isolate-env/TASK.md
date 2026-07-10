# TASK: Benchmark claude -p runs isolated from the operator's skill/command/MCP catalog (identical minimal env per arm)

slug: harness-isolate-env · created: 2026-07-09 · stage: mvp
milestone: three-phase-flow
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `benchmark/runner/agent.py:default_agent_cmd` — builds the real `claude -p` argv every arm runs under; today `["claude","-p",prompt,"--output-format","stream-json","--verbose"]` inherits the operator's `~/.claude` (148 skills, 174 slash-commands, 3 MCP servers) into every session's system prompt = the ~40K identical-but-noisy startup payload + inconsistent cache warmth documented in THREE-PHASE-FLOW-PROOF.md. · `benchmark/tests/test_runner_core.py` — imports from `benchmark.runner` (test home).
Context (working folder): `benchmark/THREE-PHASE-FLOW-PROOF.md` (harness problem #2, env pollution). Both arms drive via `Bash` (`add.py` / spec-kit scripts) — NEITHER needs skills or MCP; the ADD arm uses the `add.py` CLI, not the `add` Claude-Code skill.
Honors (patterns / conventions): `default_agent_cmd` is the injectable seam — tests inject their own `agent_cmd`, so a flag change touches only real runs (never the suite). `claude` flags confirmed accepted: `--disable-slash-commands` (disable all skills/commands) + `--strict-mcp-config` (no MCP unless --mcp-config given).
Anchors the contract cites: `default_agent_cmd` returned argv.
Ground SHA: efc100b

---

## 1 · SPECIFY — the rules

Feature: every benchmark `claude -p` runs in a minimal, IDENTICAL environment — no operator skills/commands/MCP leak into the measured system prompt.
Must:
  - `default_agent_cmd(prompt)` includes `--disable-slash-commands` (strips the 148-skill/174-command catalog).
  - `default_agent_cmd(prompt)` includes `--strict-mcp-config` (no MCP servers loaded absent an explicit --mcp-config).
  - the existing argv is PRESERVED: `claude -p <prompt> --output-format stream-json --verbose` (the transcript-parsing contract) with `prompt` still present.
Reject:
  - the isolation flags are applied per-invocation to the real argv only -> the injectable `agent_cmd` seam is untouched (tests still inject freely; no flag forced onto injected argv).
Accept: `default_agent_cmd("P")` returns a list containing `"claude"`, `"-p"`, `"P"`, `"--output-format"`, `"stream-json"`, `"--disable-slash-commands"`, and `"--strict-mcp-config"`.
Assumptions: ⚠ that neither arm needs a skill or MCP server at runtime — both drive via Bash (add.py CLI / spec-kit bash scripts), verified in the wrapper + spec-kit setup; if wrong (an arm silently relied on an ambient skill/MCP), that run would fail loudly at setup/build, not silently mis-measure — so low-risk and fail-safe.   (or "none material — biggest risk: X")

---

## 3 · CONTRACT — freeze the shape

```
default_agent_cmd(prompt: str) -> list[str]   (benchmark/runner/agent.py)
returns, in order:
  ["claude", "-p", prompt,
   "--output-format", "stream-json", "--verbose",
   "--disable-slash-commands", "--strict-mcp-config"]
- prompt stays the 3rd element (positional); stream-json contract preserved.
- flags added to the REAL argv only; build_argv's injected-agent_cmd path
  (opts.agent_cmd) is unchanged — tests never get the flags forced on them.

New test (RED first): test_default_agent_cmd_isolates_env — asserts both
isolation flags AND the preserved argv tokens are present.
```

`Least-sure flag surfaced at freeze:` [contract] flag ORDER — placing the isolation flags after --verbose; harmless (claude parses flags order-independently, confirmed accepted), asserted by membership not index, so order drift can't break the test.
Status: FROZEN @ v1 — approved by Tin Dang

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §0 GROUND anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 CONTRACT shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: `test_default_agent_cmd_isolates_env` (test_runner_core.py) — asserts both isolation flags + preserved argv tokens. RED confirmed (flags absent).
Tests live in: `benchmark/tests/test_runner_core.py` · ran RED before build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/runner/agent.py` `benchmark/tests/test_runner_core.py`
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: as planned — appended `--disable-slash-commands` + `--strict-mcp-config` to default_agent_cmd's returned list; build_argv injected path untouched.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass (127/127 benchmark suite) · coverage held · no test or contract altered during build
- [x] green was EARNED — test ran RED (flags absent) before the agent.py edit; asserts membership of observable argv tokens
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — two static CLI flags; no IO/network/eval; injected-agent_cmd seam untouched

Build expectations (from §1 Accept + §3 CONTRACT): `default_agent_cmd` returns the two isolation flags + the preserved stream-json argv — confirmed by `test_default_agent_cmd_isolates_env` GREEN + full benchmark suite green (build_argv injected path unchanged).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gated on complete evidence — mechanical CLI-flag change, autonomy auto) · date: 2026-07-09

