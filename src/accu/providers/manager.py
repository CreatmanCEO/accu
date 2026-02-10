"""Provider manager with fallback support."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from accu.providers.base import (
    AIProvider,
    CompletionRequest,
    CompletionResponse,
    ProviderError,
)

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
    """Single usage record."""

    timestamp: datetime
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_cost: float
    latency_ms: int


@dataclass
class UsageStats:
    """Aggregated usage statistics."""

    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    by_provider: dict[str, int] = field(default_factory=dict)
    by_model: dict[str, int] = field(default_factory=dict)


class UsageTracker:
    """Track API usage and costs across providers."""

    def __init__(self):
        self.records: list[UsageRecord] = []

    def record(self, response: CompletionResponse) -> None:
        """Record a completion response."""
        self.records.append(
            UsageRecord(
                timestamp=datetime.utcnow(),
                provider=response.provider,
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_cost=response.cost.total_cost,
                latency_ms=response.latency_ms,
            )
        )

    def get_stats(self, since: datetime | None = None) -> UsageStats:
        """Get aggregated usage statistics."""
        records = self.records
        if since:
            records = [r for r in records if r.timestamp >= since]

        if not records:
            return UsageStats()

        by_provider: dict[str, int] = {}
        by_model: dict[str, int] = {}

        for r in records:
            by_provider[r.provider] = by_provider.get(r.provider, 0) + 1
            by_model[r.model] = by_model.get(r.model, 0) + 1

        return UsageStats(
            total_requests=len(records),
            total_tokens=sum(r.prompt_tokens + r.completion_tokens for r in records),
            total_cost=sum(r.total_cost for r in records),
            avg_latency_ms=sum(r.latency_ms for r in records) / len(records),
            by_provider=by_provider,
            by_model=by_model,
        )

    def get_daily_cost(self) -> float:
        """Get total cost for today."""
        today = datetime.utcnow().date()
        return sum(
            r.total_cost
            for r in self.records
            if r.timestamp.date() == today
        )


class AllProvidersFailedError(Exception):
    """All providers failed to complete the request."""

    pass


class ProviderManager:
    """Manages multiple providers with fallback support."""

    def __init__(
        self,
        primary: AIProvider,
        fallbacks: list[AIProvider] | None = None,
        daily_budget_usd: float = 50.0,
    ):
        self.primary = primary
        self.fallbacks = fallbacks or []
        self.daily_budget_usd = daily_budget_usd
        self.usage_tracker = UsageTracker()

    async def complete(
        self,
        request: CompletionRequest,
        prefer_cheap: bool = False,
    ) -> CompletionResponse:
        """
        Complete request with automatic fallback.

        Args:
            request: The completion request
            prefer_cheap: If True, use model optimized for cost

        Returns:
            CompletionResponse from successful provider

        Raises:
            AllProvidersFailedError: If all providers fail
        """
        # Check budget
        if self.usage_tracker.get_daily_cost() >= self.daily_budget_usd:
            raise AllProvidersFailedError(
                f"Daily budget of ${self.daily_budget_usd} exceeded"
            )

        providers = [self.primary] + self.fallbacks
        last_error: Exception | None = None

        for provider in providers:
            try:
                response = await provider.complete(request)
                self.usage_tracker.record(response)
                return response
            except ProviderError as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                last_error = e
                if not e.retryable:
                    continue
            except Exception as e:
                logger.error(f"Unexpected error from {provider.name}: {e}")
                last_error = e

        raise AllProvidersFailedError(
            f"All providers failed. Last error: {last_error}"
        )

    def get_usage_stats(self, since: datetime | None = None) -> UsageStats:
        """Get cumulative usage statistics."""
        return self.usage_tracker.get_stats(since)

    def get_daily_cost(self) -> float:
        """Get today's total cost."""
        return self.usage_tracker.get_daily_cost()

    def get_budget_remaining(self) -> float:
        """Get remaining daily budget."""
        return max(0, self.daily_budget_usd - self.get_daily_cost())
