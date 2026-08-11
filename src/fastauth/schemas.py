import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr

ID = TypeVar("ID")


class BaseUser(BaseModel, Generic[ID]):
    """Base user schema containing core authentication fields."""

    id: ID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class BaseUserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False


class BaseUserUpdate(BaseModel):
    """Schema for user updates."""

    password: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


class UserRead(BaseUser[uuid.UUID]):
    """Default UserRead schema with UUID primary key."""

    pass


class UserCreate(BaseUserCreate):
    """Default UserCreate schema."""

    pass


class UserUpdate(BaseUserUpdate):
    """Default UserUpdate schema."""

    pass


class BearerResponse(BaseModel):
    """Response returned upon successful login with BearerTransport."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
