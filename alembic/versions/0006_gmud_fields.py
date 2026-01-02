"""add gmud fields

Revision ID: 0006_gmud_fields
Revises: 0005_seed_admin
Create Date: 2025-02-02 12:20:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '0006_gmud_fields'
down_revision = '0005_seed_admin'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('request', sa.Column('change_type', sa.String(), nullable=True))
    op.add_column('request', sa.Column('justification', sa.Text(), nullable=True))
    op.add_column('request', sa.Column('criticality', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('request', 'criticality')
    op.drop_column('request', 'justification')
    op.drop_column('request', 'change_type')

