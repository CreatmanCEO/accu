# ACCU Decision Log

> Institutional memory: why we made the decisions we made.
> Format: [DATE] [AGENT] DECISION: ... REASON: ...

---

[2026-02-10] [Human+Claude] DECISION: Choose yapsy as first revival target
REASON: 13-year history, clear maintainer request (#23), Python 3.12 fix already exists on GitHub but not released. Low risk, high visibility proof of concept.

[2026-02-10] [Human+Claude] DECISION: Build Discovery Agent and yapsy revival in parallel (Track A + Track B)
REASON: Can't wait for one to complete. Need to validate both the system AND have a success story.

[2026-02-10] [Builder] DECISION: Fork yapsy to CreatmanCEO/yapsy, add GitHub Actions CI
REASON: Original repo has no CI. Our fork demonstrates immediate value-add.

[2026-02-10] [Builder] DECISION: Create PR #26 to original yapsy with CI
REASON: Contributing back to original shows good faith, aligns with ACCU principles.

[2026-02-12] [Human+Claude] DECISION: Build multi-agent system for ACCU development
REASON: Single agent context gets lost, priorities drift. Need specialized roles with clear boundaries to scale development while maintaining coherence.

[2026-02-12] [Human] DECISION: Rent new server (4GB RAM, 60GB storage) for agent infrastructure
REASON: Need dedicated environment for running multiple Claude Code agents.

---

## Decision Template
```
[DATE] [AGENT] DECISION: What was decided
REASON: Why this decision was made
ALTERNATIVES CONSIDERED: What else was considered (optional)
REVERSIBLE: Yes/No (optional)
```
