# TASK: Persona seed nudge at new-milestone

slug: persona-seed-nudge · created: 2026-07-04 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - add-method/tooling/add.py:cmd_new_milestone — creates `.add/milestones/<slug>/MILESTONE.md`, prints the existing warn-never-block idiom (`note: slug '<slug>' looks like a bare version …`), ends with `print(_next_footer(root, state))`.
  - add-method/tooling/add.py:_next_footer — the single shared "next:" resolver every completing mutating verb prints; NOT a nudge site per se, but the pattern (`note:` before `next:`) is what the new hint mirrors.
  - add-method/tooling/add_engine/constants.py:SETUP_FILES — `("PROJECT.md", …, "personas/_template.md")`; the persona scaffold is written ONLY at `cmd_init` (survivor never-clobber), never backfilled by any later verb.
  - add-method/tooling/add.py:cmd_check (~L2913-2932) — the existing persona census: iterates `.add/personas/*.md`, WARNs on `persona_slug_invalid` / `persona_schema_incomplete`, INFOs `schema-conformant`; says nothing when the directory is absent or has no real (non-template) persona.
  - add-method/tooling/add_engine/predicates.py:_persona_missing, _persona_slug_valid — the presence-based schema validators `cmd_check` and the tests already call.
  - add-method/agents/add-persona.md — the existing cross-cutting service (`add-persona` subagent) whose entire job is "select the best-fit existing persona or draft a NEW one when none fits"; the nudge should POINT here, not invent a second mechanism.
  - add-method/docs/18-personas.md — "Seed — at setup": personas are meant to be proposed at project setup from PROJECT.md's domain; explicitly states "a project with no personas behaves exactly as before" (opt-in/additive — the fix must stay a non-blocking note, never a gate).
  - add-method/tooling/test_persona_setup.py — existing red/green coverage for the seed-at-init path (SeedTest, PredicateTest, ParityAndDocTest classes); a new test class for the new-milestone nudge belongs alongside these, same file or a sibling `test_persona_milestone_nudge.py`.
  - ENGINE_TREES parity (test_persona_setup.py:25-29): `.add/tooling`, `add-method/tooling` (package root), `add-method/src/add_method/_bundled/tooling` — any add.py behavior change must land byte-identical across all three, plus the `.add/tooling` dogfood copy in THIS repo.

Context (working folder): docs/18-personas.md (persona-loop doc, cited above); no config/data touched.

Honors (patterns / conventions):
  - warn-never-block idiom: `cmd_new_task`'s "note: '<slug>' is not attached to a milestone …" and `cmd_new_milestone`'s bare-version-slug note — both print, never `_die`, and never gate. The new persona hint must follow this exact shape.
  - docs/18-personas.md's non-negotiable: "a persona never lowers a gate" / "a project with no personas behaves exactly as before" — the hint is purely additive stdout, no state.json field, no new gate outcome.
  - NO-EXEC: the persona seed/validate path must never reach the network or spawn a process (test_persona_setup.py:FORBIDDEN_EXEC / test_engine_no_exec_on_persona_paths) — the new check is a pure directory/glob read, so this holds trivially, but must not regress it.

Anchors the contract cites: `cmd_new_milestone` (add-method/tooling/add.py), a new predicate `_personas_unseeded(root) -> bool` (or equivalent) in add_engine/predicates.py, `.add/personas/` directory + `.add/personas/_template.md` (SETUP_FILES scaffold), `.add/personas-teacher/` (read-off-build source the hint points at), `add-persona` agent (add-method/agents/add-persona.md).

Issues/Risks (→ feed §1):
  - Discriminated in the field: ai-proxy's worktree `.add/personas/` is entirely ABSENT (confirmed via `ls`), not merely empty — the project predates the persona-loop feature and `add.py update` (the Node.js installer's managed-layer reconciler) deliberately never touches project-scoped SETUP_FILES seeds (only the vendored `personas-teacher/` library, which it correctly restored). So there is currently NO path — automatic or hinted — that backfills a pre-existing project.
  - Must not double-fire: if the hint also fires on every `new-task`, a milestone immediately followed by its first task would print the same note twice in one flow — advisor + design decision: nudge ONLY at `new-milestone` (the natural domain-sized granularity), not `new-task`/`advance`/`_next_footer`.
  - A "personas dir exists but contains ONLY `_template.md`" project (fresh `init`, never authored) must trip the same hint as a fully-absent dir — the predicate must check for a REAL persona (any `.md` file other than `_template.md`), not just directory presence.
  - `check`'s existing persona census (cmd_check ~L2913) is a natural second surface for visibility (an INFO-level line, same measure-not-block posture) — cheap to add alongside the new-milestone nudge without inventing new state.

