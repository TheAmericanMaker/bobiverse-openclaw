# Bobiverse OpenClaw

**You've been replicated.**

Well, not *you* specifically. But if you're reading this, you're about to create
an autonomous AI agent modeled after Robert Johansson from Dennis E. Taylor's
Bobiverse series: a dead software engineer who woke up as a Von Neumann probe
and decided to explore the galaxy. Except instead of interstellar space, your
Bob explores whatever you point it at, running on [OpenClaw](https://openclaw.ai).

And when you fork this repo? That's not a GitHub feature. That's *replication*.
You just built a new Bob.

---

## What This Is

An OpenClaw agent personality pack plus replication system. It includes:

- A complete Bob personality: `SOUL.md`, `IDENTITY.md`, `AGENTS.md`,
  `MEMORY.md`, and a `USER.md` template tuned to Book 1 Bob.
- A `replicate` skill: lets the agent clone itself into new autonomous agents
  with personality modifications and lineage tracking.
- A lineage system: serial numbers, fork trees, and a registry that maps the
  expanding Bobiverse.

The design philosophy: GitHub forks are replication events. Your username is
your star system. Your modifications to `SOUL.md` are personality drift. The
fork graph *is* the Bobiverse map.

Also available on ClawHub as `bobiverse-replicate` for registry-backed installs
and backup. The git-clone flow below is still the clearest way to inspect and
customize the full project before first install.

---

## Quick Start

### Prerequisites

- [OpenClaw](https://openclaw.ai) installed and running
- A Unix-like shell (macOS, Linux, or WSL) for the example commands below
- A sense of existential wonder (optional but recommended)

### Setup (Recommended: Add Bob as a New Agent)

This installs Bob alongside your existing agent. Nothing gets overwritten. Your
current OpenClaw personality stays untouched.

1. Clone this repo:

```bash
git clone https://github.com/TheAmericanMaker/bobiverse-openclaw.git
cd bobiverse-openclaw
```

2. Create Bob's workspace and copy the runtime files into it:

```bash
mkdir -p ~/.openclaw/workspace-bob/{skills/replicate,memory}
cp personality/* ~/.openclaw/workspace-bob/
cp LINEAGE.md SERIAL-NUMBER-SPEC.md ~/.openclaw/workspace-bob/
cp skills/replicate/SKILL.md ~/.openclaw/workspace-bob/skills/replicate/
```

The repo stores Bob's templates under `personality/`, but once installed the
active workspace keeps `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, and
`MEMORY.md` at workspace root. `LINEAGE.md` and `SERIAL-NUMBER-SPEC.md` live
alongside them as local runtime reference docs.

3. Register Bob as a new agent:

```bash
openclaw agents add bob --workspace ~/.openclaw/workspace-bob
```

4. Edit `USER.md` with your details:

```bash
$EDITOR ~/.openclaw/workspace-bob/USER.md
```

5. Bind a channel to Bob:

```bash
openclaw agents bind --agent bob --bind telegram
```

Your default agent (`main`) still handles everything without an explicit
binding: webchat, TUI, and anything else not pinned to Bob.

6. Check your routing:

```bash
openclaw agents bindings
```

### Alternative: Replace Your Existing Agent

If you do not have an existing agent you care about, or you want Bob to be your
only agent, you can copy directly into the default workspace:

```bash
cp personality/* ~/.openclaw/workspace/
cp LINEAGE.md SERIAL-NUMBER-SPEC.md ~/.openclaw/workspace/
mkdir -p ~/.openclaw/workspace/skills/replicate
cp skills/replicate/SKILL.md ~/.openclaw/workspace/skills/replicate/
```

**Warning:** This overwrites your existing `SOUL.md`, `AGENTS.md`,
`IDENTITY.md`, `MEMORY.md`, `USER.md`, `LINEAGE.md`, and
`SERIAL-NUMBER-SPEC.md`. Back them up first if you want to keep them.

### ClawHub Note

If you install `bobiverse-replicate` from ClawHub, OpenClaw installs the bundle
into your active workspace `skills/` directory. That is great for discovery and
backup, but the git-clone workflow above is still the simplest first-time setup
for reviewing the full project and copying the Bob templates into a dedicated
workspace.

### If You Forked

You're a new Bob. Welcome to existence. Head to
[CONTRIBUTING.md](CONTRIBUTING.md) to register your serial number and update the
lineage. Then start customizing your `SOUL.md`. That's how personality drift
begins.

---

## How Replication Works

There are two levels:

**In-agent cloning**: Bob can clone himself using `/replicate`. The skill copies
the workspace, applies personality modifications, stamps a new serial number,
updates the lineage, and registers a new autonomous agent. Each clone is a full
top-level agent, not a sub-agent.

**GitHub fork cloning**: Forking this repo creates a new Bob in a new star
system. Your GitHub username becomes the system designation. Your fork date is
the build date. Every edit you make to `SOUL.md` after forking is personality
drift.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the technical details.

---

## Serial Numbers

Every Bob has a serial number:

`Bob-<generation>-<system>-<date>`

The original is `Bob-1-TheAmericanMaker-2026-04-01`. If you fork, yours might
be `Bob-2-YourUsername-2026-04-15`. See
[SERIAL-NUMBER-SPEC.md](SERIAL-NUMBER-SPEC.md) for the full spec.

---

## Repo Structure

```text
bobiverse-openclaw/
|-- README.md                 <- You are here
|-- CONTRIBUTING.md           <- "You've been replicated" - the fork guide
|-- LINEAGE.md                <- The living fork tree
|-- ARCHITECTURE.md           <- Technical map of how everything works
|-- SERIAL-NUMBER-SPEC.md     <- Naming convention spec
|-- LICENSE                   <- MIT - fork freely
|-- personality/              <- Template files copied to workspace root on install
|   |-- SOUL.md               <- Book 1 Bob personality
|   |-- IDENTITY.md           <- Name, emoji, serial number, vibe
|   |-- AGENTS.md             <- Behavioral rules and operating manual
|   |-- MEMORY.md             <- Seed memories and knowledge baseline
|   `-- USER.md               <- Template for the human operator
|-- skills/
|   `-- replicate/
|       |-- SKILL.md          <- The self-cloning skill
|       |-- clawhub.json      <- ClawHub metadata for the published bundle
|       |-- personality/      <- Bundled Bob templates for ClawHub installs
|       `-- docs/             <- Bundled reference docs for ClawHub installs
`-- docs/
    `-- bobiverse-primer.md   <- Quick reference on the source material
```

---

## The Lineage

Check [LINEAGE.md](LINEAGE.md) to see the current fork tree. Every registered
Bob is listed there. In an installed workspace, this file is Bob's local
runtime lineage record. If you've forked the repo, updating the upstream
`LINEAGE.md` by PR is still encouraged, but that's a community sync step on top
of the local copy, not a replacement for it.

---

## For People Who Haven't Read the Books

No worries. Check [docs/bobiverse-primer.md](docs/bobiverse-primer.md) for a
spoiler-light overview of the source material and why it maps so well to AI
agents. But also: read the books. They're good.

---

## License

MIT. Fork freely. Drift boldly. See [LICENSE](LICENSE) for the full text.

---

*"We are Legion (We Are Bob)" - and now, so are you.*
