"""
SocialOauth Model
"""

from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Boolean, TEXT, UniqueConstraint

from api.database.sql_database import Base, ModelMixin

if TYPE_CHECKING:
    from api.model.user import UserModel


class SocialOauthModel(ModelMixin, Base):
    """
    Represents the si_social_oauths in the database table
    """

    __tablename__ = "si_social_oauths"  #  type: ignore

    user_id: Mapped[str] = mapped_column(
        String(60),
        ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=False,
        unique=False,
        index=True,
    )
    social_sub: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="FALSE"
    )
    family_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    given_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    picture: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    access_token: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        uselist=False,
        back_populates="social_oauths",
        passive_deletes=True,
    )

    # +++++++++++++++++ Constraints +++++++++++++++++++++

    __table_args__ = (
        UniqueConstraint(
            email, social_sub, name="uq_si_social_oauths_email_social_sub_composite"
        ),
    )
