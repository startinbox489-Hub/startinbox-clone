"""
FAQs Model
"""

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import TEXT

from api.database.sql_database import Base, ModelMixin


class FAQsModel(ModelMixin, Base):
    """
    Represents the si_faqs in the database table
    """

    __tablename__ = "si_faqs"  #  type: ignore

    question: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )
    answer: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )

    @property
    def added_at(self):
        """
        added_at
        """
        return self.created_at

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++
