"""
Test auth service
"""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
import pytest
from api.service.auth_service import auth_service
from api.core.config import settings


class TestAuthService:
    """
    Test auth Service
    """

    @pytest.mark.asyncio
    async def test_generate_tokens(self):
        """
        Test generate jwt tokens
        """

        token = await auth_service.generate_tokens(
            claims={
                "ipaddress": "127.0.0.1",
                "user_agent": "test",
                "user_id": "1234",
                "jti": "56789",
                "sub": "1234",
                "role": "regular",
                "email": "some@email.com",
            }
        )

        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_validate_access_tokens(self):
        """
        Test validate access jwt tokens
        """

        data_claims = {
            "ipaddress": "127.0.0.1",
            "user_agent": "test",
            "user_id": "1234",
            "jti": "56789",
            "sub": "1234",
            "role": "regular",
            "email": "some@email.com",
        }

        # generate token
        access_token = await auth_service.generate_tokens(claims=data_claims)

        assert isinstance(access_token, str)

        # validate token
        access_token_claims = await auth_service.validate_tokens(
            token=access_token, user_agent="test"
        )

        assert data_claims["ipaddress"] == access_token_claims.ipaddress
        assert data_claims["jti"] == access_token_claims.jti
        assert data_claims["iss"] == access_token_claims.iss

        # compare exp
        assert int(access_token_claims.exp) <= int(
            (
                datetime.now(timezone.utc)
                + timedelta(days=settings.jwt_access_token_expiry)
            ).timestamp()
        )
        assert int(access_token_claims.exp) < int(
            (
                datetime.now(timezone.utc)
                + timedelta(days=settings.jwt_refresh_token_expiry)
            ).timestamp()
        )

        # check for error raised
        with pytest.raises(HTTPException) as exc:
            access_token_claims = await auth_service.validate_tokens(
                token=access_token, user_agent="test", token_type="refresh"
            )
        assert "Cannot use access token" in str(exc.value)

        with pytest.raises(HTTPException) as exc:
            access_token_claims = await auth_service.validate_tokens(
                token=access_token, user_agent="test1"
            )
        assert "Token Deprecated" in str(exc.value)

    @pytest.mark.asyncio
    async def test_validate_refresh_tokens(self):
        """
        Test validate refresh jwt tokens
        """

        data_claims = {
            "ipaddress": "127.0.0.1",
            "user_agent": "test",
            "user_id": "1234",
            "jti": "56789",
            "sub": "1234",
            "role": "regular",
            "email": "some@email.com",
        }

        refresh_token = await auth_service.generate_tokens(
            claims=data_claims, token_type="refresh"
        )

        assert isinstance(refresh_token, str)

        refresh_token_claims = await auth_service.validate_tokens(
            token=refresh_token, user_agent="test", token_type="refresh"
        )

        assert data_claims["ipaddress"] == refresh_token_claims.ipaddress
        assert data_claims["jti"] == refresh_token_claims.jti
        assert data_claims["iss"] == refresh_token_claims.iss

        assert int(refresh_token_claims.exp) <= int(
            (
                datetime.now(timezone.utc)
                + timedelta(days=settings.jwt_refresh_token_expiry)
            ).timestamp()
        )
        assert int(refresh_token_claims.exp) > int(
            (
                datetime.now(timezone.utc)
                + timedelta(days=settings.jwt_access_token_expiry)
            ).timestamp()
        )

        with pytest.raises(HTTPException) as exc:
            refresh_token_claims = await auth_service.validate_tokens(
                token=refresh_token, user_agent="test", token_type="access"
            )
        assert "Cannot use refresh token" in str(exc.value)
        with pytest.raises(HTTPException) as exc:
            refresh_token_claims = await auth_service.validate_tokens(
                token=refresh_token, user_agent="test1", token_type="refresh"
            )
        assert "Token Deprecated" in str(exc.value)
