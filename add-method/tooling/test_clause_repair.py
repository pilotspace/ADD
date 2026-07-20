#!/usr/bin/env python3
"""clause-repair red suite (task-graph-native W3, the ATG red-dot at clause depth).

W2's `locate` stops at the NODE. W3 goes one level deeper: §4 may map each red
test to the §3 clause key it proves — a `covers:` line, frozen WITH the bundle so
the map is tamper-guarded — and `locate <path>::<test_name>` (pytest node-id form)
resolves a failing test through that map to the exact frozen §3 clause line.
Deterministic, no LLM: the clause is found by literal key match inside the frozen
§3 body; a key the §3 text doesn't carry is reported honestly, never guessed.

Grammar (§4 body, any line after `Tests live in:`):
    - `test_name` covers: R-code[, R-code…]

Floors (bind after green): plain-path mode unchanged · no-covers-entry is an
advisory nudge (exit 0) · unowned stays unowned with or without `::name`.

Run: cd add-method/tooling && python3 -m unittest test_clause_repair -v
"""
import unittest

import add
from test_graph_repair import _GraphHarness

TESTS_LINE = "Tests live in: `./tests/` · MUST run red (missing implementation) before Build."


class _ClauseHarness(_GraphHarness):
    def _mk_covered_task(self, slug="api-core", covers="- `test_seed` covers: R-auth-401",
                        clause="  401 -> R-auth-401 { error: unauthenticated }"):
        """Task with a real test file, a §4 covers map, and a §3 fence carrying the clause."""
        self._mk_board()
        self._silent("new-task", slug, "--title", slug)
        rel = self._seed_task_test(slug)
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        fence = f"```\nPOST /things\n{clause}\n```"
        start = text.index("```")
        end = text.index("```", start + 3) + 3
        text = text[:start] + fence + text[end:]
        self.assertIn(TESTS_LINE, text, "template §4 line moved — update this suite")
        text = text.replace(TESTS_LINE, TESTS_LINE + "\n" + covers)
        p.write_text(text, encoding="utf-8")
        return rel


class ClauseMapTest(_ClauseHarness):
    def test_covers_maps_test_to_code(self):
        rel = self._mk_covered_task()
        out = self._silent("locate", f"{rel}::test_seed")
        self.assertIn("R-auth-401", out)

    def test_clause_line_quoted_from_frozen_s3(self):
        rel = self._mk_covered_task()
        out = self._silent("locate", f"{rel}::test_seed")
        self.assertIn("unauthenticated", out,
                      "the frozen §3 clause LINE is the answer, not just the key")

    def test_template_native_bullet_form_parses(self):
        # the template's own <test_plan> dialect: bare name, prose, `· covers:` tail
        rel = self._mk_covered_task(
            covers="- test_seed: arrange booking / act POST / assert 401 shape · covers: R-auth-401")
        out = self._silent("locate", f"{rel}::test_seed")
        self.assertIn("R-auth-401", out)
        self.assertIn("unauthenticated", out)

    def test_unfilled_template_placeholder_maps_nothing(self):
        # the scaffold's own `- test_<name>: … covers: <M#, R:code>` line must not
        # produce a phantom entry
        rel = self._mk_covered_task(
            covers="- test_<name>: arrange / act / assert behavior not internals · covers: <M#, R:code>")
        out = self._silent("locate", f"{rel}::test_seed")
        self.assertIn("no covers", out)

    def test_multiple_codes_all_resolved(self):
        rel = self._mk_covered_task(
            covers="- `test_seed` covers: R-auth-401, R-shape",
            clause="  401 -> R-auth-401 · body shape R-shape { }")
        out = self._silent("locate", f"{rel}::test_seed")
        self.assertIn("R-auth-401", out)
        self.assertIn("R-shape", out)

    def test_code_missing_from_s3_reported_honestly(self):
        rel = self._mk_covered_task(covers="- `test_seed` covers: R-ghost",
                                    clause="  401 -> { error }")
        out = self._silent("locate", f"{rel}::test_seed")
        self.assertIn("R-ghost", out)
        self.assertIn("not literal", out, "never guess a clause — say the key isn't in §3")

    def test_no_covers_entry_is_an_advisory_nudge(self):
        rel = self._mk_covered_task()
        out, code = self._run("locate", f"{rel}::test_unmapped")
        self.assertEqual(code, 0, "a missing covers entry is a nudge, not an error")
        self.assertIn("covers", out)
        self.assertIn("test_unmapped", out)


class ModeFloorsTest(_ClauseHarness):
    def test_plain_path_mode_unchanged(self):
        rel = self._mk_covered_task()
        out = self._silent("locate", rel)
        self.assertIn("owner", out)
        self.assertIn("in-node", out)

    def test_unowned_stays_unowned_with_test_name(self):
        self._mk_board()
        self._silent("new-task", "api-core", "--title", "API")
        out, code = self._run("locate", "tests/test_foreign.py::test_x")
        self.assertEqual(code, 0)
        self.assertIn("unowned", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
