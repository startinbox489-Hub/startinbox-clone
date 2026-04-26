"""
Subscription Plan Route
"""

from typing import Annotated

from fastapi import APIRouter, Query, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from api.schema.subscription_plan_schema import (
    SubscriptionPlansResponseSchema,
    ActiveUserSubscriptionPlansResponseSchema,
)
from api.service.subscription_plan_service import subscription_plan_service
from api.database.sql_database import sql_database
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address
from api.service.auth_service import auth_service


sub_plan_router = APIRouter(
    tags=["SUBSCRIPTION PLANS"],
    prefix="/subscription-plans",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "5/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@sub_plan_router.get(
    "",
    response_model=SubscriptionPlansResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def retrieve_subscription_plans(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=50),
) -> SubscriptionPlansResponseSchema:
    """
    Retrieves all available subscription plans
    """
    return await subscription_plan_service.fetch_subscription_plans(
        session=session, page=page, limit=limit
    )


@sub_plan_router.get(
    "/active",
    response_model=ActiveUserSubscriptionPlansResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def retrieve_active_subscription_plans(
    request: CustomRequest,
):
    """
    Retrieves all active user subscribed plans
    """
    return await subscription_plan_service.fetch_with_plans(
        request=request,
    )
