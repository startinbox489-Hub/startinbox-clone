"""add testimonials.is_approved column

Revision ID: ab70852cf9cd
Revises: 64cb1b8d6e1d
Create Date: 2025-09-26 16:29:39.530611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab70852cf9cd'
down_revision: Union[str, Sequence[str], None] = '64cb1b8d6e1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "si_testimonials",
        sa.Column(
            "is_approved",
            sa.Boolean(),
            server_default="FALSE",
            nullable=False,
        ),
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("si_testimonials", "is_aproved")
