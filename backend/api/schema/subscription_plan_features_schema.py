"""
Subscription Plan Features Schema
"""

from pydantic import BaseModel, Field, ConfigDict


class SubscriptionPlanFeatureBase(BaseModel):
    """
    SubscriptionPlanBase
    """

    name: str = Field(examples=["Score"])
    value: int | None = Field(default=None, examples=[5])

    model_config = ConfigDict(from_attributes=True)
