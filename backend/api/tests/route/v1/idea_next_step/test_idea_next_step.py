"""
Test deaNextStepRoute
"""

from unittest.mock import patch
from datetime import date

from fastapi.testclient import TestClient
import pytest
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from api.schema.default_response_schema import GoogleIdToken
from api.repository.user_repo import user_repository
from api.repository.user_subscription_repo import user_subscription_repo
from api.repository.subscription_plan_repo import subscription_plan_repo
from api.repository.plan_usage_statistics_repo import plan_usage_statistics_repo


class TestIdeaNextStepRoute:
    """
    Test IDEAS Next step Route
    """

    @pytest.mark.asyncio
    async def test_a_idea_next_step(
        self,
        app_sync_client: TestClient,
        async_db_session: AsyncSession,
    ):
        """
        test idea next step
        """

        user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonnextstepa@gmail.com",
                "phone_number": "+2347000011157",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )
        sub_plan = await subscription_plan_repo.fetch(
            session=async_db_session, is_default=True, plan_idx=0
        )
        assert sub_plan is not None
        await user_subscription_repo.create(
            session=async_db_session,
            user_sub_data={
                "user_id": user.id,
                "subscription_plan_id": sub_plan.id,
                "is_current": True,
            },
        )

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonnextstepa@gmail.com",
            sub="12345swa2w",
            aud="your_client_id.apps.googleusercontent.com",
            family_name="Dennis",
            given_name="Johnson",
            iss="your_client_id",
            name="Johnson Dennis",
            picture=HttpUrl("https://gmail.com"),
        )

        with patch(
            "api.service.auth_service.auth_service.verify_google_id_token",
            return_value=req_data,
        ):

            response = app_sync_client.post(
                "/api/v1/auth/signin/google",
                json={
                    "id_token": "eweoifkeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejieweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqej",
                    "agreed_to_terms": True,
                },
            )

            assert response.status_code == 200

            data = response.json()

            token = data["data"]["token"]["access_token"]
            user_id = data["data"]["user"]["id"]
            plan_usage = await plan_usage_statistics_repo.create(
                session=async_db_session, usage_data={"user_id": user_id}
            )
            await async_db_session.refresh(plan_usage)

        with patch(
            "api.service.gemini_service.gemini_service.generate_idea",
            return_value="""
            {"A. Validation Output": {"idea_validation": "idea validation"}}
            """,
        ):
            with patch(
                "api.service.resend_email_service.resend_email_service.send_email",
                return_value={"id": "e3e23r24r4t35t35", "status": True},
            ):
                response2 = app_sync_client.post(
                    "/api/v1/startup-ideas",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"prompt": "animal e-commerce app", "idx": 0},
                )

                assert response2.status_code == 201

                data2 = response2.json()

                print("data2: ", data2)
                idea_id = data2["data"]["validation"]["id"]

                response3 = app_sync_client.post(
                    "/api/v1/idea-next-steps",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "idea_id": idea_id,
                        "project_type": "Mobile",
                        "project_stage": "Entry",
                        "desired_date": date.today().isoformat(),
                    },
                )
                assert response3.status_code == 201

                data3 = response3.json()

                assert data3["status"] == "success"
                assert data3["message"] == "Idea Next Step recorded successfully"
