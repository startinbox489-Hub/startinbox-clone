"""insert subscription plans

Revision ID: c79589f76b6d
Revises: db31eccbb36c
Create Date: 2025-09-23 15:11:54.992982

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session
from uuid6 import uuid7


# revision identifiers, used by Alembic.
revision: str = "c79589f76b6d"
down_revision: Union[str, Sequence[str], None] = "db31eccbb36c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Subscription Plans
plans = [
    {
        "id": "free_trial",
        "name": "Free Trial",
        "price": 0.00,
        "description": "Access all features once, no card required",
        "features": [
            ("startup_idea_validation", 1),
        ],
        "is_default": True,
        "idx": 0,
        "is_popular": False,
    },
    {
        "id": "starter",
        "name": "Starter Plan",
        "price": 3.00,
        "description": "For founders validating ideas",
        "features": [
            ("startup_idea_validation", 1),
            ("idea_score", 1),
            ("lean_canvas", 1),
            ("customer_persona", 1),
            ("brand_name_suggestions", 3),
            ("monetization_models", 2),
        ],
        "is_default": False,
        "idx": 1,
        "is_popular": False,
    },
    {
        "id": "pro",
        "name": "Pro Plan",
        "price": 7.00,
        "description": "Go further with influencers outreach",
        "features": [
            ("startup_idea_validation", 1),
            ("idea_score", 1),
            ("lean_canvas", 1),
            ("customer_persona", 1),
            ("brand_name_suggestions", 3),
            ("monetization_models", 2),
            ("landing_page_hero", 1),
            ("blog_post_titles", 3),
            ("twitter_posts", 5),
            ("elevator_pitch_slide", 1),
        ],
        "is_default": False,
        "idx": 2,
        "is_popular": True,
    },
    {
        "id": "launch_bundle",
        "name": "Launch Bundle",
        "price": 15.00,
        "description": "Go further with influencers outreach",
        "features": [
            ("startup_idea_validation", 1),
            ("idea_score", 1),
            ("lean_canvas", 1),
            ("customer_persona", 1),
            ("brand_name_suggestions", 3),
            ("monetization_models", 2),
            ("landing_page_hero", 1),
            ("blog_post_titles", 3),
            ("twitter_posts", 5),
            ("elevator_pitch_slide", 1),
            ("influencer_outreach_dms", 3),
            ("go_to_market_strategy", 1),
            ("pdf_report", 1),
        ],
        "is_default": False,
        "idx": 3,
        "is_popular": False,
    },
]


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    session = Session(bind=bind)

    for plan in plans:
        # Insert plan if not exists
        session.execute(
            sa.text(
                """
                INSERT INTO si_subscription_plans (id, name, price, description, is_default,  idx, is_popular)
                VALUES (:id, :name, :price, :description, :is_default, :idx, :is_popular)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": plan["id"],
                "name": plan["name"],
                "price": plan["price"],
                "description": plan["description"],
                "is_default": plan["is_default"],
                "idx": plan["idx"],
                "is_popular": plan["is_popular"],
            },
        )

        # Insert features if not exists
        for fname, fvalue in plan["features"]:
            session.execute(
                sa.text(
                    """
                    INSERT INTO si_subscription_plan_features (id, plan_id, feature_name, value)
                    VALUES (:id, :plan_id, :feature_name, :value)
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "id": str(uuid7()),
                    "plan_id": plan["id"],
                    "feature_name": fname,
                    "value": fvalue,
                },
            )

    session.commit()


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    session = Session(bind=bind)

    session.execute(sa.text("DELETE FROM si_subscription_plan_features"))
    session.execute(sa.text("DELETE FROM si_subscription_plans"))
    session.commit()
