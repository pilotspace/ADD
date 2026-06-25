#!/usr/bin/env python3
"""Behavioral proof of the todo-capture backlog primitive (task: todo-capture).

A lightweight way to jot an idea without sizing it into a task:
  add.py todo "<text>"    -> capture into state["todos"]
  add.py todo             -> list open todos
  add.py todo --done <id> -> close one

CONTRACT (frozen @ v1 — capture/list/done):
  - state["todos"] : list of {id (1-based = max+1), text, created, status:"open"|"done"}
  - capture prints "captured todo #<id>: <text>"; blank text -> todo_empty (exit != 0)
  - bare `todo` lists OPEN todos ("#<id>  <text>"); none -> "no open todos"
  - `todo --done <id>` -> "todo #<id> done"; unknown/closed id -> todo_unknown (exit != 0)

Run: python3 -m unittest test_todo_capture -v
"""
import contextlib
import io
import os
import tempfile
import shutil
import unittest

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


SOUL_TODO = "seed soul.md if missed when update/init ADD into project"


class TodoCapture(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self.tmp = tempfile.mkdtemp(prefix="add-todo-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _todos(self):
        return add.load_state(add.find_root()).get("todos", [])

    # --- (a) capture -> #1 open, listed ---------------------------------------
    def test_capture_then_list(self):
        code, out, _ = _run(["todo", SOUL_TODO])
        self.assertEqual(code, 0, "capture must succeed")
        self.assertIn("#1", out, "the captured todo must report id #1")
        todos = self._todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["text"], SOUL_TODO)
        self.assertEqual(todos[0]["status"], "open")
        self.assertEqual(todos[0]["id"], 1)
        _, lout, _ = _run(["todo"])
        self.assertIn(SOUL_TODO, lout, "bare `todo` must LIST the open todo")
        self.assertIn("#1", lout)

    # --- (b) empty backlog lists nothing --------------------------------------
    def test_list_empty(self):
        _, out, _ = _run(["todo"])
        self.assertIn("no open todos", out.lower())

    # --- (c) done closes it; it leaves the open list --------------------------
    def test_done_closes(self):
        _run(["todo", SOUL_TODO])
        code, out, _ = _run(["todo", "--done", "1"])
        self.assertEqual(code, 0)
        self.assertIn("#1", out)
        self.assertEqual(self._todos()[0]["status"], "done")
        _, lout, _ = _run(["todo"])
        self.assertIn("no open todos", lout.lower(), "a closed todo must leave the open list")

    # --- (d) rejects: blank text + unknown id ---------------------------------
    def test_rejects(self):
        code, _, err = _run(["todo", "   "])
        self.assertNotEqual(code, 0, "blank text must be refused")
        self.assertIn("todo_empty", err.lower() + "")
        code2, _, err2 = _run(["todo", "--done", "99"])
        self.assertNotEqual(code2, 0, "unknown id must be refused")
        self.assertIn("todo_unknown", (err2).lower())

    # --- (e) ids are max+1, stable after a close ------------------------------
    def test_ids_are_stable_max_plus_one(self):
        _run(["todo", "first"])
        _run(["todo", "--done", "1"])
        _, out, _ = _run(["todo", "second"])
        self.assertIn("#2", out, "the second todo must be #2 even after #1 was closed")
        ids = [t["id"] for t in self._todos()]
        self.assertEqual(ids, [1, 2])


if __name__ == "__main__":
    unittest.main()
