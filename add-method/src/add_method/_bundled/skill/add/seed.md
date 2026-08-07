# Seed — give a fresh bundle its starter personas (setup, opt-in)

At setup — right after `add init`, before the first task — offer to seed one or two **starter
personas** that fit the project's domain. Seeding is **opt-in and additive**: a bundle with no
personas behaves exactly as the plain 3-beat loop. Skip it for a throwaway; do it for anything that
will grow. You propose; **the human confirms**; nothing is seeded without that.

A seeded persona changes **nothing** until a task applies one through the roster (`streams.md`). Seed
writes `.add/personas/<slug>.md` and nothing else — no gate moves, no behavior shifts.

## Ground the domain first (read, don't guess)

The teacher does not tell you which lens this project needs — the specs do. Read the two that frame
the domain:

- `.add/specs/domain.md` — what this system is *about* (the entities, the rules of its world).
- `.add/specs/system.md` — how it is *built* (the stack, the boundaries, the constraints).

From those, name the one or two lenses the work will most want — a payments system wants the
money-exact backend lens and the security lens; a dashboard wants the experience lens. Do not seed a
lens the project has no use for; an unused persona is dead weight (`personas.md`).

## Distil from the teacher — never invent

The corpus of worked archetypes lives at the engine's `.add/personas-teacher/`
(`backend-systems` · `security-reviewer` · `frontend-ux`, and any others vendored there) — and `add
init` **vendors a copy into `.add/personas-teacher/`**, so a bundle carries its own teacher
even away from this repo. Don't start blank and don't copy whole: **distil the nearest teacher entry
to this project**, then own it.

For each persona the human confirms:

```bash
add new Persona <slug> --title "<one-line lens>"   # scaffolds .add/personas/<slug>.md — no lifecycle, no freeze
```

Then **edit that file directly** (there is no author verb) to fill the four machine-readable parts,
adapted to *this* codebase's reality:

- **Identity** — the stance with earned perspective (scars, not a résumé).
- **Critical Rules** — this domain's non-negotiables, each `**clause** — the why`; a **named budget
  over an adjective** (`p95 < 200 ms`, `4.5:1`), never a vague "fast".
- **Default Requirement** — the one thing in every deliverable by default.
- **Success Metrics** — measurable invariants, each with the failure it guards. **Never invent a
  statistic** (`engagement +40%` is the signature rot of a weak corpus) — only a number the lens can
  check in-session.

Add the recommended frontmatter — `flow:` (which surfaces load it) and `use-when:` / `not-when:` (the
boundary that routes it over a sibling) — so the roster can select it later.

## Present the seed as a guided choice

This is a setup decision, so run it through `gate.md`: open with the ARC, show the drafted persona(s)
BEFORE the ask, and let the human accept, edit, or decline each. Seed only what returns confirmed. A
persona seeded and never used by a milestone's end is a prune candidate at close (`personas.md` §Grow).

## What seed does NOT do

<constraints>
- **No lifecycle.** A persona never freezes and never gates — it is a living doc; `add new Persona`
  creates it with no task status (it shows `[—]`, like a Spec). Do not drive it through the beats.
- **No behavior change on seed.** Writing a persona changes nothing until a task adopts it via the
  roster (`streams.md`). Seeding is preparation, not application.
- **The human folds; the AI never self-grows.** Personas sharpen through the delta loop at close
  (`personas.md` §Grow · `deltas.md`), never by the engine and never by silent self-edit.
</constraints>

→ persona schema + grow/apply: `personas.md`. Delegating a beat to one: `streams.md`.
