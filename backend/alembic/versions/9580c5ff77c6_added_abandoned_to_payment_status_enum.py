"""added abandoned to payment status enum

Revision ID: 9580c5ff77c6
Revises: 3cfbc280306e
Create Date: 2025-11-09 14:06:28.572735

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9580c5ff77c6"
down_revision: Union[str, Sequence[str], None] = "3cfbc280306e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text("ALTER TYPE si_payment_status_enum ADD VALUE 'abandoned';"))


def downgrade() -> None:
    """Downgrade schema."""
    pass
