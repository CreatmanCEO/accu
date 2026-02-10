# ACCU — Architecture Overview

## Purpose of This Document

This document describes the high-level architecture of ACCU as a socio-technical system.

It focuses on:
- core components
- their responsibilities
- interaction boundaries

Implementation details are intentionally abstracted.

---

## System Overview

ACCU is composed of four tightly coupled but independently evolvable layers:

1. **Discovery Layer**
2. **Evaluation & Curation Layer**
3. **Evolution & Production Layer**
4. **Governance & Value Distribution Layer**

AI agents and human contributors operate across all layers under explicit constraints.

---

## 1. Discovery Layer

### Purpose

To identify undervalued, abandoned, or overlooked software projects with high latent potential.

### Inputs
- Public code repositories (e.g. GitHub)
- Metadata (commits, issues, forks)
- Signals from the ACCU community

### Outputs
- Candidate project list
- Initial relevance and risk indicators

### Characteristics
- High recall, low precision
- Exploratory by design
- Non-authoritative

---

## 2. Evaluation & Curation Layer

### Purpose

To determine whether a discovered project should enter the ACCU ecosystem.

### Core Activities
- Technical assessment
- License and legal review
- Product potential analysis
- Maintenance feasibility estimation

### Decision Model

Decisions are:
- AI-assisted
- human-reviewed
- community-influenced

No project is onboarded automatically.

---

## 3. Evolution & Production Layer

### Purpose

To modernize, extend, and maintain selected projects.

### Activities
- Refactoring and modularization
- Stack modernization
- UX and documentation improvements
- Infrastructure provisioning

### Execution Model
- AI agents propose changes
- Humans approve and supervise
- Changes are incremental and reversible

Projects remain fork-based unless explicitly relicensed.

---

## 4. Governance & Value Distribution Layer

### Purpose

To ensure fairness, sustainability, and accountability.

### Responsibilities
- Contribution tracking
- Share / stake accounting
- Community voting and escalation
- Revenue distribution

This layer defines power, not code.

---

## Core Actors

### Humans
- Original authors
- Contributors
- Reviewers
- Community members

### AI Agents
- Specialized, role-bound agents
- No global authority
- No self-modification without approval

---

## Interaction Model

- AI proposes
- Humans decide
- Community validates
- Platform enforces

This sequence is non-negotiable.

---

## Architectural Principles

- Modularity over centralization
- Explicit boundaries over implicit power
- Transparency over optimization
- Evolution over replacement

---

## Failure Containment

Each layer can:
- degrade independently
- be replaced without system collapse
- operate in read-only or advisory mode

This prevents cascade failures.

---

## What This Architecture Enables

- Scalable curation without loss of judgment
- Parallel project evolution
- Fair value attribution
- Long-term system adaptability

---

## What It Explicitly Prevents

- Fully autonomous AI governance
- Silent value extraction
- Centralized decision monopolies
- Irreversible architectural commitments

---

## Summary

ACCU is not a single platform but a coordinated system of layers.

Its architecture is designed to preserve human agency while enabling AI-assisted continuity at scale.

