from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

ID = TypeVar("ID", contravariant=True)
UserType = TypeVar("UserType")


@runtime_checkable
class BaseUserDatabase(Protocol, Generic[UserType, ID]):
    """Protocol specifying database adapter interface for user management."""

    async def get(self, id: ID) -> UserType | None:
        """Fetch a user by primary key ID."""
        ...

    async def get_by_email(self, email: str) -> UserType | None:
        """Fetch a user by email address."""
        ...

    async def create(self, create_dict: dict[str, Any]) -> UserType:
        """Create a new user from dictionary data."""
        ...

    async def update(self, user: UserType, update_dict: dict[str, Any]) -> UserType:
        """Update an existing user with dictionary data."""
        ...

    async def delete(self, user: UserType) -> None:
        """Delete a user."""
        ...
