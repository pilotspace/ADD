════════════════════════════════════════════════════════════════════════
 component-polish · component-polish — close the component-pillar gaps and harden the cross-repo edges
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     5/5 done           CRITERIA  5/5 met
 GATES     5 PASS             WAIVERS   none

 goal  give the component pillar an end-to-end worked example, a
       components.toml validator, freeze-recency safety, and a
       path-confined federation source
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 components-validator        done      PASS 24†   ●●●●●●●●●
 federation-harden           done      PASS 17†   ●●●●●●●●●
 cross-component-recency     done      PASS 13†   ●●●●●●●●●
 component-registry-fill     done      PASS 49†   ●●●●●●●●●
 component-worked-example    done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   components-validator     PASS Tin Dang <tindang.ht97@gmail.com>
   federation-harden        PASS Tin Dang <tindang.ht97@gmail.com>
   cross-component-recency  PASS Tin Dang <tindang.ht97@gmail.com>
   component-registry-fill  PASS Tin Dang <tindang.ht97@gmail.com>
   component-worked-example PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (14 carried)
   • ADD · open · a closed engine-owned config (components.toml) needs a
     measure-not-block typo lint surfaced at BOTH a dedicated
     `components` validator AND the existing CI `check` — the
     degrade-safe readers silently dropped real typos (evidence:
     components.md's own `green-bar` example was inert until this lint
     caught it)
   • SDD · open · a new CLI subcommand ripples into test_min_pillar
     LIFECYCLE + _NONZERO_OK classification + the tri-tree ENGINE_MD5
     pin — pre-listing those traps in §5 Known-problem fixes made the
     build trap-free (evidence: 0 surprises; the 2202-test suite went
     green on the first re-run after the re-pin)
   • ADD · open · a security-adjacent verify gate ESCALATES to the human
     even under autonomy:auto — the engine auto-resolves, but a
     disclosed residue (here: a TOCTOU) is human-signed, not auto-passed
     (evidence: this gate was human-decided PASS+forward-delta, not
     auto)
   • TDD · open · an adversarial path-confinement guard earns its green
     only via a bypass-probe refute-read (absolute · deep-traversal ·
     symlink-chains · NUL · ~/$VAR literalness · TOCTOU), not fixture
     coverage alone (evidence: security-expert's 7 probes turned the
     green from asserted to EARNED)
   • TDD · open · a new test class sharing a `_Board` base may reference
     a helper defined only on a SIBLING class — re-cross tests→build to
     fix it, never hand-edit a test under build (evidence: HardenConfine
     needed `_check`, caught at first green run)
   • ADD · open · a trust-layer gate edit (tightening a HOLD / closing
     an admin-override bypass) ESCALATES the verify gate to the human
     even under autonomy:auto — it is not auto-resolved (evidence: this
     gate + federation-harden were both human-decided)
   • ADD · open · "close gap before gate" can mean SURFACE-not-block:
     the refute's R1 was closed with a never-red WARN that keeps the
     frozen §3 behavior (still existence-only) yet makes the degraded
     state visible — no §3 change, no re-freeze (evidence: Tin chose
     close-R1-now; added contract_snapshot_hashless)
   • TDD · open · a recency/staleness guard earns green only via a
     refute-read probing BOTH false-positives (current snapshot ·
     version-only bump · archived producer · self-consume) AND
     false-negatives (drift · empty fence · hash-less snapshot) —
     fixture coverage alone misses the degrade paths (evidence: agent
     affb3fcd surfaced R1, the hash-less blind spot)
   • ADD · open · "run the suite at the gate" under a NO-EXEC engine =
     SURFACE the command (print + record), never execute — the engine
     consumes the registry `verify` field as actionable DATA, mirroring
     how `green_bar` is cited-not-run (evidence: Tin froze surface-only
     over a hard cite-gate)
   • TDD · open · a template-artifact change is guarded by THREE
     pre-existing invariants at once — 3-tree byte-identical · the
     {0,1,3,4,5,6} kept-section set · the <60%-of-full line budget — so
     the hint must ride an EXISTING line (the autonomy comment), not add
     one (evidence: test_fast_lane_template's byte-identical + budget
     guards stayed green)
   • ADD · open · a docs task that fans across the book + skill trees
     must declare ALL of them in §5 Scope BEFORE the freeze — leaving
     the `./src/` placeholder meant the tests→build scope snapshot
     under-declared and the completing gate fired `scope_violation` (12
     files), returning to build (evidence: gate return_to_build attempt
     1/3)
   • ADD · open · on a DIRTY tree the honest scope fix is correct §5 →
     surgically recompute `state…scope.declared` via `_declared_scope`,
     leaving the sidecar baseline intact; re-crossing tests→build would
     re-baseline the already-edited files and hide the touch (evidence:
     healed by a state-write, gate then PASS)
   • ADD · open · backticks in a §5 Scope line's TRAILING COMMENT are
     parsed as scope tokens (the token regex reads the whole physical
     line) — a comment naming `add-method/..` resolved to `./` and
     polluted `declared`; keep the §5 comment backtick-free (evidence:
     dry-run surfaced `./` + `.add/docs/` junk tokens)
   • SDD · open · the skill lean fence is a hard floor: genuinely-new
     doc-truth on a guide is reclaimed from the same guide's prose, not
     a budget rebaseline, absent an explicit human bump (evidence:
     reference pool +418 B → terser components.md, ratio 0.68 kept)

 SPEC DELTAS    6 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              component-polish
════════════════════════════════════════════════════════════════════════