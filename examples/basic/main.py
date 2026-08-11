import os
import sys
from typing import AsyncGenerator

# Add parent src directory to path if running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fastauth import FastAuth, FastAuthConfig, UserManager
from fastauth.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastauth.db.sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase


# 1. Define SQLAlchemy User Model
class User(SQLAlchemyBaseUserTable):
    __tablename__ = "users"


# 2. Database Setup
DATABASE_URL = "sqlite+aiosqlite:///./fastauth_example.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLAlchemyBaseUserTable.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


# 3. Custom UserManager with event hooks
class CustomUserManager(UserManager[User, str]):
    async def on_after_register(self, user: User) -> None:
        print(f"🎉 User registered: {user.email}")

    async def on_after_login(self, user: User) -> None:
        print(f"🔑 User logged in: {user.email}")


def get_user_manager(user_db=Depends(get_user_db)):
    yield CustomUserManager(user_db, secret="SUPER_SECRET_KEY_12345")


# 4. Auth Backend Setup
SECRET = "SUPER_SECRET_KEY_12345"
bearer_transport = BearerTransport(token_url="/auth/login")
jwt_strategy = JWTStrategy(secret=SECRET, lifetime_seconds=3600)
auth_backend = AuthenticationBackend(
    name="jwt-bearer",
    transport=bearer_transport,
    strategy=jwt_strategy,
)

# 5. FastAuth Setup
auth = FastAuth(
    get_user_manager=get_user_manager,
    backends=[auth_backend],
)

# 6. Initialize FastAPI App
app = FastAPI(
    title="FastAuth Demo Application",
    description="Working demonstration of FastAuth authentication framework.",
    version="0.1.0",
)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


# Attach FastAuth Routers
app.include_router(
    auth.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    auth.get_register_router(),
    prefix="/auth",
    tags=["Registration"],
)

app.include_router(
    auth.get_reset_password_router(),
    prefix="/auth",
    tags=["Password Reset"],
)

app.include_router(
    auth.get_verify_router(),
    prefix="/auth",
    tags=["Verification"],
)

app.include_router(
    auth.get_users_router(),
    prefix="/users",
    tags=["User Management"],
)


# Protected Endpoint
@app.get("/protected-route", tags=["Protected Demo"])
async def protected_route(user: User = Depends(auth.current_active_user)):
    return {
        "message": f"Hello {user.email}! You have accessed a protected endpoint.",
        "user_id": str(user.id),
        "is_superuser": user.is_superuser,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
