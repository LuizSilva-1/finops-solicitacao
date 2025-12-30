"""add users table"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = "0004_add_users"
down_revision = "0003_params_tags_text"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("username", sa.String(), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, default="user"),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
    )


def downgrade():
    op.drop_table("user")
