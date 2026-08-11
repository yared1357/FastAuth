from typing import Literal, Optional

from pydantic import BaseModel, Field


class FastAuthConfig(BaseModel):
    """Configuration settings for FastAuth."""

    secret: str = Field(
        ...,
        description="Secret key used for signing JWTs and secure tokens.",
    )
    algorithm: str = Field(
        default="HS256",
        description="Algorithm used for JWT generation and verification.",
    )
    access_token_lifetime_seconds: int = Field(
        default=3600,  # 1 hour
        description="Lifetime of access tokens in seconds.",
    )
    refresh_token_lifetime_seconds: int = Field(
        default=86400 * 7,  # 7 days
        description="Lifetime of refresh tokens in seconds.",
    )
    verification_token_lifetime_seconds: int = Field(
        default=86400,  # 24 hours
        description="Lifetime of email verification tokens in seconds.",
    )
    reset_password_token_lifetime_seconds: int = Field(
        default=3600,  # 1 hour
        description="Lifetime of password reset tokens in seconds.",
    )
    cookie_name: str = Field(
        default="fastauth_token",
        description="Cookie name when using CookieTransport.",
    )
    cookie_path: str = Field(
        default="/",
        description="Cookie path setting.",
    )
    cookie_domain: Optional[str] = Field(
        default=None,
        description="Cookie domain setting.",
    )
    cookie_secure: bool = Field(
        default=True,
        description="Whether cookies require HTTPS.",
    )
    cookie_httponly: bool = Field(
        default=True,
        description="Whether cookies are HttpOnly.",
    )
    cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax",
        description="Cookie SameSite attribute ('lax', 'strict', 'none').",
    )
