"""The injectable agent-command seam — frozen per TASK.md bench-runner §3.

`default_agent_cmd` builds the real `claude -p` argv. Tests never call it —
they inject their own argv (a fake stdlib script) via `--agent-cmd`/
`agent_cmd`, so the suite never shells out to the live `claude` CLI.
"""
from __future__ import annotations

from typing import Sequence

# the single source of truth for the pinned meter model — stamped into every
# record's artifacts (wv2-family M7) and asserted by the model-pin tests
PINNED_MODEL = "claude-sonnet-5"


def default_agent_cmd(prompt: str) -> list[str]:
    """The real `claude -p` invocation, pinned by the 2026-07-07 live spike:
    `--output-format stream-json` gives the per-event transcript this runner
    parses for tokens/cost/time_to_first_edit.

    Env isolation (harness-isolate-env): `--disable-slash-commands` +
    `--strict-mcp-config` strip the operator's `~/.claude` catalog (skills,
    slash-commands, MCP servers) from the measured system prompt, so every arm
    runs in a minimal, identical environment. Both arms drive via Bash
    (`add.py` / spec-kit scripts) and need neither skills nor MCP.

    Permission grant (harness-permission-grant): `--dangerously-skip-permissions`
    is MANDATORY — headless runs get no permission prompt, and ambient operator
    config is nondeterministic. Live proof 2026-07-10 (WV1 rep0): spec-kit and
    vanilla had every workspace mkdir/Write denied and scored artifact 0.00s,
    while the add arms happened to dodge the checks — a fairness break, not a
    result. The workspace is a fresh throwaway dir; blanket grant is safe there.

    Model pin (harness-model-pin #28): `--model claude-sonnet-5 --effort medium`
    is MANDATORY. Without it `claude -p` inherits whatever ambient model the
    operator's session defaults to at run time — live proof 2026-07-09 caught the
    same add WM1 running on opus-4-8 (single, $5.62) vs fable-5 (multi-rep,
    $8.71-11.02), same work at ~2x cost, invalidating every cross-run cost/turn
    comparison. Sonnet+medium is the fixed, model-comparable meter for all arms."""
    return [
        "claude", "-p", prompt,
        "--model", PINNED_MODEL, "--effort", "medium",
        "--output-format", "stream-json", "--verbose",
        "--disable-slash-commands", "--strict-mcp-config",
        "--dangerously-skip-permissions",
    ]


def build_argv(prompt: str, agent_cmd: Sequence[str] | None) -> list[str]:
    """Resolve the actual argv for one attempt: an injected fake-agent argv
    gets the prompt appended as its final positional arg; absent an
    injection, fall back to the real `claude -p` argv."""
    if agent_cmd:
        return [*agent_cmd, prompt]
    return default_agent_cmd(prompt)
