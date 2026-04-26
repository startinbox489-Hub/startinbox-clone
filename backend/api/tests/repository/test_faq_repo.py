"""
Test TestFAQsRepo
"""

import pytest

from api.repository.faq_repo import faq_repo
from api.model import FAQsModel


class TestFAQsRepo:
    """
    Test TestFAQsRepo repo
    """

    @pytest.mark.asyncio
    async def test_a_create_new_faq(self, async_db_session):
        """
        Test create FAQ
        """

        faq = await faq_repo.create(
            async_db_session,
            {
                "question": "some message",
                "answer": "some answer",
            },
        )

        assert isinstance(faq, FAQsModel)

        assert faq.question == "some message"
        assert faq.answer == "some answer"

    @pytest.mark.asyncio
    async def test_b_fetch_faq(self, async_db_session):
        """
        Test fetch FAQ
        """
        faq = await faq_repo.create(
            async_db_session,
            {
                "question": "some message",
                "answer": "some answer",
            },
        )

        found_faq = await faq_repo.fetch(async_db_session, faq_id=faq.id)

        assert isinstance(found_faq, FAQsModel)

    @pytest.mark.asyncio
    async def test_c_fetch_all_faqs(self, async_db_session):
        """
        Test fetch all news letters
        """

        found_faqs = await faq_repo.fetch_all(
            async_db_session,
        )

        assert len(found_faqs) > 0

    @pytest.mark.asyncio
    async def test_d_update_faq(self, async_db_session):
        """
        Test update news letter
        """

        faq = await faq_repo.create(
            async_db_session,
            {
                "question": "some message",
                "answer": "some answer",
            },
        )

        found_faq = await faq_repo.fetch(async_db_session, faq_id=faq.id)

        assert found_faq is not None

        _ = await faq_repo.update(
            async_db_session,
            faq=found_faq,
            update_data={
                "question": "new question",
                "answer": "new answer",
            },
        )

        assert found_faq.question == "new question"
        assert found_faq.answer == "new answer"

    @pytest.mark.asyncio
    async def test_e_delete_faq(self, async_db_session):
        """
        Test delete FAQ
        """
        faq = await faq_repo.create(
            async_db_session,
            {
                "question": "corss message",
                "answer": "corss answer",
            },
        )

        await faq_repo.delete(session=async_db_session, faq_id=faq.id)

        found_faq = await faq_repo.fetch(async_db_session, faq_id=faq.id)

        assert found_faq is None
