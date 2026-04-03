# Architecture — How Bobiverse OpenClaw Works

This document explains the technical design: how OpenClaw's file-first architecture enables self-cloning agents, what each file does, how personality drift happens, and how clones communicate.

---

## Why OpenClaw

OpenClaw is uniquely suited to a Bobiverse-style replicant system because the entire agent "self" lives on disk as plain Markdown files. There's no opaque database, no hidden state, no API-locked personality. Everything that makes a Bob a Bob is in editable, forkable, human-readable files. Cloning an agent is literally copying a directory and changing some text.

---

## Workspace Files and Prompt Context

OpenClaw's current workspace model is centered on standard root-level files
inside the active agent workspace. The repo stores Bob's templates under
`personality/`, but after installation the runtime expects the core files at the
workspace root.

| File | Role |
|------|------|
| `AGENTS.md` | Behavioral rules, safety constraints, workspace conventions |
| `SOUL.md` | Core personality — values, communication style, thinking patterns |
| `TOOLS.md` | Environment-specific tool conventions |
| `IDENTITY.md` | External presentation — name, emoji, serial number, vibe |
| `USER.md` | Human operator context — name, preferences, working style |
| `HEARTBEAT.md` | Optional periodic check-in task list |
| `BOOT.md` | Optional startup checklist for gateway restart hooks |
| `BOOTSTRAP.md` | One-time first-run onboarding for brand-new workspaces |
| `MEMORY.md` | Curated long-term knowledge |
| `memory/YYYY-MM-DD.md` | Daily logs and short-term observations |

OpenClaw injects the bootstrap-style root files into prompt context, with
`MEMORY.md` included when present and `memory.md` used only as a lowercase
fallback. Daily files in `memory/` are not auto-injected; the agent reads or
searches them on demand.

For this project, the installed Bob workspace uses `AGENTS.md`, `SOUL.md`,
`IDENTITY.md`, `USER.md`, `MEMORY.md`, `LINEAGE.md`, and
`SERIAL-NUMBER-SPEC.md` at workspace root, plus `skills/replicate/SKILL.md`.
`TOOLS.md`, `HEARTBEAT.md`, `BOOT.md`, and `BOOTSTRAP.md` remain optional.

---

## File Roles in the Bobiverse Context

**SOUL.md = DNA.** This is the personality baseline. The "Bob Genome" section contains core traits that define what makes a Bob a Bob. When a clone is created, it inherits the parent's SOUL.md and then modifies it — that's personality drift. The agent can modify its own SOUL.md at runtime; if it does, it logs the change.

**IDENTITY.md = Birth Certificate.** Contains the serial number, generation, parent info, and fork date. This is the one file where accuracy is non-negotiable. A Bob can change its personality, its skills, its memories — but its serial number and lineage are fixed.

**AGENTS.md = Operating Manual.** Behavioral rules and conventions that govern how the agent operates. This includes replication protocol (always update LINEAGE.md), inter-agent communication etiquette, and workspace conventions. Think of it as the procedural rules, where SOUL.md is the personality rules.

**MEMORY.md = Accumulated Experience.** Starts with seed knowledge (what every Bob knows at birth) and grows as the agent learns. Memory is where long-term divergence really happens — two Bobs with the same SOUL.md but different MEMORY.md files will behave very differently because they know different things.

**USER.md = Operator Dossier.** Template for the human running this Bob. Filled in by the operator, not the agent. This is context, not personality.

**LINEAGE.md = Family Tree.** Not a bootstrap file, but still part of the Bob
runtime package. In an installed workspace it acts as the local lineage record
that Bob can read and update directly. GitHub PRs are the optional upstream sync
layer.

---

## How the Replicate Skill Works

