"""
AddsOnService Model
"""

from typing import List, Dict

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String

from api.database.sql_database import Base, ModelMixin
from api.model.adds_on_consultations import AddsOnConsultationModel
from api.model.model_enums import json_data_type


class AddsOnServiceModel(ModelMixin, Base):
    """
    Represents the si_adds_on_services in the database table
    """

    __tablename__ = "si_adds_on_services"  #  type: ignore

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=False,
        index=True,
        comment="Consult with a Startup Expert",
    )
    prices: Mapped[List[Dict[str, int | str]]] = mapped_column(
        json_data_type, nullable=False
    )

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++
    consultations_one: Mapped[List["AddsOnConsultationModel"]] = relationship(
        "AddsOnConsultationModel",
        foreign_keys=[AddsOnConsultationModel.adds_on_one_id],
        back_populates="adds_on_one",
        passive_deletes=True,
    )

    consultations_two: Mapped[List["AddsOnConsultationModel"]] = relationship(
        "AddsOnConsultationModel",
        foreign_keys=[AddsOnConsultationModel.adds_on_two_id],
        back_populates="adds_on_two",
        passive_deletes=True,
    )
