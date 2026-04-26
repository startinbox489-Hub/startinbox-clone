"""
StartupIdeas Service
"""

from typing import Dict, Any
import json
from fastapi import status, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from api.repository.startup_ideas_repo import startup_ideas_repo
from api.schema.startup_ideas_schema import (
    StartupIdeasBase,
    StartupIdeasRequestSchema,
    StartupIdeasResponseSchema,
    FetchStartupIdeasResponseSchema,
    FetchStartupIdeasBase,
    FetchStartupIdeaResponseSchema,
    StartupIdeaDataSchema,
)
from api.schema.default_response_schema import CustomRequest, Claims
from api.utils.get_session_claims_from_request import get_claims_and_session
from api.repository.user_subscription_repo import (
    user_subscription_repo,
    UserSubscriptionModel,
)
from api.service.gemini_service import gemini_service
from api.service.url_secret_service import URLSecretService
from api.service.whatsapp_service import WhatsappService
from api.service.report_generator_service import report_generator_service
from api.utils.master_prompts import (
    FREE_PLAN_PROMPT,
    STARTER_PLAN_PROMPT,
    PRO_PLAN_PROMPT,
    LAUNCH_BUNDLE_PROMPT,
)
from api.utils.task_logger import create_logger
from api.repository.subscription_plan_repo import subscription_plan_repo
from api.repository.user_repo import user_repository
from api.repository.adds_on_consultation_repo import adds_on_consultation_repo
from api.core.config import settings
from api.repository.plan_usage_statistics_repo import (
    plan_usage_statistics_repo,
    PlanUsageStatisticModel,
)
from api.service.twilio_meta_service import twilio_meta_service
from api.utils.send_files_to_mail import send_report_files_via_mail
from api.model.model_enums import SubscriptionPlanTypeEnum


logger = create_logger(":: StartupIdeasService ::")


DEFAULT_PROMPTS = {
    0: FREE_PLAN_PROMPT,
    1: STARTER_PLAN_PROMPT,
    2: PRO_PLAN_PROMPT,
    3: LAUNCH_BUNDLE_PROMPT,
}


