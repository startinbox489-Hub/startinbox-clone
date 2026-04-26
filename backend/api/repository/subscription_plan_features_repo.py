"""
SubscriptionPlanFeature Repo Module
"""

from typing import Dict, Any, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from api.base.repository import AbstractRepository
from api.model import SubscriptionPlanFeatureModel


class SubscriptionPlanFeatureRepo(AbstractRepository):
    """
    Subscription Plan Feature Repository
    """

    model: type[SubscriptionPlanFeatureModel]

    def __init__(self) -> None:
        """
        Constructore
        """
        self.model = SubscriptionPlanFeatureModel

    async def create(
        self, session: AsyncSession, feature_data: Dict[str, Any], commit: bool = True
    ) -> SubscriptionPlanFeatureModel:
        """
        Create a new subscription plan feature

        Args:
            session: Async database session
            feature_data: Dictionary containing feature data
            commit: boolean signifying if to commit the creation of new record

        Returns:
            SubscriptionPlanFeatureModel: The created feature
        """
        feature = self.model(**feature_data)

        if commit:
            session.add(feature)
            await session.commit()
            await session.refresh(feature)
        return feature

    async def fetch(
        self,
        session: AsyncSession,
        feature_name: str,
        plan_id: str,
    ) -> Optional[SubscriptionPlanFeatureModel]:
        """
        Fetch sub plan feature
        """
        query = sa.select(self.model).where(
            self.model.feature_name == feature_name, self.model.plan_id == plan_id
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_by_id(
        self, session: AsyncSession, feature_id: str
    ) -> Optional[SubscriptionPlanFeatureModel]:
        """
        Get a sub plan feature by its ID

        Args:
            session: Async database session
            feature_id: UUID string of the feature

        Returns:
            Optional[SubscriptionPlanFeatureModel]: The feature if found, None otherwise
        """
        result = await session.execute(
            sa.select(self.model).where(self.model.id == feature_id)
        )
        return result.scalar_one_or_none()

    async def fetch_all(
        self, session: AsyncSession, plan_id: str
    ) -> Sequence[SubscriptionPlanFeatureModel]:
        """
        Get all subscription features.

        Args:
            session: Async database session
            plan_id: The id of the plan to retrrieve features.

        Returns:
            Tuple[Sequence[SubscriptionPlanFeatureModel], int]: Tuple of Sequence of features and count of features
        """
        query = sa.select(self.model).where(self.model.plan_id == plan_id)
        result = await session.execute(query.order_by(self.model.created_at.desc()))

        return result.scalars().all()

    async def fetch_features_by_plan_id(
        self, session: AsyncSession, plan_id: str, offset: int = 0, limit: int = 50
    ) -> Sequence[SubscriptionPlanFeatureModel]:
        """
        Get all features for a specific subscription plan

        Args:
            session: Async database session
            plan_id: UUID of the subscription plan
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            List[SubscriptionPlanFeatureModel]: List of features for the plan
        """
        result = await session.execute(
            sa.select(self.model)
            .where(self.model.plan_id == plan_id)
            .offset(offset)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        )
        return result.scalars().all()

    async def delete(
        self,
        session: AsyncSession,
        feature: SubscriptionPlanFeatureModel,
    ) -> None:
        """
        Delete a feature

        Args:
            session: Async database session
            feature: The feature to update

        Returns:
            None
        """
        await session.execute(sa.delete(self.model).where(self.model.id == feature.id))
        await session.commit()

    async def update(
        self,
        session: AsyncSession,
        feature: SubscriptionPlanFeatureModel,
        update_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Update a feature

        Args:
            session: Async database session
            feature: The feature to update
            update_data: Dictionary containing fields to update
            commit: boolean signifying if to commit the update.

        Returns:
            Optional[SubscriptionPlanFeatureModel]: The updated feature if found, None otherwise
        """

        # Update the feature
        await session.execute(
            sa.update(self.model)
            .where(self.model.id == feature.id)
            .values(**update_data)
        )
        if commit:
            await session.commit()

            # Refresh and return the updated feature
            await session.refresh(feature)
        return feature

    async def feature_exists(
        self, session: AsyncSession, name: str, plan_id: str
    ) -> bool:
        """
        Check if a feature with the given name exists

        Args:
            session: Async database session
            name: Name of the feature to check
            plan_id: Optional plan ID to scope the check

        Returns:
            bool: True if feature exists, False otherwise
        """
        query = sa.select(self.model.id).where(
            self.model.feature_name == name, self.model.plan_id == plan_id
        )

        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_features_with_plan_details(
        self, session: AsyncSession, offset: int = 0, limit: int = 50
    ) -> Sequence[SubscriptionPlanFeatureModel]:
        """
        Get all features with their associated plan details

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            List[SubscriptionPlanFeatureModel]: List of features with plan details
        """
        result = await session.execute(
            sa.select(self.model)
            .options(sa_orm.joinedload(self.model.plan))
            .offset(offset)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        )
        return result.scalars().all()

    async def count(self, session: AsyncSession, plan_id: Optional[str] = None) -> int:
        """
        Count total features, optionally filtered by plan ID

        Args:
            session: Async database session
            plan_id: Optional plan ID to filter by

        Returns:
            int: Total number of features
        """
        query = sa.select(self.model)

        if plan_id:
            query = query.where(self.model.plan_id == plan_id)

        result = await session.execute(
            sa.select(sa.func.count()).select_from(query.subquery())
        )
        return result.scalar_one()


subscription_plan_feature_repo = SubscriptionPlanFeatureRepo()
