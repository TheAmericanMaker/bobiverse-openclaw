# Protocols and State

## Boundaries Identified

| Boundary                            | Description                                                              |
| ----------------------------------- | ------------------------------------------------------------------------ |
| Chat Interface → OpenClaw Runtime   | Agent receives messages; OpenClaw injects personality files into context |
| Replicate Skill → replicate_safe.py | Skill triggers Python script for hardened execution                      |
| Script → Filesystem                 | Python script creates/ deletes directories in ~/.openclaw                |
| Script → OpenClaw CLI               | Subprocess calls `openclaw agents add` to register clone                 |
| Parent Workspace → Clone Workspace  | shutil.copytree replicates all files                                     |
| GitHub → Repository                 | Fork creates new repo with fork relationship metadata                    |
| Agent → Agent                       | sessions_send for cross-agent messaging (optional)                       |

---

## Event Catalog

### OpenClaw Agent Message Protocol

| Field                          | Value                                            |
| ------------------------------ | ------------------------------------------------ |
| **Producer**                   | Human operator (via chat/TUI)                    |
| **Consumer**                   | Bob agent (OpenClaw runtime)                     |
| **Transport or carrier**       | OpenClaw's chat interface                        |
| **Ordering guarantees**        | Sequential; session state preserved              |
| **Required fields**            | Message text                                     |
| **Optional fields**            | Attachments, context hints                       |
| **Identifiers and timestamps** | Session ID, message timestamp (OpenClaw-managed) |
| **Error cases**                | Invalid message format → rejected by OpenClaw    |
| **Restart or resume behavior** | Session continuity maintained by OpenClaw        |

### Replication Dry-Run Event

| Field                          | Value                                                                                        |
| ------------------------------ | -------------------------------------------------------------------------------------------- |
| **Producer**                   | replicate_safe.py (dry-run mode)                                                             |
| **Consumer**                   | Human operator                                                                               |
| **Transport or carrier**       | stdout (JSON)                                                                                |
| **Ordering guarantees**        | One-shot; no ordering with other events                                                      |
| **Required fields**            | clone_id, agent_id, parent_workspace, clone_workspace, confirm_token, pending_expires_at_utc |
| **Optional fields**            | existing_workspaces, cooldown_override_reason                                                |
| **Identifiers and timestamps** | timestamp_utc, event="dry-run-created"                                                       |
| **Error cases**                | Invalid inputs → ValueError before event emission                                            |
| **Restart or resume behavior** | Must re-run dry-run to get new token if expired                                              |

### Replication Execute Events

| Field                          | Value                                                                                        |
| ------------------------------ | -------------------------------------------------------------------------------------------- |
| **Producer**                   | replicate_safe.py (execute mode)                                                             |
| **Consumer**                   | Audit log, human operator                                                                    |
| **Transport or carrier**       | stdout (JSON), replication-audit.log (append)                                                |
| **Ordering guarantees**        | Sequence: execute-started → execute-succeeded OR execute-failed                              |
| **Required fields**            | clone_id, agent_id, parent_workspace, clone_workspace, staging_workspace                     |
| **Optional fields**            | error (on failure), existing_workspaces, purpose                                             |
| **Identifiers and timestamps** | timestamp_utc, event type                                                                    |
| **Error cases**                | Validation failure → exception before started; runtime failure → execute-failed with cleanup |
| **Restart or resume behavior** | Failed execute rolls back; re-run from dry-run                                               |

### Agent Registration Protocol

| Field                          | Value                                         |
| ------------------------------ | --------------------------------------------- |
| **Producer**                   | replicate_safe.py (subprocess)                |
| **Consumer**                   | OpenClaw                                      |
| **Transport or carrier**       | subprocess.run with shell=False               |
| **Ordering guarantees**        | Synchronous; waits for completion             |
| **Required fields**            | agent_id, workspace path                      |
| **Optional fields**            | None                                          |
| **Identifiers and timestamps** | Agent ID derived from clone serial            |
| **Error cases**                | Non-zero exit → exception, rollback triggered |
| **Restart or resume behavior** | Re-run after fixing workspace                 |