class StartupIdeasService:
    """
    StartupIdeas Service
    """

    async def generate_startup_idea(
        self,
        schema: StartupIdeasRequestSchema,
        request: CustomRequest,
        background_tasks: BackgroundTasks,
    ) -> StartupIdeasResponseSchema:
        """
        Add a new FAQ.

        Args:
            request (CustomRequest): The request object.
            schema (StartupIdeasRequestSchema): The request payload.
        Returns:
            StartupIdeasResponseSchema


        # FLOW

        1] idea is generate using gemini_service.
        2] docx/pdf is created using reports_generator_service.
            the filename is returned including the file extension.
        3] send the file to user.
            if using twilio (serves files via a route):
                generate a token and expire and set as queries in the twilio url.
                when twilio is serving the file, URLSecretService.verify_signed_url verifies the token and expires_at
            if using meta (does not serve over url):
                file is uploaded to meta and meta_file_id is used to send the file over to user.

        # RULES:
            must check the user subscription to determine if files are to be sent or not.
            must check if user is on free plan.
        """
        try:
            session_add = []
            session, claims = get_claims_and_session(request)

            if schema.type_ == "reoccurring":
                credit_plan = await user_subscription_repo.fetch(
                    session=session,
                    user_id=claims.user_id,
                    is_expired=False,
                    _type=SubscriptionPlanTypeEnum.REOCCURRING,
                )
                if not credit_plan:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User has no active Subscription",
                    )
                if credit_plan.credit_used >= credit_plan.remaining_credits:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Subscription credit exhausted!",
                    )
                selected_plan = await subscription_plan_repo.fetch(
                    session=session,
                    plan_id=credit_plan.subscription_plan_id,
                )
                assert selected_plan
                # generate with credits, update used count, used credit, remaining credits
                return await self.generate_idea_on_credit_sub(
                    background_tasks=background_tasks,
                    claims=claims,
                    credit_plan=credit_plan,
                    schema=schema,
                    session=session,
                    user_sub_plan_idx=selected_plan.idx,
                )

            selected_plan = await subscription_plan_repo.fetch(
                session=session, plan_idx=schema.idx
            )

            if not selected_plan:
                raise HTTPException(
                    status_code=404, detail="Selected Plan does not exist."
                )

            user_sub = await user_subscription_repo.fetch_with_plan(
                session=session, user_id=claims.user_id
            )

            assert user_sub is not None

            user_sub_plan_idx = user_sub.get("idx", 0)
            is_user_sub_expired = user_sub.get("is_expired", False)
            prompt = DEFAULT_PROMPTS[3]

            # allow prompt for free trials
            if selected_plan.idx == 0 and (
                user_sub_plan_idx == 0 or is_user_sub_expired is True
            ):
                prompt = selected_plan.prompt or DEFAULT_PROMPTS[3]

            elif (
                user_sub_plan_idx > 0 and is_user_sub_expired is False
            ):  # allow prompt for not expired plans(payment made and verified)

                # user has active payment
                prompt = DEFAULT_PROMPTS[user_sub_plan_idx]
            else:
                # block prompts for non-free trial, and no payment
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Payment is required for this selected Plan",
                )

            plan_usage_exists = await plan_usage_statistics_repo.fetch(
                session=session, user_id=claims.user_id
            )

            if (
                (user_sub_plan_idx == 0 or is_user_sub_expired)
                and plan_usage_exists
                and plan_usage_exists.free_plan_stats.get("use_count", 0) >= 1
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Free Trial Exhausted. Upgrade or Renew Subscription",
                )

            prompt_reply_text = gemini_service.generate_idea(
                prompt=schema.prompt,
                plan_prompt=prompt,
                background_tasks=background_tasks,
            )

            prompt_reply: dict = json.loads(prompt_reply_text)

            ideas_data = schema.model_dump(exclude={"idx", "type_"})

            ideas_data.update({"user_id": claims.user_id})

            serialized_prompt = self.__serialize_prompt_reply(prompt_reply=prompt_reply)

            ideas_data.update(serialized_prompt)

            if selected_plan.idx > 0 or user_sub_plan_idx > 0:
                # update active sub as expired if using paid plan
                await user_subscription_repo.update_with_id(
                    session=session,
                    user_sub_id=user_sub.get("id", ""),
                    update_data={"is_expired": True},
                    commit=False,
                )

            new_startup_idea = await startup_ideas_repo.create(
                session=session, ideas_data=ideas_data, commit=False
            )
            session_add.append(new_startup_idea)
            # update adds on with user startup idea to link them
            adds_on_exists = None
            if user_sub_plan_idx > 0:
                user_subscription_id = user_sub.get("id") or ""
                # fetch adds on consult via payments
                adds_on_exists = await adds_on_consultation_repo.fetch_from_user_sub_id(
                    session=session,
                    user_sub_id=user_subscription_id,
                )

                if adds_on_exists and adds_on_exists.startup_idea_id is None:

                    adds_on_exists.startup_idea = new_startup_idea
                    session_add.append(adds_on_exists)

            if plan_usage_exists:
                update_data = self.__calculate_plan_usage(
                    plan_idx=user_sub_plan_idx,
                    sub_expired=is_user_sub_expired,
                    plan_usage_stats=plan_usage_exists,  # type: ignore
                )
                await plan_usage_statistics_repo.update(
                    session=session,
                    plan_usage_stats=plan_usage_exists,  # type: ignore
                    commit=False,
                    update_data=update_data,
                )
                session_add.append(plan_usage_exists)

            session.add_all(session_add)
            await session.commit()
            if adds_on_exists:
                await session.refresh(adds_on_exists)
            if new_startup_idea:
                await session.refresh(new_startup_idea)
            if plan_usage_exists:
                await session.refresh(plan_usage_exists)
            logger.info(
                "selected plan index: %s, user current sub expired: %s",
                selected_plan.idx,
                is_user_sub_expired,
            )

            if selected_plan.idx > 0 or is_user_sub_expired is False:
                # user need to recieve formatted docs/pdf
                # logger.info("sending files to email: %s", claims.email)
                background_tasks.add_task(
                    self.__send_report_files_via_mail,
                    prompt_reply=prompt_reply,
                    session=session,
                    user_id=claims.user_id,
                    prompt=schema.prompt,
                )

            # idx = user_sub_plan_idx if is_user_sub_expired is False else schema.idx

            return StartupIdeasResponseSchema(
                data=StartupIdeaDataSchema(
                    validation=StartupIdeasBase(
                        id=new_startup_idea.id,
                        user_id=str(new_startup_idea.user_id),
                        prompt=new_startup_idea.prompt,
                        idea_validation=(
                            self.__trim_validation(
                                str(new_startup_idea.idea_validation)
                            )
                            if user_sub_plan_idx < 1
                            else new_startup_idea.idea_validation
                        ),
                        idea_score=new_startup_idea.idea_score,
                    ),
                    idx=user_sub_plan_idx,
                )
            )
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except SQLAlchemyError as exc:
            logger.error(
                "Database Error occurred when generating startup idea: %s", str(exc)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc
        except Exception as exc:
            logger.error("Error generating startup idea: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def generate_idea_on_credit_sub(
        self,
        background_tasks: BackgroundTasks,
        schema: StartupIdeasRequestSchema,
        claims: Claims,
        session: AsyncSession,
        credit_plan: UserSubscriptionModel,
        user_sub_plan_idx: int,
    ) -> StartupIdeasResponseSchema:
        """
        Generate idea on credits sub
        """
        session_add = []
        prompt = DEFAULT_PROMPTS[3]
        # generate with credits
        prompt_reply_text = gemini_service.generate_idea(
            prompt=schema.prompt,
            plan_prompt=prompt,
            background_tasks=background_tasks,
        )

        prompt_reply: dict = json.loads(prompt_reply_text)

        ideas_data = schema.model_dump(exclude={"idx", "type_"})

        ideas_data.update({"user_id": claims.user_id})  # type: ignore

        serialized_prompt = self.__serialize_prompt_reply(prompt_reply=prompt_reply)

        ideas_data.update(serialized_prompt)
        new_startup_idea = await startup_ideas_repo.create(
            session=session, ideas_data=ideas_data, commit=False
        )
        session_add.append(new_startup_idea)

        # update used count
        plan_usage: PlanUsageStatisticModel = await plan_usage_statistics_repo.fetch(
            session=session,
            user_id=claims.user_id,  # type: ignore
        )
        if not plan_usage:
            plan_usage = await plan_usage_statistics_repo.create(
                session=session,
                usage_data={},
                commit=False,
            )
            session_add.append(plan_usage)
            await session.flush([plan_usage])

        update_data = {}

        if credit_plan.subscription_plan_id == "silver":
            use_count = (plan_usage.silver_plan_stats.get("use_count") or 0) + 1
            update_data["use_count"] = use_count
            plan_usage.silver_plan_stats = update_data

        if credit_plan.subscription_plan_id == "gold":
            use_count = plan_usage.gold_plan_stats.get("use_count", 0) + 1
            update_data["use_count"] = use_count
            plan_usage.gold_plan_stats = update_data

        if credit_plan.subscription_plan_id == "diamond":
            use_count = plan_usage.diamond_plan_stats.get("use_count", 0) + 1
            update_data["use_count"] = use_count
            plan_usage.diamond_plan_stats = update_data
        session_add.append(plan_usage)

        # update used credit
        # credit_plan.credit_used += 1
        credit_plan = await user_subscription_repo.update(
            session=session,
            user_sub=credit_plan,
            update_data={
                "credit_used": credit_plan.credit_used + 1,
                "remaining_credits": credit_plan.remaining_credits - 1,
            },
            commit=False,
        )

        session_add.append(credit_plan)

        session.add_all(session_add)
        await session.commit()
        if new_startup_idea:
            await session.refresh(new_startup_idea)
        if plan_usage:
            await session.refresh(plan_usage)
        if credit_plan:
            await session.refresh(credit_plan)
        background_tasks.add_task(
            self.__send_report_files_via_mail,
            prompt_reply=prompt_reply,
            session=session,
            user_id=claims.user_id,  # type: ignore
            prompt=schema.prompt,
        )
        return StartupIdeasResponseSchema(
            data=StartupIdeaDataSchema(
                validation=StartupIdeasBase(
                    id=new_startup_idea.id,
                    user_id=str(new_startup_idea.user_id),
                    prompt=new_startup_idea.prompt,
                    idea_validation=new_startup_idea.idea_validation,
                    idea_score=new_startup_idea.idea_score,
                ),
                idx=user_sub_plan_idx,
            )
        )

    def __trim_validation(self, validation: str) -> str:
        """
        Trims Validation
        """
        if len(validation) > 150:
            return f"{validation[:100]}..."
        if len(validation) > 100:
            return f"{validation[:50]}..."
        if len(validation) > 80:
            return f"{validation[:40]}..."
        if len(validation) > 60:
            return f"{validation[:30]}..."
        if len(validation) > 40:
            return f"{validation[:20]}..."
        return f"{validation[:10]}..."

    async def fetch_all_startup_ideas(
        self,
        request: CustomRequest,
        page: int,
        limit: int,
    ) -> FetchStartupIdeasResponseSchema:
        """
        Fetch all StartupIdeas.

        Args:
            request (CustomRequest): The request object.
            page (int): The current page.
            limit (int): The number of StartupIdeas per page.
        Returns:
            FetchStartupIdeasResponseSchema
        """
        try:
            session, claims = get_claims_and_session(request)

            startup_ideas = await startup_ideas_repo.fetch_all(
                session=session,
                offset=(limit * page - limit),
                limit=limit,
                user_id=claims.user_id,
                attributes=["id", "user_id", "prompt"],
            )

            return FetchStartupIdeasResponseSchema(
                data=[
                    FetchStartupIdeasBase.model_validate(fq, from_attributes=True)
                    for fq in startup_ideas
                ]
            )
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error retrieving startup ideas: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def fetch_a_startup_idea(
        self,
        request: CustomRequest,
        startup_idea_id: str,
    ) -> FetchStartupIdeaResponseSchema:
        """
        Fetch a StartupIdea.

        Args:
            request (CustomRequest): The request object.
            startup_idea_id (str): The id of the startup idea.
        Returns:
            FetchStartupIdeaResponseSchema: if found
        """
        try:
            session, claims = get_claims_and_session(request)

            startup_idea = await startup_ideas_repo.fetch(
                session=session,
                user_id=claims.user_id,
                ideas_id=startup_idea_id,
            )
            if not startup_idea:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="startup idea not found",
                )

            startup_idea_base = StartupIdeasBase.model_validate(
                startup_idea, from_attributes=True
            )

            return FetchStartupIdeaResponseSchema(data=startup_idea_base)
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error retrieving startup ideas: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    def __serialize_prompt_reply(self, prompt_reply: dict) -> dict:
        """
        Serializes prompt_reply
        """
        prompt: dict = prompt_reply.get("A. Validation Output", {}) or {}
        if prompt_reply.get("B. Launch Content Generator", None):
            prompt.update(prompt_reply.get("B. Launch Content Generator", {}) or {})
        if prompt_reply.get("C. Influencer Outreach Generator", None):
            outreach: dict = prompt_reply.get("C. Influencer Outreach Generator", {})
            suffix = ["one", "two", "three"]
            for idx, influencer in enumerate(outreach.get("influencers", [])):
                if influencer and idx <= 2:
                    prompt.update({f"influencer_{suffix[idx]}": influencer})
            prompt.update(
                {
                    "go_to_market_strategy_outline": outreach.get(
                        "go_to_market_strategy_outline"
                    )
                }
                or {}
            )
        return prompt

    def __calculate_plan_usage(
        self,
        plan_idx: int,
        sub_expired: bool,
        plan_usage_stats: PlanUsageStatisticModel,
    ) -> Dict[str, Any]:
        """
        Calculate for plan usage use
        """
        update_data = {}
        if plan_idx == 0 or sub_expired:

            update_data["free_plan_stats"] = {
                "use_count": plan_usage_stats.free_plan_stats.get("use_count", 0) + 1
            }
        elif plan_idx == 1 and not sub_expired:
            update_data["starter_plan_stats"] = {
                "use_count": plan_usage_stats.starter_plan_stats.get("use_count", 0) + 1
            }
        elif plan_idx == 2 and not sub_expired:
            update_data["pro_plan_stats"] = {
                "use_count": plan_usage_stats.pro_plan_stats.get("use_count", 0) + 1
            }
        elif plan_idx == 3 and not sub_expired:
            update_data["launch_bundle_plan_stats"] = {
                "use_count": plan_usage_stats.launch_bundle_plan_stats.get(
                    "use_count", 0
                )
                + 1
            }
        return update_data

    async def __send_report_files_via_mail(
        self,
        prompt_reply: Dict[str, Any],
        session: AsyncSession,
        user_id: str,
        prompt: str,
    ) -> None:
        """
        Sends report files to email using resend service.
        """
        await send_report_files_via_mail(
            session=session,
            user_id=user_id,
            prompt_reply=prompt_reply,
            prompt=prompt,
        )

    async def __send_report_files_via_meta(
        self,
        prompt_reply: Dict[str, Any],
        session: AsyncSession,
        user_id: str,
    ) -> None:
        """
        Sends report files.
        """
        try:
            pdf = report_generator_service.export_pdf(data=prompt_reply)
            docx = report_generator_service.export_docx(data=prompt_reply)

            user = await user_repository.fetch(session=session, user_id=user_id)
            if user and user.phone_number:
                pdf_token = None
                if pdf:
                    pdf_token = URLSecretService.generate_signed_url(
                        filename=pdf, expires_in=120
                    )
                docx_token = None
                if docx:
                    docx_token = URLSecretService.generate_signed_url(
                        filename=docx, expires_in=120
                    )
                if pdf or docx:
                    media_urls = []
                    if pdf:
                        media_urls.append(
                            f"{settings.app_url}/api/v1/reports/{pdf}?token={pdf_token}&expires={120}"
                        )
                    if docx:
                        media_urls.append(
                            f"{settings.app_url}/api/v1/reports/{docx}?token={docx_token}&expires={120}"
                        )
                    await twilio_meta_service.send_files(
                        to_whatsapp_number=user.phone_number,
                        media_urls=media_urls,
                    )

        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            logger.warning("could not send meta file reports: %s", str(exc))

    async def send_report_files(
        self,
        prompt_reply: Dict[str, Any],
        session: AsyncSession,
        user_id: str,
    ):
        """
        Sends report files

        """
        try:
            pdf = report_generator_service.export_pdf(data=prompt_reply)
            docx = report_generator_service.export_docx(data=prompt_reply)

            user = await user_repository.fetch(session=session, user_id=user_id)
            if user and user.phone_number:
                pdf_token = None
                if pdf:
                    pdf_token = URLSecretService.generate_signed_url(
                        filename=pdf, expires_in=120
                    )
                docx_token = None
                if docx:
                    docx_token = URLSecretService.generate_signed_url(
                        filename=docx, expires_in=120
                    )
                whatsap_service = WhatsappService("twilio")
                if pdf or docx:
                    attachments = []
                    if pdf:
                        attachments.append(
                            f"{settings.app_url}/api/v1/reports/{pdf}?token={pdf_token}&expires={120}"
                        )
                    if docx:
                        attachments.append(
                            f"{settings.app_url}/api/v1/reports/{docx}?token={docx_token}&expires={120}"
                        )
                    await whatsap_service.send_message(
                        to_number=user.phone_number,
                        body="🚀 Your startup report is ready!",
                        attachments=attachments,
                    )

                    # await gmail_service.send_email_route(
                    #     context={
                    #         "recipient_email": user.email,
                    #         "email_subject": "🚀 Your startup report is ready!",
                    #         "template_name": "startup-report.html",
                    #         "attachments": [
                    #             f"docs/{docx}",
                    #             f"pdfs/{pdf}",
                    #         ],
                    #     }
                    # )
        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            logger.warning("could not send meta file reports: %s", str(exc))


startup_ideas_service = StartupIdeasService()
