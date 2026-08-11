from typing import Protocol, runtime_checkable

import bcrypt


@runtime_checkable
class PasswordHasher(Protocol):
    """Protocol defining the interface for password hashing backends."""

    def hash(self, password: str) -> str:
        """Hash a plain text password."""
        ...

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hash."""
        ...


class BcryptPasswordHasher:
    """Password hasher using native Bcrypt package."""

    def hash(self, password: str) -> str:
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        try:
            pwd_bytes = plain_password.encode("utf-8")
            hash_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False


class Argon2PasswordHasher:
    """Password hasher using Argon2 via PassLib (requires argon2-cffi)."""

    def __init__(self) -> None:
        from passlib.context import CryptContext

        self.context = CryptContext(schemes=["argon2"], deprecated="auto")

    def hash(self, password: str) -> str:
        return str(self.context.hash(password))

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return bool(self.context.verify(plain_password, hashed_password))
