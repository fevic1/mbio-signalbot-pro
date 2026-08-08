# MBIO SignalBot Pro

Institutional-grade AI-assisted cryptocurrency trading platform for Hyperliquid and Bybit, with modular market intelligence, strategy selection, risk controls, execution, monitoring, APIs, and operator dashboards.

## System Overview

MBIO SignalBot Pro is organized as a production trading system with separate layers for AI analysis, market research, strategy logic, risk management, execution, state, APIs, frontend applications, monitoring, and operational tooling.

## Repository Tree

```text
mbio-signalbot-pro/
├── ai/                         # AI providers, analysis, selection, and intelligence
├── api/                        # API layer and service interfaces
├── archive/                    # Archived MBIO material
├── certbot/                    # TLS / certificate support
├── config/                     # Runtime and strategy configuration
├── core/                       # Core trading-system components
├── dashboard-v3/               # Primary dashboard application
├── db/                         # Database assets and runtime data
├── docs/                       # Project documentation
├── execution/                  # Order execution and exchange integration
├── frontend/                   # Frontend application
├── frontend_pro/               # Pro frontend application
├── handlers/                   # Application and event handlers
├── monitoring/                 # Health, telemetry, and operational monitoring
├── nginx/                      # Nginx configuration
├── research/                   # Market and project research
├── risk/                       # Risk-management components
├── routes/                     # Backend/API routes
├── scout_helpers/              # Scout and universe-selection helpers
├── scripts/                    # MBIO operational scripts
├── src/                        # Shared source modules
├── state/                      # Runtime state and persistence
├── static_frontend/            # Static frontend assets
├── strategies/                 # Trading strategies
├── telegram_bot/               # Telegram operator interface
├── templates/                  # Server-rendered templates
├── tests/                      # Automated test suites
├── utils/                      # Shared utilities
│
├── main.py                     # MBIO application entry point
├── config_loader.py             # Configuration loading
├── db.py                       # Database interface
├── router.py                   # Application routing
├── registry.py                 # Component/provider registry
├── provider_types.py            # Provider type definitions
├── cerebras_provider.py         # Cerebras provider integration
├── groq_provider.py             # Groq provider integration
├── Dockerfile                  # MBIO container image
├── docker-compose.yml           # MBIO production Docker stack
├── docker-compose.nginx.yml     # Nginx compose configuration
├── nginx.conf                   # Nginx configuration
├── nginx-spa.conf               # SPA Nginx configuration
├── requirements.txt              # MBIO runtime dependencies
├── pyproject.toml                # Python project configuration
├── pytest.ini                    # Pytest configuration
├── .env.example                  # Environment variable template
├── .dockerignore                 # Docker build exclusions
├── API_REFERENCE.md              # API reference
├── ARCHITECTURE.md               # MBIO architecture documentation
├── SECURITY_AUDIT_REPORT.md      # Security audit documentation
└── README.md                     # Project documentation
```

## Docker Runtime

The MBIO production stack is intentionally limited to MBIO services:

```text
Docker
├── mbio-bot
├── redis
├── nginx
└── frontend-builder
```

AIOS is not part of the MBIO Docker service graph.

## Core Capabilities

- **AI-assisted market intelligence** for market conditions, project/scout filtering, and trading analysis.
- **Strategy engine** for structured signal generation and strategy execution.
- **Risk management** with controlled exposure and execution safeguards.
- **Exchange execution** for Hyperliquid and Bybit workflows.
- **Persistent state** for runtime recovery and operational continuity.
- **Monitoring and health checks** for production operation.
- **Telegram operations** for alerts and operator interaction.
- **API and routing layer** for dashboard and system services.
- **Dashboard applications** for monitoring and control.
- **Research tooling** for market and project intelligence.
- **Automated tests** covering core trading and system behavior.

## Configuration

Runtime configuration is managed through `config/` and environment variables. Use `.env.example` as the reference for required environment variables.

## Running with Docker

```bash
docker compose up -d --build
```

The active Compose stack is defined by `docker-compose.yml`.

## Running Without Docker

```bash
pip install -r requirements.txt
python main.py
```

## Documentation

- `ARCHITECTURE.md` - system architecture
- `API_REFERENCE.md` - API reference
- `SECURITY_AUDIT_REPORT.md` - security audit
- `docs/` - supporting documentation

## Separation Boundary

MBIO SignalBot Pro and AIOS are maintained as separate concerns. This README documents the MBIO SignalBot Pro application and its runtime architecture. AIOS code is intentionally not included in the MBIO runtime tree or Docker service graph.
