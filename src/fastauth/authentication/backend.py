from typing import Generic, TypeVar

from fastapi import Response

from fastauth.authentication.strategy.base import Strategy
from fastauth.authentication.transport.base import Transport

UserType = TypeVar("UserType")


class AuthenticationBackend(Generic[UserType]):
    """Authentication backend combining a strategy (token algorithm) and a transport (HTTP medium)."""

    def __init__(
        self,
        name: str,
        transport: Transport,
        strategy: Strategy[UserType],
    ) -> None:
        self.name = name
        self.transport = transport
        self.strategy = strategy

    async def login(self, strategy: Strategy[UserType], user: UserType) -> Response:
        token = await strategy.write_token(user)
        return await self.transport.get_login_response(token)

    async def logout(
        self, strategy: Strategy[UserType], user: UserType, token: str
    ) -> Response:
        await strategy.destroy_token(token, user)
        return await self.transport.get_logout_response()
