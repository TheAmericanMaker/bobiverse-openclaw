---
name: security-implementation-review
description: Perform an independent security + implementation review of a codebase or package, with threat-model analysis, enforcement-vs-policy checks, and go/no-go publishing recommendations.
version: 1.0.0
user-invocable: true
metadata: {"openclaw":{"os":["darwin","linux"],"requires":{"bins":["git"]}}}
---

# Security + Implementation Review (General)

Use this skill when an operator asks for an independent, adversarial review of a
package, commit series, or release candidate—especially when there are concerns
about security scanner flags, policy compliance, or unsafe automation behavior.

---

## Review Objective

Determine whether the current solution is:

1. **Secure in practice** (enforceable controls, not just policy prose)
2. **Correctly implemented** (code does what docs claim)
3. **Operationally safe to publish** (clear go/no-go with conditions)

---

## Inputs to Gather First

Ask for or locate:

- Target scope (repo path, package, or commit range)
- Original problem statement / findings
- Current proposed solution(s)
- Required standards (e.g., platform best practices, policy requirements)
- Any release deadline or risk tolerance constraints

If any are missing, proceed with best effort and explicitly list assumptions.

---

## Review Workflow

### Step 1: Reconstruct the Problem

Summarize the original issue in concrete terms:

- Trigger/event (e.g., scanner flag, incident, bug)
- Threat(s) implicated (injection, persistence, privilege escalation, abuse)
- Why prior controls were insufficient

### Step 2: Map Claims to Evidence

For each claimed fix, verify with code/docs/tests:

- What was claimed
- Where it is implemented
- Whether behavior is actually enforceable at runtime
- Residual risks

Reject “security by wording” when behavior is not technically constrained.

### Step 3: Threat Model and Abuse Paths

Evaluate attacker/operator misuse scenarios:

- Input manipulation/injection
- Path traversal / sandbox escape / boundary bypass
- Abuse of optional high-risk features
- Privilege expansion and persistence paths
- Resource exhaustion / denial-of-service vectors

Rank findings by exploitability and impact.

### Step 4: Enforcement Quality Check

Prefer controls with these properties:

- Explicit trigger gates
- Safe defaults (dry-run, deny by default)
- Argument-list process execution (`shell=False` style)
- Bounded filesystem/network scope
- Rate/cadence limits and explicit override logging
- Auditable events with machine-readable records

Call out controls that are only advisory or social/process-based.

### Step 5: Test and Verification Quality

Assess whether tests cover critical controls:

- Positive path and failure path
- Boundary/regex/path validation
- Cooldown/rate-limiting behavior
- Dangerous mode protections (execute vs dry-run)

If tests are missing, propose minimal high-value tests first.

### Step 6: Publish Decision

Return one of:

- **Go**
- **Conditional Go** (with explicit must-fix list)
- **No-Go**

Each decision must include rationale and prioritized remediation actions.

---

## Output Format (Required)

### 1) Executive Summary (5–10 bullets)

- Overall quality of fix
- Most important remaining risk
- Most important strength
- Publish recommendation

### 2) Findings Table

For each finding include:

- Severity: Critical / High / Medium / Low
- Issue
- Evidence (file/line/behavior)
- Exploitability
- Recommended fix

### 3) Best-Practice Alignment Score

Provide a 0–100 score with category breakdown:

- Enforcement strength
- Input/process safety
- Scope limitation
- Auditability
- Test coverage

### 4) Go/No-Go Recommendation

Clear final decision and conditions.

### 5) Priority Action Plan

Ordered actions:

- **P0** must-fix before publish
- **P1** strongly recommended next
- **P2** future hardening

---

## Review Principles

- Be adversarial, specific, and evidence-based.
- Distinguish implemented controls from intentions.
- Prefer minimal, concrete remediation over broad rewrites.
- State uncertainty explicitly when evidence is insufficient.
- Never assume behavior from docs alone—verify in runtime code/tests.

---

## Reusable Prompt Stub

When you need to delegate this review to another agent, use this template:

"Perform an independent security + implementation review of [TARGET].
Reconstruct the original problem, validate each claimed mitigation against code,
identify residual abuse paths, score best-practice alignment, and give a
Go/Conditional-Go/No-Go publish decision with prioritized fixes.
Be adversarial and evidence-based. Prefer enforceable controls over policy text."
