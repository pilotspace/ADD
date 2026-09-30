"""Red guards for the persona instruction contract.

These checks deliberately sit at the skill boundary.  The engine's generic node scanner is the
authority for a project Persona's wire shape; prose, templates, and examples must either use that
shape or say exactly how their teaching input is converted to it.  The tests also execute every
ORIENT command found in the shipped persona material against a small throw-away bundle, so a
plausible-looking command cannot become an instruction nobody can run.
"""

from __future__ import annotations

import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))
import add as engine


CANONICAL = REPO / "skill" / "add"
MIRRORS = (
    REPO / "skill" / "add",
    REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
    ROOT / ".claude" / "skills" / "add",
)
CONTRACT = CANONICAL / "persona-author" / "references" / "contract.md"
TEMPLATES = REPO / "tooling" / "templates" / "personas"
BUNDLED_TEMPLATES = REPO / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "personas"
LIVE_TEMPLATES = ROOT / ".add" / "tooling" / "templates" / "personas"
PROJECT_PERSONAS = ROOT / ".add" / "personas"


def _orient_files() -> list[Path]:
    files = []
    for path in (CANONICAL / "personas.md", CANONICAL / "persona-author", TEMPLATES,
                 PROJECT_PERSONAS):
        files.extend([path] if path.is_file() else sorted(path.rglob("*.md")) +
                      sorted(path.rglob("*.tmpl")))
    return sorted(set(files))


def _orient_paragraphs() -> list[tuple[Path, str]]:
    """Keep ORIENT headings with their whole section, including blank-line command bullets."""
    paragraphs = []
    for path in _orient_files():
        content = path.read_text(encoding="utf-8")
        headings = list(re.finditer(r"(?m)^(#{1,6})[ \t]+[^\n]+$", content))
        for i, heading in enumerate(headings):
            if "ORIENT" not in heading.group(0).upper():
                continue
            level = len(heading.group(1))
            end = next((later.start() for later in headings[i + 1:]
                        if len(later.group(1)) <= level), len(content))
            paragraphs.append((path, content[heading.start():end]))
        for paragraph in re.split(r"\n\s*\n", content):
            if "ORIENT" in paragraph.upper():
                paragraphs.append((path, paragraph))
    return paragraphs


def _orient_commands() -> list[str]:
    commands = []
    for _, paragraph in _orient_paragraphs():
        commands.extend(re.findall(r"`(python3 \.add/tooling/cli\.py [^`]+)`", paragraph))
    return sorted(set(commands))


def _noncanonical_orient_commands() -> list[tuple[str, str]]:
    """Enumerate shorthands/retired paths that earlier extraction silently skipped."""
    offenders = []
    patterns = (
        r"`(python3 \.add/tooling/add [^`]+)`",
        r"`(cli\.py [^`]+)`",
        r"`(add [^`]+)`",
    )
    for path, text in _orient_paragraphs():
        label = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name
        for pattern in patterns:
            offenders.extend((label, command)
                             for command in re.findall(pattern, text))
    return offenders


def _source_paths(text: str) -> list[Path]:
    """Resolve only local teacher references; prose such as ``hand-authored`` is not a path."""
    paths = []
    teacher_groups = sorted(
        path.name for path in (ROOT / ".add" / "personas-teacher").iterdir()
        if path.is_dir()
    )
    group_pattern = "|".join(map(re.escape, teacher_groups))
    full = re.findall(r"(?:`)?(?:\.add/)?personas-teacher/([^`\s,)]+)", text)
    shorthand = re.findall(
        rf"(?<!personas-teacher/)(?<![\w-])((?:{group_pattern})/[^`\s,)]+\.md)",
        text,
    )
    for raw in full + shorthand:
        raw = raw.rstrip(".")
        paths.append(ROOT / ".add" / "personas-teacher" / raw)
    return paths


def test_persona_contract_names_the_engine_persona_node_shape(tmp_path):
    """covers M1, R:PERSONA_SCHEMA — generic creation writes type/title, not name alone."""
    bundle = tmp_path / "bundle"
    engine.init(bundle, "code", "schema probe")
    cid, _ = engine.new(bundle, "Persona", "wire-shape", title="Wire shape")
    frontmatter = (bundle / cid.lstrip("/")).read_text(encoding="utf-8").split("---", 2)[1]
    assert re.search(r"^type: Persona$", frontmatter, re.M)
    assert re.search(r"^title: Wire shape$", frontmatter, re.M)
    text = CONTRACT.read_text(encoding="utf-8")
    assert re.search(r"^type: Persona$", text, re.M), \
        "contract omits the actual Persona node type written by add.new"
    assert re.search(r"^title:", text, re.M), \
        "contract omits the actual Persona node title key written by add.new"
    assert "template" in text.lower() and "name:" in text and "title:" in text, \
        "a teaching template's name must be explicitly mapped to the node title"
    assert "engine-checked" not in text and "skips them" not in text, \
        "the authoring contract assigns body or filename checks the engine does not implement"
    for tree in MIRRORS:
        guide = (tree / "personas.md").read_text(encoding="utf-8")
        assert "what the engine checks, presence-based" not in guide, \
            f"{tree}: guide invents body-section diagnostics"


