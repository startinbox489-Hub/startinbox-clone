"""
AddsOn Service
"""

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.repository.adds_on_repo import adds_on_service_repo
from api.schema.adds_on_service_schema import (
    AddsOnBase,
    AddAddsOnRequestSchema,
    AddAddsOnResponseSchema,
    FetchAddsOnResponseSchema,
    DeleteAddsOnRequestSchema,
    DeleteAddsOnResponseSchema,
)
from api.schema.default_response_schema import CustomRequest
from api.utils.task_logger import create_logger


logger = create_logger(":: AddsOnServiceException ::")


class AddsOnServiceException(Exception):
    """
    AddsOnServiceException
    """

    def __init__(self, message: str = "Error in Adds On service") -> None:
        """
        Constructor
        """
        super().__init__(message)


class AddsOnService:
    """
    AddsOn Service
    """

    async def create_new_adds_on(
        self,
        schema: AddAddsOnRequestSchema,
        request: CustomRequest,
        session: AsyncSession,
    ) -> AddAddsOnResponseSchema:
        """
        Add a new FAQ.

        Args:
            request (CustomRequest): The request object.
            schema (AddAddsOnRequestSchema): The request payload.
        Returns:
            AddAddsOnResponseSchema
        """
        try:
            add_to_session = []
            for adds_on in schema.adds_on:
                new_adds_on = await adds_on_service_repo.create(
                    session=session, adds_on_data=adds_on.model_dump(), commit=False
                )
                add_to_session.append(new_adds_on)
            session.add_all(add_to_session)
            await session.commit()
            return AddAddsOnResponseSchema(
                data=[
                    AddsOnBase.model_validate(fq, from_attributes=True)
                    for fq in add_to_session
                ]
            )
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error creating new adds on service: %s", str(exc))
            raise AddsOnServiceException("Error creating new adds on service") from exc

    async def fetch_all_adds_on(
        self,
        request: CustomRequest,
        session: AsyncSession,
        page: int,
        limit: int,
    ) -> FetchAddsOnResponseSchema:
        """
        Fetch all AddsOn.

        Args:
            request (CustomRequest): The request object.
            page (int): The current page.
            limit (int): The number of AddsOn per page.
        Returns:
            FetchAddsOnResponseSchema
        """

        try:

            adds_on = await adds_on_service_repo.fetch_all(
                session=session, offset=(limit * page - limit), limit=limit
            )

            return FetchAddsOnResponseSchema(
                data=[
                    AddsOnBase.model_validate(fq, from_attributes=True)
                    for fq in adds_on
                ]
            )
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error fetching all adds on services: %s", str(exc))
            raise AddsOnServiceException("Error fetching all adds on services") from exc

    async def delete_adds_on(
        self,
        request: CustomRequest,
        schema: DeleteAddsOnRequestSchema,
        session: AsyncSession,
    ) -> DeleteAddsOnResponseSchema:
        """
        Fetch all AddsOn.

        Args:
            request (CustomRequest): The request object.
            schema (DeleteAddsOnRequestSchema): The request payload.
        Returns:
            DeleteAddsOnResponseSchema
        """
        try:

            for adds_on_id in schema.adds_on_ids:
                faq_exists = await adds_on_service_repo.fetch(
                    session=session, adds_on_id=adds_on_id, attributes=["id"]
                )
                if not faq_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Adds-On-Service with id {adds_on_id} not found",
                    )
                await adds_on_service_repo.delete(
                    session=session, adds_on_id=adds_on_id, commit=False
                )

            await session.commit()

            return DeleteAddsOnResponseSchema()
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error deleting adds on service: %s", str(exc))
            raise AddsOnServiceException("Error deleting adds on service") from exc


adds_on_service = AddsOnService()
