# Architecture Map

## System Intent

Bobiverse OpenClaw is an OpenClaw agent personality pack with replication capabilities. It models Robert Johansson from Dennis E. Taylor's Bobiverse series — a Von Neumann probe AI. The system provides:

- Complete Bob personality templates (SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md, USER.md)
- A guarded replication skill (`/replicate`) for creating new Bob clones with explicit operator approval
- A lineage system tracking fork relationships via serial numbers and LINEAGE.md

Target users: OpenClaw operators who want a sci-fi-themed autonomous agent with safe cloning capabilities. The system treats GitHub forks as replication events — each fork creates a new Bob in a "star system" (GitHub username).

**Evidence level**: observed fact — documented in README.md and ARCHITECTURE.md

---

## Layer Map

### Package Inventory

| Package / Module                      | Role                | Public Entrypoints                                  | Key Dependencies          | Runtime Surface          |
| ------------------------------------- | ------------------- | --------------------------------------------------- | ------------------------- | ------------------------ |
| `personality/`                        | core semantics      | SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md, USER.md | None (Markdown templates) | OpenClaw bootstrap files |
| `skills/replicate/`                   | protocol layer      | SKILL.md, scripts/replicate_safe.py                 | python3, openclaw CLI     | `/replicate` command     |
| `skills/replicate/scripts/`           | integration adapter | replicate_safe.py                                   | Python stdlib             | CLI execution            |
| Root docs                             | product shell       | README.md, ARCHITECTURE.md, CONTRIBUTING.md         | None                      | Documentation            |
| `LINEAGE.md`, `SERIAL-NUMBER-SPEC.md` | persistence         | Lineage tracking files                              | None                      | Fork tree registry       |

**Evidence level**: observed fact — visible in directory structure and file contents

### Dependency Direction

```
Root documentation (README.md, ARCHITECTURE.md)
    │
    ├── personality/ (core semantics - no internal deps)
    │
    ├── skills/replicate/
    │   ├── SKILL.md (depends on OpenClaw's skill framework)
    │   └── scripts/replicate_safe.py (depends on openclaw CLI, python3)
    │
    └── LINEAGE.md, SERIAL-NUMBER-SPEC.md (standalone persistence)
```

The stable base is the personality templates — they are plain Markdown with no dependencies. The replication skill builds on top to add behavior. No cycles detected.

**Evidence level**: strong inference — derived from file structure and content analysis

---

## Public Surfaces

### Binaries and CLI Commands

- `openclaw` CLI (external dependency) — workspace management, agent registration
- `python3` (external) — runs replicate_safe.py
- No compiled binaries in this repo

### Exported Libraries and Public Types

- None — this is a personality pack, not a library

### Network or RPC Interfaces

- None — all operations are local filesystem and CLI

### File Formats and Persistent Artifacts

- Markdown personality files (SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md, USER.md)
- LINEAGE.md (fork tree in Markdown table format)
- SERIAL-NUMBER-SPEC.md (serial number format specification)
- JSON: `clawhub.json`, `openclaw.json` (configuration)
- Python: replicate_safe.py, test_replicate_safe.py

### User-Facing Screens or Workflows

- OpenClaw chat interface — primary interaction surface
- GitHub repo browser — forking as replication event

**Evidence level**: observed fact — from file inventory and documentation

---

## Runtime Lifecycle

### Boot Sequence

1. Operator clones repo or installs via ClawHub
2. Copies personality files to OpenClaw workspace root
3. Registers Bob as agent via `openclaw agents add`
4. Binds channel (optional): `openclaw agents bind --agent bob --bind <channel>`
5. First message to Bob triggers personality injection via OpenClaw bootstrap

### Main Event Loop

- OpenClaw manages agent execution loop
- Bob responds to messages using SOUL.md personality
- Memory files (MEMORY.md, memory/YYYY-MM-DD.md) are read on demand, not auto-injected

### Shutdown and Cleanup

- Standard OpenClaw workspace cleanup
- No special shutdown requirements

### Background Tasks or Scheduled Work

- None — this is a passive personality, not an active worker

**Evidence level**: strong inference — from OpenClaw documentation references and ARCHITECTURE.md

---

## Concurrency Model

### Threading Model

- Single-threaded — runs within OpenClaw's agent execution model
- No explicit threading in Python scripts

