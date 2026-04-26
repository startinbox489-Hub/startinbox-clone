"""
FAQs Service
"""

import math
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api.repository.blog_posts_repo import blog_post_repo
from api.schema.blog_posts_schema import (
    PostsBaseSchema,
    GetPostsResponseSchema,
    GetPostResponseSchema,
    NewPostRequestSchema,
    NewPostResponseSchema,
    EditPostRequestSchema,
    EditPostResponseSchema,
    DeletePostResponseSchema,
    months,
)
from api.schema.default_response_schema import CustomRequest
from api.utils.get_session_claims_from_request import get_claims_and_session


def validate_fields(date_: datetime) -> str:
    """
    Validate fields
    """
    date: str = date_.date().isoformat()
    split_date = date.split("-")
    # print("split_date: ", split_date)
    month = (
        split_date[1].replace("0", "")
        if split_date[1].startswith("0")
        else split_date[1]
    )
    new_date = f"{months[month]} {split_date[2]}, {split_date[0]}"
    return new_date


class BlogPostService:
    """
    Blog Post Service
    """

    # ++++++++++++++++++ ADMINS ++++++++++++++++++++++++++++

    async def admin_create_new_post(
        self,
        schema: NewPostRequestSchema,
        request: CustomRequest,
    ) -> NewPostResponseSchema:
        """
        Creates a new post
        """
        session, claims = get_claims_and_session(request)

        is_draft_count = await blog_post_repo.count(
            session=session, owner_id=claims.user_id, is_draft=True
        )

        if is_draft_count > 10:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Only 10 Draft blogs"
            )

        new_blog = await blog_post_repo.create(
            session=session,
            post_data={
                "image": schema.image and schema.image.encoded_string(),
                "title": schema.title,
                "content": schema.content,
                "owner_id": claims.user_id,
                "is_draft": schema.is_draft,
            },
        )

        return NewPostResponseSchema(
            data=PostsBaseSchema(
                id=new_blog.id,
            )
        )

    async def admin_edit_post(
        self,
        request: CustomRequest,
        schema: EditPostRequestSchema,
        post_id: str,
    ) -> EditPostResponseSchema:
        """
        Edit a post
        """
        session, claims = get_claims_and_session(request)
        post_exists = await blog_post_repo.fetch(session=session, post_id=post_id)

        if not post_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Blog Post not found"
            )
        if post_exists.owner_id != claims.user_id:
            # if claims.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough privilege to perform action",
            )
        if schema.content:
            post_exists.content = schema.content  # type: ignore
        if schema.title:
            post_exists.title = schema.title  # type: ignore
        if schema.is_draft is not None:
            post_exists.is_draft = schema.is_draft  # type: ignore
        if schema.image:
            post_exists.image = schema.image.encoded_string()  # type: ignore

        session.add(post_exists)
        await session.commit()
        await session.refresh(post_exists)
        return EditPostResponseSchema(
            data=PostsBaseSchema(
                title=post_exists.title,
                id=post_exists.id,
                is_draft=post_exists.is_draft,
                date=validate_fields(post_exists.created_at),
                image=post_exists.image,
                content=post_exists.content,
            )
        )

    async def admin_fetch_all_posts(
        self,
        request: CustomRequest,
        page: int,
        limit: int,
        is_draft: Optional[bool] = None,
    ) -> GetPostsResponseSchema:
        """
        Fetch all FAQs.

        Args:
            request (CustomRequest): The request object.
            page (int): The current page.
            limit (int): The number of faqs per page.
        Returns:
            GetPostsResponseSchema
        """
        session, claims = get_claims_and_session(request)

        posts, count = await blog_post_repo.fetch_all(
            session=session,
            offset=(limit * page - limit),
            limit=limit,
            is_draft=is_draft,
            owner_id=claims.user_id,
        )

        return GetPostsResponseSchema(
            data=[
                PostsBaseSchema(
                    title=post.title,
                    id=post.id,
                    is_draft=post.is_draft,
                    date=validate_fields(post.created_at),
                    image=post.image,
                )
                for post in posts
            ],
            page=page,
            limit=limit,
            pages=(1 if count == 0 else math.ceil(count / limit)),
            total=count,
        )

    async def admin_get_post(
        self, request: CustomRequest, post_id: str
    ) -> GetPostResponseSchema:
        """
        Retrieves a single Post by ID
        """
        session, claims = get_claims_and_session(request)

        post_exists = await blog_post_repo.fetch(
            session=session,
            post_id=post_id,
        )

        if not post_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Blog Post not found"
            )
        if post_exists.owner_id != claims.user_id:
            # if claims.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough privilege to perform action",
            )

        return GetPostResponseSchema(
            data=PostsBaseSchema(
                title=post_exists.title,
                id=post_exists.id,
                is_draft=post_exists.is_draft,
                date=validate_fields(post_exists.created_at),
                image=post_exists.image,
                content=post_exists.content,
            )
        )

    async def admin_delete_post(
        self, request: CustomRequest, post_id: str
    ) -> DeletePostResponseSchema:
        """
        Delete a post
        """
        session, claims = get_claims_and_session(request)
        post_exists = await blog_post_repo.fetch(session=session, post_id=post_id)

        if not post_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Blog Post not found"
            )
        if post_exists.owner_id != claims.user_id:
            # if claims.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough privilege to perform action",
            )
        await blog_post_repo.delete(session=session, post_id=post_id)

        return DeletePostResponseSchema()

    # ++++++++++++++++++ ALL USERS ++++++++++++++++++++++++++++
    async def fetch_all_posts(
        self,
        request: CustomRequest,
        session: AsyncSession,
        page: int,
        limit: int,
    ) -> GetPostsResponseSchema:
        """
        Fetch all FAQs.

        Args:
            request (CustomRequest): The request object.
            page (int): The current page.
            limit (int): The number of faqs per page.
        Returns:
            GetPostsResponseSchema
        """

        posts, count = await blog_post_repo.fetch_all(
            session=session,
            offset=(limit * page - limit),
            limit=limit,
            is_draft=False,
        )

        return GetPostsResponseSchema(
            data=[
                PostsBaseSchema(
                    title=post.title,
                    id=post.id,
                    date=validate_fields(post.created_at),
                    image=post.image,
                    content=post.content,
                )
                for post in posts
            ],
            page=page,
            limit=limit,
            pages=(1 if count == 0 else math.ceil(count / limit)),
            total=count,
        )

    async def get_post(
        self, request: CustomRequest, session: AsyncSession, post_id: str
    ) -> GetPostResponseSchema:
        """
        Retrieves a single Post by ID
        """
        post_exists = await blog_post_repo.fetch(
            session=session,
            post_id=post_id,
            is_draft=False,
        )
        if not post_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Blog Post not found"
            )

        return GetPostResponseSchema(
            data=PostsBaseSchema(
                title=post_exists.title,
                id=post_exists.id,
                date=validate_fields(post_exists.created_at),
                image=post_exists.image,
                content=post_exists.content,
            )
        )


blog_post_service = BlogPostService()
