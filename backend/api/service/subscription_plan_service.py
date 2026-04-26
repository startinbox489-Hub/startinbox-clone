"""
Subscription Plan Service
"""

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.repository.subscription_plan_repo import subscription_plan_repo
from api.repository.subscription_plan_features_repo import (
    subscription_plan_feature_repo,
)
from api.schema.subscription_plan_schema import (
    SubscriptionPlanBase,
    SubscriptionPlansResponseSchema,
    ActiveUserSubscriptionPlan,
    ActiveUserSubscriptionPlansResponseSchema,
)
from api.utils.task_logger import create_logger
from api.schema.default_response_schema import CustomRequest
from api.utils.get_session_claims_from_request import get_claims_and_session
from api.repository.user_subscription_repo import user_subscription_repo

logger = create_logger(":: SubscriptionPlanService ::")


class SubscriptionPlanService:
    """
    Subscription Plan Service
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.repo = subscription_plan_repo
        self.feature_repo = subscription_plan_feature_repo

    async def fetch_subscription_plans(
        self, session: AsyncSession, page: int, limit: int
    ) -> SubscriptionPlansResponseSchema:
        """
        Retrieves all subscription plans with associated features.

        Args:
            session (AsyncSession): The database injected async session object.
            page (int): The current page for the subscription plans.
            limit (int): The number of plans to be retrieved per page.
        Returns:
            Something
        """
        try:
            plans = await self.repo.fetch_all(
                session,
                limit=limit,
                offset=(limit * page - limit),
                include_features=True,
            )

            return SubscriptionPlansResponseSchema(
                data=[
                    SubscriptionPlanBase.model_validate(plan, from_attributes=True)
                    for plan in plans
                ]
            )
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error(msg=str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def fetch_with_plans(
        self,
        request: CustomRequest,
    ) -> ActiveUserSubscriptionPlansResponseSchema:
        """
        fetch with plans
        """
        try:
            session, claims = get_claims_and_session(request)
            plans = await user_subscription_repo.fetch_with_plans(
                session=session, user_id=claims.user_id
            )
            return ActiveUserSubscriptionPlansResponseSchema(
                data=[
                    ActiveUserSubscriptionPlan.model_validate(
                        plan, from_attributes=True
                    )
                    for plan in plans
                ]
            )
        except HTTPException as exc:
            raise exc
        except Exception as exc:
            logger.error(msg=str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc


subscription_plan_service = SubscriptionPlanService()
