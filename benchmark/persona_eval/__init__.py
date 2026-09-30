"""Bounded, dry-run-first persona evaluation primitives.

The package deliberately contains no model client.  A caller may inject a
deterministic command into :func:`runner.run_cell`; live execution remains an
explicit property of a validated protocol and runner invocation.
"""

from .allocation import TrialCell, allocate
from .corpus import Corpus, CorpusCase, validate_corpus
from .protocol import Protocol, validate_protocol
from .report import EvaluationReport, summarize
from .runner import CampaignBudget, StopRecord, run_cell, workspace_content_digest

__all__ = [
    "Corpus",
    "CorpusCase",
    "CampaignBudget",
    "EvaluationReport",
    "Protocol",
    "StopRecord",
    "TrialCell",
    "allocate",
    "run_cell",
    "summarize",
    "validate_corpus",
    "validate_protocol",
    "workspace_content_digest",
]
