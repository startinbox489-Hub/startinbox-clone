"""
Test Post  route
"""

from fastapi.testclient import TestClient
import pytest

from api.repository.blog_posts_repo import blog_post_repo


class TestPostRoute:
    """
    Test Post Route
    """

    @pytest.mark.asyncio
    async def test_a_when_fetching_post(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test when fetching posts returns 200
        """
        new_post = await blog_post_repo.create(
            session=async_db_session,
            post_data={
                "title": "some title is here",
                "content": "some content",
                "image": "some image",
            },
        )

        response = app_sync_client.get(
            f"/api/v1/posts/{new_post.id}",
        )

        assert response.status_code == 200

        data = response.json()

        print("data: ", data)

        assert data["message"] == "Post Retrieved successfully"
        assert data["status"] == "success"

        assert data["data"]["title"] == "some title is here"
