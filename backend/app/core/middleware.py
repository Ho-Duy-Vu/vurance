import logging
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("claimflow")


async def request_id_middleware(request: Request, call_next):
    rid = str(uuid.uuid4())[:8]
    request.state.request_id = rid
    logger.info("[%s] %s %s", rid, request.method, request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


async def csrf_middleware(request: Request, call_next):
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        if not request.url.path.startswith("/auth"):
            csrf_header = request.headers.get("X-CSRF-Token")
            csrf_cookie = request.cookies.get("csrf_token")
            if not csrf_header or csrf_header != csrf_cookie:
                return JSONResponse(
                    {"detail": "CSRF validation failed"},
                    status_code=403,
                )
    return await call_next(request)
