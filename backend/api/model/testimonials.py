"""
Testimonials Model
"""

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import TEXT, Integer, String, Boolean

from api.database.sql_database import Base, ModelMixin


class TestimonialModel(ModelMixin, Base):
    """
    Represents the si_testimonials in the database table
    """

    __tablename__ = "si_testimonials"  #  type: ignore

    idea_id: Mapped[str] = mapped_column(String(60), nullable=True)  # might make a r/ship
    testimonial: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    firstname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lastname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    is_approved: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="FALSE"
    )
    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++
