"""contract — the consumer's pact, verified against the provider. Only what the consumer depends on.
usage: python3 contract_check.py <junit.xml>   (run from the repo root; adapt handle() to your provider)
"""
import json, sys, xml.etree.ElementTree as ET; sys.path.insert(0, ".")            # the consumer's pact, verified against the provider
from api import handle                                    # provider entry: handle(method, path, body) -> (status, body)
pact = json.load(open("pact.json")); suite = ET.Element("testsuite", name="checks.pact"); bad = 0
for ix in pact["interactions"]:                          # only what the consumer actually depends on
    status, body = handle(ix["request"]["method"], ix["request"]["path"], ix["request"].get("body"))
    want = ix["response"]; miss = [k for k, t in want["body"].items() if type(body.get(k)).__name__ != t]
    tc = ET.SubElement(suite, "testcase", classname="checks.pact", name="test_" + ix["name"])
    if status != want["status"] or miss:
        bad += 1; ET.SubElement(tc, "failure", message=f"status {status} want {want['status']}; type drift {miss}")
suite.set("tests", str(len(pact["interactions"]))); ET.ElementTree(suite).write(sys.argv[1]); sys.exit(1 if bad else 0)
