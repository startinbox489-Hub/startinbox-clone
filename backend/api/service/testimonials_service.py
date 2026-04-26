"""
Testimonial Service
"""

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.repository.testimonials_repo import testimonial_repo
from api.schema.testimonials_schema import (
    TestimonialBase,
    FetchTestimonialResponseSchema,
    AddTestimonialRequestSchema,
    AddTestimonialResponseSchema,
)
from api.schema.default_response_schema import CustomRequest
from api.utils.task_logger import create_logger
from api.utils.get_session_claims_from_request import get_claims_and_session
from api.repository.user_repo import user_repository
from api.repository.startup_ideas_repo import startup_ideas_repo

logger = create_logger(":: TestimonialService ::")


class TestimonialService:
    """
    Testimonial Service
    """

    async def fetch_all_testimonial(
        self,
        request: CustomRequest,
        session: AsyncSession,
        page: int,
        limit: int,
    ) -> FetchTestimonialResponseSchema:
        """
        Fetch all Testimonial.

        Args:
            request (CustomRequest): The request object.
            page (int): The current page.
            limit (int): The number of Testimonial per page.
        Returns:
            FetchTestimonialResponseSchema
        """
        try:

            testimonials = await testimonial_repo.fetch_all(
                session=session, offset=(limit * page - limit), limit=limit
            )

            return FetchTestimonialResponseSchema(
                data=[
                    TestimonialBase.model_validate(testimonial, from_attributes=True)
                    for testimonial in testimonials
                ]
            )
        except Exception as exc:
            logger.error("error fetching testimonials: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def add_testimonials(
        self, schema: AddTestimonialRequestSchema, request: CustomRequest
    ) -> AddTestimonialResponseSchema:
        """
        Adds a new etstimonial.
        """
        try:
            session, claims = get_claims_and_session(request)
            idea_exists = await startup_ideas_repo.fetch(
                session=session,
                ideas_id=schema.idea_id,
                attributes=["id"],
                user_id=claims.user_id,
            )
            if not idea_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Idea with the rovided ID not found",
                )
            userExists = await user_repository.fetch_by_email(
                session=session, email=claims.email
            )
            assert userExists is not None
            testimonial_data = schema.model_dump()
            testimonial_data["firstname"] = userExists.firstname or ""
            testimonial_data["lastname"] = userExists.lastname or ""
            testimonial_data["image_url"] = userExists.profile_photo or ""
            await testimonial_repo.create(
                session=session,
                testimonial_data=testimonial_data,
                commit=True,
            )
            return AddTestimonialResponseSchema()
        except HTTPException as exc:
            raise exc
        except Exception as exc:
            logger.error("error adding testimonials: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc


testimonial_service = TestimonialService()
