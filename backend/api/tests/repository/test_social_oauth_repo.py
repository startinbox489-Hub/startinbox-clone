"""
Test social oauth repo
"""

import pytest
import sqlalchemy as sa

from api.repository.user_repo import user_repository
from api.model import UserModel, SocialOauthModel
from api.repository.social_oauth_repo import social_oauth_repository


class TestSocialOauthRepo:
    """
    Test Social Oauth Repo
    """

    @pytest.mark.asyncio
    async def test_a_create_new_social_oauth(self, async_db_session):
        """
        Test social oauth
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonsocial@gmail.com",
                "phone_number": "+2347067000757",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        assert isinstance(new_user, UserModel)

        new_social_oauth = await social_oauth_repository.create(
            async_db_session,
            {
                "user_id": new_user.id,
                "social_sub": new_user.id,
                "email": "johnsonsocial@gmail.com",
                "email_verified": True,
                "given_name": "Johnson",
            },
        )

        assert isinstance(new_social_oauth, SocialOauthModel)

        assert new_social_oauth.given_name is not None
        assert new_social_oauth.user_id is not None
        assert new_social_oauth.family_name is None

    @pytest.mark.asyncio
    async def test_b_fetch_social_oauth(self, async_db_session):
        """
        Test fetch social oauth record
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonsocial2@gmail.com",
                "phone_number": "+2347065500757",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        assert isinstance(new_user, UserModel)

        new_social_oauth = await social_oauth_repository.create(
            async_db_session,
            {
                "user_id": new_user.id,
                "social_sub": new_user.id,
                "email": "johnsonsocial2@gmail.com",
                "email_verified": True,
                "given_name": "Johnson",
            },
        )

        assert isinstance(new_social_oauth, SocialOauthModel)

        social_exists = await social_oauth_repository.fetch(
            async_db_session, new_user.id, social_sub=new_user.id, email=new_user.email
        )

        assert social_exists is not None

        assert new_social_oauth.given_name == social_exists.given_name
        assert new_social_oauth.user_id == social_exists.user_id
        assert new_social_oauth.family_name == social_exists.family_name
