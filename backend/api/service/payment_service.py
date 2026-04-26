"""
Payment Service
"""

from typing import Tuple, Optional, List, Dict, Any
from decimal import Decimal

from fastapi import status, HTTPException, BackgroundTasks
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from psycopg2.errors import Error as PsycopgError

from api.repository.payment_repository import payment_repo, PaymentModel
from api.repository.user_subscription_repo import user_subscription_repo
from api.schema.default_response_schema import CustomRequest
from api.utils.get_session_claims_from_request import get_claims_and_session
from api.service.flutterwave_service import flutterwave_service
from api.schema.payment_schema import (
    InitiatePaymentRequestSchema,
    InitiatePaymentResponseSchema,
    InitiatePaymentResDataSchema,
    VerifyPaymentRequestSchema,
    VerifyPaymentResponseSchema,
    PaymentBase,
    GenerateBillingResponseSchema,
)
from api.repository.user_repo import user_repository
from api.repository.subscription_plan_repo import subscription_plan_repo
from api.utils.task_logger import create_logger
from api.model.model_enums import PaymentStatusEnum
from api.schema.default_response_schema import Claims
from api.model.adds_on_service import AddsOnServiceModel
from api.repository.adds_on_repo import adds_on_service_repo
from api.repository.adds_on_consultation_repo import adds_on_consultation_repo
from api.service.meta_pixel_service import MetaPixelService
from api.utils.send_files_to_mail import send_report_files_via_mail
from api.repository.startup_ideas_repo import startup_ideas_repo
from api.model.model_enums import SubscriptionPlanTypeEnum

logger = create_logger(":: PaymentService ::")

STATUS = {
    "PAID": PaymentStatusEnum.PAID,
    "APPROVED": PaymentStatusEnum.APPROVED,
    "SUCCESS": PaymentStatusEnum.SUCCESS,
    "FAILED": PaymentStatusEnum.FAILED,
    "CANCELLED": PaymentStatusEnum.CANCELLED,
    "NOT_FOUND": PaymentStatusEnum.NOT_FOUND,
    "SUCCESSFUL": PaymentStatusEnum.SUCCESSFUL,
    "PENDING": PaymentStatusEnum.PENDING,
    "REFUNDED": PaymentStatusEnum.REFUNDED,
    "NO_PAYMENT_REQUIRED": PaymentStatusEnum.NO_PAYMENT_REQUIRED,
    "ABANDONED": PaymentStatusEnum.ABANDONED,
}


