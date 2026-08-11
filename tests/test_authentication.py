import pytest

from fastauth.authentication.strategy.jwt import JWTStrategy
from fastauth.authentication.transport.bearer import BearerTransport
from fastauth.authentication.transport.cookie import CookieTransport


@pytest.mark.asyncio
async def test_jwt_strategy_write_and_read(user_manager, test_user):
    strategy = JWTStrategy(secret="testsecret", lifetime_seconds=3600)
    token = await strategy.write_token(test_user)
    assert isinstance(token, str)

    read_user = await strategy.read_token(token, user_manager)
    assert read_user is not None
    assert read_user.id == test_user.id
    assert read_user.email == test_user.email


@pytest.mark.asyncio
async def test_bearer_transport_responses():
    transport = BearerTransport(token_url="/auth/login")
    login_res = await transport.get_login_response("mock-token-123")
    assert login_res.status_code == 200

    logout_res = await transport.get_logout_response()
    assert logout_res.status_code == 204


@pytest.mark.asyncio
async def test_cookie_transport_responses():
    transport = CookieTransport(cookie_name="test_cookie")
    login_res = await transport.get_login_response("mock-token-123")
    assert login_res.status_code == 200
    assert "set-cookie" in login_res.headers

    logout_res = await transport.get_logout_response()
    assert logout_res.status_code == 204
    assert "set-cookie" in logout_res.headers
