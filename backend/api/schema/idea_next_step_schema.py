"""
FAQS schhema
"""

from datetime import date
import json
from typing import Annotated

from pydantic import BaseModel, model_validator, Field, ConfigDict, StringConstraints
import bleach


class IdeaNextStepBase(BaseModel):
    """
    IdeaNextStepBase
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    user_id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    idea_id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    project_type: str = Field(examples=["some project type"])
    project_stage: str = Field(examples=["some project stahe"])
    desired_date: date = Field(examples=[date.today()])

    model_config = ConfigDict(from_attributes=True)


# ++++++++++++++++++++++ NEW next step +++++++++++++++++++++++++++


class AddIdeaNextStepRequestSchema(BaseModel):
    """
    AddIdeaNextStepRequestSchema
    """

    idea_id: Annotated[
        str,
        StringConstraints(max_length=60, min_length=20, strip_whitespace=True),
    ] = Field(examples=["11111111-1111-1111-1111-111111111111"])
    project_type: Annotated[
        str,
        StringConstraints(max_length=255, min_length=3, strip_whitespace=True),
    ] = Field(examples=["some project type"])
    project_stage: Annotated[
        str,
        StringConstraints(max_length=255, min_length=3, strip_whitespace=True),
    ] = Field(examples=["some project stage"])
    desired_date: date = Field(examples=[date.today()])

    @model_validator(mode="before")
    @classmethod
    def vaildate_fields(cls, values: dict) -> dict:
        """
        Validate all fields

        """
        if isinstance(values, bytes):
            values = json.loads(values)

        desired_date: str | None = values.get("desired_date")
        project_stage: str | None = values.get("project_stage")
        project_type: str | None = values.get("project_type")
        if desired_date:
            try:
                values["desired_date"] = date.fromisoformat(desired_date)
            except ValueError as exc:
                raise ValueError("invalida date format") from exc
        if (
            project_stage
            and isinstance(project_stage, str)
            and project_stage.strip() != ""
        ):
            values["project_stage"] = bleach.clean(project_stage)
        if (
            project_type
            and isinstance(project_type, str)
            and project_type.strip() != ""
        ):
            values["project_type"] = bleach.clean(project_type)

        return values


class AddIdeaNextStepResponseSchema(BaseModel):
    """
    AddIdeaNextStepResponseSchema
    """

    message: str = Field(
        default="Idea Next Step recorded successfully",
        examples=["Idea Next Step recorded successfully"],
    )
    status: str = Field(default="success", examples=["success"])
    data: IdeaNextStepBase
