"""add Patient profile

Revision ID: 073d4bac2f9a
Revises: ab0603ed8136
Create Date: 2026-03-22 13:06:51.062683

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '073d4bac2f9a'
down_revision: Union[str, None] = 'ab0603ed8136'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
