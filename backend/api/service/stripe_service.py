"""
Stripe service
"""

from typing import Dict
from datetime import timedelta, timezone, datetime
from decimal import Decimal
import stripe
from stripe import SignatureVerificationError, StripeError
from fastapi import Header, HTTPException
import uuid6

from api.core.config import settings
from api.schema.default_response_schema import CustomRequest
from api.utils.task_logger import create_logger

logger = create_logger(":: StripeService ::")


class CustomStripeServiceError(Exception):
    """
    CustomStripeServiceError
    """

    def __init__(self, message: str = "Error using stripe payment") -> None:
        """
        Constructor
        """
        super().__init__(message)


class StripeService:
    """
    Stripe service
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        stripe.api_key = settings.stripe_api_secret_key

    async def initiate_payment(
        self,
        price: Decimal,
        sub_plan_id: str,
        email: str,
    ) -> Dict[str, str | None]:
        """
        Initiates subscription payment.

        Args:
            price (Decimal): The price in dollar.
            sub_plan_id (str): The subscription plan id.
            email (str): The email of the user.
        Returns:
            payment_url (str): The payment checkout url.
        """
        price_ = price * 100
        payment_ref = str(uuid6.uuid7()).replace("-", "")

        try:
            asession = await stripe.checkout.Session.create_async(
                payment_method_types=["card"],  # omit to control from dashboard
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": sub_plan_id,
                            },
                            "unit_amount": int(price_),
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",  # for one time payment
                submit_type="pay",
                customer_email=email,
                client_reference_id=payment_ref,
                success_url=settings.frontend_stripe_success_url
                + "&tx_ref="
                + payment_ref,
                cancel_url=settings.frontend_stripe_cancel_url
                + "&tx_ref="
                + payment_ref,
                metadata={
                    "email": email,
                    "sub_plan_id": sub_plan_id,
                    "payment_ref": payment_ref,
                },
                expires_at=int(
                    (datetime.now(timezone.utc) + timedelta(minutes=31)).timestamp()
                ),
            )
            return {
                "payment_link": asession.url,
                "tx_reference": asession.id,
                "payment_reference": payment_ref,
            }
        except StripeError as exc:
            logger.error("Error communicating with stripe: %s", exc)
            raise HTTPException(
                status_code=417, detail="Error communicating with Stripe."
            ) from exc
        except Exception as exc:
            logger.error("Error initiating stripe payment: %s", str(exc))
            raise CustomStripeServiceError() from exc

    async def verify_payment(self, tx_reference: str) -> stripe.checkout.Session:
        """
        Verify subscription payment
        """
        asession = await stripe.checkout.Session.retrieve_async(
            id=tx_reference, api_key=settings.stripe_api_secret_key
        )
        return asession

    async def stripe_webhook(
        self, request: CustomRequest, stripe_signature: str = Header(None)
    ):
        """
        Handles stripe webhook
        """
        payload = await request.body()

        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.stripe_webhook_secret
            )
        except SignatureVerificationError as exc:
            logger.error("Error verrifying stripe webhook payload: %s", str(exc))
            raise HTTPException(status_code=400, detail="Invalid signature") from exc

        # Handle checkout session completed
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            # ✅ Payment successful, fulfill the order
            print(f"Checkout complete for session {session['id']}")
            print(f"Customer email: {session.get('customer_details', {}).get('email')}")

            # TODO: update DB order status = paid here

        return {"status": "success"}


stripe_service = StripeService()
