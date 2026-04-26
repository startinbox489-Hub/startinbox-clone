"""
AddsOnConsultationRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import AddsOnConsultationModel


class AddsOnConsultationRepository(AbstractRepository):
    """
    AddsOnConsultationRepository
    """

    model: type[AddsOnConsultationModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = AddsOnConsultationModel

    async def create(
        self,
        session: AsyncSession,
        adds_on_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Create a new AddsOnConsultationModel

        Args:
            session: Async database session
            adds_on_data: Dictionary containing AddsOnConsultationModel data

        Returns:
            AddsOnConsultationModel: The created AddsOnConsultationModel
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
        user_id: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping | AddsOnConsultationModel]:
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
                getattr(AddsOnConsultationModel, attribute)
                for attribute in attributes
                if hasattr(AddsOnConsultationModel, attribute)
            ]

        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(self.model.id == adds_on_id)
        if user_id:
            query = query.where(self.model.user_id == user_id)

        result = await session.execute(query)
        return (
            result.scalar_one_or_none()
            if attributes is None
            else result.mappings().one_or_none()
        )

    async def fetch_from_user_sub_id(
        self,
        session: AsyncSession,
        user_sub_id: str,
    ) -> Optional[AddsOnConsultationModel]:
        """
        Get a adds_on.

        Args:
            session: Async database session
            user_sub_id: UUID string of the adds_on.

        Returns:
            Optional[adds_on]: The adds_on if found, None otherwise
        """
        from api.model import PaymentModel, UserSubscriptionModel  #  type: ignore

        query = (
            sa.select(self.model)
            .select_from(self.model)
            .outerjoin(
                PaymentModel, PaymentModel.adds_on_consultation_id == self.model.id
            )
            .outerjoin(
                UserSubscriptionModel,
                UserSubscriptionModel.id == PaymentModel.user_subscription_id,
            )
            .where(UserSubscriptionModel.id == user_sub_id)
        )

        result = await session.execute(query)

        return result.scalar_one_or_none()

    async def fetch_all(
        self,
        session: AsyncSession,
        user_id: str,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[AddsOnConsultationModel]:
        """
        Get all AddsOnConsultationModels with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[AddsOnConsultationModel]: Sequence of AddsOnConsultationModels
        """
        stmt = sa.select(self.model).where(self.model.user_id == user_id)

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all()

    async def delete(
        self,
        session: AsyncSession,
        adds_on_id: str,
        user_id: str | None = None,
        adds_on: AddsOnConsultationModel | None = None,
        commit: bool = True,
    ) -> None:
        """
        Delete an AddsOnConsultationModeler

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

        if user_id:
            query = query.where(self.model.user_id == user_id)

        await session.execute(query)
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        adds_on: AddsOnConsultationModel | sa.RowMapping,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> AddsOnConsultationModel | sa.RowMapping:
        """
        Update a AddsOnConsultationModel

        Args:
            session: Async database session
            AddsOnConsultationModel: The AddsOnConsultationModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[AddsOnConsultationModel]: The updated AddsOnConsultationModel
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


adds_on_consultation_repo = AddsOnConsultationRepository()
