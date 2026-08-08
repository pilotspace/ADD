════════════════════════════════════════════════════════════════════════
 signal-graph · Unified signal graph — note = todo = delta as nodes
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  5/5 met
 GATES     4 PASS             WAIVERS   none

 goal  Unify the three off-graph observation primitives (ephemeral note,
       todo, §7 delta) into ONE addressable signal node with a status
       lifecycle and edges, promote exit-criteria to delivered-by nodes,
       and render them through cmd_graph as a VIEW over existing text —
       no new persistence store; the honesty layer's output becomes
       navigable, not just readable
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 signal-model                done      PASS 9     ●●●●
 graph-view-signals          done      PASS 6     ●●●●
 exit-criterion-nodes        done      PASS 7     ●●●●
 atomicity-signal            done      PASS 11    ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   signal-model             PASS Tin Dang <tindang.ht97@gmail.com>
   graph-view-signals       PASS Tin Dang <tindang.ht97@gmail.com>
   exit-criterion-nodes     PASS Tin Dang <tindang.ht97@gmail.com>
   atomicity-signal         PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (7 carried)
   • ADD · open · an engine edit in this repo is a 4-way twin + md5-pin
     coupling, not a single-file change — the scope-atomicity nudge this
     milestone will build should itself flag a §3 Scope that names
     add.py without the tooling dir (evidence: 2 parity reds surfaced
     only at the gate, not at freeze) (evidence: engine_pin.ENGINE_MD5
     repin + REPO/.add twin sync both mandatory)
   • ADD · open · declaring the tooling DIR (not add.py the file) in §3
     Scope from the start made the engine_pin repin + 4-way sync
     in-scope — the signal-model return-to-build did not recur here
     (evidence: gate passed first attempt; scope-echo showed
     .add/tooling/ [ok])
   • ADD · open · folding exit-criteria into the existing `--signals`
     overlay (the frozen least-sure flag) paid off — ONE honesty
     surface, no second flag, and the ec_ block reuses the signal
     block's x_ fallback + text-sanitize verbatim; a later `--goals`
     split stays additive (evidence: 7 green, default `graph`
     byte-unchanged via test_graph_default_no_exit_nodes +
     test_graph_views 9 green)
   • ADD · open · declaring the tooling DIRS in §3 Scope up front
     (graph-view-signals lesson) again avoided the signal-model
     return-to-build — the engine_pin repin + 4-way sync landed
     in-scope, first-pass gate (evidence: check 446/0, tree-parity 6
     green)
   • ADD · open · "no new store" ≠ "no writes" — seeding into the
     EXISTING `state["todos"]` store honored the thin-engine floor while
     making the nudge persistent+addressable; the store choice (todo vs
     §7 delta) followed altitude (an intake-time backlog jot IS a todo)
     (evidence: test_seed_appends_captured_signal green, ENGINE_PKG_MD5
     unchanged, no new state key)
   • ADD · open · a self-referential engine feature must be
     dogfood-checked against ITSELF at freeze — verified
     atomicity-signal's own §3 reads as [] before freezing so the new
     hook wouldn't spuriously self-seed (evidence:
     `_scope_parts('.add','atomicity-signal') == []`; freeze emitted no
     seed note)
   • ADD · open · declaring the tooling DIRS in §3 Scope up front
     (signal-model lesson) again gave a first-pass gate — engine_pin
     repin + 4-way sync in-scope, no return-to-build (evidence: freeze
     scope-echo all [ok], check 452/0)

 SPEC DELTAS    43 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone signal-graph
════════════════════════════════════════════════════════════════════════