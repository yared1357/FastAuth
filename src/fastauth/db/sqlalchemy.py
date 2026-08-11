import contextlib
import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import Boolean, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from fastauth.db.base import BaseUserDatabase

ID = TypeVar("ID")
UserTable = TypeVar("UserTable")


class SQLAlchemyBaseUserTable(DeclarativeBase):
    """Abstract SQLAlchemy base model for FastAuth users."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class SQLAlchemyUserDatabase(Generic[UserTable, ID], BaseUserDatabase[UserTable, ID]):
    """Async SQLAlchemy adapter for FastAuth user management."""

    def __init__(self, session: AsyncSession, user_table: type[UserTable]) -> None:
        self.session = session
        self.user_table = user_table

    async def get(self, id: ID) -> UserTable | None:
        parsed_id: Any = id
        if isinstance(id, str):
            with contextlib.suppress(ValueError):
                parsed_id = uuid.UUID(id)
        statement = select(self.user_table).where(
            getattr(self.user_table, "id") == parsed_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> UserTable | None:
        statement = select(self.user_table).where(
            getattr(self.user_table, "email") == email.lower()
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, create_dict: dict[str, Any]) -> UserTable:
        if "email" in create_dict:
            create_dict["email"] = create_dict["email"].lower()
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: UserTable, update_dict: dict[str, Any]) -> UserTable:
        if "email" in update_dict:
            update_dict["email"] = update_dict["email"].lower()
        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: UserTable) -> None:
        await self.session.delete(user)
        await self.session.commit()
