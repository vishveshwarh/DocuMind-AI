# app/api/deps.py

from fastapi import Header, HTTPException, Request
from app.config import settings


def verify_demo_key(x_demo_key: str | None = Header(default=None)):
    if not settings.DEMO_ACCESS_KEY:
        return True

    if x_demo_key != settings.DEMO_ACCESS_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing demo access key"
        )

    return True


def get_client_ip(request: Request):
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.client.host if request.client else "unknown"