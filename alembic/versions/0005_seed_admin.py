"""seed admin user"""
from alembic import op
import sqlalchemy as sa
import bcrypt
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = "0005_seed_admin"
down_revision = "0004_add_users"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    conn.execute(
        sa.text(
            """
            INSERT INTO "user" (id, username, password_hash, role, display_name, active, created_at)
            VALUES (:id, :username, :password_hash, :role, :display_name, true, :created_at)
            ON CONFLICT (username) DO NOTHING
            """
        ),
        {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "password_hash": password_hash,
            "role": "admin",
            "display_name": "Administrador",
            "created_at": datetime.utcnow(),
        },
    )


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text('DELETE FROM "user" WHERE username = :u'), {"u": "admin"})
