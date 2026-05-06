# ACCU — AI-Curated Code Universe

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/CreatmanCEO/accu?style=social)](https://github.com/CreatmanCEO/accu/stargazers)
[![Validate](https://github.com/CreatmanCEO/accu/actions/workflows/validate.yml/badge.svg)](https://github.com/CreatmanCEO/accu/actions/workflows/validate.yml)
[![Status: MVP](https://img.shields.io/badge/status-MVP%20development-orange)](#status)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

[![en](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![ru](https://img.shields.io/badge/lang-Русский-green.svg)](README.ru.md)

An ecosystem for reviving undervalued open-source software through AI-curated discovery, evaluation, and evolution under human oversight.

## Why this exists

Tens of thousands of useful repos sit abandoned on GitHub — outdated dependencies, broken builds, missing maintainers, but solid ideas. ACCU surfaces them, scores them, and helps a small team revive the ones worth saving without erasing original authorship.

It is not a fork-bot. It is a curation pipeline: Discovery Agent finds candidates, a Tech Critic evaluates them, humans approve, and only then evolution starts.

**We curate, not exploit. We evolve, not overwrite. We collaborate, not replace.**

## How it works

```
Discovery → Evaluation → Evolution → Sustainability
    ↓           ↓            ↓            ↓
 AI Scout    Analysts   Contributors   Community
```

1. **Discovery Agent** — scans GitHub for low-star, abandoned, technically interesting repos
2. **Tech Critic** — fetches README, infers stack, flags red flags (security, license, maintenance)
3. **Human review** — every candidate passes through a maintainer before any code is touched
4. **Evolution** — incremental modernization with full attribution to original authors

Multi-agent orchestration is documented in `docs/agents/` and the project's `CLAUDE.md`.

## Status

**Current Phase:** MVP Development

| Component | Status |
|-----------|--------|
| Discovery Agent | Working (REST API) |
| AI Provider Abstraction | Working |
| Tech Critic Agent | Working |
| Web Interface | Planned |
| Evolution Pipeline | Planned |

## Tech stack

| Layer | Tool |
|-------|------|
| API | FastAPI + Uvicorn |
| Data | SQLAlchemy 2 (async) + asyncpg + Alembic |
| Cache / queue | Redis |
| Config | pydantic-settings |
| HTTP | httpx |
| Logging | structlog |
| Tests | pytest + pytest-asyncio + coverage |
| Lint | ruff + mypy (strict) |
| Build | hatchling |

## Quick start

```bash
git clone https://github.com/CreatmanCEO/accu.git
cd accu
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env        # set GitHub token + AI provider keys
uvicorn accu.main:app --reload
```

API will be available at http://localhost:8000. See `docs/modules/` for endpoint specs.

## Documentation

- `CLAUDE.md` — start here for any Claude Code session on this repo
- `docs/vision/` — principles and long-term direction
- `docs/architecture/` — system design
- `docs/modules/` — per-component specs
- `docs/governance/` — decision-making and authorship rules
- `docs/agents/` — multi-agent orchestration model

## Limitations

- MVP only — Discovery + Tech Critic work; the rest is design docs
- No public web UI yet
- Single-tenant; no auth layer beyond API keys in `.env`
- Discovery quality depends on the configured AI provider; outputs are not deterministic
- Not production-ready — expect breaking changes between commits

## Contributing

ACCU is in early development. Maintainer-only contributions for now. See [CONTRIBUTING.md](CONTRIBUTING.md) for the priority list and PR checklist when contributions open.

## Related — Claude Code ecosystem by the same author

- [claude-code-antiregression-setup](https://github.com/CreatmanCEO/claude-code-antiregression-setup) — guard rails against regressions in Claude Code sessions
- [ai-context-hierarchy](https://github.com/CreatmanCEO/ai-context-hierarchy) — Level 0/1/2 context layout for Claude projects
- [claude-statusline](https://github.com/CreatmanCEO/claude-statusline) — status bar for Claude Code
- [notebooklm-claude-workflows](https://github.com/CreatmanCEO/notebooklm-claude-workflows) — NotebookLM + Claude research loops
- [webtest-orch](https://github.com/CreatmanCEO/webtest-orch) — universal e2e test orchestrator
- [hydrowatch](https://github.com/CreatmanCEO/hydrowatch) — water/utility monitoring tooling
- [lingua-companion](https://github.com/CreatmanCEO/lingua-companion) — voice-first English learning
- [security-scanner](https://github.com/CreatmanCEO/security-scanner) — Telegram security scanning bot
- [diabot](https://github.com/CreatmanCEO/diabot) — KBJU-by-photo bot for type 1 diabetes
- [ghost-showcase](https://github.com/CreatmanCEO/ghost-showcase) — GHOST AI desktop overlay (paused)
- [cc-janitor](https://github.com/CreatmanCEO/cc-janitor) — Claude Code workspace janitor (in active development)

## Author

**Nick Podolyak**
- GitHub: [@CreatmanCEO](https://github.com/CreatmanCEO)
- Habr: [creatman](https://habr.com/ru/users/creatman/)
- dev.to: [@creatman](https://dev.to/creatman)
- Telegram: [@Creatman_it](https://t.me/Creatman_it)
- Site: [creatman.site](https://creatman.site)

## License

MIT — see [LICENSE](LICENSE).
