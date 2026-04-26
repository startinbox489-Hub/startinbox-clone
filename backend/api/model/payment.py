"""
Payment Model
"""

from typing import TYPE_CHECKING
from datetime import datetime
from decimal import Decimal

import sqlalchemy.orm as sa_orm
import sqlalchemy as sa

from api.database.sql_database import Base, ModelMixin, sql_database
from api.model.model_enums import (
    postgres_payment_status_enum,
    sqlite_payment_status_enum,
    postgres_payment_provider_enum,
    sqlite_payment_provider_enum,
    PaymentStatusEnum,
    PaymentProviderEnum,
)


if TYPE_CHECKING:
    from api.model.user import UserModel
    from api.model.subscription_plan import SubscriptionPlanModel
    from api.model.user_subscriptions import UserSubscriptionModel
    from api.model.adds_on_consultations import AddsOnConsultationModel

is_sqlite = sql_database.async_engine.url.get_backend_name() == "sqlite"
payment_status_enum = (
    sqlite_payment_status_enum if is_sqlite else postgres_payment_status_enum
)
payment_provider_enum = (
    sqlite_payment_provider_enum if is_sqlite else postgres_payment_provider_enum
)


class PaymentModel(ModelMixin, Base):
    """
    Represents the si_payments in the database table
    """

    __tablename__ = "si_payments"  #  type: ignore

    user_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(60),
        sa.ForeignKey("si_users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    subscription_plan_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(60),
        sa.ForeignKey("si_subscription_plans.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    user_subscription_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(60),
        sa.ForeignKey("si_user_subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    adds_on_consultation_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(60),
        sa.ForeignKey("si_adds_on_consultations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    provider: sa_orm.Mapped[PaymentProviderEnum] = sa_orm.mapped_column(
        payment_provider_enum,
        nullable=False,
        comment="e.g., paystack/flutterwave/stripe/paypal",
    )
    subscription_plan_idx: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.Integer,
        nullable=False,
    )
    flutterwave_subscription_id: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.Integer,
        nullable=True,
    )
    amount: sa_orm.Mapped[Decimal] = sa_orm.mapped_column(
        sa.Numeric(10, 2), nullable=False
    )
    currency: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.String(10),
    )
    purchase_event_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(60),
        nullable=True,
    )
    status: sa_orm.Mapped[PaymentStatusEnum] = sa_orm.mapped_column(
        payment_status_enum,
        default=PaymentStatusEnum.PENDING.value,
        server_default=PaymentStatusEnum.PENDING.value,
        comment="e.g., paid/unpaid/pending/approved/failed/cancelled",
    )
    payment_reference: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.String(255),
        unique=True,
        nullable=False,
        comment="the transaction reference provided by us.",
    )
    tx_reference: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(255),
        unique=True,
        nullable=True,
        comment="the transaction reference provided by the provider",
    )
    paid_at: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    # +++++++++++++++++++ relationship ++++++++++++++++++++++
    user: sa_orm.Mapped["UserModel"] = sa_orm.relationship(
        "UserModel",
        uselist=False,
        back_populates="payments",
        passive_deletes=True,
    )
    subscription_plan: sa_orm.Mapped["SubscriptionPlanModel"] = sa_orm.relationship(
        "SubscriptionPlanModel",
        uselist=False,
        back_populates="payments",
        passive_deletes=True,
    )
    user_subscription: sa_orm.Mapped["UserSubscriptionModel"] = sa_orm.relationship(
        "UserSubscriptionModel",
        uselist=False,
        back_populates="payment",
        passive_deletes=True,
    )
    adds_on_consultation: sa_orm.Mapped["AddsOnConsultationModel"] = (
        sa_orm.relationship(
            "AddsOnConsultationModel",
            uselist=False,
            back_populates="payment",
            passive_deletes=True,
        )
    )

    # +++++++++++++++++++ constraints ++++++++++++++++++++++
