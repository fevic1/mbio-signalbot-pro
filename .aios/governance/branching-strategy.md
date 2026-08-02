# AIOS Branching Strategy

Status: Active

## Purpose

Define the official branching strategy for MBIO SignalBot Pro and AIOS.

## Responsibilities

### main

Purpose:
Production branch for MBIO SignalBot Pro.

Owns:

- Trading Engine
- Dashboard
- Exchange Integrations
- Risk Management
- Portfolio Management
- Production Releases

Rules:

- Always production ready.
- All CI checks must pass.
- No experimental development.

---

### aios-production-hardening

Purpose:
Primary AIOS engineering branch.

Owns:

- AIOS Runtime
- Agents
- Memory
- Context Engine
- Prompt Engine
- MCP
- Governance
- Learning
- Provider Routing
- AIOS Services

Rules:

- Canonical AIOS development branch.
- All AIOS feature branches originate here.
- Architecture Audit must pass.

---

### feature/*

Purpose:
Single-feature development.

Rules:

- Branch from aios-production-hardening.
- Merge into aios-production-hardening.
- Delete after merge.

---

### hotfix/*

Purpose:
Emergency production fixes.

Rules:

- Branch from main.
- Merge into main.
- Merge into aios-production-hardening if applicable.

## Policies

Merge Flow

feature/*
    ↓
aios-production-hardening
    ↓
main

Feature branches never merge directly into main.

## Required Validation

- MBIO SignalBot CI
- AIOS Architecture Audit
- Clean merge
- Zero failing required checks

## Audit Requirements

- Passing GitHub Actions
- Architecture compliance
- Reviewable history
- No unresolved ownership conflicts

---

## Pull Request Policy

### feature/* → aios-production-hardening

Required.

Conditions:

- AIOS Architecture Audit passes.
- MBIO SignalBot CI passes.
- Review completed.

---

### aios-production-hardening → main

Not required after every AIOS commit.

Open a Pull Request only when promoting a production-ready AIOS release into MBIO SignalBot Pro.

Requirements:

- Production ready.
- Required GitHub Actions passing.
- Architecture approved.
- Release approved.

---

### hotfix/* → main

Required unless emergency maintenance procedures apply.
