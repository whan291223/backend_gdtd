"""add exercise database

Revision ID: 4cbe3f36f71c
Revises: 438e4f6a839c
Create Date: 2026-04-09 07:44:03.587059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4cbe3f36f71c'
down_revision: Union[str, None] = '438e4f6a839c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create exercise_database table
    op.create_table('exercise_database',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('met', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exercise_database_name'), 'exercise_database', ['name'], unique=True)

    # Seed initial data
    op.execute("""
        INSERT INTO exercise_database (name, met) VALUES
        ('เดิน', 0.053),
        ('วิ่ง', 0.112),
        ('ปั่นจักรยาน', 0.085),
        ('ว่ายน้ำ', 0.098),
        ('โยคะ', 0.042),
        ('ยกน้ำหนัก', 0.056),
        ('เต้นแอโรบิก', 0.095),
        ('อื่นๆ', 0.060)
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_exercise_database_name'), table_name='exercise_database')
    op.drop_table('exercise_database')
