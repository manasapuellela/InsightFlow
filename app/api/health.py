from fastapi import APIRouter

from app.schemas.health import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
def healthcheck() -> HealthStatus:
    return HealthStatus(status="ok")
