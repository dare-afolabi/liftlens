import os

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str = Depends(api_key_header)) -> str:
    expected = os.getenv("LIFTLENS_API_KEY")
    # Require an API key to be configured and matched. If no key is set,
    # deny access (some tests expect 401 when the system is not
    # configured for API key auth).
    if expected is None or key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )
    return key
