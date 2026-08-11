from collections.abc import Callable, Sequence
from typing import Any, Generic, Optional, TypeVar

from fastapi import Depends, HTTPException, Request, status

from fastauth.authentication.backend import AuthenticationBackend
from fastauth.config import FastAuthConfig
from fastauth.exceptions import (
    UserInactiveException,
    UserNotVerifiedException,
    get_http_exception,
)
from fastauth.manager import UserManager
from fastauth.router import (
    get_auth_router,
    get_register_router,
    get_reset_password_router,
    get_users_router,
    get_verify_router,
)
from fastauth.schemas import BaseUserCreate, BaseUserUpdate, UserRead

UserType = TypeVar("UserType")


class FastAuth(Generic[UserType]):
    """Main FastAuth class providing dependency injection and pre-built routers for FastAPI."""

    def __init__(
        self,
        get_user_manager: Callable[..., UserManager[Any, Any]],
        backends: Sequence[AuthenticationBackend[Any]],
        config: Optional[FastAuthConfig] = None,
    ) -> None:
        self.get_user_manager = get_user_manager
        self.backends = backends
        self.config = config

    # Dependency Injection Helpers

    async def current_user(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
    ) -> Callable[..., Any]:
        """Dependency generator for extracting current authenticated user."""

        async def current_user_dependency(
            request: Request,
            user_manager: UserManager[Any, Any] = Depends(self.get_user_manager),
        ) -> Optional[UserType]:
            user: Optional[UserType] = None

            for backend in self.backends:
                token = await backend.transport.scheme(request)  # type: ignore[operator]
                if token:
                    user = await backend.strategy.read_token(token, user_manager)
                    if user:
                        break

            if user is None:
                if optional:
                    return None
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="UNAUTHORIZED",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if active and not getattr(user, "is_active", True):
                raise get_http_exception(UserInactiveException())

            if verified and not getattr(user, "is_verified", False):
                raise get_http_exception(UserNotVerifiedException())

            if superuser and not getattr(user, "is_superuser", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="FORBIDDEN",
                )

            return user

        return current_user_dependency

    # Pre-configured Dependency Properties

    @property
    def current_user_optional(self) -> Callable[..., UserType | None]:
        """Dependency for optional authenticated user (returns None if unauthenticated)."""
        return self._build_dependency(optional=True)

    @property
    def current_user_required(self) -> Callable[..., UserType]:
        """Dependency for authenticated user."""
        return self._build_dependency(optional=False)

    @property
    def current_active_user(self) -> Callable[..., UserType]:
        """Dependency for active authenticated user."""
        return self._build_dependency(active=True)

    @property
    def current_verified_user(self) -> Callable[..., UserType]:
        """Dependency for verified active authenticated user."""
        return self._build_dependency(active=True, verified=True)

    @property
    def current_superuser(self) -> Callable[..., UserType]:
        """Dependency for superuser."""
        return self._build_dependency(active=True, superuser=True)

    def _build_dependency(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
    ) -> Callable[..., Any]:
        async def dep(
            request: Request,
            user_manager: UserManager[Any, Any] = Depends(self.get_user_manager),
        ) -> Any:
            user: Optional[UserType] = None
            for backend in self.backends:
                token = await backend.transport.scheme(request)  # type: ignore[operator]
                if token:
                    user = await backend.strategy.read_token(token, user_manager)
                    if user:
                        break

            if user is None:
                if optional:
                    return None
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="UNAUTHORIZED",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if active and not getattr(user, "is_active", True):
                raise get_http_exception(UserInactiveException())

            if verified and not getattr(user, "is_verified", False):
                raise get_http_exception(UserNotVerifiedException())

            if superuser and not getattr(user, "is_superuser", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="FORBIDDEN",
                )

            return user

        return dep

    # Router Generators

    def get_auth_router(self, backend: AuthenticationBackend[Any]) -> Any:
        """Get login/logout APIRouter for specified backend."""
        return get_auth_router(
            backend=backend,
            get_user_manager=self.get_user_manager,
            authenticator=self,
        )

    def get_register_router(
        self,
        user_schema: type[UserRead] = UserRead,
        user_create_schema: type[BaseUserCreate] = BaseUserCreate,
    ) -> Any:
        """Get user registration APIRouter."""
        return get_register_router(
            get_user_manager=self.get_user_manager,
            user_schema=user_schema,
            user_create_schema=user_create_schema,
        )

    def get_reset_password_router(self) -> Any:
        """Get forgot-password and reset-password APIRouter."""
        return get_reset_password_router(get_user_manager=self.get_user_manager)

    def get_verify_router(self) -> Any:
        """Get email verification APIRouter."""
        return get_verify_router(get_user_manager=self.get_user_manager)

    def get_users_router(
        self,
        user_schema: type[UserRead] = UserRead,
        user_update_schema: type[BaseUserUpdate] = BaseUserUpdate,
    ) -> Any:
        """Get user profile management APIRouter."""
        return get_users_router(
            get_user_manager=self.get_user_manager,
            authenticator=self,
            user_schema=user_schema,
            user_update_schema=user_update_schema,
        )
