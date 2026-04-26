"""
Startup Ideas Route
"""

from fastapi import APIRouter, status, Path, Query
from fastapi.responses import FileResponse
from slowapi import Limiter

from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.service.reports_service import reports_service
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


reports_router = APIRouter(
    tags=["IDEAS REPORTS"],
    prefix="/reports",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "50/minute"
PER_SECOND = "5/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@reports_router.get(
    "/{filename}",
    status_code=status.HTTP_200_OK,
    responses=responses,
    include_in_schema=False,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def get_report_file(
    request: CustomRequest,
    filename: str = Path(),
    token: str = Query(),
    expires: int | str = Query(),
) -> FileResponse:
    """
    Retrieve all prompted startup ideas
    """
    return reports_service.serve_file(filename=filename, token=token, expires=expires)
