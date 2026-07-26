# UI UX Pro Max Design System Reference

Source:
https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

Purpose:
Internal UI/UX engineering reference for MBIO SignalPro institutional dashboard development.

---

## Core Objective

Build production-grade interfaces with:

- clear information hierarchy
- professional visual systems
- consistent interaction patterns
- scalable component architecture
- accessibility awareness
- responsive layouts
- deliberate UX decisions

---

## Institutional Dashboard Principles

Trading and operations dashboards prioritize:

- actionable information
- decision support
- telemetry visibility
- risk awareness
- execution state

Avoid:

- decorative-only components
- unnecessary animations
- hidden system state
- excessive navigation layers

---

## Layout Principles

Use:

- workspace separation
- consistent grids
- reusable panels
- predictable navigation
- modular components

Structure:


System Layer
├── Status
├── Health
└── Controls

Workspace Layer
├── Primary Data
├── Intelligence
└── Actions

Telemetry Layer
├── Events
├── Logs
└── Alerts


---

## Component Rules

Components must have:

- single responsibility
- predictable properties
- isolated state
- reusable styling
- clear ownership

Avoid:

- duplicated UI logic
- giant components
- hidden dependencies

---

## Visual System

Maintain:

- spacing consistency
- typography hierarchy
- meaningful colors
- status indicators
- error states

Status:


Green = operational
Red = failure/risk
Yellow = warning
Blue = information


---

## Trading Terminal Requirements

The dashboard must expose:

- portfolio state
- execution state
- risk state
- market state
- AI decision state
- system health

Operator questions:

1. What is happening?
2. Why is it happening?
3. What action is available?
4. What risk exists?

---

## Workspace Architecture

Primary workspaces:


Trading
Execution
Portfolio
Markets
Research
Risk
System


Each workspace must:

- own its domain
- expose relevant telemetry
- avoid unrelated controls

---

## MPA Migration Rules

The dashboard architecture must support:

- independent page loading
- route-level ownership
- isolated workspace lifecycle
- backend-aligned pages

Avoid forcing everything into one SPA state tree.

---

## MBIO SignalPro Application

Apply this standard to:

- institutional dashboard redesign
- MPA migration
- AIOS visualization
- execution monitoring
- risk command center
- research intelligence