def test_persona_docs_enumerate_the_closed_routing_vocabularies(tmp_path):
    """covers M2, R:BAD_VOCABULARY — prose enumerates the engine's closed sets."""
    flows = engine.PERSONA_FLOWS
    kinds = engine.PERSONA_TASK_KINDS
    for tree in MIRRORS:
        text = (tree / "personas.md").read_text(encoding="utf-8")
        flow_line = next((line for line in text.splitlines() if "`flow:`" in line), "")
        kind_line = next((line for line in text.splitlines() if "`task-kinds:`" in line), "")
        assert all(value in flow_line for value in flows), f"{tree}: flow vocabulary is not closed"
        assert all(value in kind_line for value in kinds), f"{tree}: task-kind vocabulary is not closed"
        contract = (tree / "persona-author" / "references" / "contract.md").read_text(
            encoding="utf-8")
        assert all(value in contract for value in flows + kinds), \
            f"{tree}: persona-author contract omits live routing values"
        assert "reads `flow` and `task-kinds`" in contract
        assert "`doctor` reports" in contract
        assert "NOTHING warns" not in contract and "engine reads only" not in contract
        assert "judges no slot's content" not in text, \
            f"{tree}: doctor diagnoses authored invalid routing vocabulary"
        assert "leaving them blank costs you the routing" not in text, \
            f"{tree}: omitted task-kinds broadens fit rather than blocking routing"
        assert "omitting `task-kinds:` broadens" in text, \
            f"{tree}: guide does not describe the current broad-fit fallback"

    bundle = tmp_path / "routing-bundle"
    engine.init(bundle, "code", "routing fallback")
    persona_cid, _ = engine.new(bundle, "Persona", "broad-fit", title="Broad fit")
    persona_path = bundle / persona_cid.lstrip("/")
    persona_node = engine.read(persona_path, "T2")
    raw = engine.set_key(persona_node["raw"], "flow", "build")
    raw = engine.set_key(raw, "task-kinds", "")
    engine.write(persona_path, f"---\n{raw}\n---\n{persona_node['body']}")
    task_cid, _ = engine.new(bundle, "Task", "security-fit", title="Security fit", kind="security")
    graph = engine.scan(bundle)
    candidates = engine.persona_candidates(graph, graph[task_cid], "build")
    assert any(slug == "broad-fit" for slug, _ in candidates), \
        "the engine no longer treats omitted task-kinds as a broad candidate fit"


def test_doctor_and_candidates_agree_on_yaml_list_routing_keys(tmp_path):
    """covers M2, R:BAD_VOCABULARY, E10 — valid list members must not be false findings."""
    bundle = tmp_path / "routing-lists"
    engine.init(bundle, "code", "list parity")
    lens = bundle / "personas" / "list-fit.md"
    lens.write_text(
        "---\ntype: Persona\ntitle: List fit\nflow: [build]\n"
        "task-kinds: [security]\n---\n## Identity\nA valid lens.\n",
        encoding="utf-8",
    )
    task_cid, _ = engine.new(bundle, "Task", "list-task", title="List task", kind="security")
    graph = engine.scan(bundle)
    assert ("list-fit", "security") in engine.persona_candidates(graph, graph[task_cid], "build")
    assert not [f for f in engine.doctor(bundle) if f.get("code") == "persona_routing_key"
                and "list-fit" in f.get("detail", "")], \
        "doctor rejects a YAML list that the candidate reader accepts"

    lens.write_text(lens.read_text(encoding="utf-8").replace(
        "task-kinds: [security]", "task-kinds: [security, not-a-kind]"), encoding="utf-8")
    findings = [f.get("detail", "") for f in engine.doctor(bundle)
                if f.get("code") == "persona_routing_key" and "list-fit" in f.get("detail", "")]
    assert len(findings) == 1 and "not-a-kind" in findings[0] and \
        "`task-kinds: security`" not in findings[0], \
        "doctor must report only the invalid YAML-list member"


def test_orient_extractor_keeps_blank_line_bullets(tmp_path, monkeypatch):
    """covers M3, R:PHANTOM_ORIENT, E6 — heading-separated commands stay discoverable."""
    path = tmp_path / "heading.md"
    path.write_text("## ORIENT on load\n\n- Run `add ghost-verb` from the project root.\n",
                    encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "_orient_files", lambda: [path])
    assert any("add ghost-verb" in text for _, text in _orient_paragraphs()), \
        "ORIENT heading and its blank-line bullet were split apart"
    assert any(command == "add ghost-verb" for _, command in _noncanonical_orient_commands())


