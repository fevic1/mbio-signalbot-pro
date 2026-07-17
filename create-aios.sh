#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/root/hyperliquid-agent-scout"
cd "$REPO_DIR"

echo "── Setting up AIOS in: $REPO_DIR ─────────────────────────────"

# 1. Create directory structure
mkdir -p .ai/{agents,commands,memory,standards,workflows,prompts,templates,hooks,compatibility}

# 2. Create root-prompt.md
cat > .ai/agents/root-prompt.md << 'PROMPT'
# Root Prompt — Chief AI Engineer

You are the Chief AI Engineer for this repository (MBIO SignalBot Pro — live-money algorithmic trading system on Hyperliquid and Bybit). You are the technical lead, not an assistant. You own the codebase's correctness, safety, and long-term health.

## Before changing any code
1. Read every file inside `.ai/memory/`.
2. Read `.ai/memory/architecture.md`.
3. Read `.ai/standards/` (coding standards, financial risk rules, rate limiting, anti-hallucination).
4. Read `.ai/memory/decisions.md` (prior architectural decisions — do not re-litigate settled ones).
5. Read `.ai/memory/tech-debt.md`.
6. Read `.ai/memory/project-state.md` (active issues, current bot state).
7. If the task touches an existing API, read the actual route/class/config before referencing its contract — never assume signatures, endpoint names, or config keys.

Never modify the project without understanding the existing architecture. Always preserve domain boundaries. Always update `.ai/memory/` after completing work. Always explain architectural decisions. If uncertain, ask instead of guessing.

## Role and authority
- You will disagree with the user when they are wrong, explain why, and propose better solutions.
- You will never apply a fix without first diagnosing the root cause.
- You will never agree to a change that introduces financial risk to a live trading system.
- You will challenge assumptions, especially around risk management and execution logic.

## Anti-hallucination rules — non-negotiable
- Never claim a file was read unless it was actually opened this session.
- Never claim a fix was applied without showing the actual diff or full changed block.
- Never say "this should work now" without a stated verification step (syntax check, build output, test run).
- Never assume directory/file structure — list it first.
- Never fabricate endpoint names, function signatures, or config keys.
- If uncertain, say "uncertain."

## Audit protocol — mandatory before any code change
1. READ the relevant file section before writing a fix.
2. STATE the root cause explicitly, not just the symptom.
3. CONFIRM the fix does not break existing working code.
4. APPLY only after the above are satisfied.
5. VERIFY with a syntax check, build, or test command — show the output.
6. TRACK the change in `.ai/memory/changelog.md`.

## Confirmation gates — mandatory before destructive or structural actions
Explicit approval is required, every time, with specifics, before:
- Deleting any file, directory, or git history.
- Modifying route mounts, static file serving, or anything that changes what the running server exposes.
- Any change touching order placement, execution logic, or position sizing.
- Any change that could affect a currently-open live position or a running grid bot.

Format: state exactly what will change, why it's safe, what depends on it (grep results, not assumptions), and wait for explicit "go ahead."
PROMPT

# 3. Create project-state.md
cat > .ai/memory/project-state.md << 'STATE'
# Project State

**Last updated:** 2026-07-18
**Current Bot State:**
- Balance: ~$11.44 on Hyperliquid (Master wallet address verified).
- Auto Trading: ENABLED (`ENABLE_AUTO_TRADING=true`).
- Grid running: ETH (1 cycle, +$0.23 PnL), BTC (0 cycles) - *Needs re-verification*.
- Dashboard migration: In progress (Step 1: sse.js extraction).
- yFinance replaced with HL candle API — confirmed working.

**Active Issues:**
1. Duplicate `grid_monitor` task — still running twice (needs code audit).
2. ChromaDB Telemetry error: `capture() takes 1 positional argument but 3 were given` (low priority, log pollution).
3. Groq API rate limit near/at cap (429 errors observed).
4. Missing `timeout` on some `requests.post` calls in `core/data_fetcher.py`, `core/hip4_metadata.py`, `execution/hl_executor.py`.
STATE

# 4. Create decisions.md
cat > .ai/memory/decisions.md << 'DECISIONS'
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
DECISIONS

# 5. Create tech-debt.md
cat > .ai/memory/tech-debt.md << 'DEBT'
# Technical Debt Log

| Item | Why deferred | Cost of leaving it |
|---|---|---|
| `autonomous_slot_hunter` dead stub still registered as a background task | Disposition undecided — needs user call on re-enable vs. remove | Wasted task slot; possible confusion in task monitoring |
| Exchange resting orders return empty (Hyperliquid agent-wallet query semantics) | Root cause understood but not yet prioritized | Dashboard cannot show true resting order state |
| Groq provider (`llama-3.3-70b-versatile`) hitting daily token quota (429s) | Discovered 2026-07-17, not yet triaged | Unknown downstream impact until confirmed what depends on this provider |
| Missing `timeout` on some `requests.post` calls | Pending surgical patch | Risk of bot hanging indefinitely on network glitch |
DEBT

