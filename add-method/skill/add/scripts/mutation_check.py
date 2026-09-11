"""mutation on changed code — mutants ONLY in files the last commit touched inside <scope>; the score is frozen.
usage: python3 mutation_check.py <junit.xml> <min-score> <scope> <test cmd...>   e.g. r.xml 0.8 src pytest -q
"""
import re, subprocess, sys, xml.etree.ElementTree as ET   # mutants ONLY in changed files inside scope; N is frozen
junit, minimum, scope, cmd = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4:]   # r.xml 0.8 src pytest -q
changed = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "--", scope], capture_output=True, text=True).stdout.split()
SWAPS, killed, total = [(" + ", " - "), ("<=", "<"), ("==", "!="), (" and ", " or ")], 0, 0
for path in changed:
    src = open(path).read()
    for a, b in SWAPS:
        for m in re.finditer(re.escape(a), src):
            open(path, "w").write(src[:m.start()] + b + src[m.end():]); total += 1
            killed += subprocess.run(cmd, capture_output=True).returncode != 0; open(path, "w").write(src)
score = killed / total if total else 1.0                  # no mutant to kill is not a failure of the suite
suite = ET.Element("testsuite", name="checks.mutation", tests="1")
tc = ET.SubElement(suite, "testcase", classname="checks.mutation", name="test_mutation_score_changed_code")
if score < minimum: ET.SubElement(tc, "failure", message=f"{killed}/{total} mutants killed = {score:.2f} < {minimum}")
ET.ElementTree(suite).write(junit); sys.exit(0 if score >= minimum else 1)
