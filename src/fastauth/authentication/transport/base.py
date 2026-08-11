from typing import Protocol, runtime_checkable

from fastapi import Response
from fastapi.security.base import SecurityBase


@runtime_checkable
class Transport(Protocol):
    """Protocol specifying transport mechanism for tokens (e.g. Bearer Header, HttpOnly Cookie)."""

    scheme: SecurityBase

    async def get_login_response(self, token: str) -> Response:
        """Construct response upon successful login."""
        ...

    async def get_logout_response(self) -> Response:
        """Construct response upon logout."""
        ...
