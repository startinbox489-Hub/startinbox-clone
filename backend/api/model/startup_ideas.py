"""
StartupIdeas Model
"""

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, TEXT, Integer

from api.database.sql_database import Base, ModelMixin
from api.model.adds_on_consultations import AddsOnConsultationModel
from api.model.idea_next_step import IdeaNextStepModel
from api.model.model_enums import json_data_type


if TYPE_CHECKING:
    from api.model.user import UserModel


class StartupIdeasModel(ModelMixin, Base):
    """
    Represents the si_startup_ideas in the database table
    """

    __tablename__ = "si_startup_ideas"  #  type: ignore

    user_id: Mapped[str | None] = mapped_column(
        String(60),
        ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )
    prompt: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )

    # A. Validation Output
    idea_validation: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    idea_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    lean_canvas: Mapped[dict | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    ideal_customer_persona: Mapped[dict | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    suggested_startup_names: Mapped[list[str] | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    monetization_models: Mapped[list[str]] = mapped_column(
        json_data_type,
        nullable=True,
    )
    # B. Launch Content Generator
    website_hero: Mapped[dict | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    blog_posts: Mapped[list[str] | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    twitter_posts: Mapped[list[str] | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    elevator_pitch_slide: Mapped[list[str] | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    # C. Influencer Outreach Generator
    influencer_one: Mapped[dict | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    influencer_two: Mapped[dict | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    influencer_three: Mapped[dict | None] = mapped_column(
        json_data_type,
        nullable=True,
    )
    go_to_market_strategy_outline: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        uselist=False,
        back_populates="startup_ideas",
        passive_deletes=True,
    )
    adds_on_consultations: Mapped[List["AddsOnConsultationModel"]] = relationship(
        "AddsOnConsultationModel",
        uselist=True,
        back_populates="startup_idea",
        passive_deletes=True,
        foreign_keys=[AddsOnConsultationModel.startup_idea_id],
    )

    idea_next_step: Mapped["IdeaNextStepModel"] = relationship(
        "IdeaNextStepModel",
        uselist=False,
        back_populates="startup_idea",
        passive_deletes=True,
        foreign_keys=[IdeaNextStepModel.idea_id],
    )
