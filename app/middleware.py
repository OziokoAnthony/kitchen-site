import time
from fastapi import Request


class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()

        async def send_with_time(message):
            if message["type"] == "http.response.start":
                elapsed = time.time() - start
                headers = list(message.get("headers", []))
                headers.append(
                    (b"x-process-time", str(round(elapsed, 4)).encode())
                )
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_time)
