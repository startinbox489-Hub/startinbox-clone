"""
Flutterwave service
"""

import hashlib
import hmac
import base64
from typing import Dict
from httpx import AsyncClient as async_client

from fastapi import status, HTTPException, Request
from uuid6 import uuid7

from api.core.config import settings
from api.utils.task_logger import create_logger
from api.utils.app_enums import FlutterwaveEvent

from api.repository.payment_repository import payment_repo
from api.repository.subscription_plan_repo import subscription_plan_repo
from api.repository.user_subscription_repo import user_subscription_repo

logger = create_logger(":: FlutterwaveService ::")


class FlutterwaveService:
    """
    Flutterwave service
    """

    async def initiate_payment(
        self,
        sub_plan_id: str,
        email: str,
        name: str,
        amount: float,
        user_id: str,
        to_purchase: str | None = None,
    ) -> Dict[str, str]:
        """
        Initiates subscription payment.

        redirect to client side:
        http://localhost:3000/checkout?status=successful&tx_ref=01995d0b24c872c0aa8b89da124abcc4&transaction_id=9656600
        """
        payment_ref = str(uuid7()).replace("-", "")
        headers = {
            "Authorization": f"Bearer {settings.flw_secret_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "tx_ref": payment_ref,
            "amount": str(amount),
            "currency": "USD",  # ensure this is USD
            "redirect_url": (
                settings.flw_client_redirect_url
                if not to_purchase
                else f"{settings.flw_client_redirect_url}/purchase"
            ),
            "customer": {"email": email, "name": name},
            "meta": {
                "title": "Pay-as-you-go Service",
                "description": "One-time USD payment",
                "user_id": user_id,
                "sub_plan_id": sub_plan_id,
            },
            "configurations": {
                # Session timeout in minutes (maxValue: 1440)
                "session_duration": 5,
                # Max retry (int)
                "max_retry_attempt": 3,
            },
        }

        async with async_client() as aclient:
            response = await aclient.post(
                f"{settings.flw_payment_url}/payments",
                json=payload,
                headers=headers,
                timeout=20.0,
            )
            if response.status_code != 200:
                logger.error(
                    "error initiating flutterwave payment: %s", str(response.json())
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            data: dict = response.json()
            logger.info("payment data: %s", data)
            return {
                "payment_ref": payment_ref,
                "payment_link": data.get("data", {}).get("link"),
            }

    async def verify_payment(self, tx_reference: str):
        """
        Verify subscription payment.

        Args:
            payment_reference(str): Optional custom payment reference provided
            tx_reference (str): Optional flutterwave payment referece.
        Returns:
            Dict[str, Any]
            e.g.: {
                "status": 'success',
                "inner_status": successful
                ),
                "payment_reference": 'tx_ref',
                "amount": 3,
                "tx_reference": 'flw_ref',
                "message": 'Payment fetched successfully',
            }
        """
        headers = {"Authorization": f"Bearer {settings.flw_secret_key}"}

        tx_ref_url = f"{settings.flw_payment_url}/transactions/{tx_reference}/verify"

        async with async_client() as aclient:
            response = await aclient.get(
                tx_ref_url,
                headers=headers,
                timeout=20.0,
            )

            if "application/json" in response.headers.get("content-type"):
                data: dict = response.json() or {}
            else:
                return {"status": "failed", "reason": response.text}

            logger.info("flutterwave payment verification data: %s", str(data))

            data_status = data.get("status", "")
            tx_data: dict = data.get("data") or {}

            return {
                "status": ("not_found" if data_status == "error" else data_status),
                "inner_status": (
                    "not_found" if data_status == "error" else tx_data.get("status", "")
                ),
                "payment_reference": tx_data.get("tx_ref"),
                "amount": tx_data.get("amount"),
                "tx_reference": tx_data.get("id") or tx_reference,
                "currency": tx_data.get("currency"),
                "message": data.get("message", ""),
            }

    async def create_payment_plan(
        self, amount: int, name: str, interval: str, duration: int
    ):
        """
        Create a payment plan
        """
        async with async_client() as client:
            res = await client.post(
                f"{settings.flw_payment_url}/payment-plans",
                headers={"Authorization": f"Bearer {settings.flw_secret_key}"},
                json={
                    "amount": amount,
                    "name": name,
                    "interval": interval,
                    "duration": duration,
                },
            )
            data = res.json() or {}
            return data.get("id")  # payment_plan_id

    async def generate_subscription_link(
        self,
        email: str,
        plan_id: int,
        plan_price: float,
        currency: str,
        user_id: str,
        sub_name: str,
    ):
        """
        Generate subscription link
        """
        try:
            tx_ref = f"sub_{str(uuid7())}"
            async with async_client() as client:
                res = await client.post(
                    f"{settings.flw_payment_url}/payments",
                    headers={"Authorization": f"Bearer {settings.flw_secret_key}"},
                    json={
                        "tx_ref": tx_ref,
                        "amount": plan_price,
                        "currency": currency.upper(),
                        "redirect_url": f"{settings.client_side_url}/billing/verify",
                        "payment_plan": plan_id,
                        "customer": {
                            "email": email,
                            "id": user_id,
                        },
                        "customizations": {
                            "plan_name": sub_name,
                            "flw_plan_id": plan_id,
                            "user_id": user_id,
                        },
                    },
                )

                data = res.json() or {}
                return {
                    "link": data.get("data", {})["link"],
                    "tx_ref": tx_ref,
                }
        except Exception as exc:
            print(exc)
            raise exc

    async def flutterwave_webhook(self, request: Request):
        """
        Webhook handler
        Example Subscription Webhook Payload
        {
            "event": "charge.completed",
            "data": {
                "id": 10019208,
                "tx_ref": "sub_019c6165-89a4-729d-9513-ffb069b4b6ca",
                "flw_ref": "FLW-MOCK-fb6e9df7967e9962be3fa091cc89c135",
                "device_fingerprint": "566a625076752106ea53737541e832c128f52d60ce16e88ff3ab58669a99a0b1",
                "amount": 12.99,
                "currency": "USD",
                "charged_amount": 12.99,
                "app_fee": 0.5,
                "merchant_fee": 0,
                "processor_response": "Approved. Successful",
                "auth_model": "VBVSECURECODE",
                "ip": "52.209.154.143",
                "narration": "CARD Transaction ",
                "status": "successful",
                "payment_type": "card",
                "created_at": "2026-02-15T13:03:25.000Z",
                "account_id": 2584878,
                "customer": {
                    "id": 3468257,
                    "name": "Johnson Oragui Developer Freelance",
                    "phone_number": null,
                    "email": "ravesb_c89bc522f3a3071fd295_33xsaint@gmail.com",
                    "created_at": "2026-02-15T13:03:24.000Z",
                },
                "card": {
                    "first_6digits": "553188",
                    "last_4digits": "2950",
                    "issuer": "MASTERCARD  CREDIT",
                    "country": "NG",
                    "type": "MASTERCARD",
                    "expiry": "09/32",
                },
            },
            "meta_data": {"__CheckoutInitAddress": "N/A"},
            "event.type": "CARD_TRANSACTION",
        }
        """

        try:
            headers = request.headers
            payload = (await request.json()) or {}
            print("headers: ", headers)
            raw_body = await request.body()
            flutterwave_signature = headers.get("flutterwave-signature")
            print("flutterwave_signature: ", flutterwave_signature)

            if not flutterwave_signature:
                raise HTTPException(status_code=401, detail="Missing signature")

            if not self._verify_flutterwave_signature(
                raw_body,
                flutterwave_signature,
            ):
                raise HTTPException(status_code=401, detail="Invalid signature")

            event = payload.get("event")
            data = payload.get("data") or {}

            sub_id = data.get("subscription_id")
            flw_status = data.get("status")
            tx_ref = data.get("tx_ref")

            if event == FlutterwaveEvent.CHARGE_COMPLETE.value and sub_id:
                customer = data.get("customer") or {}
                email = customer.get("email")
                plan_id = data.get("payment_plan")
                print("Subscription created:", sub_id, email, plan_id)

            if event == FlutterwaveEvent.SUBSCRIPTION_CANCELLED.value:
                pass
            if event == FlutterwaveEvent.SUBSCRIPTION_EXPIRED.value:
                pass

            return {"status": "ok"}
        except HTTPException as exc:
            raise exc
        except Exception as exc:
            print("webhook error: ", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def process_webhook_payload(
        self,
        flw_status: str,
        tx_ref: str,
        email: str,
    ):
        """
        Process webhook payload
        """
        pass

    def _verify_flutterwave_signature(self, raw_body: bytes, signature: str):
        """
        Verify flutterwave signature
        """
        computed_hash = hmac.new(
            settings.flw_secret_hash.encode(), raw_body, hashlib.sha256
        ).digest()

        encoded_hash = base64.b64encode(computed_hash).decode()

        return hmac.compare_digest(encoded_hash, signature)


flutterwave_service = FlutterwaveService()
