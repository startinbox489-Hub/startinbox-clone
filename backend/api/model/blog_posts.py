"""
POSTS Model
"""

from typing import Optional

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import TEXT, String, ForeignKey, Boolean

from api.database.sql_database import Base, ModelMixin


class BlogPostModel(ModelMixin, Base):
    """
    Represents the si_blog_posts in the database table
    """

    __tablename__ = "si_blog_posts"  #  type: ignore

    owner_id: Mapped[Optional[str]] = mapped_column(
        String(60),
        ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
        index=True,
    )

    is_draft: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="FALSE", nullable=False
    )

    content: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    image: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    # ++++++++++++++++++++ relationship +++++++++++++++++++++++++++++
