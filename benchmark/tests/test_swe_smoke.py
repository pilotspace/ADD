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
        for phrase in (".claude/skills/add/SKILL.md", "reproduces the issue",
                       "regression floor", "Never weaken existing tests", "no human"):
            self.assertIn(phrase, p)
        self.assertNotIn("add.py", p, "the 2.0 engine is gone in 4.0")

    def test_add_arm_lets_the_skill_size_the_work(self):
        """SWE-LITE-PILOT-2026-10-03: the prompt demanded a freeze commit and ONE task for every
        issue, so 26 bounded fixes paid for a Task. The skill's own sizing decides the lane."""
        p = runner.wrap_prompt("x", "add")
        self.assertIn("size the work as the skill says", p)
        self.assertNotIn("ONE task", p)
        self.assertNotIn("freeze(", p)

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


class PagedFetchTest(unittest.TestCase):
    def test_paged_fetch_seeds_the_row_cache(self):
        """The per-id /filter endpoint 500s under load; the paged /rows fetch that lists the ids
        already carries every row, so it fills the instance cache and /filter is never needed."""
        import io, json as _json, pathlib, tempfile
        from unittest import mock
        row = {"instance_id": "a__b-1", "repo": "a/b", "base_commit": "c", "problem_statement": "p"}
        page = _json.dumps({"rows": [{"row": row}], "num_rows_total": 1}).encode()
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(runner.urllib.request, "urlopen", return_value=io.BytesIO(page)):
            root = pathlib.Path(td)
            ids = runner.fetch_all_ids(cache=root / "lite_ids.json", rows_cache=root / "instances.json")
            self.assertEqual(ids, ["a__b-1"])
            self.assertEqual(_json.loads((root / "instances.json").read_text()), {"a__b-1": row})

    def test_rows_cache_is_readable_by_fetch_instances(self):
        import io, json as _json, pathlib, tempfile
        from unittest import mock
        row = {"instance_id": "a__b-1", "repo": "a/b", "base_commit": "c", "problem_statement": "p"}
        page = _json.dumps({"rows": [{"row": row}], "num_rows_total": 1}).encode()
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            with mock.patch.object(runner.urllib.request, "urlopen", return_value=io.BytesIO(page)):
                runner.fetch_all_ids(cache=root / "lite_ids.json", rows_cache=root / "instances.json")
            with mock.patch.object(runner.urllib.request, "urlopen", side_effect=AssertionError("network")):
                self.assertEqual(runner.fetch_instances(["a__b-1"], cache=root / "instances.json"), [row])


class EffortOverrideTest(unittest.TestCase):
    def test_effort_override_reaches_every_arm(self):
        """The 2x2 sweep runs each arm at both efforts; the default pairing stays ADD-low / vanilla-medium."""
        self.assertEqual(runner.effort_for("add", None), "low")
        self.assertEqual(runner.effort_for("vanilla", None), "medium")
        self.assertEqual(runner.effort_for("add", "medium"), "medium")
        self.assertEqual(runner.effort_for("vanilla", "low"), "low")
        with self.assertRaises(SystemExit):
            runner.effort_for("add", "lo")


