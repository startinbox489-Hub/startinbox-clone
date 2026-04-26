"""
SocialOauth Repository Module
"""

from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import SocialOauthModel, UserModel


class SocialOauthRepository(AbstractRepository):
    """
    SocialOauth Repository
    """

    model: type[SocialOauthModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = SocialOauthModel

    async def create(
        self,
        session: AsyncSession,
        social_oauth_data: Dict[str, Any],
        user: UserModel | None = None,
        commit: bool = True,
    ):
        """
        Create a new SocialOauthModel

        Args:
            session: Async database session
            social_oauth_data: Dictionary containing SocialOauthModel data

        Returns:
            SocialOauthModel: The created SocialOauthModel
        """
        if user:
            social_oauth_data["user"] = user
        new_social_oauth = self.model(**social_oauth_data)
        session.add(new_social_oauth)
        if commit:
            await session.commit()
        return new_social_oauth

    async def fetch(
        self,
        session: AsyncSession,
        user_id: str | None = None,
        social_sub: str | None = None,
        email: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[SocialOauthModel]:
        """
        Get a socia_oauth.

        Args:
            session: Async database session
            user_id: UUID string of the user
            social_sub: social_sub of the user.
            email: email of the user.
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        select_attrs = []
        if attributes:
            for attribute in attributes:
                select_attrs.append(getattr(SocialOauthModel, attribute))
        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs)
        if email:
            query = query.where(self.model.email == email)
        if social_sub:
            query = query.where(self.model.social_sub == social_sub)
        if user_id:
            query = query.where(self.model.user_id == user_id)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_all(self, *args, **kwargs) -> Any:
        """
        Fetch all  records
        """
        return

    async def update(self, *args, **kwargs) -> Any:
        """
        Update a record
        """
        return

    async def delete(self, *args, **kwargs) -> Any:
        """
        Delete a record
        """
        return


social_oauth_repository = SocialOauthRepository()
