# TASK: footer + guide name the driver — [you drive] vs [human gate] from autonomy × phase

slug: gate-owner-marker · created: 2026-06-12 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:_next_footer(root, state)` — the footer resolver. `marker = ""` reserved
    slot (L2945) appended on ALL three return paths: Arm A in-flight (L2954, keyed off `t["phase"]`),
    Arm B milestone rollup (L2958, `_decide_next_base`), fail-soft re-orient (L2961).
  - `add-method/tooling/add.py:cmd_guide` — JSON path (L1023-1028): `owner = _phase_owner(phase)`,
    `"stop": owner != "ai"` — **autonomy-BLIND**; the no-task branch hardcodes `owner:"human",stop:True`
    (L1014). TEXT path (L1045-1059): prints `active/goal/next/read/guide/then` with **NO driver marker**.
  - `add-method/tooling/add.py:_phase_owner` / `PHASE_OWNER` (L78-82, L211-216) — phase → {ai,human,seam},
    the STRUCTURAL owner the marker renders; `_die("unmapped_phase")` on a bad phase.
  - autonomy readers — `_autonomy_level(hdr)` (L622 → {manual,conservative,auto}|None|"?"); `_task_header(root,slug)`
    (L641, comments stripped, missing→""); `_project_autonomy(root)` (L1826, absent→auto · "?"→conservative — the fail-SAFE fallback).
  - `add-method/tooling/test_next_footer_engine.py:test_marker_slot_reserved` (L251-256) — asserts the footer has
    NO `you drive`/`human gate`; filling the slot FLIPS it (a STRENGTHENING co-update, rule #3 OK). A §5-SCOPE edit, NOT a §4 red-test of THIS task.
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` — re-aim + carry "re-aimed @ next-footer-engine"; ×3 add.py mirror byte-sync.

Context (working folder): run.md autonomy semantics — the dial governs exactly ONE phase, **verify** (auto → the AI
  auto-PASSes on evidence; conservative/manual → the human gates). The **contract freeze stays human regardless of the
  dial** (run.md:21 "the decision point stays human"). So autonomy modulates verify ONLY; every other phase keeps its
  structural `_phase_owner`. Effective autonomy for a task = `_autonomy_level(_task_header(root,slug))`, falling back to
  `_project_autonomy(root)` when the task line is unset(None)/unknown("?") — the same fail-safe chain `cmd_new_task` seeds from.

