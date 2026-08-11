import pytest

from fastauth.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from fastauth.schemas import BaseUserCreate, BaseUserUpdate


@pytest.mark.asyncio
async def test_user_manager_crud(user_manager):
    # Create
    user_create = BaseUserCreate(
        email="newuser@example.com",
        password="Password123!",
    )
    user = await user_manager.create(user_create)
    assert user.email == "newuser@example.com"
    assert user.is_active is True

    # Read
    fetched = await user_manager.get(user.id)
    assert fetched.id == user.id

    fetched_by_email = await user_manager.get_by_email("newuser@example.com")
    assert fetched_by_email.id == user.id

    # Authenticate
    auth_user = await user_manager.authenticate("newuser@example.com", "Password123!")
    assert auth_user is not None
    assert auth_user.id == user.id

    wrong_auth = await user_manager.authenticate("newuser@example.com", "WrongPass")
    assert wrong_auth is None

    # Update
    updated = await user_manager.update(user, BaseUserUpdate(is_verified=True))
    assert updated.is_verified is True

    # Delete
    await user_manager.delete(user)
    with pytest.raises(UserNotFoundException):
        await user_manager.get(user.id)


@pytest.mark.asyncio
async def test_duplicate_user_creation_raises(user_manager, test_user):
    with pytest.raises(UserAlreadyExistsException):
        await user_manager.create(
            BaseUserCreate(email=test_user.email, password="password")
        )


@pytest.mark.asyncio
async def test_verify_flow(user_manager):
    unverified_user = await user_manager.create(
        BaseUserCreate(
            email="unverified@example.com", password="password", is_verified=False
        )
    )
    assert unverified_user.is_verified is False

    token = await user_manager.request_verify_token(unverified_user)
    assert isinstance(token, str)

    verified_user = await user_manager.verify(token)
    assert verified_user.is_verified is True


@pytest.mark.asyncio
async def test_password_reset_flow(user_manager, test_user):
    token = await user_manager.forgot_password(test_user.email)
    assert isinstance(token, str)

    reset_user = await user_manager.reset_password(token, "NewPassword123!")
    assert reset_user is not None

    # Authenticate with new password
    auth = await user_manager.authenticate(test_user.email, "NewPassword123!")
    assert auth is not None
