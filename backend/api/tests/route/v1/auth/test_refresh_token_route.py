"""
Test auth refresh tokens route
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from pydantic import HttpUrl

from api.schema.default_response_schema import GoogleIdToken
from api.repository.user_session_repo import user_session_repo


class TestRefreshTokensRoute:
    """
    Test auth refresh tokens Route
    """

    @pytest.mark.asyncio
    async def test_a_refresh_tokens_success(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test a refresh tokens flow
        """

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonrefresh@gmail.com",
            sub="1234567890",
            aud="your_client_id.apps.googleusercontent.com",
            family_name="Dennis",
            given_name="Johnson",
            iss="your_client_id",
            name="Johnson Dennis",
            picture=HttpUrl(url="https://gmail.com"),
        )

        # 1. Signup user with Google OAuth (patched verification)

        with patch(
            "api.service.auth_service.auth_service.verify_google_id_token",
            return_value=req_data,
        ):

            response = app_sync_client.post(
                "/api/v1/auth/signup/google",
                json={
                    "id_token": "eweoifkeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejieweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqej",
                    "agreed_to_terms": True,
                },
            )

            assert response.status_code == 201

            data = response.json()

            # print("data: ", data)

            assert data["message"] == "Signin success"
            assert data["status"] == "success"

            assert data["data"]["token"]["access_token"] is not None
            assert isinstance(data["data"]["token"]["expires_in"], int)

            assert data["data"]["user"]["id"] is not None

            #  2. Assert refresh-token is returned
            assert response.headers.get("x-refresh-token") is not None
            assert response.cookies.get("access_token") is not None
            assert response.cookies.get("refresh_token") is not None

            old_refresh_token = response.headers.get("x-refresh-token")
            old_access_token = data["data"]["token"]["access_token"]

            # 3. successfully refresh tokens
            response2 = app_sync_client.post(
                "/api/v1/auth/refresh-tokens",
                headers={"X-REFRESH-TOKEN": old_refresh_token},
                cookies={"refresh_token": old_refresh_token},
            )
            print("res: ", response2.json())

            assert response2.status_code == 201

            data2 = response2.json()

            assert data2["message"] == "Signin success"
            assert data2["status"] == "success"

            assert data2["data"]["token"]["access_token"] is not None
            assert isinstance(data2["data"]["token"]["expires_in"], int)

            assert data2["data"]["user"]["id"] is not None

            assert response2.headers.get("x-refresh-token") is not None
            new_refresh_token = response2.headers.get("x-refresh-token")

            # 4. Assert token rotation works (old != new)
            assert old_refresh_token != new_refresh_token

            # 5. Reuse old refresh-token → should fail
            # raise 401 when using old refresh token
            response3 = app_sync_client.post(
                "/api/v1/auth/refresh-tokens",
                headers={"X-REFRESH-TOKEN": old_refresh_token},
            )

            assert response3.status_code == 401

            data3 = response3.json()

            assert data3["message"] == "Unauthorized access. Revoked refresh-token."

            # 6. Check revoked user session
            session_exists = await user_session_repo.fetch_all(
                session=async_db_session,
                user_id=data["data"]["user"]["id"],
                is_revoked=True,
            )

            assert len(session_exists) == 1

            assert session_exists[0].is_revoked is True
            assert session_exists[0].revoked_at is not None

            # raise 401 when using old access_token
            # TODO: Add this test when protected route is created
