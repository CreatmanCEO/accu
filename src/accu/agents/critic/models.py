"""Data models for Tech Critic Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from accu.agents.base import AgentConfig


class Severity(str, Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CodeIssue(BaseModel):
    """A code quality issue found during analysis."""

    file_path: str
    line_number: Optional[int] = None
    severity: Severity
    category: str  # e.g., "security", "performance", "maintainability"
    message: str
    suggestion: Optional[str] = None


class DependencyInfo(BaseModel):
    """Information about a project dependency."""

    name: str
    current_version: Optional[str] = None
    latest_version: Optional[str] = None
    is_outdated: bool = False
    has_vulnerabilities: bool = False
    vulnerability_count: int = 0


class CodeMetrics(BaseModel):
    """Quantitative code metrics."""

    total_files: int = 0
    total_lines: int = 0
    python_files: int = 0
    test_files: int = 0
    test_coverage_estimate: Optional[float] = None
    avg_function_length: Optional[float] = None
    avg_file_length: Optional[float] = None


class ArchitectureAssessment(BaseModel):
    """Assessment of project architecture."""

    patterns_detected: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class TechnicalReport(BaseModel):
    """Complete technical analysis report."""

    # Metadata
    repository_url: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    agent_version: str = "0.1.0"

    # Summary
    overall_score: float = Field(ge=0, le=100)  # 0-100
    summary: str

    # Detailed analysis
    metrics: CodeMetrics
    architecture: ArchitectureAssessment
    issues: list[CodeIssue] = Field(default_factory=list)
    dependencies: list[DependencyInfo] = Field(default_factory=list)

    # Recommendations
    priority_fixes: list[str] = Field(default_factory=list)
    modernization_suggestions: list[str] = Field(default_factory=list)
    estimated_effort_hours: Optional[float] = None

    # Revival assessment
    revival_feasibility: float = Field(ge=0, le=1)  # 0-1
    revival_blockers: list[str] = Field(default_factory=list)


class CriticConfig(AgentConfig):
    """Configuration for Tech Critic Agent."""

    name: str = "tech-critic"
    version: str = "0.1.0"

    # Analysis settings
    analyze_dependencies: bool = True
    analyze_security: bool = True
    max_files_to_analyze: int = 50
    file_extensions: list[str] = Field(
        default_factory=lambda: [".py", ".js", ".ts", ".go", ".rs"]
    )

    # AI settings
    model: str = "anthropic/claude-3-haiku"
    analysis_model: str = "anthropic/claude-3-sonnet"  # Better model for deep analysis
