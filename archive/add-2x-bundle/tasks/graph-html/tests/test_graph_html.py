"""graph-html — §4 red suite (task: graph-html, standalone).

CONTRACT (frozen @ v1): `graph --html [--out PATH]` writes a self-rendering HTML page
(engine-authored chrome + `<pre class="mermaid">` + a pinned-CDN mermaid <script>) to a
temp file (default under tempfile.gettempdir(), --out overrides + mkdir -p) and prints the
path — never raw mermaid to stdout. Default `graph` (no --html) stays byte-identical.

Run: python3 -m unittest test_graph_html -v
"""
import hashlib
import re
import sys
import tempfile
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "add-method" / "tooling"))

import add  # noqa: E402
from test_graph_repair import _GraphHarness  # noqa: E402


class GraphHtmlTest(_GraphHarness):

    def _seed_signal_graph_like(self):
        """A milestone 'm' with 4 done tasks + an exit-criteria section wired to them,
        mirroring the shape the feature renders (done tasks + met criteria chips)."""
        self._mk_board()
        for slug in ("t1", "t2", "t3", "t4"):
            self._silent("new-task", slug, "--title", slug, "--milestone", "m")
            self._mark_done(slug)
        p = self.tmp / ".add" / "milestones" / "m" / "MILESTONE.md"
        t = p.read_text(encoding="utf-8")
        body = ("- [x] one  (← t1)\n- [x] two  (← t2)\n"
                "- [x] three  (← t3)\n- [x] four  (← t4)")
        p.write_text(re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                            "## Exit criteria (observable)\n" + body + "\n", t, flags=re.S),
                     encoding="utf-8")

    def test_graph_html_writes_file_to_tmp(self):                 # M1,M2
        self._mk_board()
        out = self._silent("graph", "--html")
        self.assertIn("wrote ", out)
        self.assertIn(tempfile.gettempdir(), out)
        self.assertNotIn("flowchart TD", out, "raw mermaid must not print to stdout in --html mode")
        written = Path(out.split("wrote ", 1)[1].splitlines()[0].strip())
        self.assertTrue(written.exists())

    def test_graph_html_out_override_and_mkdir(self):             # M2, R:out_parent_created
        self._mk_board()
        target = self.tmp / "nested" / "deep" / "g.html"
        self._silent("graph", "--html", "--out", str(target))
        self.assertTrue(target.exists(), "missing parent dir must be created")

    def test_graph_html_self_rendering(self):                     # M3
        self._mk_board()
        target = self.tmp / "g.html"
        self._silent("graph", "--html", "--out", str(target))
        page = target.read_text(encoding="utf-8")
        self.assertIn('<pre class="mermaid"', page)
        self.assertIn("flowchart TD", page)
        self.assertIn("mermaid.initialize", page)
        self.assertIn("<script", page)

    def test_graph_html_escaped_diagram(self):                    # M3
        self._mk_board()
        self._silent("new-task", "a", "--title", "a", "--milestone", "m")
        self._silent("new-task", "b", "--title", "b", "--milestone", "m")
        self._silent("relate", "b", "--depends-on", "a")          # a real '-->' edge to escape
        target = self.tmp / "g.html"
        self._silent("graph", "--html", "--out", str(target))
        page = target.read_text(encoding="utf-8")
        block = page.split('<pre class="mermaid"', 1)[1].split("</pre>", 1)[0]
        # the arrow '-->' escapes to '--&gt;'; no unescaped '-->' inside the mermaid block
        self.assertIn("--&gt;", block)
        self.assertNotIn("-->", block, "diagram must be HTML-escaped inside <pre>")

    def test_graph_html_status_chrome(self):                      # M4
        self._seed_signal_graph_like()
        target = self.tmp / "g.html"
        self._silent("graph", "--html", "--milestone", "m", "--out", str(target))
        page = target.read_text(encoding="utf-8").replace(" ", "")
        self.assertIn("4/4", page)   # both chips read 4/4 (4 done tasks, 4 met criteria)

    def test_graph_default_still_mermaid(self):                   # M5
        self._mk_board()
        out = self._silent("graph")
        self.assertIn("flowchart TD", out)
        self.assertNotIn("wrote ", out)
        self.assertNotIn("<pre", out)

    def test_graph_html_three_trees_identical(self):              # M6
        trees = [_REPO / "add-method" / "tooling" / "add.py",
                 _REPO / "add-method" / ".add" / "tooling" / "add.py",
                 _REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py"]
        self.assertEqual(len({hashlib.md5(p.read_bytes()).hexdigest() for p in trees}), 1)


if __name__ == "__main__":
    unittest.main()