class TestEnvTest(unittest.TestCase):
    """--testenv docker: the agent edits a host copy of the instance image's /testbed, and its
    python/pytest calls inside that copy run in the image's own conda env (the env the official
    harness scores in). Both arms get the same env; the prompts do not change."""

    def test_image_is_the_official_eval_image(self):
        self.assertEqual(runner.image_for("django__django-11630"),
                         "swebench/sweb.eval.x86_64.django_1776_django-11630:latest")

    def test_container_mounts_the_workspace_at_testbed_and_at_its_own_path(self):
        argv = runner.testenv_run_argv("ctr", "/w/space", "img:latest")
        self.assertEqual(argv[:4], ["docker", "run", "-d", "--platform"])
        self.assertIn("/w/space:/testbed", argv)
        self.assertIn("/w/space:/w/space", argv)
        self.assertEqual(argv[-1], "infinity")

    def _shims(self, td):
        import os, pathlib
        root = pathlib.Path(td)
        ws = root / "ws"; ws.mkdir()
        fake = root / "fakebin"; fake.mkdir()
        (fake / "docker").write_text('#!/bin/sh\necho "DOCKER $*"\n'); os.chmod(fake / "docker", 0o755)
        shims = runner.write_shims(root / "shims", "ctr-1", ws)
        env = dict(os.environ, PATH=f"{shims}:{fake}:{os.environ['PATH']}")
        return ws, shims, env

    def test_shim_routes_workspace_python_into_the_container(self):
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as td:
            ws, shims, env = self._shims(td)
            (ws / "pkg").mkdir()
            out = subprocess.run(["python3", "-m", "pytest", "-q"], cwd=ws / "pkg", env=env,
                                 capture_output=True, text=True).stdout
        self.assertIn("DOCKER exec -i -w", out)
        self.assertIn(f"{ws.resolve()}/pkg ctr-1", out)
        self.assertIn("activate testbed", out)
        self.assertIn("python -m pytest -q", out.replace("python3", "python"))

    def test_every_python_name_is_shimmed(self):
        import os, tempfile
        with tempfile.TemporaryDirectory() as td:
            _, shims, _ = self._shims(td)
            names = set(os.listdir(shims))
        for name in ("python", "python3", "python3.9", "pytest", "py.test", "pip"):
            self.assertIn(name, names)

    def test_shim_outside_the_workspace_runs_the_host_binary(self):
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as td:
            _, shims, env = self._shims(td)
            out = subprocess.run(["python3", "-c", "print('host')"], cwd=td, env=env,
                                 capture_output=True, text=True).stdout
        self.assertEqual(out.strip(), "host")

    def test_agent_shell_keeps_the_shims_first(self):
        """The agent's Bash tool sources the operator's zsh profile, which rebuilds PATH: the
        testenv points ZDOTDIR at an rc that puts the shims first and reads nothing else."""
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            env = runner.testenv_env(pathlib.Path(td) / "shims", {"PATH": "/usr/bin", "HOME": "/h"})
            rc = (pathlib.Path(env["ZDOTDIR"]) / ".zshrc").read_text()
        shims = (pathlib.Path(td) / "shims").resolve()
        self.assertTrue(env["PATH"].startswith(str(shims)))
        self.assertIn(f'export PATH="{shims}:', rc)

    def test_shims_are_on_path_absolute(self):
        """The runs root is often relative; the agent's cwd is the workspace, so a relative
        shims entry on PATH resolves to nothing and every call falls back to the host."""
        import os, pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            here = os.getcwd(); os.chdir(td)
            try:
                env = runner.testenv_env(runner.write_shims(pathlib.Path("rel/shims"), "c", pathlib.Path(td)),
                                         {"PATH": "/usr/bin"})
            finally:
                os.chdir(here)
        self.assertTrue(pathlib.Path(env["PATH"].split(os.pathsep)[0]).is_absolute())
        self.assertTrue(pathlib.Path(env["ZDOTDIR"]).is_absolute())

    def test_container_name_is_unique_per_runs_root(self):
        """Two cells running the same arm on the same instance at once (an effort sweep) must not
        collide on one container name: the second `docker run` fails and the run is lost."""
        import pathlib
        a = runner.container_name("add", "django__django-1", pathlib.Path("/r/low"))
        b = runner.container_name("add", "django__django-1", pathlib.Path("/r/medium"))
        self.assertNotEqual(a, b)
        self.assertEqual(a, runner.container_name("add", "django__django-1", pathlib.Path("/r/low")))


class InjectSkillTest(unittest.TestCase):
    """At --effort low the ADD arm read SKILL.md in only 134 of 270 full-300 runs: the method was
    half-applied. --inject-skill puts the installed skill in the system prompt instead."""

    def test_inject_appends_the_installed_skill_to_the_system_prompt(self):
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            ws = pathlib.Path(td)
            (ws / ".claude/skills/add").mkdir(parents=True)
            (ws / ".claude/skills/add/SKILL.md").write_text("# ADD\nthe skill body\n")
            argv = runner.agent_argv("P", "m", "low", inject_skill_from=ws)
        i = argv.index("--append-system-prompt")
        self.assertIn("the skill body", argv[i + 1])

    def test_injected_prompt_does_not_ask_to_read_the_file(self):
        p = runner.wrap_prompt("the issue", "add", injected=True)
        self.assertNotIn("read `.claude/skills/add/SKILL.md` first", p)
        self.assertIn("system prompt", p)
        self.assertIn("the issue", p)

    def test_default_is_unchanged(self):
        self.assertNotIn("--append-system-prompt", runner.agent_argv("P", "m", "low"))
        self.assertIn("read `.claude/skills/add/SKILL.md` first", runner.wrap_prompt("x", "add"))
