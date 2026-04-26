"""
Test FAQs  route
"""

from fastapi.testclient import TestClient
import pytest

from api.repository.user_repo import user_repository
from api.model import UserModel


class TestFAQsRoute:
    """
    Test FAQs Route
    """

    @pytest.mark.asyncio
    async def test_a_when_create_faqs_by_admin_returns_201(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test when create faqs by admin returns 201
        """

        new_admin_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonadmin@gmail.com",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
                "role": "admin",
            },
        )
        assert isinstance(new_admin_user, UserModel)

        response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": "johnsonadmin@gmail.com", "password": "Johnson1234#"},
        )

        assert response.status_code == 200

        data = response.json()

        access_token = data["data"]["token"]["access_token"]

        response = app_sync_client.post(
            "/api/v1/faqs",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"faqs": [{"question": "what is it?", "answer": "it is what it is"}]},
        )

        assert response.status_code == 201

        data = response.json()

        print("data: ", data)

        assert data["message"] == "FAQs created successfully"
        assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_b_when_create_faqs_returns_403(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test when create FAQs returns 403
        """

        new_regular_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonregular@gmail.com",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        assert isinstance(new_regular_user, UserModel)

        response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": "johnsonregular@gmail.com", "password": "Johnson1234#"},
        )

        assert response.status_code == 200

        data = response.json()

        access_token = data["data"]["token"]["access_token"]

        response = app_sync_client.post(
            "/api/v1/faqs",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"question": "what is it?", "answer": "it is what it is"},
        )

        assert response.status_code == 403

        data = response.json()

        print("data: ", data)

        assert data["message"] == "Not enough Privilege."

    @pytest.mark.asyncio
    async def test_c_when_fetching_faqs_returns_200(self, app_sync_client: TestClient):
        """
        test when fetching faqs returns 200
        """

        response = app_sync_client.get(
            "/api/v1/faqs",
        )

        assert response.status_code == 200

        data = response.json()

        print("data: ", data)

        assert data["message"] == "FAQs retrieved successfully"
        assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_d_when_deleting_faqs_by_admin_returns_200(
        self,
        app_sync_client: TestClient,
        async_db_session,
    ):
        """
        test when deleting faqs by admin returns 200
        """
        await user_repository.create(
            async_db_session,
            {
                "email": "johnsonadmin2@gmail.com",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
                "role": "admin",
            },
        )

        signin_response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": "johnsonadmin2@gmail.com", "password": "Johnson1234#"},
        )

        assert signin_response.status_code == 200

        signin_ = signin_response.json()

        access_token = signin_["data"]["token"]["access_token"]

        create_response = app_sync_client.post(
            "/api/v1/faqs",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"faqs": [{"question": "what is it?", "answer": "it is what it is"}]},
        )

        assert create_response.status_code == 201

        create_data = create_response.json()

        print("create_data: ", create_data)

        faq_id = create_data["data"][0]["id"]

        delete_response = app_sync_client.patch(
            "/api/v1/faqs",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"faq_ids": [faq_id]},
        )

        assert delete_response.status_code == 200

        delete_data = delete_response.json()

        assert delete_data["message"] == "FAQs removed successfully"
        assert delete_data["status"] == "success"

    @pytest.mark.asyncio
    async def test_e_when_deleting_faqs_by_regular_returns_403(
        self,
        app_sync_client: TestClient,
        async_db_session,
    ):
        """
        test when deleting faqs by regular returns 403
        """
        await user_repository.create(
            async_db_session,
            {
                "email": "johnsonregular2@gmail.com",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        signin_response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": "johnsonregular2@gmail.com", "password": "Johnson1234#"},
        )

        assert signin_response.status_code == 200

        signin_ = signin_response.json()

        access_token = signin_["data"]["token"]["access_token"]

        delete_response = app_sync_client.patch(
            "/api/v1/faqs",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"faq_ids": ["faq_id"]},
        )

        assert delete_response.status_code == 403

        delete_data = delete_response.json()

        assert delete_data["message"] == "Not enough Privilege."
