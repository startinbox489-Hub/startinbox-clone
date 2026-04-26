"""
StartupIdeasRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import StartupIdeasModel


class StartupIdeasRepository(AbstractRepository):
    """
    StartupIdeasRepository
    """

    model: type[StartupIdeasModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = StartupIdeasModel

    async def create(
        self,
        session: AsyncSession,
        ideas_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Create a new StartupIdeasModel

        Args:
            session: Async database session
            ideas_data: Dictionary containing StartupIdeasModel data

        Returns:
            StartupIdeasModel: The created StartupIdeasModel
        """
        ideas = self.model(**ideas_data)
        if commit:
            session.add(ideas)
            await session.commit()
        return ideas

    async def fetch(
        self,
        session: AsyncSession,
        ideas_id: str,
        user_id: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping | StartupIdeasModel | None]:
        """
        Get a ideas.

        Args:
            session: Async database session
            ideas_id: UUID string of the ideas
            user_id: UUID string of the user
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[ideas]: The ideas if found, None otherwise
        """
        select_attrs = []
        if attributes:
            select_attrs += [
                getattr(StartupIdeasModel, attribute)
                for attribute in attributes
                if hasattr(StartupIdeasModel, attribute)
            ]

        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(self.model.id == ideas_id)
        if user_id:
            query = query.where(self.model.user_id == user_id)

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
    ) -> Sequence[StartupIdeasModel | sa.RowMapping]:
        """
        Get all StartupIdeasModels with pagination

        Args:
            session: Async database session
            user_id: uuid string of the user.
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[StartupIdeasModel]: Sequence of StartupIdeasModels
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
        ideas_id: str,
        user_id: str,
        ideas: StartupIdeasModel | None = None,
        commit: bool = True,
    ) -> None:
        """
        Delete an StartupIdeasModeler

        Args:
            session: Async database session
            ideas_id: The id of the idea to delete
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
            query = query.where(self.model.id == ideas_id)

        await session.execute(query)
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        ideas: StartupIdeasModel | sa.RowMapping,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> StartupIdeasModel | sa.RowMapping:
        """
        Update a StartupIdeasModel

        Args:
            session: Async database session
            StartupIdeasModel: The StartupIdeasModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[StartupIdeasModel]: The updated StartupIdeasModel
        """

        await session.execute(
            sa.update(self.model).where(self.model.id == ideas.id).values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(ideas)
        return ideas

    async def fetch_last_prompt(
        self, session: AsyncSession, user_id: str
    ) -> StartupIdeasModel | None:
        """
        Retrieves the last prompt by suer

        :param session: Async session object
        :type session: AsyncSession
        :param user_id: The ID of the current user
        :type user_id: str
        """
        query = (
            sa.select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .limit(1)
        )

        result = await session.execute(query)

        return result.scalar()


startup_ideas_repo = StartupIdeasRepository()
