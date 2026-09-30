"""RED contract fixtures for acceptable-persona and no-fit corpus cases."""
from __future__ import annotations

import pytest


def _case(case_id="fit-1", acceptable=("security-reviewer", "engine-reviewer"), no_fit=False):
    digest = lambda label: "sha256:" + label.encode("utf-8").hex().ljust(64, "0")[:64]
    return {"id": case_id, "prompt_digest": digest(case_id + "-prompt"),
            "workspace_digest": digest(case_id + "-workspace"),
            "oracle_digest": digest(case_id + "-oracle"),
            "rubric_digest": digest(case_id + "-rubric"),
            "acceptable_personas": list(acceptable), "plausible_wrong_persona": "method-steward",
            "no_fit": no_fit, "agent_visible_paths": ["PROMPT.md", "workspace/"]}


def _payload():
    return {"schema": "add.persona-eval-corpus/1", "version": "persona-corpus/1",
            "cases": [_case(), _case("none-1", (), True)]}


def test_corpus_accepts_sets_and_no_fit_cases():
    from benchmark.persona_eval.corpus import validate_corpus
    corpus = validate_corpus(_payload())
    assert set(corpus.case("fit-1").acceptable_personas) == {"security-reviewer", "engine-reviewer"}
    assert corpus.case("none-1").acceptable_personas == ()


def test_corpus_rejects_wrong_overlap_duplicates_and_evaluator_leaks():
    from benchmark.persona_eval.corpus import validate_corpus
    overlap = _payload(); overlap["cases"][0]["plausible_wrong_persona"] = "security-reviewer"
    duplicate = _payload(); duplicate["cases"].append(dict(duplicate["cases"][0]))
    leaked = _payload(); leaked["cases"][0]["agent_visible_paths"].append("oracle/test_hidden.py")
    prompt_leak = _payload()
    prompt_leak["cases"][0]["prompt_digest"] = prompt_leak["cases"][0]["oracle_digest"]
    workspace_leak = _payload()
    workspace_leak["cases"][0]["workspace_digest"] = workspace_leak["cases"][0]["rubric_digest"]
    malformed_digest = _payload()
    malformed_digest["cases"][0]["rubric_digest"] = "sha256:" + "F" * 64
    for payload in (overlap, duplicate, leaked, prompt_leak, workspace_leak, malformed_digest):
        with pytest.raises(Exception, match="INVALID_CORPUS|ORACLE_LEAK"):
            validate_corpus(payload)
