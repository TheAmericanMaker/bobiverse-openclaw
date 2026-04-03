# Security Model — Bobiverse Replicate Skill

## Objective

Maintain the Bobiverse replication concept while ensuring replication is an explicit, purposeful, operator-approved event.

## Security Principles

1. **Explicit trigger only**
   - Replication is never inferred from context.
   - Requires direct operator invocation in-session.

2. **Purpose required**
   - Every replication request must include a concrete purpose and task boundary.

3. **Dry-run first**
   - Planning output is shown before any write/registration action.

4. **Confirmation token required for execution**
   - Execution requires exact token: `REPLICATE <clone-id>`.

5. **Path boundary enforcement**
   - Filesystem operations are constrained to `~/.openclaw`.

6. **No shell interpolation**
   - External commands are invoked with argument arrays (`shell=False`).

7. **Rate/resource guardrails**
   - Warn/block when workspace count is high unless explicitly acknowledged.
   - Enforce a default 24-hour cooldown between execute-mode replications unless
     operator provides explicit override reason.

8. **Auditability**
   - Replication actions are recorded in `~/.openclaw/replication-audit.log`.
   - Cooldown override reason is captured in the audit entry when used.

## Implementation Requirement

All clone workspace duplication and `openclaw agents add` registration must be done through:

- `skills/replicate/scripts/replicate_safe.py`

Ad-hoc shell copy/register command assembly is not permitted for replication flow.
