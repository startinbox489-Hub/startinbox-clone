"""
AddsOnServiceRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import AddsOnServiceModel


class AddsOnServiceRepository(AbstractRepository):
    """
    AddsOnServiceRepository
    """

    model: type[AddsOnServiceModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = AddsOnServiceModel

    async def create(
        self,
        session: AsyncSession,
        adds_on_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Create a new AddsOnServiceModel

        Args:
            session: Async database session
            adds_on_data: Dictionary containing AddsOnServiceModel data

        Returns:
            AddsOnServiceModel: The created AddsOnServiceModel
        """
        adds_on = self.model(**adds_on_data)
        session.add(adds_on)
        if commit:
            await session.commit()
        return adds_on

    async def fetch(
        self,
        session: AsyncSession,
        adds_on_id: str,
        attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping | AddsOnServiceModel]:
        """
        Get a adds_on.

        Args:
            session: Async database session
            adds_on_id: UUID string of the adds_on
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[adds_on]: The adds_on if found, None otherwise
        """
        select_attrs = []
        if attributes:
            select_attrs += [
                getattr(AddsOnServiceModel, attribute)
                for attribute in attributes
                if hasattr(AddsOnServiceModel, attribute)
            ]

        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(self.model.id == adds_on_id)

        result = await session.execute(query)
        return (
            result.scalar_one_or_none()
            if attributes is None
            else result.mappings().one_or_none()
        )

    async def fetch_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[AddsOnServiceModel]:
        """
        Get all AddsOnServiceModels with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[AddsOnServiceModel]: Sequence of AddsOnServiceModels
        """
        stmt = sa.select(self.model)

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all()

    async def delete(
        self,
        session: AsyncSession,
        adds_on_id: str,
        adds_on: AddsOnServiceModel | None = None,
        commit: bool = True,
    ) -> None:
        """
        Delete an AddsOnServiceModeler

        Args:
            session: Async database session
            adds_on: The adds_on to delete

        Returns:
            bool: True if deleted, False if not found
        """
        query = sa.delete(self.model)
        if adds_on:
            query = query.where(self.model.id == adds_on.id)
        else:
            query = query.where(self.model.id == adds_on_id)

        await session.execute(query)
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        adds_on: AddsOnServiceModel | sa.RowMapping,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> AddsOnServiceModel | sa.RowMapping:
        """
        Update a AddsOnServiceModel

        Args:
            session: Async database session
            AddsOnServiceModel: The AddsOnServiceModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[AddsOnServiceModel]: The updated AddsOnServiceModel
        """

        await session.execute(
            sa.update(self.model)
            .where(self.model.id == adds_on.id)
            .values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(adds_on)
        return adds_on


adds_on_service_repo = AddsOnServiceRepository()
