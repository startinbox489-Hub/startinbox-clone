"""
Auth Route
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from api.schema.user_schema import (
    SignupRequestSchema,
    SignupResponseSchema,
    SigninRequestSchema,
    SigninResponseSchema,
    SignoutResponseSchema,
    GoogleSignUpRequestSchema,
    UserMeResponseSchema,
)
from api.service.user_service import user_service
from api.database.sql_database import sql_database
from api.schema.default_response_schema import responses, CustomRequest
from api.core.config import settings
from api.service.auth_service import auth_service
from api.utils.get_remote_user_id_or_ip import get_user_id_or_remote_address


auth_router = APIRouter(
    tags=["AUTHENTICATION"],
    prefix="/auth",
)

limiter = Limiter(key_func=get_user_id_or_remote_address)

PER_MINUTE = "20/minute"
PER_SECOND = "2/second"
if settings.test == "TRUE":
    PER_MINUTE = "1000/minute"
    PER_SECOND = "100/second"


@auth_router.post(
    "/signup",
    response_model=SignupResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def signup_user(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_with_tx)],
    schema: SignupRequestSchema,
) -> SignupResponseSchema:
    """
    Signs up a new user using email, password, with optional phone_number.
    """
    return await user_service.signup_user(
        session=session, schema=schema, request=request
    )


@auth_router.post(
    "/signup/google",
    response_model=SigninResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def google_signup_user(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_with_tx)],
    schema: GoogleSignUpRequestSchema,
    response: Response,
) -> SigninResponseSchema:
    """
    Signs up a user via google oauth2.

    Will signin a user if user already signed up.
    """
    return await user_service.signup_google(
        session=session,
        schema=schema,
        request=request,
        response=response,
        signin=False,
    )


@auth_router.post(
    "/signin",
    response_model=SigninResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def signin_user(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    schema: SigninRequestSchema,
    response: Response,
) -> SigninResponseSchema:
    """
    Signs in a user using email, password.
    """
    return await user_service.signin_user(
        session=session, schema=schema, request=request, response=response
    )


@auth_router.post(
    "/signin/google",
    response_model=SigninResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def google_signin_user(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_with_tx)],
    schema: GoogleSignUpRequestSchema,
    response: Response,
) -> SigninResponseSchema:
    """
    Signs in a user via google oauth2.
    """
    return await user_service.signup_google(
        session=session,
        schema=schema,
        request=request,
        response=response,
        signin=True,
    )


@auth_router.delete(
    "/signout",
    response_model=SignoutResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_guard)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def signout_user(
    request: CustomRequest,
    session: Annotated[AsyncSession, Depends(sql_database.get_db_with_tx)],
) -> SignoutResponseSchema:
    """
    Signs out a user.

    Raises:
        401 on Invalid token
        500 Internal Error
        403 Forbidden resource
        405 Invalid Method
        404 Not found
    """
    return await user_service.signout_user(session=session, request=request)


@auth_router.post(
    "/refresh-tokens",
    response_model=SigninResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    dependencies=[Depends(auth_service.get_refresh_token_header)],
)
@limiter.limit(PER_MINUTE)
@limiter.limit(PER_SECOND)
async def refresh_tokens(
    request: CustomRequest,
    response: Response,
) -> SigninResponseSchema:
    """
    Refreshes User tokens.
    Revokes old(refresh) tokens.

    Returns the new refresh token in the ehader as x-refresh-token
    """
    return await user_service.refresh_token(
        request=request,
        response=response,
    )


@auth_router.get(
    "/user/me",
    response_model=UserMeResponseSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
    dependencies=[Depends(auth_service.auth_session_guard)],
)
@limiter.limit(PER_MINUTE)
async def retrieve_user_data(
    request: CustomRequest,
) -> UserMeResponseSchema:
    """
    Retrieves User data
    """
    return await user_service.get_user_data(
        request=request,
    )
