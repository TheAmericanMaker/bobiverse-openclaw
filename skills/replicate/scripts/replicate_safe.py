#!/usr/bin/env python3
"""Hardened replication runner for Bobiverse OpenClaw skill.

Security properties:
- strict input validation
- path boundary enforcement (~/.openclaw only)
- no shell command interpolation
- explicit confirmation token for execute mode
- dry-run by default
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SERIAL_RE = re.compile(r"^Bob-[0-9A-Za-z]+-[A-Za-z0-9-]{1,39}-\d{4}-\d{2}-\d{2}$")
AGENT_RE = re.compile(r"^[a-z0-9-]{1,80}$")


@dataclass(frozen=True)
class Plan:
    clone_id: str
    agent_id: str
    parent_workspace: Path
    clone_workspace: Path


def ensure_within_openclaw(path: Path, openclaw_root: Path) -> Path:
    resolved = path.expanduser().resolve()
    root = openclaw_root.expanduser().resolve()
    if root not in (resolved, *resolved.parents):
        raise ValueError(f"Path escapes ~/.openclaw boundary: {resolved}")
    return resolved


def count_workspaces(openclaw_root: Path) -> int:
    return len([p for p in openclaw_root.glob("workspace*") if p.is_dir()])


def build_plan(args: argparse.Namespace, openclaw_root: Path) -> Plan:
    if not SERIAL_RE.match(args.clone_id):
        raise ValueError("Invalid clone-id format. Expected Bob-<gen>-<system>-YYYY-MM-DD")

    agent_id = args.clone_id.lower()
    if not AGENT_RE.match(agent_id):
        raise ValueError("Derived agent-id is invalid.")

    parent = ensure_within_openclaw(Path(args.parent_workspace), openclaw_root)
    if not parent.exists() or not parent.is_dir():
        raise ValueError(f"Parent workspace does not exist: {parent}")

    clone_workspace = ensure_within_openclaw(openclaw_root / f"workspace-{agent_id}", openclaw_root)

    return Plan(
        clone_id=args.clone_id,
        agent_id=agent_id,
        parent_workspace=parent,
        clone_workspace=clone_workspace,
    )


def write_audit(openclaw_root: Path, payload: dict) -> None:
    audit_path = openclaw_root / "replication-audit.log"
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")


def run() -> int:
    parser = argparse.ArgumentParser(description="Safe Bobiverse replication runner")
    parser.add_argument("--clone-id", required=True)
    parser.add_argument("--parent-workspace", required=True)
    parser.add_argument("--purpose", required=True, help="Why replication is needed now")
    parser.add_argument("--confirm", default="", help="Must equal: REPLICATE <clone-id> for execute mode")
    parser.add_argument("--execute", action="store_true", help="Perform changes. Default is dry-run.")
    parser.add_argument(
        "--allow-high-workspace-count",
        action="store_true",
        help="Required when existing workspaces >= 10",
    )

    args = parser.parse_args()
    openclaw_root = Path("~/.openclaw").expanduser().resolve()
    openclaw_root.mkdir(parents=True, exist_ok=True)

    purpose = args.purpose.strip()
    if len(purpose) < 12:
        raise ValueError("Purpose statement too short; provide concrete justification.")

    plan = build_plan(args, openclaw_root)

    existing = count_workspaces(openclaw_root)
    if existing >= 10 and not args.allow_high_workspace_count:
        raise ValueError("Workspace count >= 10. Re-run with --allow-high-workspace-count to continue.")

    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "execute" if args.execute else "dry-run",
        "clone_id": plan.clone_id,
        "agent_id": plan.agent_id,
        "parent_workspace": str(plan.parent_workspace),
        "clone_workspace": str(plan.clone_workspace),
        "existing_workspaces": existing,
        "purpose": purpose,
    }

    if not args.execute:
        print(json.dumps(summary, indent=2))
        return 0

    if args.confirm != f"REPLICATE {plan.clone_id}":
        raise ValueError("Invalid confirmation token. Expected exact: REPLICATE <clone-id>")

    if plan.clone_workspace.exists():
        raise ValueError(f"Clone workspace already exists: {plan.clone_workspace}")

    shutil.copytree(plan.parent_workspace, plan.clone_workspace)

    subprocess.run(
        ["openclaw", "agents", "add", plan.agent_id, "--workspace", str(plan.clone_workspace)],
        check=True,
        shell=False,
    )

    write_audit(openclaw_root, summary)
    print(json.dumps({**summary, "status": "ok"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
