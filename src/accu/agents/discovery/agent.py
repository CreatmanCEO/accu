"""Discovery Agent implementation."""

import uuid
from datetime import datetime

from accu.agents.base import AgentResult, AgentStatus, BaseAgent
from accu.agents.discovery.models import (
    DiscoveryCandidate,
    DiscoveryConfig,
    DiscoveryRunResult,
)
from accu.agents.discovery.scanner import GitHubScanner
from accu.agents.discovery.analyzer import RepositoryAnalyzer
from accu.agents.discovery.scorer import RepositoryScorer
from accu.providers import ProviderManager


class DiscoveryAgent(BaseAgent):
    """Agent for discovering undervalued open-source repositories.

    This agent:
    - Searches GitHub for potentially valuable abandoned repositories
    - Analyzes code quality and documentation
    - Calculates potential scores for each candidate
    - Stores results for human review

    This agent does NOT:
    - Automatically onboard any repository
    - Contact repository authors
    - Make decisions based solely on popularity
    - Commit or modify any external code
    """

    def __init__(
        self,
        config: DiscoveryConfig,
        provider_manager: ProviderManager,
        github_token: str,
    ):
        super().__init__(config, provider_manager)
        self.config: DiscoveryConfig = config
        self.scanner = GitHubScanner(github_token)
        self.analyzer = RepositoryAnalyzer(provider_manager, config)
        self.scorer = RepositoryScorer()

    @property
    def purpose(self) -> str:
        return "Identify undervalued or abandoned repositories with high latent potential"

    @property
    def capabilities(self) -> list[str]:
        return [
            "Search GitHub for repositories matching criteria",
            "Analyze repository metadata and activity patterns",
            "Assess code quality and documentation",
            "Calculate potential scores",
            "Store candidates for human review",
        ]

    @property
    def restrictions(self) -> list[str]:
        return [
            "Cannot onboard projects automatically",
            "Cannot contact repository authors",
            "Cannot prioritize based on popularity alone",
            "Cannot commit or modify any external repositories",
            "Cannot make final decisions on project selection",
        ]

    async def run(
        self,
        strategy: str | None = None,
        max_repos: int | None = None,
    ) -> AgentResult:
        """Execute a discovery run.

        Args:
            strategy: Specific search strategy to use (optional)
            max_repos: Maximum repositories to process (optional)

        Returns:
            AgentResult with DiscoveryRunResult data
        """
        self.status = AgentStatus.RUNNING
        run_id = str(uuid.uuid4())
        started_at = datetime.utcnow()

        result = DiscoveryRunResult(
            run_id=run_id,
            started_at=started_at,
            config=self.config,
        )

        try:
            # Determine strategies to use
            strategies = (
                [strategy] if strategy else [s.value for s in self.config.strategies]
            )
            max_repos = max_repos or self.config.max_repos_per_run

            candidates: list[DiscoveryCandidate] = []

            for strat in strategies:
                self._log_operation("search_start", {"strategy": strat})

                # Search for repositories
                repos = await self.scanner.search(
                    strategy=strat,
                    languages=self.config.languages,
                    min_stars=self.config.min_stars,
                    max_stars=self.config.max_stars,
                    max_results=self.config.max_results_per_strategy,
                )

                result.repos_scanned += len(repos)

                # Analyze each repository
                for repo in repos:
                    if len(candidates) >= max_repos:
                        break

                    # Get detailed analysis
                    candidate = await self._process_repository(repo, strat, run_id)
                    if candidate and candidate.scores.potential >= 0.5:
                        candidates.append(candidate)

                self._log_operation(
                    "search_complete",
                    {"strategy": strat, "repos_found": len(repos)},
                )

            result.candidates = candidates
            result.candidates_found = len(candidates)
            result.completed_at = datetime.utcnow()
            result.status = "completed"

            self.status = AgentStatus.COMPLETED

            return AgentResult(
                success=True,
                data=result,
                started_at=started_at,
                completed_at=result.completed_at,
                tokens_used=self._get_total_tokens(),
                cost_usd=self._get_total_cost(),
            )

        except Exception as e:
            self.status = AgentStatus.FAILED
            result.status = "failed"
            result.error = str(e)
            result.completed_at = datetime.utcnow()

            return AgentResult(
                success=False,
                data=result,
                error=str(e),
                started_at=started_at,
                completed_at=result.completed_at,
            )

    async def _process_repository(
        self,
        repo: dict,
        strategy: str,
        run_id: str,
    ) -> DiscoveryCandidate | None:
        """Process a single repository and create a candidate."""
        try:
            # Get metrics
            metrics = await self.scanner.get_metrics(repo)

            # Get signals (including AI analysis)
            signals, ai_analysis = await self.analyzer.analyze(repo)

            # Calculate scores
            scores = self.scorer.calculate(metrics, signals)

            return DiscoveryCandidate(
                github_url=repo["html_url"],
                owner=repo["owner"]["login"],
                name=repo["name"],
                description=repo.get("description"),
                language=repo.get("language"),
                license=repo.get("license", {}).get("spdx_id") if repo.get("license") else None,
                created_at=repo.get("created_at"),
                pushed_at=repo.get("pushed_at"),
                topics=repo.get("topics", []),
                metrics=metrics,
                signals=signals,
                scores=scores,
                ai_analysis=ai_analysis,
                discovery_strategy=strategy,
                run_id=run_id,
            )

        except Exception as e:
            self._log_operation(
                "process_error",
                {"repo": repo.get("full_name"), "error": str(e)},
            )
            return None

    def _get_total_tokens(self) -> int:
        """Get total tokens used in this run."""
        return sum(
            op["details"].get("tokens", 0)
            for op in self._operation_log
            if op["operation"] == "completion"
        )

    def _get_total_cost(self) -> float:
        """Get total cost in USD for this run."""
        return sum(
            op["details"].get("cost", 0)
            for op in self._operation_log
            if op["operation"] == "completion"
        )
