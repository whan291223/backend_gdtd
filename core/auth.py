import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

security = HTTPBearer()

async def verify_line_user(auth: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verifies the LINE ID token passed in the Authorization header.
    Returns the line_user_id if valid.
    """
    id_token = auth.credentials

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.line.me/oauth2/v2.1/verify",
                data={
                    "id_token": id_token,
                    "client_id": settings.LINE_CHANNEL_ID
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid LINE token"
                )

            data = response.json()
            # If data is a coroutine (can happen in some mock/async environments)
            if hasattr(data, "__await__"):
                data = await data

            line_user_id = data.get("sub")
            if not line_user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not contain user ID"
                )

            return line_user_id

        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not verify token with LINE"
            )
