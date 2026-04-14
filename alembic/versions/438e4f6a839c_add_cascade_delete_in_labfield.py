"""add cascade delete in labfield

Revision ID: 438e4f6a839c
Revises: edfff2d1734d
Create Date: 2026-04-09 10:33:23.273442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '438e4f6a839c'
down_revision: Union[str, None] = 'edfff2d1734d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('lab_values_field_id_fkey', 'lab_values', type_='foreignkey')
    op.drop_constraint('lab_fields_category_id_fkey', 'lab_fields', type_='foreignkey')
    
    # Recreate with CASCADE
    op.create_foreign_key(
        'lab_values_field_id_fkey',
        'lab_values', 'lab_fields',
        ['field_id'], ['id'],
        ondelete='CASCADE'
    )
    
    op.create_foreign_key(
        'lab_fields_category_id_fkey',
        'lab_fields', 'lab_categories',
        ['category_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop CASCADE foreign keys
    op.drop_constraint('lab_values_field_id_fkey', 'lab_values', type_='foreignkey')
    op.drop_constraint('lab_fields_category_id_fkey', 'lab_fields', type_='foreignkey')
    
    # Recreate without CASCADE
    op.create_foreign_key(
        'lab_values_field_id_fkey',
        'lab_values', 'lab_fields',
        ['field_id'], ['id']
    )
    
    op.create_foreign_key(
        'lab_fields_category_id_fkey',
        'lab_fields', 'lab_categories',
        ['category_id'], ['id']
    )