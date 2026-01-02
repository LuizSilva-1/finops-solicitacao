"""add approval notes

Revision ID: 0007_approval_notes
Revises: 0006_gmud_fields
Create Date: 2025-02-02 12:45:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '0007_approval_notes'
down_revision = '0006_gmud_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('request', sa.Column('approval_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('request', 'approval_notes')

