"""
FAQs Route
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from api.schema.faq_schema import (
    AddFAQsRequestSchema,
    AddFAQsResponseSchema,
    FetchFAQsResponseSchema,
    DeleteFAQsResponseSchema,
    DeleteFAQsRequestSchema,
)
from api.service.faq_service import faqs_service
from api.database.sql_database import sql_database
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.service.auth_service import auth_service
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


faqs_router = APIRouter(
    tags=["FAQs"],
    prefix="/faqs",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "3/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@faqs_router.post(
    "",
    response_model=AddFAQsResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def create_new_faq(
    request: CustomRequest,
    schema: AddFAQsRequestSchema,
) -> AddFAQsResponseSchema:
    """
    Add a new faq.
    """
    return await faqs_service.create_new_faq(
        request=request,
        schema=schema,
    )


@faqs_router.get(
    "",
    response_model=FetchFAQsResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit("3/second")
async def retrieve_all_faqs(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    page: int = Query(ge=1, le=50, default=1),
    limit: int = Query(ge=1, le=50, default=50),
) -> FetchFAQsResponseSchema:
    """
    Retrieve all faqs
    """
    return await faqs_service.fetch_all_faqs(
        page=page, request=request, limit=limit, session=session
    )


@faqs_router.patch(
    "",
    response_model=DeleteFAQsResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def remove_new_faq(
    request: CustomRequest,
    schema: DeleteFAQsRequestSchema,
) -> DeleteFAQsResponseSchema:
    """
    Removes an faq.
    """
    return await faqs_service.delete_faqs(
        request=request,
        schema=schema,
    )
