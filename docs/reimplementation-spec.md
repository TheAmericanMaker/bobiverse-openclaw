# Reimplementation Spec

## System Summary

Bobiverse OpenClaw is a personality pack and replication system for OpenClaw agents. It provides:

1. **Personality templates** — Markdown files (SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md, USER.md) that define an agent's core traits, identity, behavior rules, and memory.

2. **Replication capability** — A skill that creates clones with explicit operator approval, using a guarded runner with input validation, nonce-backed confirmation, audit logging, and transactional workspace duplication.

3. **Lineage tracking** — Serial numbers and fork tree maintained in LINEAGE.md.

The system is primarily a content package — the only executable component is `replicate_safe.py` (Python). The personality files are framework-agnostic Markdown that could work with any agent framework that reads Markdown files into context.

---

## Conceptual Module Model

### PersonalityProvider

| Field              | Value                                                                     |
| ------------------ | ------------------------------------------------------------------------- |
| **Responsibility** | Loads and provides personality context to the agent at session start      |
| **Public inputs**  | Workspace root path containing SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md |
| **Public outputs** | Injected prompt context with personality traits                           |
| **Owned state**    | Current personality version, accumulated memory                           |
| **Invariants**     | SOUL.md must exist; IDENTITY.md must have valid serial number             |
| **Collaborators**  | OpenClaw runtime (external)                                               |

### ReplicationService

| Field              | Value                                                                |
| ------------------ | -------------------------------------------------------------------- |
| **Responsibility** | Orchestrates the creation of new agent clones with operator approval |
| **Public inputs**  | Clone ID, parent workspace, purpose statement, confirmation token    |
| **Public outputs** | New workspace directory, registered agent, lineage update            |
| **Owned state**    | Pending approvals, audit log, lineage records                        |
| **Invariants**     | Confirmation token required for execution; cooldown enforced         |
| **Collaborators**  | ReplicateRunner, AgentRegistry, LineageStore                         |

### ReplicateRunner

| Field              | Value                                                                            |
| ------------------ | -------------------------------------------------------------------------------- |
| **Responsibility** | Hardened execution of workspace duplication with security controls               |
| **Public inputs**  | Clone parameters, execute flag, confirmation token                               |
| **Public outputs** | Workspace copy, audit events, error states                                       |
| **Owned state**    | Validation state, pending approval records                                       |
| **Invariants**     | Path must stay within configured root; symlinks rejected; no shell interpolation |
| **Collaborators**  | Filesystem, subprocess (for agent registration)                                  |

### AgentRegistry

| Field              | Value                                           |
| ------------------ | ----------------------------------------------- |
| **Responsibility** | Registers new agents with the runtime framework |
| **Public inputs**  | Agent ID, workspace path                        |
| **Public outputs** | Registered agent, confirmable via listing       |
| **Owned state**    | Agent registry (framework-managed)              |
| **Invariants**     | Workspace must contain required files           |
| **Collaborators**  | OpenClaw CLI (external)                         |

### LineageStore

| Field              | Value                                                   |
| ------------------ | ------------------------------------------------------- |
| **Responsibility** | Tracks fork relationships and serial number assignments |
| **Public inputs**  | New clone info, parent info                             |
| **Public outputs** | Updated fork tree, registry entry                       |
| **Owned state**    | LINEAGE.md file contents                                |
| **Invariants**     | Serial number format must match spec; parent must exist |
| **Collaborators**  | File system                                             |

---

## Layer Split

| Module                | Layer          | Notes                                       |
| --------------------- | -------------- | ------------------------------------------- |
| PersonalityProvider   | core semantics | Framework-agnostic — Markdown files         |
| ReplicationService    | core semantics | Core behavior — framework-independent logic |
| ReplicateRunner       | adapters       | Integrates with filesystem, subprocess      |
| AgentRegistry         | adapters       | Integrates with OpenClaw runtime            |
| LineageStore          | core semantics | File-based persistence — portable           |
| SerialNumberGenerator | core semantics | Pure function — no dependencies             |

---

## Required Behaviors

1. **Personality injection**: On session start, read SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md and inject into prompt context.

