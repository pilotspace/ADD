#!/usr/bin/env python3
"""Guard for teacher-refresh-ci (persona-teacher-bundle 3/4). CONTRACT frozen @ v1.

A SCHEDULED GitHub Actions workflow keeps the vendored teacher snapshot current WITHOUT a
fetch in the release build: it re-runs the standalone update_teacher.py + prepare_bundle.py
and opens a PULL REQUEST (human reviews the third-party diff before it lands). It is decoupled
from the release/tag pipeline (publish.yml stays zero-network) and the engine stays hands-off.

This guard parses the workflow YAML as text/structure — it does not execute Actions. PyYAML
coerces the bare `on:` key to the boolean True, so trigger checks tolerate both.

Run: python3 -m unittest test_teacher_refresh_ci -v
"""
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO_ROOT = _ADD_METHOD.parent
WORKFLOWS = _REPO_ROOT / ".github" / "workflows"
REFRESH = WORKFLOWS / "teacher-refresh.yml"
PUBLISH = WORKFLOWS / "publish.yml"


def _yaml_load(path: Path):
    import yaml  # PyYAML ships in the CI/test env
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _on_block(doc: dict):
    # `on:` is coerced to the boolean key True by PyYAML — accept either spelling.
    if "on" in doc:
        return doc["on"]
    return doc.get(True)


class TeacherRefreshWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(REFRESH.is_file(),
                        ".github/workflows/teacher-refresh.yml must exist")
        self.text = REFRESH.read_text(encoding="utf-8")
        self.doc = _yaml_load(REFRESH)

    def test_workflow_exists_and_scheduled(self):
        on = _on_block(self.doc)
        self.assertIsInstance(on, dict, "the workflow must declare an `on:` trigger map")
        self.assertIn("schedule", on, "must declare an `on: schedule` trigger (not_scheduled)")
        self.assertIn("workflow_dispatch", on, "must be manually dispatchable (workflow_dispatch)")
        # the schedule entry carries a cron expression
        self.assertRegex(self.text, r"cron:\s*['\"][\d*/ ,\-]+['\"]",
                         "the schedule must carry a cron expression")

    def test_runs_refresh_scripts(self):
        self.assertIn("update_teacher.py", self.text,
                      "the workflow must run update_teacher.py (no_refresh_step)")
        self.assertIn("prepare_bundle.py", self.text,
                      "the workflow must regenerate the bundle via prepare_bundle.py")

    def test_opens_pr_not_push(self):
        opens_pr = ("create-pull-request" in self.text) or \
                   bool(re.search(r"gh\s+pr\s+create", self.text))
        self.assertTrue(opens_pr,
                        "the workflow must OPEN A PR (create-pull-request / gh pr create), "
                        "not push the corpus directly (unreviewed_push)")

    def test_least_priv_and_decoupled(self):
        perms = self.doc.get("permissions", {})
        self.assertIsInstance(perms, dict, "declare explicit least-privilege permissions")
        allowed = {"contents", "pull-requests"}
        granted = {k for k, v in perms.items() if v == "write"}
        self.assertTrue(granted, "the PR-open step needs contents:write + pull-requests:write")
        self.assertTrue(granted <= allowed,
                        f"only {allowed} may be write-granted; got extra: {granted - allowed}")
        # decoupled from the release/tag build
        on = _on_block(self.doc)
        self.assertNotIn("release", on, "must NOT trigger on release (couples_release)")
        push = on.get("push") if isinstance(on, dict) else None
        if isinstance(push, dict):
            self.assertNotIn("tags", push, "must NOT trigger on tag push (couples_release)")
        # publish.yml stays free of any teacher-refresh / schedule coupling
        pub = PUBLISH.read_text(encoding="utf-8")
        self.assertNotIn("update_teacher", pub,
                         "publish.yml must not refresh the teacher (release stays zero-network)")
        self.assertNotIn("teacher-refresh", pub,
                         "publish.yml must not reference the refresh workflow")

    def test_engine_handsoff(self):
        engine_src = (_TOOLING / "add.py").read_text(encoding="utf-8")
        for f in (_TOOLING / "add_engine").glob("*.py"):
            engine_src += f.read_text(encoding="utf-8")
        self.assertNotIn("update_teacher", engine_src,
                         "the fetch lives only in CI/script — never the engine")


if __name__ == "__main__":
    unittest.main(verbosity=2)
