"""The security floor is structural, not just prose: a security risk cannot be folded away.

`sensitivity: security` already floors authority at `human` (SENSITIVITY_FLOOR). The skill also claims
a security finding is a HARD-STOP that "no autonomy level and no persona can buy back" — but until now
`gate()` would record a `RISK-ACCEPTED` on a security node without objection (an audit proved it). This
makes the other half of the floor real: a security risk cannot be signed off as RISK-ACCEPTED; it is
resolved (PASS) or it stops (HARD-STOP).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def test_security_risk_cannot_be_folded_into_risk_accepted(tmp_path):
    """covers: R:SECURITYFOLD — a sensitivity:security node refuses a RISK-ACCEPTED verdict."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Task", "sec", title="auth change", sensitivity="security", scope=["auth.py"])
    ok, note = add.gate(tmp_path, "/tasks/sec.md", "RISK-ACCEPTED", by="x", reason="looks fine to me")
    assert ok is False, "a security risk must never be recordable as a signed acceptance"
    assert "security" in note.lower() and "HARD-STOP" in note, f"the refusal must name the security floor: {note!r}"


def test_nonsecurity_risk_accepted_is_not_blocked_by_the_security_floor(tmp_path):
    """The new floor is narrow: a non-security node's RISK-ACCEPTED is untouched (fails for other reasons only)."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Task", "mech", title="tidy", sensitivity="mechanical", scope=["util.py"])
    ok, note = add.gate(tmp_path, "/tasks/mech.md", "RISK-ACCEPTED", by="x", reason="acceptable")
    # It still refuses (no receipt yet) — but NOT for the security reason. Isolates the new rule.
    assert "security" not in note.lower(), f"the security floor must not fire on a mechanical node: {note!r}"
