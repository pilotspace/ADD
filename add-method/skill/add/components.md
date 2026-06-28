# Components — monorepo and multi-repo slices

Opt-in pillar for a milestone spanning **more than one green bar** — a BE + its
FE, a shared lib + two apps, services across repos. No components declared =
byte-identical to a single-codebase project. Full narrative: `17-components.md`.

## Declare (never inferred)

`.add/components.toml`:

```toml
[component.gateway]
root      = "apps/gateway"
green_bar = "pytest + pyright"
[component.dashboard]
root      = "apps/web"
green_bar = "vitest + a11y"
```

A task binds with a `component: <name>` header → that root joins its §5 Scope,
and verify holds it to that component's green-bar.

## The loop

1. **Per-component verify.** A bound task must CITE its green-bar in §6 evidence
   or the gate refuses `component_green_bar_uncited`. The engine never runs the
   suite — it **surfaces** the component's `verify` command (and records it in §6);
   you run it (NO-EXEC). The fast lane carries the same `component:` affordance.
2. **Freeze a cross-component contract.** Declare `[contract.<id>]`
   (producer + consumers). A task names its role `produces: <id>` / `consumes: <id>`.
   The producer's freeze (contract→tests) writes the immutable snapshot
   `.add/contracts/<id>.json`; the consumer pins its hash. A changed re-freeze
   flags consumers `contract_consumer_stale`; a missing/malformed snapshot
   HARD-STOPS — never build against an unfrozen shape.
3. **One milestone, full slice.** A `consumes:` task is HELD from advancing
   scenarios→contract (`producer_contract_unfrozen`) until the producer's snapshot
   exists — and `producer_contract_stale` if a live producer re-opened/drifted its
   §3 (freeze-recency). The FE stays downstream of the frozen BE, in one milestone.
4. **Across repos — federate.** A consumer repo declares `[federation.<id>]`
   (`source` + optional `pin`); `add.py federate pull <id>` validates and lands a
   byte-for-byte copy of the producer's snapshot locally. Fail-loud:
   unknown id / unreadable source / a `source` escaping the repo's allowlist
   (`federation_source_escapes`, confined to a repo-root sibling) / invalid
   snapshot / version mismatch each HARD-STOPS and lands nothing.

## Hold the line

- **Declared, not inferred** — no scanning `apps/*`.
- **No central server / no shared mutable state** — federation copies an immutable
  snapshot; each repo keeps its own `state.json`.
- **No new approval** — engine-enforced gates on the six-step flow, not extra human
  checkpoints. Per-component ownership/autonomy is the identity story (`streams.md`).
