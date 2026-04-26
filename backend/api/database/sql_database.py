"""
SQL Database Module
"""

import os
import asyncio
from typing import AsyncIterator
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy.ext.asyncio import (
    async_scoped_session,  # For creating scoped sessions in async environments
    async_sessionmaker,  # For creating session factories
    AsyncEngine,  # Represents an async engine (connection to DB)
    create_async_engine,  # Preferred way to create async engine
    AsyncSession,  # Represents a session for DB transactions in async context
    AsyncAttrs,  # Base class for asynchronous ORM mappings
)
from sqlalchemy.orm import (
    DeclarativeBase,  # Base class for ORM models
    Mapped,
    mapped_column,
    declared_attr,
    declarative_mixin,
    scoped_session,
    sessionmaker,
    Session,
)
from sqlalchemy import (
    MetaData,  # To define metadata and naming conventions
    pool,
    Table,
    DateTime,
    String,
    func,
    create_engine,
    Engine,
    StaticPool,
)
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import uuid7

from api.core.config import settings

DATABASE_URL: str = settings.db_url_async
ISTEST = os.getenv("TEST", "FALSE") == "TRUE"

if ISTEST:
    DATABASE_URL = settings.db_url_test


naming_convention = {
    "ix": "ix_%(column_0_label)s",  # index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # unique
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # constraints
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # foreign key
    "pk": "pk_%(table_name)s",  # primary key
}


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base
    """

    if os.getenv("TEST", None) or "sqlite" in DATABASE_URL:
        metadata = MetaData(naming_convention=naming_convention)
    else:
        metadata = MetaData(naming_convention=naming_convention)


class SqlDatabase:
    """
    Sql database class
    """

    async_engine: AsyncEngine
    async_session_factory: async_sessionmaker[AsyncSession]
    async_scopped_session_obj: async_scoped_session[AsyncSession]

    # SYNCHRONOUS
    sync_engine: Engine
    sync_scopped_session_obj: scoped_session[Session]

    def __init__(self) -> None:
        """
        COnstructor
        """
        # ASYNC
        self.__set_async_engine()

        self.__set_async_factory()

        self.__set_async_scopped_session()

        # SYNC

        self.__set_sync_engine()

        self.__set_sync_factory()

        self.__set_sync_scopped_session()

    # ++++++++++++ ASYNC ++++++++++++++++++++

    def __set_async_engine(self) -> None:
        """
        Set async engine
        """
        _kwargs = {}
        if not ISTEST:
            _kwargs["poolclass"] = pool.AsyncAdaptedQueuePool
            _kwargs["pool_size"] = 5
            _kwargs["max_overflow"] = 10
            _kwargs["pool_timeout"] = 30
            _kwargs["pool_recycle"] = 18000
        else:
            _kwargs["connect_args"] = {"check_same_thread": False}
            _kwargs["poolclass"] = StaticPool
        self.async_engine: AsyncEngine = create_async_engine(
            url=DATABASE_URL,
            echo=False,
            future=True,
            **_kwargs,
        )

    def __set_async_factory(self) -> None:
        """
        Sets async factory.
        Create a session factory, ensuring sessions are async
        """

        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False,
        )

    def __set_async_scopped_session(self) -> None:
        """
        Create and set scoped session tied to async loop
        """
        self.async_scopped_session_obj = async_scoped_session(
            session_factory=self.async_session_factory, scopefunc=asyncio.current_task
        )

    # ++++++++++++++++ SYNC +++++++++++++++++++++

    def __set_sync_engine(self) -> None:
        """
        Set sync engine
        """
        # database_url = settings.celery_result_backend.split("+")[1]
        _kwargs = {}
        if not ISTEST:
            _kwargs["pool_size"] = 5
            _kwargs["max_overflow"] = 10
            _kwargs["pool_timeout"] = 30
            _kwargs["pool_recycle"] = 18000

        self.sync_engine = create_engine(
            url=DATABASE_URL,
            echo=False,
            future=True,
            **_kwargs,
        )

    def __set_sync_factory(self) -> None:
        """
        Sets async factory.
        Create a session factory, ensuring sessions are sync
        """

        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def __set_sync_scopped_session(self) -> None:
        """
        Create and set scoped session tied to sync loop
        """
        self.sync_scopped_session_obj = scoped_session(
            session_factory=self.sync_session_factory
        )

    async def create_tables(self) -> None:
        """
        Creates tables if not already created
        """
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_specific_table(self, table: Table) -> None:
        """
        Creates a specific tables if not already created
        """
        async with self.async_engine.begin() as conn:
            await conn.run_sync(table.create)

    async def drop_tables(self) -> None:
        """
        Drops tables if not already dropped
        """
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def drop_specific_table(self, table: Table) -> None:
        """
        Drops a specific table if not already dropped
        """
        async with self.async_engine.begin() as conn:
            await conn.run_sync(table.drop)

    async def get_db_with_tx(self) -> AsyncIterator[AsyncSession]:
        """
        Dependency to provide a database session for each request.
        Handles session lifecycle including commit and rollback.
        Dependency comes with a running transaction
        """
        async with self.async_scopped_session_obj() as session:
            try:
                yield session
            except SQLAlchemyError:
                await session.rollback()
                raise
            finally:
                await self.async_scopped_session_obj.remove()
                await session.close()

    async def get_db_no_tx(self) -> AsyncIterator[AsyncSession]:
        """
        Dependency to provide a database session for each request.
        Handles session lifecycle including commit and rollback.
        Dependency comes with no running transaction
        """
        session = self.async_scopped_session_obj()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await self.async_scopped_session_obj.remove()
            await session.close()

    @contextmanager
    def get_sync_session(self):
        """
        Dependency to provide a database session for each request.
        Handles session lifecycle including commit and rollback.
        """
        session = self.sync_scopped_session_obj()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            self.sync_scopped_session_obj.remove()
            session.close()


@declarative_mixin
class ModelMixin:
    """
    Mixin Class for ORM Models
    """

    id: Mapped[str] = mapped_column(
        String(60),
        primary_key=True,
        index=True,
        default=lambda: str(uuid7()).replace("-", ""),
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @declared_attr  # type: ignore
    @classmethod
    def __tablename__(cls):
        """
        Table names
        """
        return f"{cls.__name__.lower()}s"


sql_database = SqlDatabase()
