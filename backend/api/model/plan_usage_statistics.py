"""
Usage Statistics Model
"""

from typing import TYPE_CHECKING, Dict, Any

import sqlalchemy.orm as sa_orm
import sqlalchemy as sa

from api.database.sql_database import Base, ModelMixin
from api.model.model_enums import json_data_type

if TYPE_CHECKING:
    from api.model.user import UserModel


class PlanUsageStatisticModel(ModelMixin, Base):
    """
    Represents the si_plan_usage_statistics in the database table
    """

    __tablename__ = "si_plan_usage_statistics"  #  type: ignore

    user_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(60),
        sa.ForeignKey("si_users.id", ondelete="SET NULL"),
        nullable=False,
        unique=True,
    )

    free_plan_stats: sa_orm.Mapped[Dict[str, Any]] = sa_orm.mapped_column(
        json_data_type,
        default={"use_count": 0},
        server_default='{"use_count": 0}',
    )
    starter_plan_stats: sa_orm.Mapped[Dict[str, Any]] = sa_orm.mapped_column(
        json_data_type,
        default={"use_count": 0},
        server_default='{"use_count": 0}',
    )
    pro_plan_stats: sa_orm.Mapped[Dict[str, Any]] = sa_orm.mapped_column(
        json_data_type,
        default={"use_count": 0},
        server_default='{"use_count": 0}',
    )
    launch_bundle_plan_stats: sa_orm.Mapped[Dict[str, Any]] = sa_orm.mapped_column(
        json_data_type,
        default={"use_count": 0},
        server_default='{"use_count": 0}',
    )
    # credits
    silver_plan_stats: sa_orm.Mapped[Dict[str, Any]] = sa_orm.mapped_column(
        json_data_type,
        default={"use_count": 0},
        server_default='{"use_count": 0}',
    )
    gold_plan_stats: sa_orm.Mapped[Dict[str, Any]] = sa_orm.mapped_column(
        json_data_type,
        default={"use_count": 0},
        server_default='{"use_count": 0}',
    )
    diamond_plan_stats: sa_orm.Mapped[Dict[str, Any]] = sa_orm.mapped_column(
        json_data_type,
        default={"use_count": 0},
        server_default='{"use_count": 0}',
    )

    # +++++++++++++++++++ relationship ++++++++++++++++++++++
    user: sa_orm.Mapped["UserModel"] = sa_orm.relationship(
        "UserModel",
        uselist=False,
        back_populates="plan_usage_statistic",
        passive_deletes=True,
    )
