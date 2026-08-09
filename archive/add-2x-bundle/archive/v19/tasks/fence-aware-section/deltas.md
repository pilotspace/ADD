# Competency Deltas — fence-aware-section

status: open  evidence: v19 wave 1 worker B run 2026-06-08

- TDD · the fence-aware terminator scan proves that a single-source stdlib module
  is the correct fix for a class of fence-blind idioms duplicated across four files;
  the prior workaround (### headings in templates) was a convention-by-memory leak.

- ADD · heading-inclusion assumption (§1 ⚠) confirmed harmless: all four importers
  use assertIn / line-prefix counting; one extra heading line cannot flip a verdict.
  The `or None` pattern in test_review_checklist preserves the str|None contract
  without any strip — clean delegation boundary.

- SDD · import style in test files matters when local variables shadow import names:
  `import md_section` (module reference) is safer than `from md_section import section`
  when the importing file has a local variable also named `section`.
