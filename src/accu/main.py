"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from accu.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"Starting ACCU v{__import__('accu').__version__}")
    print(f"Environment: {settings.environment}")
    yield
    # Shutdown
    print("Shutting down ACCU")


app = FastAPI(
    title="ACCU API",
    description="AI-Curated Code Universe — API for discovering and reviving open-source projects",
    version=__import__("accu").__version__,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ACCU API",
        "version": __import__("accu").__version__,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from accu.api.discovery import router as discovery_router

app.include_router(discovery_router, prefix="/api/v1/discovery", tags=["discovery"])
