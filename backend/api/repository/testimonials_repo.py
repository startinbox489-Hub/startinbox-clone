"""
TestimonialsRepository Module
"""

from typing import Dict, Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import TestimonialModel


class TestimonialsRepository(AbstractRepository):
    """
    TestimonialsRepository
    """

    model: type[TestimonialModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = TestimonialModel

    async def create(
        self,
        session: AsyncSession,
        testimonial_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Create a new TestimonialModel

        Args:
            session: Async database session
            testimonial_data: Dictionary containing TestimonialModel data

        Returns:
            TestimonialModel: The created TestimonialModel
        """
        testimonial = self.model(**testimonial_data)
        session.add(testimonial)
        if commit:
            await session.commit()
        return testimonial

    async def fetch(
        self,
        session: AsyncSession,
        testimonial_id: str,
        attributes: list[str] | None = None,
    ) -> Optional[sa.RowMapping | TestimonialModel]:
        """
        Get a testimonial.

        Args:
            session: Async database session
            testimonial_id: UUID string of the testimonial
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[testimonial]: The testimonial if found, None otherwise
        """
        select_attrs = []
        if attributes:
            select_attrs += [
                getattr(TestimonialModel, attribute)
                for attribute in attributes
                if hasattr(TestimonialModel, attribute)
            ]

        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(self.model.id == testimonial_id)

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
    ) -> Sequence[TestimonialModel]:
        """
        Get all TestimonialModels with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[TestimonialModel]: Sequence of TestimonialModels
        """
        stmt = sa.select(self.model).where(self.model.is_approved.is_(True))

        result = await session.execute(stmt.offset(offset).limit(limit))

        return result.scalars().all()

    async def delete(
        self,
        session: AsyncSession,
        testimonial_id: str,
        testimonial: TestimonialModel | None = None,
        commit: bool = True,
    ) -> None:
        """
        Delete an TestimonialModeler

        Args:
            session: Async database session
            testimonial: The testimonial to delete

        Returns:
            bool: True if deleted, False if not found
        """
        query = sa.delete(self.model)
        if testimonial:
            query = query.where(self.model.id == testimonial.id)
        else:
            query = query.where(self.model.id == testimonial_id)

        await session.execute(query)
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        testimonial: TestimonialModel | sa.RowMapping,
        update_data: Dict[str, Any],
        commit: bool = True,
    ) -> TestimonialModel | sa.RowMapping:
        """
        Update a TestimonialModel

        Args:
            session: Async database session
            TestimonialModel: The TestimonialModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[TestimonialModel]: The updated TestimonialModel
        """

        await session.execute(
            sa.update(self.model)
            .where(self.model.id == testimonial.id)
            .values(**update_data)
        )
        if commit:
            await session.commit()

            await session.refresh(testimonial)
        return testimonial


testimonial_repo = TestimonialsRepository()
