"""
News letter Route
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from api.schema.news_letter_schema import (
    NewsLetterRequestSchema,
    UnSubNewsLetterResponseSchema,
    NewsLetterResponseSchema,
    UnSubNewsLetterRequestSchema,
)
from api.service.news_letter_service import news_letter_service
from api.database.sql_database import sql_database
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


news_letter_router = APIRouter(
    tags=["NEWS LETTER"],
    prefix="/news-letter",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "3/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@news_letter_router.post(
    "",
    response_model=NewsLetterResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def subscribe_to_news_letter(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    schema: NewsLetterRequestSchema,
    background_tasks: BackgroundTasks,
) -> NewsLetterResponseSchema:
    """
    Subscribes users to news letters
    """
    return await news_letter_service.sub_to_news_letter(
        session=session,
        schema=schema,
        background_tasks=background_tasks,
    )


@news_letter_router.patch(
    "",
    response_model=UnSubNewsLetterResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def unsubscribe_from_news_letter(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    schema: UnSubNewsLetterRequestSchema,
) -> UnSubNewsLetterResponseSchema:
    """
    Unsubscribes users from news letters
    """
    return await news_letter_service.unsub_to_news_letter(
        session=session,
        schema=schema,
    )
