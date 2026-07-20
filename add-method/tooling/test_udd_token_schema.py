"""Red suite for udd-token-schema (udd-design-foundation 1/4).

Frozen contract §3 @ v1: a pure stdlib validator
    _token_layer_violations(tokens: dict) -> list[(code, path, detail)]
for the compact-DTCG 3-layer token dialect. [] == valid; else one tuple per
violation in deterministic document order. Six codes:
    unknown_layer · unknown_type · unresolved_alias · cross_layer_citation ·
    primitive_has_alias · malformed_value
Compact value forms (NAMED divergences from DTCG 2025.10): color = "#RRGGBB",
dimension = "<n><unit>". Layer = top-level group name. The validator is NOT
wired into cmd_check here (Fork A boundary — udd-check-lint wires it later).

These run RED before build (AttributeError: missing _token_layer_violations;
FileNotFoundError: the sample/doc not yet shipped; pin not yet re-aimed).
"""
import copy
import json
import unittest
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
_BUNDLE_TOOLING = _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling"
_DOGFOOD_TOOLING = _REPO / ".add" / "tooling"

CANON_SAMPLE = _TOOLING / "templates" / "tokens.sample.json"
CANON_DOC = _TOOLING / "templates" / "udd-tokens.md"


def _violations(tokens):
    """Call the (not-yet-built) validator — AttributeError until build."""
    return add._token_layer_violations(tokens)


def _pairs(violations):
    return [(v[0], v[1]) for v in violations]


def _valid_tokens():
    """A clean 3-layer fixture: component→semantic→primitive→#hex literal."""
    return {
        "primitive": {
            "color": {"$type": "color",
                      "blue-500": {"$value": "#3B82F6"},
                      "white": {"$value": "#FFFFFF"}},
            "space": {"$type": "dimension",
                      "4": {"$value": "16px"}},
        },
        "semantic": {
            "color": {"$type": "color",
                      "accent": {"$value": "{primitive.color.blue-500}"},
                      "surface": {"$value": "{primitive.color.white}"}},
            "space": {"$type": "dimension",
                      "inset": {"$value": "{primitive.space.4}"}},
        },
        "component": {
            "button": {
                "bg": {"$type": "color", "$value": "{semantic.color.accent}"},
                "padding": {"$type": "dimension", "$value": "{semantic.space.inset}"},
            }
        },
    }


class TokenLayerValidatorTest(unittest.TestCase):
    # --- valid cases (no violation) -------------------------------------
    def test_sample_validates_clean(self):
        """The shipped sample tokens file validates clean (the exit criterion)."""
        sample = json.loads(CANON_SAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(_violations(sample), [])

    def test_semantic_cites_primitive_ok(self):
        toks = {
            "primitive": {"color": {"$type": "color", "blue": {"$value": "#3B82F6"}}},
            "semantic": {"color": {"$type": "color", "accent": {"$value": "{primitive.color.blue}"}}},
        }
        self.assertEqual(_violations(toks), [])

    def test_component_cites_semantic_ok(self):
        self.assertEqual(_violations(_valid_tokens()), [])

    def test_full_chain_to_literal_ok(self):
        """component→semantic→primitive resolves to a literal hex — clean."""
        v = _violations(_valid_tokens())
        self.assertEqual(v, [])

    # --- rejections (one per Reject) ------------------------------------
    def test_unknown_layer(self):
        toks = _valid_tokens()
        toks["foundation"] = {"color": {"$type": "color", "x": {"$value": "#ffffff"}}}
        v = _violations(toks)
        self.assertIn(("unknown_layer", "foundation"), _pairs(v))
        # valid layers stay clean — no violation path points into them
        self.assertFalse(any(p.startswith(("primitive", "semantic", "component"))
                             for _, p in _pairs(v)))

    def test_unknown_type(self):
        toks = {"primitive": {"fx": {"$type": "elevation", "lift": {"$value": "0 1px 2px"}}}}
        snap = copy.deepcopy(toks)
        v = _violations(toks)
        self.assertIn(("unknown_type", "primitive.fx.lift"), _pairs(v))
        self.assertEqual(toks, snap, "validator must not mutate its input")

    def test_unresolved_alias(self):
        toks = {
            "primitive": {"color": {"$type": "color", "blue": {"$value": "#3B82F6"}}},
            "semantic": {"color": {"$type": "color", "accent": {"$value": "{primitive.color.missing}"}}},
        }
        v = _violations(toks)
        self.assertIn(("unresolved_alias", "semantic.color.accent"), _pairs(v))
        # the valid primitive reports nothing
        self.assertNotIn("primitive.color.blue", [p for _, p in _pairs(v)])

    def test_cross_layer_citation(self):
        toks = _valid_tokens()
        # component cites a PRIMITIVE directly (skips semantic)
        toks["component"]["button"]["bg"]["$value"] = "{primitive.color.blue-500}"
        v = _violations(toks)
        self.assertIn(("cross_layer_citation", "component.button.bg"), _pairs(v))
        # the cited primitive itself is fine
        self.assertNotIn("primitive.color.blue-500", [p for _, p in _pairs(v)])

    def test_primitive_has_alias(self):
        toks = {"primitive": {"color": {"$type": "color",
                                        "base": {"$value": "#3B82F6"},
                                        "alias": {"$value": "{primitive.color.base}"}}}}
        snap = copy.deepcopy(toks)
        v = _violations(toks)
        self.assertIn(("primitive_has_alias", "primitive.color.alias"), _pairs(v))
        self.assertEqual(toks, snap, "validator must not mutate its input")

    def test_malformed_value(self):
        toks = {"primitive": {"color": {"$type": "color",
                                        "good": {"$value": "#0000ff"},
                                        "bad": {"$value": "blue"}}}}
        v = _violations(toks)
        self.assertIn(("malformed_value", "primitive.color.bad"), _pairs(v))
        self.assertNotIn("primitive.color.good", [p for _, p in _pairs(v)])

    def test_nested_token_children_are_validated(self):
        """Fail-closed: a node with $value must not HIDE malformed child tokens.

        A token nested inside another token is non-standard, but the validator must
        never skip a subtree — the malformed child is reported, never silently passed.
        """
        toks = {"primitive": {"color": {"$type": "color",
                "blue": {"$value": "#3B82F6", "dark": {"$value": "nothex"}}}}}
        v = _violations(toks)
        self.assertIn(("malformed_value", "primitive.color.blue.dark"), _pairs(v),
                      f"a malformed nested child must not pass silently, got {v}")

    # --- purity / determinism -------------------------------------------
    def test_violations_are_pure_and_ordered(self):
        bad = _valid_tokens()
        bad["component"]["button"]["bg"]["$value"] = "{primitive.color.blue-500}"  # cross-layer
        snap = copy.deepcopy(bad)
        r1 = _violations(bad)
        r2 = _violations(bad)
        self.assertEqual(r1, r2, "deterministic order")
        self.assertEqual(bad, snap, "pure — input not mutated")


class TokenArtifactParityTest(unittest.TestCase):
    def test_parity_sample_and_doc_mirrored(self):
        for rel in ("templates/tokens.sample.json", "templates/udd-tokens.md"):
            canon = (_TOOLING / rel).read_bytes()
            bundle = (_BUNDLE_TOOLING / rel).read_bytes()
            dogfood = (_DOGFOOD_TOOLING / rel).read_bytes()
            self.assertEqual(canon, bundle, f"{rel}: canonical ≠ bundled")
            self.assertEqual(canon, dogfood, f"{rel}: canonical ≠ dogfood")

if __name__ == "__main__":
    unittest.main()
