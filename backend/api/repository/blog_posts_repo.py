"""
BlogPostRepository Module
"""

from typing import Dict, Any, Optional, Sequence, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.base.repository import AbstractRepository
from api.model import BlogPostModel


class BlogPostRepository(AbstractRepository):
    """
    BlogPostRepository
    """

    model: type[BlogPostModel]

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = BlogPostModel

    async def create(
        self,
        session: AsyncSession,
        post_data: Dict[str, Any],
        commit: bool = True,
    ):
        """
        Create a new BlogPostModel

        Args:
            session: Async database session
            post_data: Dictionary containing BlogPostModel data

        Returns:
            BlogPostModel: The created BlogPostModel
        """
        post = self.model(**post_data)
        session.add(post)
        if commit:
            await session.commit()
        return post

    async def fetch(
        self,
        session: AsyncSession,
        post_id: str,
        attributes: list[str] | None = None,
        is_draft: Optional[bool] = None,
        owner_id: Optional[str] = None,
    ) -> Optional[sa.RowMapping | BlogPostModel]:
        """
        Get a post.

        Args:
            session: Async database session
            post_id: UUID string of the post
            attributes: The list of attributes to fetch from the table row.

        Returns:
            Optional[post]: The post if found, None otherwise
        """
        select_attrs = []
        if attributes:
            select_attrs += [
                getattr(BlogPostModel, attribute)
                for attribute in attributes
                if hasattr(BlogPostModel, attribute)
            ]

        else:
            select_attrs.append(self.model)

        query = sa.select(*select_attrs).where(self.model.id == post_id)
        if is_draft is not None:
            query = query.where(self.model.is_draft.is_(is_draft))
        if owner_id is not None:
            query = query.where(self.model.owner_id.is_(owner_id))

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
        limit: int = 10,
        is_draft: Optional[bool] = None,
        owner_id: Optional[str] = None,
    ) -> Tuple[Sequence[BlogPostModel], int]:
        """
        Get all BlogPostModels with pagination

        Args:
            session: Async database session
            offset: Number of records to offset
            limit: Maximum number of records to return

        Returns:
            Sequence[BlogPostModel]: Sequence of BlogPostModels
        """
        stmt = sa.select(self.model)
        if is_draft is not None:
            stmt = stmt.where(self.model.is_draft.is_(is_draft))
        if owner_id is not None:
            stmt = stmt.where(self.model.owner_id == owner_id)

        result = await session.execute(
            stmt.offset(offset).limit(limit).order_by(sa.desc(self.model.created_at))
        )
        count_result = (
            await session.execute(
                sa.select(sa.func.count(self.model.id)).select_from(self.model)
            )
        ).scalar_one_or_none() or 0

        return result.scalars().all(), count_result

    async def delete(
        self,
        session: AsyncSession,
        post_id: str,
        post: BlogPostModel | None = None,
        commit: bool = True,
        owner_id: Optional[str] = None,
        is_draft: Optional[bool] = None,
    ) -> None:
        """
        Delete an BlogPostModeler

        Args:
            session: Async database session
            post: The post to delete

        Returns:
            bool: True if deleted, False if not found
        """
        query = sa.delete(self.model)
        if post:
            query = query.where(self.model.id == post.id)
        else:
            query = query.where(self.model.id == post_id)

        if owner_id:
            query = query.where(self.model.owner_id == owner_id)
        if is_draft:
            query = query.where(self.model.is_draft == is_draft)

        await session.execute(query)
        if commit:
            await session.commit()

    async def update(
        self,
        session: AsyncSession,
        post: BlogPostModel | sa.RowMapping,
        update_data: Dict[str, Any],
        commit: bool = True,
        owner_id: Optional[str] = None,
        is_draft: Optional[bool] = None,
    ) -> BlogPostModel | sa.RowMapping:
        """
        Update a BlogPostModel

        Args:
            session: Async database session
            BlogPostModel: The BlogPostModel to update
            update_data: Dictionary containing fields to update
            commit: The flag to decide if to commit the changes yet

        Returns:
            Optional[BlogPostModel]: The updated BlogPostModel
        """

        query = sa.update(self.model).where(self.model.id == post.id)
        if owner_id is not None:
            query = sa.update(self.model).where(
                self.model.owner_id == owner_id,
            )
        if is_draft is not None:
            query = sa.update(self.model).where(
                self.model.is_draft == is_draft,
            )

        await session.execute(query.values(**update_data))
        if commit:
            await session.commit()

            await session.refresh(post)
        return post

    async def count(
        self,
        session: AsyncSession,
        owner_id: str,
        is_draft: Optional[bool] = None,
    ) -> int:
        """
        Count blogs
        """
        stmt = sa.select(sa.func.count(self.model.id))
        if owner_id:
            stmt = stmt.where(self.model.owner_id == owner_id)
        if is_draft is not None:
            stmt = stmt.where(self.model.is_draft == is_draft)

        result = await session.execute(stmt)

        return result.scalar() or 0  # type: ignore


blog_post_repo = BlogPostRepository()