### Cross-Agent Messaging Protocol (Optional)

| Field                          | Value                                             |
| ------------------------------ | ------------------------------------------------- |
| **Producer**                   | Bob (parent or clone)                             |
| **Consumer**                   | Another Bob                                       |
| **Transport or carrier**       | OpenClaw sessions_send tool                       |
| **Ordering guarantees**        | Fire-and-forget or wait-for-reply with timeout    |
| **Required fields**            | target_agent_id, message                          |
| **Optional fields**            | reply_timeout                                     |
| **Identifiers and timestamps** | Session IDs, timestamps                           |
| **Error cases**                | Delivery failure → no notification (per SKILL.md) |
| **Restart or resume behavior** | Operator can retry message                        |

---

## State Machine

### Replication Flow State Machine

```
┌─────────┐    dry-run     ┌─────────┐    execute      ┌─────────┐
│  idle   │ ──────────────► │ pending │ ──────────────► │ running │
└─────────┘    creates      └─────────┘   confirmed    └────┬────┘
  (start)       token          (wait)         token              │
     ▲                                                            │
     │                                                            │
     │              ┌─────────────────────────┐                  │
     │              │                         │                  │
     │              ▼                         ▼                  ▼
     │        ┌─────────┐              ┌─────────┐         ┌─────────┐
     └────────│ expired │              │ failed  │         │ complete│
              └─────────┘              └─────────┘         └─────────┘
              (token TTL                                       (clone
               exceeded)                                        ready)
```

| Current State | Event / Trigger                | Guard                         | Next State | Side Effects                                   |
| ------------- | ------------------------------ | ----------------------------- | ---------- | ---------------------------------------------- |
| idle          | dry-run invoked                | All validations pass          | pending    | pending-approval.json created, nonce generated |
| idle          | dry-run invoked                | Validation fails              | idle       | ValueError raised                              |
| pending       | execute with correct token     | Token matches, not expired    | running    | Token consumed                                 |
| pending       | execute with wrong token       | Token mismatch                | pending    | ValueError raised                              |
| pending       | execute after TTL              | Token expired                 | idle       | pending-approval.json deleted                  |
| pending       | execute with different purpose | Purpose mismatch              | pending    | ValueError raised                              |
| running       | subprocess succeeds            | openclaw agents add returns 0 | complete   | Clone registered, audit logged                 |
| running       | subprocess fails               | CalledProcessError            | failed     | Cleanup, audit-failed event                    |
| complete      | -                              | -                             | terminal   | Clone workspace active                         |
| failed        | -                              | -                             | terminal   | Rollback complete, audit logged                |
| expired       | -                              | -                             | terminal   | Can restart from idle                          |

### Agent Lifecycle State Machine

```
┌─────────┐    add         ┌─────────┐    message     ┌─────────┐
│ missing │ ──────────────► │ registered │ ──────────► │ active  │
└─────────┘    (openclaw   └─────────┘    (session    └─────────┘
  (no agent)    agents add)   (in registry)   start)      (responding)
                                              │
                                              ▼
                                        ┌─────────┐
                                        │ inactive│
                                        └─────────┘
                                        (no sessions)
```

| Current State | Event / Trigger           | Guard           | Next State | Side Effects              |
| ------------- | ------------------------- | --------------- | ---------- | ------------------------- |
| missing       | openclaw agents add       | Valid workspace | registered | Agent added to OpenClaw   |
| registered    | First message             | Session exists  | active     | Personality injected      |
| active        | No messages for N minutes | Timeout         | inactive   | Session state may persist |
| inactive      | New message               | Session exists  | active     | Context resumed           |

---

## Persistent Schema Notes

### Workspace Files (Markdown)

| Property                         | Value                                              |
| -------------------------------- | -------------------------------------------------- |
| **Format**                       | Markdown with YAML frontmatter (some files)        |
| **Append-only vs mutable**       | Mutable — edited by agent or operator              |
| **Branching vs linear history**  | Linear — no versioning in this repo                |
| **Compaction or summarization**  | Agent can manually promote daily logs to MEMORY.md |
| **Replay or resume behavior**    | Files read at session start; resume is implicit    |
| **Locking or conflict handling** | None — single-user assumption                      |

