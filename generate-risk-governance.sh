#!/usr/bin/env bash
set -Eeuo pipefail

BASE=".aios/governance"

mkdir -p "$BASE"

cat > "$BASE/risk-governance.md" <<'EOF'
# Institutional Risk Governance

## Objective

Capital preservation is the primary objective.

Profit is secondary.

## Risk Hierarchy

1. Prevent catastrophic loss
2. Preserve capital
3. Maintain liquidity
4. Generate consistent returns
5. Maximize returns

## Position Limits

Every order must validate:

- Maximum portfolio exposure
- Strategy allocation
- Symbol allocation
- Leverage limits
- Available margin

## Drawdown Rules

Trigger warning:

- 5%

Reduce risk:

- 10%

Disable new positions:

- 15%

Emergency stop:

- 20%

## Kill Switches

Immediately disable trading when:

- Exchange unavailable
- Order rejection spikes
- Latency exceeds threshold
- Price feed becomes unreliable
- Risk engine unavailable
- Position reconciliation fails

## Order Validation

Before every order:

- Symbol exists
- Market tradable
- Margin available
- Position size valid
- Stop loss defined
- Risk/reward acceptable
- Liquidity sufficient

Reject otherwise.

## Execution Requirements

Every execution records:

- Timestamp
- Exchange
- Strategy
- Signal
- Position Size
- Entry
- Stop
- Take Profit
- Slippage
- Fees
- Latency

## Production Rules

Never bypass:

- Risk Engine
- Position Limits
- Kill Switches
- Circuit Breakers

No exceptions.

EOF

echo "Risk governance generated."
