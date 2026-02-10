# ACCU — AI-Curated Code Universe

[![en](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![ru](https://img.shields.io/badge/lang-Русский-green.svg)](README.ru.md)

Живая экосистема, где искусственный интеллект и люди-создатели совместно переоткрывают, модернизируют и дают новую жизнь недооценённому open-source программному обеспечению.

## Видение

ACCU трансформирует заброшенные, незамеченные или незаконченные репозитории в устойчивые, развивающиеся цифровые продукты — не стирая авторство, культуру или изначальный замысел.

**Мы курируем, не эксплуатируем. Развиваем, не переписываем. Сотрудничаем, не заменяем.**

## Статус

**Текущая фаза:** Разработка MVP

| Компонент | Статус |
|-----------|--------|
| Discovery Agent | В проектировании |
| AI Provider Abstraction | В проектировании |
| Technical Analyst | Запланирован |
| Web Interface | Запланирован |

## Быстрый старт

```bash
# Клонирование
git clone https://github.com/CreatmanCEO/accu.git
cd accu

# Настройка
python -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate на Windows
pip install -e ".[dev]"

# Конфигурация
cp .env.example .env
# Отредактируйте .env, добавив API ключи

# Запуск
uvicorn accu.main:app --reload
```

## Документация

- **Видение и принципы:** `docs/vision/`
- **Архитектура:** `docs/architecture/`
- **Спецификации модулей:** `docs/modules/`
- **Руководство разработчика:** `docs/development/`

Для сессий Claude Code начните с `CLAUDE.md`.

## Архитектура

```
Discovery → Evaluation → Evolution → Sustainability
    ↓           ↓            ↓            ↓
 AI Scout   Analysts    Contributors   Community
```

Все AI-агенты работают под строгим человеческим контролем. См. `docs/vision/4_ai_agents.md`.

## Участие

ACCU сейчас находится в стадии приватной разработки. Руководство по участию будет опубликовано при открытии проекта.

## Лицензия

MIT