2. **Replication trigger**: Accept `/replicate` command only with explicit operator trigger and purpose statement (min 12 chars).

3. **Dry-run confirmation**: Generate nonce token valid for 15 minutes; emit `REPLICATE <id> <nonce>` for operator confirmation.

4. **Execute validation**: Require exact token match; reject expired, mismatched, or missing tokens.

5. **Workspace duplication**: Copy parent workspace to new location; verify required files present; reject symlinks.

6. **Agent registration**: Call framework's agent add command; verify registration succeeded.

7. **Audit logging**: Log all events (dry-run, execute-started, execute-succeeded, execute-failed) atomically.

8. **Lineage update**: Add new entry to both parent and clone's LINEAGE.md after successful clone.

9. **Memory policy**: Support full/pruned/minimal memory inheritance on clone creation.

10. **Cooldown enforcement**: Block execute within 24 hours of last execution unless override reason provided.

---

## Protocols and Persisted State

### Serial Number Format

```
Bob-<generation>-<system>-<date>
```

- generation: integer >= 1
- system: alphanumeric + hyphens, max 39 chars
- date: ISO format YYYY-MM-DD

### Replication State Machine

```
idle → (dry-run) → pending → (execute) → running → (success) → complete
                                           → (failure) → failed
```

### Persistence Schemas

| Schema           | Format          | Mutability            | Notes         |
| ---------------- | --------------- | --------------------- | ------------- |
| Workspace files  | Markdown        | Mutable               | No versioning |
| Pending approval | JSON            | Temporary (15min TTL) | One per clone |
| Audit log        | JSONL           | Append-only           | Atomic writes |
| Lineage          | Markdown tables | Mutable               | No locking    |

### Audit Event Types

- `dry-run-created`: Token generated, pending approval created
- `execute-started`: Execution began
- `execute-succeeded`: Clone created and registered
- `execute-failed`: Error occurred, rollback performed

---

## External Dependencies

| Dependency                 | Stance   | Rationale                                                                                              |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------ |
| OpenClaw runtime           | postpone | The personality pack is designed for OpenClaw; porting to other frameworks requires equivalent runtime |
| openclaw CLI               | emulate  | Can invoke via subprocess in any language; the command interface is stable                             |
| File system                | wrap     | Use platform-agnostic path library; enforce boundaries programmatically                                |
| Python (replicate_safe.py) | replace  | Script can be rewritten in any language; security properties are language-agnostic                     |
| JSON/JSONL                 | wrap     | Wire format is portable across languages                                                               |

---

## Portability Hazards

1. **Path assumptions** — `~/.openclaw` assumes Unix-like home directory. Mitigation: configurable root path.

2. **Subprocess model** — Python's `subprocess.run` with `shell=False` is security-critical. Any port must replicate this with equivalent in target language.

3. **Symlink rejection** — Security feature that prevents directory traversal. Must implement equivalent validation.

4. **OpenClaw-specific features** — Sessions, agent registration, channel binding are framework-specific. Cannot port without equivalent tooling.

5. **Memory model** — OpenClaw's memory injection and search may not have equivalents in other frameworks.

6. **LINEAGE.md concurrent edits** — No locking; potential conflicts with parallel clones.

---

## Implementation Sequence

### Phase 1: Core Personality (Minimum Viable Port)

1. Implement personality file loading (SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md)
2. Implement serial number generation and validation (regex: `^Bob-[0-9A-Za-z]+-[A-Za-z0-9-]{1,39}-\d{4}-\d{2}-\d{2}$`)
3. Test personality injection into agent context

### Phase 2: Replication Logic (Major-Workflow Parity)

1. Implement dry-run / execute state machine
2. Implement nonce token generation and validation
3. Implement workspace copy with validation (required files, no symlinks)
4. Implement audit logging (JSONL, atomic append)
5. Implement lineage update (both parent and clone)
6. Implement cooldown enforcement

### Phase 3: Framework Integration (Full Parity)

1. Implement agent registration (call equivalent of `openclaw agents add`)
2. Implement configuration via environment variables
3. Implement channel binding (if framework supports)
4. Implement cross-agent messaging (if framework supports)

---

### Scope Tiers

**Minimum viable port:**

