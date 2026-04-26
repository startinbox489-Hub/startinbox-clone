"""
TestDatabaseSetup
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.sql_database import DATABASE_URL, sql_database


class TestDatabaseSetup:
    """Test database setup and configuration."""

    def test_test_environment_detection(self):
        """Test that test environment is properly detected."""
        assert "test" in DATABASE_URL.lower() or "sqlite" in DATABASE_URL.lower()

    def test_sql_database_initialization(self):
        """Test that SqlDatabase initializes correctly."""
        db = sql_database

        assert db.async_engine is not None
        assert db.async_session_factory is not None
        assert db.sync_engine is not None
        assert db.sync_session_factory is not None

    @pytest.mark.asyncio
    async def test_database_connection(
        self, test_setup: None, async_db_session: AsyncSession
    ):
        """Test that database connection works."""
        result = await async_db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
