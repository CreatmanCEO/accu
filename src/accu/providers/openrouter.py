"""OpenRouter AI provider implementation."""

import os
import time
from typing import AsyncIterator

import httpx

from accu.providers.base import (
    AIProvider,
    CompletionRequest,
    CompletionResponse,
    Cost,
    ProviderError,
    RateLimitError,
    TokenUsage,
)


class OpenRouterProvider(AIProvider):
    """OpenRouter provider implementation.

    OpenRouter provides access to multiple AI models through a single API.
    https://openrouter.ai/docs
    """

    # Pricing per 1M tokens (as of 2024)
    PRICING: dict[str, dict[str, float]] = {
        # Anthropic models
        "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
        "anthropic/claude-3-5-haiku": {"input": 1.0, "output": 5.0},
        "anthropic/claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
        "anthropic/claude-3-opus": {"input": 15.0, "output": 75.0},
        # OpenAI models
        "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "openai/gpt-4o": {"input": 2.50, "output": 10.0},
        "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
        # Google models
        "google/gemini-pro": {"input": 0.125, "output": 0.375},
        "google/gemini-pro-1.5": {"input": 1.25, "output": 5.0},
        # Meta models
        "meta-llama/llama-3-70b-instruct": {"input": 0.59, "output": 0.79},
        # Mistral models
        "mistralai/mistral-7b-instruct": {"input": 0.06, "output": 0.06},
        "mistralai/mixtral-8x7b-instruct": {"input": 0.24, "output": 0.24},
    }

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "anthropic/claude-3-haiku",
        timeout: float = 30.0,
        app_name: str = "ACCU",
        app_url: str = "https://github.com/CreatmanCEO/accu",
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = base_url
        self.default_model = default_model
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": app_url,
                "X-Title": app_name,
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send completion request to OpenRouter."""
        model = request.model or self.default_model
        start_time = time.time()

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "stop": request.stop,
                    "stream": False,
                },
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(self.name, retry_after)

            response.raise_for_status()
            data = response.json()

        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"HTTP error: {e.response.status_code}",
                self.name,
                retryable=e.response.status_code >= 500,
            )
        except httpx.RequestError as e:
            raise ProviderError(f"Request error: {e}", self.name, retryable=True)

        # Parse response
        usage = TokenUsage(
            prompt_tokens=data["usage"]["prompt_tokens"],
            completion_tokens=data["usage"]["completion_tokens"],
            total_tokens=data["usage"]["total_tokens"],
        )

        cost = self._calculate_cost(model, usage)
        latency_ms = int((time.time() - start_time) * 1000)

        return CompletionResponse(
            content=data["choices"][0]["message"]["content"],
            model=model,
            usage=usage,
            cost=cost,
            latency_ms=latency_ms,
            provider=self.name,
            request_id=data.get("id"),
        )

    async def complete_stream(
        self, request: CompletionRequest
    ) -> AsyncIterator[str]:
        """Stream completion response from OpenRouter."""
        model = request.model or self.default_model

        async with self.client.stream(
            "POST",
            "/chat/completions",
            json={
                "model": model,
                "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stop": request.stop,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    import json
                    chunk = json.loads(data)
                    if content := chunk["choices"][0]["delta"].get("content"):
                        yield content

    async def health_check(self) -> bool:
        """Check if OpenRouter is available."""
        try:
            response = await self.client.get("/models")
            return response.status_code == 200
        except Exception:
            return False

    @property
    def name(self) -> str:
        return "openrouter"

    def get_model_pricing(self, model: str) -> dict[str, float]:
        """Get pricing for a model."""
        return self.PRICING.get(model, {"input": 0, "output": 0})

    def _calculate_cost(self, model: str, usage: TokenUsage) -> Cost:
        """Calculate cost for a completion."""
        pricing = self.get_model_pricing(model)
        input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
        return Cost(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "OpenRouterProvider":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
