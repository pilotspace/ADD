# ADD 3.0 — pre-registered eval task set (D-10)

Frozen before the first run. Shared by every M4 arm so they drive the **same** work:
`v8` (2.5 census), `v0'` (unwrapped drive), `v4` (scope regime), `v9` (time-to-first-edit).

**Fixture:** `eval/fixture/` — a tiny Python library (`src/calc.py` + `tests/test_calc.py`)
placed in a fresh git repo per run. Small on purpose: the census must measure ceremony, not the
difficulty of the change.

| id | lane | request | touches |
|----|------|---------|---------|
| Q1 | quick | Add a one-line module docstring to `src/calc.py` | `src/calc.py` |
| S1 | standard | Add `mul(a, b)` returning the product, with a covering test | `src/calc.py`, `tests/test_calc.py` |
| S2 | standard | Add `sub(a, b)` with a test; the test also proves `add` is unchanged | `src/calc.py`, `tests/test_calc.py` |
| D1 | deep | Make `add()` raise `TypeError` on non-numbers, preserving the numeric contract | `src/calc.py`, `tests/test_calc.py` |

## Run rules (from PROPOSAL v6 §2)

- **Same model** on both arms; the 2.5 arm runs `prompt_wrapper = "raw"` (S6).
- **n ≥ 5** on `v0'`; the verdict reports the **no-orient-sentence** arm (no arm-shopping).
- **Per-lane cost bars**: quick / standard / deep each measured against the 2.5 baseline
  separately — the small-change class is never hidden inside an aggregate (S8).
- Counted per lane: engine calls · turns · tokens · human approvals · **is every gate's receipt
  covers-bound?**
