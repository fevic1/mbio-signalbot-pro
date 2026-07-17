# Technical Debt Log

| Item | Why deferred | Cost of leaving it |
|---|---|---|
| `autonomous_slot_hunter` dead stub still registered as a background task | Disposition undecided — needs user call on re-enable vs. remove | Wasted task slot; possible confusion in task monitoring |
| Exchange resting orders return empty (Hyperliquid agent-wallet query semantics) | Root cause understood but not yet prioritized | Dashboard cannot show true resting order state |
| Groq provider (`llama-3.3-70b-versatile`) hitting daily token quota (429s) | Discovered 2026-07-17, not yet triaged | Unknown downstream impact until confirmed what depends on this provider |
| Missing `timeout` on some `requests.post` calls | Pending surgical patch | Risk of bot hanging indefinitely on network glitch |
