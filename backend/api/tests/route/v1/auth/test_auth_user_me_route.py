"""
Test auth user me route
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from pydantic import HttpUrl

from api.schema.default_response_schema import GoogleIdToken
from api.repository.user_repo import user_repository


class TestAuthUserMeRoute:
    """
    Test auth user data Route
    """

    @pytest.mark.asyncio
    async def test_a_get_user_data(self, app_sync_client: TestClient, async_db_session):
        """
        test get user data
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonuserdata@gmail.com",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonuserdata@gmail.com",
            sub="12345qdee210",
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

            response2 = app_sync_client.get("/api/v1/auth/user/me")

            assert response2.status_code == 200

            data2 = response2.json()

            assert data2["data"]["id"] == new_user.id
            assert data2["data"]["email"] == new_user.email
