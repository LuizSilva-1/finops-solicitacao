"""make expires_at nullable

Revision ID: 0009_expires_nullable
Revises: 0008_flow_type_other_payload
Create Date: 2025-02-02 18:20:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '0009_expires_nullable'
down_revision = '0008_flow_type_other_payload'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('request', 'expires_at', existing_type=sa.DATE(), nullable=True)


def downgrade() -> None:
    op.alter_column('request', 'expires_at', existing_type=sa.DATE(), nullable=False)

