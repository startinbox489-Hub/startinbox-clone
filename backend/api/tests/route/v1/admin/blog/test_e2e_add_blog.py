"""
Test Admin add Post  route
"""

from fastapi.testclient import TestClient
import pytest

from api.repository.user_repo import user_repository
from api.repository.user_subscription_repo import user_subscription_repo
from api.repository.subscription_plan_repo import subscription_plan_repo


class TestAdminAddPostRoute:
    """
    Test Post Route
    """

    @pytest.mark.asyncio
    async def test_a_when_admin_create_post_retuens_201(
        self, app_sync_client: TestClient, admin_factory
    ):
        """
        test when admin create posts returns 201
        """

        new_post_data = {
            "title": "some title is here",
            "content": "some content some contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome content",
            "image": "https://url.com",
            "is_draft": True,
        }

        sign_response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": admin_factory.email, "password": "Johnson1234#"},
        )
        access_token = (sign_response.json())["data"]["token"]["access_token"]
        response = app_sync_client.post(
            "/api/v1/a/posts",
            json=new_post_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

        data = response.json()

        print("data: ", data)

        assert data["message"] == "Post created successfully"
        assert data["status"] == "success"

        assert data["data"]["id"] is not None

    @pytest.mark.asyncio
    async def test_b_when__non_admin_create_post_retuens_403(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test twhen non admin create post retuens 403
        """
        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonnonadmin@gmail.com",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
                "role": "regular",
            },
        )
        assert new_user
        sub_plan = await subscription_plan_repo.fetch(
            session=async_db_session, is_default=True, plan_idx=0
        )
        assert sub_plan is not None
        await user_subscription_repo.create(
            session=async_db_session,
            user_sub_data={
                "user_id": new_user.id,
                "subscription_plan_id": sub_plan.id,
                "is_current": True,
            },
        )
        new_post_data = {
            "title": "some title is here",
            "content": "some content some contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome contentsome content",
            "image": "https://url.com",
            "is_draft": True,
        }

        sign_response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": new_user.email, "password": "Johnson1234#"},
        )
        signin_data = sign_response.json()
        print("signin_data: ", signin_data)

        access_token = (signin_data)["data"]["token"]["access_token"]
        response = app_sync_client.post(
            "/api/v1/a/posts",
            json=new_post_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()

        print("data: ", data)
        assert data["message"] == "Not enough Privilege."
