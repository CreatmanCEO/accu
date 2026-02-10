# Current Sprint — yapsy Revival + Agent Development

**Sprint:** 2 (Parallel Track)
**Started:** 2026-02-10
**Goal:** Возрождение yapsy параллельно с достройкой агентов

---

## Dual Track Strategy

```
TRACK A: yapsy Revival              TRACK B: Agent Development
─────────────────────────           ─────────────────────────
[x] Discovery (найти)               [ ] Discovery API endpoints
[→] Fork + Comment                  [ ] PostgreSQL setup
[ ] Python 3.12 fix                 [ ] Tech Critic Agent
[ ] CI/CD setup                     [ ] Modernizer Agent
[ ] README update                   [ ] Scheduler/Cron
[ ] PyPI release                    [ ] Dashboard UI
```

---

## Track A: yapsy Revival

### Phase 1: Захват (Day 1) ← СЕЙЧАС
- [x] Discovery Report создан
- [ ] Fork `tibonihoo/yapsy` → `CreatmanCEO/yapsy-revival`
- [ ] Comment на Issue #23 с предложением
- [ ] Clone локально для анализа

### Phase 2: Анализ (Day 2-3)
- [ ] Полный анализ кодовой базы
- [ ] Найти все использования `imp` модуля
- [ ] Определить scope работы
- [ ] Создать Technical Report

### Phase 3: Фикс (Day 4-7)
- [ ] Заменить `imp` → `importlib`
- [ ] Добавить GitHub Actions CI
- [ ] Тесты на Python 3.10, 3.11, 3.12, 3.13
- [ ] Обновить pyproject.toml

### Phase 4: Релиз (Day 8-10)
- [ ] README rewrite
- [ ] CHANGELOG
- [ ] Version bump → 2.0.0
- [ ] PyPI publish (если права получим)

---

## Track B: Agent Development

### Priority 1: Discovery Agent → Production
- [x] Core agent code exists
- [ ] POST `/api/v1/discovery/run` endpoint
- [ ] GET `/api/v1/discovery/candidates` endpoint
- [ ] PostgreSQL schema + migrations
- [ ] GitHub Token configuration
- [ ] Rate limiting

### Priority 2: Tech Critic Agent (NEW)
- [ ] `src/accu/agents/critic/agent.py`
- [ ] Code quality analysis prompts
- [ ] Dependency audit
- [ ] Security scan integration
- [ ] Output: Technical Report JSON

### Priority 3: Modernizer Agent (NEW)
- [ ] `src/accu/agents/modernizer/agent.py`
- [ ] Pattern-based code transformation
- [ ] Dependency updates
- [ ] PR generation
- [ ] Output: Git patches

---

## Definition of Done

### Track A Success
- [ ] yapsy works on Python 3.12+
- [ ] Tests pass in CI
- [ ] At least 1 external contributor engaged

### Track B Success
- [ ] Discovery Agent runs via API autonomously
- [ ] Tech Critic produces analysis report
- [ ] All agents use unified provider abstraction

---

## Session Log

### 2026-02-10 — Session 1
- Created GitHub repo, project structure
- Deployed to VPS (port 8080)
- Added governance docs

### 2026-02-10 — Session 2
- Discovery Agent demo (manual via Claude Code)
- Found 3 candidates: yapsy, datasetGPT, slackify
- Selected yapsy (score 78/100)
- Decision: parallel development approach
- **Next:** Fork yapsy, comment on Issue #23

---

## Blockers

| Blocker | Owner | Status |
|---------|-------|--------|
| GitHub Token for VPS | Founder | Needed for autonomous agents |
| PostgreSQL on VPS | Claude Code | Not started |
