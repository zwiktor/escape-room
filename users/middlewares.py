from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi_users.authentication.strategy import RedisStrategy
from datetime import datetime


class RefreshTokenMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        redis_strategy: RedisStrategy,
        user_manager,
        refresh_interval: int = 1800,
    ):
        super().__init__(app)
        self.redis_strategy = redis_strategy
        self.user_manager = user_manager
        self.refresh_interval = refresh_interval

    async def dispatch(self, request: Request, call_next):
        if "authorization" in request.headers:
            token = request.headers.get("authorization").split(" ")[1]
            user_id = await self.redis_strategy.read_token(token, self.user_manager)
            if user_id:
                last_refresh_key = f"last_refresh:{token}"
                last_refresh = await self.redis_strategy.redis.get(last_refresh_key)
                now = datetime.utcnow()

                if (
                    not last_refresh
                    or (now - datetime.fromisoformat(last_refresh)).total_seconds()
                    > self.refresh_interval
                ):
                    await self.redis_strategy.extend_token_lifetime(token)
                    await self.redis_strategy.redis.set(
                        last_refresh_key, now.isoformat()
                    )

        response = await call_next(request)
        return response
