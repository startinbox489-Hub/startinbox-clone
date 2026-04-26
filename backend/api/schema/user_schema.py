"""
User Schema
"""

from datetime import datetime, timedelta
from typing import Annotated
import json
import phonenumbers

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    model_validator,
    StringConstraints,
)


class UserBase(BaseModel):
    """
    UserBase
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    firstname: str | None = Field(default=None, examples=["Johnson"])
    lastname: str | None = Field(default=None, examples=["Dennis"])
    email: str = Field(examples=["johnson@gmail.com"])
    phone_number: str | None = Field(default=None, examples=["+2347064712188"])
    created_at: datetime = Field(examples=[datetime.now()])

    model_config = ConfigDict(from_attributes=True)


# +++++++++++++++++++++++++++++++++ SIGNUP ++++++++++++++++++++++++++++++
class SignupRequestSchema(BaseModel):
    """
    SignupRequestSchema
    """

    email: EmailStr = Field(examples=["johnson@gmail.com"])
    phone_number: Annotated[str | None, StringConstraints(strip_whitespace=True)] = (
        Field(default=None, examples=["+2347064712188"])
    )
    idempotency_key: Annotated[
        str | None,
        StringConstraints(strip_whitespace=True, min_length=8, max_length=255),
    ] = Field(default=None, examples=["21212121-2121-2121-2121-212121212121"])
    password: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=8, max_length=24)
    ] = Field(examples=["Johnson1234#"])
    confirm_password: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=8, max_length=24)
    ] = Field(examples=["Johnson1234#"])
    agreed_to_terms: bool = Field(examples=[True])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        password: str | None = values.get("password", None)
        confirm_password: str | None = values.get("confirm_password", None)
        phone_number: str | None = values.get("phone_number", None)

        if phone_number:
            try:
                parsed = phonenumbers.parse(phone_number, None)
                if not phonenumbers.is_valid_number(parsed):
                    raise ValueError("Invalid phone number")
            except phonenumbers.NumberParseException as exc:
                raise ValueError(
                    "Phone number must be in valid international format (E.164)"
                ) from exc

        if password != confirm_password:
            raise ValueError("password and confirm_password must match")
        if not isinstance(password, str) or not confirm_password:
            raise ValueError("password and confirm_password must be provided")

        has_digit = False
        has_lowercase = False
        has_uppercase = False
        has_special_char = False
        special_char = "!@#$%^&*()_+=-;:?/\\,<.>`~'\""

        for char in password:
            if char.islower():
                has_lowercase = True
            if char.isupper():
                has_uppercase = True
            if char.isdigit():
                has_digit = True
            if char in special_char:
                has_special_char = True

        if has_digit is False:
            raise ValueError("password must contain at least one digit")
        if has_lowercase is False:
            raise ValueError("password must contain at least one lowercase letter")
        if has_uppercase is False:
            raise ValueError("password must contain at least one uppercase letter")
        if has_special_char is False:
            raise ValueError("password must contain at least one special character")
        return values


class SignupResponseSchema(BaseModel):
    """
    SignupResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="User created succesfully",
        examples=["User created succesfully"],
    )
    data: UserBase


# +++++++++++++++++++++++++++++++++ SIGNIN ++++++++++++++++++++++++++++++


class SigninRequestSchema(BaseModel):
    """
    SigninRequestSchema
    """

    email: EmailStr = Field(examples=["johnson@gmail.com"])
    password: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=8, max_length=24)
    ] = Field(examples=["Johnson1234#"])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        password: str | None = values.get("password", None)

        if not isinstance(password, str) or not password:
            raise ValueError("password must be provided")

        has_digit = False
        has_lowercase = False
        has_uppercase = False
        has_special_char = False
        special_char = "!@#$%^&*()_+=-;:?/\\,<.>`~'\""

        for char in password:
            if char.islower():
                has_lowercase = True
            if char.isupper():
                has_uppercase = True
            if char.isdigit():
                has_digit = True
            if char in special_char:
                has_special_char = True

        if has_digit is False:
            raise ValueError("password must contain at least one digit")
        if has_lowercase is False:
            raise ValueError("password must contain at least one lowercase letter")
        if has_uppercase is False:
            raise ValueError("password must contain at least one uppercase letter")
        if has_special_char is False:
            raise ValueError("password must contain at least one special character")
        return values


class TokenBase(BaseModel):
    """
    Tokens
    """

    access_token: str = Field(examples=["e23d223d24df24f.f3f4d23.r32er23r2..."])
    token_type: str = Field(default="bearer", examples=["bearer"])
    expires_in: int = Field(
        examples=[int((datetime.now() + timedelta(days=30)).timestamp())]
    )


class SigninDataSchema(BaseModel):
    """
    SigninDataSchema
    """

    user: UserBase
    token: TokenBase


class SigninResponseSchema(BaseModel):
    """
    SigninResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Signin success",
        examples=["Signin success"],
    )
    data: SigninDataSchema


# ++++++++++++++++++++++ Signout +++++++++++++++++++++++
class SignoutResponseSchema(BaseModel):
    """
    SignoutResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Signout success",
        examples=["Signout success"],
    )
    data: dict = {}


# ++++++++++++++++++++++ Google Signup +++++++++++++++++++++++
class GoogleSignUpRequestSchema(BaseModel):
    """
    GoogleSignUpRequestSchema
    """

    id_token: Annotated[
        str, StringConstraints(min_length=200, strip_whitespace=True)
    ] = Field(examples=["e23d223d24df24f.f3f4d23.r32er23r2..."])
    agreed_to_terms: bool | None = Field(default=None, examples=[True])


# ++++++++++++++++++++++++++ USER ME +++++++++++++++++++++++
class UserMeResponseSchema(SignupResponseSchema):
    """
    UserMeResponseSchema
    """

    message: str = Field(
        default="User data retrieved succesfully",
        examples=["User data retrieved succesfully"],
    )
