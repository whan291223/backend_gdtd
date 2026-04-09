"""add volume to fooddatabase

Revision ID: 3c129d0af2c0
Revises: 4cbe3f36f71c
Create Date: 2026-04-09 08:45:48.319980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c129d0af2c0'
down_revision: Union[str, None] = '4cbe3f36f71c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add volume column to fooddatabase table
    op.add_column('fooddatabase', sa.Column('volume', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('fooddatabase', 'volume')