Honors (patterns / conventions): next-footer-engine's reserved-slot contract (the exact words ` [you drive]`/` [human gate]`
  it named); **ONE resolver / no second owner map** (this milestone's whole point — reuse `_phase_owner`, refine with the dial
  at the single verify seam, and feed BOTH the footer marker AND cmd_guide's `stop` from that one source so they never drift);
  ×3 byte-identical add.py mirror + engine_pin re-aim carrying the prior task's marker; the new red suite lives in its OWN file
  (test_gate_owner_marker.py, tamper-locked at tests→build), the cross-file flip (test_next_footer_engine.py) declared in §5
  scope and NOT tamper-locked — the next-footer-engine separation (own red file + strengthened sibling as a scope co-update).

Anchors the contract cites: NEW `_driver_stop(root, state, slug, phase) -> bool` (`_phase_owner(phase) != "ai"` for every
  phase EXCEPT verify, where it is `effective_autonomy(root,state,slug) != "auto"`) + its rendering `_driver_marker(stop) -> str`
  (the SINGLE source for the footer marker AND the cmd_guide TEXT marker; Option F leaves the frozen JSON `stop` untouched);
  `_phase_owner`/`PHASE_OWNER`; `_autonomy_level`/`_task_header`/`_project_autonomy` (the effective-autonomy fallback chain);
  `_next_footer` (Arm A · Arm B · fail-soft slot); `cmd_guide` (TEXT marker line only — JSON path untouched per Option F);
  `test_marker_slot_reserved` (the flip); `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the driver marker — every engine footer AND the `guide` next-step line name who drives the
next step, ` [you drive]` (the AI proceeds) vs ` [human gate]` (a human owns it), from autonomy × phase.

Framings weighed: render the existing owner/stop, refine only verify (chosen) · a fresh autonomy×phase
decision table · footer-only (skip the guide).
  - CHOSEN renders what the engine ALREADY decides: `_phase_owner` classifies every phase and cmd_guide
    already derives `stop = owner != "ai"`. The marker is the word for that `stop`, with exactly ONE new
    refinement — verify reads the autonomy dial. One source, minimal surface, ZERO behavior change off verify.
  - A fresh decision table re-mints an owner judgment per phase — a SECOND source, the exact context-rot
    this milestone exists to remove (rejected).
  - Footer-only is rejected: the exit criterion names BOTH the footer and the guide.

Must:
<must>
  - Every footer the engine prints ends with exactly ONE driver marker filling the slot next-footer-engine
    reserved — ` [you drive]` or ` [human gate]` (leading space, the exact words that task named).
  - The marker derives from a SINGLE resolver `_driver_stop(root, state, slug, phase) -> bool`:
    `_phase_owner(phase) != "ai"` for every phase, EXCEPT verify where it is `effective_autonomy != "auto"`.
    `_driver_marker(stop)` renders True → ` [human gate]`, False → ` [you drive]`.
  - At verify under `auto` → ` [you drive]` (the AI auto-gates on evidence); under `conservative`/`manual`
    → ` [human gate]` (the human gates). ← the milestone exit criterion.
  - At the contract freeze (phase `contract`, owner `seam`) → ` [human gate]` regardless of the dial —
    the decision point stays human (run.md:21).
  - cmd_guide's TEXT path shows the SAME marker on its next-step line. The JSON path is UNCHANGED — `stop`
    stays the frozen machine-state-json contract value (`owner != "ai"`, structural, dial-blind); the driver
    marker is a FOOTER + guide-TEXT surface only (the milestone criterion names the footer, not the JSON).
  - Effective autonomy reads the task's own `autonomy:` line, falling back to `_project_autonomy(root)` when
    the line is unset(None)/unknown("?") — never silently `auto` on an unrecognized token (fail-safe to gating).
  - Fail-soft: when the footer cannot resolve a driver (no active milestone / unreadable doc / corrupt rollup),
    the degraded re-orient line carries NO marker — never assert a driver you could not compute. Never crashes.
</must>
Reject:
<reject>
  - an unmapped phase -> "unmapped_phase"  # inherited verbatim from _phase_owner; the marker invents NO default
</reject>
After:
<after>
  - every `add.py` mutating-verb footer and every `add.py guide` next-step line names the driver; a reader
    tells at a glance whether the AI proceeds or a human gates.
  - the frozen machine-state-json contract (cmd_guide JSON `owner`/`stop`) is UNTOUCHED; the autonomy-aware
    driver lives on the footer + guide TEXT only (Option F). Residue: guide-text and guide-JSON diverge at
    verify-auto — disclosed as a §7 delta → a deliberate machine-state-json amendment, NOT absorbed here.
  - no second phase→owner map exists; `_driver_stop` is the ONLY place the dial meets the phase.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ specify·scenarios driver — owns-direction (chosen) vs performs-next-action. CHOSEN renders the existing
    `_phase_owner`: specify·scenarios stay ` [human gate]` (the human owns DIRECTION; the one approval is deferred
    to the contract freeze). The alternative reads them the way verify is read ("who PERFORMS the next step"): the
    AI drafts the rules → ` [you drive]`, only the contract freeze ` [human gate]`. They differ ONLY on these two
    phases — verify(=dial), contract(=human), ai-phases(=AI) are all FIXED by run.md. Lowest confidence because it
    is the one row with NO frozen precedent. If wrong: 2 table rows + their code/tests flip. Default owns-direction
    fails toward MORE gating, and the engine literally cannot emit ` [you drive]` at specify today (`_phase_owner`
    already says human) — so it is also the zero-new-behavior choice.
  - [ ] Arm B (no in-flight task) markers: the milestone-orchestration next-steps (resolve HARD-STOP · approve
    contract · gate · decompose/new-task) are human decision points → ` [human gate]`; "run in progress" (another
    task mid-flight) → ` [you drive]`; the fail-soft re-orient line → no marker. Confirm the Arm B mapping at the freeze.
  - [ ] the marker words are EXACTLY ` [you drive]`/` [human gate]` (leading space) — the strings next-footer-engine's
    reserved-slot comment named and `test_marker_slot_reserved` asserts the ABSENCE of. A reworded marker silently
    breaks the cross-task flip; confirm no rewording.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: verify under auto names the AI
  Given an in-flight task at phase verify with autonomy: auto
  When a mutating verb prints its footer
  Then the footer ends with " [you drive]"
  And the next: command is still the gate verbs (the slot only appends a marker)

Scenario: verify under conservative names the human
  Given an in-flight task at phase verify with autonomy: conservative
  When a mutating verb prints its footer
  Then the footer ends with " [human gate]"

Scenario: verify under manual names the human
  Given an in-flight task at phase verify with autonomy: manual
  When a mutating verb prints its footer
  Then the footer ends with " [human gate]"

Scenario: the contract freeze stays human even under auto
  Given an in-flight task at phase contract with autonomy: auto
  When a mutating verb prints its footer
  Then the footer ends with " [human gate]"
  And auto does NOT flip the freeze to " [you drive]" (the decision point stays human)

Scenario: an AI-owned phase names the AI
  Given an in-flight task at phase build (owner ai) with any autonomy
  When a mutating verb prints its footer
  Then the footer ends with " [you drive]"
  And the marker is autonomy-blind off verify

Scenario: the guide text line names the same driver
  Given an in-flight task at phase verify with autonomy: conservative
  When add.py guide runs (text)
  Then its next-step line carries " [human gate]"
  And add.py guide writes nothing (read-only)

Scenario: the frozen JSON stop is left untouched
  Given an in-flight task at phase verify with autonomy: auto
  When add.py guide --json runs
  Then "stop" is still true (the frozen machine-state-json contract value, owner != "ai" — unchanged)
  And the autonomy-aware driver is NOT in the JSON; it lives on the guide TEXT marker (" [you drive]")

Scenario: unset task autonomy falls back to the project default
  Given an in-flight verify task whose TASK.md has no autonomy: line and PROJECT.md defaults to conservative
  When a mutating verb prints its footer
  Then the footer ends with " [human gate]"
  And an unrecognized token resolves to a human gate, never silently auto

Scenario: no resolvable driver degrades to a bare line
  Given no active milestone (the fail-soft path)
  When a mutating verb prints its footer
  Then the footer is "next: add.py status — re-orient" with NO driver marker
  And the verb still exits 0 (a footer never crashes a saved mutation)

Scenario: an unmapped phase is rejected, not defaulted
  Given a state whose task phase is not in PHASE_OWNER
  When the driver is resolved
  Then it dies with "unmapped_phase"
  And the marker invents no default owner

Scenario: the reserved slot is now filled (cross-task flip)
  Given an in-flight task at an AI-owned phase under auto
  When a mutating verb prints its footer
  Then the footer DOES contain a driver word (" [you drive]")
  And test_marker_slot_reserved is updated to assert presence, a strengthening (rule #3)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# Driver-marker resolver — add-method/tooling/add.py (×3 mirrors byte-identical). PURE; writes nothing.

_effective_autonomy(root, state, slug) -> str          # a member of {manual, conservative, auto}
    lvl = _autonomy_level(_task_header(root, slug))     # the task's own rung first
    -> lvl                       when lvl in _AUTONOMY_LEVELS      # explicit task rung wins
    -> _project_autonomy(root)   when lvl in (None, "?")          # unset/unknown -> project fail-safe
                                                                  #   (absent→auto · unknown→conservative)

_driver_stop(root, state, slug, phase) -> bool          # True = a human owns the NEXT step
    phase == "verify"  -> _effective_autonomy(root, state, slug) != "auto"   # the ONE dial-modulated seam
    else               -> _phase_owner(phase) != "ai"                        # structural owner, dial-blind
    # _phase_owner already _die("unmapped_phase") on a bad phase — inherited; the marker invents NO default

_driver_marker(stop) -> str                             # the reserved-slot word (each ONE leading space)
    True  -> " [human gate]"
    False -> " [you drive]"

# The phase × autonomy table the two functions encode (the FROZEN shape):
#   phase      owner   auto          conservative/manual
#   ground     ai      [you drive]   [you drive]
#   specify    human   [human gate]  [human gate]
#   scenarios  human   [human gate]  [human gate]
#   contract   seam    [human gate]  [human gate]    # the freeze stays human — dial-blind (run.md:21)
#   tests      ai      [you drive]   [you drive]
#   build      ai      [you drive]   [you drive]
#   verify     human   [you drive]   [human gate]    # <- the ONLY dial-modulated row (exit criterion)
#   observe    ai      [you drive]   [you drive]
#   done       human   (Arm B — phase!="done" leaves Arm A; resolved by the rollup branch below)

# _next_footer(root, state) — the `marker = ""` slot is now filled per path:
#   Arm A in-flight: marker = _driver_marker(_driver_stop(root, state, slug, phase))
#   Arm B rollup:    marker = _driver_marker(human_stop) where human_stop comes from the SAME precedence
#                    _decide_next_base already walks (no second precedence): a human DECISION point
#                    (resolve HARD-STOP · approve contract · gate · decompose/new-task on an empty
#                    milestone) -> [human gate]; "run in progress (<slug> at <phase>)" -> [you drive].
#   fail-soft:       NO marker — the degraded "next: add.py status — re-orient" asserts no driver it
#                    could not compute (the except/no-milestone path). Verb still exits 0.

# cmd_guide (the guide names the driver too) — Option F: the FROZEN JSON is NOT touched:
#   TEXT path: the next-step line carries _driver_marker(_driver_stop(...)) — the SAME marker as the footer.
#   JSON path: UNCHANGED. "owner"/"stop" stay the frozen machine-state-json contract (`stop = owner != "ai"`,
#              structural, dial-blind); the no-task branch keeps owner:"human",stop:True. The driver marker is a
#              FOOTER + guide-TEXT surface only — the milestone criterion names the footer, not the JSON; and per
#              intake.md, changing the frozen JSON is a change-request against machine-state-json, NOT absorbed here.
#   Residue (disclosed): guide-TEXT (` [you drive]` at verify-auto) diverges from guide-JSON (`stop=true`). Logged
#              as a §7 delta → a deliberate machine-state-json amendment (its v1.1 phase/gate amendment = the
#              precedent). Nothing in the gate/verify path reads guide-JSON `stop` (auto-gating keys off the task
#              header autonomy in cmd_gate, L676), so the stale JSON drives NO behavior.

# Marker words (frozen literals): " [you drive]" · " [human gate]"  (one leading space each; nothing else fills the slot)
Schema: READS state.json (post-save) + each task's TASK.md header (_task_header) + PROJECT.md (_project_autonomy)
        + MILESTONE.md/PROJECT.md via report_data (Arm B). WRITES nothing. engine_pin.ENGINE_MD5 re-aimed
        @ gate-owner-marker (carries the prior "re-aimed @ next-footer-engine"); add.py mirrored ×3 byte-identical.
```

Least-sure flag surfaced at freeze:
  (one real fork, two disclosures)
  ⚠ [spec] THE FORK — specify·scenarios driver: owns-direction (chosen, ` [human gate]`) vs performs-next-action
     (` [you drive]`, the way verify is read). The only table row with NO frozen precedent (verify=dial,
     contract=human, ai-phases=AI are all FIXED by run.md); the two framings differ ONLY on these two phases.
     RECOMMEND owns-direction — it fails toward MORE gating and the engine already says human there (zero new
     behavior). Cost if you want the other: 2 table rows + their code/tests flip.
  ▸ [disclosure · contract] JSON left FROZEN (Option F) — the marker rides the FOOTER + guide-TEXT only;
     cmd_guide's JSON `owner`/`stop` (the frozen machine-state-json contract) is UNTOUCHED. Per intake.md,
     changing it is a change-request against THAT contract, not absorbed here. Residue: guide-text and guide-JSON
     diverge at verify-auto → logged as a §7 delta → a deliberate machine-state-json amendment. I can fold that
     amendment in now if you want it (otherwise it stays a follow-up; nothing reads the JSON `stop` today).
  ▸ [disclosure · header] autonomy — RECOMMEND lowering `auto` → `conservative`: this edits the trust-layer
     itself (run.md's own high-risk example), it dogfoods (this task's own verify then reads ` [human gate]`),
     and it makes honest what next-footer-engine already did (ran `auto` but a human still PASS-gated). Flag, not a blocker.
  · [scenario] Arm B split (not a fork — confirm): no in-flight task → milestone decision points (HARD-STOP ·
     approve-contract · gate · decompose) read ` [human gate]`; "run in progress" reads ` [you drive]`; derived
     from `_decide_next_base`'s own branch (not string-matched, per the §5 safety rule).

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-12. Resolutions at the freeze: (1) THE FORK → owns-direction (specify·scenarios = ` [human gate]`, the chosen default); (2) Option F → the frozen machine-state-json JSON (`owner`/`stop`) stays UNTOUCHED, the marker rides the footer + guide-TEXT only, the verify-auto text↔JSON divergence deferred to a §7 delta → a later machine-state-json change-request; (3) autonomy kept at `auto` (matches next-footer-engine; the verify gate stays human-reviewable). Changing this frozen contract = change request back to SPECIFY.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject (render-blind — every assertion reads the printed footer/guide line or the public resolver, never a private state key).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_verify_auto_names_ai: task at verify, autonomy auto / run a footer verb / footer endswith ` [you drive]`
  - test_verify_conservative_names_human: verify, conservative / footer verb / endswith ` [human gate]`
  - test_verify_manual_names_human: verify, manual / footer verb / endswith ` [human gate]`
  - test_contract_freeze_stays_human_under_auto: contract, auto / footer verb / endswith ` [human gate]` (dial-blind freeze)
  - test_ai_owned_phase_names_ai: build, even conservative / footer verb / endswith ` [you drive]` (dial-blind off verify)
  - test_guide_text_names_driver: verify, conservative / `guide` text / line carries ` [human gate]`; guide writes nothing
  - test_guide_json_stop_untouched [GUARD/F]: verify, auto / `guide --json` / `stop` still true (frozen) + text marker ` [you drive]`
  - test_unset_autonomy_falls_back_to_project_default: PROJECT.md conservative + task with no autonomy line / verify / ` [human gate]`
  - test_driver_table_matches_contract: the public `_driver_marker(_driver_stop(...))` over the full phase×autonomy table (the frozen §3)
  - test_arm_b_decompose_names_human: empty new-milestone / Arm B / footer endswith ` [human gate]`
  - test_arm_b_hardstop_names_human: HARD-STOP task / Arm B / footer endswith ` [human gate]`
  - test_arm_b_run_in_progress_names_ai: a sibling task mid-run / Arm B / "run in progress" footer endswith ` [you drive]`
  - test_fail_soft_no_marker [GUARD]: lock on a fresh project / fail-soft / footer == "next: add.py status — re-orient" (NO marker)
  - test_unmapped_phase_invents_no_default: a bad-phase task / `guide` / exits nonzero, no driver word emitted
  Sibling co-updates (in §5 scope, NOT this file — applied in build, strengthenings): `test_next_footer_engine.py`
  test_gate_hardstop_routes_arm_b L218 (exact-equal → append ` [human gate]`) · test_marker_slot_reserved L251
  (assertNotIn → assertIn ` [you drive]`). Every OTHER sibling footer assertion is startswith/assertIn and survives;
  the fail-soft exact-equal (L244) survives because Option F gives fail-soft NO marker.
</test_plan>

Tests live in: `add-method/tooling/test_gate_owner_marker.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_gate_owner_marker.py` · `add-method/tooling/test_next_footer_engine.py`
Scope note (declared at the freeze): `test_next_footer_engine.py` is IN scope for the cross-task flip — `test_marker_slot_reserved` currently asserts the footer has NO driver word; filling the slot STRENGTHENS it to assert presence (rule #3 holds — a strengthening, not a weakening). It is a §5 SCOPE edit, NOT a §4 red-test of this task: this task's red suite is the NEW `test_gate_owner_marker.py`, tamper-locked at tests→build; the flip is applied in build, off the lock.
Strategy (AS BUILT — F, not U): 1. wrote `_effective_autonomy` + `_driver_stop` + `_driver_marker` in canonical add.py 2. filled `_next_footer`'s marker slot — Arm A via `_driver_stop`; Arm B via NEW `_decide_next_pair(state,d)->(text,human_stop)` (the precedence extracted ONCE; `_decide_next_base` is now a thin `[0]` wrapper so the 3 report/digest callers are unchanged); fail-soft no-marker 3. added the marker to cmd_guide's TEXT `next   :` line — JSON path UNTOUCHED (Option F, frozen machine-state-json contract) 4. flipped both sibling assertions in `test_next_footer_engine.py`: Arm B HARD-STOP exact-equal → ` [human gate]`, and `test_marker_slot_reserved`→`test_marker_slot_filled` (assert ` [you drive]`) 5. synced the ×3 add.py mirrors byte-identical 6. re-aimed `engine_pin.ENGINE_MD5` (a4dcc0b…) + annotated `re-aimed @ gate-owner-marker` carrying the prior marker. Build-discovered: `_driver_stop`'s docstring had to drop "seam"/"dial" slang (test_ubiquitous_language scans add.py string literals) — reworded to "phase"/"autonomy level".
Safety rule (feature-specific): the marker is PURE render — derived from recorded state (phase × the autonomy header), NEVER from prose; it writes nothing and, like the footer it rides on, must never turn a saved mutation into a crash (fail-soft to no-marker).
Code lives in: `add-method/tooling/add.py` (canonical) + its two mirrors.
Constraints: do NOT change any test (except the disclosed `test_marker_slot_reserved` strengthening) or the contract; allow-list packages only (stdlib only); the engine stays tool-agnostic (no git); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **924** on python3.14 (`OK`, 0 fail/0 error). The +1 over the prior 923/923 ×2 is the pin-annotation guard added at the gap-close (below); it is green on python3.10 too (standalone + the full `test_gate_owner_marker` module, 15/15 `OK`). py3.10 full suite NOT re-run for the +1 — the guard is read-only (reads `engine_pin.py`, asserts substrings; no shared fixtures, no global state) over a **byte-identical engine** (add.py md5 `a4dcc0b…` unchanged), so it cannot regress the other 923 nor diverge cross-interpreter. `add.py check` 284 passed / 0 failed (13 pre-existing WARNs, none gate-owner-marker).
- [x] coverage did not decrease — +15 new tests (test_gate_owner_marker.py) + 2 sibling assertions STRENGTHENED; nothing removed.
- [x] no test or contract was altered to pass — §3 frozen @ v1 unchanged since the freeze; the red suite (test_gate_owner_marker.py) byte-unchanged since the tests→build snapshot (re-crossed tests→build at the gap-close to re-baseline the added guard, then build→verify clean — scope + tripwire both passed); the only test edits are the 2 disclosed §5-scope sibling STRENGTHENINGS in test_next_footer_engine.py.
- [x] **disclosed gap CLOSED** — the red suite originally omitted a pin-annotation self-test for THIS task. Closed before the gate (the user's close-gap-before-gate preference): `EnginePinTest.test_pin_annotation_names_this_task` now asserts `engine_pin.py` names `re-aimed @ gate-owner-marker` AND carries the prior task's `re-aimed @ next-footer-engine` (the supersession chain). The binding carry-test (next-footer-engine L334) was already green; this adds THIS task's own obligation, which has no clean home downstream (ux-stale-followups pins ITS own marker). Lesson → §7 [TDD] delta.
- [x] the green was EARNED — independent adversarial refute-read (subagent, autonomy auto): VERDICT EARNED, all 7 refutations HELD with cited evidence (overfit·vacuous·stub·weakened-test·contract-edited·hidden-behaviour-change·fail-soft all clean). `_driver_stop` is a real 2-line resolver over `_phase_owner` + `_effective_autonomy`; `test_driver_table_matches_contract` exercises the full 18-cell table against the live resolver.
- [x] concurrency / timing safe — pure functions, no shared mutable state, computed AFTER save_state; the footer never writes.
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure render, stdlib only, writes nothing; the marker is a fixed literal, inputs are controlled state/headers.
- [x] layering & dependencies follow conventions — clean resolver trio + the `_decide_next_base`→`_decide_next_pair` pure extraction (thin `[0]` wrapper preserves all 3 report/digest callers); engine stays tool-agnostic (no git); ×3 add.py mirrors byte-identical; engine_pin re-aimed.
- [ ] a person reviewed and approved the change   ← the gate (autonomy auto allows an auto-PASS; this edits the trust-layer, so presenting for a human verdict)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_driver_stop`/`_driver_marker`/`_effective_autonomy` referenced by `_next_footer` (Arm A) + `cmd_guide` TEXT; `_decide_next_pair` referenced by `_next_footer` Arm B + the `_decide_next_base` wrapper. Confirmed by the green suite (table test hits the resolver directly; footer/guide tests hit the call sites; refute-read cited each site).
- [x] DEAD-CODE (code) — no orphan: every new symbol has a live caller (above). `_decide_next_base` retained as the thin wrapper for its 3 report/digest callers. Known: `_effective_autonomy`'s `state` param is contracted-but-unused (frozen §3 signature symmetry) — documented in its docstring; the refute-read flagged it as a low-severity FORWARD risk (a future caller passing a stale `state` would be silently ignored), not a bug.
- [x] SEMANTIC (prose) — read run.md autonomy semantics + intake.md rubric + the frozen machine-state-json contract in full: Option F is method-correct (changing JSON `stop` = a change-request against THAT contract, not absorbed here). Disclosed residue logged for §7.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-12
Note: presented for a human verdict though autonomy=auto permitted an auto-PASS (the gate edits the trust-layer). The disclosed pin-annotation gap was CLOSED before the gate (close-gap-before-gate); 2 deferred §7 deltas + 1 low-severity forward-risk remain, none security, none blocking.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): every COMPLETING mutating verb prints exactly ONE `next:` footer ending in a driver marker — except the intended marker-free paths (fail-soft re-orient; the heal exit-3 and init EXCEPTIONS). A bare footer (no marker) on any other verb, or a double marker, is the regression signal.
Spec delta for the next loop: Option F left a deliberate residue — the marker's guide-TEXT and the frozen machine-state-json guide --json `stop` disagree at verify-auto; the next loop reconciles them via a change-request against the machine-state-json contract, not an in-place edit.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] the engine-pin self-test (`re-aimed @ <slug>`) is part of the pin idiom, not optional — the red suite must include it from ground rather than discover the gap at the verify gate (evidence: gate-owner-marker's red suite omitted test_pin_annotation_names_this_task; caught at verify, closed by re-crossing tests→build→verify with the engine byte-identical, md5 a4dcc0b unchanged)
- [ADD · folded] the driver marker's guide-TEXT (`[you drive]` at verify-auto) diverges from the frozen machine-state-json guide --json `stop=true`; reconcile via a deliberate change-request against the machine-state-json contract, never an in-place edit of the frozen JSON (evidence: Option F freeze decision on §3 v1; test_machine_state locks JSON `stop = owner != "ai"` per phase)
- [ADD · folded] no mutating verb re-aims `active_milestone` — it still reads udd-design-foundation while next-step-seams is the active work; fold the re-aim into ux-stale-followups (evidence: `add.py status` shows active_milestone=udd-design-foundation while gate-owner-marker is active under next-step-seams)
- [SDD · folded] a §3 contract that broadens an engine verb-set must first map which frozen tests lock the old shape; surfacing that collision early turned a freeze-blocker into the smaller Option F (evidence: the reconcile-with-advisor pivot from "unify JSON stop" — blocked by test_machine_state — to Option F, which kept that suite green)
- [TDD · folded] a contracted-but-unused parameter is a forward-risk a self-test should pin — `_effective_autonomy(root, state, slug)` ignores `state`, so a future caller passing a stale `state` would be silently dropped (evidence: refute-read flagged it low-severity; documented in the docstring + §6 DEAD-CODE check, no test guards the contract today)
