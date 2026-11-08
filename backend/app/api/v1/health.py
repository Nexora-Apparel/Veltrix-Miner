from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.core.database import check_database_connection
from app.schemas.health import LivenessResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=LivenessResponse)
def liveness() -> LivenessResponse:
    settings = get_settings()
    return LivenessResponse(
        status="alive",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness() -> ReadinessResponse:
    settings = get_settings()
    if not settings.database_url:
        database_status = "not_configured"
    elif check_database_connection():
        database_status = "connected"
    else:
        database_status = "unavailable"

    if database_status != "connected":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "service": settings.app_name,
                "version": settings.app_version,
                "database": database_status,
            },
        )

    return ReadinessResponse(
        status="ready",
        service=settings.app_name,
        version=settings.app_version,
        database=database_status,
    )
