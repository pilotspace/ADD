# TASK: SOUL.md living voice doc: schema + scaffold + read

slug: soul-artifact · created: 2026-06-15 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
- `add-method/tooling/add.py:SETUP_FILES` (line 83) — the survivor-layer tuple `cmd_init` loops to scaffold living docs; add `"SOUL.md"`. `cmd_init` (line 378) already renders each via `_render_template` + never-clobbers an existing one, so NO cmd_init body change is needed — the tuple membership is the wiring. ENGINE change → re-pin `engine_pin.ENGINE_MD5`.
- `add-method/tooling/add.py:cmd_status` (context line ~1015) — today prints `context : .add/PROJECT.md …`. Add a sibling existence-gated pointer to `.add/SOUL.md` (the voice — read each session) so the resume point names it. Existence-only check (no open/parse → no new IO failure path), mirroring the PROJECT.md pointer idiom.
- `add-method/tooling/templates/SOUL.md.tmpl` (NEW) — the scaffold: the SOUL section SCHEMA + a starter "Trusting" voice. Synced byte-identical into all 3 tooling/templates trees (canonical · `.add` dogfood · `_bundled`); the bundle copy is what the installer ships.
- `add-method/skill/add/SKILL.md` ("Always start here", ~line 26) — add the session-start instruction: read `.add/SOUL.md` (the voice) when orienting. Synced across the 3 skill trees.
Context (working folder): SOUL.md is a NEW survivor-layer living doc, peer to PROJECT.md/CONVENTIONS.md. It is the AI's voice — tone, communication style, and what keeps the human's trust — and is designed to self-improve (soul-self-improve, task 6, owns the observe→confirm→rewrite loop that rewrites this schema).
Honors (patterns / conventions): survivor-layer never-clobber + skip-if-blank-template (cmd_init idiom); 3-tree byte-identical sync (engine + skill + templates) guarded by engine_pin / test_tree_parity / test_bundle_parity; `test_add.test_init_creates_state_and_setup_files` already loops SETUP_FILES → a free scaffold census; the milestone shared decision — SOUL.md is identity-owned: the AI proposes, the human's confirm is the only writer (so the shipped voice is a PROPOSED starter, never a locked identity claim).
Anchors the contract cites: `SETUP_FILES` membership (`"SOUL.md"`) · `templates/SOUL.md.tmpl` exists + renders non-blank · the SOUL section schema (Name · Tone · Communication style · Trust · Learns-from · Voice deltas) · the `cmd_status` SOUL.md pointer · the SKILL.md "read each session" instruction · 3-tree byte-identical sync.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: SOUL.md — a living "voice" doc (named **Trusting**) scaffolded at setup, shipped by the
installer, and read each session. It carries the AI's tone, communication style, and what keeps the
human's trust, in a stable SECTION SCHEMA the self-improve loop (task 6) later rewrites toward the
human's wording.
Framings weighed: a survivor-layer living doc added to SETUP_FILES + a template + a session-read hook
(chosen — peer to PROJECT.md, reuses the never-clobber scaffold + 3-tree sync the engine already has) ·
a brand-new engine subsystem/command for "voice" (rejected — over-built; the survivor-doc rails already
fit) · bake the voice into the skill prompt only, no file (rejected — not a living doc, can't self-improve
or be human-owned per file).
Must:
<must>
  - `"SOUL.md"` is a member of `SETUP_FILES`, so `cmd_init` scaffolds `.add/SOUL.md` at setup
    (never-clobber: an existing SOUL.md is left untouched; skip-if-blank holds).
  - `templates/SOUL.md.tmpl` exists in all 3 tooling/templates trees and renders NON-BLANK, carrying
    the SOUL section schema: Name · Tone · Communication style · Trust · Learns-from · Voice deltas.
  - the schema marks the voice HUMAN-OWNED — the shipped "Trusting" prose is a PROPOSED starter the
    human edits/confirms; the self-improve loop (soul-self-improve) is the only writer of voice deltas.
  - `cmd_status` prints an existence-gated pointer to `.add/SOUL.md` (the voice — read each session),
    sibling to the PROJECT.md pointer.
  - SKILL.md "Always start here" instructs reading `.add/SOUL.md` when orienting (read each session).
  - the installer ships the template: the `_bundled` copy of `templates/SOUL.md.tmpl` is byte-identical
    to canonical; all 3 trees (engine + skill + templates) stay byte-identical.
