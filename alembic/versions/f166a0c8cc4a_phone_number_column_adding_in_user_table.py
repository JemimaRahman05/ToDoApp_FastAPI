"""Phone number column adding in User table

Revision ID: f166a0c8cc4a
Revises: 
Create Date: 2026-10-22 09:42:42.588215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f166a0c8cc4a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('phone_number',sa.String(20),nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
