"""change params and tags to text"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_params_tags_text"
down_revision = "0002_add_aws_account"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("request", "params", type_=sa.Text(), existing_nullable=True)
    op.alter_column("request", "tags", type_=sa.Text(), existing_nullable=True)


def downgrade():
    op.alter_column("request", "params", type_=sa.JSON(), existing_nullable=True)
    op.alter_column("request", "tags", type_=sa.JSON(), existing_nullable=True)
