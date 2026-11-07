from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Non-custodial mining intelligence and operations API.",
)

app.include_router(health_router, prefix="/api/v1")


@app.get("/", tags=["service"])
def service_root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health/live",
    }
