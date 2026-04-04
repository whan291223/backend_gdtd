"""add Patient profile

Revision ID: e92d58c4860d
Revises: 14cddc151e99
Create Date: 2026-03-22 13:44:49.875596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e92d58c4860d'
down_revision: Union[str, None] = '14cddc151e99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
