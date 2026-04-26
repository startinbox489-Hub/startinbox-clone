"""
Responses
"""

from typing import Dict, Any

from fastapi import Request
from starlette.datastructures import State
from pydantic import BaseModel, ConfigDict, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession


class Claims(BaseModel):
    """
    Claims
    """

    user_id: str
    exp: int
    iat: int
    iss: str
    aud: str
    ipaddress: str
    location: str | None = None
    token_type: str
    user_agent: str
    jti: str
    role: str
    email: str


class CustomState(State):
    """
    Custom state
    """

    claims: Claims | None = None
    current_user: str = "Guest"
    session: AsyncSession | None = None  # type: ignore


class CustomRequest(Request):
    """
    Custom Request
    """

    state: CustomState  # type: ignore


# ++++++++++++++++ Google ID Token +++++++++++++++++
class GoogleIdToken(BaseModel):
    """
    GoogleIdToken
    """

    iss: str
    aud: str
    email: str
    sub: str
    email_verified: bool
    name: str | None = None
    picture: HttpUrl | None = None
    family_name: str | None = None
    given_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


responses: Dict[int | str, Dict[str, Any]] = {
    500: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {
                    "status_code": 500,
                    "message": "Internal Server error occured",
                    "data": {},
                }
            }
        },
    },
    405: {
        "description": "Method not allowed",
        "content": {
            "application/json": {
                "example": {
                    "status_code": 405,
                    "message": "Method Not Allowed",
                    "data": {},
                },
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {"status_code": 400, "message": "Bad Request", "data": {}},
            }
        },
    },
    404: {
        "description": "Not found",
        "content": {
            "application/json": {
                "example": {"status_code": 404, "message": "Not found", "data": {}},
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {"status_code": 401, "message": "Unauthorized", "data": {}},
            }
        },
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {"status_code": 403, "message": "Forbidden", "data": {}},
            }
        },
    },
}
