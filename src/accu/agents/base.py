"""Base class for all ACCU agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from accu.providers import CompletionRequest, Message, ProviderManager


class AgentStatus(str, Enum):
    """Agent execution status."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentResult:
    """Result of agent execution."""

    success: bool
    data: Any
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    tokens_used: int = 0
    cost_usd: float = 0.0


class AgentConfig(BaseModel):
    """Base configuration for agents."""

    name: str
    version: str = "0.1.0"
    model: str = "anthropic/claude-3-haiku"
    max_tokens: int = 4096
    temperature: float = 0.7


class BaseAgent(ABC):
    """Abstract base class for all ACCU agents.

    All agents follow these principles:
    - Specialized for a single purpose
    - Operate under explicit constraints
    - Require human approval for significant actions
    - Track all operations for transparency
    """

    def __init__(
        self,
        config: AgentConfig,
        provider_manager: ProviderManager,
    ):
        self.config = config
        self.ai = provider_manager
        self.status = AgentStatus.IDLE
        self._operation_log: list[dict] = []

    @property
    @abstractmethod
    def purpose(self) -> str:
        """One-line description of agent's purpose."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        """List of things this agent CAN do."""
        pass

    @property
    @abstractmethod
    def restrictions(self) -> list[str]:
        """List of things this agent CANNOT do."""
        pass

    @abstractmethod
    async def run(self, **kwargs) -> AgentResult:
        """Execute the agent's main task."""
        pass

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs,
    ) -> str:
        """Send a completion request through the provider manager."""
        request = CompletionRequest(
            messages=[
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_prompt),
            ],
            model=kwargs.get("model", self.config.model),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
        )

        response = await self.ai.complete(request)

        # Log operation
        self._log_operation(
            "completion",
            {
                "model": response.model,
                "tokens": response.usage.total_tokens,
                "cost": response.cost.total_cost,
                "latency_ms": response.latency_ms,
            },
        )

        return response.content

    def _log_operation(self, operation: str, details: dict) -> None:
        """Log an operation for transparency."""
        self._operation_log.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "details": details,
            }
        )

    def get_operation_log(self) -> list[dict]:
        """Get the operation log."""
        return self._operation_log.copy()

    def get_stats(self) -> dict:
        """Get agent statistics."""
        total_tokens = sum(
            op["details"].get("tokens", 0)
            for op in self._operation_log
            if op["operation"] == "completion"
        )
        total_cost = sum(
            op["details"].get("cost", 0)
            for op in self._operation_log
            if op["operation"] == "completion"
        )

        return {
            "name": self.config.name,
            "version": self.config.version,
            "status": self.status.value,
            "operations_count": len(self._operation_log),
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
        }
