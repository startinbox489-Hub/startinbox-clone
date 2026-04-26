"""
IdeaNextStepRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import IdeaNextStepModel


class IdeaNextStepRepository(AbstractRepository):
    """
    IdeaNextStepRepository
    """

    model: type[IdeaNextStepModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = IdeaNextStepModel

    async def create(
        self,
        session: AsyncSession,
        next_step_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Create a new IdeaNextStepModel

        Args:
            session: Async database session
            next_step_data: Dictionary containing IdeaNextStepModel data

        Returns:
            IdeaNextStepModel: The created IdeaNextStepModel
        """
        ideas = self.model(**next_step_data)
        if commit:
            session.add(ideas)
            await session.commit()
        return ideas

    async def fetch(
        self,
        session: AsyncSession,
        next_step_id: str | None = None,
        idea_id: str | None = None,
        user_id: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping | IdeaNextStepModel | None]:
        """
        Get a ideas.

        Args:
            session: Async database session
            next_step_id: UUID string of the ideas
            user_id: UUID string of the user
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[ideas]: The ideas if found, None otherwise
        """
        select_attrs = []
        if attributes:
            select_attrs += [
                getattr(IdeaNextStepModel, attribute)
                for attribute in attributes
                if hasattr(IdeaNextStepModel, attribute)
            ]

        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs)
        if user_id:
            query = query.where(self.model.user_id == user_id)
        if next_step_id:
            query = query.where(self.model.id == next_step_id)
        if idea_id:
            query = query.where(self.model.idea_id == idea_id)

        result = await session.execute(query)
        return (
            result.scalar_one_or_none()
            if attributes is None
            else result.mappings().one_or_none()
        )

    async def fetch_all(
        self,
        session: AsyncSession,
        user_id: str,
        offset: int = 0,
        limit: int = 100,
        attributes: list[str] | None = None,
    ) -> Sequence[IdeaNextStepModel | sa.RowMapping]:
        """
        Get all IdeaNextStepModels with pagination

        Args:
            session: Async database session
            user_id: uuid string of the user.
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[IdeaNextStepModel]: Sequence of IdeaNextStepModels
        """
        selected_att = []
        if attributes:
            for attribute in attributes:
                if hasattr(self.model, attribute):
                    selected_att.append(getattr(self.model, attribute))
        else:
            selected_att.append(self.model)
        stmt = sa.select(*selected_att).where(self.model.user_id == user_id)

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all() if attributes is None else result.mappings().all()

    async def delete(
        self,
        session: AsyncSession,
        next_step_id: str,
        user_id: str,
        ideas: IdeaNextStepModel | None = None,
        commit: bool = True,
    ) -> None:
        """
        Delete an IdeaNextStepModeler

        Args:
            session: Async database session
            next_step_id: The id of the idea to delete
            user_id: The is of the user
            ideas: The ideas to delete

        Returns:
            bool: True if deleted, False if not found
        """
        query = sa.delete(self.model)
        if user_id:
            query = query.where(self.model.user_id == user_id)
        if ideas:
            query = query.where(self.model.id == ideas.id)
        else:
            query = query.where(self.model.id == next_step_id)

        await session.execute(query)
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        ideas: IdeaNextStepModel | sa.RowMapping,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> IdeaNextStepModel | sa.RowMapping:
        """
        Update a IdeaNextStepModel

        Args:
            session: Async database session
            IdeaNextStepModel: The IdeaNextStepModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[IdeaNextStepModel]: The updated IdeaNextStepModel
        """

        await session.execute(
            sa.update(self.model).where(self.model.id == ideas.id).values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(ideas)
        return ideas


ideas_next_step_repo = IdeaNextStepRepository()
