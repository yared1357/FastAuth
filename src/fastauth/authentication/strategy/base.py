from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

UserType = TypeVar("UserType")


@runtime_checkable
class Strategy(Protocol, Generic[UserType]):
    """Protocol specifying the authentication strategy interface (e.g. JWT, Database Session)."""

    async def read_token(self, token: str | None, user_manager: Any) -> UserType | None:
        """Validate token and retrieve user from user manager."""
        ...

    async def write_token(self, user: UserType) -> str:
        """Generate an authentication token for a user."""
        ...

    async def destroy_token(self, token: str, user: UserType) -> None:
        """Invalidate/destroy a token on logout."""
        ...
