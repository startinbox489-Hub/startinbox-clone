"""
PaymentRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import PaymentModel, UserSubscriptionModel


class PaymentRepository(AbstractRepository):
    """
    PaymentRepository
    """

    model: type[PaymentModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = PaymentModel

    async def create(
        self,
        session: AsyncSession,
        payment_data: Dict[str, Any],
        commit: bool = True,
        user_subscription: UserSubscriptionModel | None = None,
    ):
        """
        Create a new Payment

        Args:
            session: Async database session
            payment_data: Dictionary containing Payment data

        Returns:
            Payment: The created Payment
        """
        new_payment = self.model(**payment_data)
        if user_subscription:
            new_payment.user_subscription_id = None
            new_payment.user_subscription = user_subscription
        session.add(new_payment)
        if commit:
            await session.commit()
        return new_payment

    async def fetch(
        self,
        session: AsyncSession,
        user_id: str | None = None,
        subscription_plan_id: str | None = None,
        payment_id: str | None = None,
        tx_reference: str | None = None,
        payment_reference: str | None = None,
        attributes: list[str] | None = None,
    ) -> Optional[PaymentModel]:
        """
        Get a payment.

        Args:
            session: Async database session
            user_id: UUID string of the user
            subscription_plan_id: subscription_plan_id of the payment.
            payment_id: payment_id of the user.
            tx_reference: tx_reference of the payment provider.
            payment_reference: payment_reference of the payment from us.
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        select_attrs = []
        if attributes:
            for attribute in attributes:
                select_attrs.append(getattr(PaymentModel, attribute))
        else:
            select_attrs.append(self.model)
        query = sa.select(*select_attrs)
        if payment_id:
            query = query.where(self.model.id == payment_id)
        if tx_reference:
            query = query.where(self.model.tx_reference == tx_reference)
        if subscription_plan_id:
            query = query.where(self.model.subscription_plan_id == subscription_plan_id)
        if user_id:
            query = query.where(self.model.user_id == user_id)
        if payment_reference:
            query = query.where(self.model.payment_reference == payment_reference)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def fetch_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[PaymentModel]:
        """
        Get all Payments with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[Payment]: Sequence of Payments
        """
        stmt = sa.select(self.model)

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all()

    async def delete(
        self, session: AsyncSession, payment_record: PaymentModel, commit: bool = True
    ) -> None:
        """
        Delete a Payment

        Args:
            session: Async database session
            user: The user to delete

        Returns:
            None
        """

        await session.execute(
            sa.delete(self.model).where(self.model.id == payment_record.id)
        )
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        payment_record: PaymentModel,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> PaymentModel:
        """
        Update a Payment

        Args:
            session: Async database session
            Payment: The Payment to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[Payment]: The updated Payment if found, None otherwise
        """

        await session.execute(
            sa.update(self.model)
            .where(self.model.id == payment_record.id)
            .values(**update_data)
        )
        if commit:
            session.add(payment_record)
            await session.commit()

            await session.refresh(payment_record)
        return payment_record


payment_repo = PaymentRepository()
