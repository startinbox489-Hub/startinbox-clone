"""
Test sub plan repo
"""

import pytest
import sqlalchemy as sa

from api.repository.user_repo import user_repository
from api.model import UserModel


class TestUserRepo:
    """
    Test User repo
    """

    @pytest.mark.asyncio
    async def test_a_create_new_user(self, async_db_session):
        """
        Test create User
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnson@gmail.com",
                "phone_number": "+2347067575757",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        assert isinstance(new_user, UserModel)

        assert new_user.verify_password("Johnson1234#") is True

    @pytest.mark.asyncio
    async def test_b_fetch_user(self, async_db_session):
        """
        Test fetch User
        """

        found_user = await user_repository.fetch(
            async_db_session, email="johnson@gmail.com"
        )

        assert isinstance(found_user, UserModel)

    @pytest.mark.asyncio
    async def test_c_fetch_all_users(self, async_db_session):
        """
        Test fetch all Users
        """

        found_users = await user_repository.fetch_all(
            async_db_session,
        )

        assert len(found_users) > 0

    @pytest.mark.asyncio
    async def test_d_update_user(self, async_db_session):
        """
        Test update User
        """

        found_user = await user_repository.fetch(
            async_db_session, email="johnson@gmail.com"
        )

        assert found_user is not None

        updated_users = await user_repository.update(
            async_db_session,
            user=found_user,
            update_data={"email": "johnson.bourne@gmail.com"},
        )

        assert found_user.email == updated_users.email
        assert found_user.email == "johnson.bourne@gmail.com"

    @pytest.mark.asyncio
    async def test_e_delete_user(self, async_db_session):
        """
        Test delete User
        """

        found_user = await user_repository.fetch(
            async_db_session, email="johnson.bourne@gmail.com"
        )

        assert found_user is not None

        await user_repository.delete(
            async_db_session,
            user=found_user,
        )

        found_user = await user_repository.fetch(
            async_db_session,
            email="johnson.bourne@gmail.com",
        )

        assert found_user is None

    @pytest.mark.asyncio
    async def test_f_soft_delete_user(self, async_db_session):
        """
        Test soft-delete User
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnson1@gmail.com",
                "phone_number": "+2347067575757",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        assert isinstance(new_user, UserModel)

        await user_repository.update(
            async_db_session,
            user=new_user,
            update_data={"is_deleted": True, "deleted_at": sa.func.now()},
        )

        found_user = await user_repository.fetch(
            async_db_session,
            email="johnson1@gmail.com",
        )

        assert found_user is not None
        assert found_user.is_deleted is True
        assert found_user.deleted_at is not None
