# ACCU — AI-Curated Code Universe

## Quick Start for Claude Code

**What is this?** Ecosystem for reviving undervalued open-source projects through human-AI collaboration.

**Current Phase:** MVP Development — Phase 1 (Discovery Agent)

**Last Updated:** 2026-02-10

---

## Project Status Dashboard

| Module | Status | Priority | Next Action |
|--------|--------|----------|-------------|
| Discovery Agent | 🟡 In Design | P0 | Implement GitHub scanner |
| Technical Analyst | ⚪ Not Started | P1 | Wait for Discovery |
| Product Re-evaluator | ⚪ Not Started | P2 | — |
| Evolution Support | ⚪ Not Started | P2 | — |
| Governance Observer | ⚪ Not Started | P3 | — |
| API Gateway | ⚪ Not Started | P1 | — |
| Web UI | ⚪ Not Started | P2 | — |
| Share Accounting | ⚪ Not Started | P2 | — |

Status: ⚪ Not Started | 🟡 In Progress | 🟢 Complete | 🔴 Blocked

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      ACCU Platform                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Web UI     │  │  API        │  │  CLI        │         │
│  │  (Frontend) │  │  Gateway    │  │  Tools      │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         └────────────────┼────────────────┘                 │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Agent Orchestrator                      │   │
│  │         (Claude Code / Custom Logic)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│         │           │           │           │               │
│         ▼           ▼           ▼           ▼               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Discovery │ │Technical │ │ Product  │ │Evolution │       │
│  │  Agent   │ │ Analyst  │ │Re-evaltor│ │ Support  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│         │           │           │           │               │
│         └───────────┴───────────┴───────────┘               │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              AI Provider Abstraction                 │   │
│  │    (OpenRouter / Claude API / Local LLM / etc.)      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Data Layer                         │   │
│  │         (PostgreSQL + Redis Cache)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Backend | Python 3.11+ / FastAPI | User preference, async support |
| Database | PostgreSQL | Relational data, JSONB for flexibility |
| Cache | Redis | Session, rate limiting, job queue |
| Frontend | React + TypeScript | Modern, component-based |
| AI Providers | OpenRouter (primary) | Multi-model access, cost control |
| Task Queue | Celery / ARQ | Background agent jobs |
| Deployment | Docker + Docker Compose | VPS deployment |

---

## Directory Structure

```
accu/
├── CLAUDE.md              # THIS FILE - project context for Claude Code
├── README.md              # Public project description
├── docs/
│   ├── vision/            # Original manifesto & vision docs
│   ├── architecture/      # Technical architecture decisions
│   ├── modules/           # Per-module specifications
│   ├── api/               # API documentation
│   └── development/       # Development guides & ADRs
├── src/
│   └── accu/
│       ├── __init__.py
│       ├── main.py        # FastAPI application entry
│       ├── config.py      # Configuration management
│       ├── agents/        # AI agent implementations
│       │   ├── base.py    # Base agent class
│       │   ├── discovery/ # Discovery agent module
│       │   ├── analyst/   # Technical analyst module
│       │   └── ...
│       ├── core/          # Core business logic
│       ├── api/           # API routes
│       ├── models/        # Database models
│       └── providers/     # AI provider abstractions
├── tests/
├── scripts/               # Utility scripts
├── config/                # Configuration files
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```

---

## Development Workflow

### Starting a New Session

1. Read this file (CLAUDE.md)
2. Check `docs/development/CURRENT_SPRINT.md` for active tasks
3. Review recent commits: `git log --oneline -10`
4. Continue from where the last session ended

### Making Changes

1. Create feature branch: `git checkout -b feature/<name>`
2. Implement with tests
3. Update relevant docs in `docs/modules/`
4. Update status in this file if milestone reached
5. Commit with descriptive message

### Module Development Order

```
Phase 1 (MVP Core):
  1. AI Provider Abstraction → enables all agents
  2. Discovery Agent → first value demonstration
  3. API Gateway → expose functionality

Phase 2 (Evaluation):
  4. Technical Analyst Agent
  5. Product Re-evaluator Agent
  6. Web UI (basic)

Phase 3 (Evolution):
  7. Evolution Support Agent
  8. Share Accounting System
  9. Governance Observer
```

---

## Agent Configuration Schema

All agents follow this configuration pattern:

```yaml
agent:
  name: "discovery"
  version: "0.1.0"

  provider:
    type: "openrouter"  # or "anthropic", "openai", "local"
    model: "anthropic/claude-3-haiku"
    api_key_env: "OPENROUTER_API_KEY"

  limits:
    max_tokens: 4096
    rate_limit_rpm: 60
    timeout_seconds: 30

  capabilities:
    - "github_search"
    - "repository_analysis"

  restrictions:
    - "no_direct_commits"
    - "no_author_contact"
```

---

## Key Files to Check

| Purpose | File |
|---------|------|
| Current sprint tasks | `docs/development/CURRENT_SPRINT.md` |
| Architecture decisions | `docs/architecture/ADR-*.md` |
| Module specs | `docs/modules/<module>/SPEC.md` |
| API contracts | `docs/api/openapi.yaml` |
| Environment setup | `.env.example` |

---

## Commands Reference

```bash
# Development
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest

# Run locally
uvicorn accu.main:app --reload

# Docker
docker-compose up -d

# Database
alembic upgrade head
```

---

## Open Questions / Decisions Needed

- [ ] VPS specs confirmation (CPU/RAM/Storage)
- [ ] OpenRouter API key setup
- [ ] Domain name for API
- [ ] GitHub App vs Personal Access Token for API access

---

## Contact & Resources

- **Vision Docs:** `docs/vision/`
- **Original Manifesto:** `docs/vision/1_manifesto.md`
- **GitHub Repo:** https://github.com/CreatmanCEO/accu (private)
