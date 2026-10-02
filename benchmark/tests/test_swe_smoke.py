"""Guards for the SWE-bench smoke harness (benchmark/swe/runner.py).

All offline — network/agent/docker paths are exercised by the live smoke run,
not here. These pin the parts that would silently corrupt a leaderboard-style
claim: the patch filter (fix only, never method artifacts), the pinned agent
argv (same meter as the wm bench), and the arm prompts.
"""
import unittest

from benchmark.swe import runner


FIX_BLOCK = (
    "diff --git a/requests/sessions.py b/requests/sessions.py\n"
    "index 111..222 100644\n"
    "--- a/requests/sessions.py\n"
    "+++ b/requests/sessions.py\n"
    "@@ -1 +1 @@\n-old\n+new\n"
)
ADD_BLOCK = (
    "diff --git a/.add/PROJECT.md b/.add/PROJECT.md\n"
    "index 333..444 100644\n"
    "--- a/.add/PROJECT.md\n"
    "+++ b/.add/PROJECT.md\n"
    "@@ -1 +1 @@\n-x\n+y\n"
)
CLAUDE_BLOCK = (
    "diff --git a/CLAUDE.md b/CLAUDE.md\n"
    "index 555..666 100644\n"
    "--- a/CLAUDE.md\n"
    "+++ b/CLAUDE.md\n"
    "@@ -1 +1 @@\n-a\n+b\n"
)


class PatchFilterTest(unittest.TestCase):
    def test_fix_block_survives(self):
        self.assertEqual(runner.filter_patch(FIX_BLOCK), FIX_BLOCK)

    def test_add_artifacts_dropped(self):
        mixed = ADD_BLOCK + FIX_BLOCK + CLAUDE_BLOCK
        self.assertEqual(runner.filter_patch(mixed), FIX_BLOCK)

    def test_all_artifact_patch_becomes_empty(self):
        self.assertEqual(runner.filter_patch(ADD_BLOCK + CLAUDE_BLOCK), "")

    def test_empty_patch_passthrough(self):
        self.assertEqual(runner.filter_patch(""), "")

    def test_every_declared_artifact_prefix_filtered(self):
        for prefix in runner._ARTIFACT_PREFIXES:
            block = FIX_BLOCK.replace("requests/sessions.py", f"{prefix}thing.md")
            self.assertEqual(runner.filter_patch(block), "", prefix)


class AgentArgvTest(unittest.TestCase):
    def test_argv_is_the_wm_meter_with_isolation(self):
        """Same argv builder as the wm bench (benchmark.runner.agent): the operator's user
        plugins/hooks/CLAUDE.md never reach the measured session (round-8 finding)."""
        argv = runner.agent_argv("do it", "claude-sonnet-5-5", "low")
        self.assertEqual(argv[:3], ["claude", "-p", "do it"])
        self.assertEqual(argv[argv.index("--model") + 1], "claude-sonnet-5-5")
        self.assertEqual(argv[argv.index("--effort") + 1], "low")
        self.assertEqual(argv[argv.index("--setting-sources") + 1], "project,local")
        self.assertEqual(argv[argv.index("--output-format") + 1], "stream-json")

    def test_each_arm_has_its_effort(self):
        self.assertEqual(runner.ARM_EFFORT, {"vanilla": "medium", "add": "low"})


class PromptTest(unittest.TestCase):
    def test_both_arms_embed_issue(self):
        for arm in ("vanilla", "add"):
            p = runner.wrap_prompt("THE-ISSUE-TEXT", arm)
            self.assertIn("<issue>\nTHE-ISSUE-TEXT\n</issue>", p)

    def test_add_arm_drives_the_4_0_skill(self):
        p = runner.wrap_prompt("x", "add")
        for phrase in (".claude/skills/add/SKILL.md", "freeze(", "reproduces the issue",
                       "regression floor", "Never weaken existing tests", "no human"):
            self.assertIn(phrase, p)
        self.assertNotIn("add.py", p, "the 2.0 engine is gone in 4.0")

    def test_vanilla_arm_is_method_free(self):
        p = runner.wrap_prompt("x", "vanilla")
        self.assertNotIn(".add", p)
        self.assertNotIn("SKILL", p)


