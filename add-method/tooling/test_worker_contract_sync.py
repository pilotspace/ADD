"""worker-contract-sync (method-ergonomics): the 5 roster agents hold one worker-contract floor.

CONTRACT — a drift GUARD, not a dedup (the deeper stanza dedup was deliberately DECLINED:
self-contained agent prompts are an invariant). What must hold, per agent, in BOTH trees
(`add-method/agents/` and `.claude/agents/` — agents are NOT a bundled tree):
  1. two-tree byte parity per agent (a stanza edit in one tree must not drift silently);
  2. the Boundary stanza exists with all three floor markers — MAY: · MUST NOT: ·
     STOP-and-escalate — and names the security HARD-STOP;
  3. the orchestrator-records invariant: the agent never runs add.py and never writes
     shared state (it proposes; the orchestrator records);
  4. the Return stanza exists and its structured verdict carries `persona` and
     `confidence` (the streams.md worker-contract disclosure shape).
Red-for-the-right-reason was proven by mutation (a one-byte stanza edit in one tree
turns parity red; removing a floor marker turns the census red).
Run: python3 -m unittest test_worker_contract_sync -v
"""
import hashlib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
AGENTS = ("add-advisor", "add-build", "add-design", "add-persona", "add-verify")
TREES = (ADD_METHOD / "agents", REPO / ".claude" / "agents")

BOUNDARY = "## Boundary (the irreducible floor)"
RETURN = "## Return (disclose progress)"


def _canon(name: str) -> str:
    return (TREES[0] / f"{name}.md").read_text(encoding="utf-8")


class WorkerContractSyncTest(unittest.TestCase):
    def test_two_tree_parity(self):                            # scenario 1
        for name in AGENTS:
            digests = {hashlib.md5((tree / f"{name}.md").read_bytes()).hexdigest()
                       for tree in TREES}
            self.assertEqual(len(digests), 1, f"{name}.md drifted between agents/ trees")

    def test_boundary_floor_markers(self):                     # scenario 2
        for name in AGENTS:
            text = _canon(name)
            self.assertIn(BOUNDARY, text, f"{name} misses the Boundary stanza")
            stanza = text.split(BOUNDARY, 1)[1].split("##", 1)[0]
            for marker in ("MAY:", "MUST NOT:", "STOP-and-escalate"):
                self.assertIn(marker, stanza, f"{name} Boundary misses '{marker}'")

    def test_security_floor_named(self):                       # scenario 3
        for name in AGENTS:
            self.assertIn("HARD-STOP", _canon(name),
                          f"{name} must name the security HARD-STOP floor")

    def test_orchestrator_records_invariant(self):             # scenario 4
        for name in AGENTS:
            text = _canon(name)
            self.assertIn("never run add.py", text,
                          f"{name} must state it never runs add.py")
            self.assertIn("shared state", text,
                          f"{name} must state it never writes shared state")

    def test_return_discloses_persona_and_confidence(self):    # scenario 5
        for name in AGENTS:
            text = _canon(name)
            self.assertIn(RETURN, text, f"{name} misses the Return stanza")
            stanza = text.split(RETURN, 1)[1]
            self.assertIn("persona", stanza, f"{name} Return misses the persona key")
            self.assertIn("confidence", stanza, f"{name} Return misses the confidence key")


if __name__ == "__main__":
    unittest.main()
