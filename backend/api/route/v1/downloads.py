"""
Downloads Route
"""

from fastapi import APIRouter, Depends, status, BackgroundTasks
from slowapi import Limiter

from api.schema.startup_ideas_schema import (
    StartupIdeasRequestSchema,
    StartupIdeasResponseSchema,
)
from api.service.startup_ideas_service import startup_ideas_service
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.service.auth_service import auth_service
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


downloads_router = APIRouter(
    tags=["DOWNLOADS"],
    prefix="/downloads",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "50/minute"
PER_SECOND = "1/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@downloads_router.post(
    "",
    response_model=StartupIdeasResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def prompt_startup_idea(
    request: CustomRequest,
    schema: StartupIdeasRequestSchema,
    background_tasks: BackgroundTasks,
) -> StartupIdeasResponseSchema:
    """
    Prompt for a new startup idea.
    """
    return await startup_ideas_service.generate_startup_idea(
        request=request,
        schema=schema,
        background_tasks=background_tasks,
    )