class InstallTest(unittest.TestCase):
    def test_install_runs_the_4_0_installer_only(self):
        import inspect
        src = inspect.getsource(runner.install_add)
        self.assertIn("pilotspace-add", src)
        for gone in (".add/tooling", "--force", "--stage"):
            self.assertNotIn(gone, src, f"{gone} belongs to the retired engine/installer")


class PatchCollectTest(unittest.TestCase):
    def test_new_untracked_files_are_part_of_the_patch(self):
        """`git diff <base>` alone misses a NEW file the fix adds and never commits."""
        import pathlib, subprocess, tempfile
        with tempfile.TemporaryDirectory() as td:
            w = pathlib.Path(td)
            g = lambda *a: subprocess.run(["git", "-C", td, *a], check=True, capture_output=True, text=True)
            g("init", "-q"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
            (w / "a.py").write_text("old\n"); g("add", "-A"); g("commit", "-qm", "base")
            base = g("rev-parse", "HEAD").stdout.strip()
            (w / "a.py").write_text("new\n"); (w / "b.py").write_text("added\n")
            (w / ".add").mkdir(); (w / ".add" / "x.md").write_text("artifact\n")
            patch = runner.collect_patch(w, base, w / "log")
        self.assertIn("diff --git a/a.py b/a.py", patch)
        self.assertIn("diff --git a/b.py b/b.py", patch)
        self.assertNotIn(".add/", patch)


class SampleTest(unittest.TestCase):
    def test_sample_is_deterministic_and_sized(self):
        ids = [f"repo__x-{i}" for i in range(300)]
        a, b = runner.sample_ids(ids, 30, seed=7), runner.sample_ids(list(reversed(ids)), 30, seed=7)
        self.assertEqual(a, b, "the slice must not depend on fetch order")
        self.assertEqual(len(set(a)), 30)
        self.assertNotEqual(a, runner.sample_ids(ids, 30, seed=8))


class SmokeConfigTest(unittest.TestCase):
    def test_smoke_slice_is_small_requests_trio(self):
        self.assertEqual(len(runner.SMOKE_INSTANCES), 3)
        for iid in runner.SMOKE_INSTANCES:
            self.assertTrue(iid.startswith("psf__requests-"), iid)

    def test_default_model_pinned(self):
        self.assertEqual(runner.PINNED_MODEL, "claude-sonnet-5-5")

    def test_runs_root_is_gitignored_name(self):
        self.assertTrue(str(runner.DEFAULT_RUNS).endswith("benchmark/runs-swe"))


class FetchCacheTest(unittest.TestCase):
    def test_cached_rows_never_touch_the_network(self):
        import json as _json
        import pathlib
        import tempfile
        row = {"instance_id": "psf__requests-2317", "repo": "psf/requests",
               "base_commit": "abc", "problem_statement": "x"}
        with tempfile.TemporaryDirectory() as td:
            cache = pathlib.Path(td) / "instances.json"
            cache.write_text(_json.dumps({row["instance_id"]: row}))
            # urlopen would raise on any real call in this offline test; a
            # cache hit must return without attempting one.
            got = runner.fetch_instances([row["instance_id"]], cache=cache)
        self.assertEqual(got, [row])


class CostParseTest(unittest.TestCase):
    def test_last_cost_from_stream(self):
        out = '{"type":"x"}\nnot json\n{"total_cost_usd": 1.25, "type":"result"}\n'
        self.assertEqual(runner._last_cost(out), 1.25)

    def test_no_cost_is_zero(self):
        self.assertEqual(runner._last_cost("nothing\n"), 0.0)


if __name__ == "__main__":
    unittest.main()