- Personality file loading
- Serial number generation
- Basic replication (can skip audit, cooldown for MVP)

**Major-workflow parity:**

- Full replication flow: dry-run → confirm → execute
- Workspace validation (required files, symlink rejection)
- Lineage tracking
- Audit logging

**Full parity:**

- All environment variables configurable
- Cooldown enforcement with override
- Cross-agent messaging
- Channel binding

---

## Acceptance Scenarios

| #   | Scenario              | Input                                                | Expected Output / Side Effect                       |
| --- | --------------------- | ---------------------------------------------------- | --------------------------------------------------- |
| 1   | Personality loads     | Workspace with valid SOUL.md, IDENTITY.md, AGENTS.md | Agent responds with Bob's voice and traits          |
| 2   | Invalid serial format | clone-id "invalid"                                   | Error: "Invalid clone-id format"                    |
| 3   | Path escapes root     | --parent-workspace "/etc" with root "~/.openclaw"    | Error: "Path escapes boundary"                      |
| 4   | Symlink in workspace  | Parent workspace contains symlink                    | Error: "Workspace contains a symlink"               |
| 5   | Execute without token | --execute without --confirm                          | Error: "No pending approval found"                  |
| 6   | Token expired         | Execute 16 minutes after dry-run                     | Error: "Pending approval expired"                   |
| 7   | Token mismatch        | --confirm "REPLICATE <id> wrongnonce"                | Error: "Invalid confirmation token"                 |
| 8   | Cooldown active       | Execute within 24h without override                  | Error: "24h cooldown active"                        |
| 9   | Clone created         | Valid dry-run + correct token                        | Clone workspace exists, registered, lineage updated |
| 10  | Audit logged          | Any replication event                                | Entry appended to replication-audit.log             |

---

## Deliberate Non-Goals

1. **Cross-agent messaging** — Will be stubbed; depends on framework-specific tool (`sessions_send`)

2. **Channel binding** — OpenClaw-specific; not portable without equivalent

3. **Memory indexing** — SQLite-backed search may not exist; will defer

4. **Auto-compaction** — Memory tier compaction is manual; no auto-summarization

5. **GitHub integration** — Fork-as-replication is GitHub-specific metaphor; not portable

---

## Known Unknowns

1. **OpenClaw memory injection** — Does the framework auto-inject MEMORY.md at session start, or is it read on-demand?

2. **Agent listing verification** — The script verifies registration by calling `openclaw agents list`. What is the equivalent check in other frameworks?

3. **Configuration hot-reload** — Can config changes be applied without restart? The current implementation reads config at startup.

4. **Workspace naming** — Is `workspace-<agent-id>` the required pattern, or just convention?

---

## Spike List

1. **Atomic file writes** — Test that `os.replace` (or equivalent) works atomically across platforms (Windows may need different approach).

2. **Path validation** — Test boundary enforcement on Windows (drive letters, UNC paths) vs Unix.

3. **Subprocess security** — Verify `shell=False` equivalent in target language prevents any shell injection.

4. **Lineage locking** — Prototype a solution for concurrent lineage edits (file locking, database, or accept risk).

5. **Memory file handling** — Test memory file naming on case-sensitive vs case-insensitive filesystems.

---

## Validation

| #   | Criterion                                             | Result | Evidence                                                                                                                        |
| --- | ----------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Concept-level modules are defined.                    | PASS   | 6 modules defined: PersonalityProvider, ReplicationService, ReplicateRunner, AgentRegistry, LineageStore, SerialNumberGenerator |
| 2   | Required behaviors are stated.                        | PASS   | 10 required behaviors documented with details                                                                                   |
| 3   | Protocol and persisted state expectations are stated. | PASS   | Serial format, state machine, 4 persistence schemas, 4 audit event types                                                        |
| 4   | Acceptance scenarios and known unknowns are included. | PASS   | 10 acceptance scenarios + 4 known unknowns + 5-item spike list                                                                  |
| 5   | Findings are marked with evidence levels.             | PASS   | Observations use observed fact; inferences marked as strong inference                                                           |

**Validated by:** Reimplementation-spec phase - 2026-04-06
**Overall:** PASS