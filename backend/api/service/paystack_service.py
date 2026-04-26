"""
Paystack Service
"""

from typing import Any, Dict
from httpx import AsyncClient
from uuid6 import uuid7

from api.core.config import settings
from api.utils.task_logger import create_logger


logger = create_logger(":: PaystackService ::")


class PaystackService:
    """
    Paystack Service
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.__api_secret_key = settings.paystack_secret_key

    async def inititate_payment(
        self,
        email: str,
        usd_amount: float,
        currency: str = "USD",
    ) -> Dict[str, str | None]:
        """
        Initiates Payment via paystack.

        Args:
            email (str): The email of the current user.
            usd_amount (float): The intended amount in usd.

        Returns:
            Any

        Paystack Response Sample:
            {
                "status": true,
                "message": "Authorization URL created",
                "data": {
                    "authorization_url": "https://checkout.paystack.com/3ni8kdavz62431k",
                    "access_code": "3ni8kdavz62431k",
                    "reference": "re4lyvq3s3"
                }
                }
        """
        payment_ref = str(uuid7()).replace("-", "")
        body: Dict[str, Any] = {
            "email": email,
            "currency": currency,
            "amount": int(usd_amount * 100),  # converted to lowest denomination
            "callabck_url": f"{settings.client_side_url}/checkout",
            "metadata": {},
            "channels": [
                "card",
                "apple_pay",
            ],
            "reference": payment_ref,
        }

        logger.info("Payment payload: %s", str(body))
        headers = {
            "Authorization": f"Bearer {self.__api_secret_key}",
            "Content-Type": "application/json",
        }

        try:

            async with AsyncClient() as client:
                response = await client.post(
                    url=f"{settings.paystack_base_url}/initialize",
                    json=body,
                    timeout=20.5,
                    headers=headers,
                )
                if response.status_code not in [201, 200]:
                    logger.warning(
                        "Error initiating payment. status_code not OK/CREATED: code: %s, text: %s",
                        str(response.status_code),
                        response.text,
                    )
                    return {
                        "message": "Payment Initialization failed",
                        "authorization_url": None,
                    }
                data: dict = response.json()
                print("paystack data: ", data)
                if not data.get("status"):
                    logger.warning(
                        "Error initiating paymen. Status missing: %s", str(data)
                    )
                    return {
                        "message": "Payment Initialization failed",
                        "authorization_url": None,
                    }
                return {
                    "message": "Payment Initialization successful",
                    "authorization_url": data["data"]["authorization_url"],
                    "payment_ref": data["data"]["reference"],
                    "access_code": data["data"]["access_code"],
                }
        except Exception as exc:
            logger.error("Error initiating payment: %s", str(exc))
            raise exc

    async def verify_payment(
        self, tx_refrence: str, payment_reference: str
    ) -> Dict[str, str | int | float | None]:
        """
        Verifies payments.

        Args:
            tx_reference (str): The transaction id.
            payment_reference (str): The custom payment reference.

        Returns:
            Dict[str, Any]
        https://www.google.com/?trxref=019a72b240aa74dfa6a7dfd0a1d6998b&reference=019a72b240aa74dfa6a7dfd0a1d6998b
        Paystack Sample Response:
            {
                "status": true,
                "message": "Verification successful",
                "data": {
                    "id": 4099260516,
                    "domain": "test",
                    "status": "success",
                    "reference": "re4lyvq3s3",
                    "receipt_number": null,
                    "amount": 40333,
                    "message": null,
                    "gateway_response": "Successful",
                    "paid_at": "2024-08-22T09:15:02.000Z",
                    "created_at": "2024-08-22T09:14:24.000Z",
                    "channel": "card",
                    "currency": "NGN",
                    "ip_address": "197.210.54.33",
                    "metadata": "",
                    "log": {
                    "start_time": 1724318098,
                    "time_spent": 4,
                    "attempts": 1,
                    "errors": 0,
                    "success": true,
                    "mobile": false,
                    "input": [],
                    "history": [
                        {
                        "type": "action",
                        "message": "Attempted to pay with card",
                        "time": 3
                        },
                        {
                        "type": "success",
                        "message": "Successfully paid with card",
                        "time": 4
                        }
                    ]
                    },
                    "fees": 10283,
                    "fees_split": null,
                    "authorization": {
                    "authorization_code": "AUTH_uh8bcl3zbn",
                    "bin": "408408",
                    "last4": "4081",
                    "exp_month": "12",
                    "exp_year": "2030",
                    "channel": "card",
                    "card_type": "visa ",
                    "bank": "TEST BANK",
                    "country_code": "NG",
                    "brand": "visa",
                    "reusable": true,
                    "signature": "SIG_yEXu7dLBeqG0kU7g95Ke",
                    "account_name": null
                    },
                    "customer": {
                    "id": 181873746,
                    "first_name": null,
                    "last_name": null,
                    "email": "demo@test.com",
                    "customer_code": "CUS_1rkzaqsv4rrhqo6",
                    "phone": null,
                    "metadata": null,
                    "risk_action": "default",
                    "international_format_phone": null
                    },
                    "plan": null,
                    "split": {},
                    "order_id": null,
                    "paidAt": "2024-08-22T09:15:02.000Z",
                    "createdAt": "2024-08-22T09:14:24.000Z",
                    "requested_amount": 30050,
                    "pos_transaction_data": null,
                    "source": null,
                    "fees_breakdown": null,
                    "connect": null,
                    "transaction_date": "2024-08-22T09:14:24.000Z",
                    "plan_object": {},
                    "subaccount": {}
                }
                }
        """
        headers = {
            "Authorization": f"Bearer {self.__api_secret_key}",
            "Content-Type": "application/json",
        }
        try:
            async with AsyncClient() as client:
                response = await client.get(
                    url=f"{settings.paystack_base_url}/verify/{payment_reference}",
                    timeout=20.5,
                    headers=headers,
                )
                if response.status_code not in [201, 200]:
                    logger.warning(
                        "Error verifying payment. status_code not OK/CREATED: code: %s, text: %s",
                        str(response.status_code),
                        response.text,
                    )
                    return {
                        "message": "Payment Verification failed",
                        "status": "failed",
                    }
                data: dict = response.json() or {}
                print("paystack payment verification: ", data)
                if not data.get("status"):
                    logger.warning(
                        "Error verifying paymen. Status missing: %s", str(data)
                    )
                    return {
                        "message": "Payment Verification failed",
                        "status": "failed",
                    }
                payment_data = data.get("data") or {}
                if payment_data.get("status") == "success":  # Payment successful
                    return {
                        "status": "success",
                        "inner_status": "success",
                        "payment_reference": payment_reference,
                        "tx_reference": str(payment_data.get("id", "")),
                        "amount": payment_data.get("amount", 1) / 100,
                        "currency": payment_data.get("currency"),
                        "message": data.get("message", ""),
                    }
                return {
                    "status": "pending",
                    "message": payment_data.get("message") or "payment pending",
                }
        except Exception as exc:
            logger.error("Error verifying payment: %s", str(exc))
            raise exc


paystack_service = PaystackService()
