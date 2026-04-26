"""
startup ideas Schema
"""

from typing import Annotated, List
from pydantic import BaseModel, Field, ConfigDict, StringConstraints


class StartupIdeasBase(BaseModel):
    """
    StartupIdeasBase
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    user_id: str = Field(examples=["11111111-1111-1111-1111-111111112222"])
    prompt: str = Field(examples=["A box of creation"])
    # A. Validation Output
    idea_validation: str | None = Field(default=None, examples=["idea_validation"])
    idea_score: int | None = Field(default=None, examples=[80])
    lean_canvas: dict | None = Field(
        default=None,
        examples=[
            {
                "problem": "Difficulty finding and booking reliable, affordable pet sitters.",
                "solution": "A mobile app connecting pet owners with vetted and insured pet sitters.",
                "key_metrics": "Number of registered users, number of bookings, average booking value, customer retention rate.",
                "unique_value_proposition": "Secure, convenient, and affordable pet sitting services with background-checked sitters.",
                "unfair_advantage": "Partnership with local veterinary clinics for referrals and promotions.",
                "customer_segments": "Pet owners who work long hours, travel frequently, or need temporary pet care.",
                "channels": "App Store Optimization (ASO), social media marketing (Facebook, Instagram), partnerships with veterinary clinics and pet stores.",
                "cost_structure": "App development and maintenance, marketing and advertising, sitter commission fees, customer support.",
                "revenue_streams": "Commission on each booking, premium subscription for pet owners, advertising revenue from pet-related businesses.",
            }
        ],
    )
    ideal_customer_persona: dict | None = Field(
        default=None,
        examples=[
            {
                "name": "Sarah Miller",
                "age_range": "30-45",
                "occupation": "Marketing Manager",
                "goals": "Find reliable pet care for her dog while she's at work or traveling.",
                "pain_points": "Finding trustworthy sitters, scheduling conflicts, high costs of traditional pet sitting services.",
            }
        ],
    )
    suggested_startup_names: list[str] | None = Field(
        default=None, examples=[["Pawsitive Sitters", "PetPal Connect", "Happy Tails"]]
    )
    monetization_models: list[str] | None = Field(
        default=None, examples=[["Commission-based fees", "Premium subscriptions"]]
    )
    # B. Launch Content Generator
    website_hero: dict | None = Field(
        default=None,
        examples=[
            {
                "headline": "Reliable Pet Sitting, at Your Fingertips.",
                "subheadline": "Find vetted & insured sitters for your furry friends.",
                "features": [
                    "Secure booking system",
                    "Background-checked sitters",
                    "Affordable pricing",
                ],
            }
        ],
    )
    blog_posts: list[dict] | None = Field(
        default=None,
        examples=[
            [
                {
                    "title": "Top 5 Tips for Choosing the Perfect Pet Sitter",
                    "outline": [
                        "Importance of background checks",
                        "Meeting the sitter beforehand",
                        "Preparing your pet for a sitter",
                    ],
                },
                {
                    "title": "The Benefits of Using a Pet Sitting App",
                    "outline": [
                        "Convenience and ease of scheduling",
                        "Cost savings compared to traditional services",
                        "Improved pet safety and security",
                    ],
                },
                {
                    "title": "How to Keep Your Pet Safe While You're Away",
                    "outline": [
                        "Preparing your home for a pet sitter",
                        "Providing essential pet information",
                        "Emergency contact details",
                    ],
                },
            ]
        ],
    )
    twitter_posts: list[str] | None = Field(
        default=None,
        examples=[
            [
                "Find the perfect pet sitter with our app! #petsitting #dogsitting #catsitting",
                "Secure, affordable, and convenient pet care. Download our app today! #petcare #app",
                "Worried about leaving your pet? We've got you covered. #petsitter #reliable",
                "Background-checked sitters, peace of mind. #pets #petsafety",
                "Download the app and find your perfect pet sitter now! Link in bio. #petlove",
            ]
        ],
    )
    elevator_pitch_slide: dict | None = Field(
        default=None,
        examples=[
            {
                "headline": "Pawsitive Sitters: Your Solution for Reliable Pet Care",
                "bullet_points": [
                    "Connecting pet owners with vetted and insured sitters",
                    "Secure booking system with ease of use",
                    "Affordable prices and flexible scheduling options",
                ],
            }
        ],
    )

    go_to_market_strategy_outline: str | None = Field(
        default=None, examples=["go_to_market_strategy_outline"]
    )

    model_config = ConfigDict(from_attributes=True)


# ++++++++++++++++++ Create +++++++++++++++++++++++++++++
class StartupIdeasRequestSchema(BaseModel):
    """
    StartupIdeasRequestSchema
    """

    prompt: Annotated[str, StringConstraints(min_length=3, max_length=5000)] = Field(
        examples=["A box of creation"]
    )
    idx: int = Field(examples=[1], default=0)
    type_: str = Field(default="oneoff", examples=["reoccurring"])


class StartupIdeaDataSchema(BaseModel):
    """
    StartupIdeaDataSchema
    """

    validation: StartupIdeasBase
    idx: int = Field(examples=[1], ge=0)


class StartupIdeasResponseSchema(BaseModel):
    """
    StartupIdeasResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Suggestions generated succesfully",
        examples=["Suggestions generated succesfully"],
    )
    data: StartupIdeaDataSchema


# ++++++++++++++++++ fetch +++++++++++++++++++++++++++++


class FetchStartupIdeasBase(BaseModel):
    """
    StartupIdeasBase
    """

    id: str = Field(examples=["11111111-1111-1111-1111-111111111111"])
    user_id: str = Field(examples=["11111111-1111-1111-1111-111111112222"])
    prompt: str = Field(examples=["A box of creation"])

    model_config = ConfigDict(from_attributes=True)


class FetchStartupIdeasResponseSchema(BaseModel):
    """
    FetchStartupIdeasResponseSchema
    """

    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Suggestions retrieved succesfully",
        examples=["Suggestions retrieved succesfully"],
    )
    data: List[FetchStartupIdeasBase]


# ++++++++++++++++++ FETCH STARTUP +++++++++++++++++++++++
class FetchStartupIdeaResponseSchema(BaseModel):
    """
    Fetch StartupIdeaResponseSchema
    """

    message: str = Field(
        default="Suggestion retrieved succesfully",
        examples=["Suggestion retrieved succesfully"],
    )
    status: str = Field(default="success", examples=["success"])

    data: StartupIdeasBase