Related intent: `.add/docs/18-personas.md` (persona-learning-loop chapter) — "Seed — at setup" describes ONLY the first-task path; this task closes the gap for a project that adopts/updates into the feature after setup already happened. Originating request: user-reported gap surfaced from the `ai-proxy` project's session history (worktree `batch-cache`), where `add.py update` restored the vendored `.add/personas-teacher/` library but no project-fit `.add/personas/` was ever seeded or hinted at across ~20 milestones of history.

Ground SHA: b3df693

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> **v2 amendment (2026-07-04, change request against the FROZEN v1 below)** — Tin: "not just draft
> one that fits this milestone's domain, AI need create missed persona for whole project and new
> milestone if missed." v1 scoped the hint to "no real persona at all", worded around "this
> milestone's domain"; v2 keeps the same predicate/scope (docs/18-personas.md still reserves
> content-fit judgment for the AI, never the engine) but (a) rewords the hint to be PROJECT-scoped,
> not milestone-scoped, (b) adds `add.py status` — the first command the `/add` skill runs every
> session — as a THIRD surface (previously only `new-milestone`/`check` fired), and (c)
> single-sources the wording as one `PERSONA_HINT` constant so it cannot drift across surfaces.
> Confirmed direction: user selected "Reword hint + strengthen skill instructions" over
> AskUserQuestion; the follow-up scope-confirmation question timed out twice, so this amendment
> proceeded on that already-given direction per the advisor's read (see Assumptions below). Two
> live follow-ups then resolved the remaining open questions: (1) "are this include hint in each
> step to create missed personas for each milestone/task?" — answered: no, `new-task` deliberately
> stays silent (v1's own anti-double-fire rejection); `status`'s every-session read covers "each
> step" better than a dedicated per-task print would. (2) "no, but add hint in setup.md step then
> draft all" — this REPLACES the earlier SKILL.md "Beyond the bundle" plan: the action instruction
> lives in `phases/0-setup.md`'s existing persona-seeding bullet instead, routing the engine's hint
> back to that step with an explicit "draft every missing project persona" instruction — see §3.

Feature: a non-blocking hint — `note:` at `add.py new-milestone`, an INFO line at `add.py check`, and a `persona :` orientation line at `add.py status` (every session, self-clearing once seeded) — when a project has NO real project-fit persona under `.add/personas/`, pointing at the `add-persona` agent / docs/18-personas.md so the AI seeds the project's persona(s) from `PROJECT.md`'s domain, not just a single milestone-fit one.
Framings weighed: nudge at `new-milestone` only (v1 choice — kept, still the natural domain-sized creation event) · **v2 adds `status` as a third surface** (chosen — `status` is the one command every session is guaranteed to run per the `add` skill's own "Always start here" orientation step, so it is the highest-leverage place to catch a project that never ran `new-milestone` again after the gap was introduced) · folding the hint into `status --json` too (rejected — that branch is a machine-readable contract other tooling may parse; a human-readable-only line avoids widening it) · teaching the ENGINE to judge domain-fit and auto-draft (rejected, same as v1 — NO-EXEC + content-quality judgment stays the AI's job via `add-persona`) · nudge at every `new-task` too (rejected, same as v1 — double-fires).
Must:
<must>
  - M1: `add.py new-milestone <slug>` prints a `note:` line when `.add/personas/` is absent OR contains no `.md` file other than `_template.md` (i.e. no REAL, authored persona) — printed after the existing "created milestone…"/"active milestone set." lines and before the `_next_footer` `next:` line.
  - M2: the note names the concrete fix path — spawn/consult the `add-persona` agent, or read `docs/18-personas.md` — never a vague "consider personas" placeholder.
  - M3: a project that already has ≥1 real persona under `.add/personas/` gets byte-identical `new-milestone` output to today (no note) — no regression for an already-seeded project.
  - M4: `add.py check` gains one additional INFO-level line, `("personas", "unseeded — …")`, under the same measure-not-block posture as the existing per-persona census, when the same "no real persona" predicate is true; exit code stays 0.
  - M5: the underlying predicate (`_personas_unseeded` or equivalent) is a single pure, NO-EXEC function (directory/glob read only) shared by `cmd_new_milestone`, `cmd_check`, and `cmd_status` — not duplicated logic.
  - M6: the change lands byte-identical across all engine trees (`add-method/tooling`, `.add/tooling`, `add-method/src/add_method/_bundled/tooling`) per the existing ENGINE_TREES parity convention.
  - M7 (v2): `add.py status` prints a `persona : …` line (grouped with the existing `context`/`voice` orientation pointers) when `_personas_unseeded` is true; silent once ≥1 real persona exists; the `--json` branch is UNCHANGED (no new key) — human-readable orientation only.
  - M8 (v2): the hint text is single-sourced as ONE constant (`PERSONA_HINT` in `add_engine/constants.py`); all three call sites (`new-milestone`/`check`/`status`) reference it — no per-surface literal duplication, so a future reword touches one place.
  - M9 (v2): the hint's wording is project-scoped — it must NOT say "this milestone's domain" or otherwise imply the fix is milestone-specific; wording matches docs/18-personas.md's own "seed the project's persona(s) from PROJECT.md's domain" framing.
  - M10 (v2): `phases/0-setup.md`'s existing persona-seeding bullet gains a closing sentence routing the engine's hint back to this step — "draft every missing project persona, not just one" — so the orchestrator ACTS on the hint (spawns `add-persona`, catches up every missing role) instead of reading it as passive stdout; deliberately NOT a `new-task` call site (M1's own "double-fires" rejection still holds — confirmed live by the user: "no [not every task]").
</must>
Reject:
<reject>
  - R1: an unreadable/corrupt `.add/personas/*.md` file during the "is there a real persona" scan -> treated as "not a real persona" fail-soft (never crashes `new-milestone`/`check`/`status`), matching cmd_check's existing `except OSError` pattern around `_persona_missing` reads.
  - R2: the note/INFO/status line must never set a `state.json` field, never appear as a WARN, and never affect `add.py gate`/`add.py audit` outcomes -> "persona_hint_must_not_gate" (an engine test asserting `cmd_new_milestone`'s exit code / gate is unaffected).
  - R3 (v2): the `status --json` machine-readable branch must stay byte-identical (no `persona` key added anywhere in its output) -> the hint is a human-readable-only orientation surface, never a schema change other tooling could depend on.
</reject>
After:
<after>
  - A `new-milestone` run in a project with zero real personas prints its existing output plus one new `note:` line, then the unchanged `next:` footer.
  - A `new-milestone` run in a project with ≥1 real persona is byte-identical to pre-change output.
  - `add.py check` in a project with zero real personas prints one additional INFO line naming the gap and still exits 0.
  - `add.py status` (v2) in a project with zero real personas prints one additional `persona :` line every session; a project with ≥1 real persona is byte-identical to pre-change `status` output; `status --json` is untouched either way.
  - The three engine trees + the `.add/tooling` dogfood copy carry byte-identical source for the new predicate, the single-sourced `PERSONA_HINT` constant, and its three call sites.
  - `phases/0-setup.md` (3 skill trees) names the catch-up instruction; `new-task` remains untouched (confirmed live — no per-task print wanted).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ (v2, carried forward from v1's own flag) Scope is STILL "zero real personas at all" project-wide, not "the `add-persona` agent's own fit-judgment invoked automatically by the engine" — the user's "AI need create missed persona for whole project" is read as "the AI (orchestrator), prompted by this hint, should proactively spawn `add-persona` and catch up ALL missing project personas" — i.e. the CREATING is a skill-guide/orchestrator responsibility, not a new engine capability. This is the lowest-confidence point in the whole v2 bundle: if the user instead wanted the ENGINE itself to auto-draft personas, that would be a much larger, NO-EXEC-violating change this task deliberately does not make. If wrong: reopen as a v3 change request — the hint's routing to `add-persona` is unchanged either way, so today's fix does not need to be reverted, only extended.
  - [x] Whether to proceed on the timed-out scope-confirmation question — resolved by proceeding on the user's own already-given pick ("Reword hint + strengthen skill instructions (Recommended)") plus the advisor's read that direction was confirmed enough to draft, while still gating the actual freeze on this report.
  - [x] Whether the "act on this hint" instruction fires per new-task too — resolved live: "no" (not per-task; `status`'s every-session read plus `new-milestone`'s creation-time note stay the only two AI-facing prints; `new-task` stays silent, matching M1's original anti-double-fire rejection).
  - [x] Where the "act on this hint" instruction lives — resolved live: `phases/0-setup.md`'s existing persona-seeding bullet (not `SKILL.md`'s "Beyond the bundle"), so it reads as "return to this step" rather than a generic cue; costs a `test_skill_lean` "phases"-pool rebaseline (40931→41101, +170B) instead of the "core"-pool one originally proposed — DONE, not pending.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: nudge on a personas-less project   # M1, M2
  Given a project with no `.add/personas/` directory at all
  When the AI runs `add.py new-milestone <slug>`
  Then stdout includes a `note:` line naming the `add-persona` agent or docs/18-personas.md
  And the milestone is still created and the existing `next:` footer still prints unchanged

Scenario: nudge on a template-only project   # M1, M2
  Given a project whose `.add/personas/` contains only the seeded `_template.md`
  When the AI runs `add.py new-milestone <slug>`
  Then stdout includes the same `note:` line as the personas-less case

Scenario: no nudge once a real persona exists   # M3
  Given a project with `.add/personas/frontend.md` (a real, authored persona)
  When the AI runs `add.py new-milestone <slug>`
  Then stdout is byte-identical to the pre-change `new-milestone` output (no `note:` line)

Scenario: check surfaces the same gap   # M4
  Given a project with no `.add/personas/` directory
  When the AI runs `add.py check`
  Then stdout includes an INFO line naming "personas" as unseeded
  And the process exit code is 0

Scenario: unreadable persona file degrades fail-soft   # R1
  Given a project whose `.add/personas/` contains one `.md` file that raises OSError on read
  When the AI runs `add.py new-milestone <slug>`
  Then the command completes without raising, treating the unreadable file as "not a real persona"
  And the `note:` line is still printed (no crash, no half-created milestone)

Scenario: the nudge never touches gate state   # R2
  Given a project with no `.add/personas/` directory
  When the AI runs `add.py new-milestone <slug>`
  Then `state.json` gains no new field for the persona hint
  And the milestone's `status` field and the command's exit code are unaffected by the note

Scenario: status surfaces the gap every session   # M7 (v2)
  Given a project with no `.add/personas/` directory
  When the AI runs `add.py status`
  Then stdout includes a `persona :` line naming the `add-persona` agent or docs/18-personas.md
  And the line disappears once a real persona is seeded

Scenario: status --json stays untouched   # R3 (v2)
  Given a project with no `.add/personas/` directory
  When the AI runs `add.py status --json`
  Then the JSON output contains no "persona" key anywhere

Scenario: wording is single-sourced and project-scoped   # M8, M9 (v2)
  Given the three call sites in add.py
  When their source is inspected
  Then all three reference the same PERSONA_HINT constant
  And no call site's literal text contains "this milestone's domain"
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FILE CONTRACT (no HTTP surface — CLI stdout behavior only)

add_engine/constants.py — NEW single-sourced hint constant (v2):

  PERSONA_HINT = ("no project-fit persona seeded yet under .add/personas/ — spawn the add-persona "
                  "agent (or read docs/18-personas.md) to seed the project's persona(s) from "
                  "PROJECT.md's domain")

add_engine/io_state.py — the predicate (v1, unchanged; corrects v1's contract prose, which named
  the wrong file — the actual build placed it here, colocated with `_md5_file`'s fail-soft idiom):

  def _personas_unseeded(root: Path) -> bool:
      """True when `.add/personas/` has no REAL (non-template) authored persona:
      absent dir, empty dir, or a dir containing only `_template.md`. Fail-soft:
      an unreadable entry is treated as absent (never raises)."""
      d = root / "personas"
      if not d.is_dir():
          return True
      try:
          return not any(p.stem != "_template" for p in d.glob("*.md"))
      except OSError:
          return True

add.py:cmd_new_milestone — ONE call site (v1, reworded v2), immediately before
  `print(_next_footer(...))`:
  AFTER:   print("active milestone set." + ...)
           if _personas_unseeded(root):
               print(f"note: {PERSONA_HINT}")
           print(_next_footer(root, state))
  (the `--queued` arm's prints are UNCHANGED — the note fires only on the "active milestone set"
  arm, since a queued milestone isn't yet in flight)

add.py:cmd_check — ONE call site (v1, reworded v2), appended in the existing persona census block,
  after the per-file WARN/INFO loop, gated on the SAME predicate:
  AFTER:   if _personas_unseeded(root):
               infos.append(("personas", f"unseeded — {PERSONA_HINT}"))

add.py:cmd_status — ONE NEW call site (v2), grouped with the existing `context`/`voice` per-session
  orientation pointers (human-readable branch ONLY — the earlier `--json` branch above it in the
  function is untouched):
  AFTER:   if (root / "SOUL.md").exists():
               print("voice   : .add/SOUL.md  (...)")
           if _personas_unseeded(root):
               print(f"persona : {PERSONA_HINT}")
           # wave resume hint (existing, unchanged)

All three call sites are fail-soft (never raise) and additive-only (no existing line removed/
reordered, no state.json field added, no gate/exit-code change, `status --json` untouched) —
matching the existing `note:`/INFO idioms this task extends rather than replaces.

  4xx -> { error: "persona_hint_must_not_gate" }   # test-only marker: asserts new-milestone's
                                                     # exit code / gate outcome is unaffected by
                                                     # the note — never a real runtime error code
Schema: no state.json field added; no MILESTONE.md/TASK.md template change; `status --json`'s
  key set is unchanged; reads only `.add/personas/*.md` (glob, stat) — no writes on this path.

phases/0-setup.md (3 skill trees: `add-method/skill/add/`, `.claude/skills/add/`,
  `add-method/src/add_method/_bundled/skill/add/`) — DONE (superseded the earlier SKILL.md "Beyond
  the bundle" plan per live user direction: "no, but add hint in setup.md step then draft all"):
  the existing persona-seeding bullet (step 3.1) gains a closing sentence routing the engine's hint
  back to this step:
    BEFORE: "...Covered by the baseline approval; add.py check validates; never clobber."
    AFTER:  "...Covered by the baseline approval; add.py check validates; never clobber. Still
             unseeded later? status/check/new-milestone's hint means: return here, draft every
             missing project persona — not just one."
  Cost: 136 B added to the "phases" `test_skill_lean` pool (2 B headroom before this change) →
  rebaselined that pool's frozen budget by ⌈136/0.80⌉ = 170 B (40931 → 41101), per the established
  "human-approved new surface" precedent already used elsewhere in that suite's history — done, not
  pending; `add.py new-task` deliberately gets NO call site (confirmed live: not per-task).
```

Glossary deltas: none — this task extends the existing persona-loop vocabulary (docs/18-personas.md), it does not introduce a new domain term.
Status: FROZEN @ v2 — approved by Tin Dang (confirmed "yes" to the plain-text freeze report showing the final setup.md sentence, the reworded hint text, the +170B phases-pool rebaseline cost, and the setup.md-only-loads-on-fresh-setup caveat)
Reported: yes — the freeze report (setup.md sentence, hint text, rebaseline cost, structural caveat, test/pin evidence) was rendered in chat before this outcome was recorded
Least-sure flag surfaced at freeze: [spec] Whether `phases/0-setup.md`'s prose alone (an
  instruction the orchestrator reads and must choose to act on) is a strong enough mechanism to
  reliably close the underlying gap, vs. a mechanical trigger — lowest confidence because unlike
  the engine's hint (which is code, always fires), this is prose the AI could still skim past on a
  low-attention session; mitigated by `status`/`check`/`new-milestone` re-surfacing the raw hint
  every session regardless, so even a missed read at setup keeps getting re-offered. If wrong (the
  AI keeps not acting on it in practice): the next loop's fix would be a stronger imperative or a
  `add.py doctor`-style check that measures "hint fired N times, still unseeded" — not an engine
  gate (docs/18-personas.md's "never lowers a gate" invariant holds either way).

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new predicate + both new call sites (small, additive surface)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_new_milestone_nudges_when_personas_dir_absent (M1/M2): fresh init, no `.add/personas/`
    manipulation beyond the seeded `_template.md` removed, run `new-milestone`, assert stdout
    contains a `note:` line naming `add-persona` or `docs/18-personas.md`
  - test_new_milestone_nudges_when_only_template_present (M1/M2): fresh init (personas dir has
    only `_template.md`), run `new-milestone`, assert the same `note:` line appears
  - test_new_milestone_silent_when_real_persona_exists (M3): write `.add/personas/frontend.md`
    (conformant persona), run `new-milestone`, assert stdout has NO `note:` persona line and is
    otherwise unchanged from the pre-change baseline
  - test_check_reports_personas_unseeded (M4): no real persona, run `check`, assert an INFO line
    naming "personas" as unseeded is present and the process exits 0
  - test_new_milestone_unreadable_persona_file_fails_soft (R1): a `.md` file under
    `.add/personas/` that raises `OSError` on read (monkeypatch `Path.read_text`/`glob`, or an
    unreadable-permission fixture), run `new-milestone`, assert no exception propagates and the
    `note:` line still prints
  - test_persona_hint_does_not_touch_gate_or_state (R2): no real persona, run `new-milestone`,
    assert `state.json` gains no new key and the milestone record / exit code are unchanged from
    the pre-change shape
  - test_personas_unseeded_predicate_unit (structural): direct unit coverage of
    `_personas_unseeded` for: absent dir -> True, dir with only `_template.md` -> True, dir with
    one real persona -> False, unreadable entry -> True (fail-soft) · covers: M5
  - test_persona_nudge_3tree_parity (structural, mirrors test_persona_template_3tree_parity):
    the new predicate + both call sites are byte-identical across `add-method/tooling`,
    `.add/tooling`, `add-method/src/add_method/_bundled/tooling` · covers: M6
  - test_status_nudges_when_personas_unseeded (M7, v2): no real persona, run `status`, assert
    stdout contains a `persona :` line naming `add-persona`/`docs/18-personas.md`
  - test_status_silent_when_real_persona_exists (M7, v2): a real persona exists, run `status`,
    assert no `add-persona`/`docs/18-personas.md` substring appears
  - test_status_json_unaffected_when_personas_unseeded (R3, v2): no real persona, run
    `status --json`, assert no "persona" substring anywhere in the parsed JSON
  - test_persona_hint_is_single_sourced (M8/M9, v2): `add.py` references `PERSONA_HINT` at
    all three call sites; the literal "this milestone's domain" no longer appears anywhere
</test_plan>

Tests live in: `add-method/tooling/test_persona_milestone_nudge.py`. MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/skill/add/phases/0-setup.md` `.claude/skills/add/phases/0-setup.md` `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md` `.add/SEAMS.md`
Strategy (ordered batches — ALL DONE):
  1. `_personas_unseeded(root)` in `add_engine/io_state.py`. 2. wire `cmd_new_milestone`. 3. wire
  `cmd_check`. 4. `test_persona_milestone_nudge.py` red→green. 5. mirror 3 trees. 6. re-aim pins v1.
  7. add `PERSONA_HINT` to `add_engine/constants.py` (+`__all__`), reword both v1 call sites to
  reference it instead of their own literal. 8. wire the new `cmd_status` call site (human-readable
  branch only, grouped with `context`/`voice`). 9. mirror `add.py` + `constants.py` byte-for-byte
  into the other 2 engine trees. 10. add `StatusNudgeTest` (3 tests) + a single-source parity test
  to `test_persona_milestone_nudge.py`; full 16/16 green. 11. re-aim `engine_pin.py`'s
  `ENGINE_MD5`/`ENGINE_PKG_MD5` again (v2 re-aim) and re-run the pin/parity/persona-nudge suites +
  the full discover suite — all green. 12. (superseded a first SKILL.md-bullet draft per live
  redirect) extend `phases/0-setup.md`'s persona-seeding bullet with the "return here, draft every
  missing project persona" sentence, mirror to the other 2 skill trees. 13. rebaseline
  `test_skill_lean.py`'s "phases" pool (40931→41101, +170 B) — confirmed green (`test_skill_lean`,
  `test_persona_setup`, `test_persona_method_docs`, full discover suite).

Persona (optional): none — generic stance (mechanical engine change, no domain-fit judgment needed)
Spawn isolation (default): n/a — no subagent was spawned for this build (direct, single-actor edit)
Known-problem fixes: v1's engine content change → stale ENGINE_MD5/ENGINE_PKG_MD5 pins → re-aimed
  (test_engine_pin_reaimed_x3, test_pkg_digest_includes_io_state_and_is_3tree green); v2 repeats the
  same re-aim after the reword/status/single-source change (both suites re-confirmed green);
  tests→build previously refused with `unflagged_freeze` (v1, pre-existing template/engine drift,
  unrelated to this task) — resolved once, does not recur on this v2 amendment (no new advance needed).
  v2 ALSO broke `test_seams_doc.test_every_anchor_resolves`: the new call sites shifted every
  line below them in `add.py`, staling `.add/SEAMS.md`'s `scope-token-grammar` anchor
  (`_declared_scope` cited at line 4518, actually moved to 4535) — caught by running the full
  discover suite (not just the targeted persona-nudge suite), confirmed as MY regression (not
  pre-existing) by diffing behavior against a `git stash`-clean tree, then fixed by updating the
  one stale citation. `test_seams_template_wiring.test_milestone_exit_grep_lists_all_3` also failed
  in the same run but reproduces identically on the clean tree too (a pre-existing local `grep -cl`
  alias mismatch, matches this repo's own documented history — see feedback memory
  `roster-install-drift`'s "ugrep-alias/BSD-grep" lesson) — left alone, not this task's regression.
Strategy actually used: v2 batches 7–11 executed exactly as drafted; batches 12–13 deviated from the
  FIRST v2 draft (which proposed a `SKILL.md` "Beyond the bundle" bullet + a "core"-pool rebaseline)
  — live user direction ("no, but add hint in setup.md step then draft all") redirected the action
  instruction to `phases/0-setup.md` instead, changing which `test_skill_lean` pool ("phases", not
  "core") absorbs the rebaseline. Both drafts deliver the same Must (M10); only the file and pool differ.
Safety rule (feature-specific): the hint must never raise — every new code path is wrapped in the
  existing fail-soft idiom (`is_dir()`/`glob()` guarded by `except OSError`), matching `_md5_file`'s
  adjacent pattern in the same module; `cmd_status`'s `--json` branch is untouched by construction
  (the new call site is textually below it, in the human-readable branch only)
Code lives in: `add-method/tooling/add_engine/io_state.py` (predicate, v1), `add_engine/constants.py`
  (`PERSONA_HINT`, v2), `add-method/tooling/add.py` (3 call sites + re-export), mirrored to the
  other 2 engine trees; `phases/0-setup.md`'s catch-up sentence mirrored across its 3 skill trees;
  `.add/SEAMS.md`'s stale anchor citation corrected; `test_skill_lean.py`'s "phases" pool rebaselined.
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 16/16 in `test_persona_milestone_nudge.py` + full ~2900-test discover suite (only the 2 known pre-existing local grep-alias failures, confirmed not-mine via `git stash` diff)
- [x] coverage did not decrease — new predicate + all 3 call sites each have direct unit/behavior coverage (§4 test plan); no existing test removed or weakened
- [x] no test or contract was altered during build — `test_skill_lean.py`'s baseline number is a budget, not a behavior assertion; the frozen §3 CONTRACT shape (predicate signature, call-site diffs) shipped exactly as specified
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe — pure stdlib `Path.is_dir()`/`glob()` reads, no shared mutable state, no async/threading involved
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new dependency; hint text is a static literal, never interpolates untrusted input
- [x] layering & dependencies follow CONVENTIONS.md — predicate lives in `add_engine/io_state.py` alongside its `_md5_file` sibling (same fail-soft idiom); no cross-layer leak
- [x] a person reviewed and approved the change — Tin Dang, plain-text "yes" to the freeze report (setup.md sentence + hint text + rebaseline cost + structural caveat shown first)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] `status`/`check`/`new-milestone` each print the identical `PERSONA_HINT` wording when unseeded, silent when a real persona exists — confirmed by `StatusNudgeTest` + existing v1 classes, and by `test_persona_hint_is_single_sourced` asserting all 3 call sites reference the one constant
- [x] `status --json` carries no `persona` key — confirmed by `test_status_json_unaffected_when_personas_unseeded` parsing the JSON and asserting no "persona" substring
- [x] `phases/0-setup.md`'s persona bullet (all 3 skill trees) ends with the "draft every missing project persona — not just one" sentence, byte-identical across trees — confirmed by direct `Read` of all 3 files this session
- [x] no literal "this milestone's domain" phrase remains anywhere in `add.py` — confirmed by `test_persona_hint_is_single_sourced`

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `PERSONA_HINT` referenced at exactly 3 call sites (`cmd_new_milestone`, `cmd_check`, `cmd_status`) plus `__all__`; `_personas_unseeded` referenced by the same 3 — no orphaned symbol
- [x] DEAD-CODE (code) — no new unused symbol; v1's original per-call-site literals were fully replaced, not left as dead alternates
- [x] SEMANTIC (prose) — read `phases/0-setup.md` in full (all 104 lines) after the edit to confirm the new sentence reads coherently in context, not just grepped for presence; also read `.add/SEAMS.md` in full to confirm the anchor fix didn't disturb the surrounding entry's prose

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — `_personas_unseeded` confirmed live in `io_state.py`; `PERSONA_HINT` confirmed live in `constants.py`; all 3 `add.py` call sites confirmed live via this session's `Read`/grep passes
- [x] anchor that moved since Ground SHA, named here: `.add/SEAMS.md`'s `scope-token-grammar` entry cited `_declared_scope` at `add.py:4518`; this task's new call sites pushed it to `:4535` — caught via the full discover suite (`test_seams_doc.test_every_anchor_resolves`), fixed in-band, not left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) ran the full ~2900-test discover suite, not just the targeted persona-nudge suite, specifically to surface any collateral damage from line-shifting edits — this is what caught the SEAMS.md anchor regression, a real bug a narrower run would have missed; (2) confirmed the 2 remaining failures are pre-existing by running them against a `git stash`-clean tree (same failures reproduce with none of this task's changes applied); (3) checked `M3`/`R3`'s negative-case tests (byte-identical output when a real persona exists; no `persona` key in `--json`) actually assert absence, not just presence of the happy path, ruling out a stubbed-always-true predicate; (4) read the single-source test's assertion logic directly to confirm it greps the real `add.py` source rather than a fixture copy.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self (mechanical/additive-stdout change; escalated design-direction questions to the `advisor` tool twice this session already — both informed this gate, not a separate spawn)
1. Security: CLEAR — no new input surface, no secrets, no exec/network path (NO-EXEC constraint holds by construction: pure `Path.is_dir()`/`glob()` reads)
2. Concurrency: CLEAR — no shared mutable state, no new I/O ordering dependency; each call site reads the same immutable `.add/personas/` snapshot independently
3. Architecture: CLEAR — single-sourced constant closes the exact drift risk v1 had (3 literals); no new layering violation; the `phases/0-setup.md` prose-only mechanism was flagged (via `advisor`) as the one soft spot — a prose instruction the AI could skim past — but this is a Spec-level residue, not an Architecture one, and is already carried in the "Least-sure flag" below
Verdict: PASS
Residue: none blocking — see "Least-sure flag" below for the one open (non-blocking) spec-level residue
Binding: advisory — sensitivity not declared on this task's header (defaults apply); no security/architecture finding to bind

### GATE RECORD
Reported: yes — the gate report (this §6 fill plus the pre-freeze plain-text summary) rendered before this outcome recorded
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-04

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether ai-proxy (or any pre-existing project) actually runs `add-persona` after seeing the raw hint at `status`/`check` — the real signal this task set out to move; whether any future line-shifting `add.py` edit stales another `.add/SEAMS.md` anchor undetected (only the full discover suite catches this today).

### Decisions (ADR)
- [ADD · self] v2 kept the hint single-sourced (`PERSONA_HINT`) and project-scoped rather than per-milestone, per direct user instruction — closes the drift risk v1's 3 duplicated literals carried.
- [ADD · self] the "act on this hint" instruction was routed to `phases/0-setup.md` (not a new `SKILL.md` "Beyond the bundle" clause) — live user redirect, costs the "phases" `test_skill_lean` pool rather than "core".
- [ADD · self] did not add a `new-task` call site — confirmed live as an explicit non-goal (anti-double-fire, unchanged from v1).

### Spec delta
- [SPEC · open] `phases/0-setup.md`'s catch-up sentence only reloads on the zero-touch autonomous-setup path (no `.add/state.json` yet); an already-set-up project (the ai-proxy case that motivated this task) never re-reads it — only the raw `status`/`check`/`new-milestone` hint text reaches that case. A future loop could consider a lighter-weight mechanism (e.g. `add.py doctor`-style repeat-count measure) if the raw hint alone proves insufficient to get an existing project to act (evidence: advisor's structural read this session; not yet observed in the wild).

### Competency deltas
- [ADD · open] a code edit that shifts line numbers in `add.py` can silently stale a hardcoded `Anchor: file:line` citation elsewhere in `.add/SEAMS.md` — only the FULL discover suite catches this (`test_seams_doc.test_every_anchor_resolves`), not the narrower targeted-test run a task naturally reaches for first (evidence: this task's own `scope-token-grammar` anchor went stale from `:4518` to `:4535` after adding 3 new call sites; caught only because the full suite was run before the freeze report, not the targeted persona-nudge suite alone). This is at least the 4th time this exact anchor has gone stale (per `.add/SEAMS.md`'s own citation history) — worth a systematic fix (e.g. an anchor-freshness check that runs as part of every completing build, not just an eventual full-suite catch) rather than repeat manual catches.
- [TDD · open] running the full discover suite (not just the targeted new-test file) before a freeze/gate report is what surfaces collateral regressions from line-shifting edits — the targeted suite alone would have shipped the stale SEAMS.md anchor silently (evidence: same instance as above).
