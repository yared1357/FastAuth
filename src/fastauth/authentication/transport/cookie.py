from typing import Literal, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security.base import SecurityBase

from fastauth.authentication.transport.base import Transport


class CookieSecurityScheme(SecurityBase):
    """Custom security scheme to extract token from Cookie."""

    def __init__(self, cookie_name: str) -> None:
        self.cookie_name = cookie_name
        self.scheme_name = "Cookie"

    async def __call__(self, request: Request) -> Optional[str]:
        return request.cookies.get(self.cookie_name)


class CookieTransport(Transport):
    """HttpOnly cookie transport for secure web applications."""

    def __init__(
        self,
        cookie_name: str = "fastauth_token",
        cookie_max_age: int = 3600,
        cookie_path: str = "/",
        cookie_domain: Optional[str] = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: Literal["lax", "strict", "none"] = "lax",
    ) -> None:
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.scheme = CookieSecurityScheme(cookie_name=cookie_name)

    async def get_login_response(self, token: str) -> Response:
        response = JSONResponse(content={"message": "Logged in successfully"})
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response

    async def get_logout_response(self) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            key=self.cookie_name,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response
