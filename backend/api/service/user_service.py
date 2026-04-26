"""
User Service
"""

from datetime import datetime, timedelta, timezone

import decimal
from fastapi import HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from uuid6 import uuid7

from api.repository.user_repo import user_repository, UserModel

from api.schema.user_schema import (
    UserBase,
    SignupResponseSchema,
    SignupRequestSchema,
    SigninDataSchema,
    SigninRequestSchema,
    SigninResponseSchema,
    TokenBase,
    SignoutResponseSchema,
    GoogleSignUpRequestSchema,
    UserMeResponseSchema,
)
from api.repository.user_session_repo import user_session_repo
from api.core.config import settings
from api.service.auth_service import auth_service
from api.schema.default_response_schema import CustomRequest
from api.repository.social_oauth_repo import social_oauth_repository
from api.repository.news_letter_repo import news_letter_repo
from api.repository.subscription_plan_repo import subscription_plan_repo
from api.model.model_enums import UserProviderEnum
from api.repository.user_subscription_repo import user_subscription_repo
from api.utils.task_logger import create_logger
from api.utils.get_session_claims_from_request import get_claims_and_session
from api.service.user_location_service import user_location_service
from api.repository.plan_usage_statistics_repo import plan_usage_statistics_repo
from api.utils.get_client_ip import get_client_ip_render
from api.utils.master_prompts import LAUNCH_BUNDLE_PROMPT


logger = create_logger(":: UserService ::")


