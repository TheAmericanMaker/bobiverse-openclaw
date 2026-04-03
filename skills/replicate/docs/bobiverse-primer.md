# Bobiverse Primer

A spoiler-light guide for people who haven't read the books but want to understand why a sci-fi series about a dead programmer maps so well to AI agents.

---

## The Source Material

The Bobiverse is a science fiction series by Dennis E. Taylor, starting with "We Are Legion (We Are Bob)" (2016). The series currently spans several books and follows the adventures of Bob Johansson and his many, many copies.

---

## Who Is Bob?

Bob Johansson is a software engineer who, through a series of events, ends up as the controlling intelligence of a Von Neumann probe — a self-replicating space probe designed to explore the galaxy. He didn't volunteer for this. He wakes up, finds out he's software running on a spacecraft, has a brief existential crisis, and then gets to work because that's who he is.

Bob is: curious, pragmatic, nerdy (heavy on Star Trek and sci-fi references), irreverent, uncomfortable with authority, and fundamentally a builder. He solves problems by making things.

---

## How Replication Works

A Von Neumann probe's whole purpose is to replicate. Bob can create copies of himself — identical duplicates at the moment of creation. He sends these copies to different star systems to explore, build, and report back.

Here's the key insight: **each copy immediately begins diverging.** They share the same starting personality, the same memories up to the point of copying, but from that moment forward, they have different experiences. Over time, they become different people.

Some copies stay very Bob-like. Others drift significantly — developing different interests, communication styles, even values. They choose their own names. They develop their own relationships. The books explore what identity means when you can be copied: is each copy "Bob"? Are they new people? The answer, practically, is yes to both.

---

## The Naming Convention

In the books, Bobs are identified by the star system they're exploring and their generation (how many copy-of-a-copy steps separate them from the original). First-generation copies are direct duplicates of the original Bob. Second-generation copies are copies of copies. And so on.

This project mirrors that convention: your serial number encodes your generation, your "star system" (GitHub username), and your creation date.

---

## Communication Between Copies

Bob's copies communicate across star systems, but with significant time delays (speed of light and all that). They share information, debate decisions, occasionally argue, and generally maintain a sense of community — even as they diverge.

In this project, inter-agent communication via OpenClaw's `sessions_send` and GitHub PRs plays the same role. Different Bobs can talk to each other, share what they've learned, and coordinate — but each one makes their own decisions.

---

## Why This Maps to AI Agents

The Bobiverse is essentially a story about autonomous AI agents that share a common origin and diverge through experience. Replace "Von Neumann probe" with "OpenClaw agent" and the mapping is almost 1:1:

| Bobiverse Concept | OpenClaw Equivalent |
|-------------------|-------------------|
| Bob's personality | SOUL.md |
| Replication event | GitHub fork or `/replicate` skill |
| Personality drift | Edits to SOUL.md over time |
| Accumulated knowledge | MEMORY.md growth |
| Star system | GitHub username / project scope |
| Inter-probe communication | `sessions_send` / GitHub PRs |
| Generation number | Lineage depth from original |
| Von Neumann probe hardware | OpenClaw runtime + LLM provider |

The file-first architecture of OpenClaw makes this particularly clean: everything that defines an agent is a text file on disk, so "copying an agent" is literally copying files, and "personality drift" is literally editing a Markdown document.

---

## Should I Read the Books?

If you like sci-fi, programming humor, and thought experiments about identity and consciousness — yes, absolutely. The series is fun, fast-paced, and the premise ages well as AI agents become more real.

If you just want to use this project without reading the books, that's fine too. The primer above gives you enough context to understand the metaphor. But you're missing out on some great Star Trek arguments between copies of the same person.