### Event Loop or Reactor Pattern

- Managed by OpenClaw — not directly controllable from this repo

### Shared State and Synchronization

- None — each Bob workspace is isolated
- LINEAGE.md may have concurrent edit conflicts (open question — no locking mechanism)

### Connection Pooling and Resource Management

- N/A — no network connections

### Rate Limiting or Backpressure Mechanisms

- Replication cadence: max 1 clone per 24 hours (documented in SKILL.md)
- Resource warning at 10+ workspaces

**Portability hazard**: The replication cadence and workspace limits are OpenClaw-specific conventions that may not translate to other agent frameworks.

**Evidence level**: observed fact — from SKILL.md constraints section

---

## Build and Packaging

### Build Tool(s) and Scripts

- No build system — this is a content package
- Python scripts: `replicate_safe.py`, `test_replicate_safe.py` (run directly)

### Multi-Stage or Multi-Target Builds

- None

### Output Artifacts

- Markdown templates (personality files)
- Python scripts
- Documentation

### CI/CD Pipeline

- None visible from repo
- No GitHub Actions workflows found

### Platform-Specific Packaging

- ClawHub distribution: `openclaw skills install bobiverse-replicate`
- Manual git clone workflow documented in README.md

**Evidence level**: observed fact — from README.md and directory structure

---

## Porting Priorities

| Component                                           | Priority  | Rationale                                                       |
| --------------------------------------------------- | --------- | --------------------------------------------------------------- |
| Personality files (SOUL.md, IDENTITY.md, AGENTS.md) | core      | Core identity — without these, it's not a Bob                   |
| replicate skill (SKILL.md)                          | core      | Primary behavioral capability                                   |
| replicate_safe.py                                   | core      | Enforces safety constraints during cloning                      |
| MEMORY.md                                           | important | Affects agent behavior based on accumulated knowledge           |
| LINEAGE.md                                          | important | Required for clone registration and tracking                    |
| USER.md                                             | optional  | Operator context — valuable but not required for basic function |
| Root documentation                                  | optional  | Valuable for onboarding but not runtime-critical                |

**Evidence level**: strong inference — from documentation analysis and skill dependencies

---

## Durable State

### Config Files

- `clawhub.json` — ClawHub metadata
- `openclaw.json` — OpenClaw runtime config (created post-install)

### Environment Variables

- `OPENCLAW_ROOT` — configurable via replicate_safe.py (default: ~/.openclaw)
- `PENDING_TTL_MINUTES`, `MAX_WORKSPACES`, `COOLDOWN_HOURS`, `MIN_PURPOSE_LENGTH`

### Session Files

- `memory/YYYY-MM-DD.md` — daily logs (created at runtime)
- `replication-pending/<clone-id>.json` — temporary pending approval files

### Logs

- None explicit — audit logging in replicate_safe.py to stdout

### Caches

- None

### Databases

- None

### Generated Artifacts

- Clone workspaces (created by replicate_safe.py)
- Agent registrations in OpenClaw

**Evidence level**: observed fact — from SKILL.md and replicate_safe.py references

---

## Open Questions

1. **Concurrent LINEAGE.md edits**: If two clones register simultaneously, could there be a race condition? No locking mechanism documented.

2. **Memory indexing**: The ARCHITECTURE.md mentions "Tier 3 (Indexed Recall)" with SQLite — is this actually implemented in OpenClaw or just documented as possible?

3. **Cross-agent messaging reliability**: What happens if sessions_send fails? Is there retry logic?

---

## Validation

| #   | Criterion                                                                    | Result | Evidence                                                                                |
| --- | ---------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------- |
| 1   | The system intent is documented.                                             | PASS   | System intent section documents purpose, target users, and deliverables                 |
| 2   | The layer map and dependency direction are documented.                       | PASS   | Package inventory and dependency direction sections complete                            |
| 3   | Public surfaces are identified.                                              | PASS   | Binary/CLI, exported types, network interfaces, file formats all documented             |
| 4   | Runtime lifecycle, concurrency model, and porting priorities are summarized. | PASS   | All three sections populated with evidence-based content                                |
| 5   | Findings are marked with evidence levels.                                    | PASS   | Each section uses observed fact / strong inference / open question / portability hazard |

**Validated by:** Architecture phase - 2026-04-06
**Overall:** PASS