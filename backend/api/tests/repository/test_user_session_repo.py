"""
Test user-session repo
"""

import pytest

from api.repository.user_session_repo import user_session_repo
from api.repository.user_repo import user_repository
from api.model import UserSessionModel, UserModel


class TestUserSessionRepo:
    """
    Test UserSession repo
    """

    @pytest.mark.asyncio
    async def test_a_create_new_user_session(self, async_db_session):
        """
        Test create UserSession
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnson.user.session@gmail.com",
                "phone_number": "+2347064343422",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        assert isinstance(new_user, UserModel)

        new_session = await user_session_repo.create(
            async_db_session,
            {
                "user_id": new_user.id,
                "user_agent": "test",
                "ipaddress": "127.0.0.1",
                "jti": "12121212-1212-1212-1212-121212121212",
            },
        )

        assert new_session.is_revoked is False
        assert isinstance(new_session, UserSessionModel)

    @pytest.mark.asyncio
    async def test_b_fetch_user_session(self, async_db_session):
        """
        Test fetch UserSession
        """

        found_user_session = await user_session_repo.fetch(
            async_db_session, jti="12121212-1212-1212-1212-121212121212"
        )

        assert isinstance(found_user_session, UserSessionModel)

    @pytest.mark.asyncio
    async def test_c_fetch_all_user_sessions(self, async_db_session):
        """
        Test fetch all Users
        """
        user = await user_repository.fetch_by_email(
            async_db_session,
            email="johnson.user.session@gmail.com",
        )

        assert isinstance(user, UserModel)

        found_user_sessions = await user_session_repo.fetch_all(
            async_db_session, user_id=user.id
        )

        assert len(found_user_sessions) > 0

    @pytest.mark.asyncio
    async def test_d_update_user(self, async_db_session):
        """
        Test update User
        """

        found_user_session = await user_session_repo.fetch(
            async_db_session, jti="12121212-1212-1212-1212-121212121212"
        )

        assert found_user_session is not None

        updated_users = await user_session_repo.update(
            async_db_session,
            user_session=found_user_session,
            update_data={"is_revoked": True},
        )

        assert found_user_session.is_revoked == updated_users.is_revoked
        assert found_user_session.is_revoked == True

    @pytest.mark.asyncio
    async def test_e_delete_user_session(self, async_db_session):
        """
        Test delete UserSession
        """

        found_user_session = await user_session_repo.fetch(
            async_db_session, jti="12121212-1212-1212-1212-121212121212"
        )

        assert found_user_session is not None

        await user_session_repo.delete(
            async_db_session,
            user_session=found_user_session,
        )

        found_user_session = await user_session_repo.fetch(
            async_db_session,
            jti="12121212-1212-1212-1212-121212121212",
        )

        assert found_user_session is None
