"""add Patient profile

Revision ID: 14cddc151e99
Revises: 902bffb8b85a
Create Date: 2026-03-22 13:44:07.116728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14cddc151e99'
down_revision: Union[str, None] = '902bffb8b85a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
