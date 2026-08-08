# Deltas: shared-engine-pin

status: closed  task: shared-engine-pin  date: 2026-06-08

- ADD: single-source constants in a dedicated pin module reduce multi-file amendment cost from N edits to 1; the full-suite stale-guard sweep shrinks accordingly  evidence: test_sweep_no_second_pin guards against regression
- TDD: sweeping ALL tooling .py files (not just test files) prevents a pin hiding in a helper module — scope of sweep must match scope of trust  evidence: _PIN_ASSIGN regex over glob("*.py"), excluding only engine_pin.py
- TDD: cwd-independent import must be proven by subprocess, not assumed from same-cwd runs — the full-suite runner injects tooling dir on sys.path and runs from elsewhere  evidence: test_pin_importable_from_any_cwd closes assumption flag with subprocess proof
