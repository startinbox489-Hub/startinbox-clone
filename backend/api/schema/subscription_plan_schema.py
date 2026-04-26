"""
Subscription Plan Schema
"""

from typing import List
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, model_validator
from sqlalchemy import RowMapping

from api.schema.subscription_plan_features_schema import SubscriptionPlanFeatureBase


class SubscriptionPlanBase(BaseModel):
    """
    SubscriptionPlanBase
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    name: str = Field(examples=["Free"])
    price: Decimal = Field(examples=["5"])
    description: str = Field(examples=["some description"])
    idx: int = Field(examples=[0])
    credits: int = Field(examples=[5])
    type: str = Field(examples=["oneoff"])
    flutterwave_plan_id: int | None = Field(default=None, examples=[123])

    is_popular: bool = Field(examples=[True])
    features: List[SubscriptionPlanFeatureBase]

    model_config = ConfigDict(from_attributes=True)


class SubscriptionPlansResponseSchema(BaseModel):
    """
    SubscriptionPlansResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Subscription Plans retrieved succesfully",
        examples=["Subscription Plans retrieved succesfully"],
    )
    data: List[SubscriptionPlanBase]


class ActiveUserSubscriptionPlan(BaseModel):
    """
    ActiveUserSubscriptionPlan
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    is_current: bool = Field(examples=[True])
    subscription_plan_id: str = Field(examples=["silver"])
    is_expired: bool = Field(examples=[False])
    flutterwave_subscription_id: int = Field(examples=[229923])
    credit_used: int = Field(examples=[0])
    remaining_credits: int = Field(examples=[5])
    type: str = Field(examples=["reoccurring"])
    name: str = Field(examples=["Silver Plan"])
    idx: int = Field(examples=[4])

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, value: RowMapping) -> dict:
        """
        Validate all
        """
        new_value = {}
        for k, v in value.items():
            if k == "_type":
                new_value["type"] = v
            else:
                new_value[k] = v

        return new_value


class ActiveUserSubscriptionPlansResponseSchema(BaseModel):
    """
    ActiveUserSubscriptionPlansResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Active Subscription Plans retrieved succesfully",
        examples=["Active Subscription Plans retrieved succesfully"],
    )
    data: List[ActiveUserSubscriptionPlan]
