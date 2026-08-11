import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from fastauth import FastAuth, FastAuthConfig
from fastauth.authentication.backend import AuthenticationBackend
from fastauth.authentication.strategy.jwt import JWTStrategy
from fastauth.authentication.transport.bearer import BearerTransport
from fastauth.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserInactiveException,
    UserNotFoundException,
    UserNotVerifiedException,
    get_http_exception,
)


@pytest.mark.asyncio
async def test_exception_mapping():
    assert get_http_exception(UserAlreadyExistsException()).status_code == 400
    assert get_http_exception(UserNotFoundException()).status_code == 404
    assert get_http_exception(InvalidCredentialsException()).status_code == 400
    assert get_http_exception(UserInactiveException()).status_code == 400
    assert get_http_exception(UserNotVerifiedException()).status_code == 400


@pytest_asyncio.fixture
async def full_client(user_manager, test_user, test_superuser) -> AsyncClient:
    app = FastAPI()
    config = FastAuthConfig(secret="test-secret")
    strategy = JWTStrategy(secret=config.secret, lifetime_seconds=3600)
    transport = BearerTransport(token_url="/auth/login")
    backend = AuthenticationBackend(name="jwt", strategy=strategy, transport=transport)

    def get_manager_dep():
        return user_manager

    auth = FastAuth(get_user_manager=get_manager_dep, backends=[backend], config=config)

    app.include_router(auth.get_auth_router(backend), prefix="/auth", tags=["auth"])
    app.include_router(auth.get_register_router(), prefix="/auth", tags=["auth"])
    app.include_router(auth.get_verify_router(), prefix="/auth", tags=["auth"])
    app.include_router(auth.get_reset_password_router(), prefix="/auth", tags=["auth"])
    app.include_router(auth.get_users_router(), prefix="/users", tags=["users"])

    @app.get("/optional")
    async def optional_route(user=Depends(auth.current_user_optional)):
        return {"user": user.email if user else None}

    @app.get("/admin-only")
    async def admin_route(user=Depends(auth.current_superuser)):
        return {"admin": user.email}

    transport_asgi = ASGITransport(app=app)
    async with AsyncClient(transport=transport_asgi, base_url="http://test") as ac:
        yield ac, auth, backend, test_user, test_superuser, strategy


@pytest.mark.asyncio
async def test_all_routers_and_dependencies(full_client):
    client, _auth, _backend, test_user, test_superuser, _strategy = full_client

    # 1. Login normal user
    login_res = await client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "TestPassword123!"},
    )
    assert login_res.status_code == 200
    user_token = login_res.json()["access_token"]

    # 2. Login superuser
    admin_login_res = await client.post(
        "/auth/login",
        data={"username": test_superuser.email, "password": "AdminPassword123!"},
    )
    assert admin_login_res.status_code == 200
    admin_token = admin_login_res.json()["access_token"]

    # 3. Optional user route (unauthenticated)
    opt_unauth = await client.get("/optional")
    assert opt_unauth.status_code == 200
    assert opt_unauth.json()["user"] is None

    # 4. Optional user route (authenticated)
    opt_auth = await client.get(
        "/optional", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert opt_auth.status_code == 200
    assert opt_auth.json()["user"] == test_user.email

    # 5. Superuser route with normal user (403 forbidden)
    forbidden_res = await client.get(
        "/admin-only", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert forbidden_res.status_code == 403

    # 6. Superuser route with admin user (200 OK)
    admin_res = await client.get(
        "/admin-only", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_res.status_code == 200
    assert admin_res.json()["admin"] == test_superuser.email

    # 7. Logout
    logout_res = await client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert logout_res.status_code == 204

    # 8. Password Reset Router endpoints
    forgot_res = await client.post(
        "/auth/forgot-password", json={"email": test_user.email}
    )
    assert forgot_res.status_code == 202

    # 9. Verify Router endpoints
    verify_req_res = await client.post(
        "/auth/request-verify-token", json={"email": test_user.email}
    )
    assert verify_req_res.status_code == 202

    # 10. Update user profile (PATCH /users/me)
    patch_res = await client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"is_active": True},
    )
    assert patch_res.status_code == 200

    # 11. Admin fetch user by ID (GET /users/{id})
    get_by_id_res = await client.get(
        f"/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert get_by_id_res.status_code == 200
