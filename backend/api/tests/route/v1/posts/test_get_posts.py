"""
Test Posts  route
"""

import datetime
from fastapi.testclient import TestClient
import pytest

from api.repository.blog_posts_repo import blog_post_repo


class TestPostsRoute:
    """
    Test Posts Route
    """

    @pytest.mark.asyncio
    async def test_a_when_fetchig_posts(
        self, app_sync_client: TestClient, async_db_session
    ):
        """
        test when fetching posts returns 200
        """
        await blog_post_repo.create(
            session=async_db_session,
            post_data={
                "title": "some title",
                "content": "some content",
                "image": "some image",
            },
        )

        response = app_sync_client.get(
            "/api/v1/posts",
        )

        assert response.status_code == 200

        data = response.json()

        print("data: ", data)

        assert data["message"] == "Posts Retrieved successfully"
        assert data["status"] == "success"

        assert isinstance(data["data"], list) and len(data["data"]) > 0
