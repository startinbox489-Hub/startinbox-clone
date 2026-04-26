"""
Test auth signout route
"""

from fastapi.testclient import TestClient
import pytest


class TestAuthSignOutRoute:
    """
    Test auth signout Route
    """

    @pytest.mark.asyncio
    async def test_a_sign_out_user(self, app_sync_client: TestClient):
        """
        test a sign out user
        """

        req_data = {
            "email": "johnsonsignout@gmail.com",
            "idempotency_key": "12121212-1a12-1212-1212-s21212121212",
            "phone_number": "+2347065757200",
            "agreed_to_terms": True,
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
        }

        reg_response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert reg_response.status_code == 201

        login_response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": req_data["email"], "password": req_data["password"]},
        )

        assert login_response.status_code == 200
        assert login_response.cookies.get("access_token") is not None
        assert login_response.cookies.get("refresh_token") is not None

        login_data = login_response.json()
        print("login_data: ", login_data)

        access_token = login_data["data"]["token"]["access_token"]

        signout_response = app_sync_client.delete(
            "/api/v1/auth/signout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert signout_response.status_code == 200

        signout_data = signout_response.json()
        print("signout_data: ", signout_data)

        assert signout_data["message"] == "Signout success"

    @pytest.mark.asyncio
    async def test_b_sign_out_already_signed_out_user(
        self, app_sync_client: TestClient
    ):
        """
        test sign out already signed out user
        """

        req_data = {
            "email": "johnsonsignout2@gmail.com",
            "idempotency_key": "1212d212-1a12-1212-1212-s21212121212",
            "phone_number": "+2347000757200",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "agreed_to_terms": True,
        }

        reg_response = app_sync_client.post("/api/v1/auth/signup", json=req_data)

        assert reg_response.status_code == 201

        login_response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": req_data["email"], "password": req_data["password"]},
        )

        assert login_response.status_code == 200

        login_data = login_response.json()
        print("login_data: ", login_data)

        access_token = login_data["data"]["token"]["access_token"]

        signout_response = app_sync_client.delete(
            "/api/v1/auth/signout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert signout_response.status_code == 200

        signout_data = signout_response.json()
        print("signout_data: ", signout_data)

        assert signout_data["message"] == "Signout success"

        # signout again

        signout_response2 = app_sync_client.delete(
            "/api/v1/auth/signout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert signout_response2.status_code == 401

        signout_data2 = signout_response2.json()
        print("signout_data2: ", signout_data2)

        assert signout_data2["message"] == "expired token"

    @pytest.mark.asyncio
    async def test_c_missing_header(self, app_sync_client: TestClient):
        """
        test missing header
        """

        signout_response = app_sync_client.delete(
            "/api/v1/auth/signout",
        )

        assert signout_response.status_code == 401

        signout_data = signout_response.json()

        assert signout_data["message"] == "Missing access token."
