"""Red suite for udd-catalog-content-schema (udd-design-foundation 2/4).

Frozen contract §3 @ v3: a pure stdlib validator
    _catalog_tree_violations(catalog: dict, tree: dict) -> list[(code, path, detail)]
checking OUR compact-JSON component CATALOG (typed props + token-bindings)
against a flat json-render `Spec` CONTENT TREE (pinned @ json-render v0.19.0 /
commit 4e4dc46). [] == valid; else one tuple per violation in deterministic
order. Nine codes:
    tree_cites_uncataloged_component · unknown_prop · prop_type_mismatch ·
    non_semantic_prop_token · dangling_child · children_not_allowed ·
    missing_root · malformed_catalog · malformed_element
SEPARATE from _token_layer_violations (task 1); udd-check-lint composes BOTH.

v2 narrow: non_semantic_prop_token is LAYER-only (alias must target `semantic`);
target existence + $type-match defer to udd-check-lint (it holds tokens.json).
v3 (adversarial refute at verify): the validator is a pure TOTAL function (never
raises). A non-object component entry → malformed_catalog; a tree element that is
not an object / whose props is not an object / whose children is not an array →
malformed_element; an EMPTY children array is treated as ABSENT (no violation).

These run RED before build (AttributeError: missing _catalog_tree_violations;
FileNotFoundError: the sample/doc not yet shipped; pin not yet re-aimed; v3:
crash + missing malformed_element).
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

CANON_CATALOG = _TOOLING / "templates" / "catalog.sample.json"
CANON_PROTOTYPE = _TOOLING / "templates" / "prototype.sample.json"
CANON_DOC = _TOOLING / "templates" / "udd-catalog.md"


def _violations(catalog, tree):
    """Call the (not-yet-built) validator — AttributeError until build."""
    return add._catalog_tree_violations(catalog, tree)


def _pairs(violations):
    return [(v[0], v[1]) for v in violations]


def _valid_catalog():
    """A small catalog: two containers (hasChildren) + two leaves."""
    return {
        "components": {
            "Card": {
                "description": "A surface that groups content",
                "hasChildren": True,
                "props": {
                    "padding": {"type": "token", "token": "dimension"},
                    "elevation": {"type": "enum", "values": ["none", "sm", "md"]},
                },
            },
            "Button": {
                "description": "A clickable action",
                "props": {
                    "label": {"type": "string"},
                    "variant": {"type": "enum", "values": ["primary", "secondary"]},
                    "background": {"type": "token", "token": "color"},
                    "disabled": {"type": "boolean"},
                },
            },
            "Text": {
                "props": {
                    "content": {"type": "string"},
                    "size": {"type": "number"},
                    "color": {"type": "token", "token": "color"},
                },
            },
        }
    }


def _valid_tree():
    """A flat json-render Spec that validates clean against _valid_catalog()."""
    return {
        "root": "card-1",
        "elements": {
            "card-1": {
                "type": "Card",
                "props": {"padding": "{semantic.space.inset-md}", "elevation": "sm"},
                "children": ["txt-1", "btn-1"],
            },
            "txt-1": {
                "type": "Text",
                "props": {"content": "Welcome", "size": 18, "color": "{semantic.color.text}"},
            },
            "btn-1": {
                "type": "Button",
                "props": {
                    "label": "Get started",
                    "variant": "primary",
                    "background": "{semantic.color.accent}",
                    "disabled": False,
                },
                "on": {"click": [{"action": "navigate", "to": "next"}]},
            },
        },
    }


class CatalogTreeValidatorValidTest(unittest.TestCase):
    # --- valid cases (each a DISTINCT minimal fixture — no redundant calls) ---
    def test_sample_validates_clean(self):
        """The shipped sample catalog + prototype validate clean (the exit criterion)."""
        catalog = json.loads(CANON_CATALOG.read_text(encoding="utf-8"))
        tree = json.loads(CANON_PROTOTYPE.read_text(encoding="utf-8"))
        self.assertEqual(_violations(catalog, tree), [])

    def test_token_prop_semantic_binding_ok(self):
        """A token prop bound to a {semantic.*} alias reports nothing."""
        cat = {"components": {"Box": {"props": {"bg": {"type": "token", "token": "color"}}}}}
        tree = {"root": "b", "elements": {"b": {"type": "Box", "props": {"bg": "{semantic.color.accent}"}}}}
        self.assertEqual(_violations(cat, tree), [])

    def test_literal_props_ok(self):
        """string / number / boolean / enum-in-set values all pass."""
        cat = {"components": {"F": {"props": {
            "s": {"type": "string"}, "n": {"type": "number"},
            "b": {"type": "boolean"}, "e": {"type": "enum", "values": ["x", "y"]}}}}}
        tree = {"root": "f", "elements": {"f": {"type": "F",
                "props": {"s": "hi", "n": 3, "b": True, "e": "y"}}}}
        self.assertEqual(_violations(cat, tree), [])

    def test_children_present_ok(self):
        """A hasChildren container whose child ids all exist reports nothing."""
        cat = {"components": {"Box": {"hasChildren": True, "props": {}}, "Leaf": {"props": {}}}}
        tree = {"root": "box", "elements": {
            "box": {"type": "Box", "props": {}, "children": ["a", "b"]},
            "a": {"type": "Leaf", "props": {}},
            "b": {"type": "Leaf", "props": {}}}}
        self.assertEqual(_violations(cat, tree), [])

    def test_passthrough_fields_unlinted(self):
        """json-render's state/on/visible/repeat are render-compatible but NOT linted."""
        cat, tree = _valid_catalog(), _valid_tree()
        tree["elements"]["btn-1"]["state"] = {"count": 0}
        tree["elements"]["btn-1"]["visible"] = {"==": [1, 1]}
        tree["elements"]["card-1"]["repeat"] = {"statePath": "items", "key": "id"}
        self.assertEqual(_violations(cat, tree), [])

    # --- rejections (one per Reject code) -------------------------------
    def test_tree_cites_uncataloged_component(self):
        cat, tree = _valid_catalog(), _valid_tree()
        tree["elements"]["btn-1"]["type"] = "Carousel"   # not in catalog
        v = _violations(cat, tree)
        self.assertIn(("tree_cites_uncataloged_component", "elements.btn-1.type"), _pairs(v))
        self.assertNotIn("elements.txt-1.type", [p for _, p in _pairs(v)])

    def test_unknown_prop(self):
        cat, tree = _valid_catalog(), _valid_tree()
        tree["elements"]["btn-1"]["props"]["elevation"] = "md"   # not declared on Button
        v = _violations(cat, tree)
        self.assertIn(("unknown_prop", "elements.btn-1.props.elevation"), _pairs(v))
        self.assertNotIn(("unknown_prop", "elements.btn-1.props.label"), _pairs(v))

    def test_prop_type_mismatch(self):
        cat, tree = _valid_catalog(), _valid_tree()
        tree["elements"]["btn-1"]["props"]["label"] = 42                 # number → string prop
        tree["elements"]["btn-1"]["props"]["variant"] = "ghost"         # enum ∉ values
        tree["elements"]["btn-1"]["props"]["background"] = "#3B82F6"    # token prop given a non-alias literal
        v = _violations(cat, tree)
        pairs = _pairs(v)
        self.assertIn(("prop_type_mismatch", "elements.btn-1.props.label"), pairs)
        self.assertIn(("prop_type_mismatch", "elements.btn-1.props.variant"), pairs)
        self.assertIn(("prop_type_mismatch", "elements.btn-1.props.background"), pairs)
        self.assertNotIn(("prop_type_mismatch", "elements.btn-1.props.disabled"), pairs)

    def test_non_semantic_prop_token(self):
        """v2 LAYER-only: a token-prop alias must target the semantic layer."""
        cat, tree = _valid_catalog(), _valid_tree()
        tree["elements"]["btn-1"]["props"]["background"] = "{primitive.color.blue-500}"  # primitive, not semantic
        v = _violations(cat, tree)
        self.assertIn(("non_semantic_prop_token", "elements.btn-1.props.background"), _pairs(v))
        self.assertNotIn(("non_semantic_prop_token", "elements.txt-1.props.color"), _pairs(v))

    def test_dangling_child(self):
        cat, tree = _valid_catalog(), _valid_tree()
        tree["elements"]["card-1"]["children"] = ["txt-1", "missing-1"]
        v = _violations(cat, tree)
        self.assertIn(("dangling_child", "elements.card-1.children.missing-1"), _pairs(v))
        self.assertNotIn(("dangling_child", "elements.card-1.children.txt-1"), _pairs(v))

    def test_children_not_allowed(self):
        cat, tree = _valid_catalog(), _valid_tree()
        tree["elements"]["btn-1"]["children"] = ["txt-1"]   # Button has no hasChildren
        v = _violations(cat, tree)
        self.assertIn(("children_not_allowed", "elements.btn-1.children"), _pairs(v))
        self.assertNotIn(("children_not_allowed", "elements.card-1.children"), _pairs(v))

    def test_missing_root(self):
        cat, tree = _valid_catalog(), _valid_tree()
        tree["root"] = "nope"   # names an id absent from elements
        snap = copy.deepcopy(tree)
        v = _violations(cat, tree)
        self.assertIn(("missing_root", "root"), _pairs(v))
        self.assertEqual(tree, snap, "validator must not mutate its input")

    def test_malformed_catalog(self):
        cat, tree = _valid_catalog(), _valid_tree()
        cat["components"]["Text"]["props"]["size"] = {"type": "integer"}        # unknown PropSpec type
        cat["components"]["Button"]["props"]["background"] = {"type": "token", "token": "elevation"}  # unknown $type
        v = _violations(cat, tree)
        pairs = _pairs(v)
        self.assertIn(("malformed_catalog", "components.Text.props.size"), pairs)
        self.assertIn(("malformed_catalog", "components.Button.props.background"), pairs)
        self.assertNotIn(("malformed_catalog", "components.Card.props.elevation"), pairs)

    # --- v3 fail-closed structural checks (the adversarial refute) -------
    def test_non_dict_component_no_crash(self):
        """[v3 F1] a non-object component cited with children → malformed_catalog, never a crash."""
        cat = {"components": {"Card": "a container"}}           # component is a string, not an object
        tree = {"root": "c", "elements": {
            "c": {"type": "Card", "props": {}, "children": ["d"]},
            "d": {"type": "Card", "props": {}}}}
        v = _violations(cat, tree)                              # MUST NOT raise
        self.assertIsInstance(v, list)
        self.assertIn(("malformed_catalog", "components.Card"), _pairs(v))

    def test_malformed_element(self):
        """[v3 F2] element not an object / props not an object / children not an array → malformed_element."""
        cat = {"components": {"Box": {"hasChildren": True, "props": {"label": {"type": "string"}}}}}
        tree = {"root": "ok", "elements": {
            "ok": {"type": "Box", "props": {"label": "fine"}, "children": []},
            "bad-el": "not an object",
            "bad-props": {"type": "Box", "props": [1, 2]},
            "bad-children": {"type": "Box", "props": {}, "children": "e2"}}}
        v = _violations(cat, tree)
        pairs = _pairs(v)
        self.assertIn(("malformed_element", "elements.bad-el"), pairs)
        self.assertIn(("malformed_element", "elements.bad-props.props"), pairs)
        self.assertIn(("malformed_element", "elements.bad-children.children"), pairs)
        self.assertFalse(any(p.startswith("elements.ok") for _, p in pairs),
                         "the well-formed element must not be flagged")

    def test_empty_children_on_non_container_ok(self):
        """[v3 F3] an empty children array on a non-container is treated as absent (no violation)."""
        cat = {"components": {"Leaf": {"props": {"label": {"type": "string"}}}}}
        tree = {"root": "l", "elements": {"l": {"type": "Leaf", "props": {"label": "x"}, "children": []}}}
        self.assertEqual(_violations(cat, tree), [])

    # --- purity / determinism (asserts the injected faults ARE reported) -
    def test_violations_are_pure_and_ordered(self):
        cat, tree = _valid_catalog(), _valid_tree()
        tree["elements"]["btn-1"]["type"] = "Carousel"            # uncataloged
        tree["elements"]["txt-1"]["props"]["ghost"] = "x"         # unknown prop
        snap_cat, snap_tree = copy.deepcopy(cat), copy.deepcopy(tree)
        r1 = _violations(cat, tree)
        r2 = _violations(cat, tree)
        self.assertEqual(r1, r2, "deterministic order")
        # not vacuous — the injected faults ARE reported
        self.assertIn(("tree_cites_uncataloged_component", "elements.btn-1.type"), _pairs(r1))
        self.assertIn(("unknown_prop", "elements.txt-1.props.ghost"), _pairs(r1))
        self.assertEqual(cat, snap_cat, "pure — catalog not mutated")
        self.assertEqual(tree, snap_tree, "pure — tree not mutated")


class CatalogArtifactParityTest(unittest.TestCase):
    def test_parity_samples_and_doc_mirrored(self):
        for rel in (
            "templates/catalog.sample.json",
            "templates/prototype.sample.json",
            "templates/udd-catalog.md",
        ):
            canon = (_TOOLING / rel).read_bytes()
            bundle = (_BUNDLE_TOOLING / rel).read_bytes()
            dogfood = (_DOGFOOD_TOOLING / rel).read_bytes()
            self.assertEqual(canon, bundle, f"{rel}: canonical ≠ bundled")
            self.assertEqual(canon, dogfood, f"{rel}: canonical ≠ dogfood")


if __name__ == "__main__":
    unittest.main()