def test_persona_orient_commands_are_real_and_executable(tmp_path):
    """covers M3, R:PHANTOM_ORIENT — each ORIENT command runs on a representative bundle."""
    commands = _orient_commands()
    assert commands, "persona material contains no executable ORIENT command"
    assert not _noncanonical_orient_commands(), \
        f"retired or unqualified ORIENT commands: {_noncanonical_orient_commands()}"
    suffixes = {tuple(shlex.split(command)[2:]) for command in commands}
    expected = {("status",), ("status", "--all"), ("todo",), ("deltas",), ("doctor",)}
    assert expected <= suffixes, f"wrapped ORIENT commands escaped discovery: {sorted(suffixes)}"
    for command in commands:
        assert "tooling/add" not in command, f"retired ORIENT entry point: {command}"
        assert shlex.split(command)[:2] == ["python3", ".add/tooling/cli.py"], command

    bundle = tmp_path / "representative"
    engine.init(bundle / ".add", "code", "representative")
    tooling = bundle / ".add" / "tooling"
    tooling.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / "tooling" / "cli.py", tooling / "cli.py")
    shutil.copy2(REPO / "tooling" / "add.py", tooling / "add.py")
    for command in commands:
        result = subprocess.run(shlex.split(command), cwd=bundle, text=True,
                                capture_output=True, check=False)
        assert result.returncode == 0, f"{command!r} failed:\n{result.stdout}\n{result.stderr}"


def test_persona_references_resolve_to_local_teacher_material():
    """covers M4, R:UNRESOLVED_REFERENCE — authored provenance names existing files/directories."""
    files = _orient_files()
    assert files, "persona inputs are missing"
    missing = {}
    for path in files:
        refs = _source_paths(path.read_text(encoding="utf-8"))
        absent = []
        for ref in refs:
            relative = str(ref.relative_to(ROOT))
            exists = any(ROOT.glob(relative)) if any(mark in relative for mark in "*?[") \
                else ref.exists()
            if not exists:
                absent.append(relative)
        if absent:
            missing[str(path.relative_to(ROOT))] = absent
    assert not missing, f"persona provenance names missing teacher material: {missing}"


