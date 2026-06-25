# Components — monorepo and multi-repo slices

Opt-in pillar for a milestone that spans **more than one green bar** — a backend
and its frontend, a shared lib and two apps, services across repos. A project
that declares no components is byte-identical to a single-codebase project. Reach
for this only when one milestone genuinely crosses components. Full narrative:
book chapter `17-components.md`.

## Declare (never inferred)

`.add/components.toml`:

```toml
[component.gateway]
root      = "apps/gateway"
green-bar = "pytest + pyright"
[component.dashboard]
root      = "apps/web"
green-bar = "vitest + a11y"
```

A task binds with a `component: <name>` header line → that root joins its §5
Scope, and verify holds it to that component's green-bar.

## The loop

1. **Per-component verify.** A bound task must CITE its component's green-bar in
   the §6 Build-expectations evidence, or the gate refuses
   `component_green_bar_uncited`. The engine never runs the suite — you run the
   right one; the gate checks the right bar was cited.
2. **Freeze a cross-component contract.** Declare `[contract.<id>]`
   (producer + consumers). A task names its role `produces: <id>` / `consumes: <id>`.
   The producer's freeze (contract→tests) writes the immutable snapshot
   `.add/contracts/<id>.json`; the consumer pins its hash. A changed re-freeze
   flags consumers `contract_consumer_stale`; a missing/malformed snapshot
   HARD-STOPS — never build against an unfrozen shape.
3. **One milestone, full slice.** A `consumes:` task is HELD from advancing
   scenarios→contract (`producer_contract_unfrozen`) until the producer's
   snapshot exists. The FE stays downstream of the frozen BE endpoint, in one
   milestone.
4. **Across repos — federate.** A consumer repo declares `[federation.<id>]`
   (`source` + optional `pin`); `add.py federate pull <id>` validates and lands a
   byte-for-byte copy of the producer repo's published snapshot locally, where it
   behaves as in a monorepo. Fail-loud: unknown id / unreadable source / invalid
   snapshot / version mismatch each HARD-STOPS and lands nothing.

## Hold the line

- **Declared, not inferred** — no scanning `apps/*`.
- **No central server / no shared mutable state** — federation copies an
  immutable snapshot; each repo keeps its own git-native `state.json`.
- **No new approval** — these are engine-enforced gates on the existing six-step
  flow, not extra human checkpoints. Ownership/autonomy per component is the
  identity story (`streams.md`, governance), layered on this graph.
