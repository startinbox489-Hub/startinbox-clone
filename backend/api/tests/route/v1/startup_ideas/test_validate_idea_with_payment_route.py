"""
Test startup ideas repo
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import HttpUrl

# import sqlalchemy as sa

from api.schema.default_response_schema import GoogleIdToken
from api.tests.route.v1.startup_ideas import flutterwave_data
from api.repository.adds_on_consultation_repo import adds_on_consultation_repo
from api.repository.user_subscription_repo import user_subscription_repo
from api.repository.plan_usage_statistics_repo import plan_usage_statistics_repo
from api.repository.user_subscription_repo import user_subscription_repo
from api.model.model_enums import SubscriptionPlanTypeEnum

d = """{"A. Validation Output": {"idea_validation": "idea_validation","idea_score": 75,"lean_canvas": {"problem": "Difficulty finding and booking high-quality"}}}"""


class TestStartupIdeasPaymentRoute:
    """
    Test startup ideas
    """

    @pytest.mark.asyncio
    # @pytest.mark.skip(
    #     "sqlite behaves differently from postgres, cannot properly auto test, must manually test"
    # )
    async def test_a_(
        self, async_db_session: AsyncSession, app_sync_client: TestClient
    ):
        """
        Test create and fetch startup ideas
        """

        # REGISTER
        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonunique@gmail.com",
            sub="1234azsssaq3w",
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
            with patch(
                "api.service.resend_email_service.resend_email_service.send_email",
                return_value={"id": "e3e23r24r4t35t35", "status": True},
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

            # PAY FOR starter plan
            with patch(
                "api.service.payment_service.flutterwave_service.initiate_payment",
                return_value={
                    "payment_ref": "12344567890",
                    "payment_link": "https://fake.host.com/pay",
                },
            ):
                with patch(
                    "api.service.meta_pixel_service.MetaPixelService.send_meta_event",
                    return_value=None,
                ):
                    # check for invalid amount for adds on
                    pay_res_409 = app_sync_client.post(
                        "/api/v1/payments",
                        headers={"Authorization": f"Bearer {token}"},
                        json={
                            "subscription_plan_id": "starter",
                            "adds_on_service_ids": [
                                {
                                    "unit": "week",
                                    "amount": 30,
                                    "id": "00000000-0000-0000-0000-000000000000",
                                }
                            ],
                        },
                    )
                    assert pay_res_409.status_code == 409
                    pay_res = app_sync_client.post(
                        "/api/v1/payments",
                        headers={"Authorization": f"Bearer {token}"},
                        json={
                            "subscription_plan_id": "starter",
                            "adds_on_service_ids": [
                                {
                                    "unit": "week",
                                    "amount": 300,
                                    "id": "00000000-0000-0000-0000-000000000000",
                                }
                            ],
                            "purchase_event_id": "111111111111-1111-1111-1111-11111111",
                        },
                    )

                    assert pay_res.status_code == 201

                    pay_data = pay_res.json()

                    assert pay_data["data"]["subscription_plan_id"] == "starter"
                    assert pay_data["data"]["has_active_payment"] is False
                    assert (
                        pay_data["data"]["payment_link"] == "https://fake.host.com/pay"
                    )
                    assert pay_data["data"]["payment_reference"] == "12344567890"
                    tx_reference = f"{flutterwave_data['data']['id']}"
                    await async_db_session.flush()

                    adds_on_consult = await adds_on_consultation_repo.fetch_all(
                        session=async_db_session, user_id=user_id
                    )
                    assert len(adds_on_consult) == 1
                    assert adds_on_consult[0].startup_idea_id is None

                    # VERIFY PAYMENT
                    with patch(
                        "api.service.payment_service.flutterwave_service.verify_payment",
                        return_value={
                            "status": "successful",
                            "inner_status": "successful",
                            "payment_reference": "12344567890",
                            "amount": 329.99,
                            "tx_reference": tx_reference,
                            "message": "any",
                        },
                    ):
                        pay_verify_res = app_sync_client.post(
                            "/api/v1/payments/verify",
                            headers={"Authorization": f"Bearer {token}"},
                            json={
                                "payment_reference": "12344567890",
                                "tx_reference": tx_reference,
                            },
                        )

                        await async_db_session.flush()

                        assert pay_verify_res.status_code == 200

                        pay_verify_data = pay_verify_res.json()

                        assert pay_verify_data["status"] == "success"
                        assert (
                            pay_verify_data["data"]["subscription_plan_id"] == "starter"
                        )
                        assert pay_verify_data["data"]["provider"] == "flutterwave"
                        assert pay_verify_data["data"]["status"] == "successful"
                        assert pay_verify_data["data"]["subscription_plan_idx"] == 1
                        # assert pay_verify_data["data"]["tx_reference"] == tx_reference
                        assert (
                            pay_verify_data["data"]["payment_reference"]
                            == "12344567890"
                        )

                    await async_db_session.flush()
                    # generate idea
                    with patch(
                        "api.service.gemini_service.gemini_service.generate_idea",
                        return_value=d,
                    ):
                        with patch(
                            "api.service.resend_email_service.resend_email_service.send_email",
                            return_value={"id": "e3e23r24r4t35t35", "status": True},
                        ):
                            idea_res = app_sync_client.post(
                                "/api/v1/startup-ideas",
                                headers={"Authorization": f"Bearer {token}"},
                                json={
                                    "prompt": "animal e-commerce app",
                                    "idx": 1,
                                },
                            )

                            assert idea_res.status_code == 201

                            idea_data = idea_res.json()

                            assert (
                                idea_data["data"]["validation"]["idea_validation"]
                                is not None
                            )

                            await async_db_session.flush()

                            adds_on_consult = await adds_on_consultation_repo.fetch_all(
                                session=async_db_session, user_id=user_id
                            )
                            await async_db_session.refresh(adds_on_consult[0])
                            assert len(adds_on_consult) == 1
                            assert adds_on_consult[0].startup_idea_id is not None

    @pytest.mark.asyncio
    # @pytest.mark.skip(
    #     "sqlite behaves differently from postgres, cannot properly auto test, must manually test"
    # )
    async def test_b_credits_sub(
        self, async_db_session: AsyncSession, app_sync_client: TestClient
    ):
        """
        Test create and fetch startup ideas with credits sub.
        """

        # REGISTER
        req_data = GoogleIdToken(
            email_verified=True,
            email="johnsonunique1@gmail.com",
            sub="1234azsssaq3w1",
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
            with patch(
                "api.service.resend_email_service.resend_email_service.send_email",
                return_value={"id": "e3e23r24r4t35t35", "status": True},
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

            # PAY FOR starter plan
            with patch(
                "api.service.payment_service.flutterwave_service.generate_subscription_link",
                return_value={
                    "tx_ref": "12344567890",
                    "link": "https://fake.host.com/pay",
                },
            ):
                with patch(
                    "api.service.meta_pixel_service.MetaPixelService.send_meta_event",
                    return_value=None,
                ):
                    # generate credit sub link
                    pay_res = app_sync_client.post(
                        f"/api/v1/payments/billing/generate/{12345}",
                        headers={"Authorization": f"Bearer {token}"},
                    )

                    assert pay_res.status_code == 201

                    pay_data = pay_res.json()
                    assert pay_data["data"]["link"] == "https://fake.host.com/pay"
                    assert pay_data["data"]["tx_ref"] == "12344567890"
                    tx_reference = f"{flutterwave_data['data']['id']}"
                    await async_db_session.flush()

                    # VERIFY PAYMENT
                    with patch(
                        "api.service.payment_service.flutterwave_service.verify_payment",
                        return_value={
                            "status": "successful",
                            "inner_status": "successful",
                            "payment_reference": "12344567890",
                            "amount": 29.99,
                            "tx_reference": tx_reference,
                            "message": "any",
                        },
                    ):
                        pay_verify_res = app_sync_client.post(
                            "/api/v1/payments/billing/verify",
                            headers={"Authorization": f"Bearer {token}"},
                            json={
                                "payment_reference": tx_reference,
                                "tx_reference": "12344567890",
                            },
                        )

                        await async_db_session.flush()

                        assert pay_verify_res.status_code == 201

                        pay_verify_data = pay_verify_res.json()

                        assert pay_verify_data["status"] == "success"
                        assert (
                            pay_verify_data["data"]["subscription_plan_id"] == "silver"
                        )
                        assert pay_verify_data["data"]["provider"] == "flutterwave"
                        assert pay_verify_data["data"]["status"] == "successful"
                        assert pay_verify_data["data"]["subscription_plan_idx"] == 2
                        # assert pay_verify_data["data"]["tx_reference"] == tx_reference
                        assert (
                            pay_verify_data["data"]["payment_reference"]
                            == "12344567890"
                        )

                    await async_db_session.flush()
                    sub = await user_subscription_repo.fetch(
                        session=async_db_session,
                        is_expired=False,
                        user_id=user_id,
                        _type=SubscriptionPlanTypeEnum.REOCCURRING,
                    )
                    assert sub
                    assert sub.credit_used == 0
                    assert sub.remaining_credits == 5
                    # generate idea
                    with patch(
                        "api.service.gemini_service.gemini_service.generate_idea",
                        return_value=d,
                    ):
                        with patch(
                            "api.service.resend_email_service.resend_email_service.send_email",
                            return_value={"id": "e3e23r24r4t35t35", "status": True},
                        ):
                            idea_res = app_sync_client.post(
                                "/api/v1/startup-ideas",
                                headers={"Authorization": f"Bearer {token}"},
                                json={
                                    "prompt": "animal e-commerce app",
                                    "idx": 2,
                                    "type_": "reoccurring",
                                },
                            )
                            await async_db_session.flush()

                            assert idea_res.status_code == 201

                            idea_data = idea_res.json()

                            assert (
                                idea_data["data"]["validation"]["idea_validation"]
                                is not None
                            )
                            plan_usage = await plan_usage_statistics_repo.fetch(
                                session=async_db_session,
                                user_id=user_id,  # type: ignore
                            )
                            assert plan_usage
                            await async_db_session.flush([sub, plan_usage])

                            assert plan_usage.silver_plan_stats.get("use_count") == 1

                    with patch(
                        "api.service.payment_service.flutterwave_service.generate_subscription_link",
                        return_value={
                            "tx_ref": "123445678900",
                            "link": "https://fake.host.com/pay",
                        },
                    ):
                        # generate credit sub link
                        pay_res = app_sync_client.post(
                            f"/api/v1/payments/billing/generate/{12345}",
                            headers={"Authorization": f"Bearer {token}"},
                        )

                        assert pay_res.status_code == 201

                        pay_data = pay_res.json()
                        assert pay_data["data"]["link"] == "https://fake.host.com/pay"
                        assert pay_data["data"]["tx_ref"] == "123445678900"
                        tx_reference = "1234456789001"
                        await async_db_session.flush()

                        # VERIFY PAYMENT
                        with patch(
                            "api.service.payment_service.flutterwave_service.verify_payment",
                            return_value={
                                "status": "successful",
                                "inner_status": "successful",
                                "payment_reference": "123445678900",
                                "amount": 29.99,
                                "tx_reference": tx_reference,
                                "message": "any",
                            },
                        ):
                            pay_verify_res = app_sync_client.post(
                                "/api/v1/payments/billing/verify",
                                headers={"Authorization": f"Bearer {token}"},
                                json={
                                    "payment_reference": tx_reference,
                                    "tx_reference": "123445678900",
                                },
                            )

                            await async_db_session.flush()

                            assert pay_verify_res.status_code == 201

                            pay_verify_data = pay_verify_res.json()

                            assert pay_verify_data["status"] == "success"
                            assert (
                                pay_verify_data["data"]["subscription_plan_id"]
                                == "silver"
                            )
                            assert pay_verify_data["data"]["provider"] == "flutterwave"
                            assert pay_verify_data["data"]["status"] == "successful"
                            assert pay_verify_data["data"]["subscription_plan_idx"] == 2
                            # assert pay_verify_data["data"]["tx_reference"] == tx_reference
                            assert (
                                pay_verify_data["data"]["payment_reference"]
                                == "123445678900"
                            )
