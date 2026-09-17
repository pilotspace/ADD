"""Census of what the ADD loop actually cost, derived from stamps a bundle already carries.

Read-only, zero engine bytes, outside the notary. It answers two measurement questions that
were being argued from intuition:

* **G8 — interview friction.** Before redesigning the human-floor interview, measure it. How
  many decisions does an interview actually put to a human, and how many of those answers
  change anything?
* **S3 — verification yield.** At what floor and change class does an independent refute pay
  for its context cost? Derived per verify cycle from the refute and gate stamps.

Both are a CENSUS, never a score. `.add/tasks/method-health.md` already recorded why: a
count that grades teaches pre-flighting, and the thing being measured starts optimising for
the meter instead of the work. Nothing here is read by the engine and nothing gates on it.

It parses through `add.scan`/`add.read` rather than re-reading frontmatter itself. A census of
stamp readers that adds a stamp reader would be its own counterexample.

    python3 benchmark/census.py            # both censuses, against ./.add
    python3 benchmark/census.py --bundle X # another bundle root
    python3 benchmark/census.py --json     # machine-readable
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "add-method" / "tooling"))
import add  # noqa: E402


# What this instrument CANNOT see, stated up front so a reader does not infer it from silence.
NOT_DERIVABLE = [
    "human minutes — no stamp records wall time at a gate",
    "agent tokens — the notary records no cost field",
    "first-ask-to-seal latency — stamps carry a DAY, so same-day interview and freeze are "
    "indistinguishable; append order gives sequence, never duration",
    "escaped-defect yield — requires `--escape` deltas to exist and be traced to a cycle",
]


def _stamps(fm):
    return [s for s in (fm or {}).get("verified") or [] if isinstance(s, dict)]


def interview_census(graph):
    """G8 — every interview stamp, its item count and its verdict mix.

    `answers:` is the compiled `C1=confirm|C2=correct|...` string the interview writer records.
    An item whose verdict is unparseable is counted as `malformed` rather than dropped: a
    census that silently discards what it cannot read reports a cleaner bundle than exists.
    """
    rows, totals = [], Counter()
    for cid in sorted(graph):
        fm = graph[cid]["fm"] or {}
        for stamp in _stamps(fm):
            if stamp.get("act") != "interview":
                continue
            verdicts = Counter()
            for item in str(stamp.get("answers") or "").split("|"):
                item = item.strip()
                if not item:
                    continue
                verdicts[item.split("=", 1)[1].strip() if "=" in item else "malformed"] += 1
            rows.append({
                "node": cid,
                "at": str(stamp.get("at") or ""),
                "by": str(stamp.get("by") or ""),
                "items": sum(verdicts.values()),
                "verdicts": dict(sorted(verdicts.items())),
            })
            totals.update(verdicts)
    rows.sort(key=lambda r: (-r["items"], r["node"]))
    return {"interviews": rows, "totals": dict(sorted(totals.items())),
            "items": sum(totals.values())}


def verify_census(graph):
    """S3 — one row per verify cycle: the floor it ran at, the refutes it drew, its verdict.

    A cycle is a gate stamp plus the refute stamps that precede it since the previous gate.
    Refutes with no following gate are reported as an open cycle rather than attached to the
    last closed one — an unresolved challenge is exactly the thing a yield question is about.
    """
    rows = []
    for cid in sorted(graph):
        fm = graph[cid]["fm"] or {}
        if fm.get("type") != "Task":
            continue
        pending, seq = [], 0
        for stamp in _stamps(fm):
            act = stamp.get("act")
            if act == "refute":
                pending.append(stamp)
            elif act == "gate":
                seq += 1
                rows.append(_cycle(cid, fm, seq, pending, stamp))
                pending = []
        if pending:
            rows.append(_cycle(cid, fm, seq + 1, pending, None))
    return {"cycles": rows, "by_tier": _yield_by(rows, "tier"),
            "by_authority": _yield_by(rows, "authority")}


def _cycle(cid, fm, seq, refutes, gate):
    return {
        "node": cid,
        "kind": str(fm.get("kind") or ""),
        "cycle": seq,
        "authority": str((gate or {}).get("authority")
                         or next((r.get("authority") for r in refutes), "") or ""),
        "tier": sorted({str(r.get("tier") or "T?") for r in refutes}) or [],
        "refutes": len(refutes),
        "probes": sum(int(r["probes"]) for r in refutes
                      if str(r.get("probes") or "").isdigit()),
        "refuted": sum(1 for r in refutes if str(r.get("outcome")) == "refuted"),
        "held": sum(1 for r in refutes if str(r.get("outcome")) == "held"),
        "gate": str((gate or {}).get("outcome") or "OPEN"),
    }


def _yield_by(rows, key):
    """Refute yield grouped by a cycle field — the `does T2 pay for itself here?` view."""
    buckets = {}
    for row in rows:
        values = row[key] if isinstance(row[key], list) else [row[key] or "none"]
        for value in values or ["none"]:
            bucket = buckets.setdefault(value, Counter())
            bucket["cycles"] += 1
            bucket["refutes"] += row["refutes"]
            bucket["probes"] += row["probes"]
            bucket["refuted"] += row["refuted"]
            bucket["held"] += row["held"]
    return {k: dict(v) for k, v in sorted(buckets.items())}


def render(interviews, verifies):
    out = ["INTERVIEW CENSUS (G8) — a census, never a score",
           f"  {len(interviews['interviews'])} interviews · {interviews['items']} items · "
           + " · ".join(f"{n} {v}" for v, n in interviews["totals"].items())]
    for row in interviews["interviews"]:
        mix = " ".join(f"{v}={n}" for v, n in row["verdicts"].items())
        out.append(f"    {row['items']:>3} items  {row['node']:<44} {row['at']}  {mix}")

    cycles = verifies["cycles"]
    challenged = [c for c in cycles if c["refutes"]]
    out += ["", "VERIFY CENSUS (S3)",
            f"  {len(cycles)} cycles · {len(challenged)} carried a refute · "
            f"{sum(c['refutes'] for c in cycles)} refutes · "
            f"{sum(c['probes'] for c in cycles)} probes · "
            f"{sum(c['refuted'] for c in cycles)} refuted / "
            f"{sum(c['held'] for c in cycles)} held"]
    for key, label in (("by_tier", "tier"), ("by_authority", "authority")):
        out.append(f"  yield by {label}:")
        for value, stats in verifies[key].items():
            out.append(f"    {value:<10} cycles={stats['cycles']:<4} "
                       f"refutes={stats['refutes']:<4} probes={stats['probes']:<6} "
                       f"refuted={stats['refuted']:<4} held={stats['held']}")

    out += ["", "NOT DERIVABLE FROM STAMPS — do not infer these from the numbers above:"]
    out += [f"  · {line}" for line in NOT_DERIVABLE]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bundle", default=str(REPO), help="repo root holding .add/ (default: this repo)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    graph = add.scan(Path(args.bundle))
    interviews, verifies = interview_census(graph), verify_census(graph)
    if args.json:
        print(json.dumps({"interview": interviews, "verify": verifies,
                          "not_derivable": NOT_DERIVABLE}, indent=2))
    else:
        print(render(interviews, verifies))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