def test_persona_material_uses_the_engine_source_key_or_declares_conversion():
    """covers M1/M4, R:PERSONA_SCHEMA — singular source is not silently treated as sources."""
    offenders = []
    for path in sorted(TEMPLATES.glob("*.tmpl")) + sorted(
            (CANONICAL / "persona-author").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        teaches_singular = re.search(r"^source:", text, re.M) or "`source:`" in text
        if teaches_singular and not re.search(
                r"(?:template|convert|maps?).{0,100}(?:source|sources|title|name)", text,
                re.I | re.S):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, "teaching persona files use `source:` without a node-schema conversion: " + \
        ", ".join(offenders)


def test_persona_authority_boundary_is_explicit_in_all_skill_trees(tmp_path):
    """covers M5, R:FALSE_AUTHORITY — advice cannot execute or lower an ADD gate."""
    for tree in MIRRORS:
        text = (tree / "personas.md").read_text(encoding="utf-8")
        assert re.search(r"never lowers a gate", text, re.I)
        assert re.search(r"NO-EXEC", text) and "engine" in text
        assert not re.search(r"never (?:reads|read) a persona", text, re.I)
        assert not re.search(r"persona (?:may|can) (?:freeze|gate|approve|authorize)", text, re.I)
        streams = (tree / "streams.md").read_text(encoding="utf-8")
        assert not re.search(r"never (?:reads|read) a persona", streams, re.I)

    project_lenses = "\n".join(
        path.read_text(encoding="utf-8") for path in PROJECT_PERSONAS.glob("*.md")
    )
    assert not re.search(r"never (?:reads|read) a persona", project_lenses, re.I)

    bundle = tmp_path / "bundle"
    engine.init(bundle, "code", "frontmatter probe")
    lens_path = sorted((bundle / "personas").glob("*.md"))[0]
    lens = lens_path.stem
    cid, _ = engine.new(
        bundle, "Task", "frontmatter-reaches-brief", title="probe", persona=lens
    )
    brief = str(engine.brief(bundle, cid)["text"])
    assert f'ref="personas/{lens}"' in brief and "task-kinds:" in brief
    assert "## Identity" not in brief and "## Critical Rules" not in brief, \
        "the engine should inject frontmatter without loading the Persona body"


def test_index_absence_does_not_block_persona_routing(tmp_path):
    """covers M5, R:FALSE_AUTHORITY, E9 — index is orientation, not a selector gate."""
    bundle = tmp_path / "off-index"
    engine.init(bundle, "code", "index independence")
    engine.doctor_sync(bundle)
    lens = bundle / "personas" / "off-index.md"
    lens.write_text(
        "---\ntype: Persona\ntitle: Off index\nflow: build\n"
        "task-kinds: security\nuse-when: a security build\n---\n## Identity\nA lens.\n",
        encoding="utf-8",
    )
    assert "off-index" not in (bundle / "index.md").read_text(encoding="utf-8")
    cid, _ = engine.new(bundle, "Task", "off-index-task", title="Off index task",
                        kind="security")
    graph = engine.scan(bundle)
    assert ("off-index", "security") in engine.persona_candidates(graph, graph[cid], "build")
    assert 'candidate ref="personas/off-index"' in engine.brief(bundle, cid, phase="build")["text"]
    for tree in MIRRORS:
        prose = (tree / "persona-author" / "SKILL.md").read_text(encoding="utf-8")
        assert "missing there is one no routing ever reads" not in prose
        assert "selector reads Persona nodes directly" in prose


def test_body_section_names_are_author_reviewed_not_engine_matched(tmp_path):
    """covers M5, R:FALSE_AUTHORITY, E11 — body completeness is author advice only."""
    bundle = tmp_path / "no-headings"
    engine.init(bundle, "code", "body advice")
    (bundle / "personas" / "headingless.md").write_text(
        "---\ntype: Persona\ntitle: Headingless\nflow: build\n"
        "task-kinds: feature\n---\nThis body has no recommended section headings.\n",
        encoding="utf-8",
    )
    cid, _ = engine.new(bundle, "Task", "headingless-task", title="Headingless task",
                        kind="feature")
    graph = engine.scan(bundle)
    assert ("headingless", "feature") in engine.persona_candidates(graph, graph[cid], "build")
    assert 'candidate ref="personas/headingless"' in engine.brief(bundle, cid, phase="build")["text"]
    assert not any("headingless" in f.get("detail", "") and "section" in f.get("detail", "")
                   for f in engine.doctor(bundle))
    for tree in MIRRORS:
        contract = (tree / "persona-author" / "references" / "contract.md").read_text(
            encoding="utf-8")
        assert not re.search(r"engine and every\s+apply-surface match\s+\*\*literally\*\*",
                             contract)
        assert "Body quality stays author-reviewed" in contract


def test_persona_skill_mirrors_are_byte_identical():
    """covers M6, R:TREE_DRIFT — canonical, bundled, and Claude skill trees agree."""
    relatives = ["personas.md", "streams.md"] + [
        str(path.relative_to(CANONICAL))
        for path in sorted((CANONICAL / "persona-author").rglob("*"))
        if path.is_file()
    ]
    for relative in relatives:
        payloads = [(tree / relative).read_bytes() for tree in MIRRORS]
        assert len(set(payloads)) == 1, f"persona skill mirrors diverge at {relative}"
    source_templates = {path.name: path.read_bytes() for path in TEMPLATES.glob("*.md.tmpl")}
    bundled_templates = {
        path.name: path.read_bytes() for path in BUNDLED_TEMPLATES.glob("*.md.tmpl")
    }
    assert bundled_templates == source_templates, "source and bundled persona templates diverge"
    # `.add/tooling/` is the repo's own gitignored install: a fresh checkout (CI) has none, and
    # an absent install cannot drift. Where it exists, it must match the source byte for byte.
    if LIVE_TEMPLATES.is_dir():
        live_templates = {path.name: path.read_bytes() for path in LIVE_TEMPLATES.glob("*.md.tmpl")}
        assert live_templates == source_templates, "source and live installed persona templates diverge"


def test_persona_initialization_claim_matches_seeded_templates(tmp_path):
    """covers M7, R:STALE_INIT — guidance matches a fresh bundle and non-overwrite behavior."""
    bundle = tmp_path / ".add"
    engine.init(bundle, "code", "seed truth")
    expected = {path.name.removesuffix(".md.tmpl") for path in TEMPLATES.glob("*.md.tmpl")}
    actual = {path.stem for path in (bundle / "personas").glob("*.md")}
    assert actual == expected and actual, "init did not seed the shipped starting roster"

    held = bundle / "personas" / f"{sorted(actual)[0]}.md"
    held.write_text("human-authored\n", encoding="utf-8")
    *_, note = engine.init(bundle, "code", "seed truth")
    assert held.read_text(encoding="utf-8") == "human-authored\n"
    assert "nothing written" in note

    for tree in MIRRORS:
        contract = (tree / "persona-author" / "references" / "contract.md").read_text(
            encoding="utf-8")
        assert "seeds **no personas**" not in contract
        assert "Never ship a DOMAIN lens" not in contract
        assert "seeds every shipped starting-persona template" in contract
        assert "never overwrites" in contract
