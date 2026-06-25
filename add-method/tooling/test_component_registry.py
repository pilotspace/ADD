#!/usr/bin/env python3
"""Red/green tests for the component registry (task component-registry, milestone
component-aware-add).

A project may declare named components in `.add/components.toml`
([component.<name>] root=… verify=… green_bar=… language=…). A task binds to one
via a `component: <name>` header line (anchored like `autonomy:`). Binding ADDS
the component's root subtree to the task's §5 scope cover (composes with explicit
tokens — never redraws their resolution). The whole feature is OPT-IN: with no
components.toml, every reader degrades to today's behavior, byte-identical.

Contract (FROZEN @ v1): readers are PURE + DEGRADE-SAFE (never raise on a read —
absent/unreadable/malformed -> {} / dropped cover); the reject codes
(components_malformed · component_unknown · component_root_outside) surface as
`_component_findings` (the scope_violation gate surface), not as crashes.

GREEN pin (holds before AND after the build): the unbound `_declared_scope` path
is unchanged (non-regression). Every other test is RED until the seams land.

Run: cd add-method/tooling && python3 -m unittest test_component_registry -v
"""
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

try:
    import tomllib  # the component pillar requires tomllib (stdlib, Python 3.11+)
    _HAS_TOMLLIB = True
except ModuleNotFoundError:
    _HAS_TOMLLIB = False


def setUpModule():
    # Python < 3.11 has no tomllib, so components.toml cannot be parsed and the component
    # pillar is unavailable (the engine fails loud with components_malformed). The feature's
    # behavior can only be exercised where it exists; 3.12+ runs the full suite.
    if not _HAS_TOMLLIB:
        raise unittest.SkipTest("component pillar requires tomllib (Python 3.11+)")


HERE = Path(__file__).resolve().parent           # add-method/tooling


def _scope_line(*tokens: str) -> str:
    toks = " ".join(f"`{t}`" for t in tokens)
    return f"Scope (may touch): {toks}"


class _Project(unittest.TestCase):
    """A minimal .add/ tree built by hand (the readers are pure file-readers, so no
    full CLI init is needed). self.add = the `.add/` dir = the `root` arg the engine
    readers take; self.proj = the project root (root.parent)."""

    def setUp(self):
        self.proj = Path(tempfile.mkdtemp(prefix="add-comp-")).resolve()
        self.addCleanup(shutil.rmtree, self.proj, ignore_errors=True)
        self.add = self.proj / ".add"
        (self.add / "tasks").mkdir(parents=True)
        # a real component tree so root resolution / _confined has something on disk
        (self.proj / "apps" / "gateway").mkdir(parents=True)

    def tearDown(self):
        # best-effort cleanup; tmp dirs are harmless if left
        pass

    def _components_toml(self, body: str):
        (self.add / "components.toml").write_text(body, encoding="utf-8")

    def _task(self, slug: str, header_extra: str = "", scope: str = ""):
        d = self.add / "tasks" / slug
        d.mkdir(parents=True, exist_ok=True)
        hdr = (f"# TASK: {slug}\n\nslug: {slug} · stage: mvp\n"
               f"{header_extra}phase: build\n")
        body = ("\n---\n\n## 5 · BUILD\n\n"
                f"{scope}\n" if scope else "\n---\n\n## 5 · BUILD\n\n")
        (d / "TASK.md").write_text(hdr + body, encoding="utf-8")
        return d

    _GATEWAY = (
        '[component.gateway]\n'
        'root = "apps/gateway"\n'
        'verify = "pytest -q && pyright"\n'
        'green_bar = "tests + pyright"\n'
        'language = "python"\n'
    )


class ParseRegistry(_Project):

    def test_parse_well_formed_registry(self):
        self._components_toml(self._GATEWAY)
        got = add._components(self.add)
        self.assertEqual(got["gateway"], {
            "root": "apps/gateway", "verify": "pytest -q && pyright",
            "green_bar": "tests + pyright", "language": "python",
        })

    def test_absent_registry_is_empty_map(self):
        # opt-in: no components.toml -> {} (today's behavior)
        self.assertEqual(add._components(self.add), {})

    def test_unreadable_registry_degrades_safe(self):
        # a directory where the file is expected -> OSError on read -> {} (never raises)
        (self.add / "components.toml").mkdir()
        self.assertEqual(add._components(self.add), {})

    def test_verify_is_stored_opaque_not_executed(self):
        # a dangerous string must come back verbatim as DATA — never run
        self._components_toml(
            '[component.gateway]\nroot = "apps/gateway"\nverify = "rm -rf /"\n')
        self.assertEqual(add._components(self.add)["gateway"]["verify"], "rm -rf /")
        self.assertTrue((self.proj / "apps" / "gateway").exists(),
                        "reading the registry must not execute verify")


