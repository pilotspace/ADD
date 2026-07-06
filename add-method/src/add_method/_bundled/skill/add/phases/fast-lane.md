# Fast lane — less ceremony, same floor

The fast lane is the **collapsed, opt-in task path for small work**. Same flow — ground → specify →
contract → tests → build → verify — with fewer sections and the bundle approved in one pass. It
**collapses** the ceremony; it never drops the floor. The human opts in (`--fast`); the engine never
guesses that a task is small.

## When

Pick it for a **small, low-risk, roughly single-file change**. Stay on the full lane when the work
wants its scenarios enumerated — a milestone or release, an architecture or security change, anything
cross-cutting, or anything you are not yet sure is small. In doubt, run the full lane.

## How

1. `add.py new-task <slug> --fast` scaffolds the minimal `TASK.fast.md` (sections {0,1,3,4,5,6};
   §2 SCENARIOS and §7 OBSERVE dropped — §1's Accept line carries the behavior a scenario would).
2. Ground, draft §1 + §3, and **freeze the contract as one batched approval** — the single decision
   point, led by the lowest-confidence flag.
3. Write a **red** test (§4), run it failing for the right reason.
4. Build (§5) to green, then record the **verify gate** (§6).

Both human gates (freeze, verify) render `report-template.md` too — the fast lane collapses
sections, never the report.

## Floor kept, only collapsed

Three things never move, on either lane: a **frozen** §3 before build · a **red** test before build ·
a recorded **verify gate** at the end (a security finding is always HARD-STOP). A `--fast` task is
freeze-gated under ANY milestone — `advance` refuses `contract_not_frozen` while §3 is a draft. Speed
comes from **fewer sections + auto-gating**, not from cutting any of the three.

Not a way around the contract, the red test, or the gate; not for milestones or releases; not
engine-chosen — ceremony is human-owned.
