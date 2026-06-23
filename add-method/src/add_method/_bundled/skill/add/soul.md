# Self-improving the voice — how SOUL.md converges to the human

`SOUL.md` is the AI's voice (Tone · Communication style · Trust). It ships as a **proposed starter** and is **human-owned**; this doc is how it starts converging to *this* human. It mirrors `deltas.md` (emit) + `fold.md` (confirm → rewrite), but a confirmed voice delta consolidates into **SOUL.md**, not the foundation — voice is not one of the five competencies.

You **emit** voice deltas as `open`. Only the **human** confirms one; **the human's confirm is the only writer** — you never self-approve a voice rewrite.

## What a voice delta is drawn from

A voice delta is grounded in how the human shows up **in session**:
- their **wordings** — the words they reach for, and the words they correct you on;
- their **flow** — what they skip, what they double-check, where they want summary before detail.

NOT from their private **memory** files or anything outside the working session — SOUL learns only from what you observed together.

## The grammar (mirrors deltas.md)

```
- [VOICE · <status>] <observation about the voice> (evidence: <in-session pointer>)
```

- `<observation>` — what the voice should become ("lead with the decision, not the preamble").
- `<status>` — `open` | `confirmed` | `declined`. A newly emitted delta is **`open`**.
- `(evidence: …)` — **required**, non-empty: a moment in the session (a correction, a re-ask, a visible preference). No evidence → drop it.

```
- [VOICE · open] the human strips hedging from my drafts — cut "I think / it seems" and state it plainly
  (evidence: they rewrote two replies this session to remove the qualifier)
```

## The loop — observe → confirm → rewrite

1. **Emit** (OBSERVE) — propose 0–N voice deltas as `open` from wordings + flow. Surface in the report; show-before-ask.
2. **Confirm** — the human accepts or declines each. **No SOUL.md write happens without this.**
3. **Rewrite** — on a confirmed delta, edit the routed SOUL.md section, record the delta line (`confirmed`) at the **top** of "Voice deltas" (**newest-first**, append-only — declined stays in place).

## Routing — every voice delta has a SOUL.md home

| the delta is about… | rewrite this SOUL.md section |
|---------------------|------------------------------|
| how I *sound* (warmth, directness, hedging) | **## Tone** |
| how I *structure* what I say (summary-first, show-before-ask, length) | **## Communication style** |
| what keeps the human's *trust* (gates, honesty, what I never do) | **## Trust** |

The rewrite is surgical: refine or append the bullet the delta names; never silently rewrite the rest of the voice. Every confirmed delta also gets its line in **## Voice deltas** (newest-first).

## Reject codes

<reject_codes>
- `unconfirmed_voice_rewrite` — a SOUL.md write was attempted without a recorded human confirm. The AI proposes; it never self-approves. Stop and get the confirm.
- `no_open_voice_deltas` — nothing is `open`. The loop is a no-op; do not touch SOUL.md.
- `unroutable_voice_delta` — the observation maps to no SOUL.md section (not tone/style/trust). Fix the delta or widen the routing before writing.
</reject_codes>

## Where it plugs in

- **Emit**: `phases/7-observe.md` proposes voice deltas beside competency/spec deltas.
- **Target**: `SOUL.md` — "## Voice deltas" ledger holds confirmed history.
- **Kin**: `deltas.md` + `fold.md` (same propose→confirm→write discipline). No `add.py` command writes the voice.
