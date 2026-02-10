"""Scoring algorithm for Discovery Agent."""

from accu.agents.discovery.models import (
    RepositoryMetrics,
    RepositoryScores,
    RepositorySignals,
)


class RepositoryScorer:
    """Calculates potential scores for repositories.

    The scoring algorithm evaluates repositories based on:
    - Code quality (from AI analysis)
    - Uniqueness (inverse of similar repos)
    - Completeness (presence of docs, tests, license, etc.)
    - Revival effort (estimated work needed)

    Scores are normalized to 0-1 range.
    """

    def __init__(
        self,
        weight_quality: float = 0.30,
        weight_uniqueness: float = 0.25,
        weight_completeness: float = 0.25,
        weight_effort: float = 0.20,
    ):
        self.weight_quality = weight_quality
        self.weight_uniqueness = weight_uniqueness
        self.weight_completeness = weight_completeness
        self.weight_effort = weight_effort

    def calculate(
        self,
        metrics: RepositoryMetrics,
        signals: RepositorySignals,
    ) -> RepositoryScores:
        """Calculate all scores for a repository.

        Args:
            metrics: Repository metrics
            signals: Repository signals

        Returns:
            RepositoryScores with potential, revival_feasibility, and product_fit
        """
        potential = self._calculate_potential(metrics, signals)
        revival_feasibility = self._calculate_revival_feasibility(metrics, signals)
        product_fit = self._calculate_product_fit(metrics, signals)

        return RepositoryScores(
            potential=potential,
            revival_feasibility=revival_feasibility,
            product_fit=product_fit,
        )

    def _calculate_potential(
        self,
        metrics: RepositoryMetrics,
        signals: RepositorySignals,
    ) -> float:
        """Calculate overall potential score.

        potential = w1*quality + w2*uniqueness + w3*completeness + w4*effort_inverse
        """
        quality = signals.code_quality_estimate
        uniqueness = self._estimate_uniqueness(metrics)
        completeness = self._calculate_completeness(signals)
        effort_inverse = self._calculate_effort_inverse(metrics, signals)

        potential = (
            self.weight_quality * quality
            + self.weight_uniqueness * uniqueness
            + self.weight_completeness * completeness
            + self.weight_effort * effort_inverse
        )

        return min(1.0, max(0.0, potential))

    def _calculate_revival_feasibility(
        self,
        metrics: RepositoryMetrics,
        signals: RepositorySignals,
    ) -> float:
        """Calculate how feasible it is to revive this project.

        Factors:
        - Recent activity (easier if not too stale)
        - Documentation (easier if well-documented)
        - Tests (easier if tested)
        - Contributors (easier if community exists)
        """
        # Staleness penalty (0-1, where 1 = recently active)
        days = metrics.days_since_last_commit
        staleness = max(0, 1 - (days / 1095))  # 3 years = 0

        # Documentation factor
        doc_factor = signals.documentation_quality

        # Test factor
        test_factor = 0.7 if signals.has_tests else 0.3

        # Community factor
        contrib_factor = min(1.0, metrics.contributors_count / 5)

        feasibility = (
            0.25 * staleness
            + 0.30 * doc_factor
            + 0.25 * test_factor
            + 0.20 * contrib_factor
        )

        return min(1.0, max(0.0, feasibility))

    def _calculate_product_fit(
        self,
        metrics: RepositoryMetrics,
        signals: RepositorySignals,
    ) -> float:
        """Calculate product-market fit potential.

        Factors:
        - Star count (indicates interest)
        - Fork count (indicates usage)
        - Issue engagement (indicates need)
        """
        # Normalize stars (sweet spot: 20-200 stars)
        stars = metrics.stars
        if stars < 20:
            star_score = stars / 20
        elif stars <= 200:
            star_score = 1.0
        else:
            star_score = max(0.5, 1 - (stars - 200) / 1000)

        # Fork ratio (forks / stars indicates adoption)
        fork_ratio = metrics.forks / max(1, metrics.stars)
        fork_score = min(1.0, fork_ratio * 5)  # 20% fork ratio = 1.0

        # Issue engagement (open issues indicate active need)
        issue_score = min(1.0, metrics.open_issues / 20)

        product_fit = (
            0.40 * star_score
            + 0.35 * fork_score
            + 0.25 * issue_score
        )

        return min(1.0, max(0.0, product_fit))

    def _estimate_uniqueness(self, metrics: RepositoryMetrics) -> float:
        """Estimate project uniqueness.

        Lower star count often correlates with more unique/niche projects.
        """
        stars = metrics.stars
        if stars < 20:
            return 0.9  # Very niche
        elif stars < 50:
            return 0.8
        elif stars < 100:
            return 0.7
        elif stars < 200:
            return 0.6
        else:
            return 0.5

    def _calculate_completeness(self, signals: RepositorySignals) -> float:
        """Calculate project completeness score."""
        factors = [
            signals.has_readme,
            signals.has_license,
            signals.has_tests,
            signals.has_ci,
            signals.has_documentation,
        ]

        return sum(factors) / len(factors)

    def _calculate_effort_inverse(
        self,
        metrics: RepositoryMetrics,
        signals: RepositorySignals,
    ) -> float:
        """Calculate inverse of estimated revival effort.

        Higher score = less effort needed = more attractive.
        """
        # Base effort from code quality
        base_effort = 1 - signals.code_quality_estimate

        # Increase effort if no tests
        if not signals.has_tests:
            base_effort += 0.2

        # Increase effort if poor documentation
        base_effort += (1 - signals.documentation_quality) * 0.15

        # Increase effort if very stale
        if metrics.days_since_last_commit > 730:  # 2 years
            base_effort += 0.15

        # Invert for score (less effort = higher score)
        return max(0.0, min(1.0, 1 - base_effort))
