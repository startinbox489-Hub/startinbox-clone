"""
UserSession Model
"""

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Boolean, DateTime

from api.database.sql_database import Base, ModelMixin

if TYPE_CHECKING:
    from api.model.user import UserModel


class UserSessionModel(ModelMixin, Base):
    """
    Represents the si_user_sessions in the database table
    """

    __tablename__ = "si_user_sessions"  #  type: ignore

    user_id: Mapped[str] = mapped_column(
        String(60),
        ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=False,
        unique=False,
        index=True,
    )
    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    ipaddress: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    user_agent: Mapped[str] = mapped_column(String(500), nullable=False)
    jti: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="FALSE",
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        uselist=False,
        back_populates="user_sessions",
        passive_deletes=True,
    )
