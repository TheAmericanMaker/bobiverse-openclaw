# Security Review Summary

## Executive Summary

- Verdict: source-level hardening is materially better than `c28d8ef`, but the package is still not publish-ready as a "hardened" replication skill.
- The shell-injection concern is largely fixed in the enforced path: `replicate_safe.py` uses argument-list subprocess execution with `shell=False`.
- The biggest practical flaw is deployment: the recommended repo install path copies only `SKILL.md`, not the safe runner, so common installs can lose the only enforceable control.
- Path-boundary enforcement is incomplete: the runner accepts `~/.openclaw` itself as the parent, and `copytree()` is called in a way that can follow symlink targets.
- Resource guardrails exist, but they are accident-prevention friction, not strong abuse controls; failed executions can still leave orphaned copies and avoid cooldown advancement.
- "Explicit trigger", "dry-run first", and "operator approval" are still mostly policy semantics, not authenticated runtime state.
- Cross-agent communication remains prose-hardened, not runtime-hardened, and a bundled architecture example still shows broad visibility (`"all"`), which cuts against least privilege.
- Marketplace/heuristic risk is still elevated because bundle-facing text still says "self-cloning" / "new autonomous agents".
- Tests are not strong evidence of safety; they only exercise helpers and miss the dangerous branches.
- Good enough now: shell-safety direction. Not good enough yet: deployment integrity, boundary completeness, transactional behavior, and publish-facing consistency.

## Findings

| Severity | Issue | Evidence | Exploitability | Fix |
|---|---|---|---|---|
| High | Common repo install path omits the safe runner/support files | `README.md#L77`, `skills/replicate/README.md#L69`, `skills/replicate/SKILL.md#L127` | Users following the recommended git/manual install get only `SKILL.md`; the enforced runner is absent, so the real deployment can fail or drift back to policy-only/manual behavior. | Copy the entire `skills/replicate/` tree, or make ClawHub install the only supported replication path. |
| High | Parent path is root-bounded, not workspace-bounded | `skills/replicate/scripts/replicate_safe.py#L55`, `skills/replicate/scripts/replicate_safe.py#L59` | The runner accepts `parent_workspace = ~/.openclaw`, which makes the clone path a child of the source tree; execute-mode can recurse or clone arbitrary non-workspace dirs under `~/.openclaw`. | Require workspace sentinel files and reject root/ancestor paths before planning. |
| High | Symlink traversal can escape the claimed `~/.openclaw` boundary | `skills/replicate/scripts/replicate_safe.py#L165` | `shutil.copytree()` is called with default `symlinks=False`; symlinks inside the workspace can cause external files to be copied into the clone. | Reject symlinks, or preserve only safe symlinks after per-entry realpath checks. |
| High | Failed registration leaves persistent copies and bypasses cooldown/audit | `skills/replicate/scripts/replicate_safe.py#L165`, `skills/replicate/scripts/replicate_safe.py#L173` | Copy happens before `openclaw agents add`; on failure, the clone directory remains, no audit entry is written, and cooldown never advances. | Stage into a temp dir, rollback on any failure, and log `started/failed/succeeded` attempts. |
| Medium | "Explicit trigger / operator approval / dry-run first" are not runtime-authenticated | `skills/replicate/scripts/replicate_safe.py#L107`, `skills/replicate/scripts/replicate_safe.py#L159`, `skills/replicate/SKILL.md#L67` | Any caller with exec can self-supply `--purpose`, `--confirm`, and `--execute`; there is no binding to an actual user approval event or prior dry-run state. | Use OpenClaw approval-gated execution or a dry-run-issued nonce/state file with TTL and one-time use. |
| Medium | Bundle docs/metadata still advertise risky behavior and broad comms | `skills/replicate/clawhub.json#L3`, `skills/replicate/README.md#L154`, `skills/replicate/ARCHITECTURE.md#L159` | "self-cloning", "new autonomous agents", and `sessions.visibility: "all"` undermine least-privilege messaging and are likely to keep heuristics warm because ClawHub exposes bundle files and metadata publicly. | Rewrite bundle-facing wording and remove the `"all"` visibility example; keep comms off by default. |
| Medium | Tests miss the dangerous branches | `skills/replicate/scripts/test_replicate_safe.py#L19` | Current tests only cover helpers; they do not exercise `run()`, direct execute, cooldown override, high-count gate, root-parent rejection, symlinks, rollback, or audit behavior. | Add run-level tests with mocks and workspace-local temp dirs. |
| Low | Load-time metadata under-declares runtime prerequisites | `skills/replicate/SKILL.md#L6` | `requires.bins` lists only `openclaw`, but the enforced path depends on `python3` or an executable script with a working interpreter. | Add `python3` to `metadata.openclaw.requires.bins` or ship a supported wrapper binary. |

## Best-Practices Alignment Score

**61/100**

This is clearly better than the policy-only state described in `docs/security-review-c28d8ef.md`: it adds a real runner, shell-safe subprocess use, and code-level cooldown/high-count checks. It is not best-practice complete because the common install path omits that runner, boundary enforcement is incomplete, execute-mode is non-transactional, and approval semantics are still advisory.

## Publish Recommendation

**No-Go**

If published now, the repo looks hardened in source, but the deployment story does not reliably preserve the hardening, and the runner does not fully enforce the claimed boundary/approval model.

Evidence still missing:

- A successful end-to-end `openclaw agents add` validation on a real macOS/Linux OpenClaw install
- A live ClawHub scanner result against the current package state

## Follow-Up Actions

1. Patch `skills/replicate/scripts/replicate_safe.py`: add strict workspace validation, reject `~/.openclaw` and ancestor paths, reject or safely preserve symlinks, and make execute-mode transactional with rollback plus attempt/failure audit entries.
2. Patch `README.md` Quick Start / Manual Workspace Bootstrap / Alternative sections, and the matching sections in `skills/replicate/README.md`: copy the entire `skills/replicate/` directory, not only `SKILL.md`, or explicitly bless ClawHub-only install for replication.
3. Patch `skills/replicate/SKILL.md` Step 3 and Safety/Permissions: replace the string token with a dry-run-issued nonce or real OpenClaw approval gate, and make "dry-run first" an enforced sequence, not prose.
4. Patch `ARCHITECTURE.md` and `skills/replicate/ARCHITECTURE.md`: update the flow to reflect the safe runner and remove the `sessions.visibility: "all"` example.
5. Patch `skills/replicate/clawhub.json`, `README.md`, and `skills/replicate/README.md`: tone down "self-cloning/autonomous agent" wording so metadata is truthful and less likely to trip heuristics.
6. Patch `skills/replicate/scripts/test_replicate_safe.py`: add run-level tests for root rejection, symlink rejection, cooldown/high-count, rollback on subprocess failure, audit success/failure, and a portable temp-dir strategy.
