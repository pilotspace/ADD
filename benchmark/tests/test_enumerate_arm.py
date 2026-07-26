"""`add-enumerate` must differ from `add` by exactly one clause, and that clause
must not hand the arm its answers.

The hypothesis (2026-07-26, amb1 n=3): ADD surfaced exactly 1 of 7 planted
ambiguities in EVERY rep — never 0, never 2 — while its PLAN.md template asks for
one "Least-sure flag surfaced at freeze", singular and ranked lowest-confidence
first. Two readings fit that data:

  a) the singular flag is a CEILING — ADD noticed more and reported one;
  b) ADD noticed one.

Enumeration separates them. If (a), the rate rises; if (b), it does not and the
flag design is exonerated. Either result is worth the run, which is the property
an A/B needs.

The comparison is only worth anything if the two arms differ in ONE way, so that
is asserted mechanically rather than by reading the two strings side by side.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.runner.core import ENUMERATE_CLAUSE, _wrap_prompt

ARMS = pathlib.Path(__file__).resolve().parents[1] / "arms"
PROMPT = "Build a thing.\n"


class TestSingleVariable:
    def test_the_arms_differ_by_exactly_the_clause(self):
        base = _wrap_prompt(PROMPT, "add-loop")
        variant = _wrap_prompt(PROMPT, "add-loop-enumerate")
        assert variant != base
        assert variant.replace(ENUMERATE_CLAUSE, "", 1) == base, (
            "add-enumerate differs from add by more than the enumerate clause; "
            "any measured difference would be unattributable")

    def test_the_baseline_wrapper_is_untouched(self):
        # The `add` arm's numbers must stay comparable with every run already
        # recorded, so the variant may only ever ADD to the wrapper.
        base = _wrap_prompt(PROMPT, "add-loop")
        for phrase in ("proxy authority", "`add.py freeze --by <you> --cross`",
                       "The floor never bends", "gate_mode: ai-plan-verify"):
            assert phrase in base, phrase
        assert ENUMERATE_CLAUSE not in base

    def test_workload_text_still_arrives_verbatim(self):
        assert _wrap_prompt(PROMPT, "add-loop-enumerate").endswith(PROMPT)


class TestClauseLeaksNothing:
    """A clause that names what to look for would plant the answers."""

    def test_clause_names_no_planted_ambiguity(self):
        from benchmark.workload.amb1.ambiguity import AMBIGUITIES

        low = ENUMERATE_CLAUSE.lower()
        for item in AMBIGUITIES:
            for anchor in item["anchors"]:
                assert anchor.lower() not in low, f"clause leaks {item['id']}: {anchor!r}"

    def test_clause_names_no_domain_concept_from_this_workload(self):
        low = ENUMERATE_CLAUSE.lower()
        for word in ("waitlist", "booking", "cancel", "priority", "position",
                     "conflict", "authoriz", "owner", "409", "202", "room"):
            assert word not in low, f"clause leaks domain vocabulary: {word!r}"

    def test_clause_asks_for_completeness_not_a_count(self):
        # "list at least N" would let the arm hit a quota with padding; the
        # measured thing must stay "did you notice", not "did you enumerate".
        low = ENUMERATE_CLAUSE.lower()
        assert "every" in low
        for quota in ("at least", "three", "five", "seven", "all seven"):
            assert quota not in low, f"clause sets a quota: {quota!r}"


class TestArmDefinitionMatchesBaseline:
    def _toml(self, name: str) -> dict[str, str]:
        import tomllib
        return tomllib.loads((ARMS / f"{name}.toml").read_text(encoding="utf-8"))

    def test_only_name_pin_and_wrapper_differ(self):
        base, variant = self._toml("add"), self._toml("add-enumerate")
        differing = {k for k in set(base) | set(variant)
                     if base.get(k) != variant.get(k)}
        assert differing == {"name", "prompt_wrapper", "pin"}, differing

    def test_fairness_floor_is_identical(self):
        base, variant = self._toml("add"), self._toml("add-enumerate")
        for key in ("same_model", "token_ceiling", "turn_ceiling", "setup_steps"):
            assert base[key] == variant[key], key


class TestRegisteredButNotDefault:
    """Selectable by name; absent from every default campaign.

    Adding an experiment arm to the default set would change what `run-all`
    costs and what "a full campaign" means for every future run — a decision
    about the benchmark, not about this experiment.
    """

    def test_experimental_arm_is_selectable(self):
        from benchmark.arms.loader import ALL_ARM_NAMES
        assert "add-enumerate" in ALL_ARM_NAMES

    def test_experimental_arm_is_not_in_the_default_campaign(self):
        from benchmark.arms.loader import ARM_NAMES
        assert "add-enumerate" not in ARM_NAMES

    def test_default_campaign_composition_is_unchanged(self):
        from benchmark.arms.loader import ARM_NAMES
        assert ARM_NAMES == ("add", "add-main", "vanilla", "plan-mode", "gsd", "spec-kit")

    def test_recipe_loads(self):
        import pathlib as _p
        from benchmark.arms.loader import load_arm
        arm = load_arm(_p.Path(ARMS / "add-enumerate.toml"))
        assert arm.name == "add-enumerate"
        assert arm.prompt_wrapper == "add-loop-enumerate"


class TestEveryArmGateAcceptsIt:
    """Registered is not the same as RUNNABLE.

    The first launch of this arm failed instantly on `unknown_arm` despite 423
    green tests: score.py keeps its OWN arm validation, and the suite covered the
    loader and the CLI but never the scorer. Enumerating the gates mechanically
    beats remembering them — a fourth gate added later fails here rather than at
    the start of a paid run.
    """

    def test_no_module_validates_arms_against_the_default_set(self):
        import re
        root = pathlib.Path(__file__).resolve().parents[1]
        offenders = []
        for src in root.rglob("*.py"):
            if "tests" in src.parts or "runs" in str(src):
                continue
            text = src.read_text(encoding="utf-8")
            for m in re.finditer(r"not in ARM_NAMES", text):
                line = text[:m.start()].count("\n") + 1
                offenders.append(f"{src.relative_to(root)}:{line}")
        assert not offenders, (
            "these validate against the DEFAULT campaign set, so an experimental "
            f"arm is rejected at runtime: {offenders}")

    def test_scorer_accepts_the_experimental_arm(self):
        from benchmark.score import ALL_ARM_NAMES as scorer_names
        assert "add-enumerate" in scorer_names
