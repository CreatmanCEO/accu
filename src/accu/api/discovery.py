"""Discovery Agent API endpoints."""

import uuid
from datetime import datetime
from typing import Protocol

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from accu.agents.discovery import (
    DiscoveryCandidate,
    DiscoveryConfig,
    DiscoveryRunResult,
    CandidateStatus,
    SearchStrategy,
)


# =============================================================================
# Storage Protocol (for easy swap to database later)
# =============================================================================


class DiscoveryStorage(Protocol):
    """Protocol for discovery data storage."""

    def get_run(self, run_id: str) -> DiscoveryRunResult | None: ...
    def list_runs(
        self, skip: int, limit: int, status: str | None
    ) -> list[DiscoveryRunResult]: ...
    def save_run(self, run: DiscoveryRunResult) -> None: ...
    def update_run(self, run: DiscoveryRunResult) -> None: ...
    def get_candidate(self, candidate_id: str) -> DiscoveryCandidate | None: ...
    def list_candidates(
        self,
        skip: int,
        limit: int,
        status: CandidateStatus | None,
        min_potential: float | None,
    ) -> list[DiscoveryCandidate]: ...
    def save_candidate(self, candidate: DiscoveryCandidate) -> None: ...
    def update_candidate(self, candidate: DiscoveryCandidate) -> None: ...


# =============================================================================
# In-Memory Storage Implementation
# =============================================================================


class InMemoryDiscoveryStorage:
    """In-memory storage for discovery data.

    Easy to swap for PostgreSQL later by implementing DiscoveryStorage protocol.
    """

    def __init__(self):
        self._runs: dict[str, DiscoveryRunResult] = {}
        self._candidates: dict[str, DiscoveryCandidate] = {}

    def get_run(self, run_id: str) -> DiscoveryRunResult | None:
        return self._runs.get(run_id)

    def list_runs(
        self, skip: int = 0, limit: int = 20, status: str | None = None
    ) -> list[DiscoveryRunResult]:
        runs = list(self._runs.values())
        if status:
            runs = [r for r in runs if r.status == status]
        # Sort by started_at descending
        runs.sort(key=lambda r: r.started_at, reverse=True)
        return runs[skip : skip + limit]

    def save_run(self, run: DiscoveryRunResult) -> None:
        self._runs[run.run_id] = run

    def update_run(self, run: DiscoveryRunResult) -> None:
        self._runs[run.run_id] = run

    def get_candidate(self, candidate_id: str) -> DiscoveryCandidate | None:
        return self._candidates.get(candidate_id)

    def list_candidates(
        self,
        skip: int = 0,
        limit: int = 20,
        status: CandidateStatus | None = None,
        min_potential: float | None = None,
    ) -> list[DiscoveryCandidate]:
        candidates = list(self._candidates.values())
        if status:
            candidates = [c for c in candidates if c.status == status]
        if min_potential is not None:
            candidates = [c for c in candidates if c.scores.potential >= min_potential]
        # Sort by potential score descending
        candidates.sort(key=lambda c: c.scores.potential, reverse=True)
        return candidates[skip : skip + limit]

    def save_candidate(self, candidate: DiscoveryCandidate) -> None:
        # Generate ID from github_url if not present
        candidate_id = self._generate_candidate_id(candidate)
        self._candidates[candidate_id] = candidate

    def update_candidate(self, candidate: DiscoveryCandidate) -> None:
        candidate_id = self._generate_candidate_id(candidate)
        self._candidates[candidate_id] = candidate

    def _generate_candidate_id(self, candidate: DiscoveryCandidate) -> str:
        """Generate a stable ID from owner/name."""
        return f"{candidate.owner}/{candidate.name}"


# Global storage instance (will be replaced with dependency injection later)
_storage = InMemoryDiscoveryStorage()


def get_storage() -> InMemoryDiscoveryStorage:
    """Get storage instance (dependency for FastAPI)."""
    return _storage


# =============================================================================
# Request/Response Models
# =============================================================================


