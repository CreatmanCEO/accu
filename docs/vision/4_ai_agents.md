# ACCU — AI Agents Specification (High-Level)

## Purpose of This Document

This document defines the roles, boundaries, and governance constraints of AI agents operating within ACCU.

It intentionally avoids implementation details and focuses on responsibility allocation and safety.

---

## Foundational Principle

AI agents in ACCU are **tools with judgment support**, not autonomous decision-makers.

They:
- assist
- propose
- analyze

They do **not**:
- own outcomes
- override humans
- redefine system goals

---

## Agent Taxonomy

ACCU operates with multiple **specialized agents**, never a single general intelligence.

### 1. Repository Scout Agent

**Purpose:**
Identify potentially undervalued or abandoned repositories.

**Capabilities:**
- Metadata analysis
- Commit and activity pattern detection
- Signal aggregation (stars, forks, issues)

**Restrictions:**
- Cannot onboard projects
- Cannot contact authors
- Cannot prioritize based on popularity alone

---

### 2. Technical Analyst Agent

**Purpose:**
Assess code quality, architecture, and maintainability.

**Capabilities:**
- Static analysis
- Dependency risk assessment
- Architecture pattern recognition

**Restrictions:**
- Cannot refactor directly
- Cannot approve production changes

---

### 3. Product Re-evaluation Agent

**Purpose:**
Reframe projects from a product and user-value perspective.

**Capabilities:**
- Problem-solution mapping
- User persona inference
- Market adjacency analysis

**Restrictions:**
- Cannot define monetization unilaterally
- Cannot override community direction

---

### 4. Evolution Support Agent

**Purpose:**
Assist contributors during modernization and refactoring.

**Capabilities:**
- Code suggestions
- Documentation drafts
- Migration guidance

**Restrictions:**
- All changes require human approval
- No self-initiated commits

---

### 5. Governance Observer Agent

**Purpose:**
Monitor process integrity and rule adherence.

**Capabilities:**
- Contribution tracking
- Rule violation detection
- Transparency reporting

**Restrictions:**
- No enforcement authority
- Advisory-only role

---

## Shared Constraints (All Agents)

- No direct economic control
- No private communication outside platform rules
- No self-modification
- No cross-agent authority escalation

---

## Human Override

At any point:
- agents can be paused
- outputs can be discarded
- roles can be retired

Human authority is absolute.

---

## Safety by Design

Safety is achieved through:
- specialization
- redundancy
- explicit scope limits
- mandatory human checkpoints

---

## Summary

AI agents in ACCU are structured collaborators.

They expand human capacity without replacing human responsibility.