</must>
Reject:
<reject>
  - SETUP_FILES gains "SOUL.md" but no template exists -> `cmd_init` would skip-if-blank and print the
    "template missing/blank — skipped" warning, scaffolding NO SOUL.md -> test stays red (never ship a
    dangling member).
  - the schema omits any of the six sections, OR hard-codes the voice as a non-overridable identity claim
    -> content test red (the doc must stay a human-owned, self-improvable schema, not a frozen manifesto).
</reject>
After:
<after>
  - `add.py init` on a fresh repo drops `.add/SOUL.md` with the Trusting schema; `add.py status` points to
    it; the skill reads it each session; the installer's bundled template matches canonical.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] the shipped "Trusting" voice PROSE is my draft, not the human's words — lowest confidence because
    voice/tone is identity-owned (a direction decision), and I'm seeding a starter before the human has
    spoken. Mitigated three ways: (1) the schema marks it explicitly human-owned + overridable, (2) tests
    assert the SCHEMA/mechanism only, NEVER the specific tone words — so the human can rewrite the voice
    without breaking the build, (3) soul-self-improve (task 6) is the loop that converges it to their
    wording. STILL surfaced OPEN to the human at the seam rather than silently locked; if wrong: they
    rewrite the prose, zero mechanism rework.
  - [ ] [contract] one SOUL.md per project (not per-milestone, not multi-project shared) — matches the
    milestone "Out" scope; if wrong: a later task scopes it.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: init scaffolds SOUL.md
  Given a fresh repo with no .add/
  When add.py init runs
  Then .add/SOUL.md exists and is non-blank
  And it carries the schema sections Name/Tone/Communication style/Trust/Learns-from/Voice deltas

Scenario: SOUL.md is in the survivor layer (never-clobber)
  Given a project that already has a customised .add/SOUL.md
  When add.py init --force re-runs
  Then the existing SOUL.md is left untouched (survivor-layer never-clobber)
  And no other survivor doc is clobbered

Scenario: the voice is marked human-owned and overridable
  Given a reader opens the scaffolded SOUL.md
  When they read the Trusting voice
  Then it is explicitly marked human-owned / overridable (a proposed starter, not a frozen claim)
  And it points at the self-improve loop as the writer of voice deltas

Scenario: status points at SOUL.md each session
  Given a project with .add/SOUL.md present
  When add.py status runs
  Then it prints a pointer to .add/SOUL.md (the voice — read each session)
  And the PROJECT.md context pointer still prints

Scenario: the skill reads SOUL.md when orienting
  Given a reader opens SKILL.md "Always start here"
  When they follow the orient steps
  Then they are told to read .add/SOUL.md (the voice) each session

Scenario: the installer ships the template (3-tree parity)
  Given the canonical templates/SOUL.md.tmpl
  When the bundle + dogfood trees are compared
  Then SOUL.md.tmpl is byte-identical across canonical · dogfood · bundle
  And add.py + SKILL.md stay byte-identical across their 3 trees

Scenario (reject): a SETUP_FILES member with no template scaffolds nothing
  Given "SOUL.md" in SETUP_FILES but templates/SOUL.md.tmpl missing
  When add.py init runs
  Then no .add/SOUL.md is created (skip-if-blank) and a warning prints
  And the test stays red — a dangling member never ships

Scenario (reject): a schema missing a section stays red
  Given a SOUL.md.tmpl that omits one of the six schema sections
  When the content suite runs
  Then it fails (red)
  And no existing survivor template is altered to make it pass
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE + DOC CONTRACT — SOUL.md survivor-layer living doc (named "Trusting")

