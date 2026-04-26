"""
Test startup ideas repo
"""

import pytest

from api.repository.user_repo import user_repository
from api.repository.startup_ideas_repo import startup_ideas_repo
from api.model import UserModel
from api.tests.repository import idea_reply_data


class TestStartupIdeasRepo:
    """
    Test startup ideas
    """

    @pytest.mark.asyncio
    async def test_a_create_and_fetch_startup_ideas(self, async_db_session):
        """
        Test create and fetch startup ideas
        """

        new_user = await user_repository.create(
            async_db_session,
            {
                "email": "johnsonstartup@gmail.com",
                "password": "Johnson1234#",
                "firstname": "Johnson",
                "lastname": "Dennis",
            },
        )

        assert isinstance(new_user, UserModel)

        ideas_data = {
            "user_id": new_user.id,
            "prompt": "explain",
        }
        ideas_data.update(idea_reply_data["A. Validation Output"])
        ideas_data.update(idea_reply_data["B. Launch Content Generator"])
        influencers: list = idea_reply_data["C. Influencer Outreach Generator"][
            "influencers"
        ]
        ideas_data.update({"influencer_one": influencers[0]})
        ideas_data.update({"influencer_two": influencers[1]})
        ideas_data.update({"influencer_three": influencers[2]})
        ideas_data.update(
            {
                "go_to_market_strategy_outline": idea_reply_data[
                    "C. Influencer Outreach Generator"
                ]["go_to_market_strategy_outline"]
            }
        )

        new_idea = await startup_ideas_repo.create(
            session=async_db_session, ideas_data=ideas_data
        )

        assert new_idea.prompt == ideas_data["prompt"]

        found_idea = await startup_ideas_repo.fetch(
            session=async_db_session, ideas_id=new_idea.id, user_id=new_user.id
        )

        assert found_idea == new_idea

    @pytest.mark.asyncio
    async def test_b_fetch_all_startup_ideas(self, async_db_session):
        """
        Test fetch all startup ideas
        """
        found_user = await user_repository.fetch(
            session=async_db_session, email="johnsonstartup@gmail.com"
        )
        assert found_user is not None

        found_ideas = await startup_ideas_repo.fetch_all(
            session=async_db_session, user_id=found_user.id
        )

        assert len(found_ideas) == 1
        assert found_ideas[0].prompt == "explain"

    @pytest.mark.asyncio
    async def test_c_update_startup_ideas(self, async_db_session):
        """
        Test update startup ideas
        """
        found_user = await user_repository.fetch(
            session=async_db_session, email="johnsonstartup@gmail.com"
        )
        assert found_user is not None

        found_ideas = await startup_ideas_repo.fetch_all(
            session=async_db_session, user_id=found_user.id
        )

        assert len(found_ideas) == 1
        assert found_ideas[0].prompt == "explain"

        update_idea = await startup_ideas_repo.update(
            session=async_db_session,
            ideas=found_ideas[0],
            update_data={"prompt": "do not explain"},
        )

        await async_db_session.refresh(update_idea)

        assert update_idea.prompt == "do not explain"
        assert found_ideas[0].prompt == "do not explain"

    @pytest.mark.asyncio
    async def test_d_delete_startup_ideas(self, async_db_session):
        """
        Test delete startup ideas
        """
        found_user = await user_repository.fetch(
            session=async_db_session, email="johnsonstartup@gmail.com"
        )
        assert found_user is not None

        found_ideas = await startup_ideas_repo.fetch_all(
            session=async_db_session, user_id=found_user.id
        )

        assert len(found_ideas) == 1
        assert found_ideas[0].prompt == "do not explain"

        await startup_ideas_repo.delete(
            session=async_db_session,
            user_id=found_user.id,
            ideas_id=found_ideas[0].id,
        )

        found_ideas2 = await startup_ideas_repo.fetch_all(
            session=async_db_session, user_id=found_user.id
        )

        assert len(found_ideas2) == 0
