"""
UserSubscriptionRepo Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import UserSubscriptionModel, UserModel, SubscriptionPlanModel
from api.model.model_enums import SubscriptionPlanTypeEnum


class UserSubscriptionRepo(AbstractRepository):
    """
    UserSubscriptionModel Repository
    """

    model: type[UserSubscriptionModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = UserSubscriptionModel

    async def create(
        self,
        session: AsyncSession,
        user_sub_data: Dict[str, Any],
        commit: bool = True,
        user: UserModel | None = None,
    ):
        """
        Create a new user_subscription

        Args:
            session: Async database session
            user_sub_data: Dictionary containing user_sub data

        Returns:
            UserSubscriptionModel: The created user_sub
        """
        user_sub = self.model(**user_sub_data)
        if user:
            user_sub.user_id = None
            user_sub.user = user

        if commit:
            session.add(user_sub)
            await session.commit()
            await session.refresh(user_sub)
        return user_sub

    async def fetch(
        self,
        session: AsyncSession,
        is_current: bool | None = None,
        is_expired: bool | None = None,
        user_sub_id: str | None = None,
        user_id: str | None = None,
        flutterwave_subscription_id: int | None = None,
        _type: SubscriptionPlanTypeEnum | None = None,
    ) -> Optional[UserSubscriptionModel]:
        """
        Get a user_sub by its ID

        Args:
            session: Async database session
            user_sub_id: UUID string of the user_sub
            include_features: Whether to include features

        Returns:
            Optional[UserSubscriptionModel]: The user_sub if found, None otherwise
        """
        query = sa.select(self.model)
        if user_id:
            query = query.where(self.model.user_id == user_id)
        if is_current is not None:
            query = query.where(self.model.is_current == is_current)
        if is_expired is not None:
            query = query.where(self.model.is_expired == is_expired)
        if user_sub_id:
            query = query.where(self.model.id == user_sub_id)
        if _type:
            query = query.where(self.model._type == _type.value)
        if flutterwave_subscription_id:
            query = query.where(
                self.model.flutterwave_subscription_id == flutterwave_subscription_id
            )

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[UserSubscriptionModel]:
        """
        Get all user_subs with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[UserSubscriptionModel]: Sequence of user_subs
        """
        stmt = sa.select(self.model)

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all()

    async def fetch_with_plan(
        self,
        session: AsyncSession,
        user_id: str,
        user_sub_attributes: list[str] | None = None,
        sub_attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping]:
        """
        Get a user_sub with the subscription plan

        Args:
            session: Async database session
            user_sub_id: UUID string of the user_sub

        Returns:
            Optional[sa.RowMapping]: The user_sub with sub plan if found, None otherwise
        """
        if not user_sub_attributes:
            user_sub_attributes = [
                "id",
                "is_current",
                "subscription_plan_id",
                "is_expired",
            ]
        if not sub_attributes:
            sub_attributes = ["prompt", "idx"]
        select_attributes = []
        for attribute in user_sub_attributes:
            if hasattr(self.model, attribute):
                select_attributes.append(getattr(self.model, attribute))

        for attribute in sub_attributes:
            if hasattr(SubscriptionPlanModel, attribute):
                select_attributes.append(getattr(SubscriptionPlanModel, attribute))

        query = (
            sa.select(*select_attributes)
            .select_from(self.model)
            .join(
                SubscriptionPlanModel,
                self.model.subscription_plan_id == SubscriptionPlanModel.id,
            )
            .where(self.model.user_id == user_id, self.model.is_current.is_(True))
        )

        result = await session.execute(query)
        return result.mappings().one_or_none()

    async def fetch_with_plans(
        self,
        session: AsyncSession,
        user_id: str,
        user_sub_attributes: list[str] | None = None,
        sub_attributes: list[str] | None = None,
    ) -> Sequence[sa.RowMapping]:
        """
        Get user subs with the subscription plan

        Args:
            session: Async database session
            user_sub_id: UUID string of the user_sub

        Returns:
           Sequence[sa.RowMapping]: The user_sub with sub plan if found, None otherwise
        """
        if not user_sub_attributes:
            user_sub_attributes = [
                "id",
                "is_current",
                "subscription_plan_id",
                "is_expired",
                "flutterwave_subscription_id",
                "credit_used",
                "remaining_credits",
                "_type",
            ]
        if not sub_attributes:
            sub_attributes = ["name", "idx"]
        select_attributes = []
        for attribute in user_sub_attributes:
            if hasattr(self.model, attribute):
                select_attributes.append(getattr(self.model, attribute))

        for attribute in sub_attributes:
            if hasattr(SubscriptionPlanModel, attribute):
                select_attributes.append(getattr(SubscriptionPlanModel, attribute))

        query = (
            sa.select(*select_attributes)
            .select_from(self.model)
            .join(
                SubscriptionPlanModel,
                self.model.subscription_plan_id == SubscriptionPlanModel.id,
            )
            .where(self.model.user_id == user_id, self.model.is_expired.is_(False))
        )

        result = await session.execute(query)
        return result.mappings().all()

    async def delete(
        self,
        session: AsyncSession,
        user_sub: UserSubscriptionModel,
    ) -> None:
        """
        Delete a user_sub

        Args:
            session: Async database session
            user_sub: The subscription user_sub to delete

        Returns:
            None
        """

        await session.execute(sa.delete(self.model).where(self.model.id == user_sub.id))
        await session.commit()

    async def update(
        self,
        session: AsyncSession,
        user_sub: UserSubscriptionModel,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> UserSubscriptionModel:
        """
        Update a user_sub

        Args:
            session: Async database session
            user_sub: The subscription user_sub to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[UserSubscriptionModel]: The updated user_sub if found, None otherwise
        """

        # Update the user_sub
        await session.execute(
            sa.update(self.model)
            .where(self.model.id == user_sub.id)
            .values(**update_data)
        )
        if commit:
            await session.commit()

            # Refresh and return the updated user_sub
            await session.refresh(user_sub)
        return user_sub

    async def update_with_id(
        self,
        session: AsyncSession,
        user_sub_id: str,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> Optional[UserSubscriptionModel]:
        """
        Update a user_sub

        Args:
            session: Async database session
            user_sub_id: The subscription user_sub_id to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[UserSubscriptionModel]: The updated user_sub if found, None otherwise
        """

        # Update the user_sub
        await session.execute(
            sa.update(self.model)
            .where(self.model.id == user_sub_id)
            .values(**update_data)
        )
        if commit:
            await session.commit()
        return

    async def count(self, session: AsyncSession) -> int:
        """
        Count total user_subs

        Args:
            session: Async database session

        Returns:
            int: Total number of user_subs
        """
        result = await session.execute(
            sa.select(sa.func.count()).select_from(self.model)
        )
        return result.scalar_one()


user_subscription_repo = UserSubscriptionRepo()
