"""property — one invariant over generated inputs; the seed is the reproducer.
usage: python3 property_check.py <junit.xml> [seed]   (run from the repo root; adapt Ledger to your port)
"""
import random, sys, xml.etree.ElementTree as ET; sys.path.insert(0, ".")          # a property: one invariant over generated inputs
from ledger import Ledger                                 # the PORT the acceptance checks also use
SEED, N, fails = int(sys.argv[2]) if len(sys.argv) > 2 else 2026, 500, []
rng = random.Random(SEED)
for i in range(N):                                        # invalid amounts included on purpose
    l = Ledger({"A": rng.randint(0, 1000), "B": rng.randint(0, 1000)}); before = l.total()
    l.transfer("A", "B", rng.randint(-50, 1500))
    if l.total() != before: fails.append(f"seed={SEED} case={i}: {before} -> {l.total()}")   # the reproducer
suite = ET.Element("testsuite", name="checks.props", tests="1")
tc = ET.SubElement(suite, "testcase", classname="checks.props", name="test_balance_is_conserved")
if fails: ET.SubElement(tc, "failure", message=fails[0]).text = "\n".join(fails[:5])
ET.ElementTree(suite).write(sys.argv[1]); sys.exit(1 if fails else 0)
