"""
Health ROute
"""

from fastapi import APIRouter, status
from slowapi import Limiter

from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "5/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"

health_router = APIRouter(prefix="/healthz", tags=["HEALTH"])


@health_router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def ping(request: CustomRequest) -> dict:
    """
    Pings API for health
    """
    return {"status": "Alive"}
