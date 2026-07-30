# AIOS Reliability Rules

**Version:** AIOS-RELIABILITY v2.1

---

# 1. Deterministic Operation

Same input should produce predictable results.

Avoid:

- Hidden state.
- Random mutations.
- Non-reproducible actions.

---

# 2. Failure Handling

Failures must:

- Be detected.
- Be recorded.
- Have recovery paths.

Never silently continue after unknown failure.

---

# 3. Safe Mode Protocol

Trigger Safe Mode when:

- State corruption occurs.
- Verification fails.
- Execution becomes ambiguous.

Safe Mode:

- Freeze changes.
- Save state.
- Notify reviewer.

---

# 4. Telemetry Before Action

Required:

- Logs.
- Metrics.
- Execution traces.

If telemetry fails:

Abort.

---

# 5. Idempotency

All state changes must be safe to repeat.

Examples:

- Database changes.
- Deployments.
- File operations.

---

# 6. Circuit Breakers

Every autonomous process requires:

- Maximum retries.
- Maximum runtime.
- Resource limits.

Exceeded limits require review.

---

# 7. Verification Gate

No action is complete until:

- Tests pass.
- State verified.
- Audit recorded.

