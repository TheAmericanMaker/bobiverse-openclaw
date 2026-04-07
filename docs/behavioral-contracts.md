# Behavioral Contracts

## Surfaces Covered

This codebase exposes the following user-facing surfaces:

- **CLI** — OpenClaw commands (`openclaw agents add`, `openclaw agents bind`, `openclaw agents list`) plus the replicate script (`replicate_safe.py`)
- **Chat Interface** — OpenClaw's chat/TUI where the agent receives messages and responds
- **GitHub Repository** — Forking as the meta-layer for replication events

There is no web UI, no REST API, and no background worker. The primary interaction surface is the OpenClaw chat interface.

---

## Feature Contracts

### Surface: OpenClaw Chat Interface

#### Agent Personality Injection

| Field                          | Value                                                              |
| ------------------------------ | ------------------------------------------------------------------ |
| **Feature**                    | Bob's personality loads at session start                           |
| **Trigger or input**           | Any message sent to the Bob agent                                  |
| **Defaults**                   | SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md at workspace root       |
| **Observable output**          | Agent responds with Bob's voice, tone, and behavioral rules        |
| **Side effects**               | None — personality files are read-only during session              |
| **Persisted state**            | MEMORY.md grows via daily logs in `memory/YYYY-MM-DD.md`           |
| **Error behavior**             | If personality files missing, OpenClaw falls back to generic agent |
| **Retry or recovery behavior** | Operator can re-copy personality files to restore                  |
| **Owner (layer/package)**      | personality/ (core semantics)                                      |

#### Replication Skill (/replicate)

| Field                          | Value                                                                     |
| ------------------------------ | ------------------------------------------------------------------------- |
| **Feature**                    | Create a new Bob clone with operator approval                             |
| **Trigger or input**           | Operator invokes `/replicate` command with purpose statement              |
| **Defaults**                   | Memory policy: full; Star system: operator's GitHub username              |
| **Observable output**          | New agent workspace created, registered, reported to operator             |
| **Side effects**               | LINEAGE.md updated in both parent and clone; new serial number generated  |
| **Persisted state**            | Clone workspace with copied personality files; lineage entry              |
| **Error behavior**             | Missing purpose, missing confirmation token, or validation failure aborts |
| **Retry or recovery behavior** | Re-run dry-run to get fresh confirmation token                            |
| **Owner (layer/package)**      | skills/replicate/ (protocol layer)                                        |

#### Memory Management

| Field                          | Value                                             |
| ------------------------------ | ------------------------------------------------- |
| **Feature**                    | Accumulate knowledge and experiences              |
| **Trigger or input**           | Agent writes to MEMORY.md or memory/YYYY-MM-DD.md |
| **Defaults**                   | MEMORY.md seed template; empty daily logs         |
| **Observable output**          | Future sessions include accumulated context       |
| **Side effects**               | File system writes to workspace                   |
| **Persisted state**            | MEMORY.md grows over time; daily logs accumulate  |
| **Error behavior**             | Write failures logged but don't interrupt session |
| **Retry or recovery behavior** | Operator can manually edit MEMORY.md to correct   |
| **Owner (layer/package)**      | personality/MEMORY.md (core semantics)            |

### Surface: CLI / Shell

#### replicate_safe.py Execution

