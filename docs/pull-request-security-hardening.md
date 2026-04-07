# Pull Request: Security Hardening and Configuration Improvements

## Summary

This PR addresses security vulnerabilities and adds configurability to the `replicate_safe.py` script.

## Changes

### Security Fixes

1. **Symlink Path Escape Prevention (D4.1)** - HIGH Severity
   - Changed `shutil.copytree(symlinks=True)` to `symlinks=False`
   - Prevents malicious symlinks in source workspace from escaping the OpenClaw boundary
   - Location: `skills/replicate/scripts/replicate_safe.py:402`

2. **Agent Registration Verification (D2.1)** - HIGH Severity  
   - Added verification that agent appears in agent list after `openclaw agents add`
   - Prevents orphaned workspaces when CLI registration fails
   - Location: `skills/replicate/scripts/replicate_safe.py:409-413`

3. **Atomic Audit Logging (D3.2)** - MEDIUM Severity
   - Implemented atomic file writes using temp file + `os.replace()`
   - Prevents log corruption from concurrent writes
   - Location: `skills/replicate/scripts/replicate_safe.py:82-117`

### Configuration Improvements (D6.1-D6.5)

All thresholds are now configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_ROOT` | `~/.openclaw` | OpenClaw root directory |
| `PENDING_TTL_MINUTES` | `15` | Pending approval TTL in minutes |
| `MAX_WORKSPACES` | `10` | Maximum workspace count |
| `COOLDOWN_HOURS` | `24.0` | Hours between clones |
| `MIN_PURPOSE_LENGTH` | `12` | Minimum purpose length in characters |

Location: `skills/replicate/scripts/replicate_safe.py:32-39`

### Documentation Updates

- `SKILL.md`: Added Configuration section with environment variable table
- `ARCHITECTURE.md`: Added Security Implementation section documenting all security layers
- `SECURITY.md`: Added Configuration section

## Testing

- Existing tests in `test_replicate_safe.py` should continue to pass
- Manual testing recommended for:
  - Symlink rejection behavior
  - Environment variable configuration
  - Agent registration verification

## Breaking Changes

None. All changes are backward compatible with default values matching previous behavior.

## Related Issues

- Defect IDs: D4.1, D2.1, D1.1, D3.2, D6.1-D6.5

---

## For Commit

```
fix: harden replicate_safe.py against symlink attacks and add env config

- Change symlinks=True to symlinks=False to prevent path escape
- Add agent registration verification after CLI call
- Implement atomic audit log writes to prevent corruption
- Add environment variables for configuration (OPENCLAW_ROOT,
  PENDING_TTL_MINUTES, MAX_WORKSPACES, COOLDOWN_HOURS,
  MIN_PURPOSE_LENGTH)
- Update documentation with security and config sections
```
