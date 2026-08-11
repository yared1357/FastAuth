from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional, TypeVar, cast

from jose import JWTError, jwt

from fastauth.authentication.strategy.base import Strategy

UserType = TypeVar("UserType")


class JWTStrategy(Generic[UserType], Strategy[UserType]):
    """Authentication strategy using JSON Web Tokens (JWT)."""

    def __init__(
        self,
        secret: str,
        lifetime_seconds: int = 3600,
        token_audience: str = "fastauth:auth",
        algorithm: str = "HS256",
    ) -> None:
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds
        self.token_audience = token_audience
        self.algorithm = algorithm

    async def read_token(self, token: str | None, user_manager: Any) -> UserType | None:
        if not token:
            return None

        try:
            data = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                audience=self.token_audience,
            )
            user_id = data.get("sub")
            if user_id is None:
                return None
        except JWTError:
            return None

        try:
            user = await user_manager.get(user_id)
            return cast(Optional[UserType], user)
        except Exception:
            return None

    async def write_token(self, user: UserType) -> str:
        user_id = str(getattr(user, "id"))
        now = datetime.now(timezone.utc)
        expire = now + timedelta(seconds=self.lifetime_seconds)

        payload: Dict[str, Any] = {
            "sub": user_id,
            "aud": self.token_audience,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }

        return str(jwt.encode(payload, self.secret, algorithm=self.algorithm))

    async def destroy_token(self, token: str, user: UserType) -> None:
        # JWTs are stateless; token blacklisting can be added via Redis extension
        pass
