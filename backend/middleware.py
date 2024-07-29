"""middleware.py"""

from constants import PASSWORD, USERNAME
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware

security = HTTPBasic()


class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        credentials: HTTPBasicCredentials = await security(request)

        if credentials.username != USERNAME or credentials.password != PASSWORD:
            raise HTTPException(status_code=401, detail="Unauthorized")

        response = await call_next(request)
        return response
