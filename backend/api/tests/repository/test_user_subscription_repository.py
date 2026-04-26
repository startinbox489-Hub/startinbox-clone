"""
Test user-subscription repo
"""

from decimal import Decimal
import pytest

from api.repository.user_subscription_repo import user_subscription_repo
from api.repository.user_repo import user_repository
from api.repository.payment_repository import payment_repo
from api.repository.subscription_plan_repo import subscription_plan_repo


class TestUserSubscriptionRepo:
    """
    Test Usersubscription repo
    """

    @pytest.mark.asyncio
    async def test_a_create_and_fetch_user_subscription(self, async_db_session):
        """
        Test create and fetch Usersubscription
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnson.user_subscription_test@gmail.com",
                "phone_number": "+2348064343422",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        assert new_user is not None

        new_sub_plan = await subscription_plan_repo.fetch(
            session=async_db_session, is_default=True
        )
        assert new_sub_plan is not None

        new_user_subscription = await user_subscription_repo.create(
            async_db_session,
            {
                "user_id": new_user.id,
                "subscription_plan_id": new_sub_plan.id,
                "is_current": True,
            },
        )
        assert new_user_subscription is not None

        new_payment = await payment_repo.create(
            session=async_db_session,
            payment_data={
                "user_id": new_user.id,
                "subscription_plan_id": new_sub_plan.id,
                "subscription_plan_idx": new_sub_plan.idx,
                "user_subscription_id": new_user_subscription.id,
                "amount": Decimal(10000),
                "currency": "NGN",
                "tx_reference": "213e2r32e32222222222222222",
                "payment_reference": "213e2r32e3222222222222222",
                "provider": "paystack",
            },
        )
        assert new_payment is not None

        user_sub_found = await user_subscription_repo.fetch(
            session=async_db_session,
            is_current=True,
            user_id=new_user.id,
        )

        assert user_sub_found is not None
        assert user_sub_found.id == new_user_subscription.id

        found_payment = await payment_repo.fetch(
            session=async_db_session,
            user_id=new_user.id,
            subscription_plan_id=new_sub_plan.id,
            tx_reference=new_payment.tx_reference,
        )

        assert found_payment is not None
        assert found_payment.id == new_payment.id
