"""
FAQS schhema
"""

from datetime import datetime
import json
from typing import Annotated, List
from pydantic import BaseModel, model_validator, Field, ConfigDict, StringConstraints
import bleach


class FAQsBase(BaseModel):
    """
    FAQsBase
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    question: str = Field(examples=["some question"])
    answer: str = Field(examples=["some answer"])
    added_at: datetime = Field(examples=[datetime.now()])

    model_config = ConfigDict(from_attributes=True)


# ++++++++++++++++++++++ NEW FAQs +++++++++++++++++++++++++++


class AddFaqSingleSchema(BaseModel):
    """
    AddFaqSingleSchema
    """

    question: Annotated[str, StringConstraints(min_length=3, max_length=255)] = Field(
        examples=["some question"]
    )
    answer: Annotated[str, StringConstraints(min_length=3, max_length=1000)] = Field(
        examples=["some answer"]
    )

    @model_validator(mode="before")
    @classmethod
    def vaildate_fields(cls, values: dict) -> dict:
        """
        Validate all fields

        """
        if isinstance(values, bytes):
            values = json.loads(values)

        question = values.get("question")
        answer = values.get("answer")

        if isinstance(answer, str):
            values["answer"] = bleach.clean(answer)
        if isinstance(question, str):
            values["question"] = bleach.clean(question)

        return values


class AddFAQsRequestSchema(BaseModel):
    """
    AddFAQsRequestSchema
    """

    faqs: List[AddFaqSingleSchema]

    @model_validator(mode="before")
    @classmethod
    def vaildate_fields(cls, values: dict) -> dict:
        """
        Validate all fields

        """
        if isinstance(values, bytes):
            values = json.loads(values)
        faqs: list | None = values.get("faqs", None)

        if not faqs or not isinstance(faqs, list):
            raise ValueError("faqs must be provided as a list/array")

        if len(faqs) < 1 > 10:
            raise ValueError("faqs must be greater than one(1) and less than ten(10)")

        return values


class AddFAQsResponseSchema(BaseModel):
    """
    AddFAQsResponseSchema
    """

    message: str = Field(
        default="FAQs created successfully",
        examples=["FAQs created successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: List[FAQsBase]


# +++++++++++++++++ FETCH +++++++++++++++++++++++++


class FetchFAQsResponseSchema(BaseModel):
    """
    FetchFAQsResponseSchema
    """

    message: str = Field(
        default="FAQs retrieved successfully",
        examples=["FAQs retrieved successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: List[FAQsBase]


# ++++++++++++++++ Delete +++++++++++++++++++++++


class DeleteFAQsRequestSchema(BaseModel):
    """
    DeleteFAQsRequestSchema
    """

    faq_ids: List[str]

    @model_validator(mode="before")
    @classmethod
    def vaildate_fields(cls, values: dict) -> dict:
        """
        Validate all fields

        """
        if isinstance(values, bytes):
            values = json.loads(values)
        faq_ids: list | None = values.get("faq_ids", None)

        if not faq_ids or not isinstance(faq_ids, list):
            raise ValueError("faq_ids must be provided as a list/array")

        if len(faq_ids) < 1 > 10:
            raise ValueError(
                "faq_ids must be greater than one(1) and less than ten(10)"
            )

        return values


class DeleteFAQsResponseSchema(BaseModel):
    """
    DeleteFAQsResponseSchema
    """

    message: str = Field(
        default="FAQs removed successfully",
        examples=["FAQs removed successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: dict = {}
