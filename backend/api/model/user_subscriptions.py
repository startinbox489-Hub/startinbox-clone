"""
User Subscriptions Model
"""

from typing import TYPE_CHECKING

import sqlalchemy.orm as sa_orm
import sqlalchemy as sa

from api.database.sql_database import Base, ModelMixin
from api.model.payment import PaymentModel
from api.model.model_enums import is_sqlite

if TYPE_CHECKING:
    from api.model.user import UserModel
    from api.model.subscription_plan import SubscriptionPlanModel

from api.model.model_enums import (
    is_sqlite,
    postgres_subscription_type_enum,
    sqlite_subscription_type_enum,
    SubscriptionPlanTypeEnum,
)

subscription_type_enum = (
    sqlite_subscription_type_enum if is_sqlite else postgres_subscription_type_enum
)


class UserSubscriptionModel(ModelMixin, Base):
    """
    Represents the si_user_subscriptions in the database table
    """

    __tablename__ = "si_user_subscriptions"  #  type: ignore

    user_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(60),
        sa.ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=False,
    )
    subscription_plan_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(60),
        sa.ForeignKey("si_subscription_plans.id", ondelete="SET NULL"),
        unique=False,
        nullable=True,
        index=True,
    )

    is_expired: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, default=False, server_default="FALSE"
    )
    is_current: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean,
        nullable=False,
    )

    flutterwave_subscription_id: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BIGINT,
        nullable=True,
    )
    credit_used: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BIGINT,
        nullable=False,
        default=0,
        server_default="0",
    )
    remaining_credits: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BIGINT,
        nullable=False,
        default=0,
        server_default="0",
    )
    _type: sa_orm.Mapped[SubscriptionPlanTypeEnum] = sa_orm.mapped_column(
        subscription_type_enum,
        nullable=False,
        default=SubscriptionPlanTypeEnum.ONEOFF.value,
        server_default=SubscriptionPlanTypeEnum.ONEOFF.value,
    )

    @property
    def type(self):
        """
        Type
        """
        return self._type

    # +++++++++++++++++++ relationship ++++++++++++++++++++++
    user: sa_orm.Mapped["UserModel"] = sa_orm.relationship(
        "UserModel",
        uselist=False,
        back_populates="user_subscriptions",
        passive_deletes=True,
    )
    subscription_plan: sa_orm.Mapped["SubscriptionPlanModel"] = sa_orm.relationship(
        "SubscriptionPlanModel",
        uselist=False,
        back_populates="user_subscriptions",
        passive_deletes=True,
    )
    payment: sa_orm.Mapped["PaymentModel"] = sa_orm.relationship(
        "PaymentModel",
        uselist=False,
        back_populates="user_subscription",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )

    # +++++++++++++++++++ constraints ++++++++++++++++++++++
    if not is_sqlite:
        __table_args__ = (
            sa.Index(
                "uq_si_user_sub_composite_user_id_is_urrent",
                user_id,
                unique=True,
                postgresql_where=is_current.is_(True),
            ),
        )
