"""remove realname and surname from user

Revision ID: 9a2b1c3d4e5f
Revises: 3c129d0af2c0
Create Date: 2026-04-18 12:31:06.824704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a2b1c3d4e5f'
down_revision: Union[str, None] = 'c6aba8411d08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('user', 'real_name')
    op.drop_column('user', 'surname')


def downgrade() -> None:
    op.add_column('user', sa.Column('real_name', sa.String(), nullable=True))
    op.add_column('user', sa.Column('surname', sa.String(), nullable=True))