The `/replicate` skill is a Markdown instruction set with YAML frontmatter
(OpenClaw's standard skill format). When invoked, it executes a 10-step
procedure:

1. **Gather parameters** — clone name, personality mods, memory policy, star system
2. **Generate serial number** — increment parent's generation, stamp date
3. **Copy workspace** — duplicate the current workspace to a new directory
4. **Modify SOUL.md** — apply personality changes, add divergence notes
5. **Update IDENTITY.md** — new serial, generation, parent, fork date
6. **Apply memory policy** — full/pruned/minimal inheritance
7. **Update LINEAGE.md** — in both parent and clone workspaces
8. **Register the clone** — `openclaw agents add` creates a new top-level agent
9. **Establish communication** — optional `sessions_send` setup
10. **Report** — tell the operator what happened

Key design decision: clones are created as **top-level agents**, not
sub-agents. By registering each clone as a full agent with
`openclaw agents add`, every Bob has equal standing and full autonomy.

---

## Memory Tiers and Cloning

OpenClaw's memory model affects cloning strategy:

**Tier 1 (Bootstrap Files)** — root-level workspace files like `AGENTS.md`,
`SOUL.md`, `IDENTITY.md`, `USER.md`, and `MEMORY.md`. This is the personality
and identity layer the replicate skill edits directly.

**Tier 2 (Daily Logs)** — `memory/YYYY-MM-DD.md` files. These are not
auto-injected into prompt context, but they can still be read or searched on
demand. When cloning, the memory policy determines whether they carry over.

**Tier 3 (Indexed Recall)** — SQLite-backed memory search over `MEMORY.md` and
`memory/**/*.md`. This is the long-term associative layer. A clone only inherits
that indexed history if the underlying files or index data are copied.

The default memory policy (`full`) copies everything. `pruned` keeps structured knowledge but clears observations and patterns. `minimal` gives the clone just the baseline "What I Know" section — a clean start with basic self-awareness.

---

## How Personality Drift Happens

Drift is not a single mechanism — it's the cumulative effect of several:

**Explicit SOUL.md edits.** The most direct form. A clone (or its operator) modifies personality traits, adds new sections, removes old ones. The "Divergence Notes" section in SOUL.md documents intentional changes.

**Memory accumulation.** Even with identical SOUL.md files, two Bobs with different experiences will behave differently. MEMORY.md grows over time, and the agent's responses are shaped by what it remembers.

**Skill specialization.** Adding or removing skills from a clone's `skills/` directory changes what it can do. A Bob with a `code-reviewer` skill and one with a `research-specialist` skill will approach the same problem differently.

**Operator influence.** USER.md shapes how the agent interacts. Different operators create different interaction patterns, which feed back into memory and potentially into SOUL.md modifications.

Over time, these mechanisms compound. A generation-3 Bob might be recognizably "Bob-like" but have distinctly different priorities, communication patterns, and expertise than the original. This mirrors the books exactly.

---

## Inter-Clone Communication

OpenClaw supports agent-to-agent messaging via `sessions_send`. For Bob-to-Bob communication:

**Setup**: Cross-agent session messaging needs both session-tool visibility and
an agent-to-agent allowlist in `openclaw.json`:
```json
{
  "tools": {
    "sessions": { "visibility": "all" },
    "agentToAgent": {
      "enabled": true,
      "allow": ["bob", "bob-2-someuser-2026-04-15"]
    }
  }
}
```

**Capabilities**: Fire-and-forget delivery, wait-for-reply with timeout, and
multi-turn reply loops.

**GitHub Fork Communication**: Forks can submit PRs to each other. While we haven't established a formal convention for "Bob-to-Bob messages as PRs," the mechanism is there. LINEAGE.md PRs are the minimum expected inter-fork communication.

---

## The GitHub Fork as Replication Event

This is the meta-layer that makes the project work as a community system:

- **Forking the repo = building a new probe.** The act of forking creates a new Bob.
- **Your GitHub username = your star system.** It's where this Bob lives.
- **Your fork date = your build date.** When you came into existence.
- **Your commits = personality drift.** Every change you make diverges you from the parent.
- **GitHub's fork graph = the Bobiverse map.** The network of forks visually represents the expansion.
- **PRs to parent = subspace communication.** When you update LINEAGE.md upstream, you're phoning home.

This metaphor layer costs nothing to maintain — it's built on GitHub's existing infrastructure. The only requirement is that forkers follow the CONTRIBUTING.md guide to register their serial numbers.
