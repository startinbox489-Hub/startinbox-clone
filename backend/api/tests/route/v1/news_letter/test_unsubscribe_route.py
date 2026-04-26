"""
Test news letter unsub  route
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


from api.repository.news_letter_repo import news_letter_repo


class TestNewsLetterUnSubRoute:
    """
    Test news letter unsub Route
    """

    @pytest.mark.asyncio
    async def test_unsubscribe(
        self, app_sync_client: TestClient, async_db_session: AsyncSession
    ):
        """
        test unsubscribe  existing sub email
        """
        with patch(
            "api.service.mailchimp_service.mailchimp_service.add_subscribers",
            return_value={"success": True},
        ):
            with patch(
                "api.service.mailchimp_service.mailchimp_service.remove_subscribers",
                return_value={"success": True},
            ):
                with patch(
                    "api.service.resend_email_service.resend_email_service.send_email",
                    return_value={"id": "e3e23r24r4t35t35", "status": True},
                ):
                    sub_response = app_sync_client.post(
                        "/api/v1/news-letter", json={"email": "jayson1@gmail.com"}
                    )
                    assert sub_response.status_code == 201

                    await async_db_session.flush()
                    news_letter_sub = await news_letter_repo.fetch(
                        session=async_db_session, email="jayson1@gmail.com"
                    )
                    assert news_letter_sub

                    unsub_response = app_sync_client.patch(
                        "/api/v1/news-letter",
                        json={
                            "newsletter_hash": news_letter_sub.newsletter_hash,
                            "reason": "Too many email",
                        },
                    )
                    assert unsub_response.status_code == 200

                    response = app_sync_client.post(
                        "/api/v1/news-letter", json={"email": "jayson1@gmail.com"}
                    )

                    assert response.status_code == 201

                    unsub_response = app_sync_client.patch(
                        "/api/v1/news-letter",
                        json={"email": news_letter_sub.newsletter_hash},
                    )
                    assert unsub_response.status_code == 422
