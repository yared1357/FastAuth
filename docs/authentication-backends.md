# Authentication Backends in FastAuth

FastAuth decouples **strategies** (how tokens/sessions are represented and validated) from **transports** (how credentials are passed in HTTP requests).

## Combining Strategy & Transport

An `AuthenticationBackend` couples 1 Strategy with 1 Transport:

```python
from fastauth.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)

# Option A: Mobile / API Clients (Bearer Header)
bearer_transport = BearerTransport(token_url="/auth/login")
jwt_strategy = JWTStrategy(secret="MY_SECRET", lifetime_seconds=3600)

bearer_backend = AuthenticationBackend(
    name="jwt-bearer",
    transport=bearer_transport,
    strategy=jwt_strategy,
)

# Option B: Web Frontends / Single Page Apps (HttpOnly Cookies)
cookie_transport = CookieTransport(
    cookie_name="fastauth_token",
    cookie_secure=True,
    cookie_httponly=True,
    cookie_samesite="lax",
)

cookie_backend = AuthenticationBackend(
    name="jwt-cookie",
    transport=cookie_transport,
    strategy=jwt_strategy,
)
```

## Using Multiple Backends

FastAuth allows registering multiple backends simultaneously:

```python
auth = FastAuth(
    get_user_manager=get_user_manager,
    backends=[bearer_backend, cookie_backend],
)
```

FastAuth will attempt to authenticate incoming requests against each backend in order until one succeeds.
