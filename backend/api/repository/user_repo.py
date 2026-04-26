"""
UserRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import UserModel


class UserRepository(AbstractRepository):
    """
    User Repository
    """

    model: type[UserModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = UserModel

    async def create(
        self, session: AsyncSession, user_data: Dict[str, Any], commit: bool = True
    ):
        """
        Create a new user

        Args:
            session: Async database session
            user_data: Dictionary containing user data

        Returns:
            User: The created user
        """
        user = self.model(**user_data)
        if user_data.get("password"):
            user.set_password(user_data["password"])
        session.add(user)
        if commit:
            await session.commit()
        return user

    async def fetch(
        self,
        session: AsyncSession,
        user_id: str | None = None,
        email: str | None = None,
        phone_number: str | None = None,
        idempotency_key: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[UserModel]:
        """
        Get a user.

        Args:
            session: Async database session
            user_id: UUID string of the user
            email: email of the user
            phone_number: phone_number of the user
            idempotency_key: idempotency_key string of the user
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[UserModel]: The user if found, None otherwise
        """
        select_attrs = []
        if attributes:
            for attribute in attributes:
                select_attrs.append(getattr(UserModel, attribute))
        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs)
        if user_id:
            query = query.where(self.model.id == user_id)
        if email:
            query = query.where(self.model.email == email)
        if phone_number:
            query = query.where(self.model.phone_number == phone_number)
        if idempotency_key:
            query = query.where(self.model.idempotency_key == idempotency_key)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_by_attrs(
        self,
        session: AsyncSession,
        user_id: str | None = None,
        email: str | None = None,
        phone_number: str | None = None,
        idempotency_key: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping]:
        """
        Get a user.

        Args:
            session: Async database session
            user_id: UUID string of the user
            email: email of the user
            phone_number: phone_number of the user
            idempotency_key: idempotency_key string of the user
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[RowMapping]: The user if found, None otherwise
        """
        select_attrs = []
        if attributes:
            for attribute in attributes:
                select_attrs.append(getattr(UserModel, attribute))
        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs)
        if user_id:
            query = query.where(self.model.id == user_id)
        if email:
            query = query.where(self.model.email == email)
        if phone_number:
            query = query.where(self.model.phone_number == phone_number)
        if idempotency_key:
            query = query.where(self.model.idempotency_key == idempotency_key)

        result = await session.execute(query)
        return result.mappings().one_or_none()

    async def fetch_by_email(
        self,
        session: AsyncSession,
        email: str,
        attributes: list[str] | None = None,
    ) -> Optional[UserModel]:
        """
        Get a user by its email

        Args:
            session: Async database session
            email: email of the user
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[UserModel]: The user if found, None otherwise
        """
        select_attrs = []
        if attributes:
            for attribute in attributes:
                select_attrs.append(getattr(UserModel, attribute))
        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(self.model.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_by_phone_number(
        self,
        session: AsyncSession,
        phone_number: str,
        attributes: list[str] | None = None,
    ) -> Optional[UserModel]:
        """
        Get a user by its phone_number

        Args:
            session: Async database session
            phone_number: phone_number of the user
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[UserModel]: The user if found, None otherwise
        """
        select_attrs = []
        if attributes:
            for attribute in attributes:
                select_attrs.append(getattr(UserModel, attribute))
        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(self.model.phone_number == phone_number)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_by_idempotency_key(
        self,
        session: AsyncSession,
        idempotency_key: str,
        attributes: list[str] | None = None,
    ) -> Optional[UserModel]:
        """
        Get a user by its idempotency_key

        Args:
            session: Async database session
            idempotency_key: idempotency_key of the user
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[UserModel]: The user if found, None otherwise
        """
        select_attrs = []
        if attributes:
            for attribute in attributes:
                select_attrs.append(getattr(UserModel, attribute))
        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(
            self.model.idempotency_key == idempotency_key
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[UserModel]:
        """
        Get all users with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[User]: Sequence of users
        """
        stmt = sa.select(self.model)

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all()

    async def delete(
        self, session: AsyncSession, user: UserModel, commit: bool = True
    ) -> None:
        """
        Delete a user

        Args:
            session: Async database session
            user: The user to delete

        Returns:
            bool: True if deleted, False if not found
        """

        await session.execute(sa.delete(self.model).where(self.model.id == user.id))
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        user: UserModel,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> UserModel:
        """
        Update a user

        Args:
            session: Async database session
            user: The user to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[UserModel]: The updated user if found, None otherwise
        """

        # Update the user
        await session.execute(
            sa.update(self.model).where(self.model.id == user.id).values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(user)
        return user


user_repository = UserRepository()
