# ACCU Discovery Report #002

## Project: datasetGPT

**Repository:** https://github.com/radi-cho/datasetGPT
**Discovery Date:** 2026-02-10
**Discovery Agent Version:** 0.1.0
**Status:** 🟡 POTENTIAL CANDIDATE

---

## Executive Summary

**datasetGPT** — CLI-инструмент для генерации текстовых датасетов с помощью LLM. Крайне релевантен в эпоху AI — используется для создания training data, fine-tuning моделей, исследований.

### Ключевой сигнал
Проект заброшен с августа 2023, но имеет высокую актуальность для AI-разработчиков.

---

## Repository Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Created | 2023-03-12 | ~3 года истории |
| Last Push | 2023-08-25 | ~2.5 года назад ⚠️ |
| Stars | ~300 | Хороший интерес |
| Language | Python | Основной стек ACCU |
| License | MIT (implied) | Свободная ✓ |

---

## What It Does

```bash
# Генерация текстов с разными LLM
datasetGPT texts \
    --prompt "If {country} was a planet..." \
    --backend "openai|gpt-4" \
    --backend "cohere|medium" \
    --option country Germany

# Генерация диалогов между двумя агентами
datasetGPT conversations \
    --agent1 "You're a shop assistant..." \
    --agent2 "You're a customer..." \
    --length 5
```

**Use Cases:**
- Создание датасетов для детекторов AI-контента
- Сбор данных для исследований AI
- Автоматизация задач над большими объёмами текста
- Fine-tuning малых моделей на выходах больших

---

## Open Issues Analysis

| # | Issue | Status | Revival Opportunity |
|---|-------|--------|---------------------|
| 4 | Adding localization (i18n) | Open | Medium - мультиязычность |
| 3 | Don't overwrite file in single_file mode | Open | Easy - enhancement |
| 2 | Format initial utterance with template | Open | Easy - consistency fix |
| 1 | Shared storage / community dataset | Open | High - community feature |

**Особенность:** Нет критических багов, только enhancement requests.

---

## ACCU Score Analysis

### Potential Score: 72/100

| Factor | Weight | Score | Contribution |
|--------|--------|-------|--------------|
| Code Quality | 20% | 80 | 16 |
| Community Interest | 15% | 70 | 10.5 |
| Technical Debt | 15% | 75 | 11.25 |
| Market Fit | 15% | 85 | 12.75 |
| Revival Feasibility | 20% | 70 | 14 |
| Author Accessibility | 15% | 50 | 7.5 |

### Revival Feasibility: MEDIUM-HIGH

1. ✅ Хорошо структурированный код
2. ✅ Отличная документация
3. ✅ Актуальная тематика (AI/LLM)
4. ⚠️ Нет явного запроса на мейнтейнеров
5. ⚠️ Автор активен, но не на этом проекте

---

## Modernization Opportunities

### Phase 1: Update LLM Support
- [ ] Добавить Claude 3.5/4 как backend
- [ ] Добавить Gemini, Llama 3
- [ ] Обновить OpenAI API (v1.0+)

### Phase 2: New Features
- [ ] Async generation для скорости
- [ ] Streaming output
- [ ] Dataset versioning
- [ ] HuggingFace Hub integration

### Phase 3: Community
- [ ] Shared dataset repository
- [ ] Dataset quality metrics
- [ ] Leaderboard of datasets

---

## Revenue Potential

### Use Cases
1. **AI Researchers** — создание training data
2. **ML Engineers** — fine-tuning datasets
3. **Content Teams** — автоматизация генерации
4. **AI Safety** — датасеты для детекторов

### Monetization Paths
- **Pro CLI** с расширенными backends
- **Hosted service** для генерации датасетов
- **Dataset marketplace** комиссия
- **Enterprise API** с SLA

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Author active elsewhere | Medium | Low | Fork strategy |
| Fast-moving AI space | High | Medium | Frequent updates needed |
| Competition | Medium | Medium | Focus on UX/community |

---

## Comparison with yapsy (#001)

| Criterion | yapsy | datasetGPT |
|-----------|-------|------------|
| Maintainer request | ✅ Yes | ❌ No |
| Critical bugs | ✅ Yes (Python 3.12) | ❌ No |
| Market relevance | Medium | **High** |
| Community signal | Strong | Medium |
| Entry barrier | Low | Medium |

---

## Recommendation

**HOLD** — хороший кандидат, но нет явного сигнала от сообщества (нет issue "looking for maintainers"). Рекомендуется:

1. Открыть issue с предложением помощи
2. Если автор не отвечает 14 дней — форк
3. Как backup-кандидат после yapsy

---

*Generated by ACCU Discovery Agent v0.1.0*
*Report ID: ACCU-DISC-002*
