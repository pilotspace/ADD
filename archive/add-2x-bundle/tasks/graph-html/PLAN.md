# PLAN: graph --html: engine emits a self-rendering HTML page to tmp

slug: graph-html · created: 2026-07-23 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 0 · GROUND — the observed map (anchors opened live 2026-07-23)

- `add-method/tooling/add.py` · `cmd_graph` (1454) — builds `lines` (flowchart TD + subgraphs + edges + the `--signals` overlay: sig_ signals, ec_ exit-criteria) then `print("\n".join(lines))` at the tail (1704). The `--html` branch intercepts THAT tail: same `lines`, wrapped in an HTML page + written to a file instead of printed.
- `add-method/tooling/add.py` · `_exit_criterion_nodes(root)` (exit-criterion-nodes, DONE) — reused to compute the met/total criteria chip when `--milestone` is set.
- `tempfile` (23) + `os` (18) already imported — the default out-path is `tempfile.gettempdir()` ("tmp"), STABLE per scope (no random component → testable), overwrite each run.
- Render floor: mermaid.js is ~3 MB and add.py is 4-way byte-twinned — vendoring it inline is a non-starter; the page pulls a PINNED mermaid from a CDN `<script>` (renders when opened online). The engine authors the chrome (title · status chips · legend), never the library.
- Four tooling trees stay byte-identical + `engine_pin.py` ENGINE_MD5 re-pins (add.py-only → ENGINE_PKG_MD5 holds).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py graph` gains an opt-in `--html [--out PATH]` mode — instead of printing raw mermaid, it writes a self-styled, self-rendering HTML page (title · done/met status chips · legend · the mermaid diagram in a `<pre class="mermaid">` + a pinned-CDN mermaid `<script>`) to a temp file and prints the path. Open it in a browser → the rendered graph. Default (no `--html`) output is byte-unchanged.
Framings weighed: styled page + pinned-CDN mermaid script (chosen — self-renders on open; the engine owns the chrome, the CDN owns the 3 MB library the twins can't carry) · vendor mermaid.min.js inline (rejected — 3 MB × 4 twins breaks the parity/lean floor) · emit HTML with no script, paste-to-render (rejected — doesn't render, the very thing this task removes)
Must:
<must>
  - M1 html mode: `graph --html` builds the SAME mermaid `lines` as today, wraps them in an HTML page, writes it to a file, and prints the absolute path (never the raw mermaid to stdout).
  - M2 tmp default + override: with no `--out`, the file lands under `tempfile.gettempdir()` at a STABLE name (scope-derived, no random part); `--out PATH` overrides the destination. The parent dir is created if missing.
  - M3 self-rendering page: the page contains `<pre class="mermaid">` holding the diagram (HTML-escaped so no `<`/`>`/`&` breaks parsing) AND a pinned mermaid `<script>` + an `mermaid.initialize` init call — so opening it renders without a manual paste.
  - M4 status chrome: the page shows a `<title>` naming the scope and status chips — tasks done/total in view, and (when `--milestone` is set) exit-criteria met/total via `_exit_criterion_nodes`.
  - M5 default unchanged + pure over the board: `graph` (no `--html`) still prints raw mermaid byte-identical to today; the board is READ-only (the only write is the requested output file).
  - M6 engine parity: add.py byte-identical 4-way + `engine_pin.py` ENGINE_MD5 re-pinned (ENGINE_PKG_MD5 unchanged).
</must>
Reject:
<reject>
  - a `--out` whose parent dir is missing -> the dir is created, the file written (never a crash) -> "out_parent_created"
  - `--html` combined with `--signals`/`--milestone` -> the overlay/filter still apply; the HTML wraps whatever `lines` those produced -> "overlay_composed"
</reject>
After:
<after>
  - `graph --signals --html` writes a rendered page to tmp and prints its path; opening it in a browser shows the graph without a manual paste; `graph` alone is unchanged
</after>
Boundary: inputs are the existing board (via cmd_graph's `lines`) + the optional `--out PATH`; tests must speak the default tmp path, an explicit `--out`, an `--out` under a missing dir, and the no-flag mermaid default.
<assumptions>
  ⚠ pulling mermaid from a pinned CDN (vs. a vendored/offline copy) is acceptable — if wrong: the page needs network on first open to render. Mitigated: the 3 MB library cannot ride in a 4-way byte-twinned add.py; the diagram source is fully in the file (degrades to a readable `<pre>` offline), and a `--out` into a repo that already vendors mermaid is a later, additive option. Cost if wrong is a network dependency at view-time, not a data or contract change.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
  - Given a live board, When `graph --signals --html` runs, Then a file is written under tempdir, its path printed, and it contains `<pre class="mermaid">` + the diagram + a mermaid `<script>` — and no raw mermaid on stdout.
  - Given `--out /some/new/dir/g.html` whose dir does not exist, When `graph --html --out ...` runs, Then the dir is created and the file written.
  - Given `--milestone signal-graph`, When `graph --html --milestone signal-graph` runs, Then the page's chips show 4/4 tasks done and 5/5 criteria met.
  - Given no `--html`, When `graph` runs, Then stdout is byte-identical raw mermaid (no HTML written).
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — HARD, tamper-guarded)

```
argparse: `graph` gains  --html (store_true)  and  --out PATH (default None).