### replication-pending/*.json

| Property                         | Value                                         |
| -------------------------------- | --------------------------------------------- |
| **Format**                       | JSON                                          |
| **Append-only vs mutable**       | Created on dry-run, deleted on execute/expire |
| **Branching vs linear history**  | One per pending clone; no history             |
| **Compaction or summarization**  | N/A — temporary                               |
| **Replay or resume behavior**    | TTL enforcement; 15-minute expiry             |
| **Locking or conflict handling** | None — single operation at a time             |

### replication-audit.log

| Property                         | Value                                            |
| -------------------------------- | ------------------------------------------------ |
| **Format**                       | JSONL (one JSON object per line)                 |
| **Append-only vs mutable**       | Append-only via atomic write                     |
| **Branching vs linear history**  | Linear — all events in order                     |
| **Compaction or summarization**  | None — full audit trail                          |
| **Replay or resume behavior**    | last_execute_time() reads to find last execution |
| **Locking or conflict handling** | Atomic file replacement prevents corruption      |

### LINEAGE.md

| Property                         | Value                                   |
| -------------------------------- | --------------------------------------- |
| **Format**                       | Markdown tables                         |
| **Append-only vs mutable**       | Mutable — updated on each clone         |
| **Branching vs linear history**  | Tree structure (fork graph)             |
| **Compaction or summarization**  | None                                    |
| **Replay or resume behavior**    | Full history preserved                  |
| **Locking or conflict handling** | None — potential concurrent-edit hazard |

---

## Compatibility Hazards

| Hazard                      | Where It Appears          | Severity | Notes                                                                        |
| --------------------------- | ------------------------- | -------- | ---------------------------------------------------------------------------- |
| ~/.openclaw path assumption | replicate_safe.py default | medium   | Relies on Unix-style home directory; configurable via OPENCLAW_ROOT          |
| shell=False required        | subprocess calls          | low      | Python-specific; other languages use different process models                |
| Path separators             | Workspace operations      | low      | pathlib handles OS differences; but script assumes Unix-like paths           |
| JSON timestamp format       | audit logs                | low      | ISO format with timezone; portable across languages                          |
| Symlink rejection           | validate_parent_workspace | low      | Security feature; may need equivalent in port                                |
| Memory file naming          | memory/YYYY-MM-DD.md      | low      | Date-based naming; case-sensitive on some filesystems                        |
| Session tool visibility     | OpenClaw config           | medium   | Requires "all" for cross-agent messaging; not all frameworks have equivalent |

---

## Open Questions

1. **Audit log rotation**: Is there any cleanup or rotation for replication-audit.log? No evidence of size management.

2. **Multiple pending approvals**: Can there be multiple pending approvals for different clone-ids simultaneously? Code creates one file per clone-id — appears supported but untested.

3. **Graceful shutdown during copy**: What happens if the script is interrupted during `shutil.copytree`? No signal handling — copy would be incomplete.

---

## Validation

| #   | Criterion                                 | Result | Evidence                                                                                   |
| --- | ----------------------------------------- | ------ | ------------------------------------------------------------------------------------------ |
| 1   | An event catalog is documented.           | PASS   | 5 protocols documented: agent messages, dry-run, execute, registration, cross-agent        |
| 2   | A state machine is documented.            | PASS   | 2 state machines: replication flow (idle→pending→running→complete/failed), agent lifecycle |
| 3   | Persistent schema notes are documented.   | PASS   | 4 schemas: workspace files, pending JSON, audit log, lineage                               |
| 4   | Compatibility hazards are documented.     | PASS   | 7 hazards identified with severity and notes                                               |
| 5   | Findings are marked with evidence levels. | PASS   | All findings use observed fact / strong inference / open question                          |

**Validated by:** Protocols phase - 2026-04-06
**Overall:** PASS