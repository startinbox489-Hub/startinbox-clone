"""
Testimonal schhema
"""

from typing import List, Annotated, Optional
import json
from pydantic import BaseModel, Field, ConfigDict, model_validator, StringConstraints
from bleach import clean


class TestimonialBase(BaseModel):
    """
    TestimonalBase
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    testimonial: str | None = Field(examples=["some testimonial"])
    firstname: str | None = Field(examples=["Johnson"])
    lastname: str | None = Field(examples=["Johnson"])
    image_url: str | None = Field(examples=["https://image.com"])
    rating: int = Field(examples=[5])

    model_config = ConfigDict(from_attributes=True)


# +++++++++++++++++ FETCH +++++++++++++++++++++++++


class FetchTestimonialResponseSchema(BaseModel):
    """
    FetchTestimonalResponseSchema
    """

    message: str = Field(
        default="Testimonials retrieved successfully",
        examples=["Testimionals retrieved successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: List[TestimonialBase]


# +++++++++++++++++ CREATE +++++++++++++++++++++++++
class AddTestimonialRequestSchema(BaseModel):
    """
    AddTestimonialRequestSchema
    """

    idea_id: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=20, max_length=60)
    ] = Field(examples=["11111111-1111-1111-1111-111111111111"])

    testimonial: Optional[
        Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=3, max_length=1000)
        ]
    ] = Field(default=None, examples=["some testimonial"])
    rating: int = Field(examples=[5], gt=0, lt=6)

    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, values: dict) -> dict:
        """
        validate_all_fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        testimonial = values.get("testimonial")
        if testimonial and testimonial.strip() != "":
            values["testimonial"] = clean(testimonial)

        return values


class AddTestimonialResponseSchema(BaseModel):
    """
    AddTestimonialResponseSchema
    """

    message: str = Field(
        default="Testimonials added successfully",
        examples=["Testimionals added successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: dict = {}
