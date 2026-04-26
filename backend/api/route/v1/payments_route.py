"""
Payments Route
"""

from fastapi import APIRouter, Depends, status, BackgroundTasks, Path
from slowapi import Limiter

from api.schema.payment_schema import (
    InitiatePaymentRequestSchema,
    InitiatePaymentResponseSchema,
    VerifyPaymentRequestSchema,
    VerifyPaymentResponseSchema,
    GenerateBillingResponseSchema,
)
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.service.payment_service import payment_service
from api.service.auth_service import auth_service
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address

payment_route = APIRouter(
    tags=["PAYMENTS"],
    prefix="/payments",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "4/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@payment_route.post(
    "",
    response_model=InitiatePaymentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_with_tx)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def initiate_payment(
    request: CustomRequest,
    schema: InitiatePaymentRequestSchema,
) -> InitiatePaymentResponseSchema:
    """
    Initiates Payments
    """
    return await payment_service.initiate_payment(
        request=request,
        schema=schema,
    )


@payment_route.post(
    "/verify",
    response_model=VerifyPaymentResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_with_tx)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def verify_payment(
    request: CustomRequest,
    schema: VerifyPaymentRequestSchema,
    background_tasks: BackgroundTasks,
) -> VerifyPaymentResponseSchema:
    """
    Verifies Payments
    """
    return await payment_service.verify_payment(
        request=request,
        schema=schema,
        background_tasks=background_tasks,
    )


@payment_route.post(
    "/billing/generate/{plan_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=GenerateBillingResponseSchema,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard)],
)
async def generate_billing_link(
    request: CustomRequest,
    plan_id: int = Path(
        gt=0,
        lt=9999999999999999999,
    ),
):
    """
    Handles flutterwave webhook payloads
    """
    return await payment_service.generate_subscription_link(
        request=request,
        flutterwave_plan_id=plan_id,
    )


@payment_route.post(
    "/billing/verify",
    response_model=VerifyPaymentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard_with_tx)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def verify_billing_payment(
    request: CustomRequest,
    schema: VerifyPaymentRequestSchema,
) -> VerifyPaymentResponseSchema:
    """
    Verifies Billing Payments
    """
    return await payment_service.verify_billing(
        request=request,
        schema=schema,
    )


@payment_route.post(
    "/webhook/flutterwave",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
)
async def payment_webhook(
    request: CustomRequest,
):
    """
    Handles flutterwave webhook payloads
    """
    return await payment_service.flutterwave_webhook(
        request=request,
    )
