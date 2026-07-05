#!/usr/bin/env python3
"""Tests for sweep-orphan-reclaim-tickets (Sweep Orphan Reclaim Tickets).

FROZEN @ v1: `_prune_data`/`pruneData` ALSO sweep LEAKED per-generation reclaim tickets — a
`<LOCK_FILE>.reclaim-*` under the home (home-scope) and a `<PROJECT_LOCK_FILE>.reclaim-*` under
every LIVE registered project's own `.add/` (project-scope), each aged past its OWN kind's
EXISTING staleness constant (`_LOCK_TICKET_STALE_SECONDS` / `_PROJECT_LOCK_TICKET_STALE_SECONDS`
— reused verbatim, no new threshold). Dry-run lists both classes without removing; --force
removes both (best-effort, swallow errors). `_prune_data`/`pruneData` now return/resolve a
4-tuple / extended object: `(orphans, removed, ticket_orphans, tickets_removed)` /
`{orphans, removed, ticketOrphans, ticketsRemoved}`.

RED until the ticket sweep exists — red for the right reason (an aged ticket never appearing
in ticket_orphans / never removed under --force).

Run: python3 -m unittest test_sweep_orphan_tickets -v
"""
import inspect
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from add_method import _installer            # noqa: E402

CLI_JS = _ADD_METHOD / "bin" / "cli.js"


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tktsweep-")).resolve()
        self.home = self.tmp / "home"; self.home.mkdir(parents=True)
        self.userhome = self.tmp / "user"; self.userhome.mkdir()
        self.proj = self.tmp / "proj"; self.proj.mkdir()
        (self.proj / ".add").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _stamp_home(self):
        (self.home / _installer.STAMP_FILE).write_text("9.9.9\n", encoding="utf-8")

    def _register(self, *projects):
        _installer._write_registry(self.home, [str(p.resolve()) for p in projects])

    def _age(self, p: Path, age_seconds: float):
        ts = time.time() - age_seconds
        os.utime(str(p), (ts, ts))

    def _home_ticket(self, name="123456", age_seconds=None):
        p = self.home / (_installer.LOCK_FILE + f".reclaim-{name}")
        p.write_text("", encoding="utf-8")
        if age_seconds is not None:
            self._age(p, age_seconds)
        return p

    def _project_ticket(self, proj: Path, name="654321", age_seconds=None):
        p = proj / ".add" / (_installer.PROJECT_LOCK_FILE + f".reclaim-{name}")
        p.write_text("", encoding="utf-8")
        if age_seconds is not None:
            self._age(p, age_seconds)
        return p


class AgedHomeTicketSweptTest(_Base):
    def test_aged_home_ticket_is_swept(self):
        self._stamp_home()
        ticket = self._home_ticket(age_seconds=_installer._LOCK_TICKET_STALE_SECONDS + 5)
        orphans, removed, ticket_orphans, tickets_removed = _installer._prune_data(self.home, force=True)
        self.assertIn(ticket, ticket_orphans, "an aged home-scope ticket is a ticket orphan")
        self.assertIn(ticket, tickets_removed, "--force removes an aged home-scope ticket")
        self.assertFalse(ticket.exists(), "the aged ticket is actually gone on disk")


class AgedProjectTicketSweptTest(_Base):
    def test_aged_project_ticket_is_swept_for_live_project(self):
        self._stamp_home()
        self._register(self.proj)
        ticket = self._project_ticket(self.proj, age_seconds=_installer._PROJECT_LOCK_TICKET_STALE_SECONDS + 5)
        orphans, removed, ticket_orphans, tickets_removed = _installer._prune_data(self.home, force=True)
        self.assertIn(ticket, ticket_orphans, "an aged project-scope ticket under a LIVE registered project is a ticket orphan")
        self.assertIn(ticket, tickets_removed, "--force removes an aged project-scope ticket")
        self.assertFalse(ticket.exists())


class UnregisteredProjectTicketUntouchedTest(_Base):
    def test_ticket_under_unregistered_project_untouched(self):
        self._stamp_home()
        # proj exists on disk but is NOT registered -> not swept (sweep only walks registry-live projects)
        ticket = self._project_ticket(self.proj, age_seconds=_installer._PROJECT_LOCK_TICKET_STALE_SECONDS + 5)
        orphans, removed, ticket_orphans, tickets_removed = _installer._prune_data(self.home, force=True)
        self.assertNotIn(ticket, ticket_orphans, "an unregistered project's ticket is never swept")
        self.assertTrue(ticket.exists(), "left completely alone")


