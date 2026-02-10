# ACCU — AI-Curated Code Universe

## Quick Start for Claude Code

**What is this?** Ecosystem for reviving undervalued open-source projects through human-AI collaboration.

**Current Phase:** MVP Development — Phase 1 (Discovery Agent)

**Last Updated:** 2026-02-10

**VPS Status:** Deployed on `instance102973.waicore.network` port 8080

---

## Founder Context (IMPORTANT)

Read `docs/vision/0_original_dialog.md` for the full vision. Key points:

- The founder is **architect of digital life forms**, not a task executor
- Project must **support the founder**, not consume him
- **No solo heroism** — the system should work without burning out one person
- Community model with **fair value distribution**
- Original authors **always retain authorship and get revenue share**

---

## Project Status Dashboard

| Module | Status | Priority | Location |
|--------|--------|----------|----------|
| Discovery Agent | 🟡 Code Ready | P0 | `src/accu/agents/discovery/` |
| AI Providers | 🟡 Code Ready | P0 | `src/accu/providers/` |
| API Gateway | 🟡 In Progress | P0 | `src/accu/main.py` |
| Tech Critic Agent | 🟡 Code Ready | P1 | `src/accu/agents/critic/` |
| Product Re-evaluator | ⚪ Not Started | P2 | — |
| Narrative Agent | ⚪ Not Started | P2 | — |
| Infra Agent | ⚪ Not Started | P2 | — |
| Evolution Support | ⚪ Not Started | P2 | — |
| Governance System | 🟡 Docs Ready | P1 | `docs/governance/` |
| CP Tracking | 🟡 Spec Ready | P1 | `docs/governance/` |
| Web UI | ⚪ Not Started | P3 | — |

Status: ⚪ Not Started | 🟡 In Progress | 🟢 Complete | 🔴 Blocked

---

## Full Agent Taxonomy (6 Agents)

From the original vision dialog:

| Agent | Purpose | Status |
|-------|---------|--------|
| **Code Scout** (Discovery) | Find hidden gem repositories | 🟡 Code Ready |
| **Tech Critic** (Analyst) | Evaluate architecture & quality | 🟡 Code Ready |
| **Product Reframer** | Reposition for modern markets | ⚪ Planned |
| **Modernizer** | Update stack, refactor | ⚪ Planned |
| **Narrative Agent** | Rebrand, new README | ⚪ Planned |
| **Infra Agent** | Manage servers, deployments | ⚪ Planned |

All agents: **replaceable, sandboxed, human-supervised**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      ACCU Platform                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Web UI     │  │  API        │  │  CLI        │         │
│  │  (Future)   │  │  Gateway    │  │  Tools      │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         └────────────────┼────────────────┘                 │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Agent Orchestrator                      │   │
│  │         (Claude Code / Custom Logic)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│         │         │         │         │         │           │
│         ▼         ▼         ▼         ▼         ▼           │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│  │ Scout  │ │Analyst │ │Reframe │ │Modern- │ │ Infra  │    │
│  │        │ │        │ │        │ │  izer  │ │ Agent  │    │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘    │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              AI Provider Abstraction                 │   │
│  │         (OpenRouter / Claude / OpenAI / Local)       │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           PostgreSQL + Redis + CP Tracking           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Revenue Model (3 Pools)

```
Project Revenue (after costs)
├── 30-40% → Original Author (perpetual)
├── 40-50% → Project Contributors (by CP)
└── 15-25% → ACCU Core Pool
    ├── Infrastructure
    ├── Agent maintenance
    ├── Treasury
    └── Community Incentive Pool
```

See `docs/governance/CONTRIBUTION_POINTS.md` for CP calculation.

---

## Directory Structure

