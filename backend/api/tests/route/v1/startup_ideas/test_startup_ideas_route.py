"""
Test IDEAS VALIDATION route
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from api.schema.default_response_schema import GoogleIdToken
from api.repository.user_repo import user_repository
from api.repository.user_subscription_repo import user_subscription_repo
from api.repository.subscription_plan_repo import subscription_plan_repo
from api.repository.plan_usage_statistics_repo import plan_usage_statistics_repo


class TestIdeasValidationRoute:
    """
    Test IDEAS VALIDATION Route
    """

    @pytest.mark.asyncio
    async def test_a_and_fetch_validate_idea(
        self, app_sync_client: TestClient, async_db_session: AsyncSession
    ):
        """
        test validate idea
        """

        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonuidea@gmail.com",
            sub="1234azsssss0",
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
                "/api/v1/auth/signup/google",
                json={
                    "id_token": "eweoifkeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejieweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqejeweoifkiowfioejfiwejiowejiejfidemmmmmiodiqjdioqej",
                    "agreed_to_terms": True,
                },
            )

            assert response.status_code == 201
            data = response.json()

            token = data["data"]["token"]["access_token"]
            user_id = data["data"]["user"]["id"]

        plan_usage = await plan_usage_statistics_repo.fetch(
            session=async_db_session, user_id=user_id
        )
        assert plan_usage
        print("plan_usage1: ", plan_usage.__dict__)

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
                await async_db_session.refresh(plan_usage)
                print("plan_usage2: ", plan_usage.__dict__)

                assert response2.status_code == 201

                data2 = response2.json()

                print("data2: ", data2)
                idea_id = data2["data"]["validation"]["id"]

                response3 = app_sync_client.get(
                    "/api/v1/startup-ideas",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert response3.status_code == 200

                data3 = response3.json()

                print("data3: ", data3)

                assert data3 == {
                    "status": "success",
                    "message": "Suggestions retrieved succesfully",
                    "data": [
                        {
                            "id": idea_id,
                            "user_id": user_id,
                            "prompt": "animal e-commerce app",
                        },
                    ],
                }

                response4 = app_sync_client.post(
                    "/api/v1/startup-ideas",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"prompt": "animal e-commerce app", "idx": 0},
                )

                assert response4.status_code == 409

                data4 = response4.json()

                print("data4: ", data4)

                assert (
                    data4["message"]
                    == "Free Trial Exhausted. Upgrade or Renew Subscription"
                )

    @pytest.mark.asyncio
    async def test_b_fetch_validate_idea(
        self,
        app_sync_client: TestClient,
        async_db_session: AsyncSession,
    ):
        """
        test fetch validate idea
        """

        user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonfetchidea@gmail.com",
                "phone_number": "+2347090225757",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )
        sub_plan = await subscription_plan_repo.fetch(
            session=async_db_session, is_default=True
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
            email="johnsonfetchidea@gmail.com",
            sub="12345swa10",
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

                response3 = app_sync_client.get(
                    f"/api/v1/startup-ideas/{idea_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert response3.status_code == 200

                data3 = response3.json()

                print("data3: ", data3)

                assert data3 == {
                    "status": "success",
                    "message": "Suggestion retrieved succesfully",
                    "data": {
                        "id": idea_id,
                        "user_id": user_id,
                        "prompt": "animal e-commerce app",
                        "idea_validation": "idea validation",
                        "idea_score": None,
                        "lean_canvas": None,
                        "ideal_customer_persona": None,
                        "suggested_startup_names": None,
                        "monetization_models": None,
                        "website_hero": None,
                        "blog_posts": None,
                        "twitter_posts": None,
                        "elevator_pitch_slide": None,
                        "go_to_market_strategy_outline": None,
                    },
                }
