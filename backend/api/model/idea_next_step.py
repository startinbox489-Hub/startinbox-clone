"""
IdeaNextStep Model
"""

from typing import TYPE_CHECKING
from datetime import date

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Date

from api.database.sql_database import Base, ModelMixin


if TYPE_CHECKING:
    from api.model.user import UserModel
    from api.model.startup_ideas import StartupIdeasModel


class IdeaNextStepModel(ModelMixin, Base):
    """
    Represents the si_idea_next_steps in the database table
    """

    __tablename__ = "si_idea_next_steps"  #  type: ignore

    user_id: Mapped[str | None] = mapped_column(
        String(60),
        ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )
    idea_id: Mapped[str | None] = mapped_column(
        String(60),
        ForeignKey("si_startup_ideas.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )
    project_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    project_stage: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    desired_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        uselist=False,
        back_populates="idea_next_step",
        passive_deletes=True,
    )
    startup_idea: Mapped["StartupIdeasModel"] = relationship(
        "StartupIdeasModel",
        uselist=False,
        back_populates="idea_next_step",
        passive_deletes=True,
    )
