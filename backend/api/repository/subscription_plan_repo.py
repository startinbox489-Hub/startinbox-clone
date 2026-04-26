"""
SubscriptionPlanRepo Module
"""

from typing import Dict, Any, Optional, Sequence, List
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from api.base.repository import AbstractRepository
from api.model import SubscriptionPlanModel, SubscriptionPlanFeatureModel


class SubscriptionPlanRepo(AbstractRepository):
    """
    Subscription Plan Repository
    """

    model: type[SubscriptionPlanModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = SubscriptionPlanModel

    async def create(
        self, session: AsyncSession, plan_data: Dict[str, Any], commit: bool = True
    ):
        """
        Create a new subscription plan

        Args:
            session: Async database session
            plan_data: Dictionary containing plan data

        Returns:
            SubscriptionPlanModel: The created plan
        """
        plan = self.model(**plan_data)
        session.add(plan)
        if commit:
            await session.commit()
            await session.refresh(plan)
        return plan

    async def fetch(
        self,
        session: AsyncSession,
        is_default: bool | None = None,
        plan_id: str | None = None,
        plan_idx: int | None = None,
        flutterwave_plan_id: int | None = None,
        include_features: bool = False,
        attributes: list | None = None,
    ) -> Optional[sa.RowMapping | SubscriptionPlanModel]:
        """
        Get a plan.
        Will return SubscriptionPlanModel when attributes is None.
        And RowMapping when attributes is not None.

        Args:
            session: Async database session
            plan_id: UUID string of the plan
            include_features: Whether to include features

        Returns:
            Optional[SubscriptionPlanModel]: The plan if found, None otherwise
        """
        select_attributes = []
        if attributes:
            select_attributes = [
                getattr(SubscriptionPlanModel, attribute)
                for attribute in attributes
                if hasattr(SubscriptionPlanModel, attribute)
            ]
        else:
            select_attributes.append(self.model)
        where_claus = []
        if plan_id is not None:
            where_claus.append(self.model.id == plan_id)
        if plan_idx is not None:
            where_claus.append(self.model.idx == plan_idx)
        if flutterwave_plan_id is not None:
            where_claus.append(self.model.flutterwave_plan_id == flutterwave_plan_id)

        if is_default is not None:
            where_claus.append(self.model.is_default.is_(is_default))
            where_claus.append(self.model.is_deleted.is_(False))
            where_claus.append(self.model.dummy.is_(True))

        query = sa.select(*select_attributes).where(
            *where_claus,
        )

        if include_features:
            query = query.options(sa_orm.selectinload(self.model.features))

        result = await session.execute(query)
        return (
            result.mappings().one_or_none()
            if attributes
            else result.scalar_one_or_none()
        )

    async def fetch_by_name(
        self, session: AsyncSession, name: str, include_features: bool = False
    ) -> Optional[SubscriptionPlanModel]:
        """
        Get a plan by its name

        Args:
            session: Async database session
            name: Name of the plan
            include_features: Whether to include features

        Returns:
            Optional[SubscriptionPlanModel]: The plan if found, None otherwise
        """
        query = sa.select(self.model).where(
            self.model.name == name, self.model.is_deleted.is_(False)
        )

        if include_features:
            query = query.options(sa_orm.selectinload(self.model.features))

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 100,
        include_features: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get all plans with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return
            include_features: Whether to include features

        Returns:
            List[Dict[str, Any]]: Sequence of plans
        """
        stmt = sa.select(self.model)
        if include_features:
            stmt = (
                sa.select(SubscriptionPlanModel, SubscriptionPlanFeatureModel)
                .join(
                    SubscriptionPlanFeatureModel,
                    SubscriptionPlanModel.id == SubscriptionPlanFeatureModel.plan_id,
                    isouter=True,
                )
                .order_by(SubscriptionPlanModel.idx)
            )
        result = await session.execute(
            stmt.offset(offset).limit(limit).where(self.model.is_deleted.is_(False))
        )

        rows = result.all()

        # Group features under each plan
        plans: dict[str, dict] = {}
        for plan in rows:
            plan_id = plan[0].id
            if plan_id not in plans:
                plans[plan_id] = {
                    "id": plan_id,
                    "name": plan[0].name,
                    "price": plan[0].price,
                    "description": plan[0].description,
                    "idx": plan[0].idx,
                    "is_popular": plan[0].is_popular,
                    "credits": plan[0].credits,
                    "type":  plan[0]._type or plan[0].type,
                    "flutterwave_plan_id": plan[0].flutterwave_plan_id,
                    "features": [],
                }
            if len(plan) > 1 and plan[1] is not None:
                plans[plan_id]["features"].append(
                    {"name": plan[1].feature_name, "value": plan[1].value}
                )

        return list(plans.values())

    async def fetch_plans_by_price_range(
        self,
        session: AsyncSession,
        min_price: Decimal,
        max_price: Decimal,
        offset: int = 0,
        limit: int = 100,
        include_features: bool = False,
    ) -> Sequence[SubscriptionPlanModel]:
        """
        Get plans within a specific price range

        Args:
            session: Async database session
            min_price: Minimum price
            max_price: Maximum price
            offset: Number of records to offset
            limit: Maximum number of records to return
            include_features: Whether to include features

        Returns:
            Sequence[SubscriptionPlanModel]: Sequence of plans in price range
        """
        query = (
            sa.select(self.model)
            .where(
                self.model.price.between(min_price, max_price),
                self.model.is_deleted.is_(False),
            )
            .offset(offset)
            .limit(limit)
            .order_by(self.model.price.asc())
        )

        if include_features:
            query = query.options(sa_orm.selectinload(self.model.features))

        result = await session.execute(query)
        return result.scalars().all()

    async def delete(
        self,
        session: AsyncSession,
        plan: SubscriptionPlanModel,
    ) -> None:
        """
        Delete a plan

        Args:
            session: Async database session
            plan: The subscription plan to delete

        Returns:
            bool: True if deleted, False if not found
        """

        await session.execute(sa.delete(self.model).where(self.model.id == plan.id))
        await session.commit()

    async def update(
        self,
        session: AsyncSession,
        plan: SubscriptionPlanModel,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> Optional[SubscriptionPlanModel]:
        """
        Update a plan

        Args:
            session: Async database session
            plan: The subscription plan to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[SubscriptionPlanModel]: The updated plan if found, None otherwise
        """

        # Update the plan
        await session.execute(
            sa.update(self.model).where(self.model.id == plan.id).values(**update_data)
        )
        if commit:
            await session.commit()

            # Refresh and return the updated plan
            await session.refresh(plan)
        return plan

    async def plan_exists(self, session: AsyncSession, name: str) -> bool:
        """
        Check if a plan with the given name exists

        Args:
            session: Async database session
            name: Name of the plan to check

        Returns:
            bool: True if plan exists, False otherwise
        """
        result = await session.execute(
            sa.select(self.model).where(
                self.model.name == name, self.model.is_deleted.is_(False)
            )
        )
        return result.scalar_one_or_none() is not None

    async def count(self, session: AsyncSession) -> int:
        """
        Count total plans

        Args:
            session: Async database session

        Returns:
            int: Total number of plans
        """
        result = await session.execute(
            sa.select(sa.func.count())
            .select_from(self.model)
            .where(self.model.is_deleted.is_(False))
        )
        return result.scalar_one()

    async def get_plans_with_features(
        self, session: AsyncSession, offset: int = 0, limit: int = 100
    ) -> Sequence[SubscriptionPlanModel]:
        """
        Get all plans with their features eagerly loaded

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[SubscriptionPlanModel]: Sequence of plans with features
        """
        result = await session.execute(
            sa.select(self.model)
            .where(self.model.is_deleted.is_(False))
            .options(sa_orm.selectinload(self.model.features))
            .offset(offset)
            .limit(limit)
            .order_by(self.model.price.asc())
        )
        return result.scalars().all()

    async def search_plans(
        self,
        session: AsyncSession,
        search_term: str,
        offset: int = 0,
        limit: int = 100,
        include_features: bool = False,
    ) -> Sequence[SubscriptionPlanModel]:
        """
        Search plans by name or description

        Args:
            session: Async database session
            search_term: Term to search for
            offset: Number of records to offset
            limit: Maximum number of records to return
            include_features: Whether to include features

        Returns:
            Sequence[SubscriptionPlanModel]: Sequence of matching plans
        """
        search_pattern = f"%{search_term}%"
        query = (
            sa.select(self.model)
            .where(
                sa.or_(
                    self.model.name.ilike(search_pattern),
                    self.model.description.ilike(search_pattern),
                ),
                self.model.is_deleted.is_(False),
            )
            .offset(offset)
            .limit(limit)
            .order_by(self.model.price.asc())
        )

        if include_features:
            query = query.options(sa_orm.selectinload(self.model.features))

        result = await session.execute(query)
        return result.scalars().all()

    async def get_cheapest_plan(
        self, session: AsyncSession, include_features: bool = False
    ) -> Optional[SubscriptionPlanModel]:
        """
        Get the cheapest subscription plan

        Args:
            session: Async database session
            include_features: Whether to include features

        Returns:
            Optional[SubscriptionPlanModel]: The cheapest plan if found
        """
        query = (
            sa.select(self.model)
            .where(self.model.is_deleted.is_(False))
            .order_by(self.model.price.asc())
            .limit(1)
        )

        if include_features:
            query = query.options(sa_orm.selectinload(self.model.features))

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_most_expensive_plan(
        self, session: AsyncSession, include_features: bool = False
    ) -> Optional[SubscriptionPlanModel]:
        """
        Get the most expensive subscription plan

        Args:
            session: Async database session
            include_features: Whether to include features

        Returns:
            Optional[SubscriptionPlanModel]: The most expensive plan if found
        """
        query = (
            sa.select(self.model)
            .where(self.model.is_deleted.is_(False))
            .order_by(self.model.price.desc())
            .limit(1)
        )

        if include_features:
            query = query.options(sa_orm.selectinload(self.model.features))

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_plan_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Get statistics about subscription plans

        Args:
            session: Async database session

        Returns:
            Dict[str, Any]: Plan statistics
        """
        result = await session.execute(
            sa.select(
                sa.func.count().label("total_plans"),
                sa.func.min(self.model.price).label("min_price"),
                sa.func.max(self.model.price).label("max_price"),
                sa.func.avg(self.model.price).label("avg_price"),
            ).select_from(self.model)
        )

        stats = result.mappings().one()
        return dict(stats)


subscription_plan_repo = SubscriptionPlanRepo()
