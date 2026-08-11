from typing import Any

from fastapi import HTTPException, status


class FastAuthException(Exception):
    """Base exception for FastAuth."""

    def __init__(self, message: str = "An error occurred during authentication."):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsException(FastAuthException):
    """Raised when trying to register a user with an email that already exists."""

    def __init__(self, email: str | None = None):
        msg = (
            f"User with email '{email}' already exists."
            if email
            else "User already exists."
        )
        super().__init__(msg)


class UserNotFoundException(FastAuthException):
    """Raised when a user is not found."""

    def __init__(self, identifier: Any | None = None):
        msg = f"User '{identifier}' not found." if identifier else "User not found."
        super().__init__(msg)


class InvalidCredentialsException(FastAuthException):
    """Raised when login credentials (email or password) are invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid credentials.")


class InvalidTokenException(FastAuthException):
    """Raised when an authentication or verification token is invalid or expired."""

    def __init__(self, reason: str = "Invalid or expired token.") -> None:
        super().__init__(reason)


class UserInactiveException(FastAuthException):
    """Raised when an inactive user tries to perform an action requiring active status."""

    def __init__(self) -> None:
        super().__init__("User account is inactive.")


class UserNotVerifiedException(FastAuthException):
    """Raised when an unverified user tries to perform an action requiring verification."""

    def __init__(self) -> None:
        super().__init__("User account is not verified.")


# FastAPI HTTP Exception mapping helpers


def get_http_exception(exc: FastAuthException) -> HTTPException:
    """Map a FastAuthException to a FastAPI HTTPException."""
    if isinstance(exc, UserAlreadyExistsException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="REGISTER_USER_ALREADY_EXISTS",
        )
    if isinstance(exc, UserNotFoundException):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_NOT_FOUND",
        )
    if isinstance(exc, InvalidCredentialsException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LOGIN_BAD_CREDENTIALS",
        )
    if isinstance(exc, InvalidTokenException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INVALID_TOKEN",
        )
    if isinstance(exc, UserInactiveException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_INACTIVE",
        )
    if isinstance(exc, UserNotVerifiedException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_NOT_VERIFIED",
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=exc.message,
    )
