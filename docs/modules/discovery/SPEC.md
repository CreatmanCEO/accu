# Discovery Agent — Module Specification

**Version:** 0.1.0
**Status:** In Design
**Owner:** TBD

---

## Purpose

The Discovery Agent identifies undervalued, abandoned, or overlooked software projects with high latent potential from public code repositories.

---

## Responsibilities

### Must Do
- Search GitHub for repositories matching criteria
- Analyze repository metadata (commits, issues, activity)
- Calculate "potential score" based on signals
- Store candidates for human review
- Respect GitHub API rate limits

### Must NOT Do
- Onboard projects automatically
- Contact repository authors
- Make decisions based on popularity alone
- Commit or modify any external repositories

---

## Input Sources

| Source | Type | Priority |
|--------|------|----------|
| GitHub API | Primary | P0 |
| Community nominations | Secondary | P1 |
| Cross-references from other repos | Future | P2 |

---

## Output

```json
{
  "repository": {
    "url": "https://github.com/owner/repo",
    "name": "repo",
    "owner": "owner",
    "description": "...",
    "language": "Python",
    "license": "MIT",
    "created_at": "2020-01-15T00:00:00Z",
    "pushed_at": "2023-06-01T00:00:00Z"
  },
  "metrics": {
    "stars": 45,
    "forks": 12,
    "open_issues": 8,
    "watchers": 5,
    "contributors_count": 3,
    "commit_count_last_year": 0,
    "days_since_last_commit": 620
  },
  "signals": {
    "abandoned": true,
    "has_readme": true,
    "has_license": true,
    "has_tests": false,
    "documentation_quality": 0.6,
    "code_quality_estimate": 0.7
  },
  "scores": {
    "potential": 0.72,
    "revival_feasibility": 0.65,
    "product_fit": 0.58
  },
  "ai_analysis": {
    "summary": "Well-architected CLI tool for...",
    "strengths": ["Clean code", "Good abstractions"],
    "weaknesses": ["No tests", "Outdated dependencies"],
    "revival_recommendation": "Medium effort, high value"
  },
  "discovered_at": "2026-02-10T12:00:00Z",
  "status": "pending_review"
}
```

---

## Scoring Algorithm

### Potential Score (0-1)

```
potential = w1*quality + w2*uniqueness + w3*completeness + w4*revival_effort

where:
  quality = code_quality_estimate (AI-assessed)
  uniqueness = 1 - (similar_repos_count / 100)
  completeness = (has_readme + has_license + has_docs + has_tests) / 4
  revival_effort = 1 - (estimated_hours / 1000)

weights (default):
  w1 = 0.3, w2 = 0.25, w3 = 0.25, w4 = 0.2
```

### Abandonment Criteria

Repository considered abandoned if:
- No commits in last 12 months AND
- No issue activity in last 6 months AND
- Has at least 10 stars (indicates past interest)

---

## Search Strategies

### Strategy 1: Abandoned Stars
```
stars:10..500 pushed:<2024-01-01 archived:false
```
Repositories with moderate stars but no recent activity.

### Strategy 2: Unfinished Ideas
```
stars:5..50 topics:mvp OR topics:prototype OR topics:proof-of-concept
```
Projects explicitly marked as incomplete.

### Strategy 3: Solo Developer Gems
```
stars:20..200 contributors:1 pushed:<2024-06-01
```
Quality work from single developers who moved on.

### Strategy 4: Language-Specific
```
language:python stars:15..300 pushed:<2024-01-01 topic:cli
```
Focused searches for specific tech stacks.

---

## Configuration

```yaml
discovery:
  name: "discovery-agent"
  version: "0.1.0"

  provider:
    type: "openrouter"
    model: "anthropic/claude-3-haiku"  # Cost-effective for scanning
    fallback_model: "openai/gpt-4o-mini"

  github:
    api_version: "2022-11-28"
    rate_limit_buffer: 0.8  # Use 80% of rate limit

  search:
    strategies:
      - "abandoned_stars"
      - "unfinished_ideas"
      - "solo_developer"
    max_results_per_strategy: 100
    min_stars: 5
    max_stars: 500
    languages: ["python", "javascript", "typescript", "go", "rust"]

  analysis:
    readme_analysis: true
    code_sample_analysis: true  # Analyze first 5 files
    max_files_to_analyze: 5

  output:
    batch_size: 10
    store_raw_data: true

  limits:
    max_repos_per_run: 50
    cooldown_between_runs_hours: 24
```

---

## API Endpoints

```
POST /api/v1/discovery/run
  → Trigger discovery run

GET /api/v1/discovery/runs
  → List discovery runs

GET /api/v1/discovery/runs/{run_id}
  → Get run status and results

GET /api/v1/discovery/candidates
  → List discovered candidates

GET /api/v1/discovery/candidates/{id}
  → Get candidate details

PATCH /api/v1/discovery/candidates/{id}
  → Update candidate status (reviewed, approved, rejected)
```

---

## Database Schema

```sql
CREATE TABLE discovery_runs (
    id UUID PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- running, completed, failed
    strategy VARCHAR(50),
    repos_scanned INT DEFAULT 0,
    candidates_found INT DEFAULT 0,
    config JSONB,
    error TEXT
);

CREATE TABLE discovery_candidates (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES discovery_runs(id),
    github_url VARCHAR(500) NOT NULL UNIQUE,
    owner VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    metadata JSONB NOT NULL,
    metrics JSONB NOT NULL,
    signals JSONB NOT NULL,
    scores JSONB NOT NULL,
    ai_analysis JSONB,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, reviewed, approved, rejected
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_candidates_status ON discovery_candidates(status);
CREATE INDEX idx_candidates_scores ON discovery_candidates((scores->>'potential'));
```

---

## Error Handling

| Error | Action |
|-------|--------|
| GitHub rate limit | Wait and retry with exponential backoff |
| AI provider timeout | Retry 3 times, then skip repo |
| Invalid repository data | Log and skip |
| Database connection lost | Queue results, retry connection |

---

## Monitoring

Metrics to track:
- Repos scanned per run
- Candidates found per run
- Average potential score
- AI tokens consumed
- API costs per run
- False positive rate (after human review)

---

## Testing Strategy

1. **Unit tests:** Scoring algorithm, data parsing
2. **Integration tests:** GitHub API mocking, database operations
3. **E2E tests:** Full discovery run with test repositories

---

## Implementation Files

```
src/accu/agents/discovery/
├── __init__.py
├── agent.py           # Main agent class
├── scanner.py         # GitHub scanning logic
├── analyzer.py        # AI-powered analysis
├── scorer.py          # Scoring algorithm
├── strategies.py      # Search strategies
└── models.py          # Pydantic models
```

---

## Dependencies

- `httpx` — Async HTTP client for GitHub API
- `pydantic` — Data validation
- `sqlalchemy` — Database ORM
- AI provider SDK (via abstraction layer)
