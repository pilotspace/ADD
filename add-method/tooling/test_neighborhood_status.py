#!/usr/bin/env python3
"""neighborhood-status red suite (adaptive-flow, ATG localized-context step).

Each atomic node carries its NEIGHBORHOOD's interfaces so execution never
re-discovers them from code: `new-task` and full `status` print a compact
card — one line per inherited interface (parent slug · its §3 contract head ·
where its code lives). Parents = declared edges (depends-on ∪ extends); a
board with NO edges falls back to the most recently updated DONE tasks (the
temporal neighborhood — measured: bench agents declare no edges, and the
re-discovery reads are the wm4-6 cost growth).

Floors (bind after green): degrade-safe (unreadable parent PLAN silently
skipped) · silent on an empty neighborhood · `status --brief` stays card-free
(the resume card is the lean surface) · card caps at 3 parents (bytes bound).

Run: cd add-method/tooling && python3 -m unittest test_neighborhood_status -v
"""
import json
import unittest

import add
from test_freeze_command import _Harness

CARD_HEADER = "neighborhood"


class _NbrHarness(_Harness):
    def _mk_board(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")

    def _mk_done_parent(self, slug, contract_line, code_line="`./src/`", ts="2026-07-01T00:00:00+00:00"):
        """Fabricate a DONE parent: PLAN.md with a §3 fence + §5 code line, state marked done."""
        self._silent("new-task", slug, "--title", slug)
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        fence = f"```\n{contract_line}\n  200 -> {{ ok }}\n```"
        start = text.index("```")
        end = text.index("```", start + 3) + 3
        text = text[:start] + fence + text[end:]
        text = text.replace("Code lives in: `./src/`", f"Code lives in: {code_line}")
        p.write_text(text, encoding="utf-8")
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text())
        st["tasks"][slug]["phase"] = "done"
        st["tasks"][slug]["gate"] = "PASS"
        st["tasks"][slug]["updated"] = ts
        sp.write_text(json.dumps(st, indent=2))


class DeclaredEdgeCardTest(_NbrHarness):
    def test_new_task_card_shows_parent_contract(self):
        self._mk_board()
        self._mk_done_parent("bookings-api", "POST /bookings   body: { room_id, start }")
        out = self._silent("new-task", "child", "--title", "Child", "--depends-on", "bookings-api")
        self.assertIn(CARD_HEADER, out)
        self.assertIn("bookings-api", out)
        self.assertIn("POST /bookings", out, "the parent's §3 contract head line is the interface")

    def test_status_full_shows_card_for_active_task(self):
        self._mk_board()
        self._mk_done_parent("bookings-api", "POST /bookings   body: { room_id }")
        self._silent("new-task", "child", "--title", "Child", "--depends-on", "bookings-api")
        out = self._silent("status")
        self.assertIn(CARD_HEADER, out)
        self.assertIn("POST /bookings", out)

    def test_brief_stays_card_free(self):
        self._mk_board()
        self._mk_done_parent("bookings-api", "POST /bookings   body: { room_id }")
        self._silent("new-task", "child", "--title", "Child", "--depends-on", "bookings-api")
        out = self._silent("status", "--brief")
        self.assertNotIn(CARD_HEADER, out, "--brief is the lean resume surface — no card")


class RecencyFallbackTest(_NbrHarness):
    def test_no_edges_falls_back_to_recent_done(self):
        self._mk_board()
        self._mk_done_parent("older", "GET /old", ts="2026-07-01T00:00:00+00:00")
        self._mk_done_parent("newer", "GET /new", ts="2026-07-02T00:00:00+00:00")
        out = self._silent("new-task", "child", "--title", "Child")
        self.assertIn(CARD_HEADER, out)
        self.assertIn("GET /new", out, "most recent done task is the temporal neighborhood")

    def test_first_task_has_no_card(self):
        self._mk_board()
        out = self._silent("new-task", "solo", "--title", "Solo")
        self.assertNotIn(CARD_HEADER, out, "an empty neighborhood prints nothing")

    def test_card_caps_at_three_parents(self):
        self._mk_board()
        for i in range(5):
            self._mk_done_parent(f"p{i}", f"GET /p{i}", ts=f"2026-07-0{i+1}T00:00:00+00:00")
        out = self._silent(
            "new-task", "child", "--title", "Child", "--depends-on", "p0,p1,p2,p3,p4")
        shown = sum(1 for i in range(5) if f"GET /p{i}" in out)
        self.assertLessEqual(shown, 3, "the card is a bytes-bounded summary, not the board")


class DegradeSafeTest(_NbrHarness):
    def test_unreadable_parent_skipped(self):
        self._mk_board()
        self._mk_done_parent("ok-parent", "GET /ok")
        self._silent("new-task", "ghost", "--title", "Ghost")
        (self.tmp / ".add" / "tasks" / "ghost" / "PLAN.md").unlink()
        out = self._silent(
            "new-task", "child", "--title", "Child", "--depends-on", "ok-parent,ghost")
        self.assertIn("GET /ok", out)
        self.assertNotIn("Traceback", out)

    def test_unfilled_parent_contract_skipped(self):
        # a parent whose §3 fence is still the template placeholder teaches nothing —
        # the card skips it rather than echoing `<METHOD> <path>` noise
        self._mk_board()
        self._silent("new-task", "draft-parent", "--title", "Draft")
        out = self._silent("new-task", "child", "--title", "Child", "--depends-on", "draft-parent")
        self.assertNotIn("<METHOD>", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
