from datetime import datetime, timezone
from fastapi import HTTPException

from app.config import settings


class RateLimitService:
    def __init__(self):
        # In-memory usage tracker.
        # For v1 demo this is fine.
        # Later, move this to Redis/DB for production.
        self.usage = {}

    def _today_key(self, client_ip: str) -> str:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"{client_ip}:{today}"

    def _get_record(self, client_ip: str) -> dict:
        key = self._today_key(client_ip)

        if key not in self.usage:
            self.usage[key] = {
                "requests": 0,
                "uploads": 0,
                "tokens": 0,
            }

        return self.usage[key]

    def ensure_token_budget_available(self, client_ip: str, estimated_tokens: int):
        """
        Pre-check token budget BEFORE calling Groq.
        This does not add tokens. It only blocks if the request may exceed the limit.
        """
        record = self._get_record(client_ip)
        estimated_tokens = max(0, int(estimated_tokens or 0))

        if record["tokens"] + estimated_tokens > settings.DAILY_TOKEN_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Daily token limit reached. Please try again tomorrow.",
            )

    def check_chat_limit(self, client_ip: str):
        record = self._get_record(client_ip)

        if record["requests"] >= settings.DAILY_REQUEST_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Daily chat limit reached. Please try again tomorrow.",
            )

        record["requests"] += 1

    def check_upload_limit(self, client_ip: str):
        record = self._get_record(client_ip)

        if record["uploads"] >= settings.DAILY_UPLOAD_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Daily upload limit reached. Please try again tomorrow.",
            )

        record["uploads"] += 1

    def check_token_limit(self, client_ip: str, estimated_tokens: int):
        """
        Final token check AFTER answer is generated.
        This adds tokens to daily usage.
        """
        record = self._get_record(client_ip)
        estimated_tokens = max(0, int(estimated_tokens or 0))

        if record["tokens"] + estimated_tokens > settings.DAILY_TOKEN_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Daily token limit reached. Please try again tomorrow.",
            )

        record["tokens"] += estimated_tokens

    def get_usage(self, client_ip: str):
        record = self._get_record(client_ip)

        daily_token_limit = max(1, settings.DAILY_TOKEN_LIMIT)

        return {
            "requests_used": record["requests"],
            "uploads_used": record["uploads"],
            "tokens_used": record["tokens"],
            "daily_request_limit": settings.DAILY_REQUEST_LIMIT,
            "daily_upload_limit": settings.DAILY_UPLOAD_LIMIT,
            "daily_token_limit": settings.DAILY_TOKEN_LIMIT,
            "token_usage_percent": round(
                (record["tokens"] / daily_token_limit) * 100,
                2,
            ),
        }

    def reset_usage_for_ip(self, client_ip: str):
        """
        Optional helper for local testing.
        """
        key = self._today_key(client_ip)
        if key in self.usage:
            del self.usage[key]


rate_limit_service = RateLimitService()