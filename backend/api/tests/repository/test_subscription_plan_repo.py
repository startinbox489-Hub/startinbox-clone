"""
Test sub plan repo
"""

from decimal import Decimal
from typing import Sequence

import pytest
from api.repository.subscription_plan_repo import subscription_plan_repo
from api.repository.subscription_plan_features_repo import (
    subscription_plan_feature_repo,
)
from api.model import SubscriptionPlanModel


class TestSubscriptionPlanRepo:
    """
    Test sub plan repo
    """

    @pytest.mark.asyncio
    async def test_a_create_plan(self, async_db_session):
        """
        Test create subscription plan
        """

        create_result = await subscription_plan_repo.create(
            async_db_session,
            {
                "name": "premium2",
                "price": Decimal("29.99"),
                "description": "Premium subscription plan",
                "idx": 200,
                "is_default": False,
            },
        )

        _ = await subscription_plan_feature_repo.create(
            async_db_session,
            {
                "plan_id": create_result.id,
                "feature_name": "typical offer",
                "value": 1,
            },
        )

        assert isinstance(create_result, SubscriptionPlanModel)

    @pytest.mark.asyncio
    async def test_b_fetch_all_sub_plans_with_features(self, async_db_session):
        """
        test fetch all sub plans with features
        """
        subs = await subscription_plan_repo.fetch_all(
            async_db_session, include_features=True
        )

        # print("subs: ", subs)
        for sub in subs:

            assert len(sub["features"]) > 0

    @pytest.mark.asyncio
    async def test_c_get_features(self, async_db_session):
        """
        test get features
        """
        create_result = await subscription_plan_repo.create(
            async_db_session,
            {
                "name": "premium3",
                "price": Decimal("29.99"),
                "description": "Premium subscription plan",
                "idx": 20,
                "is_default": False,
            },
        )
        plan_feature = await subscription_plan_feature_repo.create(
            async_db_session,
            {
                "plan_id": create_result.id,
                "feature_name": "typical offer",
                "value": 1,
            },
        )

        features = await subscription_plan_feature_repo.fetch_all(
            async_db_session, plan_id=create_result.id
        )

        assert len(features) == 1
        assert isinstance(features, Sequence)

        assert plan_feature in features

        feature = await subscription_plan_feature_repo.fetch(
            async_db_session,
            plan_id=create_result.id,
            feature_name=plan_feature.feature_name,
        )

        assert feature is not None
        assert feature == plan_feature
