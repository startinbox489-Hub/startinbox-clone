"""
Exception handler module
"""

import time

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.utils.task_logger import create_logger
from api.utils.get_client_ip import get_client_ip_render

logger = create_logger("Route middleware logger")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log user IP, user agent, and route details on each request.
    Also checks for a valid user-agent.
    """

    async def dispatch(self, request: Request, call_next):
        user_ip = get_client_ip_render(request=request)
        user_agent = request.headers.get("user-agent", "Unknown")
        if user_ip in [None, "", ",", " "]:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=jsonable_encoder(
                    {
                        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                        "message": "Hey!!! Careful Now!!!",
                        "data": {},
                    }
                ),
            )

        # Check for missing user-agent
        if not request.url.path.startswith("/api/v1/payments/webhook/flutterwave") and (
            user_agent == "Unknown" or not user_agent
        ):
            logger.warning(
                "Request blocked due to missing user-agent",
                extra={"user_ip": user_ip},
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    {
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Bad Request: Invalid",
                        "data": {},
                    }
                ),
            )

        if (
            not request.url.path.startswith("/api/v1")
            and request.url.path != "/"
            and not request.url.path.startswith("/socket.io")
            and not request.url.path.startswith("/docs")
            and not request.url.path.startswith("/favicon")
            and not request.url.path.startswith("/openapi")
        ):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=jsonable_encoder(
                    {
                        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                        "message": "Not Allowed",
                        "data": {},
                    }
                ),
            )

        # Log initial request info, masking sensitive information
        start_time = time.time()
        try:
            payload = await request.json()
            sensitive_field = [
                "password",
                "confirm_password",
                "secret_token",
                "refresh_token",
                "access_token",
                "code",
                "token",
                "confirm_new_password",
                "new_password",
                "id_token",
            ]
            for key in payload.keys():
                if key in sensitive_field:
                    payload[key] = "***********"
                if key == "device_info" and "device_id" in payload[key]:
                    payload[key]["device_id"] = "**************"

        except Exception:
            payload = {}
        logger.info(
            "Request received",
            extra={
                "user_ip": user_ip,
                "user_agent": user_agent,
                "path": request.url.path,
                "method": request.method,
                "payload": payload,
                "current_user": (
                    request.state.current_user
                    if hasattr(request.state, "current_user")
                    else "Guest"
                ),
                "query_params": request.query_params.multi_items(),
                "path_params": request.path_params,
            },
        )

        # Retrieve authenticated user if available
        if not hasattr(request, "current_user"):
            request.current_user = "Guest"  # type: ignore

        # Process the request
        response = await call_next(request)

        # Log response status and time taken
        process_time = time.time() - start_time
        user_info = (
            request.state.current_user
            if hasattr(request.state, "current_user")
            else "Guest"
        )

        logger.info(
            "Request completed",
            extra={
                "current_user": user_info,
                "user_ip": user_ip,
                "user_agent": user_agent,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "process_time": f"{process_time:.2f}s",
            },
        )

        return response


class UserAgentMiddleware(BaseHTTPMiddleware):
    """
    Class for UserAgent middleware
    """

    async def dispatch(self, request: Request, call_next):
        """
        Checks for user agent.
        """
        user_agent = request.headers.get("user-agent", "Unknown")
        if user_agent == "Unknown":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Bad Request!",
                    "data": {},
                },
            )

        response = await call_next(request)
        return response
