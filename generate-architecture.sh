#!/usr/bin/env bash
set -Eeuo pipefail

BASE=".aios/architecture"
mkdir -p "$BASE"

create() {
FILE="$BASE/$1"

cat > "$FILE" <<EOF
# ${2}

## Purpose

Describe the responsibility of this subsystem.

## Responsibilities

-

## Inputs

-

## Outputs

-

## Dependencies

-

## Failure Modes

-

## Monitoring

-

## Performance Targets

-

## Security

-

## AI Rules

- Never violate subsystem boundaries.
- Never duplicate business logic.
- Update this document if architecture changes.

EOF
}

create system-overview.md "System Overview"
create backend.md "Backend Architecture"
create frontend.md "Frontend Architecture"
create execution-engine.md "Execution Engine"
create risk-engine.md "Risk Engine"
create strategy-engine.md "Strategy Engine"
create portfolio-engine.md "Portfolio Engine"
create market-data.md "Market Data"
create event-bus.md "Event Bus"
create database.md "Database"
create deployment.md "Deployment"
create security.md "Security"

echo "Architecture generated."
