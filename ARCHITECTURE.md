# Architecture — How Bobiverse OpenClaw Works

This document explains the technical design: how OpenClaw's file-first architecture enables self-cloning agents, what each file does, how personality drift happens, and how clones communicate.

---

## Why OpenClaw

OpenClaw is uniquely suited to a Bobiverse-style replicant system because the entire agent "self" lives on disk as plain Markdown files. There's no opaque database, no hidden state, no API-locked personality. Everything that makes a Bob a Bob is in editable, forkable, human-readable files. Cloning an agent is literally copying a directory and changing some text.

---

## The Eight Auto-Loaded Files

OpenClaw loads exactly eight recognized filenames at session start, injected into the system prompt in this order:

| Load Order | File | Role |
|-----------|------|------|
| 1 | `AGENTS.md` | Behavioral rules, safety constraints, workspace conventions |
| 2 | `SOUL.md` | Core personality — values, communication style, thinking patterns |
| 3 | `TOOLS.md` | Environment-specific tool conventions |
| 4 | `IDENTITY.md` | External presentation — name, emoji, serial number, vibe |
| 5 | `USER.md` | Human operator context — name, preferences, working style |
| 6 | `HEARTBEAT.md` | Periodic check-in task list |
| 7 | `BOOTSTRAP.md` | First-run onboarding (self-deletes after execution) |
| 8 | `MEMORY.md` | Curated long-term knowledge (DM sessions only) |

**Important:** Filenames are case-sensitive and MUST be uppercase. The only exception is `MEMORY.md`, which falls back to `memory.md` if the uppercase version isn't found.

For this project, we use files 1, 2, 4, 5, and 8. TOOLS.md, HEARTBEAT.md, and BOOTSTRAP.md are available but not included in the template — operators can add them as needed.

---

## File Roles in the Bobiverse Context

**SOUL.md = DNA.** This is the personality baseline. The "Bob Genome" section contains core traits that define what makes a Bob a Bob. When a clone is created, it inherits the parent's SOUL.md and then modifies it — that's personality drift. The agent can modify its own SOUL.md at runtime; if it does, it logs the change.

**IDENTITY.md = Birth Certificate.** Contains the serial number, generation, parent info, and fork date. This is the one file where accuracy is non-negotiable. A Bob can change its personality, its skills, its memories — but its serial number and lineage are fixed.

**AGENTS.md = Operating Manual.** Behavioral rules and conventions that govern how the agent operates. This includes replication protocol (always update LINEAGE.md), inter-agent communication etiquette, and workspace conventions. Think of it as the procedural rules, where SOUL.md is the personality rules.

**MEMORY.md = Accumulated Experience.** Starts with seed knowledge (what every Bob knows at birth) and grows as the agent learns. Memory is where long-term divergence really happens — two Bobs with the same SOUL.md but different MEMORY.md files will behave very differently because they know different things.

**USER.md = Operator Dossier.** Template for the human running this Bob. Filled in by the operator, not the agent. This is context, not personality.

**LINEAGE.md = Family Tree.** Not an auto-loaded file — it's a repo-level document that tracks all forks and clones. The agent reads it to understand its own history and sibling count.

---

## How the Replicate Skill Works

The `/replicate` skill is a Markdown instruction set with YAML frontmatter (OpenClaw's standard skill format). When invoked, it executes a 10-step procedure:

1. **Gather parameters** — clone name, personality mods, memory policy, star system
2. **Generate serial number** — increment parent's generation, stamp date
3. **Copy workspace** — `cp -r` the entire workspace to a new directory
4. **Modify SOUL.md** — apply personality changes, add divergence notes
5. **Update IDENTITY.md** — new serial, generation, parent, fork date
6. **Apply memory policy** — full/pruned/minimal inheritance
7. **Update LINEAGE.md** — in both parent and clone workspaces
8. **Register the clone** — `openclaw agents add` creates a new top-level agent
9. **Establish communication** — optional `sessions_send` setup
10. **Report** — tell the operator what happened

Key design decision: clones are created as **top-level agents**, not sub-agents. OpenClaw's default flat hierarchy (sub-agents can't spawn sub-agents) would prevent recursive cloning. By registering each clone as a full agent with `openclaw agents add`, every Bob has equal standing and full autonomy.

---

## Memory Tiers and Cloning

OpenClaw's three-tier memory architecture affects cloning strategy:

**Tier 1 (Always-Loaded)** — MEMORY.md and identity files. Loaded every session, subject to a 20,000 character per-file cap. This is what the replicate skill's memory policy directly controls.

**Tier 2 (Daily Context)** — `memory/YYYY-MM-DD.md` files. Today's and yesterday's are auto-loaded. When cloning, the memory policy determines whether these carry over (`full` = yes, `pruned`/`minimal` = no).

**Tier 3 (Deep Knowledge)** — SQLite database with vector search (cosine similarity + BM25 keyword search). This is the agent's long-term associative memory. When cloning, you'd optionally copy the SQLite database to give the clone access to the parent's deep memory.

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

**Setup**: Enable in `openclaw.json`:
```json
{
  "tools.agentToAgent.enabled": true,
  "tools.agentToAgent.allow": ["Bob-1-TheAmericanMaker-2026-04-01", "Bob-2-SomeUser-2026-04-15"]
}
```

**Capabilities**: Fire-and-forget delivery, wait-for-reply with timeout, and multi-turn reply loops (up to 5 turns by default).

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
