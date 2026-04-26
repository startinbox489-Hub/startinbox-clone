"""
Blog Post Route
"""

from typing import Optional

from fastapi import APIRouter, Depends, status, Query, Path
from slowapi import Limiter

from api.schema.blog_posts_schema import (
    GetPostsResponseSchema,
    GetPostResponseSchema,
    EditPostRequestSchema,
    EditPostResponseSchema,
    NewPostRequestSchema,
    NewPostResponseSchema,
    DeletePostResponseSchema,
)
from api.service.blog_post_service import blog_post_service
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address
from api.service.auth_service import auth_service


admin_blog_post_router = APIRouter(
    tags=["ADMIN BLOG POSTS"],
    prefix="/a/posts",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "5/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


# +++++++++++++++++++ ADMINS +++++++++++++++++++++++++++++
@admin_blog_post_router.get(
    "",
    response_model=GetPostsResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def admin_retrieve_all_posts(
    request: CustomRequest,
    page: int = Query(ge=1, default=1),
    limit: int = Query(ge=1, default=10, le=50),
    is_draft: Optional[bool] = Query(default=None),
) -> GetPostsResponseSchema:
    """
    Retrieve all Admin specific Posts
    """
    return await blog_post_service.admin_fetch_all_posts(
        page=page, request=request, limit=limit, is_draft=is_draft
    )


@admin_blog_post_router.post(
    "",
    response_model=NewPostResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def admin_create_posts(
    request: CustomRequest,
    schema: NewPostRequestSchema,
) -> NewPostResponseSchema:
    """
    Create Posts
    """
    return await blog_post_service.admin_create_new_post(request=request, schema=schema)


@admin_blog_post_router.put(
    "/{post_id}",
    response_model=EditPostResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def admin_edit_post(
    post_id: str,
    request: CustomRequest,
    schema: EditPostRequestSchema,
) -> EditPostResponseSchema:
    """
    Edit Admin Specific Posts
    """
    return await blog_post_service.admin_edit_post(
        request=request, schema=schema, post_id=post_id
    )


@admin_blog_post_router.get(
    "/{post_id}",
    response_model=GetPostResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def admin_retrieve_post(
    request: CustomRequest,
    post_id: str = Path(min_length=1, max_length=60),
) -> GetPostResponseSchema:
    """
    Retrieve Post by id
    """
    return await blog_post_service.admin_get_post(post_id=post_id, request=request)


@admin_blog_post_router.delete(
    "/{post_id}",
    response_model=DeletePostResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_admin)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def admin_delete_post(
    request: CustomRequest,
    post_id: str = Path(min_length=1, max_length=60),
) -> DeletePostResponseSchema:
    """
    Delete Post by id
    """
    return await blog_post_service.admin_delete_post(post_id=post_id, request=request)
