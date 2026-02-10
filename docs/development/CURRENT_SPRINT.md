# Current Sprint — Discovery Agent MVP

**Sprint:** 1
**Started:** 2026-02-10
**Goal:** Implement working Discovery Agent that can find undervalued GitHub repositories

---

## Sprint Objectives

1. ✅ Project setup and documentation structure
2. ⬜ AI Provider abstraction layer
3. ⬜ Discovery Agent core implementation
4. ⬜ GitHub API integration
5. ⬜ Basic API endpoints
6. ⬜ Docker deployment setup

---

## Tasks

### Completed
- [x] Create GitHub repository
- [x] Initialize project structure
- [x] Create CLAUDE.md for continuity
- [x] Define tech stack decisions

### In Progress
- [ ] **AI Provider Abstraction** — `src/accu/providers/`
  - Base provider interface
  - OpenRouter implementation
  - Anthropic direct implementation
  - Configuration schema

### Upcoming
- [ ] **Discovery Agent Core** — `src/accu/agents/discovery/`
  - Agent base class
  - GitHub repository scanner
  - Scoring algorithm (activity, quality signals)
  - Result storage

- [ ] **API Layer** — `src/accu/api/`
  - FastAPI setup
  - Discovery endpoints
  - Authentication (API keys)

- [ ] **Infrastructure**
  - Docker configuration
  - Database schema
  - Environment configuration

---

## Blockers

| Blocker | Owner | Status |
|---------|-------|--------|
| VPS access confirmation | User | Pending |
| OpenRouter API key | User | Pending |

---

## Session Log

### 2026-02-10 — Session 1
- Created GitHub repo: CreatmanCEO/accu (private)
- Established project structure
- Created CLAUDE.md with full context
- Defined module development order
- Next: Implement AI provider abstraction

---

## Definition of Done (Sprint 1)

- [ ] Discovery agent can search GitHub for repositories
- [ ] Agent uses configurable AI provider (OpenRouter)
- [ ] Results stored in PostgreSQL
- [ ] Basic API exposes discovery results
- [ ] Docker Compose runs the stack
- [ ] Documentation updated
