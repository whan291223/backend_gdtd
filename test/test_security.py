import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from core.auth import verify_line_user
from fastapi.security import HTTPAuthorizationCredentials

@pytest.mark.asyncio
async def test_verify_line_user_success():
    auth = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"sub": "user_123"})
        mock_post.return_value = mock_response

        line_user_id = await verify_line_user(auth)
        assert line_user_id == "user_123"

@pytest.mark.asyncio
async def test_verify_line_user_invalid_token():
    auth = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with pytest.raises(HTTPException) as excinfo:
            await verify_line_user(auth)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Invalid LINE token"

@pytest.mark.asyncio
async def test_verify_line_user_no_sub():
    auth = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token_no_sub")

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={}) # No "sub" field
        mock_post.return_value = mock_response

        with pytest.raises(HTTPException) as excinfo:
            await verify_line_user(auth)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Token does not contain user ID"
