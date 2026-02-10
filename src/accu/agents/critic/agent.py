"""Tech Critic Agent implementation."""

import json
import uuid
from datetime import datetime

from accu.agents.base import AgentResult, AgentStatus, BaseAgent
from accu.agents.critic.models import (
    ArchitectureAssessment,
    CodeIssue,
    CodeMetrics,
    CriticConfig,
    DependencyInfo,
    Severity,
    TechnicalReport,
)
from accu.providers import ProviderManager


ANALYSIS_SYSTEM_PROMPT = """You are a senior software architect performing a technical code review.
Your task is to analyze the provided code and produce a structured assessment.

Focus on:
1. Code quality and maintainability
2. Architecture patterns and design
3. Potential bugs and security issues
4. Dependencies and their health
5. Test coverage and quality

Be specific and actionable in your feedback. Reference specific files and line numbers when possible.
Output your analysis as JSON matching the requested schema."""


class TechCriticAgent(BaseAgent):
    """Agent for technical analysis of repositories.

    This agent:
    - Analyzes code quality and architecture
    - Identifies potential issues and technical debt
    - Assesses dependencies for vulnerabilities
    - Produces actionable technical reports

    This agent does NOT:
    - Modify any code
    - Make subjective business decisions
    - Access private repositories without authorization
    - Store sensitive information from analyzed code
    """

    def __init__(
        self,
        config: CriticConfig,
        provider_manager: ProviderManager,
    ):
        super().__init__(config, provider_manager)
        self.config: CriticConfig = config

    @property
    def purpose(self) -> str:
        return "Analyze repositories for code quality, architecture, and revival feasibility"

    @property
    def capabilities(self) -> list[str]:
        return [
            "Analyze code quality and patterns",
            "Identify potential bugs and security issues",
            "Assess project architecture",
            "Evaluate dependencies",
            "Calculate revival feasibility score",
            "Generate technical reports",
        ]

    @property
    def restrictions(self) -> list[str]:
        return [
            "Cannot modify any code",
            "Cannot access private repositories without authorization",
            "Cannot make business decisions",
            "Cannot store sensitive code information",
            "Cannot execute arbitrary code from analyzed repositories",
        ]

    async def run(
        self,
        repository_url: str,
        file_contents: dict[str, str],
        readme_content: str | None = None,
        dependency_file: str | None = None,
    ) -> AgentResult:
        """Execute technical analysis on a repository.

        Args:
            repository_url: URL of the repository being analyzed
            file_contents: Dict mapping file paths to their contents
            readme_content: Optional README content
            dependency_file: Optional requirements.txt or pyproject.toml content

        Returns:
            AgentResult with TechnicalReport data
        """
        self.status = AgentStatus.RUNNING
        report_id = str(uuid.uuid4())
        started_at = datetime.utcnow()

        try:
            # Calculate basic metrics
            metrics = self._calculate_metrics(file_contents)

            # Analyze architecture with AI
            architecture = await self._analyze_architecture(
                file_contents, readme_content
            )

            # Find code issues with AI
            issues = await self._find_issues(file_contents)

            # Analyze dependencies
            dependencies = []
            if dependency_file:
                dependencies = await self._analyze_dependencies(dependency_file)

            # Calculate scores
            overall_score = self._calculate_overall_score(
                metrics, architecture, issues, dependencies
            )
            revival_feasibility = self._calculate_revival_feasibility(
                metrics, issues, dependencies
            )

            # Generate summary
            summary = await self._generate_summary(
                repository_url, metrics, architecture, issues
            )

            # Compile report
            report = TechnicalReport(
                repository_url=repository_url,
                analyzed_at=datetime.utcnow(),
                agent_version=self.config.version,
                overall_score=overall_score,
                summary=summary,
                metrics=metrics,
                architecture=architecture,
                issues=issues,
                dependencies=dependencies,
                priority_fixes=self._prioritize_fixes(issues),
                modernization_suggestions=architecture.recommendations,
                estimated_effort_hours=self._estimate_effort(issues),
                revival_feasibility=revival_feasibility,
                revival_blockers=self._identify_blockers(issues, dependencies),
            )

            self.status = AgentStatus.COMPLETED

            return AgentResult(
                success=True,
                data=report,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                tokens_used=self._get_total_tokens(),
                cost_usd=self._get_total_cost(),
            )

        except Exception as e:
            self.status = AgentStatus.FAILED
            return AgentResult(
                success=False,
                data=None,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

    def _calculate_metrics(self, file_contents: dict[str, str]) -> CodeMetrics:
        """Calculate basic code metrics."""
        total_lines = 0
        python_files = 0
        test_files = 0

        for path, content in file_contents.items():
            lines = len(content.split("\n"))
            total_lines += lines

            if path.endswith(".py"):
                python_files += 1
                if "test" in path.lower() or path.startswith("test_"):
                    test_files += 1

        return CodeMetrics(
            total_files=len(file_contents),
            total_lines=total_lines,
            python_files=python_files,
            test_files=test_files,
            avg_file_length=total_lines / len(file_contents) if file_contents else 0,
        )

    async def _analyze_architecture(
        self,
        file_contents: dict[str, str],
        readme_content: str | None,
    ) -> ArchitectureAssessment:
        """Analyze project architecture using AI."""
        # Prepare context
        file_list = "\n".join(file_contents.keys())
        sample_files = list(file_contents.items())[:5]
        samples = "\n\n".join(
            [f"=== {path} ===\n{content[:2000]}" for path, content in sample_files]
        )

        prompt = f"""Analyze this Python project's architecture.

File structure:
{file_list}

Sample files:
{samples}

{"README:" + readme_content[:2000] if readme_content else ""}

Provide your analysis as JSON:
{{
    "patterns_detected": ["list of design patterns found"],
    "strengths": ["list of architectural strengths"],
    "weaknesses": ["list of architectural weaknesses"],
    "recommendations": ["list of improvement recommendations"]
}}"""

        response = await self.complete(
            ANALYSIS_SYSTEM_PROMPT,
            prompt,
            model=self.config.analysis_model,
        )

        try:
            # Extract JSON from response
            data = self._extract_json(response)
            return ArchitectureAssessment(**data)
        except Exception:
            return ArchitectureAssessment(
                patterns_detected=["Unable to analyze"],
                strengths=[],
                weaknesses=["Analysis failed"],
                recommendations=["Manual review recommended"],
            )

    async def _find_issues(
        self, file_contents: dict[str, str]
    ) -> list[CodeIssue]:
        """Find code issues using AI analysis."""
        issues = []

        # Analyze files in batches
        for path, content in list(file_contents.items())[:self.config.max_files_to_analyze]:
            if not any(path.endswith(ext) for ext in self.config.file_extensions):
                continue

            prompt = f"""Analyze this code for issues:

File: {path}
```
{content[:4000]}
```

Find bugs, security issues, and code quality problems.
Return as JSON array:
[
    {{
        "line_number": 42,
        "severity": "high",
        "category": "security",
        "message": "SQL injection vulnerability",
        "suggestion": "Use parameterized queries"
    }}
]

Return empty array [] if no issues found."""

            try:
                response = await self.complete(
                    ANALYSIS_SYSTEM_PROMPT,
                    prompt,
                    temperature=0.3,  # Lower temperature for more consistent results
                )

                data = self._extract_json(response)
                if isinstance(data, list):
                    for item in data:
                        issues.append(
                            CodeIssue(
                                file_path=path,
                                line_number=item.get("line_number"),
                                severity=Severity(item.get("severity", "medium")),
                                category=item.get("category", "quality"),
                                message=item.get("message", "Issue found"),
                                suggestion=item.get("suggestion"),
                            )
                        )
            except Exception:
                continue

        return issues

    async def _analyze_dependencies(
        self, dependency_file: str
    ) -> list[DependencyInfo]:
        """Analyze project dependencies."""
        prompt = f"""Analyze these Python dependencies:

{dependency_file}

For each dependency, provide:
- Is it outdated?
- Are there known vulnerabilities?

Return as JSON array:
[
    {{
        "name": "package-name",
        "current_version": "1.0.0",
        "latest_version": "2.0.0",
        "is_outdated": true,
        "has_vulnerabilities": false,
        "vulnerability_count": 0
    }}
]"""

        try:
            response = await self.complete(
                ANALYSIS_SYSTEM_PROMPT,
                prompt,
            )
            data = self._extract_json(response)
            if isinstance(data, list):
                return [DependencyInfo(**item) for item in data]
        except Exception:
            pass

        return []

    async def _generate_summary(
        self,
        repository_url: str,
        metrics: CodeMetrics,
        architecture: ArchitectureAssessment,
        issues: list[CodeIssue],
    ) -> str:
        """Generate a human-readable summary."""
        critical_issues = len([i for i in issues if i.severity == Severity.CRITICAL])
        high_issues = len([i for i in issues if i.severity == Severity.HIGH])

        prompt = f"""Write a 2-3 sentence technical summary for this repository analysis:

Repository: {repository_url}
Files: {metrics.total_files} ({metrics.python_files} Python)
Lines: {metrics.total_lines}
Test files: {metrics.test_files}

Architecture strengths: {', '.join(architecture.strengths[:3])}
Architecture weaknesses: {', '.join(architecture.weaknesses[:3])}

Issues found: {len(issues)} total ({critical_issues} critical, {high_issues} high)

Be concise and focus on the most important findings."""

        return await self.complete(
            "You are a technical writer. Be concise and factual.",
            prompt,
            temperature=0.5,
        )

    def _calculate_overall_score(
        self,
        metrics: CodeMetrics,
        architecture: ArchitectureAssessment,
        issues: list[CodeIssue],
        dependencies: list[DependencyInfo],
    ) -> float:
        """Calculate overall code quality score (0-100)."""
        score = 70.0  # Base score

        # Adjust for issues
        for issue in issues:
            if issue.severity == Severity.CRITICAL:
                score -= 10
            elif issue.severity == Severity.HIGH:
                score -= 5
            elif issue.severity == Severity.MEDIUM:
                score -= 2
            elif issue.severity == Severity.LOW:
                score -= 0.5

        # Adjust for architecture
        score += len(architecture.strengths) * 2
        score -= len(architecture.weaknesses) * 2

        # Adjust for tests
        if metrics.test_files > 0:
            score += 5

        # Adjust for dependencies
        vulnerable_deps = len([d for d in dependencies if d.has_vulnerabilities])
        score -= vulnerable_deps * 5

        return max(0, min(100, score))

    def _calculate_revival_feasibility(
        self,
        metrics: CodeMetrics,
        issues: list[CodeIssue],
        dependencies: list[DependencyInfo],
    ) -> float:
        """Calculate how feasible it is to revive this project (0-1)."""
        feasibility = 0.7  # Base feasibility

        # Critical issues make revival harder
        critical = len([i for i in issues if i.severity == Severity.CRITICAL])
        feasibility -= critical * 0.1

        # Tests make revival easier
        if metrics.test_files > 0:
            feasibility += 0.1

        # Vulnerable dependencies make revival harder
        vulnerable = len([d for d in dependencies if d.has_vulnerabilities])
        feasibility -= vulnerable * 0.05

        # Very large codebases are harder to revive
        if metrics.total_lines > 50000:
            feasibility -= 0.1
        elif metrics.total_lines < 5000:
            feasibility += 0.1

        return max(0, min(1, feasibility))

    def _prioritize_fixes(self, issues: list[CodeIssue]) -> list[str]:
        """Get prioritized list of fixes."""
        priority_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM]
        fixes = []

        for severity in priority_order:
            for issue in issues:
                if issue.severity == severity and len(fixes) < 5:
                    fix = f"[{severity.value.upper()}] {issue.file_path}: {issue.message}"
                    fixes.append(fix)

        return fixes

    def _identify_blockers(
        self,
        issues: list[CodeIssue],
        dependencies: list[DependencyInfo],
    ) -> list[str]:
        """Identify blockers for revival."""
        blockers = []

        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        for issue in critical_issues[:3]:
            blockers.append(f"Critical issue in {issue.file_path}: {issue.message}")

        vulnerable_deps = [d for d in dependencies if d.has_vulnerabilities]
        for dep in vulnerable_deps[:3]:
            blockers.append(f"Vulnerable dependency: {dep.name}")

        return blockers

    def _estimate_effort(self, issues: list[CodeIssue]) -> float:
        """Estimate effort in hours to fix issues."""
        effort = 0.0

        for issue in issues:
            if issue.severity == Severity.CRITICAL:
                effort += 4.0
            elif issue.severity == Severity.HIGH:
                effort += 2.0
            elif issue.severity == Severity.MEDIUM:
                effort += 1.0
            elif issue.severity == Severity.LOW:
                effort += 0.5

        return effort

    def _extract_json(self, text: str) -> dict | list:
        """Extract JSON from AI response."""
        # Try to find JSON in the response
        text = text.strip()

        # Look for JSON block
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        # Try to find array or object
        if text.startswith("[") or text.startswith("{"):
            return json.loads(text)

        # Try to extract from text
        for start_char, end_char in [("[", "]"), ("{", "}")]:
            start = text.find(start_char)
            end = text.rfind(end_char)
            if start != -1 and end != -1:
                return json.loads(text[start : end + 1])

        raise ValueError("No JSON found in response")

    def _get_total_tokens(self) -> int:
        """Get total tokens used."""
        return sum(
            op["details"].get("tokens", 0)
            for op in self._operation_log
            if op["operation"] == "completion"
        )

    def _get_total_cost(self) -> float:
        """Get total cost in USD."""
        return sum(
            op["details"].get("cost", 0)
            for op in self._operation_log
            if op["operation"] == "completion"
        )
