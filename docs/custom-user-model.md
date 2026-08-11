# Extending the User Model

FastAuth makes it easy to add custom fields to your user model (such as `full_name`, `avatar_url`, `role`, or `bio`).

## 1. Extend the SQLAlchemy Model

Inherit from `SQLAlchemyBaseUserTable` and add your custom columns:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from fastauth.db.sqlalchemy import SQLAlchemyBaseUserTable

class User(SQLAlchemyBaseUserTable):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="member")
```

## 2. Extend Pydantic Schemas

Extend `UserRead`, `UserCreate`, and `UserUpdate` to include your new fields:

```python
from typing import Optional
from fastauth.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
import uuid

class UserReadCustom(BaseUser[uuid.UUID]):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "member"

class UserCreateCustom(BaseUserCreate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserUpdateCustom(BaseUserUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
```

## 3. Pass Custom Schemas to Routers

Pass your custom schemas when attaching the routers:

```python
app.include_router(
    auth.get_register_router(
        user_schema=UserReadCustom,
        user_create_schema=UserCreateCustom,
    ),
    prefix="/auth",
)

app.include_router(
    auth.get_users_router(
        user_schema=UserReadCustom,
        user_update_schema=UserUpdateCustom,
    ),
    prefix="/users",
)
```
