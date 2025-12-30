"""add aws_account to request"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_aws_account"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("request", sa.Column("aws_account", sa.String(), nullable=True))


def downgrade():
    op.drop_column("request", "aws_account")
