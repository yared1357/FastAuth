# Getting Started with FastAuth

Welcome to **FastAuth**, the modern, pluggable authentication framework built for FastAPI applications.

## Key Features

- 🔐 **JWT & Cookie Support** — Flexible token strategies and transports
- 🗃️ **Async Database Adapters** — Pre-built support for SQLAlchemy async
- 👤 **Full User Lifecycle** — Registration, Login, Email Verification, Password Reset
- 🪝 **Event Hooks** — Easily trigger emails, webhooks, or audit logging
- 🔒 **Type-Safe & Modern** — Pydantic v2 support, PEP 484 type hints

---

## Installation

FastAuth supports Python 3.10+. Install via `pip`:

```bash
# Basic installation
pip install fastauth

# With SQLAlchemy support (Recommended)
pip install fastauth[sqlalchemy]

# With Argon2 password hashing support
pip install fastauth[argon2]

# Full bundle
pip install fastauth[all]
```

---

## Minimal Example

Here is a fully functional FastAPI app with registration, authentication, and protected routes:

```python
from typing import AsyncGenerator
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from fastauth import FastAuth, FastAuthConfig, UserManager
from fastauth.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastauth.db.sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

# 1. Define Database Model
class User(SQLAlchemyBaseUserTable):
    __tablename__ = "users"

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield SQLAlchemyUserDatabase(session, User)

def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db, secret="YOUR-SECRET-KEY")

# 2. Setup Auth Backend
strategy = JWTStrategy(secret="YOUR-SECRET-KEY", lifetime_seconds=3600)
transport = BearerTransport(token_url="/auth/login")
backend = AuthenticationBackend(name="jwt", strategy=strategy, transport=transport)

# 3. Initialize FastAuth
auth = FastAuth(get_user_manager=get_user_manager, backends=[backend])

app = FastAPI()

# 4. Attach Routers
app.include_router(auth.get_auth_router(backend), prefix="/auth", tags=["auth"])
app.include_router(auth.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(auth.get_users_router(), prefix="/users", tags=["users"])

# 5. Protect Endpoints
@app.get("/protected")
async def protected_route(user=Depends(auth.current_active_user)):
    return {"message": f"Welcome back, {user.email}!"}
```