class DiscoveryRunRequest(BaseModel):
    """Request to start a discovery run."""

    strategy: SearchStrategy | None = Field(
        default=None, description="Specific strategy to use (optional)"
    )
    languages: list[str] | None = Field(
        default=None, description="Languages to search for (optional)"
    )
    min_stars: int | None = Field(
        default=None, ge=0, description="Minimum star count"
    )
    max_stars: int | None = Field(
        default=None, ge=0, description="Maximum star count"
    )
    max_repos: int | None = Field(
        default=None, ge=1, le=100, description="Maximum repos to process"
    )


class DiscoveryRunResponse(BaseModel):
    """Response for a discovery run."""

    run_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    repos_scanned: int = 0
    candidates_found: int = 0
    error: str | None = None
    message: str | None = None


class DiscoveryRunDetailResponse(DiscoveryRunResponse):
    """Detailed response including candidates."""

    candidates: list[DiscoveryCandidate] = Field(default_factory=list)
    config: DiscoveryConfig | None = None


class CandidateListResponse(BaseModel):
    """Response for listing candidates."""

    total: int
    skip: int
    limit: int
    candidates: list[DiscoveryCandidate]


class RunListResponse(BaseModel):
    """Response for listing runs."""

    total: int
    skip: int
    limit: int
    runs: list[DiscoveryRunResponse]


class CandidateUpdateRequest(BaseModel):
    """Request to update a candidate."""

    status: CandidateStatus | None = None
    reviewed_by: str | None = None
    notes: str | None = None


# =============================================================================
# Background Task Runner
# =============================================================================


async def execute_discovery_run(
    run_id: str,
    config: DiscoveryConfig,
    strategy: str | None,
    max_repos: int | None,
    storage: InMemoryDiscoveryStorage,
) -> None:
    """Execute a discovery run in the background.

    This function is called as a background task and updates the storage
    with results as they come in.
    """
    from accu.config import get_settings
    from accu.providers import ProviderManager
    from accu.providers.openrouter import OpenRouterProvider
    from accu.agents.discovery import DiscoveryAgent

    settings = get_settings()

    # Get the run to update
    run = storage.get_run(run_id)
    if not run:
        return

    try:
        # Initialize provider
        provider = OpenRouterProvider(
            api_key=settings.ai.openrouter_api_key,
        )
        provider_manager = ProviderManager(
            primary=provider,
            daily_budget_usd=settings.ai.daily_budget_usd,
        )

        # Initialize agent
        agent = DiscoveryAgent(
            config=config,
            provider_manager=provider_manager,
            github_token=settings.github.token,
        )

        # Run discovery
        result = await agent.run(strategy=strategy, max_repos=max_repos)

        # Update run with results
        if result.success and isinstance(result.data, DiscoveryRunResult):
            run_result = result.data
            run.status = run_result.status
            run.completed_at = run_result.completed_at
            run.repos_scanned = run_result.repos_scanned
            run.candidates_found = run_result.candidates_found
            run.candidates = run_result.candidates
            run.error = run_result.error

            # Save candidates individually
            for candidate in run_result.candidates:
                storage.save_candidate(candidate)
        else:
            run.status = "failed"
            run.error = result.error or "Unknown error"
            run.completed_at = datetime.utcnow()

        storage.update_run(run)

    except Exception as e:
        run.status = "failed"
        run.error = str(e)
        run.completed_at = datetime.utcnow()
        storage.update_run(run)


# =============================================================================
# Router Definition
# =============================================================================


router = APIRouter()


@router.post("/run", response_model=DiscoveryRunResponse)
async def trigger_discovery_run(
    request: DiscoveryRunRequest,
    background_tasks: BackgroundTasks,
    storage: InMemoryDiscoveryStorage = Depends(get_storage),
) -> DiscoveryRunResponse:
    """Trigger a new discovery run.

    This endpoint starts a discovery run in the background and returns
    immediately with the run ID. Use GET /runs/{run_id} to check status.
    """
    run_id = str(uuid.uuid4())
    started_at = datetime.utcnow()

    # Build config from request
    config = DiscoveryConfig()
    if request.languages:
        config.languages = request.languages
    if request.min_stars is not None:
        config.min_stars = request.min_stars
    if request.max_stars is not None:
        config.max_stars = request.max_stars
    if request.max_repos is not None:
        config.max_repos_per_run = request.max_repos
    if request.strategy:
        config.strategies = [request.strategy]

    # Create initial run record
    run = DiscoveryRunResult(
        run_id=run_id,
        started_at=started_at,
        status="running",
        strategy=request.strategy.value if request.strategy else None,
        config=config,
    )
    storage.save_run(run)

    # Schedule background task
    background_tasks.add_task(
        execute_discovery_run,
        run_id=run_id,
        config=config,
        strategy=request.strategy.value if request.strategy else None,
        max_repos=request.max_repos,
        storage=storage,
    )

    return DiscoveryRunResponse(
        run_id=run_id,
        status="running",
        started_at=started_at,
        message="Discovery run started. Check status with GET /runs/{run_id}",
    )