class ComponentRoot(_Project):

    def test_known_component_root_trailing_slash(self):
        self._components_toml(self._GATEWAY)
        self.assertEqual(add._component_root(self.add, "gateway"), "apps/gateway/")

    def test_absent_name_is_none(self):
        self._components_toml(self._GATEWAY)
        self.assertIsNone(add._component_root(self.add, "ghost"))

    def test_root_outside_project_is_dropped(self):
        # fail-closed: a root escaping the project grants no cover
        self._components_toml('[component.evil]\nroot = "../../etc"\n')
        self.assertIsNone(add._component_root(self.add, "evil"))


class TaskBinding(_Project):

    def test_bound_task_reads_component(self):
        self._components_toml(self._GATEWAY)
        self._task("t", header_extra="component: gateway\n")
        self.assertEqual(add._task_component(self.add, "t"), "gateway")

    def test_unfilled_placeholder_is_not_a_binding(self):
        self._components_toml(self._GATEWAY)
        self._task("t", header_extra="component: <name>\n")
        self.assertIsNone(add._task_component(self.add, "t"),
                          "an unfilled <…> placeholder must read as unbound")

    def test_unknown_token_reads_question_mark(self):
        self._components_toml(self._GATEWAY)
        self._task("t", header_extra="component: ghost\n")
        self.assertEqual(add._task_component(self.add, "t"), "?")


class ScopeBinding(_Project):

    def test_binding_adds_component_root_composing(self):
        self._components_toml(self._GATEWAY)
        (self.proj / "apps" / "gateway" / "rate_limits").mkdir(parents=True)
        self._task("t", header_extra="component: gateway\n",
                   scope=_scope_line("apps/gateway/rate_limits/"))
        declared = add._declared_scope(self.add, "t")
        self.assertIn("apps/gateway/", declared, "component root must be added")
        self.assertIn("apps/gateway/rate_limits/", declared,
                      "explicit token must still resolve as today")

    def test_bound_task_without_scope_line_covered_by_root(self):
        self._components_toml(self._GATEWAY)
        self._task("t", header_extra="component: gateway\n")   # no Scope line
        declared = add._declared_scope(self.add, "t")
        self.assertEqual(declared, ["apps/gateway/"])
        self.assertFalse(add._in_scope("apps/dashboard/x.ts", declared),
                         "a touch outside the component root stays out of scope")

    def test_unbound_declared_scope_unchanged_GREEN_PIN(self):
        # NON-REGRESSION: with no components.toml and no component line, the existing
        # §5 scope behavior is byte-identical. Holds BEFORE and AFTER the build.
        (self.proj / "src").mkdir()
        self._task("t", scope=_scope_line("src/"))
        self.assertEqual(add._declared_scope(self.add, "t"), ["src/"])


class ComponentFindings(_Project):

    def test_malformed_toml_is_a_finding_not_a_crash(self):
        self._components_toml('[component.gateway]\nroot = "apps/gateway"\nthis is not toml')
        # reader degrades safe...
        self.assertEqual(add._components(self.add), {})
        # ...and the gate surface reports it loud
        codes = [c for c, _ in add._component_findings(self.add)]
        self.assertIn("components_malformed", codes)

    def test_missing_required_root_is_malformed(self):
        self._components_toml('[component.gateway]\nverify = "pytest"\n')
        codes = [c for c, _ in add._component_findings(self.add)]
        self.assertIn("components_malformed", codes)

    def test_unknown_binding_is_a_finding(self):
        self._components_toml(self._GATEWAY)
        self._task("t", header_extra="component: ghost\n")
        codes = [c for c, _ in add._component_findings(self.add)]
        self.assertIn("component_unknown", codes)

    def test_root_outside_is_a_finding(self):
        self._components_toml('[component.evil]\nroot = "../../etc"\n')
        codes = [c for c, _ in add._component_findings(self.add)]
        self.assertIn("component_root_outside", codes)

    def test_clean_registry_has_no_findings(self):
        self._components_toml(self._GATEWAY)
        self.assertEqual(add._component_findings(self.add), [])

    def test_unreadable_tasks_dir_degrades_safe(self):
        # refute-read MAJOR: scanning tasks/ must not crash a read. An unreadable
        # tasks/ (PermissionError from iterdir, an OSError) degrades to no crash —
        # the contract's "never raise on a read" guarantee.
        if os.geteuid() == 0:
            self.skipTest("root bypasses directory permissions")
        self._components_toml(self._GATEWAY)
        tasks = self.add / "tasks"
        os.chmod(tasks, 0o000)
        try:
            add._component_findings(self.add)        # must not raise
        finally:
            os.chmod(tasks, 0o755)

    def test_reserved_question_mark_name_is_malformed(self):
        # refute-read MINOR: "?" is the reserved unknown-binding sentinel; a component
        # literally named "?" must NOT register (it would collide and silently drop
        # cover) — it is reported malformed instead.
        self._components_toml('[component."?"]\nroot = "apps/gateway"\n')
        self.assertNotIn("?", add._components(self.add))
        codes = [c for c, _ in add._component_findings(self.add)]
        self.assertIn("components_malformed", codes)


if __name__ == "__main__":
    unittest.main()
