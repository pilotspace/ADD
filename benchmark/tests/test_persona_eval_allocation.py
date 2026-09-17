"""RED contract fixtures for balanced, seeded persona-condition allocation."""
from __future__ import annotations

import pytest


def test_allocation_is_complete_balanced_and_seed_stable():
    from benchmark.persona_eval.allocation import allocate
    from benchmark.persona_eval.fixtures import example_corpus, example_protocol
    from benchmark.persona_eval.runner import CampaignBudget
    corpus = example_corpus()
    protocol_a = example_protocol(seed=7)
    a = allocate(protocol_a, corpus)
    again = allocate(example_protocol(seed=7), example_corpus())
    b = allocate(example_protocol(seed=11), example_corpus())
    assert a == again
    assert {c.cell_id for c in a} == {c.cell_id for c in b}
    assert {c.to_dict()["pin_manifest_digest"] for c in a} == {
        c.to_dict()["pin_manifest_digest"] for c in b
    }
    assert list(a) != list(b)
    assert {c.campaign_manifest_digest for c in a} == {
        c.campaign_manifest_digest for c in b
    }
    blocks = {}
    for cell in a:
        blocks.setdefault((cell.task_id, cell.repetition), []).append(cell)
    assert all({c.condition for c in cells} == {"neutral", "routed_correct", "plausible_wrong"}
               for cells in blocks.values())
    no_fit = [c for c in a if c.task_id == "none-1"]
    assert all(c.persona_id is None for c in no_fit if c.condition != "plausible_wrong")

    b_by_id = {cell.cell_id: cell for cell in b}
    seed_b_in_seed_a_order = tuple(b_by_id[cell.cell_id] for cell in a)
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        CampaignBudget(protocol_a, corpus, seed_b_in_seed_a_order)


def test_allocation_detects_condition_drift():
    from dataclasses import replace

    import benchmark.persona_eval.allocation as allocation_module
    from benchmark.persona_eval.allocation import assert_condition_balance, validate_trial_cell
    from benchmark.persona_eval.fixtures import example_cells
    cells = list(example_cells())
    cells[1] = cells[1].replace(token_ceiling=cells[1].token_ceiling + 1)
    with pytest.raises(Exception, match="CONDITION_DRIFT"):
        assert_condition_balance(cells)

    forged = list(example_cells())
    neutral = next(i for i, cell in enumerate(forged) if cell.condition == "neutral")
    forged[neutral] = forged[neutral].replace(
        persona_id="method-steward",
        persona_digest="sha256:forged-persona",
        persona_injection_digest="sha256:forged-injection",
        effective_prompt_digest="sha256:forged-prompt",
    )
    with pytest.raises(Exception, match="CONDITION_DRIFT|PROVENANCE_DRIFT"):
        assert_condition_balance(forged)

    base = next(cell for cell in example_cells() if cell.condition == "neutral")
    invented = replace(base, task_id="not-in-corpus", cell_id="", pin_manifest_digest="")
    values = invented.to_dict()
    manifest = allocation_module._pin_manifest_digest(values)
    invented = replace(
        invented,
        pin_manifest_digest=manifest,
        cell_id=allocation_module._cell_id(manifest),
    )
    with pytest.raises(Exception, match="PROVENANCE_DRIFT|UNBALANCED_MATRIX"):
        validate_trial_cell(invented)