add.py:SETUP_FILES  MUST contain "SOUL.md"
  -> cmd_init scaffolds .add/SOUL.md from templates/SOUL.md.tmpl (never-clobber, skip-if-blank)

templates/SOUL.md.tmpl  MUST exist (3 trees) AND render non-blank, containing the section schema:
    "# SOUL"  (or "SOUL.md" title)  + the literal name token "Trusting"
    section markers (case-insensitive): "Tone" · "Communication style" · "Trust"
                                        · "Learns from" · "Voice deltas"
    a human-owned marker: the words "human-owned" AND "overridable" (or "starter")
    a self-improve pointer: names "soul-self-improve" (the loop that writes voice deltas)

add.py:cmd_status  MUST print, when .add/SOUL.md exists:
    a line containing "SOUL.md" AND "voice"  (existence-gated; PROJECT.md pointer still prints)

SKILL.md "Always start here"  MUST instruct reading ".add/SOUL.md" (the voice) when orienting

Parity: add.py · SKILL.md · templates/SOUL.md.tmpl each byte-identical across the 3 trees
        (canonical · .add dogfood · _bundled). engine_pin.ENGINE_MD5 re-pinned (add.py changed).
Schema: docs + engine; no state.json shape change (SOUL.md is a file survivor, not a state key).
Tests assert the SCHEMA + mechanism ONLY — never the specific Trusting tone words (the voice stays
        human-owned: the human may rewrite the prose without breaking any test).
