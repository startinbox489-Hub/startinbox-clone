"""
Auth Service
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from jose import JWTError, jwt
from fastapi import HTTPException, status, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.utils.task_logger import create_logger
from api.schema.default_response_schema import CustomRequest, Claims, GoogleIdToken
from api.model import UserSessionModel
from api.database.sql_database import sql_database

logger = create_logger(":::  Auth Service  :::")

http_bearer_security = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="BearerAuth",
    description="JWT Bearer authentication",
    auto_error=False,
)

RequestCredentials = Annotated[
    HTTPAuthorizationCredentials, Depends(http_bearer_security)
]


class AuthService:
    """
    Auth Service
    """

    async def generate_tokens(self, claims: dict, token_type: str = "access") -> str:
        """
        Generates JWT tokens
        """
        try:
            if token_type not in ["access", "refresh"]:
                raise TypeError("token_type must be of access or refresh")

            secret: str = settings.jwt_secrets
            now = datetime.now(timezone.utc) + timedelta(milliseconds=0)

            claims["iss"] = settings.jwt_issuer
            claims["aud"] = settings.jwt_audience
            claims["token_type"] = token_type
            claims["exp"] = (
                now + timedelta(days=settings.jwt_access_token_expiry)
                if token_type == "access"
                else now + timedelta(days=settings.jwt_refresh_token_expiry)
            )
            claims["iat"] = now

            token = jwt.encode(claims=claims, key=secret)

            return token
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error in generate tokens:  %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def validate_tokens(
        self, token: str, user_agent: str, token_type: str = "access"
    ) -> Claims:
        """
        Validates JWT tokens
        """
        try:
            decoded_claims = jwt.decode(
                token=token,
                key=settings.jwt_secrets,
                algorithms=["HS256"],
                audience=settings.jwt_audience,
                issuer=settings.jwt_issuer,
            )
            claims = Claims(**decoded_claims)
            if token_type == "access":
                if claims.token_type != "access":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Cannot use refresh token",
                    )
            if token_type == "refresh":
                if claims.token_type != "refresh":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Cannot use access token",
                    )
            if claims.user_agent != user_agent:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token Deprecated",
                )
            return claims
        except JWTError as exc:
            logger.warning(msg=str(exc))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            ) from exc
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error in validate tokens:  %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def auth_guard(
        self,
        credential: RequestCredentials,
        request: CustomRequest,
        session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    ) -> None:
        """
        Uses DI to Validates auth bearer and sets claims to request.
        e.g request.claims = claims
        request.current_user = claims.get("user_id")
        where claims is the decoded jwt values.
        """
        cookie_token = request.cookies.get("access_token", "")
        if not credential and not cookie_token:
            raise HTTPException(status_code=401, detail="Missing access token.")
        token = credential and credential.credentials or None
        scheme = credential and credential.scheme or None
        if scheme != "Bearer" and not cookie_token:
            raise HTTPException(
                status_code=401,
                detail="Authorization Bearer scheme or access token required",
            )

        user_agent = request.headers.get("user-agent", "")

        claims = await self.validate_tokens(
            token=(token or cookie_token), token_type="access", user_agent=user_agent
        )

        request.state.claims = claims
        request.state.current_user = claims.user_id
        request.state.session = session

        return

    async def auth_session_guard(
        self,
        credential: RequestCredentials,
        request: CustomRequest,
        session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    ) -> None:
        """
        Uses DI to Validates auth bearer and sets claims to request.
        Checks for session revocation in the database.

        e.g request.claims = claims
        request.current_user = claims.get("user_id")
        where claims is the decoded jwt values.
        """
        try:
            await self.auth_guard(
                credential=credential, request=request, session=session
            )

            query = sa.select(
                UserSessionModel.is_revoked, UserSessionModel.revoked_at
            ).where(
                UserSessionModel.jti
                == (request.state.claims and request.state.claims.jti or "")
            )
            session_exists = (await session.execute(query)).mappings().one_or_none()

            if not session_exists:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Malformed session."
                )
            if session_exists.get("is_revoked") is True:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Revoked session."
                )
            if session_exists.get("revoked_at") is not None:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Revoked session."
                )
            request.state.session = session
            return
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error in auth session guard:  %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def auth_session_guard_with_tx(
        self,
        credential: RequestCredentials,
        request: CustomRequest,
        session: Annotated[AsyncSession, Depends(sql_database.get_db_with_tx)],
    ) -> None:
        """
        Uses DI to Validates auth bearer and sets claims to request.
        Checks for session revocation in the database.

        e.g request.claims = claims
        request.current_user = claims.get("user_id")
        where claims is the decoded jwt values.
        """
        try:
            await self.auth_guard(
                credential=credential, request=request, session=session
            )

            query = sa.select(
                UserSessionModel.is_revoked, UserSessionModel.revoked_at
            ).where(
                UserSessionModel.jti
                == (request.state.claims and request.state.claims.jti or "")
            )
            session_exists = (await session.execute(query)).mappings().one_or_none()

            if not session_exists:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Malformed session."
                )
            if session_exists.get("is_revoked") is True:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Revoked session."
                )
            if session_exists.get("revoked_at") is not None:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Revoked session."
                )
            request.state.session = session
            return
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error in auth session guard:  %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def auth_session_guard_admin(
        self,
        credential: RequestCredentials,
        request: CustomRequest,
        session: Annotated[AsyncSession, Depends(sql_database.get_db_no_tx)],
    ) -> None:
        """
        Uses DI to Validates auth bearer and sets claims to request.
        Checks for session revocation in the database.

        e.g request.claims = claims
        request.current_user = claims.get("user_id")
        where claims is the decoded jwt values.
        """
        try:
            await self.auth_guard(
                credential=credential, request=request, session=session
            )
            claims = request.state.claims
            assert claims is not None

            if claims.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough Privilege.",
                )

            query = sa.select(
                UserSessionModel.is_revoked, UserSessionModel.revoked_at
            ).where(UserSessionModel.jti == claims.jti)
            session_exists = (await session.execute(query)).mappings().one_or_none()

            if not session_exists:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Malformed session."
                )
            if session_exists.get("is_revoked") is True:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Revoked session."
                )
            if session_exists.get("revoked_at") is not None:
                raise HTTPException(
                    status_code=401, detail="Unauthorized access. Revoked session."
                )
            request.state.session = session
            return
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error in admin auth session guard:  %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def get_refresh_token_header(
        self,
        request: CustomRequest,
        session: Annotated[AsyncSession, Depends(sql_database.get_db_with_tx)],
        x_refresh_token: str | None = Header(title="X-REFRESH-TOKEN", default=None),
    ) -> None:
        """
        Retrieves refresh token from header
        """
        try:
            cookie_refresh = request.cookies.get("refresh_token", None)
            if not x_refresh_token and not cookie_refresh:
                raise HTTPException(
                    status_code=401, detail="Missing X-REFRESH-TOKEN Header"
                )

            user_agent = request.headers.get("user-agent", "")

            claims = await self.validate_tokens(
                token=(x_refresh_token or cookie_refresh or ""),
                user_agent=user_agent,
                token_type="refresh",
            )

            request.state.claims = claims
            request.state.current_user = claims.user_id or "Guest"

            query = sa.select(UserSessionModel).where(
                UserSessionModel.jti == claims.jti
            )
            session_exists = (await session.execute(query)).scalar_one_or_none()

            if not session_exists:
                raise HTTPException(
                    status_code=401,
                    detail="Unauthorized access. Malformed refresh-token.",
                )
            if session_exists.is_revoked is True:
                raise HTTPException(
                    status_code=401,
                    detail="Unauthorized access. Revoked refresh-token.",
                )
            if session_exists.revoked_at is not None:
                raise HTTPException(
                    status_code=401,
                    detail="Unauthorized access. Revoked refresh-token.",
                )

            stmt = (
                sa.update(UserSessionModel)
                .where(UserSessionModel.jti == claims.jti)
                .values(is_revoked=True, revoked_at=sa.func.now())
            )

            await session.execute(stmt)
            request.state.session = session
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error in get refresh token header guard:  %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc

    async def verify_google_id_token(self, token: str) -> GoogleIdToken:
        """
        Verifies google id-token
        """
        try:
            id_info = id_token.verify_oauth2_token(
                id_token=token,
                request=requests.Request(),
                audience=settings.google_client_id,
            )
            # print("id_info: ", id_info)
            google_id_token = GoogleIdToken.model_validate(
                id_info, from_attributes=True
            )
            return google_id_token
        except GoogleAuthError as exc:
            logger.warning(msg=str(exc))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google ID Token",
            ) from exc
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.error("Error in verify google id token:  %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from exc


auth_service = AuthService()
