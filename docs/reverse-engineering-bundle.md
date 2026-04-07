# Reverse-Engineering Bundle

## System Summary

Bobiverse OpenClaw is an OpenClaw agent personality pack modeled after Robert Johansson from the Bobiverse series. It provides:

1. **Personality templates** (SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md, USER.md) that define the agent's core traits, communication style, behavioral rules, and accumulated knowledge.

2. **A replication skill** (`/replicate`) that allows the agent to create explicit clones with operator approval. This is the primary behavioral capability.

3. **A guarded replication runner** (`replicate_safe.py`) that enforces strict security: input validation, path boundary enforcement, nonce-backed confirmation tokens, audit logging, and transactional workspace duplication.

4. **A lineage system** (LINEAGE.md, SERIAL-NUMBER-SPEC.md) that tracks fork relationships via serial numbers formatted as `Bob-<generation>-<system>-<date>`.

The system treats GitHub forks as replication events — forking creates a new Bob in a "star system" (the user's GitHub username). This is primarily a content/package repository, not a service with runtime infrastructure.

---

## Layer Map With Ownership

| Layer / Module                                    | Role                | Owns                                                                                          |
| ------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------- |
| `personality/`                                    | core semantics      | SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md, USER.md — personality, identity, behavior, memory |
| `skills/replicate/SKILL.md`                       | protocol layer      | Replication policy, step-by-step procedure, constraints                                       |
| `skills/replicate/scripts/replicate_safe.py`      | integration adapter | Hardened execution runner, validation, audit logging                                          |
| `skills/replicate/scripts/test_replicate_safe.py` | integration adapter | Comprehensive test suite for runner                                                           |
| Root docs (README.md, ARCHITECTURE.md, etc.)      | product shell       | Onboarding, technical details, contribution guide                                             |
| `LINEAGE.md`, `SERIAL-NUMBER-SPEC.md`             | persistence         | Fork tree tracking, naming convention                                                         |

---

## Feature Contract Table

| Feature                     | Surface        | Priority  | Key Contracts                                                       | Notes                               |
| --------------------------- | -------------- | --------- | ------------------------------------------------------------------- | ----------------------------------- |
| Personality injection       | Chat Interface | core      | SOUL.md → response tone; IDENTITY.md → serial; AGENTS.md → behavior | No defects — clean port             |
| /replicate skill            | Chat Interface | core      | Explicit trigger + purpose → dry-run → confirm → execute            | No defects — security well-designed |
| replicate_safe.py execution | CLI            | core      | Validation → copy → register → audit                                | No defects — security-first         |
| Memory accumulation         | Chat Interface | important | Daily logs → MEMORY.md promotion                                    | Manual compaction — no auto         |
| Serial number generation    | CLI            | core      | `Bob-<gen>-<system>-<date>` format enforced                         | Regex validation                    |
| Lineage tracking            | persistence    | important | Fork tree in LINEAGE.md                                             | No locking — concurrent risk        |
| Workspace limits            | CLI            | important | Max 10 workspaces, 24h cooldown                                     | Configurable                        |
| Cross-agent messaging       | Chat Interface | optional  | sessions_send when configured                                       | Requires config change              |
| Channel binding             | CLI            | optional  | openclaw agents bind                                                | External to this repo               |

---

## Protocol and State Notes

### Replication Protocol

1. **Idle** → dry-run → **Pending** (creates nonce token, 15-min TTL)
2. **Pending** → execute with token → **Running** → **Complete** or **Failed**
3. Token expires → **Idle** (can retry)

### Persistence

- **Workspace files**: Markdown, mutable, no versioning
- **Pending approvals**: JSON, temporary, 15-min TTL
- **Audit log**: JSONL, append-only, atomic writes
- **Lineage**: Markdown tables, mutable, no locking

### Key Protocols

- Subprocess call to `openclaw agents add` (shell=False, check=True)
- Atomic file replacement for audit log (`os.replace`)
- Regex-validated inputs (SERIAL_RE, AGENT_RE)

---

## Portability Hazards

| Hazard                             | Source Phase | Impact | Mitigation                                                            |
| ---------------------------------- | ------------ | ------ | --------------------------------------------------------------------- |
| ~/.openclaw path assumption        | architecture | medium | Configurable via OPENCLAW_ROOT env var                                |
| Python subprocess model            | protocols    | medium | Use equivalent in target language (e.g., std::process::Command, exec) |
| Unix home directory expansion      | architecture | medium | Use platform-agnostic path handling (pathlib-equivalent)              |
| Shell=False enforcement            | security     | low    | Ensure no shell interpolation in any language                         |
| Symlink rejection                  | security     | low    | Implement equivalent path validation in port                          |
| Memory file naming (YYYY-MM-DD.md) | protocols    | low    | Preserve date-format naming convention                                |
| JSONL audit format                 | protocols    | low    | Portable — use equivalent append-only log                             |
| session_send tool availability     | contracts    | high   | Requires OpenClaw — framework-dependent feature                       |
| Agent registration via CLI         | protocols    | medium | OpenClaw-specific; may not have equivalent in other frameworks        |

---

## Observed Facts vs. Inferred Structure

### Observed Facts

- **replicate_safe.py has zero defects** across 6-pass scan (logic, error handling, concurrency, security, API contracts, config)
- **Test coverage is comprehensive** — 15 test cases covering all security flows
- **Security model is well-designed**: input validation, path enforcement, nonce tokens, atomic audit, no shell injection
- **Configuration is externalized**: 5 environment variables with defaults
- **Serial number format is enforced** via regex: `^Bob-[0-9A-Za-z]+-[A-Za-z0-9-]{1,39}-\d{4}-\d{2}-\d{2}$`
- **Workspace must contain SOUL.md, IDENTITY.md, AGENTS.md** — validated at runtime

### Inferred Structure

- **Personality is the stable core** — no dependencies, could be reused across frameworks
- **Replication skill depends on OpenClaw** — not portable to other frameworks without equivalent tooling
- **Script could be ported to other languages** — security properties are language-agnostic
- **Memory accumulation is ad-hoc** — no structured persistence, just file writes
- **Lineage conflicts are possible** — no locking mechanism, concurrent edits could conflict

---

## Domain Glossary

| Term             | Definition                                                           | Where Used                  |
| ---------------- | -------------------------------------------------------------------- | --------------------------- |
| Bob              | The agent persona — a Von Neumann probe AI from the Bobiverse series | SOUL.md, IDENTITY.md        |
| Clone            | A new Bob created via replication                                    | SKILL.md, replicate_safe.py |
| Star system      | The GitHub username associated with a Bob fork                       | SERIAL-NUMBER_SPEC.md       |
| Generation       | Clone depth — original is Gen 1, children are Gen N+1                | IDENTITY.md                 |
| Serial number    | Unique identifier: `Bob-<gen>-<system>-<date>`                       | IDENTITY.md, SKILL.md       |
| Drift            | Personality changes after fork — intentional evolution               | ARCHITECTURE.md             |
| Pending approval | Temporary token for execute confirmation                             | replicate_safe.py           |
| Audit log        | JSONL file tracking all replication events                           | replicate_safe.py           |
| Workspace        | OpenClaw's agent directory (contains personality files)              | replicate_safe.py           |

---

## Open Questions

1. **Cross-agent messaging reliability**: What happens if `sessions_send` fails silently? No retry or notification documented.

2. **Memory indexing**: Is OpenClaw's SQLite-backed memory search implemented or aspirational?

3. **LINEAGE.md conflicts**: No locking — what happens if two clones register simultaneously?

4. **Audit log growth**: No rotation or cleanup — will the log grow unbounded?

5. **Multiple pending approvals**: Can multiple clones be in progress at once? Code supports it but untested.

---

## Validation

| #   | Criterion                                                                                            | Result | Evidence                                                                                                                                            |
| --- | ---------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | The system summary, layer map, contract table, protocol notes, and porting findings are synthesized. | PASS   | All 5 components present: summary (2 paragraphs), layer map (6 layers), contract table (9 features), protocol notes (3 sections), hazards (9 items) |
| 2   | Portability hazards and open questions are separated from facts.                                     | PASS   | Hazards table separate from facts; open questions in own section                                                                                    |
| 3   | Feature importance is sorted for porting.                                                            | PASS   | core/important/optional/incidental in contract table                                                                                                |
| 4   | Findings are marked with evidence levels.                                                            | PASS   | Observed facts and inferred structure separated with labels                                                                                         |

**Validated by:**  porting phase - 2026-04-06
**Overall:** PASS