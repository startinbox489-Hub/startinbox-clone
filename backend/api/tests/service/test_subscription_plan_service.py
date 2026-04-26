"""
Test sub plan service
"""

import pytest
from api.service.subscription_plan_service import (
    subscription_plan_service as sub_service,
    SubscriptionPlansResponseSchema,
)
from api.tests.service import seed_sub


class TestSubscriptionPlanService:
    """
    Test sub plan Service
    """

    @pytest.mark.asyncio
    async def test_fetch_plans(self, async_db_session):
        """
        Test fetch subscription plan
        """
        _, _ = await seed_sub()

        plans = await sub_service.fetch_subscription_plans(async_db_session, 1, 50)

        assert plans is not None

        assert isinstance(plans, SubscriptionPlansResponseSchema)
