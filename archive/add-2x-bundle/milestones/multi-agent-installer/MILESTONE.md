# MILESTONE: Multi-agent installer reach

goal: On install, ADD onboards six more AI agents — Cursor, Windsurf, Trae, Gemini CLI, GitHub Copilot, Cline/Aider — by writing each one's context file so it loads ADD on first run.
rationale: sub-milestone — a slice of the live installer & onboarding theme (extends installer-smarts / installer-experience / installer-soul-seed), too big for one task: six new agent profiles across BOTH twins + a brand-new installer capability (JSON config merge for Gemini CLI) + docs. Additive to the FROZEN-@-v1 agent-detect contract (detect → write integration file → next step) — it extends the registry that contract operates over, so it is NOT a change-request.
stage: mvp · status: active · created: 2026-06-18

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  Six new entries in the `AGENT_PROFILES` registry — cursor · windsurf · trae ·
     copilot · cline · aider — each with id · label · integration_file · env / env_prefix
     detection signals · tailored next_step, mirrored byte-decision-equal across BOTH twins
     (bin/cli.js + src/add_method/_installer.py). Enriched-detection CLI probe list extended
     so an installed agent binary is a machine signal. A NEW installer capability: an
     idempotent, fail-soft merge of `.gemini/settings.json` `context.fileName` so Gemini CLI
     loads the AGENTS.md pointer ADD writes. Docs/onboarding copy updated to name the
     expanded agent set. All detection stays best-effort + overridable in the interactive
     picker; unknown env still degrades to generic.
Out: NO change to the non-interactive/CI byte stream beyond the new profiles' own output
     (the byte-identical pin still holds for the generic/claude paths); NO `add.py init` run
     from the installer (deferred-init / v12-lock invariant); NO engine (add.py) edits
     (ENGINE_MD5 pin holds); NO new runtime dependency (pip stays stdlib; JSON via json
     module / Node built-in); NO agent-native rule DIRECTORY formats (.cursor/rules/*.mdc,
     .windsurf/rules/, .trae/rules/, .clinerules/ dir) — ADD writes ONE markdown pointer file
     per agent, not a rules tree; NO settings.json wiring for any agent OTHER than Gemini CLI
     (the only one that does not auto-load AGENTS.md without config); per-agent integration_file
     CHOICE (native file vs shared AGENTS.md) decided with the human at each task's contract.

## Shared decisions & glossary deltas   (living — every task must honor these)
- agent profile — a registry entry { id, label, integration_file, env, env_prefix, next_step }
  the installer matches against the environment to pick the agent and its context file.
- integration_file — the single markdown file ADD injects its marker-delimited pointer block
  into (CLAUDE.md / AGENTS.md / GEMINI.md / agent-native), superseded by sync-guidelines at /add.
- twin parity — every profile + detection decision is identical in bin/cli.js and
  src/add_method/_installer.py; rendering may differ, decisions may not (guarded by
  test_agent_detect.py::ParityTest).
- settings merge (NEW) — a read-merge-write of an agent's JSON config that preserves existing
  user keys, is idempotent (second run is a no-op), and is fail-soft (a malformed/unwritable
  config warns + skips, never aborts the drop). Introduced for Gemini CLI's context.fileName.

## Shared / risky contracts (freeze these first)
- expanded AGENT_PROFILES registry shape — the exact id/label/integration_file/env/env_prefix/next_step
  for all six agents, in BOTH twins, + the enriched-detection probe order -> owning task agents-md-profiles
- `.gemini/settings.json` merge contract — key path (context.fileName), merge/idempotency/fail-soft
  rules, what is written vs preserved -> owning task gemini-settings-config

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] agents-md-profiles    depends-on: none                  — Add cursor·windsurf·trae·copilot·cline·aider to AGENT_PROFILES in both twins + enriched-detection CLI probes; freezes the registry shape.
- [x] gemini-settings-config depends-on: agents-md-profiles   — Add the gemini profile + the new idempotent fail-soft `.gemini/settings.json` context.fileName merge so Gemini CLI loads AGENTS.md.
- [x] onboarding-docs-refresh depends-on: agents-md-profiles  — Surface the expanded agent set in README / GETTING-STARTED / installer help + next-step copy.

## Exit criteria (observable; map each to the task that delivers it)
- [x] Installing under each of the six agents' env signals writes that agent's integration file with the ADD pointer block and prints that agent's tailored next step; an unknown env still degrades to generic AGENTS.md   (← agents-md-profiles)
- [x] Both twins enumerate the same six profiles and pass test_agent_detect.py::ParityTest with the new tokens   (← agents-md-profiles)
- [x] A Gemini CLI install writes AGENTS.md AND merges `.gemini/settings.json` so context.fileName includes AGENTS.md; re-running is a no-op and a malformed/unwritable settings file warns + skips without aborting the drop   (← gemini-settings-config)
- [x] README / GETTING-STARTED / installer help name the supported agents including the six new ones   (← onboarding-docs-refresh)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- installer (bin/cli.js + src/add_method/_installer.py) : `AGENT_PROFILES` grew by SEVEN entries — cursor · windsurf · trae · copilot · cline · aider (agents-md-profiles) + gemini (gemini-settings-config) — each detected best-effort (env + `env_prefix`), inserted before `generic`; the enriched-detection machine-probe list gained the same agents' CLI binary names. NEW capability: `_write_gemini_settings`/`writeGeminiSettings` — a fail-soft, idempotent, key-preserving merge of `.gemini/settings.json` `context.fileName` (the installer's first JSON-config write), hooked into install()/dropFiles() only for the gemini profile. cli.js exports `writeGeminiSettings`. Pointer writer unchanged (every integration_file is a project-root file: 9×AGENTS.md/CLAUDE.md + cline→.clinerules).
- tooling : add.py ENGINE UNTOUCHED (ENGINE_MD5 pin green). Tests: test_agent_detect.py extended (+ ParityTest token check); NEW test_gemini_settings.py (12) + test_supported_agents_docs.py (2).
- skill   : UNTOUCHED.
- book    : UNTOUCHED. Onboarding docs: README gained a "Works with your agent" paragraph; GETTING-STARTED:138 agent list expanded to the real 10-agent set (kept the "**any agent**" phrasing).

### Cross-task evidence   (one row per task)
- agents-md-profiles    : gate=PASS · tests=full suite green incl. test_agent_detect 26 (live npm per agent) · residue=none
- gemini-settings-config: gate=PASS · tests=test_gemini_settings 12 (live npm settings merge) · residue=none
- onboarding-docs-refresh: gate=PASS · tests=test_supported_agents_docs 2 + docs-accord lints · residue=none (tamper tripwire caught a test-edit-during-build; corrected by reverting the test + fixing the doc — honest redo)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: "On install, ADD onboards six more AI agents by writing each one's context file so it loads ADD on first run." — proven by the live `node bin/cli.js init` runs: Windsurf/Cursor/Trae/Copilot/Aider → AGENTS.md, Cline → .clinerules, Gemini → AGENTS.md + `.gemini/settings.json {"context":{"fileName":["AGENTS.md"]}}`; full suite 1369 green.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] Merge the milestone work directly to `main` (per the human's directive — branch + PR or fast-forward).
- [ ] Cut ADD **v1.7.3**: bump the 4 version sources in lockstep + migrate the forward-pinned test, run `add.py release 1.7.3` (writes CHANGELOG + RELEASES ledger + attribution), then tag.
- [ ] Publish: the tag triggers publish.yml (npm + PyPI); cut the GH release manually. (human-run, per release.md)
