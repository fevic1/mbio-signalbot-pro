# Architectural Decisions Log

### Position sizing framework
**Decision:** Use the Kelly Criterion as the sizing framework. The account is treated primarily as a strategy validation tool, not an income source.
**Why:** Mathematically grounded, appropriate for a small account where survival matters more than maximizing short-term growth.

### HLExecutor rate-limit fix pattern
**Decision:** Fixed via a TTL guard on `core/hip4_metadata.py` (max 1 refresh per 5 minutes), not a global singleton wrapper.
**Why:** Multiple call sites were constructing fresh `HLExecutor` instances, causing 429 storms.

### Dashboard rebuild: from scratch, not a patch
**Decision:** Settled — full rebuild, not incremental patching of `frontend-v2-dist` or `frontend/`.
**Why:** Existing dashboard is monitoring-oriented (read-only stat tiles); requirement is a workflow-oriented dashboard where every state panel has an inline action attached.

### Third-party audit reports require independent verification
**Decision:** Any external audit report claims must be independently verified against live `docker compose logs` and `grep` output before being recorded in `.ai/memory/`.
