"""`add deltas` reads the validity intervals the dated grammar records.

The grammar landed ids and intervals on all 43 lessons and nothing read the dates. A `## Deltas`
section is append-only and now 42 entries deep across five specs, so the inventory SKILL.md tells
the loop to read before planning is a wall: no way to ask which lessons are recent, which belong
to one lens, or what a spec asserted when a past decision was taken.

The two failure shapes these checks exist to prevent, both drawn from this corpus's own record:
a filter that silently drops what it cannot date (a smaller number reads as success), and an
unreadable value that resolves to a clean default instead of refusing.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

CLI = REPO / "tooling" / "cli.py"


def _bundle(tmp_path, lines_by_lens):
    root = tmp_path / ".add"
    (root / "specs").mkdir(parents=True)
    (root / "index.md").write_text('---\nabf_version: "1.3"\nname: b\n---\n', encoding="utf-8")
    for lens, lines in lines_by_lens.items():
        body = "## Now\nx\n\n## Deltas\n\n" + "".join(l + "\n" for l in lines)
        (root / "specs" / f"{lens}.md").write_text(
            f"---\ntype: Spec\ntitle: {lens.title()}\nlens: {lens}\n---\n{body}", encoding="utf-8")
    return root


def _cli(root, *args):
    return subprocess.run([sys.executable, str(CLI), "--root", str(root), "deltas", *args],
                          capture_output=True, text=True)


OPEN_AUG = "- [ADD · M1 · open · 2026-08-11] filed in august (evidence: /tasks/a.md)"
OPEN_SEP = "- [ADD · M2 · open · 2026-09-01] filed in september (evidence: /tasks/b.md)"
FOLDED   = "- [ADD · M3 · folded · 2026-08-11→2026-09-03] folded in september (evidence: /tasks/c.md)"
LEGACY   = "- [ADD · open] a legacy undated lesson (evidence: /tasks/d.md)"
BADDATE  = "- [ADD · M5 · open · not-a-date] a broken recorded date (evidence: /tasks/e.md)"
QUALITY  = "- [TDD · Q1 · open · 2026-08-11] a quality lesson (evidence: /tasks/f.md)"


def test_lens_filter_narrows_to_one_spec(tmp_path):
    """covers: M1,M8 — one lens listed, the others absent, an unknown lens refused."""
    root = _bundle(tmp_path, {"method": [OPEN_AUG], "quality": [QUALITY]})
    items, note = add.deltas(root, lens="method")
    assert [i[0] for i in items] == ["method"], note
    assert "a quality lesson" not in note, note

    _items, refusal = add.deltas(root, lens="nosuchlens")
    assert "nosuchlens" in refusal and "method" in refusal and "quality" in refusal, refusal


def test_since_lists_only_intervals_that_start_on_or_after(tmp_path):
    """covers: M2,A2 — `--since` reads valid_from, so an old-but-recently-folded delta stays out."""
    root = _bundle(tmp_path, {"method": [OPEN_AUG, OPEN_SEP, FOLDED]})
    items, note = add.deltas(root, since="2026-09-01")
    texts = " ".join(i[2] for i in items)
    assert "filed in september" in texts, note
    assert "filed in august" not in texts, note
    folded, _ = add.deltas(root, status="folded", since="2026-09-01")
    assert not folded, "a delta FILED in august leaked into a september --since because it CLOSED in september"


def test_as_of_reports_the_status_held_then(tmp_path):
    """covers: M3 — the whole point: a delta folded today was open on an earlier date."""
    root = _bundle(tmp_path, {"method": [FOLDED]})
    items, note = add.deltas(root, status="open", as_of="2026-08-20")
    assert [i[2] for i in items] == ["folded in september (evidence: /tasks/c.md)"], note
    today, _ = add.deltas(root, status="open")
    assert not today, "the delta is folded TODAY and must not appear in an unfiltered open listing"


def test_as_of_excludes_a_delta_closed_on_the_queried_date(tmp_path):
    """covers: M4,E2,A3 — half-open [from, to): closing on D means not asserted ON D."""
    root = _bundle(tmp_path, {"method": [FOLDED]})
    on_close, _ = add.deltas(root, status="open", as_of="2026-09-03")
    assert not on_close, "a delta folded ON the queried date was still counted as open"
    day_before, _ = add.deltas(root, status="open", as_of="2026-09-02")
    assert day_before, "the day before the close must still be open — the boundary is off by one"


def test_undated_deltas_are_shown_and_counted_never_dropped(tmp_path):
    """covers: M5,R:SILENT_DROP,A4 — a filter that hides what it cannot judge lies by omission."""
    root = _bundle(tmp_path, {"method": [OPEN_AUG, LEGACY]})
    items, note = add.deltas(root, since="2026-09-01")
    texts = " ".join(i[2] for i in items)
    assert "legacy undated" in texts, f"the undated delta was dropped by a time filter: {note}"
    assert "undated" in note.lower(), f"the listing never says the undated line is unjudged: {note}"


def test_an_unreadable_date_argument_refuses(tmp_path):
    """covers: M6,R:TODAYFALLBACK — never fall back to today, never treat it as absent."""
    root = _bundle(tmp_path, {"method": [OPEN_AUG]})
    items, refusal = add.deltas(root, since="last tuesday")
    assert not items, "an unreadable --since listed as though unfiltered"
    assert "YYYY-MM-DD" in refusal, f"the refusal does not name the accepted form: {refusal}"


def test_a_malformed_recorded_date_is_reported_not_defaulted(tmp_path):
    """covers: M7,A4 — an unreadable field reads as UNKNOWN, never as zero and never as now.

    The guarantee is stronger than "shown and marked": `parse_delta_head` classifies a bad date
    as `bad_date`, so the line is NAMED, QUOTED and COUNTED in its own malformed section rather
    than blended into the listing as merely unjudged. What matters is that no date is invented
    for it — a default of today would put it inside every recent window, a default of epoch
    would put it inside none, and both would read as a clean value.
    """
    root = _bundle(tmp_path, {"method": [BADDATE]})
    items, note = add.deltas(root, since="2026-01-01")
    assert not items, f"a line the engine cannot date was listed as though dated: {note}"
    assert "bad_date" in note, f"the broken date is not reported at all: {note}"
    assert "a broken recorded date" in note, f"the offending line is not quoted back: {note}"

    # and no invented default: it is absent from BOTH ends of the range, not silently inside one
    far_future, note_f = add.deltas(root, since="2099-01-01")
    assert not far_future and "bad_date" in note_f, note_f


def test_filters_compose_and_the_header_names_them(tmp_path):
    """covers: M8,A6 — a narrowed listing must announce that it is narrowed."""
    root = _bundle(tmp_path, {"method": [OPEN_AUG, OPEN_SEP], "quality": [QUALITY]})
    items, note = add.deltas(root, lens="method", since="2026-09-01")
    assert [i[2].split(" (")[0] for i in items] == ["filed in september"], note
    assert "method" in note and "2026-09-01" in note, f"the header hides the active filters: {note}"


def test_as_of_before_everything_is_an_empty_listing_not_an_error(tmp_path):
    """covers: E1 — an empty result is a recorded outcome, not a failure."""
    root = _bundle(tmp_path, {"method": [OPEN_AUG]})
    out = _cli(root, "--as-of", "2020-01-01")
    assert out.returncode == 0, out.stderr
    assert "no open deltas" in out.stdout, out.stdout


def test_a_lens_with_no_deltas_differs_from_an_unknown_lens(tmp_path):
    """covers: E3 — 'nothing here' and 'no such thing' are different answers."""
    root = _bundle(tmp_path, {"method": [OPEN_AUG], "quality": []})
    empty, empty_note = add.deltas(root, lens="quality")
    assert not empty and "no open deltas" in empty_note, empty_note
    _u, unknown = add.deltas(root, lens="ghost")
    assert "ghost" in unknown and "no open deltas" not in unknown, unknown


def test_unfiltered_output_is_byte_identical(tmp_path):
    """covers: A5 — this task adds a filter; with no flags nothing may move."""
    root = _bundle(tmp_path, {"method": [OPEN_AUG, OPEN_SEP], "quality": [QUALITY]})
    items, note = add.deltas(root)
    assert len(items) == 3, note
    assert note.startswith("open deltas (3):"), note
    assert "undated" not in note.lower(), f"an unfiltered listing gained filter chatter: {note}"


def test_the_planning_flags_a_planner_reaches_for_are_wired(tmp_path):
    """covers: A1 — the probe A1 declared: the filters exist to serve the PLANNING beat.

    SKILL.md now routes intake through `add deltas` before drafting a Task or Milestone, so the
    audience is a planner deciding what to work on next — not a reporter. `--lens` (what does
    this spec already say) and `--since` (what have we learned lately) are the two that beat
    reaches for, and both must be reachable from the CLI, not just from the library.
    """
    root = _bundle(tmp_path, {"method": [OPEN_AUG, OPEN_SEP], "quality": [QUALITY]})
    help_text = subprocess.run([sys.executable, str(CLI), "deltas", "--help"],
                               capture_output=True, text=True).stdout
    for flag in ("--lens", "--since", "--as-of"):
        assert flag in help_text, f"{flag} is not reachable from the CLI: {help_text}"
    # M4's boundary must be STATED, not merely implemented — two readers disagree otherwise.
    assert "half-open" in help_text, f"--as-of does not state its boundary rule: {help_text}"

    lens_run = _cli(root, "--lens", "method")
    assert lens_run.returncode == 0 and "a quality lesson" not in lens_run.stdout, lens_run.stdout
    since_run = _cli(root, "--since", "2026-09-01")
    assert since_run.returncode == 0 and "filed in august" not in since_run.stdout, since_run.stdout
