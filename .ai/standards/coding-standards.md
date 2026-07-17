# Code Quality Standards

- No fix scripts in repo root (`fix_*.py`, `deploy_*.py`, `god_mode_bypass.py` etc.).
- No backup directories committed (`backup_20260617/` etc.).
- No `.env` in git history.
- No duplicate function definitions in the same file.
- Every new module must have at minimum: error handling, logging, and a syntax check.
- `asyncio.Lock()` required on all `OPEN_POSITIONS` writes.
