#!/usr/bin/env python3
"""Guard: publish.yml's npm job uses npm Trusted Publishing (OIDC), not a long-lived token.

TODO #23 — migrate @pilotspace/add publishing from a stored NPM_TOKEN + `--provenance`
to npm Trusted Publishing (OIDC), the current best practice. Trusted publishing:
  - needs `id-token: write` (OIDC) and NO NODE_AUTH_TOKEN / NPM_TOKEN secret,
  - requires npm CLI >= 11.5.1 (so Node >= 24 + an explicit npm@latest bump — even
    Node 24.0 ships npm 11.3, below the floor),
  - generates provenance automatically (the `--provenance` flag is no longer needed).
The one-time npmjs.com trusted-publisher registration (org/repo/workflow) is a human
step; this test only locks the workflow shape so a future edit can't silently
re-introduce the token path.

Run: python3 -m unittest test_publish_provenance -v
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PUBLISH_YML = REPO / ".github" / "workflows" / "publish.yml"


def _npm_job(text: str) -> str:
    """The npm job body — from the `npm:` job header to the next top-level job."""
    start = re.search(r"(?m)^  npm:\s*$", text)
    assert start, "publish.yml has no `npm:` job"
    rest = text[start.end():]
    nxt = re.search(r"(?m)^  \w+:\s*$", rest)  # next 2-space-indented job key
    return rest[: nxt.start()] if nxt else rest


class TrustedPublishingShapeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PUBLISH_YML.read_text(encoding="utf-8")
        cls.npm = _npm_job(cls.text)

    def test_no_stored_npm_token(self):
        # the whole point of trusted publishing: no long-lived token to store/rotate
        for tok in ("NODE_AUTH_TOKEN", "NPM_TOKEN", "secrets.NPM_TOKEN"):
            self.assertNotIn(tok, self.text,
                             f"trusted publishing must not reference {tok}")

    def test_npm_job_has_oidc_permission(self):
        self.assertIn("id-token: write", self.npm,
                      "the npm job needs id-token: write for OIDC trusted publishing")

    def test_node_24_or_newer(self):
        # npm 11.5.1+ (trusted-publishing floor) ships with Node 24+
        m = re.search(r"node-version:\s*'?(\d+)", self.npm)
        self.assertIsNotNone(m, "npm job must pin a node-version")
        self.assertGreaterEqual(int(m.group(1)), 24,
                                "trusted publishing needs Node >= 24 (npm 11.5.1+)")

    def test_explicit_npm_floor_bump(self):
        # Node 24.0 ships npm 11.3 < 11.5.1 — bump explicitly, don't rely on the bundle
        self.assertTrue(
            re.search(r"npm (install|i) -g npm@", self.npm),
            "npm job must upgrade the npm CLI (npm install -g npm@latest) to reach >= 11.5.1")

    def test_publish_command_present_without_provenance_flag(self):
        self.assertIn("npm publish", self.npm, "the npm job must run `npm publish`")
        # provenance is automatic under trusted publishing — the flag is redundant
        self.assertNotIn("--provenance", self.npm,
                         "drop --provenance: trusted publishing generates it automatically")

    def test_setup_documents_trusted_publisher(self):
        # the one-time human npmjs.com step must be documented in the workflow header
        low = self.text.lower()
        self.assertIn("trusted publish", low,
                      "publish.yml header must document the trusted-publisher setup")


if __name__ == "__main__":
    unittest.main(verbosity=2)
