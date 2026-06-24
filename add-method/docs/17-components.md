# 17 · Components — monorepo and multi-repo

[← 16 Releasing](./16-releasing.md) · [Contents](./README.md) · Next: [Appendix A Templates →](./appendix-a-templates.md)

---

Most of this book treats a project as one codebase with one green bar. Real
systems are rarely that tidy: a backend and a frontend, a shared library and two
apps, or three services across three repos. ADD models all of these the same
way — as a **graph of components**. A component owns a source root, its own
green bar, and the contracts it produces or consumes. With that, **one milestone
can ship a vertical slice across components** — a backend endpoint and the
frontend that calls it — instead of splitting the slice across milestones.

This pillar is **opt-in and additive**: a project that declares no components
behaves exactly as the rest of the book describes. You reach for it only when a
milestone genuinely spans more than one green bar.

## Declare the components

Components are **declared, never inferred** — ADD does not scan `apps/*` and
guess. You name them in `.add/components.toml`:

```toml
[component.gateway]
root      = "apps/gateway"
green-bar = "pytest + pyright"

[component.dashboard]
root      = "apps/web"
green-bar = "vitest + a11y"
```

Each component owns a **root** (the source subtree it governs) and a
**green-bar** (the suite + checks that prove *that* component healthy). A task
binds to a component with a `component:` header line; the component's root is
then added to the task's §5 Scope automatically. A project with no
`components.toml`, or a task with no `component:` line, is byte-identical to a
single-component project.

## Verify each task against its own green bar

In a mixed milestone, a backend task and a frontend task pass on **different
toolchains**. The verify gate enforces this per component: a task bound to
`gateway` must cite its component's green-bar (`pytest + pyright`) in the §6
Build-expectations evidence, or the gate refuses `component_green_bar_uncited`.
The engine never *runs* the suite — that invariant holds here too. The AI runs
the right suite for the bound component; the gate checks the **right bar was
cited** in the evidence. Two tasks, one milestone, two green bars — each held to
its own.

## Freeze a contract between components

When one component produces an interface another consumes, that boundary needs a
**frozen, machine-checkable contract**. Declare it, name its producer and
consumers:

```toml
[contract.gateway-api]
producer  = "gateway"
consumers = ["dashboard"]
```

A task declares its role with a header line — `produces: gateway-api` or
`consumes: gateway-api`. When the **producer** task freezes its §3 and crosses
contract→tests, the engine writes an immutable snapshot at
`.add/contracts/gateway-api.json` (id, producer, version, frozen date, and a
hash over the frozen §3 shape). When a **consumer** task crosses contract→tests,
it **pins** that live hash. If the producer later re-freezes a *changed* shape,
`add.py check` flags every consumer `contract_consumer_stale` — a §7 delta to
re-pin against the new shape. A missing or malformed snapshot is a HARD-STOP, not
a guess: the consumer never builds against a shape that was never frozen.

## One milestone, a full-stack slice

The reason to put a producer and a consumer in the *same* milestone is to ship a
vertical slice — but the frontend must not commit to an endpoint the backend has
not frozen yet. ADD enforces that ordering with a **hold**: a `consumes:` task
cannot advance scenarios→contract (it cannot write its §3) while its producer's
snapshot does not yet exist. The engine refuses `producer_contract_unfrozen` and
the task stays at `scenarios`. Once the backend freezes its contract, the
frontend proceeds and pins it. The slice is **ordered by the frozen contract**,
all inside one milestone — the FE stays downstream of the BE endpoint, not split
into a later milestone.

## Across repositories: federation

Components in separate repositories work the same way; only the
**snapshot transport** differs. A consumer repo declares where a producer repo
publishes its frozen contract:

```toml
[federation.gateway-api]
source = "../gateway/.add/contracts/gateway-api.json"
pin    = "v1"        # optional — the version this repo expects
```

`add.py federate pull gateway-api` reads that source, validates it (valid JSON,
matching id, a hash, and — if `pin` is set — a matching version), and lands a
**byte-for-byte copy** at the local `.add/contracts/gateway-api.json`. From
there, the consuming repo's task holds and pins exactly as in a monorepo. The
pull is **fail-loud by design**: an unknown id, an unreadable source, an invalid
snapshot, or a version mismatch each HARD-STOPS and lands nothing — federation
never builds an FE against a guessed or stale endpoint. The producer's snapshot
is the published artifact; "publishing" is committing that file in the producer
repo. Each repo keeps its own git-native `state.json`; federation transports only
the immutable frozen shape, never shared mutable state.

## What this pillar is not

- **Not auto-discovery.** Components are declared in `components.toml`, not
  inferred from the directory tree.
- **Not a central server.** Federation copies an immutable snapshot between
  repos; there is no shared service and no shared mutable state.
- **Not a new approval.** The component machinery rides the existing six-step
  flow and its single contract-freeze approval — it adds gates the engine
  enforces, not human checkpoints.

The whole pillar is structure, not policy: who *owns* a component and how
autonomy is set per component is the identity/governance story (chapters 11–12),
layered on top of this graph.

---

[← 16 Releasing](./16-releasing.md) · [Contents](./README.md) · Next: [Appendix A Templates →](./appendix-a-templates.md)
