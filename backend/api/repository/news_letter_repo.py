"""
NewsLetterRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import NewsLetterSubscriptionModel, UserModel


class NewsLetterRepository(AbstractRepository):
    """
    NewsLetterRepository
    """

    model: type[NewsLetterSubscriptionModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = NewsLetterSubscriptionModel

    async def create(
        self,
        session: AsyncSession,
        news_letter_data: Dict[str, Any],
        commit: bool = True,
        user: UserModel | None = None,
    ):
        """
        Create a new NewsLetterSubscription

        Args:
            session: Async database session
            news_letter_data: Dictionary containing NewsLetterSubscription data

        Returns:
            NewsLetterSubscription: The created NewsLetterSubscription
        """
        news_letter = self.model(**news_letter_data)
        if user:
            news_letter.user = user
        session.add(news_letter)
        if commit:
            await session.commit()
        return news_letter

    async def fetch(
        self,
        session: AsyncSession,
        news_letter_id: str | None = None,
        email: str | None = None,
        newsletter_hash: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping | NewsLetterSubscriptionModel]:
        """
        Get a news_letter.

        Args:
            session: Async database session
            news_letter_id: UUID string of the news_letter
            email: email of the news_letter.
            newsletter_hash: newsletter hash of the news_letter.
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[news_letter]: The news_letter if found, None otherwise
        """
        select_attrs = []
        if attributes:
            select_attrs.append(
                [
                    getattr(NewsLetterSubscriptionModel, attribute)
                    for attribute in attributes
                    if hasattr(NewsLetterSubscriptionModel, attribute)
                ]
            )
        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs)
        if news_letter_id:
            query = query.where(self.model.id == news_letter_id)
        if email:
            query = query.where(self.model.email == email)
        if newsletter_hash:
            query = query.where(self.model.newsletter_hash == newsletter_hash)

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
    ) -> Sequence[NewsLetterSubscriptionModel]:
        """
        Get all NewsLetterSubscriptionModels with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[NewsLetterSubscriptionModel]: Sequence of NewsLetterSubscriptionModels
        """
        stmt = sa.select(self.model)

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all()

    async def delete(
        self,
        session: AsyncSession,
        news_letter: NewsLetterSubscriptionModel,
        commit: bool = True,
    ) -> None:
        """
        Delete a usNewsLetterSubscriptionModeler

        Args:
            session: Async database session
            news_letter: The news_letter to delete

        Returns:
            bool: True if deleted, False if not found
        """

        await session.execute(
            sa.delete(self.model).where(self.model.id == news_letter.id)
        )
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        news_letter: NewsLetterSubscriptionModel | sa.RowMapping,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> NewsLetterSubscriptionModel:
        """
        Update a NewsLetterSubscriptionModel

        Args:
            session: Async database session
            NewsLetterSubscriptionModel: The NewsLetterSubscriptionModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[NewsLetterSubscriptionModel]: The updated NewsLetterSubscriptionModel
        """

        await session.execute(
            sa.update(self.model)
            .where(self.model.id == news_letter.id)
            .values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(news_letter)
        return news_letter


news_letter_repo = NewsLetterRepository()
