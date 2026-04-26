"""
Test sub plan route
"""

from fastapi.testclient import TestClient
import pytest


class TestSubscriptionPlanRoute:
    """
    Test sub plan Route
    """

    @pytest.mark.asyncio
    async def test_a_fetch_plans(self, app_sync_client: TestClient):
        """
        Test fetch subscription plans
        """

        response = app_sync_client.get("/api/v1/subscription-plans")

        assert response.status_code == 200

        data = response.json()

        print("data: ", data)

        assert data["message"] == "Subscription Plans retrieved succesfully"
        assert data["status"] == "success"

        assert len(data["data"]) > 0
