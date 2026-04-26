"""
Test Index module
"""

import pytest
from fastapi.testclient import TestClient


class TestIndex:
    """
    Test Index
    """

    @pytest.mark.asyncio
    async def test_index(self, app_sync_client: TestClient):
        """
        Tests success / route
        """

        # register first user
        response = app_sync_client.get(url="/")
        assert response.status_code == 200
