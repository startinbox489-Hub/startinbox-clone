"""
Plan Usage Repo Statistics
"""

from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import PlanUsageStatisticModel, UserModel


class PlanUsageStatisticRepository(AbstractRepository):
    """
    PlanUsageStatisticRepository
    """

    model: type[PlanUsageStatisticModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = PlanUsageStatisticModel

    async def create(
        self,
        session: AsyncSession,
        usage_data: Dict[str, Any],
        commit: bool = True,
        user: UserModel | None = None,
    ):
        """
        Create a new plan usage data

        Args:
            session: Async database session
            usage_data: Dictionary containing plan_usage data

        Returns:
            PlanUsageStatisticModel: The created plan_usage
        """
        user_id = usage_data.get("user_id")
        plan_usage = self.model()
        if user_id:
            plan_usage.user_id = user_id
        if user:
            plan_usage.user = user
        session.add(plan_usage)
        if commit:
            await session.commit()
            await session.refresh(plan_usage)
        return plan_usage

    async def fetch(
        self,
        session: AsyncSession,
        user_id: str,
        plan_usage_id: str | None = None,
        include_features: bool = False,
        attributes: list | None = None,
    ) -> Optional[sa.RowMapping | PlanUsageStatisticModel]:
        """
        Get a plan_usage.
        Will return PlanUsageStatisticModel when attributes is None.
        And RowMapping when attributes is not None.

        Args:
            session: Async database session
            plan_usage_id: UUID string of the plan usage
            include_features: Whether to include features

        Returns:
            Optional[PlanUsageStatisticModel]: The plan usage if found, None otherwise
        """
        select_attributes = []
        if attributes:
            select_attributes = [
                getattr(PlanUsageStatisticModel, attribute)
                for attribute in attributes
                if hasattr(PlanUsageStatisticModel, attribute)
            ]
        else:
            select_attributes.append(self.model)
        where_claus = []
        where_claus.append(self.model.user_id == user_id)
        if plan_usage_id:
            where_claus.append(self.model.id == plan_usage_id)
        query = sa.select(*select_attributes).where(
            *where_claus,
        )

        result = await session.execute(query)
        return (
            result.mappings().one_or_none()
            if attributes
            else result.scalar_one_or_none()
        )

    async def update(
        self,
        session: AsyncSession,
        plan_usage_stats: PlanUsageStatisticModel,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> PlanUsageStatisticModel:
        """
        Update a PlanUsageStatisticModel

        Args:
            session: Async database session
            PlanUsageStatisticModel: The PlanUsageStatisticModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[PlanUsageStatisticModel]: The updated PlanUsageStatisticModel if found, None otherwise
        """

        await session.execute(
            sa.update(self.model)
            .where(
                self.model.id == plan_usage_stats.id,
                self.model.user_id == plan_usage_stats.user_id,
            )
            .values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(plan_usage_stats)
        return plan_usage_stats

    async def delete(
        self,
        session: AsyncSession,
        plan_usage_stats: PlanUsageStatisticModel,
        commit: bool = True,
    ) -> None:
        """
        Delete a PlanUsageStatisticModel

        Args:
            session: Async database session
            plan_usage_stats: The plan_usage_stats to delete

        Returns:
            bool: True if deleted, False if not found
        """

        await session.execute(
            sa.delete(self.model).where(self.model.id == plan_usage_stats.id)
        )
        if commit:
            await session.commit()

    async def fetch_all(self, *args, **kwargs) -> Any:
        """
        Fetch all  records
        """
        return


plan_usage_statistics_repo = PlanUsageStatisticRepository()
