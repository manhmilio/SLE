"""001_core_tables

Revision ID: (giữ nguyên id được generate)
Revises:
Create Date: (giữ nguyên)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, INET
revision = "..."   # giữ nguyên id file của bạn
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensions — bỏ pg_cron
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "unaccent"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    # Trigger function set_updated_at()
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)

    # Table: users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("streak", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("last_studied", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("role IN ('user', 'admin')", name="ck_users_role"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_role", "users", ["role"])
    op.create_index("idx_users_is_active", "users", ["is_active"])

    op.execute("""
        CREATE TRIGGER trg_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION set_updated_at()
    """)

    # Table: refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(512), nullable=False),
        sa.Column("device", sa.String(255), nullable=True),
        sa.Column("ip", INET, nullable=True),
        sa.Column("is_revoked", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("token", name="uq_refresh_tokens_token"),
    )
    op.create_index("idx_refresh_tokens_token", "refresh_tokens", ["token"], unique=True)
    op.create_index("idx_refresh_tokens_user", "refresh_tokens", ["user_id", "is_revoked"])
    op.create_index("idx_refresh_tokens_expires", "refresh_tokens", ["expires_at"])


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_users_updated_at ON users")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")
    op.execute('DROP EXTENSION IF EXISTS "vector"')
    op.execute('DROP EXTENSION IF EXISTS "unaccent"')
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')