"""
Startup Ideas Route
"""

from fastapi import APIRouter, Depends, status, Query, Path, BackgroundTasks
from slowapi import Limiter

from api.schema.startup_ideas_schema import (
    StartupIdeasRequestSchema,
    StartupIdeasResponseSchema,
    FetchStartupIdeasResponseSchema,
    FetchStartupIdeaResponseSchema,
)
from api.service.startup_ideas_service import startup_ideas_service
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.service.auth_service import auth_service
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


startup_ideas = APIRouter(
    tags=["STARTUP IDEAS"],
    prefix="/startup-ideas",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "2/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@startup_ideas.post(
    "",
    response_model=StartupIdeasResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard)],
)
@limiter.limit("10/minute")
@limiter.limit("3/second")
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


@startup_ideas.get(
    "",
    response_model=FetchStartupIdeasResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_guard)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def retrieve_all_startup_ideas(
    request: CustomRequest,
    page: int = Query(ge=1, le=50, default=1),
    limit: int = Query(ge=1, le=50, default=50),
) -> FetchStartupIdeasResponseSchema:
    """
    Retrieve all prompted startup ideas
    """
    return await startup_ideas_service.fetch_all_startup_ideas(
        page=page,
        request=request,
        limit=limit,
    )


@startup_ideas.get(
    "/{startup_idea_id}",
    response_model=FetchStartupIdeaResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_guard)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def retrieve_a_startup_idea(
    request: CustomRequest,
    startup_idea_id: str = Path(),
) -> FetchStartupIdeaResponseSchema:
    """
    Retrieve a prompted startup idea
    """
    return await startup_ideas_service.fetch_a_startup_idea(
        startup_idea_id=startup_idea_id,
        request=request,
    )
