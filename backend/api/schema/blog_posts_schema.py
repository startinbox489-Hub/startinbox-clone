"""
Posts Schema
"""

from typing import List, Any, Annotated, Optional
import json

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    StringConstraints,
    HttpUrl,
)

months = {
    "1": "Jan",
    "2": "Feb",
    "3": "Mar",
    "4": "Apr",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "Aug",
    "9": "Sept",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}


class PostsBaseSchema(BaseModel):
    """
    Post base
    """

    id: str = Field(examples=["1111111-1111-1111-1111-111111111111"])
    title: str | None = Field(examples=["Emerging Technologies"], default=None)
    content: str | None = Field(
        examples=[
            "Lorem ipsum dolor sit amet consectetur. Volutpat pharetra scelerisque velit orci rutrum placerat mauris"
        ],
        default=None,
    )
    date: str | None = Field(examples=["Mar 25, 2025"], default=None)
    image: str | None = Field(examples=["https://image.com.png"], default=None)
    is_draft: bool | None = Field(examples=[True], default=None)

    model_config = ConfigDict(from_attributes=True)

    # @model_validator(mode="before")
    # @classmethod
    # def validate_fields(cls, values: Any) -> Any:
    #     """
    #     Validate fields
    #     """
    #     date: str = values.created_at.date().isoformat()
    #     split_date = date.split("-")
    #     print("split_date: ", split_date)
    #     month = (
    #         split_date[1].replace("0", "")
    #         if split_date[1].startswith("0")
    #         else split_date[1]
    #     )
    #     values.date = f"{months[month]} {split_date[2]}, {split_date[0]}"
    #     return values


##################################################
class GetPostsResponseSchema(BaseModel):
    """
    Get Posts
    """

    message: str = Field(
        examples=["Posts Retrieved successfully"],
        default="Posts Retrieved successfully",
    )
    status: str = Field(examples=["success"], default="success")
    page: int = Field(examples=[10])
    limit: int = Field(examples=[10])
    pages: int = Field(examples=[10])
    total: int = Field(examples=[10])
    data: List[PostsBaseSchema]


##################################################


class GetPostResponseSchema(BaseModel):
    """
    Get Post
    """

    message: str = Field(
        examples=["Post Retrieved successfully"],
        default="Post Retrieved successfully",
    )
    status: str = Field(examples=["success"], default="success")
    data: PostsBaseSchema


# +++++++++++++++++++++  CREATE +++++++++++++++++++++++++


class NewPostRequestSchema(BaseModel):
    """
    NewPostRequestSchema
    """

    title: Annotated[
        str, StringConstraints(max_length=100, min_length=3, strip_whitespace=True)
    ] = Field(examples=["A title"])
    content: Annotated[
        str, StringConstraints(max_length=3000, min_length=50, strip_whitespace=True)
    ] = Field(examples=["A content"])
    image: Optional[HttpUrl] = Field(default=None, examples=["https://url.com"])
    is_draft: bool = Field(examples=[True])

    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, values: dict) -> dict:
        """
        Validates all fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)

        return values


class NewPostResponseSchema(BaseModel):
    """
    New Post
    """

    message: str = Field(
        examples=["Post created successfully"],
        default="Post created successfully",
    )
    status: str = Field(examples=["success"], default="success")
    data: PostsBaseSchema


# +++++++++++++++++++++  UPDATE +++++++++++++++++++++++++
class EditPostRequestSchema(BaseModel):
    """
    Edit PostRequestSchema
    """

    title: Optional[
        Annotated[
            str, StringConstraints(max_length=100, min_length=3, strip_whitespace=True)
        ]
    ] = Field(examples=["A title"], default=None)
    content: Optional[
        Annotated[
            str,
            StringConstraints(max_length=3000, min_length=50, strip_whitespace=True),
        ]
    ] = Field(examples=["A content"], default=None)
    image: Optional[HttpUrl] = Field(default=None, examples=["https://url.com"])
    is_draft: Optional[bool] = Field(examples=[True], default=None)

    @model_validator(mode="before")
    @classmethod
    def validate_all_fields(cls, values: dict) -> dict:
        """
        Validates all fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        title = values.get("title")
        content = values.get("content")
        image = values.get("image")
        is_draft = values.get("is_draft")

        if not any([title, content, image, is_draft]):
            raise ValueError("missing payload")

        return values


class EditPostResponseSchema(BaseModel):
    """
    Edits Post
    """

    message: str = Field(
        examples=["Post updated successfully"],
        default="Post updated successfully",
    )
    status: str = Field(examples=["success"], default="success")
    data: PostsBaseSchema


# ++++++++++++ DELETE +++++++++++++++
class DeletePostResponseSchema(BaseModel):
    """
    DeletePostResponseSchema
    """

    message: str = Field(
        examples=["Post deleted successfully"],
        default="Post deleted successfully",
    )
    status: str = Field(examples=["success"], default="success")
    data: dict = {}
