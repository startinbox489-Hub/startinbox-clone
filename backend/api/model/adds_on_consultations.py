"""
AddsOnConsultation Model
"""

from typing import TYPE_CHECKING, Dict

from sqlalchemy.orm import mapped_column, Mapped, relationship
import sqlalchemy as sa

from api.database.sql_database import Base, ModelMixin
from api.model.payment import PaymentModel
from api.model.model_enums import json_data_type

if TYPE_CHECKING:
    from api.model.user import UserModel
    from api.model.startup_ideas import StartupIdeasModel
    from api.model.adds_on_service import AddsOnServiceModel


class AddsOnConsultationModel(ModelMixin, Base):
    """
    Represents the si_adds_on_consultations in the database table
    """

    __tablename__ = "si_adds_on_consultations"  #  type: ignore

    user_id: Mapped[str | None] = mapped_column(
        sa.String(60),
        sa.ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )

    startup_idea_id: Mapped[str | None] = mapped_column(
        sa.String(60),
        sa.ForeignKey("si_startup_ideas.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )
    adds_on_one_id: Mapped[str | None] = mapped_column(
        sa.String(60),
        sa.ForeignKey("si_adds_on_services.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )
    adds_on_one_price: Mapped[Dict[str, str | int] | None] = mapped_column(
        json_data_type, nullable=True, comment="e.g. {'amount': 200, 'unit': 'week'}"
    )
    is_adds_on_one_used: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        server_default="FALSE",
        nullable=False,
    )
    adds_on_two_id: Mapped[str | None] = mapped_column(
        sa.String(60),
        sa.ForeignKey("si_adds_on_services.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )
    adds_on_two_price: Mapped[Dict[str, str | int] | None] = mapped_column(
        json_data_type,
        nullable=True,
        comment="e.g. {'amount': 50, 'unit': '1-hour video call'}",
    )
    is_adds_on_two_used: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        server_default="FALSE",
        nullable=False,
    )

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        uselist=False,
        back_populates="adds_on_consultations",
        passive_deletes=True,
    )

    payment: Mapped["PaymentModel"] = relationship(
        "PaymentModel",
        uselist=False,
        back_populates="adds_on_consultation",
        passive_deletes=True,
        # cascade="all, delete-orphan",
    )

    startup_idea: Mapped["StartupIdeasModel"] = relationship(
        "StartupIdeasModel",
        uselist=False,
        back_populates="adds_on_consultations",
        # passive_deletes=True,
    )

    adds_on_one: Mapped["AddsOnServiceModel"] = relationship(
        "AddsOnServiceModel",
        foreign_keys=[adds_on_one_id],
        back_populates="consultations_one",
        passive_deletes=True,
    )

    adds_on_two: Mapped["AddsOnServiceModel"] = relationship(
        "AddsOnServiceModel",
        foreign_keys=[adds_on_two_id],
        back_populates="consultations_two",
        passive_deletes=True,
    )
