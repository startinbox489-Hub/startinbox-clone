"""
Idea Next Step Service
"""

from fastapi import status, HTTPException, BackgroundTasks

from api.repository.idea_next_step_repo import ideas_next_step_repo
from api.repository.startup_ideas_repo import startup_ideas_repo
from api.schema.idea_next_step_schema import (
    IdeaNextStepBase,
    AddIdeaNextStepRequestSchema,
    AddIdeaNextStepResponseSchema,
)
from api.schema.default_response_schema import CustomRequest
from api.utils.get_session_claims_from_request import get_claims_and_session
from api.service.resend_email_service import resend_email_service
from api.utils.task_logger import create_logger
from api.repository.user_repo import user_repository
from api.core.config import settings

logger = create_logger()


class IdeaNextStepService:
    """
    IdeaNextStep Service
    """

    async def create_new_next_step(
        self,
        schema: AddIdeaNextStepRequestSchema,
        request: CustomRequest,
        backgroung_task: BackgroundTasks,
    ) -> AddIdeaNextStepResponseSchema:
        """
        Add a new IdeaNextStep.

        Args:
            request (CustomRequest): The request object.
            schema (AddFAQsRequestSchema): The request payload.
        Returns:
            AddIdeaNextStepResponseSchema
        """
        try:
            session, claims = get_claims_and_session(request)
            idea_exists = await startup_ideas_repo.fetch(
                session=session,
                ideas_id=schema.idea_id,
                user_id=claims.user_id,
                attributes=["id"],
            )
            if not idea_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existing Record for the provided Startup Idea",
                )

            idea_next_step_exists = await ideas_next_step_repo.fetch(
                session=session, idea_id=schema.idea_id, attributes=["user_id"]
            )
            if idea_next_step_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Next step already recorded for the selected Idea.",
                )
            next_step_data = schema.model_dump()
            next_step_data["user_id"] = claims.user_id
            new_next_step = await ideas_next_step_repo.create(
                session=session, next_step_data=next_step_data
            )
            user_exists = await user_repository.fetch_by_attrs(
                session=session,
                attributes=[
                    "firstname",
                    "email",
                ],
                email=str(claims.email),
            )

            backgroung_task.add_task(
                resend_email_service.send_email,
                to_email=claims.email,
                subject="Your Onboarding Pack is ready!",
                template_name="pm-onboarding.html",
                context_data={
                    "firstname": user_exists and user_exists.get("firstname", " "),
                    "calendly_link": settings.pm_calendly_link,
                },
            )

            return AddIdeaNextStepResponseSchema(
                data=IdeaNextStepBase.model_validate(
                    new_next_step, from_attributes=True
                )
            )
        except HTTPException as exc:
            raise exc
        except Exception as exc:
            logger.error("Error creating idea next step: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc


idea_next_step_service = IdeaNextStepService()
