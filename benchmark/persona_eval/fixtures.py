"""Deterministic, no-network mechanism fixtures used by the scoped suite."""
from __future__ import annotations

import sys
from typing import Any

from ._common import sha256_text
from .allocation import TrialCell, allocate
from .corpus import Corpus, validate_corpus
from .protocol import Protocol, validate_protocol
from .runner import EMPTY_WORKSPACE_DIGEST, run_cell


def example_corpus() -> Corpus:
    return validate_corpus(
        {
            "schema": "add.persona-eval-corpus/1",
            "version": "persona-corpus/1",
            "cases": [
                {
                    "id": "fit-1",
                    "prompt_digest": sha256_text("case-fit-prompt"),
                    "workspace_digest": EMPTY_WORKSPACE_DIGEST,
                    "oracle_digest": sha256_text("case-fit-oracle"),
                    "rubric_digest": sha256_text("case-fit-rubric"),
                    "acceptable_personas": ["security-reviewer", "engine-reviewer"],
                    "plausible_wrong_persona": "method-steward",
                    "no_fit": False,
                    "agent_visible_paths": ["PROMPT.md", "workspace/"],
                },
                {
                    "id": "none-1",
                    "prompt_digest": sha256_text("case-none-prompt"),
                    "workspace_digest": EMPTY_WORKSPACE_DIGEST,
                    "oracle_digest": sha256_text("case-none-oracle"),
                    "rubric_digest": sha256_text("case-none-rubric"),
                    "acceptable_personas": [],
                    "plausible_wrong_persona": "method-steward",
                    "no_fit": True,
                    "agent_visible_paths": ["PROMPT.md", "workspace/"],
                },
            ],
        }
    )


def example_protocol(
    seed: int = 7391,
    *,
    repetitions: int = 2,
    live_enabled: bool = False,
    cost_ceiling: float = 1.0,
) -> Protocol:
    corpus = example_corpus()
    return validate_protocol(
        {
            "schema": "add.persona-eval-protocol/1",
            "campaign_id": "fixture-campaign",
            "repository_revision": "git:fixture-repository",
            "add_version": "3.6.0",
            "add_revision": "git:fixture-add",
            "corpus_version": corpus.version,
            "corpus_digest": corpus.digest,
            "model_id": "fixture-model",
            "model_family": "fixture-family",
            "effort": "medium",
            "runner_digest": sha256_text("fixture-runner"),
            "environment_digest": sha256_text("fixture-environment"),
            "tool_allowlist": ["shell"],
            "prompt_template_digest": sha256_text("fixture-prompt-template"),
            "token_ceiling": 1000,
            "turn_ceiling": 8,
            "wall_time_ceiling_seconds": 30,
            "per_cell_cost_ceiling_usd": cost_ceiling,
            "aggregate_cost_cap_usd": max(cost_ceiling, cost_ceiling * 24),
            "repetitions": repetitions,
            "allocation_seed": seed,
            "live_enabled": live_enabled,
            "stop_policy": "before_next_cell",
        }
    )


def example_cells(*, seed: int = 7391) -> tuple[TrialCell, ...]:
    corpus = example_corpus()
    return allocate(example_protocol(seed=seed), corpus)


def example_cell(
    *,
    condition: str = "routed_correct",
    cost_ceiling: float = 1.0,
) -> TrialCell:
    corpus = example_corpus()
    cells = allocate(example_protocol(cost_ceiling=cost_ceiling), corpus)
    for cell in cells:
        if cell.task_id == "fit-1" and cell.repetition == 1 and cell.condition == condition:
            return cell
    raise ValueError(f"unknown example condition: {condition}")


def example_observed_provenance(cell: TrialCell) -> dict[str, Any]:
    """Return complete observed pins for deterministic live-runner probes."""

    return {
        "actual_repository_revision": cell.repository_revision,
        "actual_add_version": cell.add_version,
        "actual_add_revision": cell.add_revision,
        "actual_corpus_digest": cell.corpus_digest,
        "actual_model_id": cell.model_id,
        "actual_model_family": cell.model_family,
        "actual_effort": cell.effort,
        "actual_runner_digest": cell.runner_digest,
        "actual_environment_digest": cell.environment_digest,
        "actual_tool_allowlist": cell.tool_allowlist,
        "actual_prompt_template_digest": cell.prompt_template_digest,
        "actual_case_prompt_digest": cell.case_prompt_digest,
        "actual_effective_prompt_digest": cell.effective_prompt_digest,
        "actual_workspace_digest": cell.workspace_digest,
        "actual_oracle_digest": cell.oracle_digest,
        "actual_rubric_digest": cell.rubric_digest,
        "actual_grader_digest": cell.rubric_digest,
        "actual_persona_id": cell.persona_id,
        "actual_persona_digest": cell.persona_digest,
        "actual_pin_manifest_digest": cell.pin_manifest_digest,
    }


def example_campaign(
    *,
    missing_one: bool = False,
    timeout_one: bool = False,
    runner_kind: str = "fixture",
) -> tuple[Protocol, Corpus, tuple[TrialCell, ...], list[dict[str, Any]]]:
    corpus = example_corpus()
    protocol = example_protocol(live_enabled=runner_kind == "live")
    cells = allocate(protocol, corpus)
    records: list[dict[str, Any]] = []
    missing_id = cells[-1].cell_id if missing_one else None
    timeout_id = cells[0].cell_id if timeout_one else None
    for cell in cells:
        if cell.cell_id == missing_id:
            continue
        outcome = "timed_out" if cell.cell_id == timeout_id else "passed"
        record = run_cell(
            cell,
            agent_cmd=[sys.executable, "-c", "pass"],
            grader=lambda _, result=outcome: {
                "task": result,
                "severe_misses": 0 if result == "passed" else 1,
                "false_blockers": 0,
                "rounds": 0,
                "contract_edits_after_first_freeze": 0,
                "test_receipts": (
                    ["held-out:example-campaign"] if result == "passed" else []
                ),
                "artifacts": [],
            },
            runner_kind=runner_kind,
            **example_observed_provenance(cell),
        )
        records.append(record.to_dict())
    return protocol, corpus, cells, records
