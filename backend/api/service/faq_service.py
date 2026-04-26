"""
FAQs Service
"""

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.repository.faq_repo import faq_repo
from api.schema.faq_schema import (
    FAQsBase,
    AddFAQsRequestSchema,
    AddFAQsResponseSchema,
    FetchFAQsResponseSchema,
    DeleteFAQsRequestSchema,
    DeleteFAQsResponseSchema,
)
from api.schema.default_response_schema import CustomRequest
from api.utils.get_session_claims_from_request import get_claims_and_session


class FAQsService:
    """
    FAQs Service
    """

    async def create_new_faq(
        self,
        schema: AddFAQsRequestSchema,
        request: CustomRequest,
    ) -> AddFAQsResponseSchema:
        """
        Add a new FAQ.

        Args:
            request (CustomRequest): The request object.
            schema (AddFAQsRequestSchema): The request payload.
        Returns:
            AddFAQsResponseSchema
        """
        session, _ = get_claims_and_session(request)
        add_to_session = []
        for faq in schema.faqs:
            new_faq = await faq_repo.create(
                session=session, faq_data=faq.model_dump(), commit=False
            )
            add_to_session.append(new_faq)
        session.add_all(add_to_session)
        await session.commit()
        return AddFAQsResponseSchema(
            data=[
                FAQsBase.model_validate(fq, from_attributes=True)
                for fq in add_to_session
            ]
        )

    async def fetch_all_faqs(
        self,
        request: CustomRequest,
        session: AsyncSession,
        page: int,
        limit: int,
    ) -> FetchFAQsResponseSchema:
        """
        Fetch all FAQs.

        Args:
            request (CustomRequest): The request object.
            page (int): The current page.
            limit (int): The number of faqs per page.
        Returns:
            FetchFAQsResponseSchema
        """

        faqs = await faq_repo.fetch_all(
            session=session, offset=(limit * page - limit), limit=limit
        )

        return FetchFAQsResponseSchema(
            data=[FAQsBase.model_validate(fq, from_attributes=True) for fq in faqs]
        )

    async def delete_faqs(
        self,
        request: CustomRequest,
        schema: DeleteFAQsRequestSchema,
    ) -> DeleteFAQsResponseSchema:
        """
        Fetch all FAQs.

        Args:
            request (CustomRequest): The request object.
            schema (DeleteFAQsRequestSchema): The request payload.
        Returns:
            DeleteFAQsResponseSchema
        """
        session, _ = get_claims_and_session(request)

        for faq_id in schema.faq_ids:
            faq_exists = await faq_repo.fetch(
                session=session, faq_id=faq_id, attributes=["id"]
            )
            if not faq_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"FAQ with id {faq_id} not found",
                )
            await faq_repo.delete(session=session, faq_id=faq_id, commit=False)

        await session.commit()

        return DeleteFAQsResponseSchema()


faqs_service = FAQsService()
