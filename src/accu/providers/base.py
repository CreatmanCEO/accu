"""Base classes for AI providers."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""

    role: str  # "system", "user", "assistant"
    content: str


class TokenUsage(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Cost(BaseModel):
    """Cost breakdown in USD."""

    input_cost: float
    output_cost: float
    total_cost: float


class CompletionRequest(BaseModel):
    """Request for AI completion."""

    messages: list[Message]
    model: str | None = None  # Override default model
    max_tokens: int = 4096
    temperature: float = 0.7
    stop: list[str] | None = None
    stream: bool = False


class CompletionResponse(BaseModel):
    """Response from AI completion."""

    content: str
    model: str
    usage: TokenUsage
    cost: Cost
    latency_ms: int
    provider: str
    request_id: str | None = None


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(self, message: str, provider: str, retryable: bool = False):
        self.message = message
        self.provider = provider
        self.retryable = retryable
        super().__init__(message)


class RateLimitError(ProviderError):
    """Rate limit exceeded."""

    def __init__(self, provider: str, retry_after: int | None = None):
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded, retry after {retry_after}s",
            provider,
            retryable=True,
        )


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send completion request and return response."""
        pass

    @abstractmethod
    async def complete_stream(
        self, request: CompletionRequest
    ) -> AsyncIterator[str]:
        """Stream completion response."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier."""
        pass

    @abstractmethod
    def get_model_pricing(self, model: str) -> dict[str, float]:
        """Get pricing for a model (per 1M tokens)."""
        pass
