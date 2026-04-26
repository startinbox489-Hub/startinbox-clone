"""
Payment schema
"""

from typing import List, Annotated, Optional, Dict
import json

from pydantic import BaseModel, Field, StringConstraints, ConfigDict, model_validator
from uuid6 import uuid7

from api.model.model_enums import PaymentStatusEnum, PaymentProviderEnum


class PaymentBase(BaseModel):
    """
    Payment Base
    """

    payment_reference: str = Field(examples=["22222222-3333-2222-1111-111122223333"])
    tx_reference: str | None = Field(
        default=None, examples=["22222222-3333-2222-1111-111122223333"]
    )
    status: str = Field(examples=[PaymentProviderEnum.FLUTTERWAVE.value])
    provider: str = Field(examples=[PaymentStatusEnum.APPROVED.value])
    subscription_plan_id: str | None = Field(
        default=None, examples=["23232323-2323-2323-2323-232323232323"]
    )
    subscription_plan_idx: int | None = Field(default=None, examples=[1])
    flutterwave_subscription_id: int | None = Field(default=None, examples=[12313])
    amount: str | None = Field(default="0", examples=["10.99"])

    model_config = ConfigDict(from_attributes=True)


# ++++++++++++++++++++++ Initiate payment ++++++++++++++++
class InitiatePaymentRequestSchema(BaseModel):
    """
    InitiatePaymentRequestSchema
    """

    subscription_plan_id: Optional[
        Annotated[
            str, StringConstraints(min_length=3, max_length=60, strip_whitespace=True)
        ]
    ] = Field(examples=["starter"], default=None)
    subscription_plan_idx: Optional[int] = Field(default=None, examples=[1], ge=0)
    adds_on_service_ids: Optional[List[Dict[str, int | str]]] = Field(
        default=None,
        examples=[[{"amount": 300, "unit": "week", "id": "1234567890"}]],
    )
    purchase_event_id: Optional[
        Annotated[
            str, StringConstraints(min_length=20, max_length=60, strip_whitespace=True)
        ]
    ] = Field(default=None, examples=[str(uuid7())])
    gen_pdf: bool = Field(default=False, examples=[False])
    to_purchase: Optional[str] = Field(
        default=None, examples=["true"], min_length=1
    )  # enables redirect to checkout/purchase and not /checkout

    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, values: dict) -> dict:
        """
        Validates all fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        adds_on_service_ids = values.get("adds_on_service_ids", None)
        subscription_plan_id = values.get("subscription_plan_id", None)
        subscription_plan_idx = values.get("subscription_plan_idx", None)

        if not subscription_plan_id and not subscription_plan_idx:
            raise ValueError(
                "must provide one of subscription_plan_id or subscription_plan_idx"
            )

        if adds_on_service_ids and not isinstance(adds_on_service_ids, list):
            raise ValueError("adds_on_service_ids must be a list of adds-on IDs")
        if adds_on_service_ids:
            if len(adds_on_service_ids) > 2:
                raise ValueError("Can only add two Add On services")
            for adds_on in adds_on_service_ids:
                if not isinstance(adds_on, dict):
                    raise ValueError(
                        "adds_on_service_ids must contain dicts/objects/hashes"
                    )
                adds_on_id = adds_on.get("id")
                if (
                    not adds_on_id
                    or not isinstance(adds_on_id, str)
                    or len(adds_on_id.strip()) < 10
                ):
                    raise ValueError("each adds_on must have an id.")
                unit = adds_on.get("unit")
                if not unit or not isinstance(unit, str) or len(unit.strip()) < 1:
                    raise ValueError("each adds_on must have a unit")
                amount = adds_on.get("amount")
                if not amount or not isinstance(amount, int) or amount < 1:
                    raise ValueError(
                        "each adds_on must have an amount not less than zero(0)"
                    )

        return values


class InitiatePaymentResDataSchema(BaseModel):
    """
    InitiatePaymentResponseSchema
    """

    subscription_plan_id: str = Field(examples=["starter"])
    has_active_payment: bool = Field(examples=[False])
    payment_link: str = Field(examples=["https://hosted.com/payments"])
    payment_reference: str = Field(examples=["11111111111111111111222222222222"])
    tx_reference: str | None = Field(
        default=None, examples=["11111111111111111111222222222223"]
    )
    gen_pdf: bool = Field(default=False, examples=[False])


class InitiatePaymentResponseSchema(BaseModel):
    """
    InitiatePaymentResponseSchema
    """

    message: str = Field(
        default="Payments initiated successfully",
        examples=["Payments initiated successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: InitiatePaymentResDataSchema


# +++++++++++++++++++++++++ verify payment +++++++++++++++++++++
class VerifyPaymentRequestSchema(BaseModel):
    """
    VerifyPaymentRequestSchema
    """

    payment_reference: Annotated[
        str, StringConstraints(min_length=3, max_length=60, strip_whitespace=True)
    ] = Field(examples=["11111111-1111-1111-1111-111111111111"])
    tx_reference: Annotated[
        str, StringConstraints(min_length=3, max_length=60, strip_whitespace=True)
    ] = Field(examples=["11111111-1111-1111-1111-111111111111"])
    gen_pdf: bool = Field(default=False, examples=[False])

    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, values: dict) -> dict:
        """
        Validates all fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)

        payment_reference: str | None = values.get("payment_reference", "")
        tx_reference: str | None = values.get("tx_reference", "")

        if (
            not tx_reference
            or not isinstance(tx_reference, str)
            or tx_reference.strip() == ""
        ):
            raise ValueError("must provide tx_reference as a string")

        if (
            not payment_reference
            or not isinstance(payment_reference, str)
            or payment_reference.strip() == ""
        ):
            raise ValueError("must provide payment_reference as a string")

        return values


class VerifyPaymentResponseSchema(BaseModel):
    """
    VerifyPaymentResponseSchema
    """

    message: str = Field(
        default="Payments verified successfully",
        examples=["Payments verified successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: PaymentBase
    gen_pdf: bool = Field(default=False, examples=[False])


# +++++++++++++++++++++++++ fetch payments +++++++++++++++++++++
class FetchPayemntsResponseSchema(BaseModel):
    """
    FetchPayemntsResponseSchema
    """

    message: str = Field(
        default="Payments retrieved successfully",
        examples=["Payments retrieved successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: List[PaymentBase]


# +++++++++++++++++++ WEBHOOK PAYLOAD ++++++++++++++++++++++++
class StripeWebhookRequestSchema(BaseModel):
    """
    WebhookRequestSchema
    """

    status: str = Field(examples=["success"])


class PaystackWebhookRequestSchema(BaseModel):
    """
    WebhookRequestSchema
    """

    status: str = Field(examples=["success"])


# +++++++++++++++++
class GenerateBillingResponseSchema(BaseModel):
    """
    GenerateBillingResponseSchema
    """

    message: str = Field(
        default="Billing link generated successfully",
        examples=["Billing link generated successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: dict = Field(
        examples=[
            {
                "link": "https://link.pay",
                "tx_ref": "sub_11111111-1111-1111-1111-111111111111",
            }
        ]
    )
