import contextlib
from collections.abc import Callable
from typing import Any, Type, TypeVar

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from fastauth.authentication.backend import AuthenticationBackend
from fastauth.exceptions import (
    FastAuthException,
    InvalidCredentialsException,
    UserNotFoundException,
    get_http_exception,
)
from fastauth.manager import UserManager
from fastauth.schemas import BaseUserCreate, BaseUserUpdate, UserRead

UserType = TypeVar("UserType")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class RequestVerifyTokenRequest(BaseModel):
    email: EmailStr


class VerifyRequest(BaseModel):
    token: str


def get_auth_router(
    backend: AuthenticationBackend[Any],
    get_user_manager: Callable[..., UserManager[Any, Any]],
    authenticator: Any = None,
) -> APIRouter:
    """Generate router for login and logout endpoints."""
    router = APIRouter()

    @router.post("/login")
    async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> Response:
        user = await user_manager.authenticate(
            email=credentials.username, password=credentials.password
        )
        if user is None:
            raise get_http_exception(InvalidCredentialsException())

        response = await backend.login(backend.strategy, user)
        await user_manager.on_after_login(user)
        return response

    @router.post("/logout")
    async def logout(
        request: Request,
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
        user: Any = Depends(authenticator.current_user_optional)
        if authenticator
        else None,
    ) -> Response:
        token = await backend.transport.scheme(request)  # type: ignore[operator]
        if token and user:
            return await backend.logout(backend.strategy, user, token)
        return await backend.transport.get_logout_response()

    return router


def get_register_router(
    get_user_manager: Callable[..., UserManager[Any, Any]],
    user_schema: Type[UserRead] = UserRead,
    user_create_schema: Type[BaseUserCreate] = BaseUserCreate,
) -> APIRouter:
    """Generate router for user registration endpoint."""
    router = APIRouter()

    @router.post(
        "/register",
        response_model=user_schema,
        status_code=status.HTTP_201_CREATED,
    )
    async def register(
        user_create: BaseUserCreate,
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> Any:
        try:
            user = await user_manager.create(user_create)
            return user
        except FastAuthException as e:
            raise get_http_exception(e) from e

    return router


def get_reset_password_router(
    get_user_manager: Callable[..., UserManager[Any, Any]],
) -> APIRouter:
    """Generate router for forgot-password and reset-password endpoints."""
    router = APIRouter()

    @router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
    async def forgot_password(
        data: ForgotPasswordRequest,
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> dict[str, str]:
        with contextlib.suppress(UserNotFoundException):
            await user_manager.forgot_password(data.email)
        return {"message": "Password reset email sent if user exists."}

    @router.post("/reset-password", status_code=status.HTTP_200_OK)
    async def reset_password(
        data: ResetPasswordRequest,
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> dict[str, str]:
        try:
            await user_manager.reset_password(data.token, data.password)
            return {"message": "Password has been successfully reset."}
        except FastAuthException as e:
            raise get_http_exception(e) from e

    return router


def get_verify_router(
    get_user_manager: Callable[..., UserManager[Any, Any]],
) -> APIRouter:
    """Generate router for email verification endpoints."""
    router = APIRouter()

    @router.post("/request-verify-token", status_code=status.HTTP_202_ACCEPTED)
    async def request_verify_token(
        data: RequestVerifyTokenRequest,
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> dict[str, str]:
        with contextlib.suppress(FastAuthException):
            user = await user_manager.get_by_email(data.email)
            await user_manager.request_verify_token(user)
        return {"message": "Verification token sent if email exists."}

    @router.post("/verify", status_code=status.HTTP_200_OK)
    async def verify(
        data: VerifyRequest,
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> dict[str, str]:
        try:
            await user_manager.verify(data.token)
            return {"message": "Email successfully verified."}
        except FastAuthException as e:
            raise get_http_exception(e) from e

    return router


def get_users_router(
    get_user_manager: Callable[..., UserManager[Any, Any]],
    authenticator: Any,
    user_schema: Type[UserRead] = UserRead,
    user_update_schema: Type[BaseUserUpdate] = BaseUserUpdate,
) -> APIRouter:
    """Generate router for user profile management endpoints (/me, /{id})."""
    router = APIRouter()

    @router.get("/me", response_model=user_schema)
    async def get_me(
        user: Any = Depends(authenticator.current_active_user),
    ) -> Any:
        return user

    @router.patch("/me", response_model=user_schema)
    async def update_me(
        user_update: BaseUserUpdate,
        user: Any = Depends(authenticator.current_active_user),
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> Any:
        try:
            return await user_manager.update(user, user_update)
        except FastAuthException as e:
            raise get_http_exception(e) from e

    @router.get("/{id}", response_model=user_schema)
    async def get_user_by_id(
        id: str,
        user: Any = Depends(authenticator.current_superuser),
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> Any:
        try:
            return await user_manager.get(id)
        except FastAuthException as e:
            raise get_http_exception(e) from e

    @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_user(
        id: str,
        user: Any = Depends(authenticator.current_superuser),
        user_manager: UserManager[Any, Any] = Depends(get_user_manager),
    ) -> None:
        try:
            target_user = await user_manager.get(id)
            await user_manager.delete(target_user)
        except FastAuthException as e:
            raise get_http_exception(e) from e

    return router
