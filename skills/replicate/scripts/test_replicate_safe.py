import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import importlib.util
import sys


SPEC = importlib.util.spec_from_file_location(
    "replicate_safe", Path(__file__).with_name("replicate_safe.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ReplicateSafeTests(unittest.TestCase):
    def test_ensure_within_openclaw_rejects_escape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / ".openclaw"
            root.mkdir(parents=True)
            outside = Path(td) / "outside"
            outside.mkdir()
            with self.assertRaises(ValueError):
                MODULE.ensure_within_openclaw(outside, root)

    def test_build_plan_validates_clone_id(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / ".openclaw"
            parent = root / "workspace-parent"
            parent.mkdir(parents=True)

            class Args:
                clone_id = "bad-id"
                parent_workspace = str(parent)

            with self.assertRaises(ValueError):
                MODULE.build_plan(Args, root)

    def test_build_plan_happy_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / ".openclaw"
            parent = root / "workspace-parent"
            parent.mkdir(parents=True)

            class Args:
                clone_id = "Bob-2-TestSystem-2026-04-03"
                parent_workspace = str(parent)

            plan = MODULE.build_plan(Args, root)
            self.assertEqual(plan.agent_id, "bob-2-testsystem-2026-04-03")
            self.assertTrue(str(plan.clone_workspace).endswith("workspace-bob-2-testsystem-2026-04-03"))

    def test_last_execute_time_reads_latest_execute(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / ".openclaw"
            root.mkdir(parents=True)
            audit = root / "replication-audit.log"
            older = datetime.now(timezone.utc) - timedelta(days=2)
            newer = datetime.now(timezone.utc) - timedelta(hours=2)
            records = [
                {"timestamp_utc": older.isoformat(), "mode": "execute"},
                {"timestamp_utc": newer.isoformat(), "mode": "execute"},
                {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "mode": "dry-run"},
            ]
            with audit.open("w", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r) + "\n")

            last = MODULE.last_execute_time(root)
            self.assertIsNotNone(last)
            assert last is not None
            self.assertEqual(last.replace(microsecond=0), newer.replace(microsecond=0))


if __name__ == "__main__":
    unittest.main()
