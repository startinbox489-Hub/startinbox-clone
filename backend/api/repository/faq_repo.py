"""
FAQsRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import FAQsModel


class FAQsRepository(AbstractRepository):
    """
    FAQsRepository
    """

    model: type[FAQsModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = FAQsModel

    async def create(
        self,
        session: AsyncSession,
        faq_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Create a new FAQsModel

        Args:
            session: Async database session
            faq_data: Dictionary containing FAQsModel data

        Returns:
            FAQsModel: The created FAQsModel
        """
        faq = self.model(**faq_data)
        session.add(faq)
        if commit:
            await session.commit()
        return faq

    async def fetch(
        self,
        session: AsyncSession,
        faq_id: str,
        attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping | FAQsModel]:
        """
        Get a faq.

        Args:
            session: Async database session
            faq_id: UUID string of the faq
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[faq]: The faq if found, None otherwise
        """
        select_attrs = []
        if attributes:
            select_attrs += [
                getattr(FAQsModel, attribute)
                for attribute in attributes
                if hasattr(FAQsModel, attribute)
            ]

        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(self.model.id == faq_id)

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
    ) -> Sequence[FAQsModel]:
        """
        Get all FAQsModels with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[FAQsModel]: Sequence of FAQsModels
        """
        stmt = sa.select(self.model)

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all()

    async def delete(
        self,
        session: AsyncSession,
        faq_id: str,
        faq: FAQsModel | None = None,
        commit: bool = True,
    ) -> None:
        """
        Delete an FAQsModeler

        Args:
            session: Async database session
            faq: The faq to delete

        Returns:
            bool: True if deleted, False if not found
        """
        query = sa.delete(self.model)
        if faq:
            query = query.where(self.model.id == faq.id)
        else:
            query = query.where(self.model.id == faq_id)

        await session.execute(query)
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        faq: FAQsModel | sa.RowMapping,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> FAQsModel | sa.RowMapping:
        """
        Update a FAQsModel

        Args:
            session: Async database session
            FAQsModel: The FAQsModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[FAQsModel]: The updated FAQsModel
        """

        await session.execute(
            sa.update(self.model).where(self.model.id == faq.id).values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(faq)
        return faq


faq_repo = FAQsRepository()