```
accu/
├── CLAUDE.md              # THIS FILE
├── docs/
│   ├── vision/            # Manifesto, original dialog
│   ├── governance/        # Charter, CP spec
│   ├── candidates/        # Discovery reports ← NEW
│   ├── modules/           # Per-module specifications
│   ├── architecture/      # ADRs
│   └── development/       # Sprint tracking
├── src/accu/
│   ├── agents/
│   │   ├── base.py
│   │   └── discovery/     # Scout agent
│   ├── providers/         # AI abstraction
│   ├── api/               # FastAPI routes
│   └── models/            # DB models
└── tests/
```

---

## VPS Deployment

**Host:** instance102973.waicore.network
**Port:** 8080
**Path:** /root/accu

```bash
# SSH to VPS, then:
cd ~/accu
export PATH="$HOME/.local/bin:$PATH"
uv run uvicorn accu.main:app --host 0.0.0.0 --port 8080
```

---

## Key Files to Check

| Purpose | File |
|---------|------|
| Original vision | `docs/vision/0_original_dialog.md` |
| Current sprint | `docs/development/CURRENT_SPRINT.md` |
| Governance rules | `docs/governance/GOVERNANCE_CHARTER.md` |
| CP specification | `docs/governance/CONTRIBUTION_POINTS.md` |
| Discovery spec | `docs/modules/discovery/SPEC.md` |
| Provider spec | `docs/modules/providers/SPEC.md` |
| **First candidate** | `docs/candidates/001_yapsy.md` |

---

## Commands Reference

```bash
# Local development
uv sync
uv run uvicorn accu.main:app --reload

# VPS deployment
ssh root@<vps-ip>
cd ~/accu && git pull
uv sync
uv run uvicorn accu.main:app --host 0.0.0.0 --port 8080

# Tests
uv run pytest
```

---

## Open Questions / Decisions Needed

- [x] VPS specs — 2GB RAM, 30GB disk, 1 CPU (sufficient for MVP)
- [x] OpenRouter API key — configured
- [ ] Domain name for API
- [ ] GitHub App vs PAT for repository access
- [ ] PostgreSQL setup on VPS
- [ ] Systemd service for persistent run

---

## Discovery Candidates

| ID | Project | Score | Status | Report |
|----|---------|-------|--------|--------|
| 001 | [yapsy](https://github.com/tibonihoo/yapsy) | 78/100 | 🟢 **RECOMMENDED** | `docs/candidates/001_yapsy.md` |
| 002 | [datasetGPT](https://github.com/radi-cho/datasetGPT) | 72/100 | 🟡 Potential | `docs/candidates/002_datasetGPT.md` |
| 003 | [slackify](https://github.com/Ambro17/slackify) | 65/100 | ⚪ Pass | `docs/candidates/003_slackify.md` |

### Winner: yapsy ← QUICK WIN DISCOVERED
- Python plugin framework, 13 years history, ~200 stars
- **Critical:** Issue #23 — community actively seeking maintainers!
- **Plot twist:** Python 3.12 fix ALREADY EXISTS on GitHub master!
- Just needs: testing + CI + PyPI release
- Fork created: https://github.com/CreatmanCEO/yapsy

---

## Session Log

### 2026-02-10 — Session 2
- Ran Discovery Agent demo using MCP GitHub tools
- Found first candidate: **yapsy** (tibonihoo/yapsy)
- Created Discovery Report #001 (`docs/candidates/001_yapsy.md`)
- Identified perfect entry point: Issue #23 "Request for maintainers"

**Next:** Decision on yapsy revival, contact strategy

### 2026-02-10 — Session 1
- Created GitHub repo (private)
- Built project structure
- Implemented Discovery Agent (code ready)
- Implemented AI Provider abstraction (OpenRouter)
- Deployed to VPS (port 8080)
- Added Governance Charter + CP Spec
- Integrated original vision dialog

---

## Contact & Resources

- **GitHub:** https://github.com/CreatmanCEO/accu (private)
- **Vision:** `docs/vision/`
- **Governance:** `docs/governance/`
