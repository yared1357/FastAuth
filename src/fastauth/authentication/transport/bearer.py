from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from fastauth.authentication.transport.base import Transport
from fastauth.schemas import BearerResponse


class BearerTransport(Transport):
    """Bearer token transport using Authorization header and OAuth2PasswordBearer security scheme."""

    def __init__(self, token_url: str = "/auth/login") -> None:
        self.scheme = OAuth2PasswordBearer(tokenUrl=token_url, auto_error=False)

    async def get_login_response(self, token: str) -> Response:
        bearer_response = BearerResponse(access_token=token, token_type="bearer")
        return JSONResponse(content=bearer_response.model_dump())

    async def get_logout_response(self) -> Response:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
