# Deterministic rescore progression — 2026-07-23

Every existing run under benchmark/runs/ re-scored with the frozen-checklist
requirement_coverage meter (no LLM in the path; judge annotation 'unavailable').
Stale artifact paths (post-move archived roots) mechanically repaired first.

| run | requirement_coverage | oracle_pass_rate | regression_rate | repaired |
|---|---|---|---|---|
| advancefold-r0/add/wm1 | 1.0 | 1.0 | 0.0 | - |
| advancefold-r1/add/wm1 | 1.0 | 1.0 | 0.0 | - |
| baseline-round3/add/wm1 | 1.0 | 1.0 | 0.0 | workspace,oracle_report,transcript |
| baseline-round3/add/wm2 | 0.2 | 0.2 | 1.0 | workspace,oracle_report,transcript |
| baseline-round3/add/wm3 | 0.0 | 0.0 | 0.8571428571428571 | workspace,oracle_report,transcript |
| baseline-round3/spec-kit/wm1 | 1.0 | 1.0 | 0.0 | workspace,oracle_report,transcript |
| baseline-round3/spec-kit/wm2 | 0.2 | 0.2 | 1.0 | workspace,oracle_report,transcript |
| baseline-round3/spec-kit/wm3 | 0.25 | 0.5 | 0.42857142857142855 | workspace,oracle_report,transcript |
| enforced-r1/add/wm1 | 0.9166666666666666 | 0.8 | 0.0 | workspace,oracle_report,transcript |
| enforced-r1/add/wm2 | 0.2 | 0.2 | 1.0 | workspace,oracle_report,transcript |
| enforced-r1/add/wm3 | 0.0 | 0.0 | 1.0 | workspace,oracle_report,transcript |
| hint-r1/add/wm1 | 1.0 | 1.0 | 0.0 | workspace,oracle_report,transcript |
| lean-r1/add/wm1 | 0.08333333333333333 | 0.0 | 0.0 | workspace,oracle_report,transcript |
| lean-r1/add/wm2 | 1.0 | 1.0 | 0.0 | workspace,oracle_report,transcript |
| lean-r1/add/wm3 | 0.0 | 0.0 | 1.0 | workspace,oracle_report,transcript |
| lean-r2/add/wm1 | 1.0 | 1.0 | 0.0 | workspace,oracle_report,transcript |
| lean-r2/add/wm2 | 0.2 | 0.2 | 1.0 | workspace,oracle_report,transcript |
| lean-r2/add/wm3 | 0.0 | 0.0 | 1.0 | workspace,oracle_report,transcript |
| lean-r3/add/wm1 | 1.0 | 1.0 | 0.0 | workspace,oracle_report,transcript |
| lean-r3/add/wm2 | 0.2 | 0.2 | 1.0 | workspace,oracle_report,transcript |
| lean-r3/add/wm3 | 0.0 | 0.0 | 0.8571428571428571 | workspace,oracle_report,transcript |
| leanconfirm-r0/add/wm1 | 1.0 | 1.0 | 0.0 | - |
| seeded-r1/add/wm1 | 0.9166666666666666 | 0.8 | 0.0 | workspace,oracle_report,transcript |
| seeded-r1/add/wm2 | 0.2 | 0.2 | 1.0 | workspace,oracle_report,transcript |
| seeded-r1/add/wm3 | 0.0 | 0.0 | 0.8571428571428571 | workspace,oracle_report,transcript |

re-scored: 25 · un-re-scorable: 0
