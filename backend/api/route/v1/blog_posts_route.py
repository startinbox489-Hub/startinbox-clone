"""
Blog Post Route
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from api.schema.blog_posts_schema import GetPostsResponseSchema, GetPostResponseSchema
from api.service.blog_post_service import blog_post_service
from api.database.sql_database import sql_database
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


blog_post_router = APIRouter(
    tags=["BLOG POSTS"],
    prefix="/posts",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "5/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@blog_post_router.get(
    "",
    response_model=GetPostsResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def retrieve_all_posts(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    page: int = Query(ge=1, default=1),
) -> GetPostsResponseSchema:
    """
    Retrieve all Posts
    """
    return await blog_post_service.fetch_all_posts(
        page=page, request=request, limit=10, session=session
    )


@blog_post_router.get(
    "/{post_id}",
    response_model=GetPostResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def retrieve_post(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    post_id: str = Path(min_length=1, max_length=60),
) -> GetPostResponseSchema:
    """
    Retrieve Post by id
    """
    return await blog_post_service.get_post(
        post_id=post_id, request=request, session=session
    )
