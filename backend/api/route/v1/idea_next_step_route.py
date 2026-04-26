"""
Idea Next Step Route
"""

from fastapi import APIRouter, Depends, status, BackgroundTasks
from slowapi import Limiter

from api.schema.idea_next_step_schema import (
    AddIdeaNextStepRequestSchema,
    AddIdeaNextStepResponseSchema,
)
from api.service.idea_next_step_service import idea_next_step_service
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.service.auth_service import auth_service
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


idea_next_step_router = APIRouter(
    tags=["IDEA NEXT STEP"],
    prefix="/idea-next-steps",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "3/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@idea_next_step_router.post(
    "",
    response_model=AddIdeaNextStepResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def create_new_next_step(
    request: CustomRequest,
    schema: AddIdeaNextStepRequestSchema,
    backgroung_task: BackgroundTasks,
) -> AddIdeaNextStepResponseSchema:
    """
    Add a new Idea next step.
    """
    return await idea_next_step_service.create_new_next_step(
        request=request,
        schema=schema,
        backgroung_task=backgroung_task,
    )
