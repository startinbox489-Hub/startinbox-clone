"""
Test news letter sub  route
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest


class TestNewsLetterSubRoute:
    """
    Test news letter sub Route
    """

    @pytest.mark.asyncio
    async def test_a_subscribe_to_news_letter(self, app_sync_client: TestClient):
        """
        test subscribe to news letter
        """
        with patch(
            "api.service.mailchimp_service.mailchimp_service.add_subscribers",
            return_value={"success": True},
        ):
            with patch(
                "api.service.resend_email_service.resend_email_service.send_email",
                return_value={"id": "e3e23r24r4t35t35", "status": True},
            ):
                response = app_sync_client.post(
                    "/api/v1/news-letter", json={"email": "jayson@gmail.com"}
                )

                assert response.status_code == 201

                data = response.json()

                print("data: ", data)

                assert data["message"] == "Subscribed to news letter succesfully"
                assert data["status"] == "success"

                assert data["data"]["email"] == "jayson@gmail.com"

    @pytest.mark.asyncio
    async def test_b_subscribe_with_existing_sub_email(
        self, app_sync_client: TestClient
    ):
        """
        test subscribe with existing sub email
        """
        with patch(
            "api.service.mailchimp_service.mailchimp_service.add_subscribers",
            return_value={"success": True},
        ):
            with patch(
                "api.service.resend_email_service.resend_email_service.send_email",
                return_value={"id": "e3e23r24r4t35t35", "status": True},
            ):
                app_sync_client.post(
                    "/api/v1/news-letter", json={"email": "jayson1@gmail.com"}
                )
                response = app_sync_client.post(
                    "/api/v1/news-letter", json={"email": "jayson1@gmail.com"}
                )

                assert response.status_code == 409

                data = response.json()

                print("data: ", data)

                assert (
                    data["message"]
                    == "This email is already subscribed to the newsletter"
                )
