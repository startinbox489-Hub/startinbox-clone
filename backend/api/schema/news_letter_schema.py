"""
news_letter Schema
"""

from typing import Annotated, Optional
from datetime import datetime
import json
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    model_validator,
    StringConstraints,
)


class NewsLetterBase(BaseModel):
    """
    NewsLetterBase
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    name: str | None = Field(default=None, examples=["Free"])
    email: str = Field(examples=["johnson@gmail.com"])
    subscribed_at: datetime = Field(examples=[datetime.now()])

    model_config = ConfigDict(from_attributes=True)


# ++++++++++++++++++ Subscribe +++++++++++++++++++++++++++++
class NewsLetterRequestSchema(BaseModel):
    """
    NewsLetterRequestSchema
    """

    email: EmailStr = Field(examples=["johnson@gmail.com"])
    name: str | None = Field(default=None, examples=["Free"])

    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, values: dict) -> dict:
        """
        Validates all fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        email: str | None = values.get("email") or None

        if email and isinstance(email, str):
            values["email"] = email.lower()
        return values


class NewsLetterResponseSchema(BaseModel):
    """
    NewsLetterResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Subscribed to news letter succesfully",
        examples=["Subscribed to news letter succesfully"],
    )
    data: NewsLetterBase


# ++++++++++++++++++ Unubscribe +++++++++++++++++++++++++++++
class UnSubNewsLetterRequestSchema(BaseModel):
    """
    UnSubNewsLetterRequestSchema
    """

    newsletter_hash: Annotated[
        str, StringConstraints(min_length=21, max_length=60, strip_whitespace=True)
    ] = Field(examples=["AUIUiuh87yHGT5RTu&yUJ"])
    reason: Optional[
        Annotated[
            str, StringConstraints(min_length=3, max_length=255, strip_whitespace=True)
        ]
    ] = Field(default=None, examples=["Too many emails"])

    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, values: dict) -> dict:
        """
        Validates all fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        newsletter_hash: str | None = values.get("newsletter_hash") or None

        if (
            not newsletter_hash
            or not isinstance(newsletter_hash, str)
            or newsletter_hash.strip() == ""
        ):
            raise ValueError("newsletter_hash must be a string")
        return values


class UnSubNewsLetterResponseSchema(BaseModel):
    """
    NewsLetterResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Unsubscribed from news letter succesfully",
        examples=["Unsubscribed from news letter succesfully"],
    )
    data: dict = {}
