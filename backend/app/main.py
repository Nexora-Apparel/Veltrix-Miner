from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.market import router as market_router
from app.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    application = FastAPI(
        title=active_settings.app_name,
        version=active_settings.app_version,
        description="Non-custodial mining intelligence and operations API.",
    )

    # Cross-origin browser access is disabled unless one exact console origin is configured.
    if active_settings.web_origin:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[active_settings.web_origin],
            allow_credentials=False,
            allow_methods=["GET"],
            allow_headers=["Accept"],
            max_age=300,
        )

    application.include_router(health_router, prefix="/api/v1")
    application.include_router(market_router, prefix="/api/v1")

    @application.get("/", tags=["service"])
    def service_root() -> dict[str, str]:
        return {
            "service": active_settings.app_name,
            "version": active_settings.app_version,
            "docs": "/docs",
            "health": "/api/v1/health/live",
        }

    return application


app = create_app()
