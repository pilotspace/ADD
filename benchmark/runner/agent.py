"""The injectable agent-command seam — frozen per TASK.md bench-runner §3.

`default_agent_cmd` builds the real `claude -p` argv. Tests never call it —
they inject their own argv (a fake stdlib script) via `--agent-cmd`/
`agent_cmd`, so the suite never shells out to the live `claude` CLI.
"""
from __future__ import annotations

from typing import Sequence


def default_agent_cmd(prompt: str) -> list[str]:
    """The real `claude -p` invocation, pinned by the 2026-07-07 live spike:
    `--output-format stream-json` gives the per-event transcript this runner
    parses for tokens/cost/time_to_first_edit.

    Env isolation (harness-isolate-env): `--disable-slash-commands` +
    `--strict-mcp-config` strip the operator's `~/.claude` catalog (skills,
    slash-commands, MCP servers) from the measured system prompt, so every arm
    runs in a minimal, identical environment. Both arms drive via Bash
    (`add.py` / spec-kit scripts) and need neither skills nor MCP."""
    return [
        "claude", "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--disable-slash-commands", "--strict-mcp-config",
    ]


def build_argv(prompt: str, agent_cmd: Sequence[str] | None) -> list[str]:
    """Resolve the actual argv for one attempt: an injected fake-agent argv
    gets the prompt appended as its final positional arg; absent an
    injection, fall back to the real `claude -p` argv."""
    if agent_cmd:
        return [*agent_cmd, prompt]
    return default_agent_cmd(prompt)
