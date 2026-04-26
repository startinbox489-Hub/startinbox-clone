"""
AddsOn Route
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from api.schema.adds_on_service_schema import (
    AddAddsOnRequestSchema,
    AddAddsOnResponseSchema,
    FetchAddsOnResponseSchema,
    DeleteAddsOnResponseSchema,
    DeleteAddsOnRequestSchema,
)
from api.service.adds_on_service import adds_on_service
from api.database.sql_database import sql_database
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.service.auth_service import auth_service
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


adds_on_router = APIRouter(
    tags=["ADDS ON SERVICES"],
    prefix="/adds-on-services",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "10/minute"
PER_SECOND = "3/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"

SESSION_DI = Annotated[AsyncSession, Depends(sql_database.get_db_with_tx)]


@adds_on_router.post(
    "",
    response_model=AddAddsOnResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def create_new_add_on(
    request: CustomRequest,
    schema: AddAddsOnRequestSchema,
    session: SESSION_DI,
) -> AddAddsOnResponseSchema:
    """
    Add a new add on.
    """
    return await adds_on_service.create_new_adds_on(
        request=request,
        schema=schema,
        session=session,
    )


@adds_on_router.get(
    "",
    response_model=FetchAddsOnResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit("3/second")
async def retrieve_all_adds_on(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    page: int = Query(ge=1, le=50, default=1),
    limit: int = Query(ge=1, le=50, default=50),
) -> FetchAddsOnResponseSchema:
    """
    Retrieve all AddsOn
    """
    return await adds_on_service.fetch_all_adds_on(
        page=page, request=request, limit=limit, session=session
    )


@adds_on_router.patch(
    "",
    response_model=DeleteAddsOnResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def remove_new_faq(
    request: CustomRequest,
    schema: DeleteAddsOnRequestSchema,
    session: SESSION_DI,
) -> DeleteAddsOnResponseSchema:
    """
    Removes an add on.
    """
    return await adds_on_service.delete_adds_on(
        request=request,
        schema=schema,
        session=session,
    )
