import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from fastauth import FastAuth, FastAuthConfig
from fastauth.authentication.backend import AuthenticationBackend
from fastauth.authentication.strategy.jwt import JWTStrategy
from fastauth.authentication.transport.bearer import BearerTransport


@pytest_asyncio.fixture
async def client(user_manager) -> AsyncClient:
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
    app.include_router(auth.get_users_router(), prefix="/users", tags=["users"])

    @app.get("/protected")
    async def protected_route(user=Depends(auth.current_active_user)):
        return {"user_email": user.email}

    transport_asgi = ASGITransport(app=app)
    async with AsyncClient(transport=transport_asgi, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    # 1. Register new user
    register_res = await client.post(
        "/auth/register",
        json={"email": "routeruser@example.com", "password": "RouterPassword123!"},
    )
    assert register_res.status_code == 201
    data = register_res.json()
    assert data["email"] == "routeruser@example.com"
    assert "id" in data

    # 2. Login
    login_res = await client.post(
        "/auth/login",
        data={"username": "routeruser@example.com", "password": "RouterPassword123!"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]

    # 3. Access protected route without token (401)
    unauth_res = await client.get("/protected")
    assert unauth_res.status_code == 401

    # 4. Access protected route with Bearer token (200)
    auth_res = await client.get(
        "/protected", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert auth_res.status_code == 200
    assert auth_res.json()["user_email"] == "routeruser@example.com"

    # 5. Access /users/me
    me_res = await client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "routeruser@example.com"
