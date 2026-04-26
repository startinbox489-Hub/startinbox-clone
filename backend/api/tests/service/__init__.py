"""
sub service init
"""

from decimal import Decimal
from typing import Tuple, Any, List

from api.repository.subscription_plan_repo import (
    subscription_plan_repo,
    SubscriptionPlanModel,
)
from api.repository.subscription_plan_features_repo import (
    subscription_plan_feature_repo,
    SubscriptionPlanFeatureModel,
)
from api.database.sql_database import sql_database


async def seed_sub(
    plan_name: str | None = None,
    price: Decimal | None = None,
    description: str | None = None,
    plan_id: str | None = None,
    feature_name: str | None = None,
    is_default: bool | None = None,
    idx: int | None = None,
    value: Any | None = None,
) -> Tuple[SubscriptionPlanModel, List[SubscriptionPlanFeatureModel]]:
    """
    Seed subs
    """
    session = sql_database.async_session_factory()
    create_result = await subscription_plan_repo.fetch_by_name(
        session=session, name=(plan_name or "premium2")
    )
    if not create_result:
        create_result = await subscription_plan_repo.create(
            session,
            {
                "name": plan_name or "premium2",
                "price": price or Decimal("29.99"),
                "description": description or "Premium subscription plan",
                "is_default": is_default is not None and is_default or True,
                "idx": idx or 5,
            },
        )
    plan_feature = await subscription_plan_feature_repo.fetch(
        session=session,
        plan_id=(plan_id or create_result.id),
        feature_name=(feature_name or "typical offer"),
    )
    if not plan_feature:
        plan_feature = await subscription_plan_feature_repo.create(
            session,
            {
                "plan_id": plan_id or create_result.id,
                "feature_name": feature_name or "typical offer",
                "value": value or True,
            },
        )

    return create_result, [plan_feature]
