"""
Test auth google signup route
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from pydantic import HttpUrl
import sqlalchemy as sa

from api.schema.default_response_schema import GoogleIdToken
from api.repository.news_letter_repo import news_letter_repo
from api.repository.user_subscription_repo import user_subscription_repo


class TestAuthGoogleSignupRoute:
    """
    Test auth google signup Route
    """

    @pytest.mark.asyncio
    async def test_a_google_sign_up_user(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test a google sign up user
        """

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonsigningoogle@gmail.com",
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

            assert response.headers.get("x-refresh-token") is not None

            news_letter_subbed = await news_letter_repo.fetch(
                session=async_db_session,
                email=data["data"]["user"]["email"],
            )

            assert news_letter_subbed is not None
            assert news_letter_subbed.is_unsubscribed is False
            assert news_letter_subbed.unsubscribed_at is None

            user_sub = await user_subscription_repo.fetch(
                session=async_db_session,
                is_current=True,
                user_id=data["data"]["user"]["id"],
            )
            await async_db_session.refresh(user_sub)

            assert user_sub is not None

    @pytest.mark.asyncio
    async def test_b_existing_email(self, app_sync_client: TestClient):
        """
        test existing email
        """

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonsigningoogle@gmail.com",
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
                "/api/v1/auth/signup/google",
                json={
                    "id_token": "eweoifkeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejieweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqej",
                    "agreed_to_terms": True,
                },
            )

            assert response.status_code == 201

            data = response.json()

            assert data["message"] == "Signin success"
            assert data["data"]["token"]["access_token"] is not None
            assert isinstance(data["data"]["token"]["expires_in"], int)

            assert data["data"]["user"]["id"] is not None

    @pytest.mark.asyncio
    async def test_c_subscribe_unsubscribed_user_on_signup(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test subscribe unsubscribed user on signup
        """

        news_letter_subbed = await news_letter_repo.create(
            session=async_db_session,
            news_letter_data={
                "email": "johnsonsigningooglenews@gmail.com",
                "name": "Johnson Dennis",
                "is_unsubscribed": True,
                "unsubscribed_at": sa.func.now(),
            },
        )

        assert news_letter_subbed.is_unsubscribed is True

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonsigningooglenews@gmail.com",
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
                "/api/v1/auth/signup/google",
                json={
                    "id_token": "eweoifkeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejieweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqej",
                    "agreed_to_terms": True,
                },
            )

            assert response.status_code == 201

            data = response.json()

            print("data: ", data)

            assert data["message"] == "Signin success"
            assert data["status"] == "success"

            assert data["data"]["token"]["access_token"] is not None
            assert isinstance(data["data"]["token"]["expires_in"], int)

            assert data["data"]["user"]["id"] is not None

            assert response.headers.get("x-refresh-token") is not None

            news_letter_subbed = await news_letter_repo.fetch(
                session=async_db_session,
                email=data["data"]["user"]["email"],
            )

            await async_db_session.refresh(news_letter_subbed)

            assert news_letter_subbed is not None
            assert news_letter_subbed.is_unsubscribed is False
            assert news_letter_subbed.unsubscribed_at is None

            user_sub = await user_subscription_repo.fetch(
                session=async_db_session,
                is_current=True,
                user_id=data["data"]["user"]["id"],
            )
            await async_db_session.refresh(user_sub)

            assert user_sub is not None
