"""create column phone number on table users

Revision ID: 87c3bc4d8fc9
Revises: 83a8270fbf6c
Create Date: 2025-09-23 07:35:59.005076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87c3bc4d8fc9'
down_revision: Union[str, Sequence[str], None] = '83a8270fbf6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'phone_number')
