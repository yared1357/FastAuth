from datetime import datetime, timedelta, timezone
from typing import Generic, TypeVar

from jose import JWTError, jwt

from fastauth.db.base import BaseUserDatabase
from fastauth.exceptions import (
    InvalidTokenException,
    UserAlreadyExistsException,
    UserInactiveException,
    UserNotFoundException,
)
from fastauth.schemas import BaseUserCreate, BaseUserUpdate
from fastauth.security.password import BcryptPasswordHasher, PasswordHasher

UserType = TypeVar("UserType")
ID = TypeVar("ID")


class UserManager(Generic[UserType, ID]):
    """Central manager handling user business logic, lifecycle events, and DB persistence."""

    def __init__(
        self,
        user_db: BaseUserDatabase[UserType, ID],
        password_hasher: PasswordHasher | None = None,
        secret: str = "secret",
        verification_token_lifetime_seconds: int = 86400,
        reset_password_token_lifetime_seconds: int = 3600,
    ) -> None:
        self.user_db = user_db
        self.password_hasher = password_hasher or BcryptPasswordHasher()
        self.secret = secret
        self.verification_token_lifetime_seconds = verification_token_lifetime_seconds
        self.reset_password_token_lifetime_seconds = (
            reset_password_token_lifetime_seconds
        )

    async def get(self, id: ID) -> UserType:
        user = await self.user_db.get(id)
        if user is None:
            raise UserNotFoundException(id)
        return user

    async def get_by_email(self, email: str) -> UserType:
        user = await self.user_db.get_by_email(email)
        if user is None:
            raise UserNotFoundException(email)
        return user

    async def create(self, user_create: BaseUserCreate, safe: bool = False) -> UserType:
        existing = await self.user_db.get_by_email(user_create.email)
        if existing:
            raise UserAlreadyExistsException(user_create.email)

        create_dict = user_create.model_dump()
        password = create_dict.pop("password")
        create_dict["hashed_password"] = self.password_hasher.hash(password)

        created_user = await self.user_db.create(create_dict)
        await self.on_after_register(created_user)
        return created_user

    async def authenticate(self, email: str, password: str) -> UserType | None:
        try:
            user = await self.get_by_email(email)
        except UserNotFoundException:
            return None

        if not self.password_hasher.verify(
            password, str(getattr(user, "hashed_password", ""))
        ):
            return None

        if not getattr(user, "is_active", True):
            raise UserInactiveException()

        return user

    async def update(self, user: UserType, user_update: BaseUserUpdate) -> UserType:
        update_dict = user_update.model_dump(exclude_unset=True)
        if update_dict.get("password"):
            password = update_dict.pop("password")
            update_dict["hashed_password"] = self.password_hasher.hash(password)

        if "email" in update_dict and update_dict["email"] != getattr(
            user, "email", ""
        ):
            existing = await self.user_db.get_by_email(update_dict["email"])
            if existing:
                raise UserAlreadyExistsException(update_dict["email"])

        updated_user = await self.user_db.update(user, update_dict)
        return updated_user

    async def delete(self, user: UserType) -> None:
        await self.user_db.delete(user)

    # Verification token flow
    async def request_verify_token(self, user: UserType) -> str:
        if getattr(user, "is_verified", False):
            raise InvalidTokenException("User is already verified.")

        user_id = str(getattr(user, "id", ""))
        user_email = str(getattr(user, "email", ""))
        now = datetime.now(timezone.utc)
        exp = now + timedelta(seconds=self.verification_token_lifetime_seconds)
        token_data = {
            "sub": user_id,
            "email": user_email,
            "aud": "fastauth:verify",
            "exp": int(exp.timestamp()),
        }
        token = str(jwt.encode(token_data, self.secret, algorithm="HS256"))
        await self.on_after_request_verify(user, token)
        return token

    async def verify(self, token: str) -> UserType:
        try:
            data = jwt.decode(
                token, self.secret, algorithms=["HS256"], audience="fastauth:verify"
            )
            user_id = data.get("sub")
        except JWTError as err:
            raise InvalidTokenException(
                "Invalid or expired verification token."
            ) from err

        user = await self.get(user_id)
        if getattr(user, "is_verified", False):
            return user

        updated_user = await self.user_db.update(user, {"is_verified": True})
        await self.on_after_verify(updated_user)
        return updated_user

    # Password reset flow
    async def forgot_password(self, email: str) -> str:
        user = await self.get_by_email(email)
        user_id = str(getattr(user, "id", ""))
        now = datetime.now(timezone.utc)
        exp = now + timedelta(seconds=self.reset_password_token_lifetime_seconds)
        token_data = {
            "sub": user_id,
            "aud": "fastauth:reset-password",
            "exp": int(exp.timestamp()),
        }
        token = str(jwt.encode(token_data, self.secret, algorithm="HS256"))
        await self.on_after_forgot_password(user, token)
        return token

    async def reset_password(self, token: str, new_password: str) -> UserType:
        try:
            data = jwt.decode(
                token,
                self.secret,
                algorithms=["HS256"],
                audience="fastauth:reset-password",
            )
            user_id = data.get("sub")
        except JWTError as err:
            raise InvalidTokenException(
                "Invalid or expired password reset token."
            ) from err

        user = await self.get(user_id)
        hashed_password = self.password_hasher.hash(new_password)
        updated_user = await self.user_db.update(
            user, {"hashed_password": hashed_password}
        )
        await self.on_after_reset_password(updated_user)
        return updated_user

    # Event Hooks (Override these in custom subclasses for emails/logging)
    async def on_after_register(self, user: UserType) -> None:
        pass

    async def on_after_login(self, user: UserType) -> None:
        pass

    async def on_after_request_verify(self, user: UserType, token: str) -> None:
        pass

    async def on_after_verify(self, user: UserType) -> None:
        pass

    async def on_after_forgot_password(self, user: UserType, token: str) -> None:
        pass

    async def on_after_reset_password(self, user: UserType) -> None:
        pass
