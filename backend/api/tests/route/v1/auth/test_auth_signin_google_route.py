"""
Test auth google signin route
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from pydantic import HttpUrl

from api.schema.default_response_schema import GoogleIdToken
from api.repository.user_repo import user_repository


class TestAuthGoogleSigninRoute:
    """
    Test auth google signin Route
    """

    @pytest.mark.asyncio
    async def test_a_google_sign_in_user(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test a google sign in user
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonsigningoogle@gmail.com",
                "phone_number": "+2347022225757",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonsigningoogle@gmail.com",
            sub="1234567210",
            aud="your_client_id.apps.googleusercontent.com",
            family_name="Dennis",
            given_name="Johnson",
            iss="your_client_id",
            name="Johnson Dennis",
            picture=HttpUrl("https://gmail.com"),
        )

        with patch(
            "api.service.auth_service.auth_service.verify_google_id_token",
            return_value=req_data,
        ):

            response = app_sync_client.post(
                "/api/v1/auth/signin/google",
                json={
                    "id_token": "eweoifkeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejieweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqej",
                    "agreed_to_terms": True,
                },
            )

            assert response.status_code == 200

            data = response.json()

            print("data: ", data)

            assert data["message"] == "Signin success"
            assert data["status"] == "success"

            assert data["data"]["token"]["access_token"] is not None
            assert isinstance(data["data"]["token"]["expires_in"], int)

            assert data["data"]["user"]["id"] is not None
            assert data["data"]["user"]["id"] == new_user.id

            assert response.headers.get("x-refresh-token") is not None

    @pytest.mark.asyncio
    async def test_c_non_existing_email(self, app_sync_client: TestClient):
        """
        test non existing email
        """

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonsigningooglenot@gmail.com",
            sub="1234567890",
            aud="your_client_id.apps.googleusercontent.com",
            family_name="Dennis",
            given_name="Johnson",
            iss="your_client_id",
            name="Johnson Dennis",
            picture=HttpUrl("https://gmail.com"),
        )

        with patch(
            "api.service.auth_service.auth_service.verify_google_id_token",
            return_value=req_data,
        ):

            response = app_sync_client.post(
                "/api/v1/auth/signin/google",
                json={
                    "id_token": "eweoifkeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejieweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqej"
                },
            )

            assert response.status_code == 200

            # data = response.json()

            # assert (
            #     data["message"]
            #     == "No account found for this email. Please sign up via /api/v1/auth/signup/google"
            # )
