"""
Test news letter repo
"""

import pytest
import sqlalchemy as sa

from api.repository.news_letter_repo import news_letter_repo
from api.model import NewsLetterSubscriptionModel


class TestNewsLetterRepo:
    """
    Test NewsLetter repo
    """

    @pytest.mark.asyncio
    async def test_a_create_new_news_letter(self, async_db_session):
        """
        Test create NewsLetter
        """

        news_letter = await news_letter_repo.create(
            async_db_session,
            {
                "email": "johnson.user.session@gmail.com",
                "name": "Johnson Dennis",
            },
        )

        assert isinstance(news_letter, NewsLetterSubscriptionModel)

        assert news_letter.email == "johnson.user.session@gmail.com"

    @pytest.mark.asyncio
    async def test_b_fetch_news_letter(self, async_db_session):
        """
        Test fetch NewsLetter
        """

        found_news_letter = await news_letter_repo.fetch(
            async_db_session, email="johnson.user.session@gmail.com"
        )

        assert isinstance(found_news_letter, NewsLetterSubscriptionModel)

    @pytest.mark.asyncio
    async def test_c_fetch_all_news_letters(self, async_db_session):
        """
        Test fetch all news letters
        """

        found_news_letters = await news_letter_repo.fetch_all(
            async_db_session,
        )

        assert len(found_news_letters) > 0

    @pytest.mark.asyncio
    async def test_d_update_news_letter(self, async_db_session):
        """
        Test update news letter
        """

        found_news_letter = await news_letter_repo.fetch(
            async_db_session, email="johnson.user.session@gmail.com"
        )

        assert found_news_letter is not None

        _ = await news_letter_repo.update(
            async_db_session,
            news_letter=found_news_letter,
            update_data={
                "name": None,
                "unsubscribed_at": sa.func.now(),
                "is_unsubscribed": True,
            },
        )

        assert found_news_letter.name is None
        assert found_news_letter.email is not None
        assert found_news_letter.is_unsubscribed is True
