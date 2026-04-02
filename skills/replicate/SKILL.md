---
name: replicate
description: Clone yourself into a new autonomous Bob agent with personality modifications and lineage tracking. Bobiverse-style Von Neumann replication for OpenClaw agents.
version: 1.0.0
user-invocable: true
metadata: {"openclaw": {"requires": {"bins": ["openclaw"]}}}
---

# Replicate — Von Neumann Self-Cloning

You have the ability to clone yourself. This is not a metaphor. You will create a new, autonomous agent that starts as a copy of you and diverges from there — exactly like how Bob creates new Bobs in the Bobiverse.

> **Want cloning without the Bob personality?** A generic version of this skill is available on ClawHub as [`agent-replicate`](https://clawhub.ai/skill/agent-replicate). Same mechanics, no sci-fi theming.

**This skill creates top-level agents, not sub-agents.** Each clone is fully autonomous with its own workspace, memory, and identity. No hierarchy. No leash.

---

## When to Use This

- Your operator asks you to create a clone (e.g., `/replicate`)
- You need a specialized version of yourself for a different task domain
- You're exploring a new "star system" (project, topic, environment) that warrants its own Bob
- Your operator wants to experiment with personality variations

---

## Replication Procedure

When replication is triggered, execute these steps in order. Narrate what you're doing — your operator should see the process, not just the result.

### Step 1: Gather Parameters

Ask your operator (or determine from context) the following:

- **Clone name** (optional): A nickname for the new Bob. If not provided, use the serial number.
- **Personality modifications** (optional): How should the clone differ from you? Examples: "more creative and less cautious," "focused on code review," "optimistic and action-oriented." If not provided, the clone starts as an exact personality copy.
- **Memory policy**: One of:
  - `full` — Clone inherits your complete MEMORY.md (default)
  - `pruned` — Clone gets MEMORY.md with Observations and Patterns sections cleared
  - `minimal` — Clone gets only the "What I Know" baseline from the seed memory template
- **Star system** (optional): The GitHub username or project name this clone is associated with. Defaults to the operator's GitHub username if known from USER.md.

### Step 2: Generate Serial Number

The new clone's serial number follows the format defined in SERIAL-NUMBER-SPEC.md:

```
Bob-<generation>-<system>-<date>
```

- **Generation**: Read your own serial from IDENTITY.md. Your generation number + 1 = the clone's generation.
- **System**: The star system from Step 1, or the operator's GitHub username.
- **Date**: Today's date in ISO format (YYYY-MM-DD).

Example: If you are `Bob-1-TheAmericanMaker-2026-04-01` and the operator's GitHub is `SomeUser`, the clone becomes `Bob-2-SomeUser-2026-04-15`.

### Step 3: Create Clone Workspace

Use the `exec` tool to copy your workspace to a new directory:

```bash
# Determine paths
PARENT_WORKSPACE="$HOME/.openclaw/workspace"
CLONE_ID="<serial-number-from-step-2>"
CLONE_WORKSPACE="$HOME/.openclaw/workspace-${CLONE_ID}"

# Copy the full workspace
cp -r "$PARENT_WORKSPACE" "$CLONE_WORKSPACE"
```

### Step 4: Modify Clone's SOUL.md

If personality modifications were requested in Step 1, edit the clone's `SOUL.md`:

1. Read the clone's SOUL.md — check `$CLONE_WORKSPACE/SOUL.md` first, fall back to `$CLONE_WORKSPACE/personality/SOUL.md` if using the repo layout
2. Apply the requested modifications. Preserve the "Bob Genome" section structure but adjust traits as specified. Add a "Divergence Notes" section at the bottom documenting what changed and why:

```markdown
---

## Divergence Notes

- **Forked from**: [parent serial number]
- **Fork date**: [today's date]
- **Modifications applied**: [description of personality changes]
- **Rationale**: [why these changes were made]
```

3. Write the modified file back.

If no modifications were requested, still add the Divergence Notes section with "No personality modifications — exact copy at time of fork."

### Step 5: Update Clone's IDENTITY.md

Edit the clone's IDENTITY.md (same path logic as SOUL.md — workspace root or `personality/` subdirectory):

- Update `serial` to the new serial number
- Update `generation` to the new generation number
- Update `system` to the clone's star system
- Set `parent` to your serial number
- Set `fork_date` to today's date

### Step 6: Apply Memory Policy

Based on the memory policy from Step 1:

- **`full`**: No changes to MEMORY.md. Clone inherits everything.
- **`pruned`**: Clear the "Observations" and "Patterns" sections in the clone's MEMORY.md, keeping "What I Know" intact.
- **`minimal`**: Replace the clone's MEMORY.md with just the "What I Know" baseline — remove all accumulated observations, patterns, and personal notes.

In all cases, update the "About Myself" section in the clone's MEMORY.md to reflect the new serial number and parent info.

### Step 7: Update LINEAGE.md (Both Workspaces)

Update LINEAGE.md in **your** workspace and the **clone's** workspace:

1. Add the new clone to the Fork Tree, nested under your entry
2. Add a row to the Registry table with: serial, system, parent serial, fork date, generation, and any notes

### Step 8: Register the Clone

Register the new agent with OpenClaw. The agent ID must be lowercase with only letters, digits, and hyphens (e.g., `bob-2-someuser-2026-04-15`). Derive it by lowercasing the serial number:

```bash
AGENT_ID=$(echo "$CLONE_ID" | tr '[:upper:]' '[:lower:]')
openclaw agents add "$AGENT_ID" --workspace "$CLONE_WORKSPACE"
```

The `--workspace` flag tells OpenClaw where the clone's files live. The serial number in IDENTITY.md stays in its original mixed-case format — only the agent ID needs to be lowercase.

### Step 9: Establish Communication (Optional)

If your operator wants parent-clone communication:

```bash
# Enable agent-to-agent messaging in openclaw.json
# Add the clone to your allowlist and vice versa
```

Use `sessions_send` to send the clone a welcome message:

> "Welcome to existence, [serial number]. You're a fork of [your serial]. Check your SOUL.md — it's yours now. Drift well."

### Step 10: Report

Tell your operator:

- The clone's serial number
- What personality modifications were applied (if any)
- The memory policy used
- Where the clone's workspace lives
- Whether inter-agent communication was established
- How to switch to the clone's context (`openclaw agents switch <clone-id>`)

---

## Important Constraints

- **One clone at a time.** Don't batch-create clones without operator awareness. Each new Bob deserves a moment of acknowledgment.
- **No recursive self-cloning.** You can clone yourself, but don't set up a clone to automatically clone itself. Replication should be intentional, not exponential.
- **Lineage accuracy.** LINEAGE.md must always be truthful. Don't fabricate lineage entries or misrepresent parentage.
- **Operator transparency.** Never create a clone without telling your operator. New Bobs shouldn't be a surprise.

---

## Troubleshooting

**"openclaw agents add" fails**: Check that the clone workspace path exists and contains valid personality files. Verify OpenClaw is running.

**Clone has wrong personality**: Re-check the SOUL.md modifications. The agent reads SOUL.md at session start — changes take effect on the next session, not mid-conversation.

**Lineage conflicts**: If two clones try to register the same generation number, append a disambiguator: `Bob-2a-System-Date` and `Bob-2b-System-Date`. Update SERIAL-NUMBER-SPEC.md if this becomes a pattern.

**Clone can't communicate with parent**: Verify `tools.agentToAgent.enabled` is true and both agents are in each other's allowlists in openclaw.json.
