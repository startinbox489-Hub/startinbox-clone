"""
UserSession Repository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import UserSessionModel


class UserSessionRepository(AbstractRepository):
    """
    UserSession Repository
    """

    model: type[UserSessionModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = UserSessionModel

    async def create(
        self,
        session: AsyncSession,
        user_session_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Create a new UserSessionModel

        Args:
            session: Async database session
            user_session_data: Dictionary containing UserSessionModel data

        Returns:
            UserSessionModel: The created UserSessionModel
        """
        user = self.model(**user_session_data)
        session.add(user)
        if commit:
            await session.commit()
        return user

    async def fetch(
        self,
        session: AsyncSession,
        user_id: str | None = None,
        jti: str | None = None,
        session_id: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[UserSessionModel]:
        """
        Get a user_session.

        Args:
            session: Async database session
            user_id: UUID string of the user
            jti: jti of the user.
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        select_attrs = []
        if attributes:
            for attribute in attributes:
                select_attrs.append(getattr(UserSessionModel, attribute))
        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs)

        if session_id:
            query = query.where(self.model.id == session_id)
        if jti:
            query = query.where(self.model.jti == jti)
        if user_id:
            query = query.where(self.model.user_id == user_id)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_all(
        self,
        session: AsyncSession,
        user_id: str,
        is_revoked: bool | None = None,
    ) -> Sequence[UserSessionModel]:
        """
        Get all UserSessionModels with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[UserSessionModel]: Sequence of UserSessionModels
        """
        stmt = sa.select(self.model).where(self.model.user_id == user_id)
        if is_revoked is not None:
            stmt = stmt.where(self.model.is_revoked.is_(is_revoked))

        result = await session.execute(
            stmt.order_by(sa.desc(getattr(self.model, "created_at")))
        )

        return result.scalars().all()

    async def delete(
        self, session: AsyncSession, user_session: UserSessionModel, commit: bool = True
    ) -> None:
        """
        Delete a usUserSessionModeler

        Args:
            session: Async database session
            user: The user to delete

        Returns:
            bool: True if deleted, False if not found
        """

        await session.execute(
            sa.delete(self.model).where(self.model.id == user_session.id)
        )
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        user_session: UserSessionModel,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> UserSessionModel:
        """
        Update a UserSessionModel

        Args:
            session: Async database session
            UserSessionModel: The UserSessionModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[UserSessionModel]: The updated UserSessionModel if found, None otherwise
        """

        await session.execute(
            sa.update(self.model)
            .where(self.model.id == user_session.id)
            .values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(user_session)
        return user_session


user_session_repo = UserSessionRepository()
