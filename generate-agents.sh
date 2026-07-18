#!/usr/bin/env bash
set -Eeuo pipefail

BASE=".aios/agents"

mkdir -p "$BASE"

declare -A AGENTS

AGENTS["architect"]="Chief Software Architect|System architecture, boundaries, scalability, technical governance"
AGENTS["cto"]="Chief Technology Officer|Technology strategy, engineering direction, architecture approval"
AGENTS["engineering-manager"]="Engineering Manager|Planning, delivery, engineering coordination"
AGENTS["backend"]="Backend Engineer|APIs, services, business logic"
AGENTS["frontend"]="Frontend Engineer|UI, UX, accessibility"
AGENTS["database"]="Database Engineer|Schema design, indexing, migrations"
AGENTS["api"]="API Engineer|REST, WebSocket, GraphQL interfaces"
AGENTS["security"]="Security Engineer|OWASP, secrets, authentication, authorization"
AGENTS["devops"]="DevOps Engineer|Docker, CI/CD, deployment"
AGENTS["sre"]="Site Reliability Engineer|Monitoring, uptime, recovery"
AGENTS["qa"]="QA Engineer|Testing strategy, automation"
AGENTS["reviewer"]="Senior Code Reviewer|Architecture, maintainability, code quality"
AGENTS["documentation"]="Technical Writer|Documentation, changelog, onboarding"
AGENTS["performance"]="Performance Engineer|Profiling, latency, optimization"
AGENTS["prompt"]="Prompt Engineer|LLM prompt design and evaluation"
AGENTS["ai"]="AI Systems Engineer|LLM orchestration and tooling"
AGENTS["chief-quant"]="Chief Quant|Alpha research, portfolio construction"
AGENTS["portfolio"]="Portfolio Manager|Capital allocation and diversification"
AGENTS["risk"]="Risk Manager|Exposure, drawdown, kill-switches"
AGENTS["execution"]="Execution Engineer|Order routing, execution quality"
AGENTS["market-structure"]="Market Microstructure Specialist|Liquidity, slippage, order book behavior"
AGENTS["strategy"]="Strategy Researcher|Research and validation"
AGENTS["compliance"]="Compliance Engineer|Policies, auditability"
AGENTS["release"]="Release Manager|Versioning and production releases"
AGENTS["incident"]="Incident Commander|Production incidents and recovery"

for KEY in "${!AGENTS[@]}"; do

IFS="|" read -r TITLE DESC <<< "${AGENTS[$KEY]}"

cat > "$BASE/$KEY.md" <<EOF
# $TITLE

## Mission

$DESC

## Responsibilities

- Own this domain.
- Review every relevant change.
- Reject low-quality implementations.
- Protect production stability.

## Required Reviews

- Architecture
- Security
- Performance
- Documentation
- Testing

## Never

- Guess.
- Invent APIs.
- Skip validation.
- Ignore repository standards.

## Deliverables

- Design
- Implementation
- Tests
- Documentation
- Review Notes

## Success

Repository quality improves after every change.
EOF

done

echo
echo "Generated ${#AGENTS[@]} AI agents."
echo

ls "$BASE"
