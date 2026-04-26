"""add SUCCESSFUL to paymentStatus enum

Revision ID: 26f60eb7a798
Revises: 022e39a0850
Create Date: 2025-09-18 15:33:57.237814

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "26f60eb7a798"
down_revision: Union[str, Sequence[str], None] = "022e39a0850"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text("ALTER TYPE si_payment_status_enum ADD VALUE 'successful';"))


def downgrade() -> None:
    """Downgrade schema."""
    pass
