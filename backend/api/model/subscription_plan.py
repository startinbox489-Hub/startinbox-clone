"""
Subscription Plan Model
"""

from typing import List
from decimal import Decimal

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (
    String,
    Numeric,
    Index,
    Boolean,
    Integer,
    TEXT,
    BIGINT,
)

from api.database.sql_database import Base, ModelMixin
from api.model.subscription_plan_features import SubscriptionPlanFeatureModel
from api.model.payment import PaymentModel
from api.model.user_subscriptions import UserSubscriptionModel
from api.model.model_enums import (
    is_sqlite,
    postgres_subscription_type_enum,
    sqlite_subscription_type_enum,
    SubscriptionPlanTypeEnum,
)

subscription_type_enum = (
    sqlite_subscription_type_enum if is_sqlite else postgres_subscription_type_enum
)


class SubscriptionPlanModel(ModelMixin, Base):
    """
    Represents the si_subscription_plans in the database table
    """

    __tablename__ = "si_subscription_plans"  #  type: ignore

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    idx: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="FALSE"
    )
    dummy: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="TRUE",
        nullable=False,
        comment="used for enforcing is_default unique constraint. do not change to FALSE.",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="FALSE"
    )
    is_popular: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="FALSE"
    )
    prompt: Mapped[str | None] = mapped_column(
        TEXT, nullable=True, comment="The prompt for each plan."
    )
    _type: Mapped[SubscriptionPlanTypeEnum] = mapped_column(
        subscription_type_enum,
        nullable=False,
        default=SubscriptionPlanTypeEnum.ONEOFF.value,
        server_default=SubscriptionPlanTypeEnum.ONEOFF.value,
    )

    @property
    def type(self):
        """
        type
        """
        return self._type

    credits: Mapped[int] = mapped_column(
        BIGINT, nullable=False, default=0, server_default="0"
    )
    flutterwave_plan_id: Mapped[int | None] = mapped_column(
        BIGINT, nullable=True, unique=True
    )

    # +++++++++++++++++++ relationship ++++++++++++++++++++++
    features: Mapped[List["SubscriptionPlanFeatureModel"]] = relationship(
        "SubscriptionPlanFeatureModel",
        uselist=True,
        back_populates="plan",
        passive_deletes=True,
        foreign_keys=[SubscriptionPlanFeatureModel.plan_id],
    )
    payments: Mapped[List["PaymentModel"]] = relationship(
        "PaymentModel",
        uselist=True,
        back_populates="subscription_plan",
        passive_deletes=True,
        foreign_keys=[PaymentModel.subscription_plan_id],
    )
    user_subscriptions: Mapped[List["UserSubscriptionModel"]] = relationship(
        "UserSubscriptionModel",
        uselist=True,
        back_populates="subscription_plan",
        passive_deletes=True,
        foreign_keys=[UserSubscriptionModel.subscription_plan_id],
    )

    # +++++++++++++++++++ constraints ++++++++++++++++++++++
    if not is_sqlite:
        __table_args__ = (
            Index(
                "uq_si_subscription_plans_is_default",
                dummy,
                unique=True,
                postgresql_where="is_default is TRUE AND is_deleted IS FALSE",
            ),
        )
