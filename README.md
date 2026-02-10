# ACCU — AI-Curated Code Universe

A living ecosystem where artificial intelligence and human creators collaborate to rediscover, modernize, and give new life to undervalued open-source software.

## Vision

ACCU transforms abandoned, overlooked, or unfinished repositories into sustainable, evolving digital products — without erasing authorship, culture, or intent.

**We curate, not exploit. We evolve, not overwrite. We collaborate, not replace.**

## Status

**Current Phase:** MVP Development

| Component | Status |
|-----------|--------|
| Discovery Agent | In Design |
| AI Provider Abstraction | In Design |
| Technical Analyst | Planned |
| Web Interface | Planned |

## Quick Start

```bash
# Clone
git clone https://github.com/CreatmanCEO/accu.git
cd accu

# Setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn accu.main:app --reload
```

## Documentation

- **Vision & Principles:** `docs/vision/`
- **Architecture:** `docs/architecture/`
- **Module Specs:** `docs/modules/`
- **Development Guide:** `docs/development/`

For Claude Code sessions, start with `CLAUDE.md`.

## Architecture

```
Discovery → Evaluation → Evolution → Sustainability
    ↓           ↓            ↓            ↓
 AI Scout   Analysts    Contributors   Community
```

All AI agents operate under strict human oversight. See `docs/vision/4_ai_agents.md`.

## Contributing

ACCU is currently in private development. Contribution guidelines will be published when we open the project.

## License

MIT