class YoungTicketNeverSweptTest(_Base):
    def test_young_ticket_never_swept(self):
        self._stamp_home()
        ticket = self._home_ticket()   # no age_seconds -> fresh (mtime == now)
        orphans, removed, ticket_orphans, tickets_removed = _installer._prune_data(self.home, force=True)
        self.assertNotIn(ticket, ticket_orphans, "a fresh, still-in-flight ticket is never treated as orphaned")
        self.assertTrue(ticket.exists())


class DryRunListsWithoutRemovingTest(_Base):
    def test_dry_run_lists_tickets_without_removing(self):
        self._stamp_home()
        ticket = self._home_ticket(age_seconds=_installer._LOCK_TICKET_STALE_SECONDS + 5)
        orphans, removed, ticket_orphans, tickets_removed = _installer._prune_data(self.home, force=False)
        self.assertIn(ticket, ticket_orphans, "dry-run still reports the ticket orphan")
        self.assertEqual(tickets_removed, [], "dry-run removes nothing")
        self.assertTrue(ticket.exists(), "the ticket survives a dry-run")


class ReCheckAtUnlinkTest(_Base):
    """§5 safety rule: the age check is re-verified at the moment of the (best-effort) unlink,
    not just at the moment of listing, so a race between listing and removal can't widen the
    window past what the constant already accepts. Proven deterministically (no real sleep, no
    real concurrency) by forcing time.time() to advance between the listing snapshot and the
    per-ticket unlink re-check: a ticket that reads AGED at listing time but reads FRESH by the
    time its own unlink is attempted must survive."""

    def test_ticket_refreshed_between_listing_and_unlink_is_not_removed(self):
        self._stamp_home()
        stale_after = _installer._LOCK_TICKET_STALE_SECONDS
        ticket = self._home_ticket(age_seconds=stale_after + 10)
        real_mtime = ticket.stat().st_mtime
        listing_now = real_mtime + stale_after + 10   # ticket reads AGED at listing time
        unlink_now = real_mtime + stale_after - 1      # ticket reads FRESH by unlink re-check time
        with mock.patch("add_method._installer.time.time", side_effect=[listing_now, unlink_now]):
            orphans, removed, ticket_orphans, tickets_removed = _installer._prune_data(self.home, force=True)
        self.assertIn(ticket, ticket_orphans, "still a candidate at listing time")
        self.assertNotIn(ticket, tickets_removed, "re-check at unlink time must catch the now-fresh ticket")
        self.assertTrue(ticket.exists(), "the ticket must survive — proves the re-check is a live stat, not a cached snapshot")


class NoNewStalenessConstantTest(unittest.TestCase):
    def test_no_new_staleness_constant_introduced(self):
        py_src = inspect.getsource(_installer._prune_data) + inspect.getsource(_installer._aged_reclaim_tickets)
        self.assertIn("_LOCK_TICKET_STALE_SECONDS", py_src)
        self.assertIn("_PROJECT_LOCK_TICKET_STALE_SECONDS", py_src)
        self.assertNotRegex(py_src, r'_TICKET_SWEEP_STALE|NEW_TICKET_STALE',
                            "no new, sweep-specific staleness constant may be introduced")

        js = CLI_JS.read_text(encoding="utf-8")
        prune_start = js.index("function pruneData(")
        prune_end = js.index("\n}\n", prune_start)
        prune_fn = js[prune_start:prune_end]
        agedticket_start = js.index("function agedReclaimTickets(")
        agedticket_end = js.index("\n}\n", agedticket_start)
        agedticket_fn = js[agedticket_start:agedticket_end]
        self.assertIn("LOCK_TICKET_STALE_SECONDS", prune_fn + agedticket_fn)
        self.assertIn("PROJECT_LOCK_TICKET_STALE_SECONDS", prune_fn + agedticket_fn)
        self.assertNotRegex(prune_fn + agedticket_fn, r'TICKET_SWEEP_STALE|NEW_TICKET_STALE',
                            "no new, sweep-specific staleness constant may be introduced")


class NpmParityTest(_Base):
    def test_npm_ticket_sweep_parity(self):
        if not shutil.which("node"):
            self.skipTest("node not available")
        self._stamp_home()
        ticket = self._home_ticket(age_seconds=_installer._LOCK_TICKET_STALE_SECONDS + 5)
        env = dict(os.environ)
        env.update({"ADD_HOME": str(self.home), "HOME": str(self.userhome)})
        r = subprocess.run(["node", str(CLI_JS), "prune-data", "--force"],
                           capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(ticket.exists(), "the npm twin sweeps the same aged home-scope ticket")
        self.assertIn("reclaim ticket", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