class PaymentService:
    """
    Payment service
    """

    async def initiate_payment(
        self, schema: InitiatePaymentRequestSchema, request: CustomRequest
    ) -> InitiatePaymentResponseSchema:
        """
        Initiates subscription payment.

        Args:
            schema (InitiatePaymentRequestSchema): The request payload.
            request (CustomRequest): The request object.
        Returns:
            response payload (InitiatePaymentResponseSchema)
        """
        try:
            session, claims = get_claims_and_session(request=request)
            user_sub = await user_subscription_repo.fetch_with_plan(
                session=session,
                user_id=claims.user_id,
                sub_attributes=["price", "idx", "subscription_plan_id"],
            )
            assert user_sub is not None

            if user_sub.get("is_expired") is False and user_sub.get("idx") != 0:
                # user has active payment.
                # Add a flag in the response payload to signify active_payment=True, plan_id=plan_id
                # This would allow client-side to go straight to the the generate ideas endpoint
                return InitiatePaymentResponseSchema(
                    data=InitiatePaymentResDataSchema(
                        subscription_plan_id=user_sub.get("subscription_plan_id", ""),
                        has_active_payment=True,
                        payment_link="",
                        payment_reference="",
                        tx_reference="",
                        gen_pdf=schema.gen_pdf,
                    ),
                    message="Unused active payment detected. Please use your active payments.",
                )

            sub_plan = await subscription_plan_repo.fetch(
                session=session,
                plan_id=schema.subscription_plan_id,
                plan_idx=schema.subscription_plan_idx,
            )
            if not sub_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Subscription plan not found",
                )
            if sub_plan._type == SubscriptionPlanTypeEnum.ONEOFF.value:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Can only payment for oneoff subs from here.",
                )
            amount = sub_plan.price
            add_to_session = []

            # check for adds on
            adds_on_one = None
            adds_on_two = None
            new_adds_on_consult = None

            if (
                schema.adds_on_service_ids is not None
                and len(schema.adds_on_service_ids) > 0
            ):
                adds_on_one, adds_on_two = await self.__validate_selected_adds_on(
                    session=session,
                    adds_on_ids=[
                        add_on.get("id")
                        for add_on in schema.adds_on_service_ids
                        if isinstance(add_on.get("id"), str)
                    ],  # type: ignore
                )
                new_adds_on_data: Dict[str, Any] = {"user_id": claims.user_id}
                # ensure same adds-on were not selected twice
                if adds_on_one == adds_on_two:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Cannot select the same add-ons twice for the same Idea",
                    )

                if adds_on_one:
                    # flag to track match for unit and amount
                    first_price_match = False
                    for price in adds_on_one.prices:
                        for schema_price in schema.adds_on_service_ids:
                            # ensure that the unit and amount matches db record
                            if price.get("amount") == schema_price.get(
                                "amount"
                            ) and price.get("unit") == schema_price.get("unit"):
                                first_price_match = True
                                logger.warning(
                                    "schema-amount: %s, schema-unit: %s, db-amount: %s, db-unit: %s",
                                    schema_price.get("amount"),
                                    schema_price.get("unit"),
                                    price.get("amount"),
                                    price.get("unit"),
                                )
                                # update the payment for add ons one,
                                amount += Decimal(price.get("amount", 0))

                                new_adds_on_data["adds_on_one_price"] = price
                    if first_price_match is False:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=f"Invalid amount or unit for adds-on with ID: {adds_on_one.id}",
                        )
                    new_adds_on_data["adds_on_one_id"] = adds_on_one.id

                if adds_on_two:
                    # flag to track match for unit and amount
                    second_price_match = False
                    for price2 in adds_on_two.prices:
                        for schema_price2 in schema.adds_on_service_ids:
                            # ensure that the unit and amount matches db record
                            if price2.get("amount") == schema_price2.get(
                                "amount"
                            ) and price2.get("unit") == schema_price2.get("unit"):
                                second_price_match = True
                                # update the payment for add ons two,
                                amount += Decimal(price2.get("amount", 0))
                                new_adds_on_data["adds_on_two_price"] = price2
                    if second_price_match is False:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=f"Invalid amount or unit for adds-on with ID: {adds_on_two.id}",
                        )
                    new_adds_on_data["adds_on_two_id"] = adds_on_two.id
                # create an instance of the add ons consultations

                new_adds_on_consult = await adds_on_consultation_repo.create(
                    session=session,
                    adds_on_data=new_adds_on_data,
                    commit=False,
                )
                add_to_session.append(new_adds_on_consult)

            user = await user_repository.fetch(session=session, user_id=claims.user_id)
            assert user is not None

            payment_data = {
                # "user_subscription_id": user_sub.get("id"),  Set this field during payment verification
                "subscription_plan_id": sub_plan.id,
                "subscription_plan_idx": sub_plan.idx,
                "adds_on_consultation_id": new_adds_on_consult,
                "user_id": claims.user_id,
                "amount": amount,
                "currency": "USD",
            }
            if new_adds_on_consult:
                payment_data["adds_on_consultation"] = new_adds_on_consult

            provider, payment_ref, tx_reference, payment_link = (
                await self.__get_payment_links(
                    user_location=user.location,
                    user_data={
                        "email": user.email,
                        "id": user.id,
                        "firstname": user.firstname,
                        "lastname": user.lastname,
                    },
                    amount=amount,
                    subscription_plan_id=sub_plan.id,
                    to_purchase=schema.to_purchase,  # enables redirect to checkout/purchase and not /checkout
                )
            )

            payment_data["provider"] = provider
            payment_data["payment_reference"] = payment_ref

            new_payment = await payment_repo.create(
                session=session,
                payment_data=payment_data,
                commit=False,
            )

            add_to_session.append(new_payment)

            session.add_all(add_to_session)
            await session.commit()
            await session.refresh(new_payment)

            return InitiatePaymentResponseSchema(
                data=InitiatePaymentResDataSchema(
                    subscription_plan_id=sub_plan.id,
                    has_active_payment=False,
                    payment_link=payment_link,
                    payment_reference=payment_ref,
                    tx_reference=tx_reference,
                    gen_pdf=schema.gen_pdf,
                )
            )

        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:  # type: ignore
            logger.error("Error initiating payment %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong. Could not complete Payment initiation",
            ) from exc

    async def __validate_selected_adds_on(
        self,
        session: AsyncSession,
        adds_on_ids: List[str],
    ) -> Tuple[AddsOnServiceModel, Optional[AddsOnServiceModel]]:
        """
        Checks for the presence of selected adds on services,
          Must return atleast one AddsOnServiceModel.
        Args:
            session (AsyncSession): The database async session object.
            adds_on_ids (list(str)): The adds on IDs
        Returns:
            Tuple(AddsOnServiceModel, AddsOnServiceModel | None)
        Raises:
            HTTPException 404 (AddsOnServiceModel not found).
        """
        adds_ons = []
        for adds_id in adds_on_ids:
            adds_on_exists = await adds_on_service_repo.fetch(
                session=session, adds_on_id=adds_id
            )
            if not adds_on_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Selected Adds-On not found",
                )
            adds_ons.append(adds_on_exists)
        if len(adds_ons) == 1:
            adds_ons.append(None)
        return tuple(adds_ons)

    async def __get_payment_links(
        self,
        user_data: Dict[str, Any],
        subscription_plan_id: str,
        amount: Any | Decimal,
        provider: str | None = None,
        user_location: str | None = None,
        to_purchase: str | None = None,
    ) -> Tuple[str, str, str | None, str]:
        """
        Gets payment links.

        Args:
            user_data (Dict[str, Any]):
            subscription_plan_id: (str)
            amount: (Any | Decimal):
            provider: (str | None):
            user_location: (str | None):
        Returns:
            Tuple[str, str, str]: provider, payment_ref, tx_reference, payment_link
        """
        # NOTE: temporary use flutterwave for all payments
        tx_reference = None
        provider = "flutterwave"
        flutterwave_payment_res = await flutterwave_service.initiate_payment(
            sub_plan_id=subscription_plan_id,
            email=user_data.get("email", ""),
            user_id=user_data.get("id", ""),
            amount=float(amount),
            name=f"{user_data.get('firstname', '')} {user_data.get('lastname') or ''}",
            to_purchase=to_purchase,
        )
        payment_ref = flutterwave_payment_res.get("payment_ref") or ""
        payment_link = flutterwave_payment_res.get("payment_link") or ""
        return provider, payment_ref, tx_reference, payment_link

    async def verify_payment(
        self,
        schema: VerifyPaymentRequestSchema,
        request: CustomRequest,
        background_tasks: BackgroundTasks,
    ) -> VerifyPaymentResponseSchema:
        """
        Verifies payment
        """
        try:
            session, claims = get_claims_and_session(request=request)
            payment_exists = await payment_repo.fetch(
                session=session,
                user_id=claims.user_id,
                payment_reference=schema.payment_reference,
            )
            if not payment_exists:
                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=schema.payment_reference,
                        tx_reference=schema.tx_reference,
                        provider="",
                        subscription_plan_id="",
                        subscription_plan_idx=None,
                        status="not found",
                        amount=str(0),
                    ),
                    message="Payment record not found",
                    status="not found",
                )
            if payment_exists.status in [
                PaymentStatusEnum.APPROVED,
                PaymentStatusEnum.PAID,
                PaymentStatusEnum.SUCCESS,
                PaymentStatusEnum.SUCCESSFUL,
            ]:
                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=payment_exists.payment_reference,
                        tx_reference=payment_exists.tx_reference,
                        provider=payment_exists.provider.value,
                        subscription_plan_id=payment_exists.subscription_plan_id,
                        status=payment_exists.status.value,
                        subscription_plan_idx=payment_exists.subscription_plan_idx,
                        amount=str(payment_exists.amount),
                    ),
                    message="Payment already verified as successful!",
                )

            # fetch current user sub plan and set to expired and not current
            current_user_sub = await user_subscription_repo.fetch(
                session=session, is_current=True, user_id=claims.user_id
            )
            assert current_user_sub is not None

            return await self.__verify_flutterwave(
                session=session,
                current_user_sub=current_user_sub,
                payment_exists=payment_exists,
                schema=schema,
                claims=claims,
                background_tasks=background_tasks,
                gen_pdf=schema.gen_pdf,
            )

        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error verifying payment: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong. Could not complete Payment verification",
            ) from exc

    # +++++++++++++++++++++++++++++ FLUTTERWAVE +++++++++++++++++++++++++
    async def __verify_flutterwave(
        self,
        schema: VerifyPaymentRequestSchema,
        current_user_sub,
        payment_exists: PaymentModel,
        session: AsyncSession,
        claims: Claims,
        background_tasks: BackgroundTasks,
        gen_pdf: bool,
    ) -> VerifyPaymentResponseSchema:
        """
        Verifies flutterwave payment
        """
        try:

            result = await flutterwave_service.verify_payment(
                tx_reference=schema.tx_reference,
            )
            inner_status = STATUS.get(result.get("inner_status", "").upper())
            f_paid_amount = result.get("amount", 0)
            # check for amount discrepancy
            if not f_paid_amount or int(f_paid_amount) < int(payment_exists.amount):
                logger.warning(
                    "paid amount $%s, expected $%s",
                    f_paid_amount,
                    payment_exists.amount,
                )
                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=payment_exists.payment_reference,
                        provider=payment_exists.provider.value,
                        subscription_plan_id=payment_exists.subscription_plan_id,
                        status=payment_exists.status.value,
                        tx_reference=payment_exists.tx_reference,
                        subscription_plan_idx=payment_exists.subscription_plan_idx,
                        amount=str(payment_exists.amount or 0),
                    ),
                    message=f"paid amount ${f_paid_amount}, expected ${payment_exists.amount}",
                    status="amount discrepancy",
                )
            if inner_status in [
                PaymentStatusEnum.APPROVED,
                PaymentStatusEnum.PAID,
                PaymentStatusEnum.SUCCESS,
                PaymentStatusEnum.SUCCESSFUL,
            ]:

                session_add = []

                updated_current_user_sub = await user_subscription_repo.update(
                    session=session,
                    update_data={"is_current": False, "is_expired": True},
                    commit=False,
                    user_sub=current_user_sub,
                )

                session_add.append(updated_current_user_sub)

                session.add_all(session_add)

                await session.flush([updated_current_user_sub])  # type: ignore

                tx_reference = (
                    str(result.get("tx_reference"))
                    if isinstance(result.get("tx_reference"), int)
                    else result.get("tx_reference")
                )

                # create new sub plan in case user could not use payment.
                # during prompting, this new_sub can be fetched as current and reused.
                new_user_sub = await user_subscription_repo.create(
                    session=session,
                    commit=False,
                    user_sub_data={
                        "user_id": claims.user_id,
                        "is_current": True,
                        "is_expired": False,
                        "subscription_plan_id": payment_exists.subscription_plan_id,
                    },
                )

                session_add.append(new_user_sub)
                session.add_all(session_add)

                await session.flush()

                updated_payment = await payment_repo.update(
                    session=session,
                    payment_record=payment_exists,
                    update_data={
                        "status": inner_status,
                        "tx_reference": tx_reference,
                        "paid_at": sa.func.now(),
                        "user_subscription_id": new_user_sub.id,
                    },
                    commit=False,
                )

                session.add_all(session_add)

                await session.commit()
                if updated_payment:
                    await session.refresh(updated_payment)
                if updated_current_user_sub:
                    await session.refresh(updated_current_user_sub)
                if new_user_sub:
                    await session.refresh(new_user_sub)

                if payment_exists.purchase_event_id and payment_exists.amount:
                    self.__send_meta_event(
                        payment=payment_exists,
                        email=claims.email,
                        background_tasks=background_tasks,
                    )
                if gen_pdf:
                    await self.__send_report_files_via_mail(
                        session=session,
                        user_id=claims.user_id,
                        background_tasks=background_tasks,
                    )
                    if new_user_sub:
                        # immediately update the current user sub plan as expired
                        new_user_sub.is_expired = True
                        await session.commit()
                        await session.refresh(new_user_sub)

                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=updated_payment.payment_reference,
                        provider=updated_payment.provider.value,
                        subscription_plan_id=updated_payment.subscription_plan_id,
                        status=updated_payment.status.value,
                        tx_reference=tx_reference,
                        subscription_plan_idx=updated_payment.subscription_plan_idx,
                        amount=str(updated_payment.amount or 0),
                    ),
                    gen_pdf=schema.gen_pdf,
                )
            update_data: Dict[str, Any] = {
                "status": inner_status or PaymentStatusEnum.FAILED
            }
            if result.get("tx_reference"):
                update_data["tx_reference"] = (
                    str(result.get("tx_reference"))
                    if isinstance(result.get("tx_reference"), int)
                    else result.get("tx_reference")
                )
                await payment_repo.update(
                    session=session,
                    payment_record=payment_exists,
                    update_data=update_data,
                    commit=True,
                )
            status_ = result.get("inner_status", "failed").upper().replace("_", " ")

            return VerifyPaymentResponseSchema(
                data=PaymentBase(
                    payment_reference=payment_exists.payment_reference,
                    provider=payment_exists.provider.value,
                    subscription_plan_id=payment_exists.subscription_plan_id,
                    status=payment_exists.status.value,
                    tx_reference=payment_exists.tx_reference,
                    subscription_plan_idx=payment_exists.subscription_plan_idx,
                    amount=str(payment_exists.amount or 0),
                ),
                message=f"Payment {status_}",
                status=status_,
            )
        except PsycopgError as exc:
            logger.error("Error verifying flutterwave payment: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc
        except Exception as exc:
            logger.error("Error verifying flutterwave payment: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    # ##################### HELPER ###########################
    def __send_meta_event(
        self, payment: PaymentModel, email: str, background_tasks: BackgroundTasks
    ) -> None:
        """
        Sends meta events

        :param payment: Payment object
        :type payment: PaymentModel
        :param email: Current user email
        :type email: str
        """
        contents = [
            {
                "sub_id": payment.subscription_plan_id,
                "quantity": 1,
                "idx": payment.subscription_plan_idx,
            },
        ]
        if payment.adds_on_consultation_id:
            contents.append(
                {
                    "adds_on_consultation_id": payment.adds_on_consultation_id,
                }
            )
        custom_data = {
            "contents": contents,
            "value": float(payment.amount),
            "currency": "USD",
        }
        background_tasks.add_task(
            MetaPixelService.send_meta_event,
            event_name="Purchase",
            email=email,
            event_id=str(payment.purchase_event_id),
            custom_data=custom_data,
        )

    async def __send_report_files_via_mail(
        self, session: AsyncSession, user_id: str, background_tasks: BackgroundTasks
    ) -> None:
        """
        Sends report files to User

        :param session: AsyncSession object
        :type session: AsyncSession
        :param user_id: The current user ID
        :type user_id: str
        :param background_tasks: Backgroud task
        :type background_tasks: BackgroundTasks
        """
        prompt = await startup_ideas_repo.fetch_last_prompt(
            session=session, user_id=user_id
        )
        if prompt:
            prompt_dict = prompt.__dict__.copy()
            prompt_dict.pop("_sa_instance_state", None)
            prompt_dict.pop("created_at", None)
            prompt_dict.pop("updated_at", None)
            prompt_dict.pop("id", None)
            prompt_dict.pop("user_id", None)
            prompt_str = prompt_dict.pop("prompt", None)
            # generate files here
            background_tasks.add_task(
                send_report_files_via_mail,
                prompt_reply=prompt_dict,
                session=session,
                user_id=user_id,
                prompt=prompt_str,
            )

    async def generate_subscription_link(
        self, request: CustomRequest, flutterwave_plan_id: int
    ):
        """
        Generate subscription link
        """
        session, claims = get_claims_and_session(request=request)
        plan_exists = await subscription_plan_repo.fetch(
            session=session,
            flutterwave_plan_id=flutterwave_plan_id,
        )
        if not plan_exists or not plan_exists.flutterwave_plan_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found",
            )
        result = await flutterwave_service.generate_subscription_link(
            email=claims.email,
            plan_id=plan_exists.flutterwave_plan_id,
            plan_price=float(plan_exists.price),
            currency="USD",
            user_id=claims.user_id,
            sub_name=plan_exists.name,
        )
        payment_data = {
            "subscription_plan_id": plan_exists.id,
            "subscription_plan_idx": plan_exists.idx,
            "user_id": claims.user_id,
            "amount": plan_exists.price,
            "currency": "USD",
            "payment_reference": result.get("tx_ref"),  # custom
            "tx_reference": result.get(
                "tx_ref"
            ),  # temporarily the same with payment_reference
            "provider": "flutterwave",
            "flutterwave_subscription_id": plan_exists.flutterwave_plan_id,
        }
        _ = await payment_repo.create(
            session=session,
            payment_data=payment_data,
            commit=True,
        )

        return GenerateBillingResponseSchema(data=result)

    async def verify_billing(
        self, request: CustomRequest, schema: VerifyPaymentRequestSchema
    ):
        """
        Verifies billing payment
        """
        try:
            session, claims = get_claims_and_session(request=request)
            payment_exists = await payment_repo.fetch(
                session=session,
                user_id=claims.user_id,
                payment_reference=schema.tx_reference,  # custom
            )
            if not payment_exists:
                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=schema.payment_reference,
                        tx_reference=schema.tx_reference,
                        provider="",
                        subscription_plan_id="",
                        subscription_plan_idx=None,
                        status="not found",
                        amount=str(0),
                    ),
                    message="Payment record not found",
                    status="not found",
                )
            if not payment_exists.flutterwave_subscription_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification is for reoccurring only",
                )
            if payment_exists.status in [
                PaymentStatusEnum.APPROVED,
                PaymentStatusEnum.PAID,
                PaymentStatusEnum.SUCCESS,
                PaymentStatusEnum.SUCCESSFUL,
            ]:
                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=payment_exists.payment_reference,
                        tx_reference=payment_exists.tx_reference,
                        provider=payment_exists.provider.value,
                        subscription_plan_id=payment_exists.subscription_plan_id,
                        status=payment_exists.status.value,
                        subscription_plan_idx=payment_exists.subscription_plan_idx,
                        amount=str(payment_exists.amount),
                    ),
                    message="Payment already verified as successful!",
                )
            result = await flutterwave_service.verify_payment(
                tx_reference=schema.payment_reference,
            )
            if result.get("status") == "not_found":
                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=payment_exists.payment_reference,
                        provider=payment_exists.provider.value,
                        subscription_plan_id=payment_exists.subscription_plan_id,
                        status=payment_exists.status.value,
                        tx_reference=payment_exists.tx_reference,
                        subscription_plan_idx=payment_exists.subscription_plan_idx,
                        amount=str(payment_exists.amount or 0),
                    ),
                    message="No transaction was found for this id",
                    status="not found",
                )
            inner_status = STATUS.get(result.get("inner_status", "").upper())
            f_paid_amount = result.get("amount", 0)
            # check for amount discrepancy
            if not f_paid_amount or int(f_paid_amount) < int(payment_exists.amount):
                logger.warning(
                    "paid amount $%s, expected $%s",
                    f_paid_amount,
                    payment_exists.amount,
                )
                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=payment_exists.payment_reference,
                        provider=payment_exists.provider.value,
                        subscription_plan_id=payment_exists.subscription_plan_id,
                        status=payment_exists.status.value,
                        tx_reference=payment_exists.tx_reference,
                        subscription_plan_idx=payment_exists.subscription_plan_idx,
                        amount=str(payment_exists.amount or 0),
                    ),
                    message=f"paid amount ${f_paid_amount}, expected ${payment_exists.amount}",
                    status="amount discrepancy",
                )
            if inner_status in [
                PaymentStatusEnum.APPROVED,
                PaymentStatusEnum.PAID,
                PaymentStatusEnum.SUCCESS,
                PaymentStatusEnum.SUCCESSFUL,
            ]:
                session_add = []
                remaining_credits = 0
                existing_sub = await user_subscription_repo.fetch(
                    session=session,
                    user_id=claims.user_id,
                    _type=SubscriptionPlanTypeEnum.REOCCURRING,
                    is_expired=False,
                )
                if existing_sub:
                    existing_sub.is_expired = True
                    session_add.append(existing_sub)
                    associated_sub_plan = await subscription_plan_repo.fetch(
                        session=session,
                        plan_id=existing_sub.subscription_plan_id,
                    )
                    assert associated_sub_plan
                    if existing_sub.credit_used < associated_sub_plan.credits:
                        remaining_credits += (
                            associated_sub_plan.credits - existing_sub.credit_used
                        )

                new_sub_plan = await subscription_plan_repo.fetch(
                    session=session,
                    plan_id=payment_exists.subscription_plan_id,
                )
                assert new_sub_plan
                new_user_sub = await user_subscription_repo.create(
                    session=session,
                    commit=False,
                    user_sub_data={
                        "user_id": claims.user_id,
                        "is_current": False,
                        "is_expired": False,
                        "subscription_plan_id": payment_exists.subscription_plan_id,
                        "flutterwave_subscription_id": payment_exists.flutterwave_subscription_id,
                        "_type": SubscriptionPlanTypeEnum.REOCCURRING.value,
                        "remaining_credits": remaining_credits + new_sub_plan.credits,
                    },
                )
                session_add.append(new_user_sub)
                session.add_all(session_add)

                tx_reference = (
                    str(result.get("tx_reference"))
                    if isinstance(result.get("tx_reference"), int)
                    else result.get("tx_reference")
                ) or schema.payment_reference
                updated_payment = await payment_repo.update(
                    session=session,
                    payment_record=payment_exists,
                    update_data={
                        "status": inner_status,
                        "tx_reference": tx_reference or schema.payment_reference,
                        "paid_at": sa.func.now(),
                        "user_subscription_id": new_user_sub.id,
                    },
                    commit=False,
                )

                session.add_all(session_add)

                await session.commit()
                if updated_payment:
                    await session.refresh(updated_payment)
                return VerifyPaymentResponseSchema(
                    data=PaymentBase(
                        payment_reference=updated_payment.payment_reference,
                        provider=updated_payment.provider.value,
                        subscription_plan_id=updated_payment.subscription_plan_id,
                        status=updated_payment.status.value,
                        tx_reference=tx_reference,
                        subscription_plan_idx=updated_payment.subscription_plan_idx,
                        amount=str(updated_payment.amount or 0),
                        flutterwave_subscription_id=updated_payment.flutterwave_subscription_id,
                    ),
                    gen_pdf=schema.gen_pdf,
                )
            update_data: Dict[str, Any] = {
                "status": inner_status or PaymentStatusEnum.FAILED
            }
            if result.get("tx_reference"):
                update_data["tx_reference"] = (
                    str(result.get("tx_reference"))
                    if isinstance(result.get("tx_reference"), int)
                    else result.get("tx_reference")
                )
                await payment_repo.update(
                    session=session,
                    payment_record=payment_exists,
                    update_data=update_data,
                    commit=True,
                )
            status_ = result.get("inner_status", "failed").upper().replace("_", " ")

            return VerifyPaymentResponseSchema(
                data=PaymentBase(
                    payment_reference=payment_exists.payment_reference,
                    provider=payment_exists.provider.value,
                    subscription_plan_id=payment_exists.subscription_plan_id,
                    status=payment_exists.status.value,
                    tx_reference=payment_exists.tx_reference,
                    subscription_plan_idx=payment_exists.subscription_plan_idx,
                    amount=str(payment_exists.amount or 0),
                ),
                message=f"Payment {status_}",
                status=status_,
            )
        except HTTPException as exc:
            raise exc
        except Exception as exc:
            logger.error("Error verifying billing payment: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def flutterwave_webhook(self, request: CustomRequest):
        """
        Handles flutterwave webhook notification
        """
        return await flutterwave_service.flutterwave_webhook(request=request)


payment_service = PaymentService()
