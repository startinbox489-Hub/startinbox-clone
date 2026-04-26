"""
Testimonials Route
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from api.schema.testimonials_schema import (
    FetchTestimonialResponseSchema,
    AddTestimonialRequestSchema,
    AddTestimonialResponseSchema,
)
from api.service.testimonials_service import testimonial_service
from api.database.sql_database import sql_database
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address
from api.service.auth_service import auth_service


testimonials_router = APIRouter(
    tags=["TESTIMONIALS"],
    prefix="/testimonials",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "5/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@testimonials_router.get(
    "",
    response_model=FetchTestimonialResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def retrieve_all_testimonials(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    page: int = Query(ge=1, le=50, default=1),
    limit: int = Query(ge=1, le=50, default=50),
) -> FetchTestimonialResponseSchema:
    """
    Retrieve all testimonials
    """
    return await testimonial_service.fetch_all_testimonial(
        page=page, request=request, limit=limit, session=session
    )


@testimonials_router.post(
    "",
    response_model=AddTestimonialResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def add_new_testimonial(
    request: CustomRequest,
    schema: AddTestimonialRequestSchema,
) -> AddTestimonialResponseSchema:
    """
    Add a new testimonial
    """
    return await testimonial_service.add_testimonials(request=request, schema=schema)
