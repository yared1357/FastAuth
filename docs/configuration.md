# FastAuth Configuration Guide

FastAuth provides a flexible settings model via `FastAuthConfig`.

## Usage

```python
from fastauth.config import FastAuthConfig

config = FastAuthConfig(
    secret="super-secret-key-change-in-production",
    algorithm="HS256",
    access_token_lifetime_seconds=3600,       # 1 hour
    refresh_token_lifetime_seconds=604800,    # 7 days
    cookie_secure=True,                         # HTTPS only
)
```

## Options Reference

| Parameter | Type | Default | Description |
|---|---|---|---|
| `secret` | `str` | *Required* | Secret key for signing JWTs and verification tokens. |
| `algorithm` | `str` | `"HS256"` | JWT signature algorithm (`HS256`, `HS512`, `RS256`). |
| `access_token_lifetime_seconds` | `int` | `3600` | Lifetime of access tokens in seconds. |
| `refresh_token_lifetime_seconds` | `int` | `604800` | Lifetime of refresh tokens in seconds. |
| `verification_token_lifetime_seconds` | `int` | `86400` | Lifetime of email verification tokens in seconds. |
| `reset_password_token_lifetime_seconds` | `int` | `3600` | Lifetime of password reset tokens in seconds. |
| `cookie_name` | `str` | `"fastauth_token"` | Name of cookie used by `CookieTransport`. |
| `cookie_path` | `str` | `"/"` | Path restriction for cookie. |
| `cookie_domain` | `Optional[str]` | `None` | Allowed domain for cookie. |
| `cookie_secure` | `bool` | `True` | Requires HTTPS connection for cookie. |
| `cookie_httponly` | `bool` | `True` | Prevents JavaScript access to cookie (XSS protection). |
| `cookie_samesite` | `str` | `"lax"` | CSRF protection setting (`lax`, `strict`, `none`). |
