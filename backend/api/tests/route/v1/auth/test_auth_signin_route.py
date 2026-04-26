"""
Test auth signin route
"""

from fastapi.testclient import TestClient
import pytest


class TestAuthSigninRoute:
    """
    Test auth signin Route
    """

    @pytest.mark.asyncio
    async def test_a_sign_in_user(self, app_sync_client: TestClient):
        """
        test a sign in user
        """

        req_data = {
            "email": "johnsonsignin@gmail.com",
            "idempotency_key": "12121212-1212-1212-1212-s21212121212",
            "phone_number": "+2347065757234",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "agreed_to_terms": True,
        }

        response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response.status_code == 201

        response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": req_data["email"], "password": req_data["password"]},
        )

        assert response.status_code == 200

        data = response.json()

        print("data: ", data)

        assert data["message"] == "Signin success"
        assert data["status"] == "success"

        assert response.headers.get("x-refresh-token") is not None

    @pytest.mark.asyncio
    async def test_b_non_existing_email(self, app_sync_client: TestClient):
        """
        test non existing email
        """

        req_data = {
            "email": "fake@gmail.com",
            "idempotency_key": "12121212-1212-1212-1212-2323232321",
            "phone_number": "+23470657570234",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
        }

        response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": req_data["email"], "password": req_data["password"]},
        )

        assert response.status_code == 403

        data = response.json()

        assert data["message"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_c_invalid_password(self, app_sync_client: TestClient):
        """
        test invalid password
        """

        req_data = {
            "email": "johnsonpassword@gmail.com",
            "idempotency_key": "12121212-1212-1212-12q12-s21212121212",
            "phone_number": "+2347065750034",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "agreed_to_terms": True,
        }

        response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert response.status_code == 201

        response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": req_data["email"], "password": "Fa21#kepassword"},
        )

        assert response.status_code == 403

        data = response.json()

        assert data["message"] == "Invalid credentials"
