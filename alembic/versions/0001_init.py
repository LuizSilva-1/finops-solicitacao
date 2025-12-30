"""initial tables"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "request",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("requester", sa.String(), nullable=False),
        sa.Column("service_type", sa.String(), nullable=False),
        sa.Column("params", sa.JSON(), nullable=True),
        sa.Column("cost_center", sa.String(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, default="pendente"),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column("expires_at", sa.Date(), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=True),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("estimated_cost", sa.String(), nullable=True),
        sa.Column("auto_delete", sa.Boolean(), default=False),
        sa.Column("approver", sa.String(), nullable=True),
        sa.Column("last_alert_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "alert",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("request_id", sa.String(), sa.ForeignKey("request.id"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, default="pendente"),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
    )

    op.create_table(
        "audit",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("request_id", sa.String(), sa.ForeignKey("request.id"), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("by", sa.String(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("at", sa.DateTime(), nullable=False, default=datetime.utcnow),
    )

    op.create_table(
        "importjob",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, default="pendente"),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_table("importjob")
    op.drop_table("audit")
    op.drop_table("alert")
    op.drop_table("request")
