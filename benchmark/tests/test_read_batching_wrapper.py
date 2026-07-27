"""The measured arm exercises the method's own batching guidance.

If the direction guide tells a reader to batch their grounding reads but the
`add-loop` wrapper does not, the benchmark measures a version of ADD that no
user runs — the same class of dishonesty `arm-honesty` just closed on the
comparison side. And a clause leaked into `raw` or `spec-kit` would improve the
controls along with the treatment, making the comparison meaningless in the
other direction.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pytest

from benchmark.runner.core import BATCH_CLAUSE, _wrap_prompt

PROMPT = "BUILD THE THING"


@pytest.mark.parametrize("wrapper", ["add-loop", "add-loop-enumerate"])
def test_add_loop_wrapper_carries_the_batch_clause(wrapper):
    assert BATCH_CLAUSE in _wrap_prompt(PROMPT, wrapper), (
        f"unbatched_arm: the {wrapper} wrapper omits the batching instruction the "
        "direction guide gives every user — the benchmark would measure a method "
        "nobody runs")


@pytest.mark.parametrize("wrapper", ["add-loop", "add-loop-enumerate"])
def test_wrapper_tells_the_agent_to_skip_harness_bookkeeping(wrapper):
    wrapped = _wrap_prompt(PROMPT, wrapper).lower()
    assert "task-tracker" in wrapped and "sleep" in wrapped, (
        "harness bookkeeping (task-tracker calls, sleep-polling) cost 3.9 minutes of "
        "the measured direction phase and delivers nothing to the workload")


@pytest.mark.parametrize("wrapper", ["add-loop", "add-loop-enumerate"])
def test_wrapper_still_carries_the_workload_prompt(wrapper):
    assert PROMPT in _wrap_prompt(PROMPT, wrapper)


def test_raw_wrapper_is_untouched():
    # The honest control must stay verbatim; a clause leaked in here biases every
    # comparison the benchmark publishes.
    assert _wrap_prompt(PROMPT, "raw") == PROMPT
    assert BATCH_CLAUSE not in _wrap_prompt(PROMPT, "raw")


def test_spec_kit_wrapper_does_not_receive_it():
    assert BATCH_CLAUSE not in _wrap_prompt(PROMPT, "spec-kit")


def test_batch_clause_is_substantive():
    # A one-word constant would satisfy the containment checks above vacuously.
    assert len(BATCH_CLAUSE) > 80, BATCH_CLAUSE
    assert "one turn" in BATCH_CLAUSE.lower()