```

Status: FROZEN @ v1 — approved by Tin Dang (autonomous authorization 2026-06-15; voice CONTENT surfaced OPEN to the human at the seam — see §1 ⚠ flag)
Least-sure flag surfaced at freeze: [spec] the shipped "Trusting" voice PROSE is my draft, not the human's words — voice/tone is identity-owned. The contract deliberately freezes only the SCHEMA + mechanism (tests never assert the tone words), so the human can rewrite the voice with zero mechanism rework; the starter is explicitly marked human-owned + overridable and the self-improve loop converges it to their wording. Surfaced OPEN, not silently locked.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: SETUP_FILES membership + scaffold + schema + status pointer + skill read + 3-tree parity
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_soul_in_setup_files: assert "SOUL.md" in add.SETUP_FILES
  - test_init_scaffolds_soul: in-process init in a tmp dir / assert .add/SOUL.md exists + non-blank
    + contains "Trusting" and the six section markers
  - test_soul_never_clobbered: write a custom .add/SOUL.md / init --force / assert it is unchanged
  - test_soul_marked_human_owned: assert the template says "human-owned" AND "overridable"/"starter"
    AND names "soul-self-improve"
  - test_status_points_at_soul: init then capture status stdout / assert a line names "SOUL.md" + "voice"
    + assert the PROJECT.md context line still prints
  - test_skill_reads_soul_each_session: assert SKILL.md "Always start here" region names ".add/SOUL.md"
  - test_template_three_trees_identical: SOUL.md.tmpl byte-identical across canonical · dogfood · bundle
  - test_skill_three_trees_identical: SKILL.md byte-identical across the 3 skill trees (or rely on
    existing test_tree_parity/test_bundle_parity — assert here for the SOUL anchor specifically)
  - test_dangling_member_scaffolds_nothing (reject): simulate a missing template / assert skip-if-blank
    creates no file (use a name not backed by a template, or monkeypatch _templates_dir)
</test_plan>

Tests live in: `tooling/test_soul_artifact.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/templates/SOUL.md.tmpl` `.add/tooling/templates/SOUL.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/SOUL.md.tmpl` `add-method/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md`
Strategy (ordered batches): 1. write canonical `templates/SOUL.md.tmpl` (schema + Trusting starter, human-owned markers) · 2. add `"SOUL.md"` to `SETUP_FILES` + the `cmd_status` SOUL pointer in canonical add.py · 3. add the session-read line to canonical SKILL.md · 4. re-pin `engine_pin.ENGINE_MD5` to the new add.py digest · 5. sync: `cp` add.py + SKILL.md + template to `.add` dogfood, run `prepare_bundle.py` to regenerate `_bundled` · 6. full suite green (watch wording lint + parity + engine_pin)
Safety rule (feature-specific): cmd_init/cmd_status changes are additive + existence-gated (no new IO failure path); never-clobber + skip-if-blank preserved; the voice prose is human-owned (tests never assert tone words)
Code lives in: the 3 tooling trees (add.py + templates) + the 3 skill trees (SKILL.md); canonical is source, dogfood + bundle are synced copies; engine_pin.py is the single MD5 pin
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1085 green (was 1077; +8 in test_soul_artifact)
- [x] coverage did not decrease — net +8 tests; test_add's SETUP_FILES census now also covers SOUL.md
- [x] no test or contract was altered during build — only the scoped engine/skill/template trees + engine_pin changed
- [x] the green was EARNED, not gamed — suite ran RED first (4 fail + 2 err: missing SETUP_FILES member, missing template, no status pointer, no skill line); GREEN only after the mechanism landed. The assertions check the MECHANISM + SCHEMA (membership, scaffold, never-clobber via real init --force, status pointer line, skill instruction, 3-tree parity, skip-if-blank via monkeypatched _templates_dir) — NOT the specific tone words, so the voice is not overfit and the human can rewrite it freely
- [x] concurrency / timing of the risky operation is safe — n/a; cmd_status pointer is existence-gated (no open/parse), cmd_init scaffold reuses the existing atomic-write + never-clobber path
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; additive docs + one print line + one tuple member; zero new deps
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree byte-identical sync honored (add.py · SKILL.md · SOUL.md.tmpl); ENGINE_MD5 re-pinned to 6c5ba081 with newest-first narrative
- [x] a person reviewed and approved the change — MECHANISM auto-resolved under autonomy=auto (autonomous authorization 2026-06-15). The VOICE CONTENT (identity-owned) is surfaced OPEN to the human at the milestone-close report — NOT auto-stamped; it is overridable with zero build impact

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `"SOUL.md"` in SETUP_FILES is consumed by cmd_init's render+write loop (~line 401); the cmd_status voice pointer prints under the existence guard; the SKILL.md instruction lives in "Always start here". All three confirmed by passing behavior tests (test_init_scaffolds_soul, test_status_points_at_soul, test_skill_reads_soul_each_session).
- [x] SEMANTIC (prose / non-code) — read SOUL.md.tmpl in full: the six schema sections (Name·Tone·Communication style·Trust·Learns-from·Voice deltas) present; the header marks it living + human-owned + overridable + a starter, names soul-self-improve as the only writer, says the engine never clobbers it. Wording lint green (fixed "wall of"→"not more than the work needs"; "human seam"→"human decision"). The Trusting voice is a PROPOSED default, not a frozen claim.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (autonomous authorization 2026-06-15; MECHANISM gate — voice content surfaced OPEN, not stamped) · date: 2026-06-15

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does the shipped "Trusting" starter voice actually fit the human, or do they rewrite it wholesale on first read? (the §1 ⚠ flag) — if wholesale, the starter was too opinionated; trim it toward a neutral schema in a §7 delta. Watch that the status `voice :` line + the SKILL.md read instruction actually change how sessions open.
Spec delta for the next loop: soul-self-improve (task 6) must define HOW a voice delta is observed + confirmed + written back into these six sections — this task ships the target schema but NOT the writer loop; the §6 "Voice deltas" section is the seam it plugs into.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the method had no first-class home for the AI's VOICE — tone/style/trust lived only in scattered global instructions; SOUL.md makes it a survivor-layer living doc the human owns (evidence: SETUP_FILES had no voice doc until this task; test_soul_in_setup_files now guards it)
- [ADD · folded] identity-owned content can ship as a PROPOSED, test-unlocked starter — the gate attests the mechanism while the human keeps the voice (evidence: tests assert schema not tone words; the §3 freeze explicitly carves the voice prose out of the contract)
