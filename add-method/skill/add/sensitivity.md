# Sensitivity — the project's risk-class vocabulary

A task declares its risk-CLASS with a `sensitivity:` line in the TASK header — *what
kind* of risk it carries, distinct from `risk:` (*how much*). The engine validates +
surfaces the human's declaration; it **never classifies**. Read live by freeze/status/check.

## The base four (method-universal — always apply)

- **security** — authn/authz, secrets, crypto, attack surface. A finding here is HARD-STOP;
  the human is in the loop in EVERY tier (never advisor-gated, never auto-passed).
- **data** — persistence, migrations, privacy of stored records, data loss.
- **architecture** — module boundaries, contracts, cross-cutting structure.
- **mechanical** — rote, low-impact change (rename, move, format, doc). The only class
  a recorded advisor verdict (three §6 fields: Verdict · Residue · Binding) can gate for
  auto-completion (`advisor-gate-relax`).

These four can't be removed — a project only EXTENDS them.

## Extend per project (you maintain this)

Domain risk-classes live in `.add/GLOSSARY.md` under a `## Sensitivity classes` section,
one `- <token>: <definition>` bullet per line:

```markdown
## Sensitivity classes
Base (always apply): security · data · architecture · mechanical
- pii: personally identifiable information; any task touching it escalates to human review
- payments: money movement; reconciliation + an audit trail are required
```

`freeze` then accepts a header `sensitivity:` value from **base ∪ your domain classes**;
a token in neither is refused `sensitivity_invalid`. `status` prints the active task's
class; `check` nudges (`sensitivity_classes_unset`, never red) until you declare some.

## The AI's job — keep it current

- When a milestone or task reveals a **new kind of risk** this project carries (a regulated
  data category, a payment rail, a tenancy boundary), ADD it as a class with a one-line
  definition — propose it, the human confirms (it is foundation, like a glossary term).
- **Re-read the section each session** (it rides `GLOSSARY.md`); pick the tightest class
  when you declare a task's `sensitivity:` at freeze.
- **Map domain → base behavior** in the definition so downstream gating is unambiguous —
  e.g. "pii … escalates to human review" pins it as human-floor, not advisor-gatable.

## Hold the line

- **Declared, never inferred** — the engine reads your token; it does not guess a class.
- **Base four are universal** — domain classes add to them, never replace them; security
  stays a human floor in every tier.
- **A comment is never a declaration** — commented-out example bullets don't count; only a
  real `- <token>:` line under the section is a class.
