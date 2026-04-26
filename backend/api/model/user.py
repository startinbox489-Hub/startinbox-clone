"""
User Model
"""

from datetime import datetime
from typing import List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, TEXT, Boolean, DateTime, UniqueConstraint
from passlib.context import CryptContext

from api.database.sql_database import Base, ModelMixin, sql_database
from api.model.model_enums import (
    postgres_user_provider_enum,
    sqlite_user_provider_enum,
    UserProviderEnum,
    UserRoleEnum,
    postgres_user_role_enum,
    sqlite_user_role_enum,
)
from api.model.user_session import UserSessionModel
from api.model.social_oauth import SocialOauthModel
from api.model.news_letter import NewsLetterSubscriptionModel
from api.model.payment import PaymentModel
from api.model.user_subscriptions import UserSubscriptionModel
from api.model.startup_ideas import StartupIdeasModel
from api.model.adds_on_consultations import AddsOnConsultationModel
from api.model.idea_next_step import IdeaNextStepModel
from api.model.plan_usage_statistics import PlanUsageStatisticModel

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

is_sqlite = sql_database.async_engine.url.drivername == "sqlite+aiosqlite"
user_provider_enum = postgres_user_provider_enum
user_role_enum = postgres_user_role_enum
if is_sqlite:
    user_provider_enum = sqlite_user_provider_enum
    user_role_enum = sqlite_user_role_enum


class UserModel(ModelMixin, Base):
    """
    Represents the si_users in the database table
    """

    __tablename__ = "si_users"  #  type: ignore

    email: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True, index=True
    )
    sub: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=False,
        comment="Socials user ID (sub claim from id_token)",
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(150), nullable=True, unique=True, index=True
    )
    password: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=False, index=False
    )
    firstname: Mapped[str | None] = mapped_column(
        String(150), unique=False, nullable=True
    )
    lastname: Mapped[str | None] = mapped_column(
        String(150), unique=False, nullable=True
    )
    profile_photo: Mapped[str | None] = mapped_column(TEXT, unique=False, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="FALSE", nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    signup_provider: Mapped[UserProviderEnum] = mapped_column(
        user_provider_enum,
        nullable=False,
        default=UserProviderEnum.STARTINBOX.value,
        server_default=UserProviderEnum.STARTINBOX.value,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="FALSE"
    )
    agreed_to_terms: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="TRUE"
    )
    role: Mapped[UserRoleEnum] = mapped_column(
        user_role_enum,
        nullable=False,
        default=UserRoleEnum.REGULAR.value,
        server_default=UserRoleEnum.REGULAR.value,
    )
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # +++++++++++++++++++ relationships ++++++++++++++++++++++
    user_sessions: Mapped[List["UserSessionModel"]] = relationship(
        "UserSessionModel",
        uselist=True,
        back_populates="user",
        passive_deletes=True,
        foreign_keys=[UserSessionModel.user_id],
    )

    social_oauths: Mapped[List["SocialOauthModel"]] = relationship(
        "SocialOauthModel",
        uselist=True,
        back_populates="user",
        passive_deletes=True,
        foreign_keys=[SocialOauthModel.user_id],
    )
    payments: Mapped[List["PaymentModel"]] = relationship(
        "PaymentModel",
        uselist=True,
        back_populates="user",
        passive_deletes=True,
        foreign_keys=[PaymentModel.user_id],
    )
    user_subscriptions: Mapped[List["UserSubscriptionModel"]] = relationship(
        "UserSubscriptionModel",
        uselist=True,
        back_populates="user",
        passive_deletes=True,
        foreign_keys=[UserSubscriptionModel.user_id],
    )

    news_letter_subscription: Mapped["NewsLetterSubscriptionModel"] = relationship(
        "NewsLetterSubscriptionModel",
        uselist=False,
        back_populates="user",
        passive_deletes=True,
        foreign_keys=[NewsLetterSubscriptionModel.user_id],
    )

    startup_ideas: Mapped[List["StartupIdeasModel"]] = relationship(
        "StartupIdeasModel",
        uselist=True,
        back_populates="user",
        passive_deletes=True,
        foreign_keys=[StartupIdeasModel.user_id],
    )
    adds_on_consultations: Mapped[List["AddsOnConsultationModel"]] = relationship(
        "AddsOnConsultationModel",
        uselist=True,
        back_populates="user",
        passive_deletes=True,
        foreign_keys=[AddsOnConsultationModel.user_id],
    )

    idea_next_step: Mapped["IdeaNextStepModel"] = relationship(
        "IdeaNextStepModel",
        uselist=False,
        back_populates="user",
        passive_deletes=True,
    )

    plan_usage_statistic: Mapped["PlanUsageStatisticModel"] = relationship(
        "PlanUsageStatisticModel",
        uselist=False,
        back_populates="user",
        passive_deletes=True,
    )

    # +++++++++++++++++ Constraints +++++++++++++++++++++

    __table_args__ = (
        UniqueConstraint(
            signup_provider, sub, name="uq_si_users_sub_signup_provider_composite"
        ),
    )

    # +++++++++++++++++++++ Methods +++++++++++++++++++++++++++

    def set_password(self, plain_password: str) -> None:
        """
        Sets a user password.

        Args:
            plain_password(str): password to hash.
        """
        if not plain_password or plain_password == "":
            raise TypeError("plain_password must be provided for password hashing")
        hashed_password = password_context.hash(plain_password)
        self.password = hashed_password

    def verify_password(self, plain_password: str) -> bool:
        """
        Verifies user password.

        Args:
            plain_password(str): password to compare with hash.
        """
        if not plain_password:
            raise TypeError(
                "plain_password must be provided for password matching/comparing"
            )
        return password_context.verify(secret=plain_password, hash=self.password)