cmd_graph tail (additive; default path byte-unchanged):
  mermaid = "\n".join(lines)                    # the SAME lines built today (incl. --signals overlay)
  if not args.html:
      print(mermaid); return                    # today's behavior, byte-identical

  # status chrome
  done = count(shown tasks with phase == "done"); total = len(shown)
  ecs  = [n for n in _exit_criterion_nodes(root) if not only or n["ms"] == only]
  met  = count(ecs met); ectot = len(ecs)
  title = only or "ADD graph"

  html = _graph_html_page(title, mermaid, done, total, met, ectot, bool(only))
      -> <!doctype html> + engine-authored <style> (theme-aware; light diagram plate)
         + <title> + status chips + legend
         + <pre class="mermaid">{HTML-escaped mermaid}</pre>
         + <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
         + <script>mermaid.initialize({startOnLoad:true})</script>

  out = Path(args.out) if args.out else Path(tempfile.gettempdir()) / f"add-graph{'-'+only if only else ''}.html"
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(html, encoding="utf-8")
  print(f"wrote {out}")
  print("open it in a browser to view the rendered graph")
```
Schema: no state/store write; the ONLY disk write is the requested output HTML file. `_exit_criterion_nodes`/`_signals`/add_engine untouched (ENGINE_PKG_MD5 stable). Pure read of the board.

Target (measurable): `graph --html` writes a file under tempdir (or `--out`), prints its path, and the file contains `<pre class="mermaid">` + `flowchart TD` + a `mermaid.initialize` call; `--out` under a missing dir succeeds; `--milestone signal-graph` chips read 4/4 + 5/5; `graph` (no flag) stdout byte-identical to today; `test_graph_html_*` green; graph/parity/pin regression floor green; add.py 4-way identical, ENGINE_PKG_MD5 unchanged.
Least-sure flag surfaced at freeze: [contract] the rendered page pulls a PINNED mermaid from a CDN `<script>` rather than a vendored offline copy — chosen because the 3 MB library cannot ride a 4-way byte-twinned add.py and the diagram source is fully embedded (readable offline, renders online); a repo-vendored-mermaid `--out` mode is additive later. The network dependency is at view-time only, never in the engine.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `./tests/`
Regression floor: the graph test(s) (`test_graph_views`, `test_graph_view_signals`) + tree parity + engine pin — run green before the gate.
Persona (required): `.add/personas/methodology-engine-dev.md` (deterministic, fail-loud engine work; advisory, never lowers a gate)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_graph_html_writes_file_to_tmp: `graph --html` with no --out writes under tempfile.gettempdir(), prints the path, no raw mermaid on stdout · covers: M1,M2
  - test_graph_html_out_override_and_mkdir: `--out <newdir>/g.html` creates the missing dir + writes the file · covers: M2, R:out_parent_created
  - test_graph_html_self_rendering: the file contains `<pre class="mermaid"`, `flowchart TD`, and a `mermaid.initialize` script · covers: M3
  - test_graph_html_escaped_diagram: the mermaid block is HTML-escaped (no raw unescaped `<` from any label) yet holds the diagram · covers: M3
  - test_graph_html_status_chrome: `--milestone signal-graph` page shows 4/4 tasks + 5/5 criteria chips · covers: M4
  - test_graph_default_still_mermaid: `graph` (no --html) prints raw mermaid to stdout, writes no file · covers: M5
  - test_graph_html_three_trees_identical: add.py byte-identical across the tooling trees · covers: M6
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — added `_graph_html_page(...)` (theme-aware chrome + HTML-escaped `<pre class="mermaid">` + pinned mermaid@11 CDN `<script>` + `mermaid.initialize`) and a `--html`/`--out` argparse pair; the cmd_graph tail now branches: `--html` wraps the SAME `mermaid` string, writes to `--out` or a stable `tempfile.gettempdir()/add-graph[-<ms>].html`, mkdir -p the parent, prints the path — else prints raw mermaid byte-identical. Status chips computed from `shown`/`_exit_criterion_nodes`. add.py-only → ENGINE_PKG_MD5 held (81553881); ENGINE_MD5 e7ad9f97→5c769b93 + 4-way sync. Test fixture fix pre-freeze: the escaped-diagram case needed a real depends-on edge (`relate b --depends-on a`) to produce a `-->` to escape. Dogfood: `graph --signals --milestone signal-graph --html` wrote /var/folders/.../T/add-graph-signal-graph.html.
Code lives in: `add-method/tooling/` (add.py + engine_pin.py, 4-way; add_engine untouched)
Constraints: do NOT change any test or the frozen §3 contract; do NOT edit add_engine (keep ENGINE_PKG_MD5); stay inside §3 Scope; keep default `graph` byte-identical; repin ENGINE_MD5 + sync 4-way.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all §4 tests pass — including graph + parity + pin floor
- [ ] coverage did not decrease
- [ ] no test or contract altered during build
- [ ] the green was EARNED — test_graph_default_still_mermaid proves the raw path held
- [ ] the only disk write is the requested output file (no state/store write); ENGINE_PKG_MD5 unchanged
- [ ] a person reviewed and approved the change

### GATE RECORD
Reported: no
Outcome: PASS | RISK-ACCEPTED | HARD-STOP
Reviewed by: name · date: date

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
harvested at done

### Spec delta
- [SPEC · open] the page pulls mermaid from a pinned CDN (network at view-time); a repo-vendored-mermaid `--out` mode (fully offline render) is a deferred additive follow-up if an air-gapped render is ever needed (evidence: test_graph_html_self_rendering asserts the CDN `<script>` + init; the diagram source is fully embedded so it degrades to a readable `<pre>` offline)

### Competency deltas
- [ADD · open] a render/export feature stays engine-lean by owning only the CHROME (title/chips/legend/escaping) and delegating the heavy renderer (3 MB mermaid.js) to a pinned CDN — vendoring it would have broken the 4-way byte-twin parity floor (evidence: add.py-only diff, ENGINE_PKG_MD5 unchanged, tree-parity 6 green)
- [ADD · open] `--html` reused the EXISTING `mermaid` string (the same `lines` the default path prints) rather than re-deriving the graph — the escape+wrap is a pure post-step, so `graph`/`graph --signals`/`--milestone` all compose into `--html` for free (evidence: test_graph_default_still_mermaid byte-identical + status-chrome test on --milestone)
