"""
Subscription Plan Features Model
"""

from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Integer

from api.database.sql_database import Base, ModelMixin

if TYPE_CHECKING:
    from api.model.subscription_plan import SubscriptionPlanModel


class SubscriptionPlanFeatureModel(ModelMixin, Base):
    """
    Represents the si_subscription_plan_features in the database table
    """

    __tablename__ = "si_subscription_plan_features"  #  type: ignore

    plan_id: Mapped[str] = mapped_column(
        String(60),
        ForeignKey("si_subscription_plans.id", ondelete="SET NULL"),
        index=True,
        unique=False,
        nullable=False,
    )
    feature_name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[None | int] = mapped_column(
        Integer,
        nullable=True,
        comment="optional limit",
    )

    # ++++++++++++++++++ Relationship ++++++++++++++++++
    plan: Mapped["SubscriptionPlanModel"] = relationship(
        "SubscriptionPlanModel",
        back_populates="features",
        uselist=False,
        passive_deletes=True,
    )