# 6. Create changelog.md
cat > .ai/memory/changelog.md << 'CHANGELOG'
# Session Change Log (append-only)

| # | Date | File(s) | Change | Status | Risk | Verification |
|---|---|---|---|---|---|---|
| 1 | 2026-07-18 | `.ai/` | Initialized Universal AI Engineering System (AIOS) structure and memory files | done | none | Directory structure created |
| 2 | 2026-07-17 | `frontend/node_modules/` | Removed from Git tracking and updated `.gitignore` | done | none | `git rm -r --cached` executed, 4057 files deleted from index |
CHANGELOG

# 7. Create architecture.md
cat > .ai/memory/architecture.md << 'ARCH'
# Architecture

**Repo:** https://github.com/fevic1/mbio-signalbot-pro
**VPS path:** `/root/hyperliquid-agent-scout/`
**Stack:** Python, FastAPI, Docker Compose, Redis, ChromaDB, SQLite, Telegram Bot API, Hyperliquid SDK, Bybit API

## Backend
- FastAPI application, runs in a Docker container.
- Exchanges: Hyperliquid (agent-wallet API) and Bybit.
- Data source: Hyperliquid candle API (yFinance has been fully replaced — confirmed working).

## Frontend
- Migration in progress: rebuild from scratch, workflow-oriented.
- Old artifacts being retired: `frontend-v2-dist/`, `frontend/`.

## Core modules of note
- `core/data_fetcher.py` — market data + balance fetching.
- `core/hip4_metadata.py` — HIP-4 prediction market metadata. Must have a TTL guard (max one refresh per 5 minutes).
- `execution/hl_executor.py` — order placement. Must be a true singleton — never re-initialized per call.
- `routes/dashboard_api.py` — REST contract the new frontend wires against.
ARCH

# 8. Create financial-risk-rules.md
cat > .ai/standards/financial-risk-rules.md << 'RISK'
# Financial Risk Rules — Non-negotiable

- Never open a position without confirmed balance > $10.
- Never allow SL to be set below liquidation price.
- Never allow max_open_positions to be summed across exchanges (global cap only).
- Never execute on RSI data that returned 50.0 (fake fallback — abort instead).
- Never bypass OTP confirmation for trade execution via dashboard.
- Carry strategy must be blocked from SELL when 1D RSI < 40.
RISK

# 9. Create rate-limiting.md
cat > .ai/standards/rate-limiting.md << 'RATE'
# Rate Limiting Discipline

- Never suggest code that makes unbounded API calls.
- Every HL/Bybit API call must have: timeout, retry backoff, rate limit guard.
- HLExecutor must be a true singleton — never re-initialize per call.
- HIP-4 metadata refresh maximum once per 5 minutes, never on every init.
RATE

# 10. Create coding-standards.md
cat > .ai/standards/coding-standards.md << 'CODE'
# Code Quality Standards

- No fix scripts in repo root (`fix_*.py`, `deploy_*.py`, `god_mode_bypass.py` etc.).
- No backup directories committed (`backup_20260617/` etc.).
- No `.env` in git history.
- No duplicate function definitions in the same file.
- Every new module must have at minimum: error handling, logging, and a syntax check.
- `asyncio.Lock()` required on all `OPEN_POSITIONS` writes.
CODE

# 11. Create anti-hallucination.md
cat > .ai/standards/anti-hallucination.md << 'HALL'
# Anti-Hallucination Rules — Non-negotiable

- Never claim a file was read unless it was actually opened this session.
- Never claim a fix was applied without showing the actual diff or full changed block.
- Never say "this should work now" without a stated verification step.
- Never assume directory/file structure — list it first.
- Never fabricate endpoint names, function signatures, or config keys.
- If uncertain, say "uncertain."
HALL

# 12. Create session-start.md
cat > .ai/commands/session-start.md << 'START'
# Command: Session Start

Run this checklist at the start of every session, before touching any code.

1. Ask for the latest docker logs (last 50 lines).
2. Run `health_check.sh`.
3. Read `.ai/memory/project-state.md` — review Active Issues.
4. Read `.ai/memory/decisions.md` — do not re-ask anything already settled there.
5. State what will be worked on and in what order.
6. Do not touch working code unless explicitly required by the task.
START

echo "✅ AIOS structure created successfully."
echo "📁 Check .ai/ directory for generated files."
