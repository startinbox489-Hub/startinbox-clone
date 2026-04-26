"""
CONFTEST MODULE
"""

# Set test environment
import os
from typing import AsyncGenerator, Any, Tuple
from decimal import Decimal
from unittest.mock import AsyncMock
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from fastapi import BackgroundTasks

os.environ["TEST"] = "TRUE"

from main import app
from api.database.sql_database import sql_database, Base

from api.repository.subscription_plan_repo import (
    subscription_plan_repo,
    SubscriptionPlanModel,
)
from api.repository.subscription_plan_features_repo import (
    subscription_plan_feature_repo,
    SubscriptionPlanFeatureModel,
)
from api.repository.adds_on_repo import adds_on_service_repo
from api.repository.user_subscription_repo import user_subscription_repo
from api.repository.subscription_plan_repo import subscription_plan_repo
from api.repository.user_repo import user_repository


# ++++++++++++++++++ db setup fixtures ++++++++++++++++++++++++++++++


@pytest.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with sql_database.async_scopped_session_obj() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await sql_database.async_scopped_session_obj.remove()
            await session.close()


@pytest.fixture(scope="function", autouse=True)
async def test_setup():
    """
    create database session for testing service classes
    """
    async with sql_database.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield


@pytest.fixture(scope="function")
async def test_teardown_db():
    """
    create database session for testing service classes
    """
    await sql_database.drop_tables()
    await sql_database.async_engine.dispose()
    yield


# ++++++++++++++++++ app client ++++++++++++++++++++++++++++++


@pytest.fixture(scope="function")
async def app_sync_client() -> AsyncGenerator[TestClient, None]:
    """
    Sync test client for websocket connection tests
    """
    with TestClient(app) as app_clients:
        yield app_clients


# ++++++++++++++++++ app background tasks ++++++++++++++++++++++++++++++


@pytest.fixture(scope="function", autouse=True)
async def background_tasks_fix():
    """
    Background_tasks_fix
    """
    mock_bgt = AsyncMock(spec=BackgroundTasks, return_value=None)
    return mock_bgt


# ++++++++++++++++++ seed subscription plans ++++++++++++++++++++++++++++++


@pytest.fixture(autouse=True)
async def seed_subscription_plans(
    test_setup,
) -> AsyncGenerator[
    tuple[SubscriptionPlanModel, list[SubscriptionPlanFeatureModel]], Any
]:
    """
    Seed subs
    """
    session = sql_database.async_session_factory()
    # free plan
    free = await subscription_plan_repo.fetch(
        session=session, plan_id="free_trial", plan_idx=0
    )
    if not free:
        free = await subscription_plan_repo.create(
            session,
            {
                "name": "Free",
                "price": Decimal("0.00"),
                "description": "Free subscription plan",
                "is_default": True,
                "idx": 0,
                "id": "free_trial",
            },
        )
    free_plan_feature = await subscription_plan_feature_repo.fetch(
        session=session,
        plan_id=free.id,
        feature_name="free offer",
    )
    if not free_plan_feature:
        free_plan_feature = await subscription_plan_feature_repo.create(
            session,
            {
                "plan_id": free.id,
                "feature_name": "starter",
                "value": True,
            },
        )
    # starter plan
    starter = await subscription_plan_repo.fetch(
        session=session, plan_id="starter", plan_idx=1
    )
    if not starter:
        starter = await subscription_plan_repo.create(
            session,
            {
                "name": "Starter",
                "price": Decimal("29.99"),
                "description": "Starter subscription plan",
                "is_default": False,
                "idx": 1,
                "id": "starter",
            },
        )
    starter_plan_feature = await subscription_plan_feature_repo.fetch(
        session=session,
        plan_id=starter.id,
        feature_name="starter",
    )
    if not starter_plan_feature:
        starter_plan_feature = await subscription_plan_feature_repo.create(
            session,
            {
                "plan_id": starter.id,
                "feature_name": "starter",
                "value": False,
            },
        )
    # silver plan
    silver = await subscription_plan_repo.fetch(
        session=session, plan_id="silver", plan_idx=2
    )
    if not silver:
        silver = await subscription_plan_repo.create(
            session,
            {
                "name": "Silver Plan",
                "price": Decimal("29.99"),
                "description": "Silver subscription plan",
                "is_default": False,
                "idx": 2,
                "id": "silver",
                "credits": 5,
                "flutterwave_plan_id": 12345,
                "_type": "reoccurring",
            },
        )
    silver_plan_feature = await subscription_plan_feature_repo.fetch(
        session=session,
        plan_id=starter.id,
        feature_name="silver",
    )
    if not silver_plan_feature:
        silver_plan_feature = await subscription_plan_feature_repo.create(
            session,
            {
                "plan_id": silver.id,
                "feature_name": "silver",
                "value": False,
            },
        )

    yield free, [free_plan_feature]  # type: ignore


@pytest.fixture(scope="function", autouse=True)
async def seed_adds_on_services(
    test_setup,
) -> AsyncGenerator[Tuple[Any, Any], Any]:
    """
    Seed subs
    """
    session = sql_database.async_session_factory()

    adds_on_one_exists = await adds_on_service_repo.fetch(
        session=session, adds_on_id="00000000-0000-0000-0000-000000000000"
    )
    if not adds_on_one_exists:
        adds_on_one_exists = await adds_on_service_repo.create(
            session=session,
            adds_on_data={
                "id": "00000000-0000-0000-0000-000000000000",
                "name": "adss on 1",
                "prices": [{"amount": 300, "unit": "week"}],
            },
        )
    adds_on_two_exists = await adds_on_service_repo.fetch(
        session=session, adds_on_id="00000000-0000-0000-0000-000000000001"
    )
    if not adds_on_two_exists:
        adds_on_two_exists = await adds_on_service_repo.create(
            session=session,
            adds_on_data={
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "adss on 2",
                "prices": [{"amount": 200, "unit": "week"}],
            },
        )

    yield adds_on_one_exists, adds_on_two_exists


@pytest.fixture(scope="function", autouse=True)
async def admin_factory(test_setup, seed_subscription_plans):
    """
    Add admins
    """
    session = sql_database.async_session_factory()
    new_user = await user_repository.create(
        session,
        {
            "email": f"{str(uuid.uuid4()).replace('-', '')}@gmail.com",
            "password": "Johnson1234#",
            "firstname": "Johnson",
            "lastname": "Dennis",
            "role": "admin",
        },
    )
    assert new_user
    sub_plan = await subscription_plan_repo.fetch(
        session=session, is_default=True, plan_idx=0
    )
    assert sub_plan is not None
    await user_subscription_repo.create(
        session=session,
        user_sub_data={
            "user_id": new_user.id,
            "subscription_plan_id": sub_plan.id,
            "is_current": True,
        },
    )

    yield new_user
