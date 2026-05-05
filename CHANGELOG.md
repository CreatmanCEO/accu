# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- README rewrite with badges, tech stack table, and limitations section
- `CONTRIBUTING.md` with priority list and PR checklist
- `.github/workflows/validate.yml` — Python syntax check, link presence, LICENSE/CHANGELOG presence
- `CHANGELOG.md` reconstructed from git history

## [0.1.0] — 2026-02-16

### Added
- Multi-agent development system (Conductor / Builder / Scout / Critic) with state tracking
- Discovery API + Tech Critic Agent
- README fetching for AI analysis in Discovery Agent
- Russian translation and language switcher
- Governance docs and original vision dialog
- MIT License (CREATMAN style)
- Initial project structure: FastAPI app, async SQLAlchemy, Redis, structlog, pydantic-settings

### Fixed
- Nested settings now read correctly from `.env`

[Unreleased]: https://github.com/CreatmanCEO/accu/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/CreatmanCEO/accu/releases/tag/v0.1.0
