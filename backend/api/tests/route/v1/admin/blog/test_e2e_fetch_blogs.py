"""
Test Admin add Post  route
"""

from fastapi.testclient import TestClient
import pytest

from api.repository.user_repo import user_repository
from api.repository.user_subscription_repo import user_subscription_repo
from api.repository.subscription_plan_repo import subscription_plan_repo


class TestAdminFetchPostRoute:
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

        post_id = data["data"]["id"]

        response2 = app_sync_client.get(
            "/api/v1/a/posts",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response2.status_code == 200

        data2 = response2.json()

        print("data2: ", data2)

        assert data2["message"] == "Posts Retrieved successfully"
        assert len(data2["data"]) > 0

        response3 = app_sync_client.get(
            f"/api/v1/a/posts/{post_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response3.status_code == 200

        data3 = response3.json()

        print("data3: ", data3)

        assert data3["message"] == "Post Retrieved successfully"
        assert data3["data"]["id"] == post_id

    @pytest.mark.asyncio
    async def test_b_when_admin2_access_admin1_post_retuens_403(
        self, app_sync_client: TestClient, async_db_session, admin_factory
    ):
        """
        test twhen non admin create post retuens 403
        """
        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonnonadmin2@gmail.com",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
                "role": "admin",
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

        admin_1sign_response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": new_user.email, "password": "Johnson1234#"},
        )
        signin_data = admin_1sign_response.json()
        print("signin_data: ", signin_data)

        admin_1_access_token = (signin_data)["data"]["token"]["access_token"]

        response = app_sync_client.post(
            "/api/v1/a/posts",
            json=new_post_data,
            headers={"Authorization": f"Bearer {admin_1_access_token}"},
        )

        assert response.status_code == 201

        data = response.json()

        print("data: ", data)
        post_id = data["data"]["id"]

        # admin 2 tries to access data

        admin_2sign_response = app_sync_client.post(
            "/api/v1/auth/signin",
            json={"email": admin_factory.email, "password": "Johnson1234#"},
        )
        admin2_signin_data = admin_2sign_response.json()

        admin_2_access_token = (admin2_signin_data)["data"]["token"]["access_token"]

        admin_2_response = app_sync_client.get(
            f"/api/v1/a/posts/{post_id}",
            headers={"Authorization": f"Bearer {admin_2_access_token}"},
        )

        assert admin_2_response.status_code == 403

        assert (admin_2_response.json())[
            "message"
        ] == "Not enough privilege to perform action"
