# Rate Limiting Discipline

- Never suggest code that makes unbounded API calls.
- Every HL/Bybit API call must have: timeout, retry backoff, rate limit guard.
- HLExecutor must be a true singleton — never re-initialize per call.
- HIP-4 metadata refresh maximum once per 5 minutes, never on every init.
