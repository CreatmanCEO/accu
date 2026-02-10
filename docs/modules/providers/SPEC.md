# AI Provider Abstraction — Module Specification

**Version:** 0.1.0
**Status:** In Design
**Priority:** P0 (Required for all agents)

---

## Purpose

Provide a unified interface for interacting with different AI providers, allowing easy switching between models and cost optimization without changing agent code.

---

## Design Principles

1. **Provider Agnostic** — Agents don't know which provider they use
2. **Hot Swappable** — Change providers via configuration, no code changes
3. **Cost Aware** — Track token usage and costs per request
4. **Fallback Support** — Automatic failover to backup providers
5. **Rate Limit Handling** — Built-in rate limiting and queuing

---

## Supported Providers (MVP)

| Provider | Priority | Models |
|----------|----------|--------|
| OpenRouter | Primary | All models via single API |
| Anthropic Direct | Backup | Claude family |
| OpenAI Direct | Backup | GPT family |
| Local (Ollama) | Future | Open models |

---

## Interface

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator
from pydantic import BaseModel

class Message(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class CompletionRequest(BaseModel):
    messages: list[Message]
    model: str | None = None  # Override default model
    max_tokens: int = 4096
    temperature: float = 0.7
    stop: list[str] | None = None
    stream: bool = False

class CompletionResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage
    cost: Cost
    latency_ms: int
    provider: str

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Cost(BaseModel):
    input_cost: float  # USD
    output_cost: float  # USD
    total_cost: float  # USD

class AIProvider(ABC):
    """Base class for all AI providers."""

    @abstractmethod
    async def complete(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Send completion request and return response."""
        pass

    @abstractmethod
    async def complete_stream(
        self,
        request: CompletionRequest
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
```

---

## Provider Manager

```python
class ProviderManager:
    """Manages multiple providers with fallback support."""

    def __init__(self, config: ProviderConfig):
        self.primary = self._create_provider(config.primary)
        self.fallbacks = [
            self._create_provider(f) for f in config.fallbacks
        ]
        self.usage_tracker = UsageTracker()

    async def complete(
        self,
        request: CompletionRequest,
        prefer_cheap: bool = False
    ) -> CompletionResponse:
        """
        Complete request with automatic fallback.

        Args:
            request: The completion request
            prefer_cheap: If True, use cheapest available model
        """
        providers = self._get_provider_order(prefer_cheap)

        for provider in providers:
            try:
                response = await provider.complete(request)
                self.usage_tracker.record(response)
                return response
            except ProviderError as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                continue

        raise AllProvidersFailedError("No providers available")

    def get_usage_stats(self) -> UsageStats:
        """Get cumulative usage statistics."""
        return self.usage_tracker.get_stats()
```

---

## Configuration Schema

```yaml
providers:
  primary:
    type: "openrouter"
    api_key_env: "OPENROUTER_API_KEY"
    base_url: "https://openrouter.ai/api/v1"
    default_model: "anthropic/claude-3-haiku"
    timeout_seconds: 30
    max_retries: 3

  fallbacks:
    - type: "anthropic"
      api_key_env: "ANTHROPIC_API_KEY"
      default_model: "claude-3-haiku-20240307"

    - type: "openai"
      api_key_env: "OPENAI_API_KEY"
      default_model: "gpt-4o-mini"

  rate_limits:
    requests_per_minute: 60
    tokens_per_minute: 100000

  cost_tracking:
    enabled: true
    alert_threshold_usd: 10.0  # Alert when daily spend exceeds
    budget_limit_usd: 50.0     # Hard stop when exceeded

  model_aliases:
    cheap: "anthropic/claude-3-haiku"
    balanced: "anthropic/claude-3-5-sonnet"
    powerful: "anthropic/claude-3-opus"
```

---

## OpenRouter Implementation

```python
class OpenRouterProvider(AIProvider):
    """OpenRouter provider implementation."""

    PRICING = {
        "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},  # per 1M tokens
        "anthropic/claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
        "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
        # ... more models
    }

    def __init__(self, config: OpenRouterConfig):
        self.api_key = os.getenv(config.api_key_env)
        self.base_url = config.base_url
        self.default_model = config.default_model
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://accu.dev",
                "X-Title": "ACCU Discovery"
            },
            timeout=config.timeout_seconds
        )

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        model = request.model or self.default_model
        start_time = time.time()

        response = await self.client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": [m.model_dump() for m in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": False
            }
        )
        response.raise_for_status()
        data = response.json()

        usage = TokenUsage(
            prompt_tokens=data["usage"]["prompt_tokens"],
            completion_tokens=data["usage"]["completion_tokens"],
            total_tokens=data["usage"]["total_tokens"]
        )

        cost = self._calculate_cost(model, usage)
        latency = int((time.time() - start_time) * 1000)

        return CompletionResponse(
            content=data["choices"][0]["message"]["content"],
            model=model,
            usage=usage,
            cost=cost,
            latency_ms=latency,
            provider="openrouter"
        )

    def _calculate_cost(self, model: str, usage: TokenUsage) -> Cost:
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
        return Cost(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost
        )

    @property
    def name(self) -> str:
        return "openrouter"
```

---

## Usage Tracking

```python
class UsageTracker:
    """Track API usage and costs across providers."""

    def __init__(self):
        self.records: list[UsageRecord] = []

    def record(self, response: CompletionResponse):
        self.records.append(UsageRecord(
            timestamp=datetime.utcnow(),
            provider=response.provider,
            model=response.model,
            tokens=response.usage,
            cost=response.cost,
            latency_ms=response.latency_ms
        ))

    def get_stats(self, since: datetime = None) -> UsageStats:
        records = self.records
        if since:
            records = [r for r in records if r.timestamp >= since]

        return UsageStats(
            total_requests=len(records),
            total_tokens=sum(r.tokens.total_tokens for r in records),
            total_cost=sum(r.cost.total_cost for r in records),
            avg_latency_ms=mean(r.latency_ms for r in records) if records else 0,
            by_provider=self._group_by_provider(records),
            by_model=self._group_by_model(records)
        )
```

---

## Agent Integration Example

```python
from accu.providers import ProviderManager

class DiscoveryAgent:
    def __init__(self, provider_manager: ProviderManager):
        self.ai = provider_manager

    async def analyze_repository(self, repo_data: dict) -> Analysis:
        prompt = self._build_analysis_prompt(repo_data)

        # Use cheap model for bulk scanning
        response = await self.ai.complete(
            CompletionRequest(
                messages=[
                    Message(role="system", content=ANALYZER_SYSTEM_PROMPT),
                    Message(role="user", content=prompt)
                ],
                max_tokens=1000
            ),
            prefer_cheap=True  # Optimize for cost
        )

        return self._parse_analysis(response.content)
```

---

## Implementation Files

```
src/accu/providers/
├── __init__.py
├── base.py            # AIProvider ABC, models
├── manager.py         # ProviderManager
├── openrouter.py      # OpenRouter implementation
├── anthropic.py       # Anthropic direct
├── openai.py          # OpenAI direct
├── usage.py           # Usage tracking
└── config.py          # Configuration loading
```

---

## Testing

```python
# Mock provider for testing
class MockProvider(AIProvider):
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_count = 0

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return CompletionResponse(
            content=response,
            model="mock",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            cost=Cost(input_cost=0, output_cost=0, total_cost=0),
            latency_ms=1,
            provider="mock"
        )
```

---

## Environment Variables

```bash
# Required
OPENROUTER_API_KEY=sk-or-...

# Optional fallbacks
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Cost controls
AI_DAILY_BUDGET_USD=50
AI_ALERT_THRESHOLD_USD=10
```