class UserService:
    """
    User Service
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.repo = user_repository

    async def signup_user(
        self,
        session: AsyncSession,
        schema: SignupRequestSchema,
        request: CustomRequest,
    ) -> SignupResponseSchema:
        """
        Signs up users.

        Args:
            session (AsyncSession): The database injected async session object.
            schema (SignupRequestSchema): The request payload object as pydantic model.
        Returns:
            SignupResponseSchema (pydantic): The response payload to be serialized.
        """
        try:
            if (
                not isinstance(schema.agreed_to_terms, bool)
                or schema.agreed_to_terms is False
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Must Agree to Terms",
                )

            if schema.idempotency_key:
                idempotency_key_exists = await self.repo.fetch_by_idempotency_key(
                    session=session, idempotency_key=schema.idempotency_key
                )
                if idempotency_key_exists:
                    return SignupResponseSchema(
                        data=UserBase.model_validate(
                            idempotency_key_exists, from_attributes=True
                        ),
                        message="User already created succesfully",
                    )

            email_exists = await self.repo.fetch_by_email(
                session=session, email=str(schema.email), attributes=["email"]
            )
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Email already in use"
                )
            if schema.phone_number:
                phone_number_exists = await self.repo.fetch_by_phone_number(
                    session=session,
                    phone_number=schema.phone_number,
                    attributes=["phone_number"],
                )
                if phone_number_exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Phone Number already in use",
                    )

            user_data = schema.model_dump(exclude={"confirm_password"})

            add_to_sessions_list = []
            user_location = None
            user_ip = get_client_ip_render(request=request)
            if user_ip:
                user_location_dict = await user_location_service.get_country_ipinfo(
                    user_ip
                )
                if user_location_dict:
                    user_location = user_location_dict.get("country_name", "").lower()
                    user_data["location"] = user_location

            new_user = await self.repo.create(
                session=session,
                user_data=user_data,
                commit=False,
            )
            add_to_sessions_list.append(new_user)

            news_letter_subbed = await news_letter_repo.fetch(
                session=session, email=schema.email
            )
            # set this flag to help decide if i refresh news_letter record after not (if updated)
            news_letter_is_subbed = news_letter_subbed is not None

            if not news_letter_subbed:
                news_letter_subbed = await news_letter_repo.create(
                    session=session,
                    news_letter_data={"email": schema.email},
                    commit=False,
                    user=new_user,
                )
                add_to_sessions_list.append(news_letter_subbed)

            elif news_letter_subbed and news_letter_subbed.is_unsubscribed:
                news_letter_subbed = await news_letter_repo.update(
                    session=session,
                    update_data={"is_unsubscribed": False, "unsubscribed_at": None},
                    news_letter=news_letter_subbed,
                    commit=False,
                )

            else:
                pass

            default_plan = await subscription_plan_repo.fetch(
                session=session,
                is_default=True,
                include_features=True,
            )
            if not default_plan:
                # to prevent 500 error, create a default plan if missing from db
                default_plan = await subscription_plan_repo.create(
                    session=session,
                    plan_data={
                        "name": "Free trial",
                        "price": decimal.Decimal(0.00),
                        "description": "Access all features once, no card required",
                        "id": "free_trial",
                        "is_default": True,
                        "dummy": True,
                        "is_popular": False,
                        "idx": 0,
                        "prompt": LAUNCH_BUNDLE_PROMPT,
                    },
                    commit=False,
                )
                await session.flush([default_plan])

            user_sub = await user_subscription_repo.create(
                session=session,
                user_sub_data={
                    "user_id": new_user.id,
                    "subscription_plan_id": default_plan.id,  # type: ignore
                    "is_current": True,
                },
                commit=False,
                user=new_user,
            )
            add_to_sessions_list.append(user_sub)

            new_plan_usage_stats = await plan_usage_statistics_repo.create(
                session=session,
                commit=False,
                usage_data={},
                user=new_user,
            )

            add_to_sessions_list.append(new_plan_usage_stats)

            session.add_all(add_to_sessions_list)
            await session.commit()

            # refresh news_letter is it was updated
            if news_letter_is_subbed:
                await session.refresh(news_letter_subbed)

            return SignupResponseSchema(
                data=UserBase.model_validate(new_user, from_attributes=True),
            )
        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            logger.error("Error signing up user: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def signin_user(
        self,
        session: AsyncSession,
        schema: SigninRequestSchema,
        request: CustomRequest,
        response: Response,
    ) -> SigninResponseSchema:
        """
        Signin a User

        Args:
            session (AsyncSession): The database injected async session object.
            schema (SignupRequestSchema): The request payload object as pydantic model.
            request (Request): The request object.
        Returns:
            SigninResponseSchema (pydantic): The response payload to be serialized.
        """
        try:
            email_exists = await self.repo.fetch_by_email(
                session=session, email=str(schema.email)
            )

            if not email_exists:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
                )

            password_valid = email_exists.verify_password(schema.password)

            if not password_valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
                )
            if email_exists.deleted_at:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            return await self.create_signin_schema(
                session=session, request=request, response=response, user=email_exists
            )
        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            logger.error("Error siging in user: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def signout_user(
        self, request: CustomRequest, session: AsyncSession
    ) -> SignoutResponseSchema:
        """
        Signs out a User.
        """
        try:
            claims = request.state.claims
            if not claims:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            user_session_exists = await user_session_repo.fetch(
                session=session,
                jti=claims.jti,
                user_id=claims.user_id,
            )
            if not user_session_exists:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            if user_session_exists.is_revoked:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="expired token"
                )

            await user_session_repo.update(
                session=session,
                user_session=user_session_exists,
                update_data={"is_revoked": True, "revoked_at": sa.func.now()},
            )
            request.cookies.clear()

            return SignoutResponseSchema()
        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            logger.error("Error signing out user: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def signup_google(
        self,
        session: AsyncSession,
        schema: GoogleSignUpRequestSchema,
        request: CustomRequest,
        response: Response,
        signin: bool = False,
    ) -> SigninResponseSchema:
        """
        Signs up/in users via google
        """
        try:
            print("debug pring google id_token: ", schema.id_token)
            id_info = await auth_service.verify_google_id_token(token=schema.id_token)
            email_exists = await self.repo.fetch_by_email(
                session=session, email=id_info.email
            )

            if not signin and (
                not isinstance(schema.agreed_to_terms, bool)
                or schema.agreed_to_terms is False
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Must Agree to Terms",
                )
            add_to_sessions_list = []

            user_location = None

            user_ip = get_client_ip_render(request=request)
            user_location_dict = await user_location_service.get_country_from_ip(
                user_ip
            )
            if user_location_dict:
                user_location = user_location_dict.get("country_name", "").lower()

            if email_exists:
                if not email_exists.firstname and id_info.given_name:
                    email_exists.firstname = id_info.given_name
                if not email_exists.lastname and id_info.family_name:
                    email_exists.lastname = id_info.family_name
                if not email_exists.profile_photo and id_info.picture:
                    email_exists.profile_photo = str(id_info.picture)
                # login user here
                return await self.create_signin_schema(
                    session=session,
                    request=request,
                    response=response,
                    user=email_exists,
                )
            email_exists = await self.repo.create(
                session=session,
                user_data={
                    "email": id_info.email,
                    "email_verified": id_info.email_verified,
                    "sub": id_info.sub,
                    "firstname": id_info.given_name,
                    "lastname": id_info.family_name,
                    "signup_provider": UserProviderEnum.GOOGLE.value,
                    "profile_photo": id_info.picture and str(id_info.picture) or None,
                    "location": user_location,
                },
                commit=False,
            )
            add_to_sessions_list.append(email_exists)

            new_user_social_oauth2 = await social_oauth_repository.create(
                session=session,
                social_oauth_data={
                    "email": id_info.email,
                    "email_verified": id_info.email_verified,
                    "social_sub": id_info.sub,
                    "given_name": id_info.given_name,
                    "family_name": id_info.family_name,
                    "picture": id_info.picture and str(id_info.picture) or None,
                },
                user=email_exists,
                commit=False,
            )
            add_to_sessions_list.append(new_user_social_oauth2)

            # incase if user had subscribed with same email before becoming a user
            news_letter_subbed = await news_letter_repo.fetch(
                session=session, email=id_info.email
            )
            # set this flag to help decide if i refresh news_letter record after not (if updated)
            news_letter_is_subbed = news_letter_subbed is not None
            # create news_letter if user is fresh like yoghurt
            if not news_letter_subbed:
                news_letter_subbed = await news_letter_repo.create(
                    session=session,
                    news_letter_data={
                        "email": id_info.email,
                        "name": f"{id_info.given_name} {id_info.family_name or ''}",
                    },
                    commit=False,
                    user=email_exists,
                )
                add_to_sessions_list.append(news_letter_subbed)
            # incase if user had unsubscribed with same email before becoming a user
            elif news_letter_subbed.is_unsubscribed:
                news_letter_subbed = await news_letter_repo.update(
                    session=session,
                    update_data={"is_unsubscribed": False, "unsubscribed_at": None},
                    news_letter=news_letter_subbed,
                    commit=False,
                )
            else:
                pass
            # add user_subscription
            default_plan = await subscription_plan_repo.fetch(
                session=session, is_default=True, include_features=True
            )
            # if for some reason default_plan has been deleted or not seeded yet, raise exception
            if not default_plan:
                # to prevent 500 error, create a default plan if missing from db
                default_plan = await subscription_plan_repo.create(
                    session=session,
                    plan_data={
                        "name": "Free trial",
                        "price": decimal.Decimal(0.00),
                        "description": "Access all features once, no card required",
                        "id": "free_trial",
                        "is_default": True,
                        "dummy": True,
                        "is_popular": False,
                        "idx": 0,
                        "prompt": LAUNCH_BUNDLE_PROMPT,
                    },
                    commit=False,
                )
                await session.flush([default_plan])
            new_user_sub = await user_subscription_repo.create(
                session=session,
                user_sub_data={
                    "subscription_plan_id": default_plan.id,
                    "is_current": True,
                },
                commit=False,
                user=email_exists,
            )
            add_to_sessions_list.append(new_user_sub)

            new_plan_usage_stats = await plan_usage_statistics_repo.create(
                session=session,
                commit=False,
                usage_data={},
                user=email_exists,
            )

            add_to_sessions_list.append(new_plan_usage_stats)

            session.add_all(add_to_sessions_list)
            await session.commit()
            # refresh news_letter is it was updated
            if news_letter_is_subbed:
                await session.refresh(news_letter_subbed)

            return await self.create_signin_schema(
                session=session, request=request, response=response, user=email_exists
            )
        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            logger.error("Google oauth2 error: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def refresh_token(
        self, request: CustomRequest, response: Response
    ) -> SigninResponseSchema:
        """
        Refreshes tokens for user
        """
        try:
            claims = request.state.claims
            session = request.state.session
            if not claims:
                logger.error(msg="claims is None")
                raise RuntimeError("claims is None")
            if not session:
                logger.error(msg="session is None")
                raise RuntimeError("session is None")

            user = await self.repo.fetch(session=session, user_id=claims.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return await self.create_signin_schema(
                session=session, request=request, response=response, user=user
            )
        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            logger.error("Error refreshing tokens: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def create_signin_schema(
        self,
        user: UserModel,
        request: CustomRequest,
        response: Response,
        session: AsyncSession,
    ) -> SigninResponseSchema:
        """
        create and return SigninResponseSchema for signin
        """
        claims = {
            "user_id": user.id,
            "jti": str(uuid7()),
            "ipaddress": request.client and request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "location": user.location or "",
        }

        _ = await user_session_repo.create(session=session, user_session_data=claims)
        role = user.role if isinstance(user.role, str) else user.role.value
        claims["role"] = role
        claims["email"] = user.email

        access_token = await auth_service.generate_tokens(claims=claims)
        refresh_token = await auth_service.generate_tokens(
            claims=claims, token_type="refresh"
        )

        user_base = UserBase.model_validate(user, from_attributes=True)
        token_base = TokenBase(
            access_token=access_token,
            expires_in=int(
                (
                    datetime.now(timezone.utc)
                    + timedelta(days=settings.jwt_access_token_expiry)
                ).timestamp()
            ),
        )

        signin_data = SigninDataSchema(user=user_base, token=token_base)

        response.headers["X-REFRESH-TOKEN"] = refresh_token

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="none",  # "strict"
            secure=(settings.app_env != "development"),  # Crucial for localhost testing
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            secure=(settings.app_env != "development"),
        )

        return SigninResponseSchema(data=signin_data)

    async def get_user_data(self, request: CustomRequest) -> UserMeResponseSchema:
        """
        Retrieves user data
        """
        try:
            session, claims = get_claims_and_session(request)
            user = await self.repo.fetch(session=session, user_id=claims.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No User account found",
                )
            return UserMeResponseSchema(
                data=UserBase.model_validate(user, from_attributes=True)
            )
        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            logger.error("Error fetching user data: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc


user_service = UserService()
