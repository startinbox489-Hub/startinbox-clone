"""
NewsLetter Service
"""

import datetime
from typing import Any, Dict
from nanoid import generate

from fastapi import status, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from api.repository.news_letter_repo import news_letter_repo
from api.service.mailchimp_service import mailchimp_service
from api.schema.news_letter_schema import (
    NewsLetterBase,
    NewsLetterRequestSchema,
    NewsLetterResponseSchema,
    UnSubNewsLetterResponseSchema,
    UnSubNewsLetterRequestSchema,
)
from api.service.resend_email_service import resend_email_service
from api.core.config import settings


class NewsLetterService:
    """
    NewsLetter Service
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.repo = news_letter_repo

    async def sub_to_news_letter(
        self,
        session: AsyncSession,
        schema: NewsLetterRequestSchema,
        background_tasks: BackgroundTasks,
    ) -> NewsLetterResponseSchema:
        """
        Subscribe users to NewsLetter.

        Args:
            session (AsyncSession): The database injected async session object.
            schema (NewsLetterRequestSchema): The request payload.
        Returns:
            Something
        """
        newsletter_hash = None
        user_newsletter_sub = await self.repo.fetch(
            session=session, email=schema.email.lower()
        )
        if user_newsletter_sub and not user_newsletter_sub.is_unsubscribed:
            raise HTTPException(
                detail="This email is already subscribed to the newsletter",
                status_code=status.HTTP_409_CONFLICT,
            )
        update_data: Dict[str, Any] = {"is_unsubscribed": False}
        if schema.name:
            update_data["name"] = schema.name
        if user_newsletter_sub and user_newsletter_sub.is_unsubscribed:
            update_data["unsubscribed_at"] = None

            res = await mailchimp_service.add_subscribers(email=schema.email)
            if res.get("success") is True:
                update_data.update({"is_sub_success": True})

            user_newsletter_sub = await self.repo.update(
                session=session,
                news_letter=user_newsletter_sub,
                update_data=update_data,
            )
            newsletter_hash = user_newsletter_sub.newsletter_hash
        else:
            newsletter_hash = generate(
                alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890",
                size=40,
            )
            update_data["email"] = schema.email.lower()
            update_data["newsletter_hash"] = newsletter_hash
            res = await mailchimp_service.add_subscribers(email=schema.email)
            if res.get("success") is True:
                update_data.update({"is_sub_success": True})
            user_newsletter_sub = await self.repo.create(
                session=session,
                news_letter_data=update_data,
            )
        background_tasks.add_task(
            resend_email_service.send_email,
            to_email=schema.email,
            context_data={
                "current_year": datetime.date.year,
                "unsubscribe_link": f"{settings.client_side_url}/unsubscribe/{newsletter_hash}",
            },
            subject="Welcome to Our Newsletter!",
            template_name="newsletter-subscription.html",
        )

        return NewsLetterResponseSchema(
            data=NewsLetterBase.model_validate(
                user_newsletter_sub, from_attributes=True
            )
        )

    async def unsub_to_news_letter(
        self,
        session: AsyncSession,
        schema: UnSubNewsLetterRequestSchema,
    ) -> UnSubNewsLetterResponseSchema:
        """
        Unsubscribe users from NewsLetter.

        Args:
            session (AsyncSession): The database injected async session object.
            schema (UnSubNewsLetterRequestSchema): The request payload.
        Returns:
            Something
        """
        user_subscribed = await self.repo.fetch(
            session=session, newsletter_hash=schema.newsletter_hash
        )
        if not user_subscribed:
            raise HTTPException(
                detail="This email is not yet subscribed to the newsletter",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if user_subscribed.is_unsubscribed:
            raise HTTPException(
                detail="This email is not yet subscribed to the newsletter",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        res = await mailchimp_service.remove_subscribers(email=user_subscribed.email)
        update_data: Dict[str, Any] = {
            "is_unsubscribed": True,
            "unsubscribed_at": sa.func.now(),
        }
        if res.get("success") is True:
            update_data.update(
                {"is_sub_success": False}
            )  # email removed from mailchimp sub
        if schema.reason:
            update_data.update({"reason": schema.reason})

        user_subscribed = await self.repo.update(
            session=session,
            news_letter=user_subscribed,
            update_data=update_data,  # type: ignore
        )

        return UnSubNewsLetterResponseSchema()


news_letter_service = NewsLetterService()
