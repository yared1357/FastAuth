import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fastauth.db.sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastauth.manager import UserManager
from fastauth.schemas import BaseUserCreate

SECRET = "super-secret-key-for-testing-12345"


# SQLAlchemy Model for testing
class User(SQLAlchemyBaseUserTable):
    __tablename__ = "users"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLAlchemyBaseUserTable.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def user_db(get_db_session: AsyncSession) -> SQLAlchemyUserDatabase[User, str]:
    return SQLAlchemyUserDatabase(session=get_db_session, user_table=User)


@pytest_asyncio.fixture
async def user_manager(
    user_db: SQLAlchemyUserDatabase[User, str],
) -> UserManager[User, str]:
    return UserManager(user_db=user_db, secret=SECRET)


@pytest_asyncio.fixture
async def test_user(user_manager: UserManager[User, str]) -> User:
    user_create = BaseUserCreate(
        email="testuser@example.com",
        password="TestPassword123!",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    return await user_manager.create(user_create)


@pytest_asyncio.fixture
async def test_superuser(user_manager: UserManager[User, str]) -> User:
    user_create = BaseUserCreate(
        email="admin@example.com",
        password="AdminPassword123!",
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    return await user_manager.create(user_create)
