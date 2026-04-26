"""
AddsOn schhema
"""

import json
from typing import Annotated, List, Dict
from pydantic import BaseModel, model_validator, Field, ConfigDict, StringConstraints


class AddsOnBase(BaseModel):
    """
    AddsOnBase
    """

    id: str = Field(examples=["product-manager"])
    name: str = Field(examples=["Hire a Product Manager"])
    prices: List[Dict[str, str | int]] = Field(
        examples=[
            [
                {"amount": 300, "unit": "week"},
                {"amount": 1000, "unit": "month"},
            ]
        ]
    )

    model_config = ConfigDict(from_attributes=True)


# ++++++++++++++++++++++ NEW AddsOn +++++++++++++++++++++++++++


class AddAddsOningleSchema(BaseModel):
    """
    AddAddsOningleSchema
    """

    id: Annotated[str, StringConstraints(min_length=3, strip_whitespace=True)] = Field(
        examples=["product-manager"]
    )
    name: Annotated[str, StringConstraints(min_length=3, strip_whitespace=True)] = (
        Field(examples=["Hire a Product Manager"])
    )
    prices: List[Dict[str, str | int]] = Field(
        examples=[
            [
                {"amount": 300, "unit": "week"},
                {"amount": 1000, "unit": "month"},
            ]
        ]
    )

    @model_validator(mode="before")
    @classmethod
    def vaildate_fields(cls, values: dict) -> dict:
        """
        Validate all fields

        """
        if isinstance(values, bytes):
            values = json.loads(values)

        prices = values.get("prices")
        if not isinstance(prices, list):
            raise ValueError("prices must be an array/list")

        for price in prices:
            if not isinstance(price, dict):
                raise ValueError("prices must be an array with hashes/objects/dicts")
            amount = price.get("amount")
            if not isinstance(amount, int) or amount < 1:
                raise ValueError(
                    "prices must have an amount for each price and must not be zero(0)"
                )
            unit = price.get("unit")
            if not isinstance(unit, str) or unit.strip() == "":
                raise ValueError("prices must have a unit for each price")

        return values


class AddAddsOnRequestSchema(BaseModel):
    """
    AddAddsOnRequestSchema
    """

    adds_on: List[AddAddsOningleSchema]

    @model_validator(mode="before")
    @classmethod
    def vaildate_fields(cls, values: dict) -> dict:
        """
        Validate all fields

        """
        if isinstance(values, bytes):
            values = json.loads(values)
        adds_ons: list | None = values.get("adds_ons", None)

        if not adds_ons or not isinstance(adds_ons, list):
            raise ValueError("adds_ons must be provided as a list/array")

        if len(adds_ons) < 1 > 10:
            raise ValueError(
                "adds_ons must be greater than one(1) and less than ten(10)"
            )

        return values


class AddAddsOnResponseSchema(BaseModel):
    """
    AddAddsOnResponseSchema
    """

    message: str = Field(
        default="AddsOn created successfully",
        examples=["AddsOn created successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: List[AddsOnBase]


# +++++++++++++++++ FETCH +++++++++++++++++++++++++


class FetchAddsOnResponseSchema(BaseModel):
    """
    FetchAddsOnResponseSchema
    """

    message: str = Field(
        default="AddsOn retrieved successfully",
        examples=["AddsOn retrieved successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: List[AddsOnBase]


# ++++++++++++++++ Delete +++++++++++++++++++++++


class DeleteAddsOnRequestSchema(BaseModel):
    """
    DeleteAddsOnRequestSchema
    """

    adds_on_ids: List[str]

    @model_validator(mode="before")
    @classmethod
    def vaildate_fields(cls, values: dict) -> dict:
        """
        Validate all fields

        """
        if isinstance(values, bytes):
            values = json.loads(values)
        adds_on_ids: list | None = values.get("adds_on_ids", None)

        if not adds_on_ids or not isinstance(adds_on_ids, list):
            raise ValueError("adds_on_ids must be provided as a list/array")

        if len(adds_on_ids) < 1 > 10:
            raise ValueError(
                "adds_on_ids must be greater than one(1) and less than ten(10)"
            )

        return values


class DeleteAddsOnResponseSchema(BaseModel):
    """
    DeleteAddsOnResponseSchema
    """

    message: str = Field(
        default="AddsOn removed successfully",
        examples=["AddsOn removed successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: dict = {}