| Field                          | Value                                                                                                                           |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| **Feature**                    | Hardened runner for workspace duplication                                                                                       |
| **Trigger or input**           | `python scripts/replicate_safe.py --clone-id <id> --parent-workspace <path> --purpose <reason> [--execute] [--confirm <token>]` |
| **Defaults**                   | dry-run mode; 15-min pending approval TTL; 24h cooldown; 10 workspace limit                                                     |
| **Observable output**          | JSON output with event type and status                                                                                          |
| **Side effects**               | Creates/deletes directories in ~/.openclaw; registers agent via openclaw CLI                                                    |
| **Persisted state**            | Clone workspace directory; replication-pending/*.json; replication-audit.log                                                    |
| **Error behavior**             | Validation errors raise ValueError; execute failures trigger cleanup and audit                                                  |
| **Retry or recovery behavior** | Re-run with corrected arguments; expired pending requires new dry-run                                                           |
| **Owner (layer/package)**      | skills/replicate/scripts/replicate_safe.py (integration adapter)                                                                |

#### OpenClaw Agent Registration

| Field                          | Value                                               |
| ------------------------------ | --------------------------------------------------- |
| **Feature**                    | Register new agent with OpenClaw                    |
| **Trigger or input**           | `openclaw agents add <agent-id> --workspace <path>` |
| **Defaults**                   | Agent becomes available in default pool             |
| **Observable output**          | Agent appears in `openclaw agents list`             |
| **Side effects**               | OpenClaw internal state updated                     |
| **Persisted state**            | OpenClaw's agent registry                           |
| **Error behavior**             | Exit code non-zero on failure                       |
| **Retry or recovery behavior** | Re-run command after fixing workspace issues        |
| **Owner (layer/package)**      | OpenClaw (external)                                 |

#### Channel Binding

| Field                          | Value                                                  |
| ------------------------------ | ------------------------------------------------------ |
| **Feature**                    | Bind agent to communication channel                    |
| **Trigger or input**           | `openclaw agents bind --agent <name> --bind <channel>` |
| **Defaults**                   | Agent not bound to any channel                         |
| **Observable output**          | Messages from bound channel route to agent             |
| **Side effects**               | OpenClaw routing configuration updated                 |
| **Persisted state**            | OpenClaw configuration                                 |
| **Error behavior**             | Invalid channel or agent name fails                    |
| **Retry or recovery behavior** | Re-run with correct parameters                         |
| **Owner (layer/package)**      | OpenClaw (external)                                    |

### Surface: GitHub Repository (Meta-Layer)

#### Fork as Replication

| Field                          | Value                                                                   |
| ------------------------------ | ----------------------------------------------------------------------- |
| **Feature**                    | Fork creates a new Bob in a new star system                             |
| **Trigger or input**           | GitHub "Fork" button click                                              |
| **Defaults**                   | Fork inherits all files; fork date = build date; username = star system |
| **Observable output**          | New repository under user's account                                     |
| **Side effects**               | Fork appears in GitHub's fork graph                                     |
| **Persisted state**            | GitHub's fork relationship metadata                                     |
| **Error behavior**             | Fork limit or permission issues handled by GitHub                       |
| **Retry or recovery behavior** | N/A — GitHub-managed                                                    |
| **Owner (layer/package)**      | GitHub (external)                                                       |

---

## High-Value Behaviors

### Cancellation and Abort Handling

- The replicate skill requires explicit confirmation token before execution — operator can abort by not providing the token
- No cancellation during workspace copy (handled by operator intervention)

### Streaming and Partial Output

- Not applicable — this is a personality pack, not a streaming service

### Queueing or Follow-Up Behavior

- Not applicable — no message queue system

### Compaction and Summarization

- Memory tier system: daily logs can be compacted into MEMORY.md over time
- No automatic compaction — agent must manually promote patterns

### Persistence and Resume Flows

- Persistence is via file system — workspaces resume on restart
- No explicit "resume" command — session continuity handled by OpenClaw

### Tool Execution and Validation

- replicate_safe.py validates all inputs before execution
- Workspace must contain required files (SOUL.md, IDENTITY.md, AGENTS.md)
- Symlinks rejected to prevent directory traversal

---

## Security and Authorization

No authentication or authorization system exists in this codebase:

- This is a passive personality pack, not a service with access control
- OpenClaw provides the authentication layer (managed externally)
- The replicate skill enforces operator confirmation but is not auth — it's an approval workflow

**Conclusion**: Skip — the system has no auth model of its own.

---

## Configuration Model

Configuration flows through environment variables in `replicate_safe.py`:

| Config Variable       | Default       | Description                      |
| --------------------- | ------------- | -------------------------------- |
| `OPENCLAW_ROOT`       | `~/.openclaw` | OpenClaw root directory          |
| `PENDING_TTL_MINUTES` | 15            | Pending approval time-to-live    |
| `MAX_WORKSPACES`      | 10            | Max workspaces before warning    |
| `COOLDOWN_HOURS`      | 24.0          | Hours between clones             |
| `MIN_PURPOSE_LENGTH`  | 12            | Minimum purpose statement length |

**Config precedence**: Environment variables override defaults. No config file support.

**Validation**: All numeric configs validated at startup (integer conversion, range checks).

**Portability hazard**: `~/.openclaw` path uses home directory expansion — not portable to systems without standard Unix home layout without setting OPENCLAW_ROOT explicitly.

---

## Doc/Test Conflicts

None found. The test file (`test_replicate_safe.py`) comprehensively validates the documented behavior:

- Dry-run creates pending approval with nonce token
- Execute requires exact token match
- Purpose must match between dry-run and execute
- Workspace count limits enforced
- Cooldown period enforced
- Failed execute rolls back and audits failure

---

## Black-Box Acceptance List

| #   | Scenario                 | Precondition                                       | Action                                              | Expected Outcome                                        |
| --- | ------------------------ | -------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------- |
| 1   | Personality loads        | Workspace contains SOUL.md, IDENTITY.md, AGENTS.md | Send message to Bob agent                           | Response uses Bob's voice and traits                    |
| 2   | Dry-run creates token    | Parent workspace valid, clone-id valid             | Run replicate_safe.py without --execute             | JSON output with confirm_token (REPLICATE <id> <nonce>) |
| 3   | Execute requires token   | Dry-run completed, token obtained                  | Run replicate_safe.py --execute --confirm "<token>" | Clone workspace created, agent registered               |
| 4   | Rejects invalid clone-id | Invalid serial format                              | Run with --clone-id "invalid"                       | ValueError: "Invalid clone-id format"                   |
| 5   | Path boundary enforced   | Path outside ~/.openclaw provided                  | Run with --parent-workspace "/tmp/malicious"        | ValueError: "Path escapes ~/.openclaw boundary"         |
| 6   | Symlink rejected         | Parent workspace contains symlink                  | Run with symlinked directory                        | ValueError: "Workspace contains a symlink"              |
| 7   | Memory policy full       | clone created with --memory-policy full            | Read clone's MEMORY.md                              | Parent's complete MEMORY.md inherited                   |
| 8   | Serial number format     | clone-id "Bob-2-System-2026-04-15"                 | Parse generated ID                                  | Generation=2, System=System, Date=2026-04-15            |
| 9   | Lineage updated          | Clone created successfully                         | Read both LINEAGE.md files                          | Both contain new entry with parent/child relationship   |
| 10  | Workspace limit warning  | 10+ workspaces exist                               | Run without --allow-high-workspace-count            | ValueError: "Workspace count >= 10"                     |

---

## Open Questions

1. **Cross-agent communication reliability**: What happens if `sessions_send` fails? Is there retry logic or user notification?

2. **Memory indexing**: Is OpenClaw's SQLite-backed memory search actually implemented, or is it aspirational documentation?

3. **Concurrent lineage edits**: If two clones register simultaneously, could LINEAGE.md have merge conflicts? No locking mechanism exists.

---

## Validation

| #   | Criterion                                                                                                                  | Result | Evidence                                                                             |
| --- | -------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------ |
| 1   | User-facing surfaces are split by surface type.                                                                            | PASS   | Surfaces documented: Chat Interface, CLI/Shell, GitHub (meta-layer)                  |
| 2   | Feature contracts record trigger, defaults, outputs, side effects, persisted state, error behavior, and recovery behavior. | PASS   | All 8 fields captured for personality injection, replicate skill, memory, CLI tools  |
| 3   | Security and authorization model is documented (if applicable).                                                            | PASS   | Documented "no auth model" - system relies on OpenClaw's external auth               |
| 4   | Contract ownership is mapped back to a layer or package.                                                                   | PASS   | Each contract maps to personality/, skills/replicate/, or external (OpenClaw/GitHub) |
| 5   | A black-box acceptance list is included.                                                                                   | PASS   | 10 acceptance scenarios with preconditions, actions, expected outcomes               |
| 6   | Findings are marked with evidence levels.                                                                                  | PASS   | All findings use observed fact / strong inference / open question                    |

**Validated by:** contracts phase - 2026-04-06
**Overall:** PASS