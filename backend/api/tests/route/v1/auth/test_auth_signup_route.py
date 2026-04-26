"""
Test auth route
"""

from fastapi.testclient import TestClient
import pytest
import sqlalchemy as sa

from api.repository.news_letter_repo import news_letter_repo
from api.repository.user_subscription_repo import user_subscription_repo


class TestAuthRoute:
    """
    Test auth Route
    """

    @pytest.mark.asyncio
    async def test_a_successful_sign_up_user(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test successful sign up user
        """

        req_data = {
            "email": "johnsonsign@gmail.com",
            "idempotency_key": "12121212-1212-1212-1212-121212121212",
            "phone_number": "+2347065757575",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "agreed_to_terms": True,
        }

        response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response.status_code == 201

        data = response.json()

        print("data: ", data)

        assert data == {
            "status": "success",
            "message": "User created succesfully",
            "data": {
                "id": data["data"]["id"],
                "firstname": None,
                "lastname": None,
                "email": "johnsonsign@gmail.com",
                "phone_number": "+2347065757575",
                "created_at": data["data"]["created_at"],
            },
        }

        user_sub = await user_subscription_repo.fetch(
            session=async_db_session, is_current=True, user_id=data["data"]["id"]
        )
        await async_db_session.refresh(user_sub)

        assert user_sub is not None

        response2 = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response2.status_code == 201

        data2 = response2.json()

        print("data2: ", data2)

        assert data2["message"] == "User already created succesfully"
        assert data2["status"] == "success"

        news_letter_subbed = await news_letter_repo.fetch(
            session=async_db_session,
            email=data2["data"]["email"],
        )

        assert news_letter_subbed is not None
        assert news_letter_subbed.is_unsubscribed is False
        assert news_letter_subbed.unsubscribed_at is None

    @pytest.mark.asyncio
    async def test_c_existing_email(self, app_sync_client: TestClient):
        """
        test existing email
        """

        req_data = {
            "email": "johnsonsign@gmail.com",
            "phone_number": "+2347065757575",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "agreed_to_terms": True,
        }
        response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response.status_code == 201

        response2 = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response2.status_code == 409

        data = response2.json()

        print("data: ", data)

        assert data["message"] == "Email already in use"

    @pytest.mark.asyncio
    async def test_d_existing_phone_number(self, app_sync_client: TestClient):
        """
        test existing phone_numbe
        """

        req_data = {
            "email": "johnson123@gmail.com",
            "phone_number": "+2347065757575",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "agreed_to_terms": True,
        }
        response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response.status_code == 201

        req_data["email"] = "johnson1234@gmail.com"

        response2 = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response2.status_code == 409

        data = response2.json()

        print("data: ", data)

        assert data["message"] == "Phone Number already in use"

    @pytest.mark.asyncio
    async def test_e_subscribe_unsubscribed_user_on_signup(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test successful sign up user
        """
        news_letter_subbed = await news_letter_repo.create(
            session=async_db_session,
            news_letter_data={
                "email": "johnsonsignnewss@gmail.com",
                "name": "Johnson Dennis",
                "is_unsubscribed": True,
                "unsubscribed_at": sa.func.now(),
            },
        )

        assert news_letter_subbed.is_unsubscribed is True

        req_data = {
            "email": "johnsonsignnewss@gmail.com",
            "idempotency_key": "1sas21212-1212-1212-1212-121212121212",
            "phone_number": "+2347065700000",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "agreed_to_terms": True,
        }

        response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response.status_code == 201

        data = response.json()

        print("data: ", data)

        assert data == {
            "status": "success",
            "message": "User created succesfully",
            "data": {
                "id": data["data"]["id"],
                "firstname": None,
                "lastname": None,
                "email": "johnsonsignnewss@gmail.com",
                "phone_number": "+2347065700000",
                "created_at": data["data"]["created_at"],
            },
        }

        news_letter_subbed = await news_letter_repo.fetch(
            session=async_db_session,
            email=data["data"]["email"],
        )

        await async_db_session.refresh(news_letter_subbed)

        assert news_letter_subbed is not None
        assert news_letter_subbed.is_unsubscribed is False
        assert news_letter_subbed.unsubscribed_at is None

    @pytest.mark.asyncio
    async def test_f_missing_agree_to_terms_returns_400(
        self, app_sync_client: TestClient
    ):
        """
        test missing agree to terms returns 400
        """

        req_data = {
            "email": "johnson1222223@gmail.com",
            "phone_number": "+2347065222275",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
        }
        response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response.status_code == 422
