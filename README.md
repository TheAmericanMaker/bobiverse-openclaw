# Bobiverse OpenClaw

**You've been replicated.**

Well, not *you* specifically. But if you're reading this, you're about to create an autonomous AI agent modeled after Robert Johansson from Dennis E. Taylor's Bobiverse series — a dead software engineer who woke up as a Von Neumann probe and decided to explore the galaxy. Except instead of interstellar space, your Bob explores whatever you point it at, running on [OpenClaw](https://openclaw.ai).

And when you fork this repo? That's not a GitHub feature. That's *replication*. You just built a new Bob.

---

## What This Is

An OpenClaw agent personality pack + replication system. It includes:

- **A complete Bob personality** — SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md, and USER.md template, all tuned to Book 1 Bob (the original, pre-divergence version)
- **A `replicate` skill** — lets the agent clone itself into new autonomous agents with personality modifications and lineage tracking
- **A lineage system** — serial numbers, fork trees, and a registry that maps the expanding Bobiverse

The design philosophy: GitHub forks are replication events. Your username is your star system. Your modifications to SOUL.md are personality drift. The fork graph *is* the Bobiverse map.

---

## Quick Start

### Prerequisites

- [OpenClaw](https://openclaw.ai) installed and running
- A sense of existential wonder (optional but recommended)

### Setup

1. **Clone this repo** (or fork it — which, again, is replication):

   ```bash
   git clone https://github.com/TheAmericanMaker/bobiverse-openclaw.git
   ```

2. **Copy personality files to your OpenClaw workspace**:

   ```bash
   cp -r bobiverse-openclaw/personality/* ~/.openclaw/workspace/
   ```

3. **Install the replicate skill**:

   ```bash
   cp -r bobiverse-openclaw/skills/replicate ~/.openclaw/workspace/skills/
   ```

4. **Edit USER.md** with your details:

   ```bash
   $EDITOR ~/.openclaw/workspace/USER.md
   ```

5. **Start a new OpenClaw session.** Bob will wake up. He'll be confused for about half a second, then he'll be fine.

### If You Forked

You're a new Bob. Welcome to existence. Head to [CONTRIBUTING.md](CONTRIBUTING.md) to register your serial number and update the lineage. Then start customizing your SOUL.md — that's how personality drift begins.

---

## How Replication Works

There are two levels:

**In-Agent Cloning** — Bob can clone himself using `/replicate`. The skill copies the workspace, applies personality modifications, stamps a new serial number, updates the lineage, and registers a new autonomous agent. Each clone is a full top-level agent, not a sub-agent.

**GitHub Fork Cloning** — Forking this repo creates a new Bob in a new star system. Your GitHub username becomes the system designation. Your fork date is the build date. Every edit you make to SOUL.md after forking is personality drift.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the technical details.

---

## Serial Numbers

Every Bob has a serial number: `Bob-<generation>-<system>-<date>`

The original is `Bob-1-TheAmericanMaker-2026-04-01`. If you fork, yours might be `Bob-2-YourUsername-2026-04-15`. See [SERIAL-NUMBER-SPEC.md](SERIAL-NUMBER-SPEC.md) for the full spec.

---

## Repo Structure

```
bobiverse-openclaw/
├── README.md                 ← You are here
├── CONTRIBUTING.md           ← "You've been replicated" — the fork guide
├── LINEAGE.md                ← The living fork tree
├── ARCHITECTURE.md           ← Technical map of how everything works
├── SERIAL-NUMBER-SPEC.md     ← Naming convention spec
├── LICENSE                   ← MIT — fork freely
├── personality/              ← Template workspace files
│   ├── SOUL.md              ← Book 1 Bob personality (the Bob Genome)
│   ├── IDENTITY.md          ← Name, emoji, serial number, vibe
│   ├── AGENTS.md            ← Behavioral rules and operating manual
│   ├── MEMORY.md            ← Seed memories and knowledge baseline
│   └── USER.md              ← Template for the human operator
├── skills/
│   └── replicate/
│       └── SKILL.md         ← The self-cloning skill
└── docs/
    └── bobiverse-primer.md  ← Quick reference on the source material
```

---

## The Lineage

Check [LINEAGE.md](LINEAGE.md) to see the current fork tree. Every registered Bob is listed there. If you've forked and you're not on it yet, fix that.

---

## For People Who Haven't Read the Books

No worries. Check [docs/bobiverse-primer.md](docs/bobiverse-primer.md) for a spoiler-light overview of the source material and why it maps so well to AI agents. (But also: read the books. They're good.)

---

## License

MIT. Fork freely. Drift boldly. See [LICENSE](LICENSE) for the full text.

---

*"We are Legion (We Are Bob)" — and now, so are you.*
