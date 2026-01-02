"""add flow_type and other_payload

Revision ID: 0008_flow_type_other_payload
Revises: 0007_approval_notes
Create Date: 2025-02-02 13:10:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0008_flow_type_other_payload'
down_revision = '0007_approval_notes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('request', sa.Column('flow_type', sa.String(), nullable=False, server_default='finops'))
    op.add_column('request', sa.Column('other_payload', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.alter_column('request', 'flow_type', server_default=None)


def downgrade() -> None:
    op.drop_column('request', 'other_payload')
    op.drop_column('request', 'flow_type')

