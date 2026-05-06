# Contributing to ACCU

ACCU is in early MVP development. Contributions are limited to maintainers right now, but issue reports and discussions are welcome.

## Priority list

1. Discovery Agent — improve scoring heuristics, reduce false positives
2. Tech Critic — extend stack inference, add license/security flags
3. Persistence layer — Alembic migrations, retention policy for candidate cache
4. Web interface — read-only candidate browser
5. Provider abstraction — add second AI provider, conformance tests
6. Tests — raise coverage on `accu/agents/`

## Before opening a PR

- [ ] Branch from `main`, name like `feat/...` or `fix/...`
- [ ] `ruff check src/` passes
- [ ] `mypy src/` passes (strict mode)
- [ ] `pytest` passes locally
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] No secrets committed; `.env` not staged
- [ ] PR description explains the *why*, not just the *what*

## Commit style

Conventional Commits — `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.

## Code of conduct

Be honest, be specific, attribute prior art. ACCU exists to credit original authors of the projects it touches — that ethos applies internally too.

## Contact

Open an issue or reach the maintainer via the channels in [README.md](README.md#author).
