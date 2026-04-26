"""
NewsLetterSubscription Model
"""

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Boolean, DateTime

from api.database.sql_database import Base, ModelMixin

if TYPE_CHECKING:
    from api.model.user import UserModel


class NewsLetterSubscriptionModel(ModelMixin, Base):
    """
    Represents the si_news_letter_subscriptions in the database table
    """

    __tablename__ = "si_news_letter_subscriptions"  #  type: ignore

    user_id: Mapped[str | None] = mapped_column(
        String(60),
        ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )
    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    newsletter_hash: Mapped[str | None] = mapped_column(
        String(60),
        nullable=True,
        unique=True,
        index=True,
    )
    is_unsubscribed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="FALSE"
    )
    is_sub_success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="FALSE",
    )
    unsubscribed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def subscribed_at(self):
        """
        subscribed_at
        """
        return self.created_at

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        uselist=False,
        back_populates="news_letter_subscription",
        passive_deletes=True,
    )