@router.get("/runs", response_model=RunListResponse)
async def list_discovery_runs(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of records to return"),
    status: str | None = Query(default=None, description="Filter by status"),
    storage: InMemoryDiscoveryStorage = Depends(get_storage),
) -> RunListResponse:
    """List all discovery runs.

    Returns paginated list of discovery runs, sorted by start time descending.
    """
    runs = storage.list_runs(skip=skip, limit=limit, status=status)
    all_runs = storage.list_runs(skip=0, limit=10000, status=status)

    return RunListResponse(
        total=len(all_runs),
        skip=skip,
        limit=limit,
        runs=[
            DiscoveryRunResponse(
                run_id=r.run_id,
                status=r.status,
                started_at=r.started_at,
                completed_at=r.completed_at,
                repos_scanned=r.repos_scanned,
                candidates_found=r.candidates_found,
                error=r.error,
            )
            for r in runs
        ],
    )


@router.get("/runs/{run_id}", response_model=DiscoveryRunDetailResponse)
async def get_discovery_run(
    run_id: str,
    storage: InMemoryDiscoveryStorage = Depends(get_storage),
) -> DiscoveryRunDetailResponse:
    """Get details of a specific discovery run.

    Returns the full run details including all discovered candidates.
    """
    run = storage.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    return DiscoveryRunDetailResponse(
        run_id=run.run_id,
        status=run.status,
        started_at=run.started_at,
        completed_at=run.completed_at,
        repos_scanned=run.repos_scanned,
        candidates_found=run.candidates_found,
        error=run.error,
        candidates=run.candidates,
        config=run.config,
    )


@router.get("/candidates", response_model=CandidateListResponse)
async def list_candidates(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of records to return"),
    status: CandidateStatus | None = Query(default=None, description="Filter by status"),
    min_potential: float | None = Query(
        default=None, ge=0.0, le=1.0, description="Minimum potential score"
    ),
    storage: InMemoryDiscoveryStorage = Depends(get_storage),
) -> CandidateListResponse:
    """List discovered candidates.

    Returns paginated list of candidates, sorted by potential score descending.
    """
    candidates = storage.list_candidates(
        skip=skip, limit=limit, status=status, min_potential=min_potential
    )
    all_candidates = storage.list_candidates(
        skip=0, limit=10000, status=status, min_potential=min_potential
    )

    return CandidateListResponse(
        total=len(all_candidates),
        skip=skip,
        limit=limit,
        candidates=candidates,
    )


@router.get("/candidates/{candidate_id:path}", response_model=DiscoveryCandidate)
async def get_candidate(
    candidate_id: str,
    storage: InMemoryDiscoveryStorage = Depends(get_storage),
) -> DiscoveryCandidate:
    """Get details of a specific candidate.

    The candidate_id is in the format "owner/repo" (e.g., "tibonihoo/yapsy").
    """
    candidate = storage.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    return candidate


@router.patch("/candidates/{candidate_id:path}", response_model=DiscoveryCandidate)
async def update_candidate(
    candidate_id: str,
    update: CandidateUpdateRequest,
    storage: InMemoryDiscoveryStorage = Depends(get_storage),
) -> DiscoveryCandidate:
    """Update a candidate's status or notes.

    Used for reviewing candidates and marking them as approved/rejected.
    """
    candidate = storage.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    # Update fields if provided
    if update.status is not None:
        candidate.status = update.status
    if update.reviewed_by is not None:
        candidate.reviewed_by = update.reviewed_by
        candidate.reviewed_at = datetime.utcnow()
    if update.notes is not None:
        candidate.notes = update.notes

    storage.update_candidate(candidate)
    return candidate
