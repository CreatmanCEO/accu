"""Data models for Discovery Agent."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from accu.agents.base import AgentConfig


class SearchStrategy(str, Enum):
    """Discovery search strategies."""

    ABANDONED_STARS = "abandoned_stars"
    UNFINISHED_IDEAS = "unfinished_ideas"
    SOLO_DEVELOPER = "solo_developer"
    LANGUAGE_SPECIFIC = "language_specific"


class DiscoveryConfig(AgentConfig):
    """Configuration for Discovery Agent."""

    name: str = "discovery-agent"

    # Search settings
    strategies: list[SearchStrategy] = Field(
        default=[SearchStrategy.ABANDONED_STARS, SearchStrategy.SOLO_DEVELOPER]
    )
    max_results_per_strategy: int = 100
    min_stars: int = 5
    max_stars: int = 500
    languages: list[str] = Field(
        default=["python", "javascript", "typescript", "go", "rust"]
    )

    # Analysis settings
    analyze_readme: bool = True
    analyze_code_samples: bool = True
    max_files_to_analyze: int = 5

    # Limits
    max_repos_per_run: int = 50
    cooldown_hours: int = 24


class RepositoryMetrics(BaseModel):
    """Quantitative metrics for a repository."""

    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    watchers: int = 0
    contributors_count: int = 0
    commit_count_last_year: int = 0
    days_since_last_commit: int = 0
    days_since_last_release: int | None = None


class RepositorySignals(BaseModel):
    """Qualitative signals about a repository."""

    is_abandoned: bool = False
    has_readme: bool = False
    has_license: bool = False
    has_tests: bool = False
    has_ci: bool = False
    has_documentation: bool = False
    documentation_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    code_quality_estimate: float = Field(default=0.0, ge=0.0, le=1.0)


class RepositoryScores(BaseModel):
    """Calculated scores for a repository."""

    potential: float = Field(default=0.0, ge=0.0, le=1.0)
    revival_feasibility: float = Field(default=0.0, ge=0.0, le=1.0)
    product_fit: float = Field(default=0.0, ge=0.0, le=1.0)


class AIAnalysis(BaseModel):
    """AI-generated analysis of a repository."""

    summary: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    revival_recommendation: str = ""
    estimated_effort_hours: int | None = None
    target_audience: str = ""


class CandidateStatus(str, Enum):
    """Status of a discovery candidate."""

    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class DiscoveryCandidate(BaseModel):
    """A discovered repository candidate."""

    # Repository info
    github_url: str
    owner: str
    name: str
    description: str | None = None
    language: str | None = None
    license: str | None = None
    created_at: datetime | None = None
    pushed_at: datetime | None = None
    topics: list[str] = Field(default_factory=list)

    # Analysis
    metrics: RepositoryMetrics
    signals: RepositorySignals
    scores: RepositoryScores
    ai_analysis: AIAnalysis | None = None

    # Status
    status: CandidateStatus = CandidateStatus.PENDING
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    notes: str | None = None

    # Metadata
    discovery_strategy: str | None = None
    run_id: str | None = None


class DiscoveryRunResult(BaseModel):
    """Result of a discovery run."""

    run_id: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str = "running"  # running, completed, failed
    strategy: str | None = None
    repos_scanned: int = 0
    candidates_found: int = 0
    candidates: list[DiscoveryCandidate] = Field(default_factory=list)
    error: str | None = None
    config: DiscoveryConfig | None = None
